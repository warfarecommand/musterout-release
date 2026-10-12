"""Validate both projections and their signed data before replacing any file."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from validate_v1 import validate_feed as validate_v1
from validate_v2 import validate_feed as validate_v2


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def verify_signed(script, feed, public_key, key_id):
    if not script.startswith('self.postMessage(') or not script.endswith(');\n'):
        raise ValueError('Unexpected feed script wrapper')
    signed = json.loads(script[len('self.postMessage('):-3])
    if set(signed) != {'envelope', 'signature', 'data'} or canonical(signed['data']) != canonical(feed):
        raise ValueError('Signed data differs from the v2 feed')
    envelope = signed['envelope']
    raw = canonical(feed)
    if set(envelope) != {'product','kind','seq','pack','sha256','size','created','expires','key_id','keychain'}:
        raise ValueError('Unexpected envelope fields')
    if (envelope['product'] != 'Muster Out' or envelope['kind'] != 'feed'
            or envelope['seq'] != feed['seq'] or envelope['created'] != feed['generated_at']
            or envelope['expires'] != feed['expires_at'] or envelope['sha256'] != hashlib.sha256(raw).hexdigest()
            or envelope['size'] != len(raw) or not isinstance(envelope['pack'],str) or not envelope['pack']
            or not isinstance(envelope['keychain'],list) or len(envelope['keychain']) > 16):
        raise ValueError('Envelope does not bind the feed')
    if len(public_key) != 32:
        raise ValueError('Expected a raw Ed25519 public key')
    def verify(message, signature, key):
        with tempfile.TemporaryDirectory(prefix='feed-verify-') as directory:
            root = Path(directory)
            (root/'pub.der').write_bytes(bytes.fromhex('302a300506032b6570032100') + key)
            (root/'message').write_bytes(canonical(message))
            (root/'signature').write_bytes(base64.b64decode(signature, validate=True))
            subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-inkey',str(root/'pub.der'),
                            '-keyform','DER','-in',str(root/'message'),'-sigfile',str(root/'signature')],
                           check=True,capture_output=True)
    trusted = {key_id:public_key}
    for link in envelope['keychain']:
        if set(link) != {'key_id','public_key','signed_by','signature'} or link['key_id'] in trusted or link['signed_by'] not in trusted:
            raise ValueError('Invalid rotation chain')
        message = {'product':'Muster Out','kind':'feed', **{k:link[k] for k in ('key_id','public_key','signed_by')}}
        verify(message,link['signature'],trusted[link['signed_by']])
        key=base64.b64decode(link['public_key'],validate=True)
        if len(key)!=32:
            raise ValueError('Invalid rotation public key')
        trusted[link['key_id']]=key
    if envelope['key_id'] not in trusted:
        raise ValueError('Untrusted feed signing key')
    verify(envelope,signed['signature'],trusted[envelope['key_id']])
    return signed


def sync(downloads, target, public_key, key_id):
    paths = ('latest.json','v2/latest.json','v2/feed.js')
    payloads = {name:(downloads/name).read_bytes() for name in paths}
    if any(len(value)>2_000_000 for value in payloads.values()):
        raise ValueError('Feed exceeds the size limit')
    v1, v2 = [json.loads(payloads[name]) for name in paths[:2]]
    validate_v1(v1,require_complete=False)
    validate_v2(v2)
    if v2.get('capture_replay',False) or v1.get('capture_replay',False):
        raise ValueError('Capture feed cannot be published')
    verify_signed(payloads['v2/feed.js'].decode('utf-8'),v2,public_key,key_id)
    previous=target/'v2/latest.json'
    if previous.exists():
        old=json.loads(previous.read_text())
        if v2['seq']<old['seq'] or (v2['seq']==old['seq'] and canonical(v2)!=canonical(old)):
            raise ValueError('Feed replay or same-sequence replacement')
    marine=next((b for b in v2['sources'] if b['source']=='MARADMIN'),None)
    if marine and marine['status']=='ok':
        if v1['generated_at']!=v2['generated_at'] or v1['checked_to']!=marine['window']['to']:
            raise ValueError('Projection generation mismatch')
        subset=[{k:v for k,v in n.items() if k not in {'series','id'}} for n in marine['notices']
                if v1['checked_from']<=n['posted']<=v1['checked_to']]
        if canonical(subset)!=canonical(v1['notices']):
            raise ValueError('Projection notices mismatch')
    for name,data in payloads.items():
        path=target/name
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and path.read_bytes()==data:
            continue
        temporary=path.with_suffix(path.suffix+'.tmp')
        temporary.write_bytes(data)
        temporary.replace(path)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--downloads',type=Path,required=True)
    parser.add_argument('--target',type=Path,default=Path('feed'))
    args=parser.parse_args()
    try:
        sync(args.downloads,args.target,base64.b64decode(os.environ['MO_FEED_PUBLIC_KEY'],validate=True),os.environ['MO_FEED_KEY_ID'])
    except (KeyError,ValueError,OSError,subprocess.CalledProcessError):
        raise SystemExit('Feed sync failed; existing files preserved until all validations pass')
