# Claude dedicated routing acceptance — 2026-11-02

## Delivered

Canonical routing revision `f3fb97840872c6c51cf2107db53a4d9154fdf3ce` adds 19 Claude/Anthropic/ecosystem suffixes and 6 exact infrastructure/feature/analytics hosts. Source rationale and shared-host limitations are in [the inventory](../../../docs/claude-routing.md). The canonical list has 53 active entries; OpenAI entries stay inactive. Existing Flow, NotebookLM and other routing survives unchanged.

An isolated `codex/claude-dedicated-routing` branch based on current origin/main preserved the original dirty checkout, which was behind the shared source. No original checkout files or proxy definitions were overwritten.

## Claim-to-evidence

| Claim | Evidence |
|---|---|
| Published source and CI | Public main contains 53 active rules. [Validation run](https://github.com/ab00b/proxy-rules/actions/runs/41379172139) succeeded for routing revision f3fb978; local 14 tests and renewal shell syntax check passed. |
| Both server caches agree | ASMU and ITL SHA-256: `e3e92a07acb7231fbd96a9e114b4f180f5cb79b9b1b838997881988609948c04`, matching the canonical list. |
| All render outputs agree | Every active exact/suffix entry matches Xray, sing-box live configuration and persistent renewal fragment on each host. Xray and sing-box syntax checks pass; normalized renewal merge equals complete runtime configuration. |
| Services healthy | xray, sing-box, trusttunnel, snell-split and dedicated-egress-sync.timer active on both hosts. Existing domain-routing ingresses and protocol adapters remain unchanged. |
| ASMU runtime route | Latest API and Claude access-log routes use `[split-route-test -> dedicated-egress]`; earlier default-egress samples preceded synchronization and are not acceptance evidence. |
| ITL runtime route | Holding SOCKS CONNECT requests through the domain router increased Xray connections to its configured dedicated outlet by one for api.anthropic.com and claude.ai each; www.gstatic.com control increased them by zero. No payloads, endpoints or credentials exported. |
| Real server requests | Both routers reached api.anthropic.com (root returns 404) and claude.ai (HEAD returns Cloudflare challenge 403); these are HTTP reachability results, not authenticated application success. |
| Surge matching | All 19 suffixes were checked using child hostnames and all six exact destinations using their own names: every rule matched the canonical ruleset and resolved through the dedicated group. OpenAI/ChatGPT did not match that ruleset. |
| Client real policy | HEAD requests to Claude, API and clau.de reported Dedicated-ASMU-tt and the canonical ruleset. Chrome real requests for claude.ai and assets-proxy.anthropic.com used Dedicated-ASMU-tt. |
| Browser acceptance | Existing signed-in Chrome session loaded Claude's new-chat composer and sidebar, including after final ASMU synchronization. No prompt was submitted. |
| Client preservation | Original profile bytes and module diff unchanged. Surge engine start remains 2026-10-28 21:12:24 +08:00; only canonical external-resource refresh and Reload Profile used. Existing QUIC blocking/TCP fallback remains active. |

## Deployment notes and boundaries

The current GitHub workflow validates code; it does not deploy servers. Both server sync services were explicitly started. ITL fetched the current main list. ASMU's main Raw URL initially served the old 28-rule body despite a successful service result; running the existing sync executable against the immutable f3fb978 source applied all 53 rules. Its periodic main URL and timer remain unchanged. A short cached response is not evidence of a sync implementation failure.

ASMU's local tailnet hostname resolved through a fake-IP path and direct management timed out. Management succeeded through ITL using ASMU's actual tailnet address and the existing hostname's known-host key; no SSH security checks were disabled or SSH configuration changed.

Private recovery snapshots live under `/root/claude-routing-20261102/` on each host; client baseline and sanitized verification summaries are in the task's private temporary directory. Existing synchronizer validation/rollback remains in use. If reverting, remove only this task's domain block from the current canonical source and resync; full old-profile restoration would risk discarding later changes.

No generated answer, file upload, MCP operation, all-protocol traffic matrix, other client device, cold boot, raw-IP flow, or long-run session has been accepted. Generic shared GCS/GitHub/telemetry/CDN destinations retain existing routing, as documented; this is domain routing, not strict per-process isolation. Community inventories are mutable and do not establish permanent completeness.
