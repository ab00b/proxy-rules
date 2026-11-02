# Claude routing inventory — 2026-11-02

The canonical dedicated-egress list includes 19 suffixes and 6 exact destinations for Claude/Anthropic, preserving existing Google/NotebookLM/Microsoft rules and inactive OpenAI entries.

## Sources inspected

- [Official desktop requirements](https://code.claude.com/docs/en/desktop#network-access-requirements): six core domain families, including previews, bridge and MCP content.
- [MetaCubeX](https://github.com/MetaCubeX/meta-rules-dat/blob/meta/geo/geosite/anthropic.list) and [v2fly upstream](https://github.com/v2fly/domain-list-community/blob/master/data/anthropic): 18 Anthropic domain families plus the exact branded Bunny CDN host. They are related inventories, not independent ownership verification.
- [blackmatrix7](https://github.com/blackmatrix7/ios_rule_script/blob/master/rule/Surge/Claude/Claude.list): two older core suffixes and exact Fathom CDN host.
- [erwanjun core](https://github.com/erwanjun/surge-claude-rules/blob/main/Surge/Claude-Core.list): short URL, MCP client, branded CDN, Auth0 and Ghost endpoints.
- [xiaolai registry](https://github.com/xiaolai/anthropic-claude-surge-rules-set/blob/main/domains.yaml): short URL, MCP specification site, GrowthBook and Fathom endpoints, plus shared installation/telemetry candidates.

Community classifications are evidence of intended routing coverage, not a guarantee of ownership or use by every Claude feature. Newer product, redirect and ecosystem suffixes are included to satisfy broad Claude coverage. Auth0, Ghost and CDN aliases use exact matches; their parent providers are not included. The exact GrowthBook and Fathom hosts are shared and therefore also change the exit of unrelated applications requesting those same hosts.

## Shared dependency boundary

Generic storage.googleapis.com, raw.githubusercontent.com, Sentry, Datadog, Intercom, Stripe, Cloudflare challenge and generic artifact CDNs retain existing routing. Their entire destination is shared with unrelated services, including OpenAI. Add a narrow host only when an actual Claude workflow demonstrates it needs the same exit. Domain routing cannot distinguish Claude-specific URL paths inside shared GCS/GitHub/CDN hosts. This inventory does not claim every third-party request from a Claude process uses the dedicated exit.

No keyword rules, NTP catch-all or IP/ASN rules were copied. The canonical format supports domain/exact suffix matches consistently on Surge, Xray and sing-box. Domain routing depends on the destination hostname remaining available to the server; raw-IP flows without hostname metadata are not claimed.

## Activation

Use existing server-pulled synchronization, then compare canonical source and caches, Xray, sing-box runtime and renewal fragments. Surge refreshes its canonical RULE-SET and uses Reload Profile, preserving engine uptime. Existing TCP fallback and dedicated UDP groups remain unchanged. Original ordinary Snell fallback listeners continue their existing default-egress behavior.
