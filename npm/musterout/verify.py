#!/usr/bin/env python3
"""Muster Out protocol 1 verifier. Standard library only. Public bytes only.

This file runs only after an independently supplied SHA-256 pin is checked.
Never import downloaded product code. CLI input/output contains public data only.
"""
import base64
import zlib
import datetime as dt
import decimal
import hashlib
import http.client
import io
import socket
import ssl
import json
import os
from pathlib import Path
import re
import sys
import stat
import tempfile
import time
import threading
import urllib.error
import urllib.request
import urllib.parse

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
# Only release-gated package mirrors may provide schema 3.
FEEDS_V3 = ['https://cdn.jsdelivr.net/npm/musterout-feed@latest/v3/feed.js', 'https://raw.githubusercontent.com/warfarecommand/musterout-release/main/feed/v3/feed.js']
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
    need(type(v) is str and len(v) <= 128 and not re.search(r'[^0-9.]', v) and re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', v), 'invalid_version')
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


# WATCH_V3_BEGIN
"""Feed v2 data validation. Safe to copy into the release feed directory."""
from datetime import date as _wv3p_date, datetime as _wv3p_datetime, timedelta as _wv3p_timedelta, timezone as _wv3p_timezone
import re as _wv3p_re
from urllib.parse import urlsplit as _wv3p_urlsplit, unquote as _wv3p_unquote
_wv3p_LINES = {'separation', 'retirement', 'va', 'skillbridge', 'reserve', 'leave', 'family'}
_wv3p_PATHS = {'resign', 'retire', 'eas', 'all'}
_wv3p_VA_SOURCES = {'ECFR', 'FEDERAL_REGISTER', 'M21_1', 'VA_GOV'}
_wv3p_SOURCES = {'MARADMIN', 'ALMAR', 'ALNAV', 'ORDER'} | _wv3p_VA_SOURCES
_wv3p_OFF_SOURCE_REASONS = {'M21_1': 'VA blocks automated reads'}
_wv3p_VA_FALLBACK = 'The official source records a possible VA rule or program change. Read the official text before acting.'
_wv3p_APPLICABILITY = {'grades': {'o5', 'o14', 'cwo45', 'wo13', 'e89', 'e67', 'e15'}, 'service_types': {'officer', 'enlisted'}, 'reserve': {True, False}, 'skillbridge': {True, False}}
_wv3p_SOURCE_BLOCK_FIELDS_BY_VERSION = {3: frozenset({'source', 'coverage', 'status', 'reason', 'last_attempt', 'last_success', 'window', 'checked_count', 'unclassified_count', 'truncated', 'body_available', 'notices'})}
_wv3p_ORDER_BLOCK_FIELDS = frozenset({'unresolved_count', 'unresolved_items'})

def _wv3p_validate_source_block_fields(block, schema_version=3):
    if not isinstance(block, dict):
        raise ValueError('Invalid schema-3 source-block fields')
    required = _wv3p_SOURCE_BLOCK_FIELDS_BY_VERSION[schema_version]
    allowed = required | (_wv3p_ORDER_BLOCK_FIELDS if block.get('source') == 'ORDER' else frozenset())
    if not required <= block.keys() or not block.keys() <= allowed:
        raise ValueError('Invalid schema-3 source-block fields')
    return block

def _wv3p_failure_reason(value):
    """Bound public failure summaries to the installed board's 500 UTF-16 units."""
    value = _wv3p_re.sub('[<>\\x00-\\x1f\\x7f-\\x9f]', ' ', str(value)).strip()
    raw = value.encode('utf-16-le')
    if len(raw) > 1000:
        value = raw[:994].decode('utf-16-le', errors='ignore').rstrip() + '...'
    return value

def _wv3p_validate_applicability(notice):
    if 'applicability' not in notice:
        if any((k in notice for k in ('applicability_evidence', 'applicability_version'))):
            raise ValueError('Applicability metadata without dimensions')
        return
    value = notice['applicability']
    if not isinstance(value, dict) or not value.keys() <= _wv3p_APPLICABILITY.keys():
        raise ValueError('Invalid notice applicability')
    for key, values in value.items():
        kind = bool if key in {'reserve', 'skillbridge'} else str
        if not isinstance(values, list) or not values or any((type(v) is not kind or v not in _wv3p_APPLICABILITY[key] for v in values)) or (len(values) != len(set(values))):
            raise ValueError('Invalid applicability dimension')
    if 'applicability_version' in notice and (type(notice['applicability_version']) is not int or notice['applicability_version'] != 1):
        raise ValueError('Invalid applicability rule version')
    if 'applicability_evidence' in notice:
        evidence = notice['applicability_evidence']
        if not isinstance(evidence, dict) or evidence.keys() != value.keys():
            raise ValueError('Applicability evidence differs from dimensions')
        for phrases in evidence.values():
            if not isinstance(phrases, list) or not 1 <= len(phrases) <= 4:
                raise ValueError('Invalid applicability evidence list')
            for phrase in phrases:
                _wv3p_text(phrase, 500)
                if '@' in phrase or _wv3p_re.search('https?://|\\b\\d{3}[-. ]\\d{3}[-. ]\\d{4}\\b', phrase):
                    raise ValueError('Contact information in applicability evidence')

def _wv3p_clean(value):
    if isinstance(value, str) and _wv3p_re.search('[\\x00-\\x1f\\x7f-\\x9f]', value):
        raise ValueError('Control character in feed')
    if isinstance(value, dict):
        for key, item in value.items():
            _wv3p_clean(key)
            _wv3p_clean(item)
    elif isinstance(value, list):
        for item in value:
            _wv3p_clean(item)

def _wv3p_day(value):
    if not isinstance(value, str) or not _wv3p_re.fullmatch('\\d{4}-\\d{2}-\\d{2}', value):
        raise ValueError('Invalid ISO date')
    return _wv3p_date.fromisoformat(value)

def _wv3p_stamp(value):
    if not isinstance(value, str) or not _wv3p_re.fullmatch('\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?(?:Z|[+-]\\d{2}:\\d{2})', value):
        raise ValueError('Invalid timestamp')
    return _wv3p_datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(_wv3p_timezone.utc)

def _wv3p_official_url(source, value):
    if not isinstance(value, str) or len(value) > 500 or _wv3p_re.search('[\\s<>\\\\?#]', value):
        raise ValueError('Invalid source URL')
    u = _wv3p_urlsplit(value)
    if u.scheme != 'https' or u.username or u.password or u.port or u.query or u.fragment:
        raise ValueError('Invalid source URL authority')
    if _wv3p_re.search('%2f|%5c', u.path, _wv3p_re.I) or any((p in {'.', '..'} for p in _wv3p_unquote(u.path).split('/'))):
        raise ValueError('Invalid source URL path')
    if source in {'MARADMIN', 'ALMAR'}:
        valid = u.netloc == 'www.marines.mil' and _wv3p_re.fullmatch('/News/Messages/Messages-Display/Article/\\d+/[A-Za-z0-9-]+/', u.path)
    elif source == 'ALNAV':
        valid = u.netloc == 'www.mynavyhr.navy.mil' and (u.path.startswith('/References/Messages/') or u.path.startswith('/Portals/55/Messages/'))
    elif source == 'ORDER':
        valid = u.netloc == 'www.marines.mil' and (u.path.startswith('/News/Publications/MCPEL/') or u.path.startswith('/Portals/1/Publications/'))
    elif source == 'ECFR':
        valid = u.netloc == 'www.ecfr.gov' and _wv3p_re.fullmatch('/current/title-38/chapter-I/part-[34]/section-[34]\\.\\d+[a-z]?(?:-(?:[34]\\.)?\\d+[a-z]?)?', u.path)
    elif source == 'FEDERAL_REGISTER':
        valid = u.netloc == 'www.federalregister.gov' and _wv3p_re.fullmatch('/documents/\\d{4}/\\d{2}/\\d{2}/\\d{4}-\\d{4,6}/[A-Za-z0-9-]+/?', u.path)
    elif source == 'M21_1':
        valid = u.netloc == 'www.knowva.ebenefits.va.gov' and _wv3p_re.fullmatch('/system/templates/selfservice/va_ssnew/help/customer/locale/en-[Uu][Ss]/portal/\\d+/content/\\d+/[A-Za-z0-9-]+', u.path)
    elif source == 'VA_GOV':
        valid = u.netloc == 'www.va.gov' and u.path.startswith(('/resources/', '/disability/', '/health-care/')) or (u.netloc == 'news.va.gov' and _wv3p_re.fullmatch('/(?:press-room/[A-Za-z0-9-]+|\\d+/[A-Za-z0-9-]+)/', u.path))
    else:
        valid = False
    if not valid:
        raise ValueError('URL does not belong to source')
    return value

def _wv3p_text(value, limit):
    if not isinstance(value, str) or not value.strip() or len(value.encode('utf-16-le')) // 2 > limit or _wv3p_re.search('[<>]', value):
        raise ValueError('Invalid notice text')
_wv3p_VA_NOTICE_FIELDS = {'series', 'number', 'id', 'title', 'url', 'posted', 'relevant', 'lines', 'paths', 'action', 'summary', 'confidence', 'deadline', 'body_available', 'identifiers', 'change', 'source_evidence', 'rule_type', 'comments_close_on', 'cfr_parts', 'diagnostic_code_evidence', 'applicability', 'applicability_evidence', 'applicability_version'}

def _wv3p_va_summary(notice):
    """Canonical VA prose from validated structured facts, never source/model text."""
    source = notice['series']
    if source not in _wv3p_VA_SOURCES:
        raise ValueError('Invalid VA summary source')
    identifiers = notice['identifiers']
    for identity in identifiers:
        _wv3p_validate_native_id(identity)
    cfr = sorted({f"{i['title']} CFR {i['section']}" for i in identifiers if 'section' in i})
    codes = sorted({i['dc'] for i in identifiers if 'dc' in i})
    manuals = sorted({i['m21_1'] for i in identifiers if 'm21_1' in i})
    documents = sorted({i['document_number'] for i in identifiers if 'document_number' in i})

    def bounded(values):
        return ', '.join(values[:3]) + (f' and {len(values) - 3} more' if len(values) > 3 else '')

    def date_label(value):
        d = _wv3p_day(value)
        months = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')
        return f'{d.day:02} {months[d.month - 1]} {d.year:04}'
    change = notice['change']
    kind = change['kind']
    if kind not in {'published', 'amended', 'removed', 'added', 'updated', 'version_changed'}:
        raise ValueError('Invalid VA summary change')
    if source == 'FEDERAL_REGISTER':
        rule = {'final': 'final rule', 'proposed': 'proposed rule'}[notice['rule_type']]
        target = bounded(cfr) if cfr else 'Federal Register document ' + bounded(documents)
        result = f'VA published a {rule} about {target}'
    elif source == 'ECFR':
        action = {'amended': 'an amendment to', 'added': 'the addition of', 'removed': 'the removal of', 'published': 'a publication of', 'updated': 'an update to', 'version_changed': 'a version change to'}[kind]
        result = 'eCFR records ' + action + ' ' + bounded(cfr)
    elif source == 'M21_1':
        result = 'M21-1 records an update to ' + bounded(manuals)
    else:
        result = 'VA.gov records a benefit-page content update' if kind == 'updated' else 'VA.gov published a benefit or program update'
        if cfr:
            result += ' concerning ' + bounded(cfr)
    if codes:
        result += '; diagnostic codes ' + bounded(codes)
    if change.get('published_at'):
        result += ', published ' + date_label(change['published_at'])
    if change.get('effective_from'):
        result += ', effective ' + date_label(change['effective_from'])
    if notice.get('comments_close_on'):
        result += '; comments close ' + date_label(notice['comments_close_on'])
    return result + '. Read the official text.'

def _wv3p_validate_va_summary(summary, notice=None):
    if not isinstance(notice, dict) or summary != _wv3p_va_summary(notice):
        raise ValueError('VA summary differs from the structured template')
    _wv3p_text(summary, 1000)
    return summary

def _wv3p_refresh_va_notice(notice):
    """Discard legacy generated fields and reconstruct prose without reading it."""
    for key in list(notice):
        if key not in _wv3p_VA_NOTICE_FIELDS or key == 'summary':
            del notice[key]
    notice['summary'] = _wv3p_va_summary(notice)
    return notice

def _wv3p_validate_native_id(value):
    """Native official identity, never an inferred topic or a local rule key."""
    if not isinstance(value, dict):
        raise ValueError('Invalid native identifier')
    keys = set(value)
    if keys == {'title', 'part', 'section'}:
        if type(value['title']) is int and 1 <= value['title'] <= 50 and (type(value['part']) is int) and (value['part'] > 0) and isinstance(value['section'], str) and _wv3p_re.fullmatch(str(value['part']) + '\\.\\d+[a-z]?(?:-(?:' + str(value['part']) + '\\.)?\\d+[a-z]?)?', value['section']):
            return value
    elif keys == {'dc'}:
        if isinstance(value['dc'], str) and _wv3p_re.fullmatch('\\d{4}', value['dc']):
            return value
    elif keys == {'m21_1'}:
        if isinstance(value['m21_1'], str) and _wv3p_re.fullmatch('[IVX]+(?:\\.[A-Za-z0-9]+){1,7}', value['m21_1']):
            return value
    elif keys == {'document_number'}:
        if isinstance(value['document_number'], str) and _wv3p_re.fullmatch('\\d{4}-\\d{4,6}', value['document_number']):
            return value
    elif keys == {'form_number'}:
        if isinstance(value['form_number'], str) and _wv3p_re.fullmatch('(?:VA|DD|NAVMC) [A-Za-z0-9][A-Za-z0-9 ()-]{0,60}', value['form_number']):
            return value
    elif keys in ({'issuance', 'paragraph'}, {'issuance', 'paragraph', 'volume'}):
        if isinstance(value['issuance'], str) and _wv3p_re.fullmatch('(?:DoDI|DoDM|DoDD|MCO|SECNAVINST) \\d+[A-Za-z0-9. -]{0,40}', value['issuance']) and isinstance(value['paragraph'], str) and _wv3p_re.fullmatch('[A-Za-z0-9.()]{1,40}', value['paragraph']) and ('volume' not in value or (value['issuance'].startswith('DoDM ') and type(value['volume']) is int and (value['volume'] > 0))):
            return value
    elif keys == {'url'}:
        if not isinstance(value['url'], str) or len(value['url']) > 500 or _wv3p_re.search('[\\s<>\\\\]', value['url']):
            raise ValueError('Invalid native document URL')
        parsed = _wv3p_urlsplit(value['url'])
        _wv3p_official_url('VA_GOV', parsed._replace(query='', fragment='').geturl())
        return value
    raise ValueError('Invalid native identifier')

def _wv3p_validate_va_notice(notice):
    import json as _wv3p_json
    if not notice.keys() <= _wv3p_VA_NOTICE_FIELDS:
        raise ValueError('Unsupported VA notice fields')
    _wv3p_validate_va_summary(notice.get('summary'), notice)
    identifiers = notice.get('identifiers')
    if not isinstance(identifiers, list) or not 1 <= len(identifiers) <= 200:
        raise ValueError('Invalid native identifier list')
    seen = set()
    for value in identifiers:
        _wv3p_validate_native_id(value)
        key = _wv3p_json.dumps(value, sort_keys=True)
        if key in seen:
            raise ValueError('Duplicate native identifier')
        seen.add(key)
    source = notice['series']
    number = notice['number']
    if source == 'FEDERAL_REGISTER':
        if {'document_number': number} not in identifiers or '/' + number + '/' not in notice['url'] or notice.get('rule_type') not in {'final', 'proposed'}:
            raise ValueError('Federal Register native identity mismatch')
        if notice.get('comments_close_on') != notice.get('deadline'):
            raise ValueError('Federal Register comment deadline mismatch')
    elif source == 'ECFR':
        parts = number.split(':')
        if len(parts) != 5 or parts[0] != '38' or parts[1] not in {'3', '4'} or ({'title': 38, 'part': int(parts[1]), 'section': parts[2]} not in identifiers) or (not notice['url'].endswith('/section-' + parts[2])):
            raise ValueError('eCFR native identity mismatch')
    elif source == 'M21_1':
        if {'m21_1': number.split(':')[0]} not in identifiers:
            raise ValueError('M21-1 native identity mismatch')
    elif source == 'VA_GOV' and {'url': notice['url']} not in identifiers:
        raise ValueError('VA document native identity mismatch')
    change = notice.get('change')
    if not isinstance(change, dict) or change.get('kind') not in {'published', 'amended', 'removed', 'added', 'updated', 'version_changed'}:
        raise ValueError('Invalid VA change')
    for key in ('before_hash', 'after_hash'):
        value = change.get(key)
        if key == 'before_hash' and value is None:
            continue
        if not isinstance(value, str) or not _wv3p_re.fullmatch('[0-9a-f]{64}', value):
            raise ValueError('Invalid VA source hash')
    if change.get('scope') not in {'identified', 'section', 'document'}:
        raise ValueError('Invalid VA change scope')
    if type(change.get('effective_unknown')) is not bool or change['effective_unknown'] != (change.get('effective_from') is None):
        raise ValueError('Invalid VA effective-date certainty')
    for key in ('published_at', 'effective_from', 'effective_to'):
        if change.get(key) is not None:
            _wv3p_day(change[key])
    _wv3p_stamp(change.get('observed_at'))
    if change.get('effective_from') and change.get('effective_to') and (change['effective_to'] < change['effective_from']):
        raise ValueError('Invalid VA effective-date interval')
    evidence = notice.get('source_evidence')
    if not isinstance(evidence, dict) or evidence.get('basis') not in {'official_metadata', 'official_body', 'snapshot_diff'} or evidence.get('source_sha256') != change['after_hash']:
        raise ValueError('Invalid VA source evidence')
    _wv3p_text(evidence.get('quote'), 500)
    if '@' in evidence['quote'] or _wv3p_re.search('https?://|\\b\\d{3}[-. ]\\d{3}[-. ]\\d{4}\\b', evidence['quote']):
        raise ValueError('Contact details in VA evidence')
    if 'diagnostic_code_evidence' in notice:
        code_evidence = notice['diagnostic_code_evidence']
        if source != 'ECFR' or not isinstance(code_evidence, list):
            raise ValueError('Invalid diagnostic code evidence')
        expected_codes = {identity['dc'] for identity in identifiers if 'dc' in identity}
        if {row.get('dc') for row in code_evidence if isinstance(row, dict)} != expected_codes or len(code_evidence) != len(expected_codes):
            raise ValueError('Diagnostic code evidence differs from identifiers')
        for row in code_evidence:
            if row.get('snapshot') not in {'before', 'after'} or row.get('source_sha256') != change[row['snapshot'] + '_hash']:
                raise ValueError('Diagnostic code evidence snapshot mismatch')
            _wv3p_text(row.get('quote'), 500)
    if 'cfr_parts' in notice:
        if not isinstance(notice['cfr_parts'], list) or len(notice['cfr_parts']) > 100 or any((not isinstance(ref, dict) or set(ref) != {'title', 'part'} or type(ref['title']) is not int or (not 1 <= ref['title'] <= 50) or (type(ref['part']) is not int) or (ref['part'] < 1) for ref in notice['cfr_parts'])):
            raise ValueError('Invalid official CFR part references')
    if notice.get('applicability'):
        raise ValueError('VA applicability requires a supported evidence rule')

def _wv3p_validate_block(block, now=None):
    now = now or _wv3p_datetime.now(_wv3p_timezone.utc)
    _wv3p_clean(block)
    required = {'source', 'coverage', 'status', 'reason', 'last_attempt', 'last_success', 'window', 'checked_count', 'unclassified_count', 'truncated', 'body_available', 'notices'}
    if not isinstance(block, dict) or not required <= block.keys() or block['source'] not in _wv3p_SOURCES:
        raise ValueError('Invalid source block')
    source = block['source']
    _wv3p_text(block['coverage'], 2000)
    if block['status'] not in {'ok', 'failed', 'off'}:
        raise ValueError('Invalid source status')
    if block['status'] == 'off':
        if source not in _wv3p_OFF_SOURCE_REASONS or block['reason'] != _wv3p_OFF_SOURCE_REASONS[source] or block['last_success'] is not None or (block['notices'] != []) or (block['checked_count'] != 0) or (block['unclassified_count'] != 0) or (block['truncated'] is not False) or (block['body_available'] is not False):
            raise ValueError('Invalid off source')
    if block['status'] == 'ok' and block['reason'] is not None:
        raise ValueError('Successful source has a failure reason')
    if block['status'] == 'failed':
        _wv3p_text(block['reason'], 2000)
    attempt = _wv3p_stamp(block['last_attempt'])
    success = _wv3p_stamp(block['last_success']) if block['last_success'] is not None else None
    if attempt > now or (success and success > attempt) or (block['status'] == 'ok' and success is None):
        raise ValueError('Invalid source timestamps')
    window = block['window']
    if not isinstance(window, dict) or not {'from', 'to'} <= window.keys():
        raise ValueError('Invalid source window')
    start, end = (_wv3p_day(window['from']), _wv3p_day(window['to']))
    if end < start or end - start > _wv3p_timedelta(days=30) or end > now.date():
        raise ValueError('Invalid source window')
    notices = block['notices']
    if not isinstance(notices, list) or len(notices) > 500:
        raise ValueError('Invalid notice list')
    for key in ('checked_count', 'unclassified_count'):
        if type(block[key]) is not int or block[key] < 0:
            raise ValueError('Invalid source count')
    if block['checked_count'] < len(notices) or block['unclassified_count'] > block['checked_count']:
        raise ValueError('Inconsistent source counts')
    for key in ('truncated', 'body_available'):
        if type(block[key]) is not bool:
            raise ValueError('Invalid source flag')
    if success is None and (notices or block['checked_count']):
        raise ValueError('Results without a successful check')
    identities = set()
    for n in notices:
        if not isinstance(n, dict) or n.get('series') != source:
            raise ValueError('Invalid notice series')
        number = n.get('number')
        _wv3p_text(number, 200)
        if source in _wv3p_VA_SOURCES:
            if not _wv3p_re.fullmatch('[A-Za-z0-9.:-]{1,200}', number):
                raise ValueError('Invalid VA notice number')
            expected = source + '-' + number
            _wv3p_validate_va_notice(n)
            if _wv3p_stamp(n['change']['observed_at']) > attempt:
                raise ValueError('VA change observed after source attempt')
        elif source == 'ORDER':
            expected = 'ORDER-' + _wv3p_re.sub('[^A-Z0-9]+', '-', number.upper()).strip('-')
        else:
            if not _wv3p_re.fullmatch('\\d{1,3}/\\d{2}', number):
                raise ValueError('Invalid notice number')
            expected = source + '-' + number.replace('/', '-')
        if n.get('id') != expected or expected in identities:
            raise ValueError('Invalid or duplicate notice identity')
        identities.add(expected)
        _wv3p_text(n.get('title'), 300)
        if 'summary' in n:
            _wv3p_text(n['summary'], 1000)
        _wv3p_official_url(source, n.get('url'))
        if not start <= _wv3p_day(n.get('posted')) <= end:
            raise ValueError('Notice outside source window')
        if type(n.get('body_available')) is not bool or (block['body_available'] and (not n['body_available'])):
            raise ValueError('Invalid notice body flag')
        for key, allowed in (('lines', _wv3p_LINES), ('paths', _wv3p_PATHS)):
            values = n.get(key)
            if not isinstance(values, list) or not values or any((not isinstance(v, str) or v not in allowed for v in values)) or (len(values) != len(set(values))):
                raise ValueError('Invalid notice classification')
        if n.get('action', 'informational') not in {'required', 'informational'} or n.get('confidence', 'low') not in {'high', 'medium', 'low'}:
            raise ValueError('Invalid notice action or confidence')
        if n.get('deadline') is not None:
            _wv3p_day(n['deadline'])
        _wv3p_validate_applicability(n)
    return block

def _wv3p_validate_feed(feed, now=None):
    now = now or _wv3p_datetime.now(_wv3p_timezone.utc)
    _wv3p_clean(feed)
    if not isinstance(feed, dict) or type(feed.get('schema_version')) is not int or feed['schema_version'] != 2:
        raise ValueError('Invalid feed schema')
    if type(feed.get('seq')) is not int or not 1 <= feed['seq'] <= 9007199254740991:
        raise ValueError('Invalid feed sequence')
    generated, expires = (_wv3p_stamp(feed.get('generated_at')), _wv3p_stamp(feed.get('expires_at')))
    if generated > now or expires != generated + _wv3p_timedelta(days=8) or now >= expires:
        raise ValueError('Future or expired feed')
    if type(feed.get('capture_replay', False)) is not bool:
        raise ValueError('Invalid capture flag')
    blocks = feed.get('sources')
    if not isinstance(blocks, list) or not blocks or len(blocks) > len(_wv3p_SOURCES):
        raise ValueError('Invalid sources')
    labels = set()
    for block in blocks:
        _wv3p_validate_block(block, now)
        if block['status'] == 'off':
            raise ValueError('Off sources belong in off_sources, not checked sources')
        if block['source'] in labels or _wv3p_stamp(block['last_attempt']) > generated:
            raise ValueError('Duplicate source or attempt after generation')
        labels.add(block['source'])
    off_sources = feed.get('off_sources', [])
    if not isinstance(off_sources, list) or len(off_sources) > len(_wv3p_OFF_SOURCE_REASONS):
        raise ValueError('Invalid off_sources')
    for off in off_sources:
        if not isinstance(off, dict) or set(off) != {'source', 'reason'} or off.get('source') not in _wv3p_OFF_SOURCE_REASONS or (off['source'] in labels) or (off.get('reason') != _wv3p_OFF_SOURCE_REASONS[off['source']]):
            raise ValueError('Invalid or duplicate off source')
        labels.add(off['source'])
    return feed

"""Schema-3 board profile. Legacy v2 validation remains a separate contract."""
from copy import deepcopy as _wv3r_deepcopy
import hashlib as _wv3r_hashlib
import json as _wv3r_json
import re as _wv3r_re
from urllib.parse import unquote as _wv3r_unquote, urlsplit as _wv3r_urlsplit
_wv3r_ACTIVE = ('MARADMIN', 'ALMAR', 'ALNAV', 'ORDER', 'ECFR', 'FEDERAL_REGISTER', 'VA_GOV')
_wv3r_LEGACY = _wv3r_ACTIVE[:4]
_wv3r_TOP = {'schema_version', 'seq', 'generated_at', 'expires_at', 'capture_replay', 'sources', 'off_sources', 'legacy_seq', 'legacy_sha256'}
_wv3r_SOURCE_BLOCK_FIELDS_BY_VERSION = {3: frozenset({'source', 'coverage', 'status', 'reason', 'last_attempt', 'last_success', 'window', 'checked_count', 'unclassified_count', 'truncated', 'body_available', 'notices'})}
_wv3r_ORDER_BLOCK_FIELDS = frozenset({'unresolved_count', 'unresolved_items'})

def _wv3r_validate_source_block_fields(block, schema_version=3):
    if not isinstance(block, dict):
        raise ValueError('Invalid schema-3 source-block fields')
    required = _wv3r_SOURCE_BLOCK_FIELDS_BY_VERSION[schema_version]
    allowed = required | (_wv3r_ORDER_BLOCK_FIELDS if block.get('source') == 'ORDER' else frozenset())
    if not required <= block.keys() or not block.keys() <= allowed:
        raise ValueError('Invalid schema-3 source-block fields')
    return block

def _wv3r_bounded_json(value):
    nodes = 0

    def visit(item, depth=0):
        nonlocal nodes
        nodes += 1
        if nodes > 50000 or depth > 32:
            raise ValueError('Feed traversal limit exceeded')
        if type(item) is str:
            try:
                item.encode('utf-8')
            except UnicodeEncodeError as error:
                raise ValueError('Invalid Unicode scalar') from error
            return
        if item is None or type(item) is bool:
            return
        if type(item) is int and abs(item) <= 9007199254740991:
            return
        if type(item) is list and len(item) <= 50000:
            for child in item:
                visit(child, depth + 1)
            return
        if type(item) is dict and len(item) <= 256:
            for key, child in item.items():
                if not isinstance(key, str) or not _wv3r_re.fullmatch('[\\x20-\\x7e]+', key):
                    raise ValueError('Invalid canonical object key')
                visit(key, depth + 1)
                visit(child, depth + 1)
            return
        raise ValueError('Invalid canonical feed value')
    visit(value)
    return value

def _wv3r_bounded(value, limit):
    return isinstance(value, str) and bool(value.strip()) and (len(value.encode('utf-16-le')) // 2 <= limit) and (not _wv3r_re.search('[<>\\x00-\\x1f\\x7f-\\x9f]', value))

def _wv3r_strict_blocks(feed):
    for block in feed['sources']:
        if feed['schema_version'] == 3:
            _wv3r_validate_source_block_fields(block, 3)
        if not _wv3r_bounded(block['coverage'], 500):
            raise ValueError('Coverage exceeds the board contract')
        if block['status'] == 'failed' and (not _wv3r_bounded(block['reason'], 500)):
            raise ValueError('Failure reason exceeds the board contract')
        for notice in block['notices']:
            military = block['source'] in _wv3r_LEGACY
            if military and block['source'] != 'ORDER' and (not _wv3r_re.fullmatch('[0-9]{1,3}/[0-9]{2}', notice['number'])):
                raise ValueError('Non-ASCII military identity')
            if not _wv3r_bounded(notice['number'], 100 if military else 200):
                raise ValueError('Notice number exceeds the board contract')
            if not _wv3r_bounded(notice['id'], 120 if military else len(block['source']) + 201):
                raise ValueError('Notice identity exceeds the board contract')
    return feed

def _wv3r_validate_feed(feed, now=None):
    _wv3r_bounded_json(feed)
    if not isinstance(feed, dict) or not _wv3r_TOP <= feed.keys() or (not feed.keys() <= _wv3r_TOP | {'classification_mode'}):
        raise ValueError('Invalid schema-3 fields')
    if type(feed['schema_version']) is not int or feed['schema_version'] != 3 or feed['capture_replay'] is not False:
        raise ValueError('Invalid schema-3 profile')
    if 'classification_mode' in feed and (not _wv3r_bounded(feed['classification_mode'], 100)):
        raise ValueError('Invalid classification mode')
    if type(feed['legacy_seq']) is not int or feed['legacy_seq'] < 1 or type(feed['seq']) is not int or (feed['seq'] != feed['legacy_seq'] + 1) or (not isinstance(feed['legacy_sha256'], str)) or (not _wv3r_re.fullmatch('[a-f0-9]{64}', feed['legacy_sha256'])):
        raise ValueError('Invalid signed legacy binding')
    value = _wv3r_deepcopy(feed)
    value['schema_version'] = 2
    _wv3p_validate_feed(value, now)
    stamps = [feed['generated_at'], feed['expires_at']]
    for block in feed['sources']:
        stamps.append(block['last_attempt'])
        if block['last_success'] is not None:
            stamps.append(block['last_success'])
        if block['window']['to'] > feed['generated_at'][:10]:
            raise ValueError('Source window extends beyond generation day')
        for notice in block['notices']:
            if not _wv3r_bounded(notice['url'], 500) or not notice['url'].startswith('https://') or _wv3r_re.search('%(?![0-9A-Fa-f]{2})', notice['url']):
                raise ValueError('Noncanonical source URL')
            try:
                _wv3r_unquote(notice['url'], errors='strict')
            except UnicodeDecodeError as error:
                raise ValueError('Invalid URL encoding') from error
            if block['source'] not in _wv3r_LEGACY:
                stamps.append(notice['change']['observed_at'])
                for identity in notice['identifiers']:
                    if any((isinstance(v, str) and (not v.isascii()) for k, v in identity.items() if k != 'url')):
                        raise ValueError('Non-ASCII native identity')
                    if 'url' in identity and (not _wv3r_bounded(identity['url'], 500) or not identity['url'].startswith('https://')):
                        raise ValueError('Noncanonical native URL')
                    if 'url' in identity:
                        path = _wv3r_urlsplit(identity['url']).path
                        if _wv3r_re.search('%(?![0-9A-Fa-f]{2})', path):
                            raise ValueError('Invalid native URL encoding')
                        try:
                            _wv3r_unquote(path, errors='strict')
                        except UnicodeDecodeError as error:
                            raise ValueError('Invalid native URL encoding') from error
    if any((not isinstance(value, str) or not _wv3r_re.fullmatch('\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{3})?Z', value) for value in stamps)):
        raise ValueError('Noncanonical feed timestamp')
    if {block['source'] for block in feed['sources']} != set(_wv3r_ACTIVE) or len(feed['sources']) != len(_wv3r_ACTIVE):
        raise ValueError('Schema 3 requires exactly seven active sources')
    if feed['off_sources'] != [{'source': 'M21_1', 'reason': 'VA blocks automated reads'}]:
        raise ValueError('Schema 3 requires explicit M21-1 off coverage')
    return _wv3r_strict_blocks(feed)
# WATCH_V3_END

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
    return b'self.postMessage(' + canonical({k: raw[k] for k in ['envelope','signature','data']}).replace('\u2028', '\\u2028').replace('\u2029', '\\u2029').encode() + b');\n'


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


def feed_v3(raw, now, pack=PACK, roots=None, historical=False):
    t = wrapper(raw, 'feed')
    expected = ('self.postMessage(' + canonical(t).replace('\u2028', '\\u2028').replace('\u2029', '\\u2029') + ');\n').encode('utf-8')
    need(raw == expected, 'noncanonical_transport')
    data = t['data']
    e = envelope(t['envelope'], t['signature'], canonical(data).encode(), 'feed', pack, roots)
    need(type(now) in (int, float) and 0 < now < 253402300800, 'clock_unavailable')
    need(data.get('seq') == e['seq'] and type(data.get('seq')) is int and ('pack' not in data or data['pack'] == pack) and data.get('generated_at') == e['created'] and data.get('expires_at') == e['expires'], 'feed_binding')
    start, end = stamp(e['created']), stamp(e['expires'])
    need(end-start == 8*86400 and start <= now < end, 'expired_or_future')
    _wv3r_validate_feed(data, _wv3p_datetime.fromtimestamp(now, _wv3p_timezone.utc))
    return t


def highwater_v3(records, legacy_records, now, pack=PACK, roots=None):
    need(type(records) is list and type(legacy_records) is list, 'invalid_records')
    best, identities = None, {}
    for rows, validate in [(legacy_records, feed), (records, feed_v3)]:
        for r in rows:
            try:
                at = stamp(r['accepted_at'])
                need(at <= now and type(r['highest_seq']) is int and r['highest_seq'] == r['envelope']['seq'], 'invalid_record')
                t = validate(record(r), at, pack, roots)
                seq, identity = t['envelope']['seq'], feed_identity(t['envelope'])
                need(seq not in identities or identities[seq] == identity, 'equivocation')
                identities[seq] = identity
                if best is None or seq > best['envelope']['seq']: best = t
            except (KeyError, TypeError, ValueError) as error:
                if str(error) == 'equivocation': raise
    return best


def replay_v3(t, records, legacy_records, now, pack=PACK, roots=None):
    best = highwater_v3(records, legacy_records, now, pack, roots)
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


# Registry integrity detects transport corruption only. Publisher signatures remain authority.
REGISTRY = 'https://registry.npmjs.org/musterout/'
MAX_ENTRIES = MAX_FILES + 8
MAX_TAR = MAX_TOTAL + MAX_ENTRIES*1024 + 1024


def registry_urls(selected):
    version(selected)
    return {'metadata': REGISTRY+selected, 'tarball': REGISTRY+'-/musterout-'+selected+'.tgz'}


def url_limit(url):
    need(type(url) is str and re.fullmatch(r'[\x21-\x7e]+', url), 'unsafe_url')
    if url in FEEDS or url in FEEDS_V3:
        return MAX_BYTES
    v = r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
    if re.fullmatch(r'https://registry\.npmjs\.org/musterout/'+v, url):
        return MAX_BYTES
    if re.fullmatch(r'https://registry\.npmjs\.org/musterout/-/musterout-'+v+r'\.tgz', url):
        return MAX_TOTAL
    for m in MIRRORS:
        if not url.startswith(m): continue
        try:
            selected, p = url[len(m):].split('/', 1)
            version(selected)
            if p not in ('install.json', 'release.js'):
                need(p.startswith('install/'), 'unsafe_url')
                safe_path(p[8:])
            return MAX_BYTES
        except ValueError:
            pass
    raise ValueError('unsafe_url')


def tar_read(raw):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_TOTAL, 'transport_size')
    # Bounded decompression also validates the gzip CRC and complete stream.
    # Exactly one gzip member: concatenation cannot multiply decoder work.
    try:
        decoder = zlib.decompressobj(31)
        tar = decoder.decompress(raw, MAX_TAR+1)
        need(len(tar) <= MAX_TAR and decoder.eof and not decoder.unused_data, 'invalid_gzip')
    except zlib.error:
        raise ValueError('invalid_gzip') from None
    need(len(tar) % 512 == 0, 'invalid_tar')
    files, seen, at, total, ended = {}, set(), 0, 0, False
    def text(b):
        end = b.find(b'\0')
        if end < 0: end = len(b)
        need(not any(b[end:]) and all(32 <= x <= 126 for x in b[:end]), 'invalid_tar')
        return b[:end].decode('ascii')
    def octal(b):
        need(all(x in (0, 32) or 48 <= x <= 55 for x in b), 'invalid_tar')
        n = b.strip(b'\0 ')
        need(re.fullmatch(b'[0-7]+', n), 'invalid_tar')
        return int(n, 8)
    while at+512 <= len(tar):
        h = tar[at:at+512]
        if not any(h):
            need(at+1024 <= len(tar) and not any(tar[at:]), 'invalid_tar')
            ended = True
            break
        checksum = octal(h[148:156])
        need(sum(h[:148])+8*32+sum(h[156:]) == checksum, 'invalid_tar')
        need(h[156] in (0, 48) and not any(h[157:257]), 'tar_type')
        prefix = text(h[345:500])
        name = (prefix+'/' if prefix else '')+text(h[:100])
        need(name.startswith('package/') and len(name) <= 300 and re.fullmatch(r'[A-Za-z0-9_./-]+', name) and all(x not in ('', '.', '..') for x in name.split('/')), 'unsafe_tar_path')
        need(name.lower() not in seen, 'duplicate_entry')
        seen.add(name.lower())
        need(len(seen) <= MAX_ENTRIES, 'file_count')
        size = octal(h[124:136])
        need(size <= MAX_BYTES, 'transport_size')
        total += size
        need(total <= MAX_TOTAL, 'aggregate_limit')
        end, next_at = at+512+size, at+512+((size+511)//512)*512
        need(next_at <= len(tar) and not any(tar[end:next_at]), 'invalid_tar')
        files[name[8:]] = tar[at+512:end]
        at = next_at
    need(ended and seen, 'invalid_tar')
    return files


def registry_package(selected, fetch=None):
    fetch = fetch or get
    u = registry_urls(selected)
    m = parse(fetch(u['metadata']))
    need(type(m) is dict, 'registry_identity')
    need(m.get('name') == 'musterout' and m.get('version') == selected and type(m.get('dist')) is dict and m['dist'].get('tarball') == u['tarball'], 'registry_identity')
    integrity = m['dist'].get('integrity')
    need(type(integrity) is str and integrity.startswith('sha512-'), 'registry_integrity')
    expected = b64(integrity[7:], 64)
    raw = fetch(u['tarball'])
    need(type(raw) is bytes and 0 < len(raw) <= MAX_TOTAL, 'transport_size')
    need(hashlib.sha512(raw).digest() == expected, 'registry_integrity')
    return tar_read(raw)


def proxy_config():
    raw = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    if not raw: return None
    try:
        p = urllib.parse.urlsplit(raw)
        need(p.scheme in ('http', 'https') and p.hostname and p.path in ('', '/') and not p.query and not p.fragment, 'unsafe_proxy')
        port = p.port or (443 if p.scheme == 'https' else 80)
        auth = None
        if p.username is not None or p.password is not None:
            auth = 'Basic '+base64.b64encode((urllib.parse.unquote(p.username or '')+':'+urllib.parse.unquote(p.password or '')).encode()).decode()
        return p.scheme, p.hostname, port, auth
    except ValueError:
        raise ValueError('unsafe_proxy') from None


class TLSReader(io.RawIOBase):
    def __init__(self, stream):
        self._sock = stream
        stream.readers += 1
    def close(self):
        if not self.closed:
            self._sock.readers -= 1
            if self._sock.closed and not self._sock.readers: self._sock.transport.close()
        super().close()
    def readable(self): return True
    def readinto(self, buffer):
        raw = self._sock.recv(len(buffer))
        buffer[:len(raw)] = raw
        return len(raw)


class TLSStream:
    """Verified origin TLS inside a verified TLS connection to an HTTPS proxy."""
    def __init__(self, transport, context, hostname):
        self.transport = transport
        self.readers, self.closed = 0, False
        self.incoming, self.outgoing = ssl.MemoryBIO(), ssl.MemoryBIO()
        self.tls = context.wrap_bio(self.incoming, self.outgoing, server_hostname=hostname)
        self.call(self.tls.do_handshake)
    def flush(self):
        while self.outgoing.pending:
            self.transport.sendall(self.outgoing.read())
    def call(self, function, *args):
        while True:
            try:
                result = function(*args)
                self.flush()
                return result
            except ssl.SSLWantWriteError:
                self.flush()
            except ssl.SSLWantReadError:
                self.flush()
                raw = self.transport.recv(65536)
                if raw: self.incoming.write(raw)
                else: self.incoming.write_eof()
    def sendall(self, raw):
        at = 0
        while at < len(raw): at += self.call(self.tls.write, raw[at:])
    def recv(self, size):
        try: return self.call(self.tls.read, size)
        except (ssl.SSLZeroReturnError, ssl.SSLEOFError): return b''
    def makefile(self, mode):
        need(mode == 'rb', 'http_refused')
        return io.BufferedReader(TLSReader(self))
    def settimeout(self, value): self.transport.settimeout(value)
    def close(self):
        self.closed = True
        if not self.readers: self.transport.close()


class EnvironmentProxy(urllib.request.ProxyHandler):
    def __init__(self, proxy):
        super().__init__({'https': 'http://proxy.invalid'})
        self.proxy = proxy
    def proxy_open(self, req, proxy, type):
        scheme, host, port, auth = self.proxy
        if auth: req.add_header('Proxy-authorization', auth)
        req.set_proxy(('['+host+']' if ':' in host else host)+':'+str(port), 'http')
        return None


class RequestDeadline:
    """One monotonic deadline, including DNS and trickled headers; no late I/O."""
    def __init__(self):
        self.expires = time.monotonic() + 20
        self.sockets, self.closed, self.lock = [], False, threading.Lock()
    def remaining(self):
        remaining = self.expires - time.monotonic()
        need(not self.closed and remaining > 0, 'http_timeout')
        return remaining
    def register(self, sock):
        with self.lock:
            if self.closed or time.monotonic() >= self.expires:
                sock.close()
                raise ValueError('http_timeout')
            self.sockets.append(sock)
        return sock
    def close(self):
        with self.lock:
            self.closed = True
            sockets, self.sockets = self.sockets, []
        for sock in sockets:
            try: sock.shutdown(socket.SHUT_RDWR)
            except OSError: pass
            try: sock.close()
            except OSError: pass
    def connect(self, address, timeout=None, source_address=None):
        self.remaining()
        addresses = socket.getaddrinfo(*address, type=socket.SOCK_STREAM)
        self.remaining()  # A delayed resolver cannot start a connection after expiry.
        last = OSError('http_unavailable')
        for family, kind, protocol, _, endpoint in addresses:
            raw = self.register(socket.socket(family, kind, protocol))
            try:
                raw.settimeout(self.remaining())
                if source_address: raw.bind(source_address)
                raw.connect(endpoint)
                return raw
            except OSError as error:
                raw.close()
                last = error
        raise last
    def tls(self, raw, context, hostname):
        self.remaining()
        secure = self.register(context.wrap_socket(raw, server_hostname=hostname, do_handshake_on_connect=False))
        secure.settimeout(self.remaining())
        secure.do_handshake()
        return secure


class TunnelHTTPSHandler(urllib.request.HTTPSHandler):
    def __init__(self, proxy, deadline):
        super().__init__(context=ssl.create_default_context())
        self.proxy, self.deadline = proxy, deadline
    def https_open(self, req):
        proxy, deadline = self.proxy, self.deadline
        class Connection(http.client.HTTPSConnection):
            def connect(self):
                origin = self._tunnel_host if proxy else self.host
                self.sock = deadline.connect((proxy[1], proxy[2]) if proxy else (self.host, self.port), source_address=self.source_address)
                try:
                    if proxy:
                        if proxy[0] == 'https': self.sock = deadline.tls(self.sock, ssl.create_default_context(), proxy[1])
                        try: self._tunnel()
                        except OSError as error:
                            status = re.search(r'Tunnel connection failed: ([0-9]{3})', str(error))
                            if status: raise ValueError('network_policy_refusal' if int(status[1]) in (401, 403, 407, 451) else 'http_refused') from None
                            raise
                    self.sock = TLSStream(self.sock, self._context, origin) if proxy and proxy[0] == 'https' else deadline.tls(self.sock, self._context, origin)
                except Exception:
                    # _tunnel() may already have closed and cleared self.sock.
                    if self.sock is not None:
                        try: self.sock.close()
                        except OSError: pass
                    raise
        return self.do_open(Connection, req, context=self._context)


def get(url):
    limit, proxy = url_limit(url), proxy_config()
    deadline, complete, result = RequestDeadline(), threading.Event(), {}
    def worker():
        try: result['raw'] = get_response(url, limit, proxy, deadline)
        except Exception as error: result['error'] = error
        finally: complete.set()
    # A stalled resolver cannot hold the caller past its deadline. All registered
    # sockets are shut down at expiry, and delayed DNS cannot initiate later I/O.
    threading.Thread(target=worker, daemon=True).start()
    try:
        need(complete.wait(deadline.remaining()), 'http_timeout')
        deadline.remaining()
        if 'error' in result: raise result['error']
        return result['raw']
    finally: deadline.close()


def get_response(url, limit, proxy, deadline):
    req = urllib.request.Request(url, headers={'Accept-Encoding': 'identity'})
    handlers = [EnvironmentProxy(proxy) if proxy else urllib.request.ProxyHandler({}), TunnelHTTPSHandler(proxy, deadline)]
    opener = urllib.request.build_opener(*handlers, NoRedirect())
    try:
        with opener.open(req, timeout=deadline.remaining()) as response:
            need(response.status == 200 and response.url == url and response.headers.get('Content-Encoding', 'identity') == 'identity', 'http_refused')
            parts, size = [], 0
            while True:
                remaining = deadline.remaining()
                if response.fp is not None:
                    response.fp.raw._sock.settimeout(remaining)
                chunk = response.read1(min(65536, limit+1-size))
                if not chunk: break
                parts.append(chunk); size += len(chunk)
                need(size <= limit, 'transport_size')
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
        except (ValueError, OSError):
            pass
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
        except (ValueError, OSError):
            pass
    need(good, 'unavailable_or_invalid')
    identities = {}
    for t in good:
        e = t['envelope']
        need(e['seq'] not in identities or identities[e['seq']] == feed_identity(e), 'equivocation')
        identities[e['seq']] = feed_identity(e)
    return replay(max(good, key=lambda t: t['envelope']['seq']), list(records), now, pack, roots)


def stage(selected, parent, pack=PACK, target=None, fetch=get, roots=None, local=None):
    version(selected)
    if target is not None:
        target_check(target, selected, pack, roots)
    else:
        need(version(selected) >= version(V0), 'below_bootstrap_floor')
    archive, registry_tried = None, False
    totals = {}
    def bounded(url):
        key = REGISTRY if url.startswith(REGISTRY) else next((m for m in MIRRORS if url.startswith(m)), None)
        need(key and totals.get(key, 0) <= MAX_TOTAL, 'aggregate_limit')
        raw = fetch(url)
        need(type(raw) is bytes and 0 < len(raw) <= url_limit(url), 'transport_size')
        totals[key] = totals.get(key, 0)+len(raw)
        need(totals[key] <= MAX_TOTAL, 'aggregate_limit')
        return raw
    registry = registry_urls(selected)['tarball']
    def retrieve_path(p, validate):
        if local is not None:
            need(p in local, 'unavailable_or_invalid')
            validate(local[p])
            return local[p]
        def source(url):
            nonlocal archive, registry_tried
            if url != registry:
                return bounded(url)
            if not registry_tried:
                registry_tried = True
                try: archive = registry_package(selected, bounded)
                except (ValueError, OSError): archive = None
            need(archive is not None and p in archive, 'unavailable_or_invalid')
            return archive[p]
        return retrieve([registry]+[m+selected+'/'+p for m in MIRRORS], validate, source)
    iraw = retrieve_path('install.json', lambda x: install(x, selected, pack, roots))
    i = install(iraw, selected, pack, roots)
    if target is not None:
        need(canonical(i) == canonical(target['install']), 'target_changed')
    rraw = retrieve_path('release.js', lambda x: release(x, selected, pack, roots))
    files = {}
    for p, sha in i['manifest']['files'].items():
        files[p] = retrieve_path('install/'+p, lambda x: hashcheck(x, sha))
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


def read_local(file, limit):
    fd = os.open(file, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as source:
        info = os.fstat(source.fileno())
        need(stat.S_ISREG(info.st_mode) and 0 < info.st_size <= limit, 'transport_size')
        raw = source.read(limit+1)
    need(0 < len(raw) <= limit, 'transport_size')
    return raw


def transport_integrity(raw, integrity):
    if integrity is not None:
        need(type(integrity) is str and integrity.startswith('sha512-'), 'registry_integrity')
        need(hashlib.sha512(raw).digest() == b64(integrity[7:], 64), 'registry_integrity')


def stage_tarball(selected, file, parent, pack=PACK, target=None, roots=None, integrity=None):
    raw = read_local(file, MAX_TOTAL)
    transport_integrity(raw, integrity)
    return stage(selected, parent, pack, target, roots=roots, local=tar_read(raw))


def feed_file(file, now, records=(), pack=PACK, roots=None):
    return replay(feed(read_local(file, MAX_BYTES), now, pack, roots), list(records), now, pack, roots)


def feed_file_v3(file, now, records=(), legacy_records=(), pack=PACK, roots=None):
    return replay_v3(feed_v3(read_local(file, MAX_BYTES), now, pack, roots), list(records), list(legacy_records), now, pack, roots)


def fetch_feed_v3(now, records=(), legacy_records=(), pack=PACK, fetch=get, roots=None):
    good = []
    for url in FEEDS_V3:
        try: good.append(feed_v3(fetch(url), now, pack, roots))
        except (ValueError, OSError): pass
    need(good, 'unavailable_or_invalid')
    identities = {}
    for t in good:
        e = t['envelope']
        need(e['seq'] not in identities or identities[e['seq']] == feed_identity(e), 'equivocation')
        identities[e['seq']] = feed_identity(e)
    return replay_v3(max(good, key=lambda t:t['envelope']['seq']), list(records), list(legacy_records), now, pack, roots)


def main():
    preflight()
    if len(sys.argv) == 2 and sys.argv[1] == 'preflight':
        print(canonical(preflight()))
        return
    need(len(sys.argv) >= 2, 'command_required')
    command = sys.argv[1]
    if command in ('stage-tarball', 'stage-resume-tarball', 'stage-update-tarball'):
        update, resume = command == 'stage-update-tarball', command == 'stage-resume-tarball'
        n = 6 if update else 5
        need(len(sys.argv) in (n, n+1), 'tarball_arguments')
        selected = sys.argv[2]
        if update: select_update(selected, sys.argv[3])
        target = parse(sys.stdin.buffer.read(MAX_BYTES+1)) if resume else None
        if resume: target_check(target, selected)
        offset = 4 if update else 3
        result = stage_tarball(selected, sys.argv[offset], sys.argv[offset+1], target=target, integrity=sys.argv[offset+2] if len(sys.argv) > offset+2 else None)
    elif command == 'feed-file-v3':
        need(len(sys.argv) == 3, 'feed_file_arguments')
        value = parse(sys.stdin.buffer.read(MAX_BYTES+1))
        result = feed_file_v3(sys.argv[2], stamp(value['now']), value.get('records', []), value.get('legacy_records', []), value.get('pack', PACK))
    elif command == 'feed-file':
        need(len(sys.argv) == 3, 'feed_file_arguments')
        value = parse(sys.stdin.buffer.read(MAX_BYTES+1))
        result = feed_file(sys.argv[2], stamp(value['now']), value.get('records', []), value.get('pack', PACK))
    elif command == 'stage-update':
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
        elif command == 'feed-v3':
            now = stamp(value['now'])
            result = replay_v3(feed_v3(raw, now, value.get('pack',PACK)), value.get('records', []), value.get('legacy_records', []), now, value.get('pack',PACK))
        elif command == 'feed-fetch-v3':
            result = fetch_feed_v3(stamp(value['now']), value.get('records', []), value.get('legacy_records', []), value.get('pack',PACK))
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
        print(canonical({'error': known if re.fullmatch(r'[a-z_]{1,80}', known) else 'verification_failed'}), file=sys.stderr)
        sys.exit(1)
