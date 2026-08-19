#!/usr/bin/env python3
"""Synchronize a policy-free rule list into Xray and Sing-box configs."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import urllib.request


DEFAULT_URL = (
    "https://raw.githubusercontent.com/ab00b/proxy-rules/"
    "main/dedicated-egress.list"
)
DEFAULT_XRAY_CONFIG = "/etc/v2ray-agent/xray/conf/13_dedicated_egress.json"
DEFAULT_SING_BOX_CONFIG = "/etc/v2ray-agent/sing-box/conf/config.json"
DEFAULT_CACHE = "/var/lib/dedicated-egress/dedicated-egress.list"
DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
)
LEGACY_LABELS = {
    "openai-egress": "dedicated-egress",
    "openai-direct": "default-egress",
    "openai-split-health": "dedicated-egress-health",
}


class RuleListError(ValueError):
    """Raised when a rule list or target configuration is unsafe to apply."""


def parse_rule_list(text: str) -> list[tuple[str, str]]:
    rules: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 2:
            raise RuleListError(f"line {line_number}: expected TYPE,domain")
        rule_type, domain = parts[0].upper(), parts[1].lower()
        if rule_type not in {"DOMAIN", "DOMAIN-SUFFIX"}:
            raise RuleListError(
                f"line {line_number}: unsupported rule type {rule_type}"
            )
        if not DOMAIN_RE.fullmatch(domain):
            raise RuleListError(f"line {line_number}: invalid domain {domain!r}")
        rule = (rule_type, domain)
        if rule in seen:
            raise RuleListError(f"line {line_number}: duplicate rule {line}")
        seen.add(rule)
        rules.append(rule)
    if not 1 <= len(rules) <= 500:
        raise RuleListError(f"unsafe active rule count: {len(rules)}")
    return rules


def migrate_legacy_labels(value):
    if isinstance(value, dict):
        return {key: migrate_legacy_labels(item) for key, item in value.items()}
    if isinstance(value, list):
        return [migrate_legacy_labels(item) for item in value]
    if isinstance(value, str):
        return LEGACY_LABELS.get(value, value)
    return copy.deepcopy(value)


def _one(items: list[dict], description: str) -> dict:
    if len(items) != 1:
        raise RuleListError(
            f"expected exactly one {description} dedicated-egress rule; "
            f"found {len(items)}"
        )
    return items[0]


def update_xray_config(config: dict, rules: list[tuple[str, str]]) -> None:
    route_rules = config.get("routing", {}).get("rules", [])
    target = _one(
        [
            rule
            for rule in route_rules
            if rule.get("outboundTag") == "dedicated-egress"
            and "domain" in rule
        ],
        "Xray domain",
    )
    target["domain"] = [
        ("full:" if rule_type == "DOMAIN" else "domain:") + domain
        for rule_type, domain in rules
    ]


def update_sing_box_config(config: dict, rules: list[tuple[str, str]]) -> None:
    route_rules = config.get("route", {}).get("rules", [])
    exact_target = _one(
        [
            rule
            for rule in route_rules
            if rule.get("outbound") == "dedicated-egress" and "domain" in rule
        ],
        "Sing-box exact-domain",
    )
    suffix_target = _one(
        [
            rule
            for rule in route_rules
            if rule.get("outbound") == "dedicated-egress"
            and "domain_suffix" in rule
        ],
        "Sing-box domain-suffix",
    )
    exact_target["domain"] = [
        domain for rule_type, domain in rules if rule_type == "DOMAIN"
    ]
    suffix_target["domain_suffix"] = [
        domain for rule_type, domain in rules if rule_type == "DOMAIN-SUFFIX"
    ]


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "dedicated-egress-sync/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuleListError(f"rule source returned HTTP {response.status}")
        return response.read().decode("utf-8")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise RuleListError(f"{path} must contain a JSON object")
    return value


def write_atomic(path: Path, content: bytes, reference: Path | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    reference = reference if reference and reference.exists() else path
    stat_result = reference.stat() if reference.exists() else None
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        if stat_result:
            os.chmod(temp_path, stat_result.st_mode)
            os.chown(temp_path, stat_result.st_uid, stat_result.st_gid)
        else:
            os.chmod(temp_path, 0o600)
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def json_bytes(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def run_checked(command: list[str]) -> None:
    subprocess.run(command, check=True)


def backup(path: Path) -> Path:
    destination = path.with_name(path.name + ".dedicated-egress-sync.previous")
    shutil.copy2(path, destination)
    return destination


def restore(source: Path, destination: Path) -> None:
    shutil.copy2(source, destination)


def apply(
    source_text: str,
    xray_path: Path,
    sing_box_path: Path,
    cache_path: Path,
    xray_bin: str,
    sing_box_bin: str,
    xray_service: str,
    sing_box_service: str,
    migrate_labels: bool,
    dry_run: bool,
) -> dict:
    rules = parse_rule_list(source_text)
    xray_original = load_json(xray_path)
    sing_box_original = load_json(sing_box_path)
    xray_updated = (
        migrate_legacy_labels(xray_original) if migrate_labels else copy.deepcopy(xray_original)
    )
    sing_box_updated = (
        migrate_legacy_labels(sing_box_original)
        if migrate_labels
        else copy.deepcopy(sing_box_original)
    )
    update_xray_config(xray_updated, rules)
    update_sing_box_config(sing_box_updated, rules)
    xray_changed = xray_updated != xray_original
    sing_box_changed = sing_box_updated != sing_box_original
    digest = hashlib.sha256(source_text.encode()).hexdigest()
    result = {
        "active_rules": len(rules),
        "source_sha256": digest,
        "xray_changed": xray_changed,
        "sing_box_changed": sing_box_changed,
        "dry_run": dry_run,
    }
    if dry_run:
        return result

    xray_backup = backup(xray_path)
    sing_box_backup = backup(sing_box_path)
    try:
        if xray_changed:
            write_atomic(xray_path, json_bytes(xray_updated), xray_path)
        if sing_box_changed:
            write_atomic(sing_box_path, json_bytes(sing_box_updated), sing_box_path)
        run_checked([xray_bin, "run", "-test", "-confdir", str(xray_path.parent)])
        run_checked([sing_box_bin, "check", "-c", str(sing_box_path)])
        if xray_changed:
            run_checked(["systemctl", "restart", xray_service])
        if sing_box_changed:
            run_checked(["systemctl", "reload", sing_box_service])
        run_checked(["systemctl", "is-active", "--quiet", xray_service])
        run_checked(["systemctl", "is-active", "--quiet", sing_box_service])
        write_atomic(cache_path, source_text.encode())
    except Exception:
        restore(xray_backup, xray_path)
        restore(sing_box_backup, sing_box_path)
        subprocess.run(["systemctl", "restart", xray_service], check=False)
        subprocess.run(["systemctl", "restart", sing_box_service], check=False)
        raise
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--source-file")
    parser.add_argument("--xray-config", default=DEFAULT_XRAY_CONFIG)
    parser.add_argument("--sing-box-config", default=DEFAULT_SING_BOX_CONFIG)
    parser.add_argument("--cache", default=DEFAULT_CACHE)
    parser.add_argument("--xray-bin", default="/etc/v2ray-agent/xray/xray")
    parser.add_argument(
        "--sing-box-bin", default="/etc/v2ray-agent/sing-box/sing-box"
    )
    parser.add_argument("--xray-service", default="xray.service")
    parser.add_argument("--sing-box-service", default="sing-box.service")
    parser.add_argument("--migrate-labels", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_text = (
        Path(args.source_file).read_text(encoding="utf-8")
        if args.source_file
        else fetch_text(args.url)
    )
    result = apply(
        source_text=source_text,
        xray_path=Path(args.xray_config),
        sing_box_path=Path(args.sing_box_config),
        cache_path=Path(args.cache),
        xray_bin=args.xray_bin,
        sing_box_bin=args.sing_box_bin,
        xray_service=args.xray_service,
        sing_box_service=args.sing_box_service,
        migrate_labels=args.migrate_labels,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
