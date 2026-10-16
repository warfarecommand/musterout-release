#!/usr/bin/env python3
"""Muster Out protocol 1 verifier. Standard library only. Public bytes only.

This file runs only after an independently supplied SHA-256 pin is checked.
Never import downloaded product code. CLI input/output contains public data only.
"""
import base64
import datetime as dt
import decimal
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request

MAX_BYTES = 2_000_000
MAX_TOTAL = 16_000_000
MAX_FILES = 256
V0 = '0.2.13'
PACK = 'usmc-2026.10'
ROOTS = {
    'release': {'release-2026-10-6da55817': 'lJHnis3XITfBHO3iy0tBM60/QydDw4fe4R3Znh6wuwY='},
    'feed': {'feed-2026-10-05bbe934': 'Wu+hyhxyklR3J/HQsbRq6XkCcWjNmiunuCfCb3G8TLo='},
}
MIRRORS = ['https://cdn.jsdelivr.net/npm/musterout@', 'https://unpkg.com/musterout@']
FEEDS = ['https://watch.warfarecommand.com/feed/v2/feed.js', 'https://raw.githubusercontent.com/warfarecommand/musterout-release/main/feed/v2/feed.js']
PREFIX = '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,sans-serif;background:#fafaf9}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
SUFFIX = '</body></html>'
REQUIRED = ['SETUP.md','WEEKLY.md','UPDATE.md','CLAUDE.md','SUPPORT.md','config.json','CHANGELOG.md','board/board.html','board/board.publish.html','.claude/skills/intake/SKILL.md','.claude/skills/board/SKILL.md','.claude/skills/update/SKILL.md','.claude/skills/watch/SKILL.md']
OPTIONAL = ['PROJECT.md', 'COACH.md', 'board/coach.js', 'workflows/appointment-collisions.md', 'workflows/call-brief.md', 'workflows/household-coverage.md', 'workflows/income-runway.md', 'workflows/move-decision.md', 'workflows/resume-skills-gap.md', 'workflows/school-comparison.md', 'workflows/spouse-brief.md', 'workflows/tap-evidence.md', 'workflows/va-status.md']
# RFC 8032 section 7.1 test 1. Both ports run the same positive and negative.
VECTOR_KEY = 'd75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a'
VECTOR_SIG = 'e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b'


def need(ok, code):
    if not ok:
        raise ValueError(code)


def canonical(v, depth=0):
    need(depth <= 100, 'json_depth')
    if v is None or type(v) in (str, bool):
        if type(v) is str:
            v.encode('utf-8')  # Reject unpaired surrogates.
        return json.dumps(v, ensure_ascii=False, separators=(',', ':'))
    if type(v) is int:
        need(abs(v) <= 9007199254740991, 'unsafe_number')
        return str(v)
    if type(v) is list:
        return '[' + ','.join(canonical(x, depth+1) for x in v) + ']'
    need(type(v) is dict, 'invalid_json_value')
    need(all(type(k) is str and re.fullmatch(r'[\x20-\x7e]+', k) for k in v), 'invalid_key')
    return '{' + ','.join(canonical(k) + ':' + canonical(v[k], depth+1) for k in sorted(v)) + '}'


def parse(raw):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES, 'transport_size')
    def pairs(items):
        out = {}
        for k, v in items:
            need(k not in out, 'duplicate_key')
            out[k] = v
        return out
    def number(s):
        exponent = re.search(r'[eE]([+-]?\d+)$', s)
        need(exponent is None or abs(int(exponent[1])) <= 10000, 'unsafe_number')
        value = decimal.Decimal(s)
        need(value == value.to_integral_value() and abs(value) <= 9007199254740991, 'unsafe_number')
        return int(value)
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_float=number,
                       parse_constant=lambda _: need(False, 'unsafe_number'))
    canonical(value)
    return value


def wrapper(raw, kind):
    need(type(raw) is bytes and raw.startswith(b'self.postMessage(') and raw.endswith(b');\n') and len(raw) <= MAX_BYTES, 'invalid_wrapper')
    value = parse(raw[17:-3])
    exact(value, ['envelope','signature','html' if kind == 'release' else 'data'])
    return value


def exact(v, keys):
    need(type(v) is dict and set(v) == set(keys), 'invalid_fields')


def b64(s, size):
    need(type(s) is str, 'invalid_base64')
    raw = base64.b64decode(s, validate=True)
    need(len(raw) == size and base64.b64encode(raw).decode() == s, 'invalid_base64')
    return raw


# Extended Edwards coordinates, RFC 8032 equation with strict subgroup checks.
P = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
D = -121665 * pow(121666, P - 2, P) % P
I = pow(2, (P - 1) // 4, P)
IDENTITY = (0, 1, 1, 0)


def add(a, b):
    x, y, z, t = a
    X, Y, Z, T = b
    A, B = (y-x)*(Y-X) % P, (y+x)*(Y+X) % P
    C, E = 2*D*t*T % P, 2*z*Z % P
    return ((B-A)*(E-C) % P, (E+C)*(B+A) % P, (E-C)*(E+C) % P, (B-A)*(B+A) % P)


def mul(a, n):
    r = IDENTITY
    while n:
        if n & 1:
            r = add(r, a)
        a = add(a, a)
        n >>= 1
    return r


def equal(a, b):
    return (a[0]*b[2]-b[0]*a[2]) % P == 0 and (a[1]*b[2]-b[1]*a[2]) % P == 0


def point(raw):
    n = int.from_bytes(raw, 'little')
    y, sign = n & (2**255-1), n >> 255
    need(y < P, 'bad_signature')
    xx = (y*y-1)*pow(D*y*y+1, P-2, P) % P
    x = pow(xx, (P+3)//8, P)
    if (x*x-xx) % P:
        x = x*I % P
    need((x*x-xx) % P == 0 and not (x == 0 and sign), 'bad_signature')
    if x & 1 != sign:
        x = P-x
    return (x, y, 1, x*y % P)


BASE = point(bytes.fromhex('5866666666666666666666666666666666666666666666666666666666666666'))


def edverify(key, sig, message):
    try:
        need(len(key) == 32 and len(sig) == 64, 'bad_signature')
        a, r, s = point(key), point(sig[:32]), int.from_bytes(sig[32:], 'little')
        need(s < L and not equal(a, IDENTITY) and not equal(r, IDENTITY), 'bad_signature')
        need(equal(mul(a, L), IDENTITY) and equal(mul(r, L), IDENTITY), 'bad_signature')
        h = int.from_bytes(hashlib.sha512(sig[:32]+key+message).digest(), 'little') % L
        return equal(mul(BASE, s), add(r, mul(a, h)))
    except (ValueError, OverflowError):
        return False


def preflight():
    key, sig = bytes.fromhex(VECTOR_KEY), bytes.fromhex(VECTOR_SIG)
    need(edverify(key, sig, b'') and not edverify(key, sig, b'x'), 'runtime_unavailable')
    need(hashlib.sha256(b'abc').hexdigest() == 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad', 'runtime_unavailable')
    return {'protocol': 1, 'positive': True, 'modified_rejected': True}


def signed(key, sig, message):
    need(edverify(b64(key, 32), b64(sig, 64), canonical(message).encode()), 'bad_signature')


def stamp(s):
    need(type(s) is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{3})?Z', s), 'invalid_time')
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()


def day(s):
    need(type(s) is str and re.fullmatch(r'\d{4}-\d\d-\d\d', s), 'invalid_day')
    return dt.date.fromisoformat(s)


def version(v):
    need(type(v) is str and len(v) <= 128 and re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', v), 'invalid_version')
    return tuple(int(x) for x in v.split('.'))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def hashcheck(raw, sha, size=None):
    need(type(raw) is bytes and len(raw) <= MAX_BYTES, 'transport_size')
    need(type(sha) is str and re.fullmatch(r'[a-f0-9]{64}', sha), 'invalid_hash')
    need(digest(raw) == sha, 'hash_mismatch')
    if size is not None:
        need(type(size) is int and 0 < size <= MAX_BYTES and len(raw) == size, 'size_mismatch')


def envelope(e, sig, payload, kind, pack=PACK, roots=None):
    fields = ['product','kind','pack','sha256','size','created','key_id','keychain']
    fields += ['seq','expires'] if kind == 'feed' else ['version']
    if kind == 'release':
        fields += ['notes','correction','impact']
    need(kind in ('release','install','feed'), 'wrong_kind')
    exact(e, fields)
    need(e['product'] == 'Muster Out' and e['kind'] == kind and e['pack'] == pack, 'wrong_identity')
    stamp(e['created'])
    need(type(e['key_id']) is str and 0 < len(e['key_id'].encode('utf-16-le'))//2 <= 128, 'invalid_key_id')
    if kind != 'feed':
        version(e['version'])
    else:
        need(type(e['seq']) is int and 0 < e['seq'] <= 9007199254740991 and stamp(e['expires']) > stamp(e['created']), 'invalid_sequence')
    scope = 'feed' if kind == 'feed' else 'release'
    trusted = dict((roots or ROOTS)[scope])
    need(type(e['keychain']) is list and len(e['keychain']) <= 16, 'invalid_keychain')
    for link in e['keychain']:
        exact(link, ['key_id','public_key','signed_by','signature'])
        need(type(link['key_id']) is str and 0 < len(link['key_id'].encode('utf-16-le'))//2 <= 128 and link['key_id'] not in trusted and link['signed_by'] in trusted, 'invalid_keychain')
        b64(link['public_key'], 32)
        signed(trusted[link['signed_by']], link['signature'], dict(product=e['product'], kind=scope, **{k: link[k] for k in ['key_id','public_key','signed_by']}))
        trusted[link['key_id']] = link['public_key']
    need(e['key_id'] in trusted, 'untrusted_key')
    signed(trusted[e['key_id']], sig, e)
    hashcheck(payload, e['sha256'], e['size'])
    return e


def notes(v):
    need(type(v) is list and len(v) == 2 and all(type(s) is str and s.strip() and len(s.encode('utf-16-le'))//2 <= 500 for s in v), 'invalid_notes')


def release(raw, selected, pack=PACK, roots=None):
    t = wrapper(raw, 'release')
    need(type(t['html']) is str, 'invalid_document')
    e = envelope(t['envelope'], t['signature'], t['html'].encode(), 'release', pack, roots)
    need(e['version'] == selected, 'wrong_version')
    notes(e['notes'])
    need(type(e['correction']) is bool and (e['impact'] is None or type(e['impact']) is str and len(e['impact'].encode('utf-16-le'))//2 <= 1000) and (not e['correction'] or e['impact'] and e['impact'].strip()), 'invalid_impact')
    need(t['html'].startswith(PREFIX) and t['html'].endswith(SUFFIX), 'invalid_document')
    need('var VERSION = ' + json.dumps(selected) + ';' in t['html'], 'document_version')
    return t


def safe_path(p):
    need(type(p) is str and 0 < len(p) <= 240 and re.fullmatch(r'[A-Za-z0-9_./-]+', p), 'unsafe_path')
    parts = p.split('/')
    need(all(x not in ('', '.', '..') for x in parts), 'unsafe_path')
    low = [x.lower() for x in parts]
    need(not any(x == '.git' or x.startswith('.env') for x in low), 'unsafe_path')
    need(low[0] not in ('my','npm','feed') and low[:2] != ['supabase','migrations'], 'unsafe_path')
    need(p.lower() not in ('install.json','release.json','release.js','verify.py','verify.cjs'), 'unsafe_path')
    return p


def install(raw, selected, pack=PACK, roots=None):
    t = parse(raw)
    exact(t, ['envelope','signature','manifest'])
    m = t['manifest']
    e = envelope(t['envelope'], t['signature'], canonical(m).encode(), 'install', pack, roots)
    exact(m, ['schema_version','product','version','released','pack','notes','files','release'])
    need(type(m['schema_version']) is int and m['schema_version'] == 1 and m['product'] == e['product'] and m['version'] == e['version'] == selected and m['pack'] == pack, 'manifest_identity')
    day(m['released'])
    notes(m['notes'])
    need(type(m['files']) is dict and 0 < len(m['files']) <= MAX_FILES, 'file_count')
    seen = set()
    for p, sha in m['files'].items():
        safe_path(p)
        need(p.lower() not in seen, 'case_collision')
        seen.add(p.lower())
        need(type(sha) is str and re.fullmatch(r'[a-f0-9]{64}', sha), 'invalid_hash')
    need(all(p in m['files'] for p in REQUIRED), 'missing_required_file')
    offered = [p in m['files'] for p in OPTIONAL]
    need(all(offered) or not any(offered), 'partial_optional_set')
    r = m['release']
    exact(r, ['path','sha256','size','html_sha256','html_size'])
    need(r['path'] == 'release.js', 'release_path')
    for key in ['sha256','html_sha256']:
        need(type(r[key]) is str and re.fullmatch(r'[a-f0-9]{64}', r[key]), 'invalid_hash')
    for key in ['size','html_size']:
        need(type(r[key]) is int and 0 < r[key] <= MAX_BYTES, 'transport_size')
    return t


def package_check(i, rraw, selected, files, pack=PACK, roots=None):
    t = install(i, selected, pack, roots)
    m = t['manifest']
    r = release(rraw, selected, pack, roots)
    hashcheck(rraw, m['release']['sha256'], m['release']['size'])
    need(m['release']['html_sha256'] == r['envelope']['sha256'] and m['release']['html_size'] == r['envelope']['size'] and m['notes'] == r['envelope']['notes'], 'release_binding')
    need(type(files) is dict and set(files) == set(m['files']), 'file_set')
    need(len(i)+len(rraw)+sum(len(x) for x in files.values()) <= MAX_TOTAL, 'aggregate_limit')
    for p, sha in m['files'].items():
        hashcheck(files[p], sha)
    html = r['html'].encode()
    need(files['board/board.publish.html'] == html and files['board/board.html'] == r['html'][len(PREFIX):-len(SUFFIX)].encode(), 'fragment_binding')
    config = parse(files['config.json'])
    need(config['product'] == 'Muster Out' and config['version'] == selected and config['pack'] == pack and config['update_keys'] == ({'release_keys': roots['release'], 'feed_keys': roots['feed']} if roots else ROOTS_CONFIG), 'config_binding')
    embedded = re.search(r'window\.MusterOutUpdateConfig=(\{[^\n]+?\});', r['html'])
    need(embedded is not None, 'embedded_config_missing')
    embedded = parse(embedded[1].encode())
    need(embedded == dict(product='Muster Out',version=selected,pack=pack,release_keys=config['update_keys']['release_keys'],feed_keys=config['update_keys']['feed_keys']), 'embedded_config_binding')
    changelog = files['CHANGELOG.md'].decode('utf-8')
    match = re.search(r'^## ' + re.escape(selected) + r' \((\d{4}-\d\d-\d\d)\)\n(.*?)(?=^## |\Z)', changelog, re.M | re.S)
    need(match and match[1] == m['released'] and [x[2:].strip() for x in match[2].splitlines() if x.startswith('- ')] == m['notes'], 'changelog_binding')
    return {'install': t, 'release': r}


ROOTS_CONFIG = {'release_keys': ROOTS['release'], 'feed_keys': ROOTS['feed']}


def plain(s, limit):
    need(type(s) is str and s.strip() and len(s.encode('utf-16-le'))//2 <= limit and not re.search(r'[<>\x00-\x1f\x7f-\x9f]', s), 'invalid_text')


def feed_shape(data):
    def clean(value):
        if type(value) is str:
            need(not re.search(r'[\x00-\x1f\x7f-\x9f]', value), 'feed_controls')
        elif type(value) is dict:
            for k, v in value.items():
                clean(k); clean(v)
        elif type(value) is list:
            for v in value: clean(v)
    clean(data)
    need(type(data) is dict and data.get('schema_version') == 2 and type(data['schema_version']) is int and data.get('capture_replay') is False, 'feed_schema')
    need({'schema_version','seq','generated_at','expires_at','capture_replay','sources'} <= data.keys(), 'feed_fields')
    sources = data.get('sources')
    need(type(sources) is list and 0 < len(sources) <= 4, 'feed_sources')
    seen = set()
    for s in sources:
        need(type(s) is dict and {'source','coverage','status','reason','last_attempt','last_success','window','checked_count','unclassified_count','truncated','body_available','notices'} <= s.keys(), 'source_fields')
        name = s.get('source')
        need(name in ('MARADMIN','ALMAR','ALNAV','ORDER') and name not in seen, 'feed_source')
        seen.add(name)
        plain(s.get('coverage'), 500)
        need(s.get('status') in ('ok','failed'), 'source_status')
        attempt = stamp(s.get('last_attempt'))
        success = None if s.get('last_success') is None else stamp(s['last_success'])
        need(attempt <= stamp(data['generated_at']) and (success is None or success <= attempt), 'source_time')
        need((s['status'] == 'ok' and success is not None and s.get('reason') is None) or (s['status'] == 'failed' and type(s.get('reason')) is str), 'source_status')
        if s['status'] == 'failed':
            plain(s['reason'], 500)
        w = s.get('window')
        exact(w, ['from','to'])
        start, end = day(w['from']), day(w['to'])
        need(0 <= (end-start).days <= 30 and end <= day(data['generated_at'][:10]), 'source_window')
        ns = s.get('notices')
        need(type(ns) is list and len(ns) <= 500, 'notice_count')
        need(type(s.get('checked_count')) is int and len(ns) <= s['checked_count'] <= 9007199254740991 and type(s.get('unclassified_count')) is int and 0 <= s['unclassified_count'] <= s['checked_count'], 'source_count')
        need(success is not None or (not ns and s['checked_count'] == 0), 'source_history')
        need(type(s.get('truncated')) is bool and type(s.get('body_available')) is bool, 'source_flags')
        ids = set()
        for n in ns:
            need(type(n) is dict and {'series','number','id','title','url','posted','body_available','lines','paths'} <= n.keys(), 'notice_fields')
            need(n.get('series') == name, 'notice_series')
            number = n.get('number')
            need(type(number) is str and number.strip(), 'notice_number')
            if name != 'ORDER':
                need(re.fullmatch(r'[0-9]{1,3}/[0-9]{2}', number), 'notice_number')
                identity = name + '-' + number.replace('/', '-')
            else:
                need(len(number.encode('utf-16-le'))//2 <= 120, 'notice_number')
                identity = 'ORDER-' + re.sub(r'[^A-Z0-9]+', '-', number.upper()).strip('-')
            need(n.get('id') == identity and identity not in ids, 'notice_identity')
            ids.add(identity)
            plain(n.get('title'), 300)
            if 'summary' in n:
                plain(n['summary'], 1000)
            if n.get('deadline') is not None:
                day(n['deadline'])
            posted = day(n.get('posted'))
            need(start <= posted <= end, 'notice_window')
            need(type(n.get('body_available')) is bool and (not s['body_available'] or n['body_available']), 'notice_body')
            for key, allowed in [('lines', ['separation','retirement','va','skillbridge','reserve','leave','family']), ('paths', ['resign','retire','eas','all'])]:
                a = n.get(key)
                need(type(a) is list and a and all(x in allowed for x in a) and len(a) == len(set(a)), 'classification')
            for key, allowed in [('action',['required','informational']), ('confidence',['high','medium','low'])]:
                need(key not in n or n[key] in allowed, 'classification')
            u = n.get('url')
            need(type(u) is str and len(u) <= 500 and not re.search(r'%2e', u, re.I) and not re.search(r'[\s<>\\?#@:]|%2f|%5c', u[8:], re.I) and not any(x in ('.','..') for x in u[8:].split('/')), 'notice_url')
            pattern = r'https://www\.marines\.mil/News/Messages/Messages-Display/Article/[0-9]+/[a-zA-Z0-9-]+/' if name in ('MARADMIN','ALMAR') else r'https://www\.mynavyhr\.navy\.mil/(?:References/Messages/|Portals/55/Messages/)[A-Za-z0-9_./%()-]+' if name == 'ALNAV' else r'https://www\.marines\.mil/(?:News/Publications/MCPEL/|Portals/1/Publications/)[A-Za-z0-9_./%()-]+'
            need(re.fullmatch(pattern, u), 'notice_url')


def feed(raw, now, pack=PACK, roots=None, historical=False):
    t = wrapper(raw, 'feed')
    data = t['data']
    e = envelope(t['envelope'], t['signature'], canonical(data).encode(), 'feed', pack, roots)
    need(type(now) in (int, float) and 0 < now < 253402300800, 'clock_unavailable')
    need(data.get('seq') == e['seq'] and type(data.get('seq')) is int and ('pack' not in data or data['pack'] == pack) and data.get('generated_at') == e['created'] and data.get('expires_at') == e['expires'], 'feed_binding')
    start, end = stamp(e['created']), stamp(e['expires'])
    need(end-start == 8*86400 and start <= now < end, 'expired_or_future')
    feed_shape(data)
    return t


def record(raw):
    return b'self.postMessage(' + canonical({k: raw[k] for k in ['envelope','signature','data']}).encode() + b');\n'


def feed_identity(e):
    return canonical({k: e[k] for k in ['seq','created','expires','pack','sha256','size']})


def highwater(records, now, pack=PACK, roots=None):
    need(type(records) is list, 'invalid_records')
    best = None
    identities = {}
    for r in records:
        # Unsigned/invalid legacy metadata is not proof; ignore it.
        try:
            at = stamp(r['accepted_at'])
            need(at <= now and r['highest_seq'] == r['envelope']['seq'], 'invalid_record')
            t = feed(record(r), at, pack, roots, True)
            seq = t['envelope']['seq']
            identity = feed_identity(t['envelope'])
            need(seq not in identities or identities[seq] == identity, 'equivocation')
            identities[seq] = identity
            if best is None or seq > best['envelope']['seq']:
                best = t
        except (KeyError, TypeError, ValueError) as error:
            if str(error) == 'equivocation':
                raise
    return best


def replay(t, records, now, pack=PACK, roots=None):
    best = highwater(records, now, pack, roots)
    if best:
        a, b = t['envelope'], best['envelope']
        need(a['seq'] >= b['seq'], 'replay')
        need(a['seq'] != b['seq'] or feed_identity(a) == feed_identity(b), 'equivocation')
    return t


def target_check(target, to, pack=PACK, roots=None):
    exact(target, ['package','version','pack','mirrors','install','release','release_sha256','html_sha256','html_size','verifier'])
    need(target['package'] == 'musterout' and target['version'] == to and target['pack'] == pack and target['mirrors'] == MIRRORS, 'target_identity')
    i = install(canonical(target['install']).encode(), to, pack, roots)
    e = target['release']['envelope']
    exact(target['release'], ['envelope','signature'])
    # Payload hash is authenticated by the envelope signature; exact bytes checked on retrieval.
    fields = ['product','kind','version','pack','sha256','size','created','key_id','notes','correction','impact','keychain']
    exact(e, fields)
    # Verify with the canonical real payload when retrieved, never create substitute HTML.
    need(e['version'] == to and e['pack'] == pack and e['product'] == 'Muster Out' and e['kind'] == 'release', 'target_identity')
    scope = dict((roots or ROOTS)['release'])
    need(type(e['keychain']) is list and len(e['keychain']) <= 16, 'invalid_keychain')
    for link in e['keychain']:
        exact(link, ['key_id','public_key','signed_by','signature'])
        need(link['key_id'] not in scope and link['signed_by'] in scope, 'invalid_keychain')
        signed(scope[link['signed_by']], link['signature'], dict(product='Muster Out', kind='release', **{k: link[k] for k in ['key_id','public_key','signed_by']}))
        scope[link['key_id']] = link['public_key']
    need(e['key_id'] in scope, 'untrusted_key')
    signed(scope[e['key_id']], target['release']['signature'], e)
    r = i['manifest']['release']
    need(r['sha256'] == target['release_sha256'] and r['html_sha256'] == e['sha256'] == target['html_sha256'] and r['html_size'] == e['size'] == target['html_size'] and i['manifest']['notes'] == e['notes'], 'target_binding')
    v = target['verifier']
    exact(v, ['version','cjs_sha256','py_sha256'])
    version(v['version'])
    need(all(type(v[k]) is str and re.fullmatch(r'[a-f0-9]{64}', v[k]) for k in ['cjs_sha256','py_sha256']), 'verifier_audit')
    return target


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('redirect_refused')


def get(url):
    allowed = url in FEEDS or any(url.startswith(m) and re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)/(?:install.json|release.js|install/[A-Za-z0-9_./-]+)', url[len(m):]) for m in MIRRORS)
    need(allowed, 'unsafe_url')
    req = urllib.request.Request(url, headers={'Accept-Encoding': 'identity'})
    # Empty proxy/cookie handlers: no ambient credentials or redirect handling.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    started = time.monotonic()
    try:
        with opener.open(req, timeout=20) as response:
            need(response.status == 200 and response.url == url and response.headers.get('Content-Encoding', 'identity') == 'identity', 'http_refused')
            parts, size = [], 0
            while True:
                remaining = 20 - (time.monotonic() - started)
                need(remaining > 0, 'http_timeout')
                if response.fp is not None:
                    response.fp.raw._sock.settimeout(remaining)
                chunk = response.read1(min(65536, MAX_BYTES+1-size))
                if not chunk: break
                parts.append(chunk); size += len(chunk)
                need(size <= MAX_BYTES, 'transport_size')
            need(size > 0, 'transport_size')
            return b''.join(parts)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 407, 451):
            raise ValueError('network_policy_refusal') from None
        raise ValueError('http_unavailable') from None
    except http.client.HTTPException:
        raise ValueError('http_unavailable') from None
    except PermissionError:
        raise ValueError('network_policy_refusal') from None
    except urllib.error.URLError as e:
        if isinstance(e.reason, PermissionError):
            raise ValueError('network_policy_refusal') from None
        raise ValueError('http_unavailable') from None


def retrieve(urls, validate, fetch=get):
    good = []
    for url in urls:
        try:
            raw = fetch(url)
            validate(raw)
            good.append(raw)
        except (ValueError, OSError) as e:
            if str(e) in ('network_policy_refusal','aggregate_limit'):
                raise
    need(good, 'unavailable_or_invalid')
    need(all(x == good[0] for x in good), 'mirror_conflict')
    return good[0]


def select_update(selected, current):
    need(version(selected) >= version(V0) and version(selected) > version(current), 'not_newer')
    return selected


def fetch_feed(now, records=(), pack=PACK, fetch=get, roots=None):
    good = []
    for url in FEEDS:
        try:
            t = feed(fetch(url), now, pack, roots)
            good.append(t)
        except (ValueError, OSError) as error:
            if str(error) == 'network_policy_refusal': raise
    need(good, 'unavailable_or_invalid')
    identities = {}
    for t in good:
        e = t['envelope']
        need(e['seq'] not in identities or identities[e['seq']] == feed_identity(e), 'equivocation')
        identities[e['seq']] = feed_identity(e)
    return replay(max(good, key=lambda t: t['envelope']['seq']), list(records), now, pack, roots)


def stage(selected, parent, pack=PACK, target=None, fetch=get, roots=None):
    version(selected)
    if target is not None:
        target_check(target, selected, pack, roots)
    else:
        need(version(selected) >= version(V0), 'below_bootstrap_floor')
    total = 0
    def bounded(url):
        nonlocal total
        raw = fetch(url)
        total += len(raw)
        need(total <= MAX_TOTAL, 'aggregate_limit')
        return raw
    urls = lambda p: [m + selected + '/' + p for m in MIRRORS]
    iraw = retrieve(urls('install.json'), lambda x: install(x, selected, pack, roots), bounded)
    i = install(iraw, selected, pack, roots)
    if target is not None:
        need(canonical(i) == canonical(target['install']), 'target_changed')
    rraw = retrieve(urls('release.js'), lambda x: release(x, selected, pack, roots), bounded)
    files = {}
    for p, sha in i['manifest']['files'].items():
        files[p] = retrieve(urls('install/'+p), lambda x: hashcheck(x, sha), bounded)
    checked = package_check(iraw, rraw, selected, files, pack, roots)
    # Fresh private staging only. Every parent is created by this process.
    parent = Path(parent)
    need(parent.is_dir() and not parent.is_symlink() and parent.resolve() == parent.absolute(), 'unsafe_stage_parent')
    dest = Path(tempfile.mkdtemp(prefix='musterout-public-', dir=parent))
    os.chmod(dest, 0o700)
    rootfd = os.open(dest, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for p, raw in files.items():
            safe_path(p)
            directory = os.dup(rootfd)
            try:
                parts = p.split('/')
                for part in parts[:-1]:
                    try: os.mkdir(part, 0o700, dir_fd=directory)
                    except FileExistsError: pass
                    child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                    os.close(directory); directory = child
                fd = os.open(parts[-1], os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory)
                with os.fdopen(fd, 'w+b') as out:
                    out.write(raw); out.flush(); out.seek(0)
                    hashcheck(out.read(), i['manifest']['files'][p])
            finally: os.close(directory)
    finally: os.close(rootfd)
    return {'stage': str(dest), 'version': selected, 'install': checked['install'], 'release': {k: checked['release'][k] for k in ['envelope','signature']}, 'release_sha256': digest(rraw)}


def main():
    preflight()
    if len(sys.argv) == 2 and sys.argv[1] == 'preflight':
        print(canonical(preflight()))
        return
    need(len(sys.argv) >= 2, 'command_required')
    command = sys.argv[1]
    if command == 'stage-update':
        need(len(sys.argv) == 5, 'update_requires_target_current_private_parent')
        select_update(sys.argv[2], sys.argv[3])
        result = stage(sys.argv[2], sys.argv[4])
    elif command in ('stage','stage-resume'):
        need(len(sys.argv) == 4, 'stage_requires_version_and_private_parent')
        target = parse(sys.stdin.buffer.read(MAX_BYTES+1)) if command == 'stage-resume' else None
        if command == 'stage-resume':
            target_check(target, sys.argv[2])
        result = stage(sys.argv[2], sys.argv[3], target=target)
    else:
        value = parse(sys.stdin.buffer.read(MAX_BYTES+1))
        raw = b64(value['transport'], len(base64.b64decode(value['transport'], validate=True))) if 'transport' in value else None
        if command == 'release':
            result = release(raw, value['version'], value.get('pack',PACK))
        elif command == 'install':
            result = install(raw, value['version'], value.get('pack',PACK))
        elif command == 'feed':
            now = stamp(value['now'])
            result = replay(feed(raw, now, value.get('pack',PACK)), value.get('records', []), now, value.get('pack',PACK))
        elif command == 'feed-fetch':
            result = fetch_feed(stamp(value['now']), value.get('records', []), value.get('pack',PACK))
        elif command == 'target':
            result = target_check(value['target'], value['version'], value.get('pack',PACK))
        else:
            raise ValueError('unknown_command')
    print(canonical(result))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Never print raw input, server response, or arbitrary exception content.
        known = str(error)
        print(json.dumps({'error': known if re.fullmatch(r'[a-z_]{1,80}', known) else 'verification_failed'}), file=sys.stderr)
        sys.exit(1)
