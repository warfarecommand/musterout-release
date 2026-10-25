"""Actual sync transaction proof with ephemeral in-memory Node test keys."""
from copy import deepcopy
import base64
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from test_contract_v3 import pair, FIXTURES
from sync import canonical, sync, snapshot_id

SIGN = r'''const fs=require('node:fs'),c=require('node:crypto'),x=JSON.parse(fs.readFileSync(0,'utf8'));
function canon(v){return v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canon).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canon(v[k])).join(',')+'}';}
const k=c.generateKeyPairSync('ed25519');function wrap(d){const raw=canon(d),e={product:'Muster Out',kind:'feed',seq:d.seq,pack:'usmc-2026.10',sha256:c.createHash('sha256').update(raw).digest('hex'),size:Buffer.byteLength(raw),created:d.generated_at,expires:d.expires_at,key_id:'test',keychain:[]};return 'self.postMessage('+canon({envelope:e,signature:c.sign(null,Buffer.from(canon(e)),k.privateKey).toString('base64'),data:d}).replaceAll('\u2028','\\u2028').replaceAll('\u2029','\\u2029')+');\n';}
console.log(JSON.stringify({key:k.publicKey.export({type:'spki',format:'der'}).subarray(-32).toString('base64'),scripts:x.map(wrap)}));'''


class SyncTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='v32-sync-')
        self.root = Path(self.tmp.name); self.downloads = self.root / 'download'; self.target = self.root / 'target'
        self.legacy, self.modern = pair()
        result = subprocess.run(['node', '-e', SIGN], input=json.dumps([self.legacy, self.modern]), text=True, capture_output=True, check=True)
        value = json.loads(result.stdout); self.key = base64.b64decode(value['key']); self.scripts = value['scripts']
        self.write('latest.json', (FIXTURES / 'v1.json').read_bytes())
        for name, data, script in [('v2', self.legacy, self.scripts[0]), ('v3', self.modern, self.scripts[1])]:
            self.write(name+'/latest.json', canonical(data)); self.write(name+'/feed.js', script.encode())

    def tearDown(self): self.tmp.cleanup()
    def write(self, name, raw):
        path = self.downloads / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    def hashes(self): return {str(p.relative_to(self.target)): p.read_bytes() for p in self.target.rglob('*') if p.is_file()}

    def test_real_legacy_and_dual_consumer_and_retry(self):
        sync(self.downloads, self.target, self.key, 'test')
        self.assertEqual(set(self.hashes()), {'latest.json', 'v2/latest.json', 'v2/feed.js'})
        sync(self.downloads, self.target, self.key, 'test', 'v3', self.scripts[1].encode())
        before = self.hashes(); self.assertEqual(len(before), 5)
        sync(self.downloads, self.target, self.key, 'test', 'v3')
        self.assertEqual(self.hashes(), before)
        with self.assertRaises(ValueError): sync(self.downloads, self.target, self.key, 'test')
        self.assertEqual(self.hashes(), before)
        self.assertEqual(snapshot_id(self.scripts[1].encode(), self.key, 'test'), str(self.legacy['seq'])+'-'+str(self.modern['seq']))

    def test_corrupt_projection_snapshot_and_oversize_preserve_targets(self):
        sync(self.downloads, self.target, self.key, 'test', 'v3'); before = self.hashes()
        for mutation in ['projection', 'snapshot', 'oversize', 'signature']:
            original = (self.downloads / 'v3/latest.json').read_bytes(); script = (self.downloads / 'v3/feed.js').read_bytes()
            try:
                if mutation == 'projection':
                    value = deepcopy(self.modern); value['legacy_sha256'] = '0'*64; self.write('v3/latest.json', canonical(value))
                if mutation == 'oversize': self.write('v3/latest.json', b' ' * 2_000_001)
                if mutation == 'signature': self.write('v3/feed.js', script.replace(b'"signature":"', b'"signature":"A', 1))
                with self.subTest(mutation=mutation), self.assertRaises((ValueError, subprocess.CalledProcessError)):
                    sync(self.downloads, self.target, self.key, 'test', 'v3', b'wrong' if mutation == 'snapshot' else None)
                self.assertEqual(self.hashes(), before)
            finally:
                self.write('v3/latest.json', original); self.write('v3/feed.js', script)

    def test_same_sequence_replacement_and_rollback_preserve_targets(self):
        sync(self.downloads, self.target, self.key, 'test', 'v3'); before = self.hashes()
        old = json.loads((self.target/'v3/latest.json').read_bytes()); old['legacy_sha256'] = '0'*64
        (self.target/'v3/latest.json').write_bytes(canonical(old)); altered = self.hashes()
        with self.assertRaises(ValueError): sync(self.downloads, self.target, self.key, 'test', 'v3')
        self.assertEqual(self.hashes(), altered)
        old['seq'] += 2; (self.target/'v3/latest.json').write_bytes(canonical(old)); higher = self.hashes()
        with self.assertRaises(ValueError): sync(self.downloads, self.target, self.key, 'test', 'v3')
        self.assertEqual(self.hashes(), higher)


if __name__ == '__main__': unittest.main()
