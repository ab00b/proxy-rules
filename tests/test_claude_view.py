from pathlib import Path
import unittest

from scripts.render_claude_rules import render
from scripts.sync_dedicated_egress import RuleListError, parse_rule_list


class ClaudeViewTests(unittest.TestCase):
    def test_client_view_tracks_only_canonical_claude_block(self):
        root = Path(__file__).resolve().parents[1]
        source = (root / "dedicated-egress.list").read_text()
        output = render(source)
        self.assertEqual(output, (root / "claude-egress.list").read_text())
        rules = parse_rule_list(output)
        self.assertEqual(len(rules), 25)
        self.assertIn(("DOMAIN-SUFFIX", "claude.ai"), rules)
        for domain in ("chatgpt.com", "openai.com", "gemini.google.com", "proxy-seller.com"):
            self.assertFalse(any(host == domain for _, host in rules))

    def test_new_canonical_claude_rule_appears_in_view(self):
        source = (
            "# Claude / Anthropic: test\nDOMAIN-SUFFIX,claude.ai\n"
            "DOMAIN,extra.claude.ai\n# Dedicated proxy provider qualification\n"
            "DOMAIN,other.example\n"
        )
        self.assertEqual(parse_rule_list(render(source)), [
            ("DOMAIN-SUFFIX", "claude.ai"), ("DOMAIN", "extra.claude.ai")
        ])

    def test_ambiguous_or_missing_block_is_rejected(self):
        for source in (
            "DOMAIN,claude.ai\n",
            "# Claude / Anthropic: one\n# Claude / Anthropic: two\n"
            "DOMAIN,claude.ai\n# Dedicated proxy provider qualification\n",
        ):
            with self.subTest(source=source), self.assertRaises(RuleListError):
                render(source)
