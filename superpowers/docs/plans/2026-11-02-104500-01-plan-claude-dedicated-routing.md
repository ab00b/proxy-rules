# Claude dedicated routing

**Goal:** Route Claude-owned domains through dedicated egress on Surge, ASMU and ITL using one canonical list.
**Why planning is required:** Cross-system live routing change.
**Acceptance:** Official and community domain families render as suffix rules; OpenAI stays excluded; publish only task changes based on latest origin/main; GitHub automation and both server caches, Xray, sing-box live/source fragments and active services agree; Surge resource refresh and Reload Profile preserve engine uptime; real requests report dedicated policies. HTTP challenges and authenticated application acceptance are separate results.

### Outcome 1: Canonical rules
- Work: Add the 19 suffixes and 6 exact hosts documented in docs/claude-routing.md after cross-checking five GitHub inventories; regression coverage for both renderers. Shared third-party CDN domains remain on existing routes unless Claude-specific runtime evidence requires a narrow rule.
- Verify: python3 -m unittest discover -s tests -v; inspect task diff.

### Outcome 2: Delivery and runtime
- Work: Publish the verified revision, use existing server-pulled synchronization and refresh Surge shared resource. Preserve dirty original checkout and unrelated profile configuration.
- Risks/open questions: ASMU tailnet DNS currently resolves to a fake-IP and SSH times out; establish a working management path before runtime claims.
- Recovery/stop: Save client profile and server routing/config/cache snapshots privately before rollout; existing sync validates and rolls back on failure. Stop on failed config checks or unhealthy services; revert only task suffixes in canonical list and resync if recovery is needed. No engine restart.
- Verify: Public source hash, Actions status, per-host normalized routing/source/cache and service checks, rule explain, real request final policy; signed-in browser if an existing session is available.

### Outcome 3: Named Claude group (user-approved naming)
- Work: Add visible `✳️ Claude线路` under 自动分流 with the dedicated group's identical fallback members and parameters; keep `🤖 Codex线路` and `✨ Gemini可用线路` unchanged. Publish a generated Claude-only ruleset derived from the canonical Claude block, enforce regeneration in CI, and reference it before the broader shared ruleset. Keep the existing dedicated UDP guard ahead of Claude TCP routing. No new server routing rules or aliases; existing probe URLs remain unchanged and are not Claude application checks.
- Recovery/stop: Save the current iCloud profile privately; stop before reload on invalid profile or any unrelated change. Roll back only added group and Claude rule reference if new rules fail. Never restart the engine.
- Verify: Generated subset matches canonical block and excludes unrelated sites; CI passes; all 25 Claude entries choose the named group; Gemini/Codex and UDP routing preserved; real client request final policy and engine uptime checked. iOS requires its own sync/reload and runtime check.
