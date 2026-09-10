import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.sync_dedicated_egress import apply


class DurableMergeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.xray, self.runtime, self.fragment, self.cache = [root / n for n in ('xray.json', 'runtime.json', 'fragment.json', 'cache.list')]
        route = {'rules': [
            {'domain': ['old.example'], 'outbound': 'dedicated-egress'},
            {'domain_suffix': ['old.example'], 'outbound': 'dedicated-egress'},
        ], 'final': 'default-egress'}
        self.source = {'route': route, 'outbounds': [{'tag': 'default-egress', 'type': 'direct'}]}
        self.inbounds = [{'type': 'hysteria2', 'tls': {'certificate_path': '/current/cert'}}]
        self.xray.write_text(json.dumps({'routing': {'rules': [{'domain': ['full:old.example'], 'outboundTag': 'dedicated-egress'}]}}))
        self.fragment.write_text(json.dumps(self.source))
        self.runtime.write_text(json.dumps(dict(copy.deepcopy(self.source), inbounds=self.inbounds)))
        self.cache.write_text('old cache')

    def run_sync(self, dry_run=False):
        return apply('DOMAIN,signaler-pa.googleapis.com\nDOMAIN-SUFFIX,example.org\n', self.xray, self.runtime, self.cache, 'xray', 'sing-box', 'xray.service', 'sing-box.service', False, dry_run, self.fragment)

    @patch('scripts.sync_dedicated_egress.run_checked')
    def test_sync_survives_renewal_merge_and_preserves_tls(self, checked):
        self.run_sync()
        live = json.loads(self.runtime.read_text())
        source = json.loads(self.fragment.read_text())
        rebuilt = dict(source, inbounds=self.inbounds)
        self.assertEqual(live, rebuilt)
        self.assertEqual(live['inbounds'], self.inbounds)
        self.assertEqual(source['route']['rules'][0]['domain'], ['signaler-pa.googleapis.com'])
        checked.reset_mock()
        result = self.run_sync()
        self.assertFalse(result['xray_changed'])
        self.assertFalse(result['sing_box_changed'])
        self.assertFalse(any(c.args[0][:2] == ['systemctl', 'restart'] for c in checked.call_args_list))

    @patch('scripts.sync_dedicated_egress.subprocess.run')
    @patch('scripts.sync_dedicated_egress.run_checked', side_effect=RuntimeError('validation failed'))
    def test_failure_restores_source_runtime_and_cache(self, checked, run):
        before = {p: p.read_bytes() for p in (self.xray, self.runtime, self.fragment, self.cache)}
        with self.assertRaises(RuntimeError):
            self.run_sync()
        for p, content in before.items():
            self.assertEqual(p.read_bytes(), content)

    def test_dry_run_does_not_change_source_or_runtime(self):
        before = {p: p.read_bytes() for p in (self.xray, self.runtime, self.fragment, self.cache)}
        self.run_sync(dry_run=True)
        for p, content in before.items():
            self.assertEqual(p.read_bytes(), content)
