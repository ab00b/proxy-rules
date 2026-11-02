# Personal/team ISP profiles

The personal profile assigns all dedicated-egress groups to ITL and ISP A. The
colleague profile assigns those groups to ASMU and ISP B. Each purchased proxy
is contacted only by its assigned server. ISP credentials live only in private
server configuration, not in the repository or client profiles.

`dedicated-egress.list` stays the canonical shared domain source, including its
generated Claude view. No per-role domain copy is required. Server Xray and
sing-box dedicated outlets use their assigned, authenticated SOCKS5 endpoint.
Their source addresses are bound to the physical server interface's IPv4 address
to avoid the ordinary WARP route and keep the provider's single-device binding
stable. A server address change requires refreshing that binding.

Both sing-box runtime and its renewal source fragment must be updated together.
The ordinary routes, public protocol listeners, TrustTunnel forwarding and Snell
split adapters retain their contracts. The old ITL-to-ASMU dedicated bridge and
its ASMU gateway are disabled after the independent paths are accepted; their
private recovery configuration is retained.

## Client rendering

Run the renderer against an existing private profile that contains both servers'
proxy aliases. It can also regenerate the colleague version from the generated
personal profile because it reconstructs role-specific groups from aliases.

```sh
python3 -m scripts.render_role_profile --source /private/path/base.conf \
  --role personal --output /private/path/Surge-personal.conf
python3 -m scripts.render_role_profile --source /private/path/base.conf \
  --role colleague --exclude-protocol hy2 --output /private/path/Surge-colleague.conf
```

All three dedicated TCP groups (Claude, Gemini, shared dedicated) contain only
the role's server. Both dedicated UDP groups contain only that server's split
Snell alias. Original ordinary Snell fallbacks are intentionally removed from
Gemini: availability fallback must not change the assigned public IP. If an
upstream lacks verified UDP support, `--tcp-only` makes these UDP groups reject
instead of allowing an ordinary or another user's exit. QUIC blocking remains
unchanged.

Ordinary GitHub, Codex and general groups can still use both servers. This is
role-specific destination routing, not account-level authorization isolation.
The colleague profile retains the authorized proxy connection credentials but
removes personal Tailscale/WireGuard enrollment, dependent private-network rules,
MITM CA material, private host aliases and controller/listener configuration.
Exports are mode 0600 and must stay outside Git. They are private proxy profiles,
not credential-free public artifacts. The renderer never sends them to anyone.

Mac/iOS display requirements and the existing ordinary routing remain intact.
Syntax checks on projected iOS content do not replace an actual iOS or colleague
client acceptance test. After a role change, existing connections must reconnect
to adopt the new role's node; an old established session cannot migrate in place.

## Acceptance

Validate candidates before reload. Verify each concrete public protocol path
with a real target request, and verify expected egress independently of its
client policy name. `https://claude.ai/cdn-cgi/trace` can expose the observed exit
for diagnostics; a trace response does not establish conversation, upload or
account availability. Finish the user-facing browser path separately. Never
print ISP credentials, CA keys or raw private endpoints into logs.

ASMU HY2 timed out both during the earlier GitHub benchmark and during this
rollout, including its ordinary-policy test. It is excluded from the delivered
colleague dedicated groups with `--exclude-protocol hy2`; ASMU TrustTunnel,
Snell split and VMess passed expected-exit checks. Ordinary group definitions
remain unchanged. Reaccept that protocol before removing the exclusion.
