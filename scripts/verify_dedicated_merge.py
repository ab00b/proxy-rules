#!/usr/bin/env python3
"""Read-only verification; report no private outbound values."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

def normalized(config):
    config = json.loads(json.dumps(config))
    for rule in config.get('route', {}).get('rules', []):
        if 'outbound' in rule:
            rule.setdefault('action', 'route')
        for key in ('inbound', 'domain', 'domain_suffix'):
            if isinstance(rule.get(key), str):
                rule[key] = [rule[key]]
    return config

h = 'signaler-pa.googleapis.com'
root = Path('/etc/v2ray-agent/sing-box/conf')
c = Path('/var/lib/dedicated-egress/dedicated-egress.list').read_bytes()
s = json.loads((root / 'config.json').read_text())
f = json.loads((root / 'config/90_dedicated_egress.json').read_text())
x = json.loads(Path('/etc/v2ray-agent/xray/conf/13_dedicated_egress.json').read_text())
with tempfile.TemporaryDirectory() as tmp:
    result = subprocess.run(['/etc/v2ray-agent/sing-box/sing-box', 'merge', 'merged.json', '-C', str(root / 'config'), '-D', tmp], capture_output=True)
    assert result.returncode == 0, 'merge failed'
    merged = json.loads((Path(tmp) / 'merged.json').read_text())
    result = subprocess.run(['/etc/v2ray-agent/sing-box/sing-box', 'check', '-c', str(Path(tmp) / 'merged.json')], capture_output=True)
    assert result.returncode == 0, 'merged config invalid'
    assert normalized(merged) == normalized(s), 'renewal merge would change runtime configuration'
print(json.dumps({
 'cache_sha256': hashlib.sha256(c).hexdigest(),
 'cache_has_rule': b'DOMAIN,signaler-pa.googleapis.com' in c,
 'xray_has_rule': any(r.get('outboundTag') == 'dedicated-egress' and 'full:' + h in r.get('domain', []) for r in x['routing']['rules']),
 'sing_box_has_rule': any(r.get('outbound') == 'dedicated-egress' and h in r.get('domain', []) for r in s['route']['rules']),
 'source_matches_live_routes': normalized(f)['route'] == normalized(s)['route'],
 'renewal_merge_matches_live': True,
 'services': subprocess.run(['systemctl', 'is-active', 'xray.service', 'sing-box.service', 'dedicated-egress-sync.timer'], capture_output=True, text=True).stdout.splitlines(),
}))
print(subprocess.run(['systemctl', 'show', 'dedicated-egress-sync.service', '-p', 'Result', '-p', 'ExecMainStartTimestamp', '-p', 'ExecMainStatus'], capture_output=True, text=True).stdout)
