"""Render private Surge profiles without storing credentials in the repository."""

import argparse
from pathlib import Path


TCP_GROUPS = {"✳️ Claude线路", "✨ Gemini可用线路", "🎯 专用代理"}
UDP_GROUPS = {"✨ Gemini UDP", "🎯 专用UDP"}
ROLE_HOST = {"personal": "ITL", "colleague": "ASMU"}


def render_profile(source: str, role: str, *, udp_supported: bool = True,
                   exclude_protocols: tuple[str, ...] = ()) -> str:
    host = ROLE_HOST[role]
    policies = {}
    section = ""
    for line in source.splitlines():
        if line.strip().startswith("["):
            section = line.strip()
        elif section == "[Proxy]" and "=" in line and not line.lstrip().startswith("#"):
            name, body = line.split("=", 1)
            policies[name.strip()] = body.strip()
    kinds = ("tt", "snell-split", "hy2", "vmess")
    if not set(exclude_protocols) <= set(kinds):
        raise ValueError("unknown protocol exclusion")
    tcp = [f"Dedicated-{host}-{kind}" for kind in kinds if kind not in exclude_protocols]
    if not tcp:
        raise ValueError("dedicated groups must retain at least one concrete policy")
    udp = [f"UDP-{host}-snell-split"]
    required = tcp + (udp if udp_supported else [])
    if any(name not in policies for name in required):
        raise ValueError("source profile lacks required per-server policy aliases")
    private_policies = {
        name for name, body in policies.items()
        if body.split(",", 1)[0].strip() in {"tailscale", "wireguard"}
    }
    section = ""
    seen = set()
    output = []
    for line in source.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("["):
            section = stripped
        if role == "colleague":
            if section in {"[MITM]", "[Host]"} or section.startswith(("[Tailscale ", "[WireGuard ")):
                continue
            if section == "[General]" and "=" in line and not stripped.startswith("#"):
                key = line.split("=", 1)[0].strip().lower()
                if key.startswith(("http-api", "external-controller")) or key in {"http-listen", "socks5-listen"}:
                    continue
                if key in {"allow-wifi-access", "allow-hotspot-access"}:
                    line = line.split("=", 1)[0] + "= false\n"
            if section == "[Proxy]" and "=" in line and line.split("=", 1)[0].strip() in private_policies:
                continue
            if section == "[Rule]" and (
                any(name in line for name in private_policies) or ".ts.net" in line
            ):
                continue
            # Preserve platform requirements, but not personal annotations.
            if stripped.startswith("#") and not stripped.startswith("#!REQUIREMENT"):
                continue
        if section == "[Proxy Group]" and "=" in line and not stripped.startswith("#"):
            name, body = line.split("=", 1)
            name = name.strip()
            if name in TCP_GROUPS | UDP_GROUPS:
                if name in seen:
                    raise ValueError("duplicate dedicated group")
                seen.add(name)
                options = [x.strip() for x in body.strip().split(",") if "=" in x]
                if name in UDP_GROUPS and not udp_supported:
                    body = "select, REJECT, category=自动分流"
                else:
                    members = tcp if name in TCP_GROUPS else udp
                    body = ", ".join(["fallback", *members, *options])
                line = f"{name} = {body}\n"
        output.append(line)
    if seen != TCP_GROUPS | UDP_GROUPS:
        raise ValueError("source must contain all dedicated routing groups")
    return "".join(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--role", choices=ROLE_HOST, required=True)
    parser.add_argument("--tcp-only", action="store_true")
    parser.add_argument("--exclude-protocol", action="append", default=[],
                        choices=("tt", "snell-split", "hy2", "vmess"))
    args = parser.parse_args()
    result = render_profile(args.source.read_text(), args.role, udp_supported=not args.tcp_only,
                            exclude_protocols=tuple(args.exclude_protocol))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.touch(mode=0o600, exist_ok=True)
    args.output.chmod(0o600)
    args.output.write_text(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
