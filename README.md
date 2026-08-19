# proxy-rules

Shared, policy-free routing rules for Surge and Mihomo.

## Dedicated egress

Raw URL:

```text
https://raw.githubusercontent.com/ab00b/proxy-rules/main/dedicated-egress.list
```

Surge:

```ini
RULE-SET,https://raw.githubusercontent.com/ab00b/proxy-rules/main/dedicated-egress.list,🎯 专用代理
```

Mihomo rule provider:

```yaml
rule-providers:
  dedicated-egress:
    type: http
    behavior: classical
    format: text
    url: https://raw.githubusercontent.com/ab00b/proxy-rules/main/dedicated-egress.list
    path: ./providers/DedicatedEgress.list
    interval: 86400
    proxy: 🚀 Proxy

rules:
  - RULE-SET,dedicated-egress,🎯 专用代理
```

The policy and proxy-group names are examples. Define them in each client and
place the rule-set reference before broader global or catch-all rules.

This repository contains match expressions only. It does not contain proxy
nodes, credentials, controller secrets, or private server addresses.

## Server synchronization

ASMU and ITL use `scripts/sync_dedicated_egress.py` to render this same text
list into their Xray and Sing-box JSON configurations. Commented rules remain
documented but are not rendered.

The installed `dedicated-egress-sync.timer` runs two minutes after boot and
then every six hours, with up to five minutes of randomized delay. A GitHub
Actions workflow also requests an immediate sync whenever
`dedicated-egress.list` changes on `main`. The Actions SSH key is restricted on
each server to starting this one sync service; the timer remains the fallback.

Manual immediate synchronization on a server:

```sh
systemctl start dedicated-egress-sync.service
```
