"""Exact REFV32 duplicate_projection_key and extra_block_fresh_release probes."""
from copy import deepcopy
import base64,json,subprocess
from test_sync_v3 import SyncTest,SIGN
from sync import canonical,sync
from validate_v3 import validate_feed
class RefuteTest(SyncTest):
 def test_F02_exact_duplicate_projection_before_any_write(self):
  sync(self.downloads,self.target,self.key,'test','v3');before=self.hashes()
  self.write('v3/latest.json',b'{"seq":0,'+canonical(self.modern)[1:])
  with self.assertRaises(ValueError):sync(self.downloads,self.target,self.key,'test','v3')
  self.assertEqual(before,self.hashes())
 def test_F02_pretty_projection_is_preserved(self):
  pretty=(' \n'+json.dumps(self.modern,indent=2)+'\n').encode();self.write('v3/latest.json',pretty)
  sync(self.downloads,self.target,self.key,'test','v3');self.assertEqual((self.target/'v3/latest.json').read_bytes(),pretty)
 def test_F04_exact_extra_block_fresh_release(self):
  modern=deepcopy(self.modern);next(b for b in modern['sources'] if b['source']=='VA_GOV')['unexpected']='x'
  proof=json.loads(subprocess.check_output(['node','-e',SIGN],input=json.dumps([self.legacy,modern]).encode()));self.key=base64.b64decode(proof['key'])
  self.write('v2/feed.js',proof['scripts'][0].encode());self.write('v3/feed.js',proof['scripts'][1].encode());self.write('v3/latest.json',canonical(modern))
  with self.assertRaises(ValueError):sync(self.downloads,self.target,self.key,'test','v3')
  self.assertEqual(self.hashes(),{})
