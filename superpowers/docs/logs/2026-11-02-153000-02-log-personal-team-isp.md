## Implementation Log

**Completed:** 2026-11-02

### What changed
- Assigned the first newly supplied ISP exclusively to ITL/personal and the second to ASMU/colleagues. Both servers' Xray outlet, sing-box runtime and renewal fragment now use their own verified SOCKS5 endpoint with physical-source binding. The old cross-server client/gateway services are disabled; their private recovery configurations remain.
- Applied the personal profile to the active iCloud profile and generated two private role exports from one renderer. Dedicated TCP/UDP groups stay on the assigned server, with no ordinary or cross-server fallback. Colleague groups exclude ASMU HY2, which was already failing before this rollout. Ordinary GitHub/Codex/general behavior and Mac/iOS display conditions are preserved.
- Removed personal MITM CA, tailnet enrollment, controller/listener material and private host aliases from the colleague export. ISP credentials remain only in root-only server files; authorized proxy connection credentials remain in mode-0600 client exports outside Git.

### Verification
- Both providers returned their expected distinct addresses when tested only from the assigned physical server. Live public Claude trace checks verified ITL TrustTunnel/Snell split/HY2/VMess and ASMU TrustTunnel/Snell split/VMess exit identities. The domain routers and forced-dedicated ingresses agreed; ordinary exits remained different. Both cores on both hosts passed three dedicated-outlet UDP DNS round trips; one initial ITL UDP timeout passed on recheck.
- All server core services are healthy; rule synchronization preserved the new outlets and all 53 canonical rules, and normalized certificate-renewal merges equal runtime configuration. ITL's first activation hit a listener-readiness race and automatically restored the original configuration; the successful retry explicitly waited for listeners. No Surge engine restart, global-route change, or remaining temporary rules/test services.
- All 23 tests and four role/platform syntax checks passed. Actual personal Claude, Gemini, authentication and NotebookLM routes select ITL; GitHub and Codex retain their own groups. Personal Chrome loaded the signed-in Claude new-chat page through ITL. The current Mac profile equals the personal export; the colleague export passed secret-boundary checks.

### Notes
- ASMU HY2 timed out in both the earlier GitHub benchmark and current ordinary/dedicated tests; it is excluded from colleague dedicated groups rather than treated as accepted. It was not repaired here.
- iOS, the colleague's actual client/account, generated answers, uploads, long-session stability and cold boots remain unverified. These role files provide routing separation, not independent server account authorization. Existing sessions need new connections to adopt the new assigned node.
- Backups and root-only deployment records are under `/root/isp-split-20261102/` on each host; local private exports are under `/Users/albert/Documents/代理配置/2026-11-02-公司ISP/`. No file was sent to colleagues and no provider-side cancellation/renewal setting was changed.
