#!/usr/bin/env python3
"""One-time host-local repair; never exports private proxy configuration."""
import datetime
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess


def run(*args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f'{args[0]} {args[1]} failed (exit {p.returncode}); inspect host-local logs')
    return p.stdout


def main():
    os.umask(0o077)
    root = Path('/etc/v2ray-agent/sing-box/conf')
    live = root / 'config.json'
    fragment = root / 'config/90_dedicated_egress.json'
    sync = Path('/usr/local/sbin/dedicated-egress-sync')
    refresh = Path('/usr/local/sbin/refresh-sing-box-tls-config')
    timer = Path('/etc/systemd/system/dedicated-egress-sync.timer')
    cache = Path('/var/lib/dedicated-egress/dedicated-egress.list')
    xray = Path('/etc/v2ray-agent/xray/conf/13_dedicated_egress.json')
    backup = Path('/root/dedicated-sync-repair-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(mode=0o700)
    paths = [live, fragment, sync, refresh, timer, cache, xray]
    existed = {}
    for i, p in enumerate(paths):
        existed[str(p)] = p.exists()
        if p.exists():
            shutil.copy2(p, backup / str(i))
    (backup / 'manifest.json').write_text(json.dumps({'paths': [str(p) for p in paths], 'existed': existed}))
    states = {s: subprocess.run(['systemctl', 'is-active', s], capture_output=True, text=True).stdout.strip() for s in ['sing-box.service', 'xray.service']}
    (backup / 'service-states.json').write_text(json.dumps(states))
    print('backup', backup, flush=True)
    with open('/run/lock/dedicated-egress-config.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        current = json.loads(live.read_text())
        old = json.loads((root / 'config.json.dedicated-egress-sync.previous').read_text())
        assert not current.get('route') and not current.get('outbounds'), 'Unexpected live routes; stop instead of overwrite'
        assert not fragment.exists(), 'Fragment already exists; stop instead of overwrite'
        matches = []
        for f in Path('/etc/v2ray-agent/xray/conf').glob('*.json'):
            matches.extend(o for o in json.loads(f.read_text()).get('outbounds', []) if o.get('tag') == 'dedicated-egress')
        assert len(matches) == 1 and matches[0]['protocol'] == 'socks'
        s = matches[0]['settings']
        outbound = {'type': 'socks', 'tag': 'dedicated-egress', 'server': s['address'], 'server_port': s['port'], 'version': '5'}
        if s.get('user'):
            outbound.update(username=s['user'], password=s['pass'])
        source = {'route': old['route'], 'outbounds': [outbound, {'type': 'direct', 'tag': 'default-egress'}]}
        candidate = dict(current, **source)
        assert candidate['inbounds'] == current['inbounds']
        candidate_path = backup / 'candidate.json'
        candidate_path.write_text(json.dumps(candidate, indent=2) + '\n')
        run('/etc/v2ray-agent/sing-box/sing-box', 'check', '-c', str(candidate_path))
        try:
            fragment.write_text(json.dumps(source, indent=2) + '\n')
            shutil.copyfile(candidate_path, live)
            shutil.copyfile('/root/dedicated-sync-stage/sync_dedicated_egress.py', sync)
            os.chmod(sync, 0o700)
        except Exception:
            for i,p in enumerate(paths):
                if existed[str(p)]: shutil.copy2(backup / str(i), p)
                elif p.exists(): p.unlink()
            raise
    try:
        run('/usr/local/sbin/dedicated-egress-sync')
        # Bootstrap restored routing differs from the running pre-repair config.
        # Sync normally restarts it because canonical rules also changed.
        run('systemctl', 'is-active', '--quiet', 'sing-box.service')
        run('systemctl', 'is-active', '--quiet', 'xray.service')
        shutil.copyfile('/root/dedicated-sync-stage/refresh-sing-box-tls-config', refresh)
        os.chmod(refresh, 0o700)
        shutil.copyfile('/root/dedicated-sync-stage/dedicated-egress-sync.timer', timer)
        run('systemctl', 'daemon-reload')
        run('systemctl', 'enable', '--now', 'dedicated-egress-sync.timer')
        run('systemctl', 'restart', 'dedicated-egress-sync.timer')
    except Exception:
        with open('/run/lock/dedicated-egress-config.lock', 'a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            for i,p in enumerate(paths):
                if existed[str(p)]: shutil.copy2(backup / str(i), p)
                elif p.exists(): p.unlink()
        subprocess.run(['systemctl', 'daemon-reload'], capture_output=True)
        for service, state in states.items():
            subprocess.run(['systemctl', 'restart' if state == 'active' else 'stop', service], capture_output=True)
        raise
    print('repair_applied', flush=True)

if __name__ == '__main__':
    main()
