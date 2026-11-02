# GitHub clone throughput routing

**Goal:** Diagnose GitHub Desktop's slow clone and route GitHub transfers through measured healthy high-throughput ordinary-egress nodes.
**Why planning is required:** Live client routing and shared iCloud profile change.
**Acceptance:** Preserve profile, platform-specific display directives, all existing routes and active unrelated sessions; compare a common public GitHub transfer across concrete policies; verify the actual policy used, not just the expected rule; add a GitHub-specific group only if measurement supports it; check a real Git clone and permanent rule match after reload without engine restart. Do not add GitHub to the ISP-only canonical dedicated-egress list or alter server routes without evidence.

### Outcome 1: Reproduce and distinguish
- Work: Baseline request evidence shows GitHub Desktop git-remote-https on ITL-snell at ~28 KB/s. Use temporary source-port-scoped rules and bounded public GitHub downloads to compare ordinary ASMU/ITL Snell, HY2, VMess and TrustTunnel paths, keeping user traffic untouched.
- Verify: Same URL and payload; record HTTP status, bytes, total/first-byte time, throughput and Surge final policy. Repeat strongest candidates and current slow path to bound variability.
- Recovery/stop: List existing temp rules before tests; clear only exact rules created here in finally handlers. Stop individual transfers on bounded timeouts; preserve partial results privately. Never print credentials or private node addresses.

### Outcome 2: Delivery and acceptance
- Work: If supported, add a visible GitHub group in 自动分流 using a measured ordered set of ordinary nodes and narrow GitHub domain suffixes. Keep platform-specific Mac/iOS display conditions and other groups unchanged. Group availability is not continuous throughput optimization.
- Verify: Candidate profile syntax, effective diff, GitHub/objects/codeload and non-GitHub rules, fresh real clone, actual final node and engine start time. iOS still needs sync/reload and physical runtime acceptance.
- Recovery/stop: Back up current private profile; abort on concurrent edits, invalid configuration, or unexpected route changes. Roll back only task-created group/rules if acceptance fails. Existing long-running clone connections retain their node until reconnected.
