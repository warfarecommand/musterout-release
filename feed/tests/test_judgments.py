"""Optional judgment publication must preserve every required feed byte."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'feed'))
from sync import canonical, sync, WIRE_LIMITS, JUDGMENT_PATHS, judgment_payloads


@pytest.fixture
def bundle(tmp_path):
    key = tmp_path / 'synthetic-key.der'
    key.write_bytes(bytes.fromhex('302e020100300506032b657004220420') + os.urandom(32))
    public = subprocess.run(['openssl','pkey','-in',str(key),'-inform','DER','-pubout','-outform','DER'],check=True,capture_output=True).stdout[-32:]
    def sign(message):
        message_path = tmp_path / 'message.json'
        message_path.write_bytes(message)
        return subprocess.run(['openssl','pkeyutl','-sign','-rawin','-inkey',str(key),'-keyform','DER','-in',str(message_path)],check=True,capture_output=True).stdout
    generated = (datetime.now(timezone.utc) - timedelta(seconds=2)).replace(microsecond=0)
    stamp = generated.isoformat().replace('+00:00', 'Z')
    expires = (generated + timedelta(days=8)).isoformat().replace('+00:00', 'Z')
    legacy = json.loads((ROOT / 'feed/v2/latest.json').read_bytes())
    modern = json.loads((ROOT / 'feed/v3/latest.json').read_bytes())
    notice = legacy['sources'][0]['notices'][0]
    notice['posted'] = (generated.date() - timedelta(days=8)).isoformat()
    for value in (legacy, modern):
        value.update(generated_at=stamp, expires_at=expires)
        for block in value['sources']:
            block.update(last_attempt=stamp, last_success=stamp, notices=[],
                         window={'from': (generated.date()-timedelta(days=29)).isoformat(),
                                 'to': generated.date().isoformat()})
    legacy['sources'][0]['notices'] = [notice]
    modern['sources'][:4] = deepcopy(legacy['sources'])
    modern['legacy_sha256'] = hashlib.sha256(canonical(legacy)).hexdigest()
    v1 = json.loads((ROOT / 'feed/latest.json').read_bytes())
    v1.update(generated_at=stamp, checked_from=(generated.date()-timedelta(days=3)).isoformat(),
              checked_to=generated.date().isoformat(), notices=[])
    judgment = {'v': 1, 'kind': 'policy', 'summary': 'The policy provides administrative guidance.',
                'audience': 'Marines', 'fit': dict.fromkeys(('eas','resign','retire','deciding'), 'no'),
                'depends_on': None, 'action': None, 'evidence': 'This guidance applies to all Marines.',
                'judged': generated.date().isoformat()}
    judgments = {'schema_version': 1, 'seq': modern['seq'], 'generated_at': stamp,
                 'expires_at': expires, 'base_seq': modern['seq'],
                 'base_sha256': hashlib.sha256(canonical(modern)).hexdigest(),
                 'notices': [{'id':notice['id'], 'title':notice['title'],
                              'body_sha256':'a'*64, 'judgment':judgment}]}
    downloads = tmp_path / 'downloads'
    def write(name, raw):
        dest = downloads / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    def signed(data, mutate=None):
        raw = canonical(data)
        envelope = {'product':'Muster Out','kind':'feed','seq':data['seq'],'pack':'usmc-2026.10',
                    'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),
                    'created':data['generated_at'],'expires':data['expires_at'],
                    'key_id':'test','keychain':[]}
        if mutate:
            mutate(envelope)
        transport = {'envelope':envelope,'data':data,
                     'signature':base64.b64encode(sign(canonical(envelope))).decode()}
        return b'self.postMessage(' + canonical(transport).decode().replace('\u2028','\\u2028').replace('\u2029','\\u2029').encode() + b');\n'
    for name, value in [('latest.json',v1),('v2/latest.json',legacy),('v3/latest.json',modern),
                        (JUDGMENT_PATHS[0],judgments)]:
        write(name, json.dumps(value, ensure_ascii=False, indent=2).encode()+b'\n')
    for name, value in [('v2/feed.js',legacy),('v3/feed.js',modern),(JUDGMENT_PATHS[1],judgments)]:
        write(name,signed(value))
    return downloads, tmp_path/'target', public, modern, judgments, write, signed


def apply(bundle):
    downloads, target, public, *_ = bundle
    sync(downloads,target,public,'test','v3', (downloads/'v3/feed.js').read_bytes())
    for name in WIRE_LIMITS:
        assert (target/name).read_bytes() == (downloads/name).read_bytes()


def test_pass_through_is_byte_identical_and_idempotent(bundle):
    apply(bundle)
    apply(bundle)
    for name in JUDGMENT_PATHS:
        assert (bundle[1]/name).read_bytes() == (bundle[0]/name).read_bytes()


FAILURES = ['missing_json','missing_js','missing_both','html_json','html_js','invalid_json',
            'duplicate_json','duplicate_transport','noncanonical','utf8','large_json','large_js',
            'deep_json','signature','unknown_key','bad_chain','projection_mismatch',
            'seq','base_seq','base_hash','generated','expires','unknown_id','wrong_title',
            'duplicate_id','body_hash','judgment_fields','future_judged','summary','fit',
            'envelope_hash','envelope_size','envelope_seq','envelope_created',
            'envelope_expires','envelope_kind','envelope_product','envelope_pack']


def corrupt(bundle, case):
    downloads, _, _, modern, judgments, write, signed = bundle
    value = deepcopy(judgments)
    js = downloads/JUDGMENT_PATHS[1]
    if case.startswith('missing_'):
        for name in JUDGMENT_PATHS:
            if case == 'missing_both' or name.endswith('latest.json' if case == 'missing_json' else 'feed.js'):
                (downloads/name).unlink()
        return
    raw_cases = {
        'html_json':(0,b'<html>not a feed</html>'), 'html_js':(1,b'<html>not a feed</html>'),
        'invalid_json':(0,b'{'), 'utf8':(1,b'\xff'),
        'large_json':(0,b' '*2_000_001), 'large_js':(1,b' '*2_000_001),
        'deep_json':(0,b'['*40+b'0'+b']'*40),
        'duplicate_json':(0,canonical(value).replace(b'{',b'{"seq":1,',1)),
        'duplicate_transport':(1,js.read_bytes().replace(b'{',b'{"data":null,',1)),
        'noncanonical':(1,js.read_bytes().replace(b'{',b'{ ',1)),
    }
    if case in raw_cases:
        index, raw = raw_cases[case]; write(JUDGMENT_PATHS[index],raw); return
    if case in {'signature','unknown_key','bad_chain'}:
        transport=json.loads(js.read_bytes()[17:-3])
        if case=='signature': transport['signature']=base64.b64encode(bytes(64)).decode()
        if case=='unknown_key': transport['envelope']['key_id']='unknown'
        if case=='bad_chain': transport['envelope']['keychain']=[None]
        write(JUDGMENT_PATHS[1],b'self.postMessage('+canonical(transport)+b');\n'); return
    if case.startswith('envelope_'):
        field=case.removeprefix('envelope_')
        bad={'hash':'0'*64,'size':1,'seq':1,'created':'2000-01-01T00:00:00Z',
             'expires':'2000-01-09T00:00:00Z','kind':'release','product':'Other','pack':'wrong'}[field]
        write(JUDGMENT_PATHS[1],signed(value,lambda e:e.update({{'hash':'sha256'}.get(field,field):bad})))
        return
    if case=='projection_mismatch':
        value['notices']=[];write(JUDGMENT_PATHS[0],canonical(value));return
    if case=='seq': value['seq']+=1
    if case=='base_seq': value['base_seq']+=1
    if case=='base_hash': value['base_sha256']='0'*64
    if case=='generated': value['generated_at']='2000-01-01T00:00:00Z'
    if case=='expires': value['expires_at']='2000-01-09T00:00:00Z'
    if case=='unknown_id': value['notices'][0]['id']='MARADMIN-999-26'
    if case=='wrong_title': value['notices'][0]['title']='Other title'
    if case=='duplicate_id': value['notices']*=2
    if case=='body_hash': value['notices'][0]['body_sha256']='invalid'
    if case=='judgment_fields': value['notices'][0]['judgment']={}
    if case=='future_judged': value['notices'][0]['judgment']['judged']='9999-01-01'
    if case=='summary': value['notices'][0]['judgment']['summary']='Invalid'
    if case=='fit': value['notices'][0]['judgment']['fit']['eas']='unsupported'
    write(JUDGMENT_PATHS[0],canonical(value)); write(JUDGMENT_PATHS[1],signed(value))


@pytest.mark.parametrize('case',FAILURES)
def test_every_failure_removes_previous_judgments_and_preserves_base(bundle,case):
    apply(bundle)
    corrupt(bundle,case)
    apply(bundle)
    assert all(not (bundle[1]/name).exists() for name in JUDGMENT_PATHS)


def test_empty_feed_is_a_valid_signed_pair(bundle):
    downloads, target, public, modern, judgments, write, signed = bundle
    judgments['notices']=[]
    write(JUDGMENT_PATHS[0],canonical(judgments)); write(JUDGMENT_PATHS[1],signed(judgments))
    apply(bundle)
    assert (target/JUDGMENT_PATHS[1]).exists()


def test_optional_disk_failure_cannot_block_base(bundle,monkeypatch):
    original=Path.write_bytes
    def fail(path,raw):
        if 'judgments' in path.parts and 'target' in path.parts:
            raise OSError('Synthetic optional disk failure')
        return original(path,raw)
    monkeypatch.setattr(Path,'write_bytes',fail)
    apply(bundle)
    assert all(not (bundle[1]/name).exists() for name in JUDGMENT_PATHS)


def package_root(bundle):
    downloads, target, public, *_ = bundle
    root=target.parent/'package-root'
    shutil.copytree(ROOT/'feed',root/'feed',ignore=shutil.ignore_patterns('__pycache__','tests'))
    for name in (*WIRE_LIMITS,*JUDGMENT_PATHS):
        destination=root/'feed'/name
        if (downloads/name).exists():
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(downloads/name,destination)
    shutil.copytree(ROOT/'npm/musterout-feed',root/'npm/musterout-feed')
    config=json.loads((ROOT/'config.json').read_bytes())
    keys={'test':base64.b64encode(public).decode()}
    config['update_keys']['feed_keys']=keys
    (root/'config.json').write_text(json.dumps(config))
    (root/'npm/musterout-feed/public_keys.json').write_text(json.dumps({'feed_keys':keys}))
    return root


@pytest.mark.parametrize('case',[None,*FAILURES])
def test_npm_rechecks_optional_pair_and_removes_stale_package_files(bundle,case):
    if case: corrupt(bundle,case)
    root=package_root(bundle)
    stale=root/'npm/musterout-feed/judgments/v1/feed.js'
    stale.parent.mkdir(parents=True,exist_ok=True);stale.write_text('stale')
    script="""
      import {verifyBundle,preparePackage} from './feed/verify_publish.mjs';
      import assert from 'node:assert/strict';
      const v=verifyBundle('.',{MO_FEED_PUBLIC_KEY:process.argv[1],MO_FEED_KEY_ID:'test'});
      assert.equal(Boolean(v.judgments),process.argv[2]==='true');
      assert(preparePackage('.',v,null));
      assert.equal(preparePackage('.',v,'1.0.'+v.seq),false);
    """
    subprocess.run(['node','--input-type=module','-e',script,base64.b64encode(bundle[2]).decode(),str(case is None).lower()],cwd=root,check=True,capture_output=True)
    for name in WIRE_LIMITS:
        if name.endswith('feed.js'):
            path='feed.js' if name.startswith('v2/') else name
            assert (root/'npm/musterout-feed'/path).read_bytes()==(bundle[0]/name).read_bytes()
    for name in JUDGMENT_PATHS:
        packed=root/'npm/musterout-feed'/name
        assert packed.exists()==(case is None)
        if packed.exists():assert packed.read_bytes()==(bundle[0]/name).read_bytes()


@pytest.mark.parametrize('case',[None,'missing_json','missing_js','missing_both','html_js'])
def test_actual_download_workflow_keeps_required_sync_on_optional_http_failure(bundle,case):
    if case:corrupt(bundle,case)
    root=package_root(bundle)
    workflow=(ROOT/'.github/workflows/sync-feed.yml').read_text()
    step=workflow.split('      - name: Download and validate public feeds\n',1)[1].split('      - name:',1)[0]
    import textwrap
    shell=textwrap.dedent(step.split('        run: |\n',1)[1])
    binary=root/'bin';binary.mkdir()
    curl=binary/'curl'
    curl.write_text('''#!/usr/bin/env python3
import os,sys
from pathlib import Path
args=sys.argv[1:]
url=next(arg for arg in args if arg.startswith('https://'))
name=url.split('/feed/',1)[1]
if name.startswith('snapshots/'):name=name.split('/',2)[2]
source=Path(os.environ['RELJUDGE_DOWNLOADS'])/name
dest=Path(args[args.index('-o')+1])
if not source.exists():
    dest.write_text('partial failed transfer')
    raise SystemExit(22)
dest.write_bytes(source.read_bytes())
''')
    curl.chmod(0o755)
    runner=root/'runner';runner.mkdir()
    env={**os.environ,'PATH':str(binary)+os.pathsep+os.environ['PATH'],
         'RUNNER_TEMP':str(runner),'MO_FEED_PROFILE':'v3',
         'MO_FEED_PUBLIC_KEY':base64.b64encode(bundle[2]).decode(),'MO_FEED_KEY_ID':'test',
         'RELJUDGE_DOWNLOADS':str(bundle[0])}
    subprocess.run(['bash','-c',shell],cwd=root,env=env,check=True,capture_output=True)
    for name in WIRE_LIMITS:
        assert (root/'feed'/name).read_bytes()==(bundle[0]/name).read_bytes()
    for name in JUDGMENT_PATHS:
        assert (root/'feed'/name).exists()==(case is None)
