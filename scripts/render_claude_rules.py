"""Generate the Claude client view; dedicated-egress.list stays authoritative."""

import argparse
from pathlib import Path

from scripts.sync_dedicated_egress import RuleListError, parse_rule_list


ROOT = Path(__file__).resolve().parents[1]
START = "# Claude / Anthropic:"
END = "# Dedicated proxy provider qualification"
HEADER = (
    "# Generated from the Claude block in dedicated-egress.list; do not edit.\n"
    "# Regenerate: python3 -m scripts.render_claude_rules\n"
)


def render(source: str) -> str:
    lines = source.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith(START)]
    ends = [i for i, line in enumerate(lines) if line == END]
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise RuleListError("expected one bounded canonical Claude block")
    # Validate the entire source as well as its derived view.
    parse_rule_list(source)
    rules = parse_rule_list("\n".join(lines[starts[0]:ends[0]]))
    return HEADER + "".join(f"{kind},{domain}\n" for kind, domain in rules)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = render((ROOT / "dedicated-egress.list").read_text())
    target = ROOT / "claude-egress.list"
    if args.check:
        if not target.exists() or target.read_text() != output:
            parser.exit(1, "Claude view is stale: run python3 -m scripts.render_claude_rules\n")
    else:
        target.write_text(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
