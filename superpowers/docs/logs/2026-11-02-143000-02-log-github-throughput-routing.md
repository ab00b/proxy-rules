# GitHub clone routing acceptance — 2026-11-02

## Diagnosis

A real GitHub Desktop git-remote-https connection to github.com used ITL-snell through the general Smart group. Its observed receive rate was approximately 20–28 KB/s. DNS traces for GitHub, codeload and objects took 12–14 ms. Global Git proxy configuration contained no proxy entries. This identifies an unsuitable selected path for this workload; it does not identify why that node/transport became slow internally.

The same public git/git v2.51.0 shallow clone reproduced 22,095 B/s on ITL-snell (bounded at 12 seconds), while ITL-hy2 completed at 2,500,184 B/s and ASMU-snell at 1,556,996 B/s. The two completed clones had identical HEAD c44beea485f0f2feaf460e2ac87fdd5608d63cf0 and passed connectivity checks. Temporary source-port-scoped rules isolated probe sockets; user clone connections were not switched. The first preflight ITL clone overlapped the end of archive probing; acceptance uses the later sequential clone results.

## Common codeload transfer

A fixed public archive was downloaded or time-bounded for eight ordinary policies. Timeout averages include setup and partial transfer time, not sustained capacity estimates. Every source-port-isolated request's actual Surge final policy matched its requested policy.

| Policy | HTTP | Curl exit | Bytes | Seconds | B/s |
|---|---:|---:|---:|---:|---:|
| ITL-snell | 200 | 28 | 625323 | 12.001 | 52106 |
| ASMU-hy2 | 0 | 28 | 0 | 5.004 | 0 |
| ASMU-snell | 200 | 0 | 11750213 | 5.430 | 2163824 |
| ITL-hy2 | 200 | 0 | 11750213 | 2.985 | 3936522 |
| ASMU-vmess | 200 | 0 | 11750213 | 6.007 | 1956074 |
| ITL-vmess | 200 | 28 | 3809157 | 12.006 | 317270 |
| ASMU-tt | 200 | 28 | 6061523 | 12.005 | 504909 |
| ITL-tt | 200 | 28 | 355978 | 12.002 | 29660 |

## Delivered

- Public `github-download.list` contains only github.com, githubusercontent.com and githubassets.com suffixes. The shared dedicated ISP list and all server routes remain unchanged.
- Visible `🐙 GitHub线路` in 自动分流 uses ordered GitHub-ITL-hy2, GitHub-ASMU-snell, GitHub-ASMU-vmess. These aliases preserve their ordinary-node definitions and set only GitHub-specific HEAD health checks on https://github.com/robots.txt (all returned 200). Interval 180 seconds, group timeout four seconds, reevaluation before use enabled. This is availability fallback, not continuous bandwidth optimization.
- An exact raw.githubusercontent.com rule precedes the remote ruleset to bootstrap downloads through the fast group. Initial resource fetch showed 404 and its first generic-path retry timed out; explicit fast-path probes returned 200. Adding the bootstrap route and refreshing the resource successfully loaded the list.
- Candidate profile syntax passed. Existing configuration is byte-for-byte recoverable by removing only the three task-created alias definitions, group, bootstrap rule/comment and GitHub rule reference. Platform-specific Mac/iOS display requirements and original module-injected settings are preserved. Engine start remained 2026-10-28 21:12:24 +08:00.
- GitHub, API, codeload, SSH, objects, release-assets, media and assets rule explanations resolve to the new group and GitHub-ITL-hy2. Claude, Gemini and ChatGPT retain their intended groups. No task temporary rules remain.
- Local 17 tests, generated Claude view check, narrow GitHub list parse and diff checks passed. [CI](https://github.com/ab00b/proxy-rules/actions/runs/41402463870) passed for source revision 2c0291261a86e8554124fb5cffbdedb6699c7384.

## Final unforced clone

The permanent profile selected GitHub-ITL-hy2 via RULE-SET github-download.list for a fresh ordinary Git clone. No source-port test rule or policy override was used. Surge recorded 12,595,197 received bytes; the clone took 11.023 seconds (~1,142,629 B/s), returned success, reached the same HEAD and passed object connectivity validation. Its process is reported as git-remote-http by this Mac's Git installation; the initial telemetry filter looking only for git-remote-https was corrected using the matching actual request record. This snapshot is distinct from the faster isolated-policy sample.

## Limitations and recovery

The original long-lived GitHub Desktop clone remained on its prior ITL-snell connection at approximately 28 KB/s; it needs a new clone connection to benefit. It was not terminated. No user repository data was modified. No iOS runtime, every repository, custom LFS storage, SSH transfer performance, server-network root cause or long-run bandwidth guarantee is claimed. A reachable but slow preferred node is not automatically rejected by a HEAD health check.

Private client profile recovery and sanitized measurement records are held in the task's private temporary evidence directory. If recovery is needed, remove only the task additions or restore the pre-change profile after checking for subsequent user edits; validate then Reload Profile. No engine restart or server service restart is needed.
