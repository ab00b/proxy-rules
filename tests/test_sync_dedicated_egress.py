import copy
from pathlib import Path
import unittest

from scripts.sync_dedicated_egress import (
    RuleListError,
    activation_commands,
    migrate_legacy_labels,
    parse_rule_list,
    update_sing_box_config,
    update_xray_config,
)


SAMPLE_RULES = """\
# Disabled OpenAI route
# DOMAIN-SUFFIX,openai.com
# DOMAIN-SUFFIX,chatgpt.com

DOMAIN-SUFFIX,proxy-seller.com
DOMAIN,gemini.google.com
DOMAIN,login.live.com
"""


class ParseRuleListTests(unittest.TestCase):
    def test_comments_are_ignored(self):
        rules = parse_rule_list(SAMPLE_RULES)

        self.assertEqual(
            rules,
            [
                ("DOMAIN-SUFFIX", "proxy-seller.com"),
                ("DOMAIN", "gemini.google.com"),
                ("DOMAIN", "login.live.com"),
            ],
        )

    def test_duplicate_active_rules_are_rejected(self):
        with self.assertRaisesRegex(RuleListError, "duplicate"):
            parse_rule_list("DOMAIN,example.com\nDOMAIN,example.com\n")

    def test_unsupported_rule_type_is_rejected(self):
        with self.assertRaisesRegex(RuleListError, "unsupported"):
            parse_rule_list("DOMAIN-KEYWORD,example\n")

    def test_repository_list_has_expected_active_and_disabled_boundaries(self):
        source = (
            Path(__file__).resolve().parents[1] / "dedicated-egress.list"
        ).read_text(encoding="utf-8")
        active = parse_rule_list(source)
        disabled_openai = [
            line
            for line in source.splitlines()
            if line.startswith("# DOMAIN")
        ]

        self.assertEqual(len(active), 21)
        self.assertEqual(len(disabled_openai), 20)
        self.assertIn(("DOMAIN", "labs.google"), active)
        self.assertIn(("DOMAIN", "flow.google"), active)
        self.assertIn(("DOMAIN", "flow-content.google"), active)
        self.assertFalse(
            any("openai" in domain or "chatgpt" in domain for _, domain in active)
        )


class RendererTests(unittest.TestCase):
    def setUp(self):
        self.rules = parse_rule_list(SAMPLE_RULES)

    def test_xray_rule_is_replaced(self):
        config = {
            "routing": {
                "rules": [
                    {
                        "inboundTag": ["dedicated-egress-health"],
                        "outboundTag": "dedicated-egress",
                    },
                    {
                        "domain": ["full:stale.example"],
                        "outboundTag": "dedicated-egress",
                    },
                ]
            }
        }

        update_xray_config(config, self.rules)

        self.assertEqual(
            config["routing"]["rules"][1]["domain"],
            [
                "domain:proxy-seller.com",
                "full:gemini.google.com",
                "full:login.live.com",
            ],
        )

    def test_sing_box_exact_and_suffix_rules_are_replaced(self):
        config = {
            "route": {
                "rules": [
                    {
                        "domain_suffix": ["stale.example"],
                        "outbound": "dedicated-egress",
                    },
                    {
                        "domain": ["stale.example"],
                        "outbound": "dedicated-egress",
                    },
                ]
            }
        }

        update_sing_box_config(config, self.rules)

        self.assertEqual(
            config["route"]["rules"][0]["domain_suffix"],
            ["proxy-seller.com"],
        )
        self.assertEqual(
            config["route"]["rules"][1]["domain"],
            ["gemini.google.com", "login.live.com"],
        )

    def test_ambiguous_dedicated_rules_are_rejected(self):
        config = {
            "route": {
                "rules": [
                    {"domain": ["one.example"], "outbound": "dedicated-egress"},
                    {"domain": ["two.example"], "outbound": "dedicated-egress"},
                    {
                        "domain_suffix": ["example"],
                        "outbound": "dedicated-egress",
                    },
                ]
            }
        }

        with self.assertRaisesRegex(RuleListError, "exact-domain"):
            update_sing_box_config(config, self.rules)


class MigrationTests(unittest.TestCase):
    def test_legacy_labels_are_renamed_recursively(self):
        config = {
            "outbounds": [
                {"tag": "openai-egress", "type": "socks"},
                {"tag": "openai-direct", "type": "direct"},
            ],
            "route": {
                "rules": [
                    {
                        "inbound": ["openai-split-health"],
                        "outbound": "openai-egress",
                    }
                ],
                "final": "openai-direct",
            },
        }
        original = copy.deepcopy(config)

        migrated = migrate_legacy_labels(config)

        self.assertEqual(original["outbounds"][0]["tag"], "openai-egress")
        self.assertEqual(migrated["outbounds"][0]["tag"], "dedicated-egress")
        self.assertEqual(migrated["outbounds"][1]["tag"], "default-egress")
        self.assertEqual(
            migrated["route"]["rules"][0]["inbound"],
            ["dedicated-egress-health"],
        )
        self.assertEqual(migrated["route"]["final"], "default-egress")


class ActivationTests(unittest.TestCase):
    def test_both_cores_use_restart_after_config_change(self):
        self.assertEqual(
            activation_commands(
                xray_changed=True,
                sing_box_changed=True,
                xray_service="xray.service",
                sing_box_service="sing-box.service",
            ),
            [
                ["systemctl", "restart", "xray.service"],
                ["systemctl", "restart", "sing-box.service"],
            ],
        )


if __name__ == "__main__":
    unittest.main()
