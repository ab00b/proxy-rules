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
