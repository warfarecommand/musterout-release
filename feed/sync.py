"""Validate both projections and their signed data before replacing any file."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import shutil

from validate_v3 import validate_feed as validate_v3, validate_legacy, validate_pair, bounded_json

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


def sync_legacy(downloads, target, public_key, key_id):
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


WIRE_LIMITS = {'latest.json': 250_000, 'v2/latest.json': 2_000_000,
               'v2/feed.js': 2_000_000, 'v3/latest.json': 2_000_000, 'v3/feed.js': 2_000_000}


def read_wire(path, limit):
    if path.stat().st_size > limit:
        raise ValueError('Feed exceeds wire limit')
    raw = path.read_bytes()
    if len(raw) > limit:
        raise ValueError('Feed exceeds wire limit')
    return raw


def verified_v3(script, public_key, key_id):
    if len(script) > WIRE_LIMITS['v3/feed.js']:
        raise ValueError('Feed exceeds wire limit')
    text = script.decode('utf-8')
    if not text.startswith('self.postMessage(') or not text.endswith(');\n'):
        raise ValueError('Invalid feed wrapper')
    transport = bounded_json(json.loads(text[17:-3]))
    expected = canonical(transport).decode('utf-8').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    if text[17:-3] != expected:
        raise ValueError('Noncanonical or duplicate transport fields')
    feed = transport['data']
    validate_v3(feed)
    verify_signed(text, feed, public_key, key_id)
    if transport['envelope']['pack'] != 'usmc-2026.10':
        raise ValueError('Wrong feed pack')
    return feed


def snapshot_id(script, public_key, key_id):
    feed = verified_v3(script, public_key, key_id)
    return str(feed['legacy_seq']) + '-' + str(feed['seq'])


def sync(downloads, target, public_key, key_id, profile='v2', expected_v3=None):
    if profile not in {'v2', 'v3'}:
        raise ValueError('Unknown feed profile')
    if profile == 'v2' and (target / 'v3/latest.json').exists():
        raise ValueError('Dual publication cannot be downgraded to legacy-only sync')
    names = tuple(WIRE_LIMITS) if profile == 'v3' else tuple(WIRE_LIMITS)[:3]
    payloads = {name: read_wire(downloads / name, WIRE_LIMITS[name]) for name in names}
    legacy = json.loads(payloads['v2/latest.json'])
    validate_legacy(legacy)
    if profile == 'v3':
        modern = verified_v3(payloads['v3/feed.js'], public_key, key_id)
        if canonical(json.loads(payloads['v3/latest.json'])) != canonical(modern):
            raise ValueError('V3 projection differs from signed data')
        validate_pair(legacy, modern)
        if expected_v3 is not None and payloads['v3/feed.js'] != expected_v3:
            raise ValueError('Snapshot differs from authenticated latest transport')
        previous = target / 'v3/latest.json'
        if previous.exists():
            old = json.loads(previous.read_bytes())
            if modern['seq'] < old['seq'] or (modern['seq'] == old['seq'] and canonical(modern) != canonical(old)):
                raise ValueError('V3 replay or same-sequence replacement')
    # Run the actual legacy consumer into an isolated target first. It checks
    # v1 canonical parity, signature and existing v2 high-water before any real write.
    with tempfile.TemporaryDirectory(prefix='feed-bundle-') as directory:
        temporary = Path(directory)
        old = target / 'v2/latest.json'
        if old.exists():
            (temporary / 'v2').mkdir()
            shutil.copyfile(old, temporary / 'v2/latest.json')
        sync_legacy(downloads, temporary, public_key, key_id)
    staged = []
    try:
        for name, raw in payloads.items():
            path = target / name
            if path.exists() and path.read_bytes() == raw:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            pending = path.with_suffix(path.suffix + '.tmp')
            staged.append((pending, path))
            pending.write_bytes(raw)
        for pending, path in staged:
            pending.replace(path)
    finally:
        for pending, _ in staged:
            pending.unlink(missing_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--downloads', type=Path)
    parser.add_argument('--target', type=Path, default=Path('feed'))
    parser.add_argument('--profile', choices=['v2', 'v3'], default='v2')
    parser.add_argument('--snapshot-script', type=Path)
    parser.add_argument('--expected-v3', type=Path)
    args = parser.parse_args()
    try:
        public_key = base64.b64decode(os.environ['MO_FEED_PUBLIC_KEY'], validate=True)
        key_id = os.environ['MO_FEED_KEY_ID']
        if args.snapshot_script:
            print(snapshot_id(read_wire(args.snapshot_script, WIRE_LIMITS['v3/feed.js']), public_key, key_id))
        else:
            if args.downloads is None:
                parser.error('--downloads is required for sync')
            expected = read_wire(args.expected_v3, WIRE_LIMITS['v3/feed.js']) if args.expected_v3 else None
            sync(args.downloads, args.target, public_key, key_id, args.profile, expected)
    except (KeyError, ValueError, TypeError, OSError, subprocess.CalledProcessError):
        raise SystemExit('Feed sync failed; no unvalidated files are installed')
