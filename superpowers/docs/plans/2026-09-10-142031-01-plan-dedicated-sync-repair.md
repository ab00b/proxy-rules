# Repair dedicated egress synchronization

**Goal:** Restore durable ASMU/ITL routing and automatic rule updates while keeping SSH private through Tailscale.
**Why planning is required:** Authorized production changes span two proxy servers, certificate refresh, and CI delivery.
**Acceptance:** Back up affected files and service states on each host before changes; validate candidate configs before activation; deploy one host at a time; stop on failed configuration or health checks and restore that host. Preserve credentials locally on each host and preserve current TLS/inbounds. Do not alter firewall or Tailscale access. Confirm rendered rules, running services, actual requests, renewal merge persistence, and a subsequent timer-triggered no-change sync. Preserve original local checkout modifications.

### Outcome 1: Durable configuration source
- Work: Persist dedicated route/outbound configuration in a Sing-box merge fragment; sync both fragment and runtime configuration transactionally; serialize renewal and sync using a shared lock.
- Verify: Focused unit tests, runtime config validation, renewed merge comparison, and service/request health.

### Outcome 2: Private automatic delivery
- Work: Replace public SSH CI trigger with repository validation; servers pull canonical rules every two minutes with bounded jitter. Existing credentials are not exported or expanded.
- Verify: Successful CI at released revision; both timers enabled; timer-triggered sync succeeds and caches match canonical source.

### Outcome 3: Production rollout
- Work: Back up each host before deploy; retain current inbound/certificate values and current verified dedicated outbound. Roll out ASMU then ITL with host-local recovery copies.
- Verify: Fresh SSH remains available; both cores active; domain appears in Xray, Sing-box source/runtime, and cache; actual client request selects dedicated policy. Gemini region eligibility remains a separate signed-in acceptance check.
