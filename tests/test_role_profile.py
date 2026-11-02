import unittest

from scripts.render_role_profile import render_profile, TCP_GROUPS, UDP_GROUPS


def fixture():
    lines = ["[General]", "http-api = secret@127.0.0.1:6166", "allow-wifi-access = true", "[Proxy]"]
    for host in ("ASMU", "ITL"):
        for kind in ("tt", "snell-split", "hy2", "vmess"):
            lines.append(f"Dedicated-{host}-{kind} = snell, example.invalid, 1, psk=fake")
        lines.append(f"UDP-{host}-snell-split = snell, example.invalid, 1, psk=fake")
    lines += ["private = tailscale, section-name=private", "[Proxy Group]",
              "#!REQUIREMENT SYSTEM!='iOS' Apple = select, DIRECT",
              "#!REQUIREMENT SYSTEM=='iOS' Apple = select, DIRECT, category=常用",
              "ordinary = select, DIRECT"]
    for name in TCP_GROUPS | UDP_GROUPS:
        lines.append(f"{name} = fallback, Dedicated-ASMU-tt, Dedicated-ITL-tt, interval=60, category=自动分流")
    lines += ["[Rule]", "DOMAIN,private.ts.net,private", "DOMAIN,public.example,ordinary",
              "[MITM]", "ca-p12 = personal-ca", "[Host]", "private.example = 127.0.0.1",
              "[Tailscale private]", "auth-key = personal-tailnet-key"]
    return "\n".join(lines) + "\n"


class RoleProfileTests(unittest.TestCase):
    def groups(self, result):
        return [line for line in result.splitlines()
                if line.split("=", 1)[0].strip() in TCP_GROUPS | UDP_GROUPS]

    def test_roles_cannot_cross_servers_or_use_ordinary_fallback(self):
        for role, host, other in [("personal", "ITL", "ASMU"), ("colleague", "ASMU", "ITL")]:
            result = render_profile(fixture(), role)
            for line in self.groups(result):
                self.assertIn(host, line)
                self.assertNotIn(other, line)
                self.assertNotIn(", DIRECT", line)
            self.assertIn("DOMAIN,public.example,ordinary", result)
            self.assertIn("SYSTEM!='iOS' Apple", result)
            self.assertIn("SYSTEM=='iOS' Apple", result)

    def test_colleague_export_excludes_personal_management_secrets(self):
        result = render_profile(fixture(), "colleague")
        for forbidden in ("secret@", "personal-ca", "personal-tailnet-key", "private.ts.net", "[MITM]", "[Host]", "[Tailscale"):
            self.assertNotIn(forbidden, result)
        self.assertIn("allow-wifi-access = false", result)
        self.assertIn("psk=fake", result)
        self.assertIn("personal-ca", render_profile(fixture(), "personal"))

    def test_personal_profile_can_generate_colleague_version_again(self):
        personal = render_profile(fixture(), "personal")
        self.assertEqual(render_profile(personal, "colleague"), render_profile(fixture(), "colleague"))
        self.assertEqual(render_profile(personal, "personal"), personal)

    def test_unsupported_udp_fails_closed(self):
        result = render_profile(fixture(), "personal", udp_supported=False)
        for name in UDP_GROUPS:
            self.assertIn(f"{name} = select, REJECT, category=自动分流", result)

    def test_incomplete_source_rejected(self):
        with self.assertRaises(ValueError):
            render_profile(fixture().replace("Dedicated-ITL-vmess =", "missing ="), "personal")

    def test_unaccepted_protocol_can_be_excluded_without_affecting_ordinary_nodes(self):
        result = render_profile(fixture(), "colleague", exclude_protocols=("hy2",))
        for line in self.groups(result):
            self.assertNotIn("Dedicated-ASMU-hy2", line)
        self.assertIn("Dedicated-ASMU-hy2 =", result)
        with self.assertRaises(ValueError):
            render_profile(fixture(), "colleague", exclude_protocols=("tt", "snell-split", "hy2", "vmess"))
