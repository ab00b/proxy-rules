# GitHub throughput routing

`github-download.list` selects GitHub domains for an independent ordinary-egress
client group. It is separate from `dedicated-egress.list`, which selects the
special ISP egress on servers. Do not add GitHub to that ISP list merely to make
a dedicated client group.

Surge reference:

```ini
RULE-SET,https://raw.githubusercontent.com/ab00b/proxy-rules/main/github-download.list,🐙 GitHub线路
```

Place it before general domain proxy rules while retaining existing management
and process-rule precedence. The list covers github.com and its API, codeload
and SSH hosts, GitHub's content/release hosts under githubusercontent.com, and
githubassets.com. It does not include arbitrary GitHub Pages, Copilot, or shared
Amazon/Cloudflare/CDN destinations. Additional LFS or redirected endpoints need
observed hostname evidence.

The current client uses ordered fallback between GitHub-specific aliases for
ITL HY2, ASMU Snell, and ASMU VMess. Their node definitions inherit the existing
ordinary policies; only alias health probes use https://github.com/robots.txt.
No node credentials or private addresses are stored here.

On 2026-11-02, GitHub Desktop's existing clone selected ITL-snell through the
general Smart group and ran at approximately 20–28 KB/s. A source-port-isolated
real shallow clone of git/git v2.51.0 reproduced approximately 22 KB/s on that
policy, versus 2.50 MB/s on ITL-hy2 and 1.56 MB/s on ASMU-snell. The latter two
clones completed and passed object connectivity checks at the same commit.
Eight-policy codeload tests additionally measured ASMU-vmess near 1.96 MB/s;
the other slow or failing samples were excluded from this group.

These are bounded snapshots on the current Mac/network, not sustained-bandwidth
guarantees or evidence for every repository. Ordered fallback keeps the measured
preferred path while healthy; its HEAD probes detect availability, not live
throughput. A still-reachable slow line requires manual override or remeasurement.
Existing clone connections keep their original node until reconnected. No server
configuration or global Smart-group change is required. iOS needs its own
configuration refresh and network acceptance.
