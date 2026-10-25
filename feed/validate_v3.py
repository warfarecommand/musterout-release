"""Schema-3 board profile. Legacy v2 validation remains a separate contract."""
from copy import deepcopy
import hashlib
import json
import re
from urllib.parse import unquote, urlsplit

try:
    from .validate_v2 import validate_feed as validate_v2
    from .watch_contract import validate_feed as validate_collector
except ImportError:  # Direct release CLI execution.
    from validate_v2 import validate_feed as validate_v2
    from watch_contract import validate_feed as validate_collector

ACTIVE = ('MARADMIN', 'ALMAR', 'ALNAV', 'ORDER', 'ECFR', 'FEDERAL_REGISTER', 'VA_GOV')
LEGACY = ACTIVE[:4]
TOP = {'schema_version', 'seq', 'generated_at', 'expires_at', 'capture_replay',
       'sources', 'off_sources', 'legacy_seq', 'legacy_sha256'}


SOURCE_BLOCK_FIELDS_BY_VERSION = {3: frozenset({'source', 'coverage', 'status', 'reason', 'last_attempt', 'last_success', 'window', 'checked_count', 'unclassified_count', 'truncated', 'body_available', 'notices'})}
ORDER_BLOCK_FIELDS = frozenset({'unresolved_count', 'unresolved_items'})


def validate_source_block_fields(block, schema_version=3):
    required = SOURCE_BLOCK_FIELDS_BY_VERSION[schema_version]
    allowed = required | (ORDER_BLOCK_FIELDS if block.get('source') == 'ORDER' else frozenset())
    if not required <= block.keys() or not block.keys() <= allowed:
        raise ValueError('Invalid schema-3 source-block fields')
    return block




def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def bounded_json(value):
    nodes = 0
    def visit(item, depth=0):
        nonlocal nodes
        nodes += 1
        if nodes > 50_000 or depth > 32:
            raise ValueError('Feed traversal limit exceeded')
        if type(item) is str:
            try: item.encode('utf-8')
            except UnicodeEncodeError as error: raise ValueError('Invalid Unicode scalar') from error
            return
        if item is None or type(item) is bool:
            return
        if type(item) is int and abs(item) <= 9_007_199_254_740_991:
            return
        if type(item) is list and len(item) <= 50_000:
            for child in item: visit(child, depth + 1)
            return
        if type(item) is dict and len(item) <= 256:
            for key, child in item.items():
                if not isinstance(key, str) or not re.fullmatch(r'[\x20-\x7e]+', key):
                    raise ValueError('Invalid canonical object key')
                visit(key, depth + 1)
                visit(child, depth + 1)
            return
        raise ValueError('Invalid canonical feed value')
    visit(value)
    return value


def bounded(value, limit):
    return (isinstance(value, str) and bool(value.strip())
            and len(value.encode('utf-16-le')) // 2 <= limit
            and not re.search(r'[<>\x00-\x1f\x7f-\x9f]', value))


def strict_blocks(feed):
    for block in feed['sources']:
        if feed['schema_version'] == 3:
            validate_source_block_fields(block, 3)
        if not bounded(block['coverage'], 500):
            raise ValueError('Coverage exceeds the board contract')
        if block['status'] == 'failed' and not bounded(block['reason'], 500):
            raise ValueError('Failure reason exceeds the board contract')
        for notice in block['notices']:
            military = block['source'] in LEGACY
            if military and block['source'] != 'ORDER' and not re.fullmatch(r'[0-9]{1,3}/[0-9]{2}', notice['number']):
                raise ValueError('Non-ASCII military identity')
            if not bounded(notice['number'], 100 if military else 200):
                raise ValueError('Notice number exceeds the board contract')
            if not bounded(notice['id'], 120 if military else len(block['source']) + 201):
                raise ValueError('Notice identity exceeds the board contract')
    return feed


def validate_legacy(feed, now=None):
    validate_v2(feed, now)
    if feed.get('capture_replay') is not False or 'off_sources' in feed:
        raise ValueError('Legacy feed must explicitly be live without off metadata')
    if {block['source'] for block in feed['sources']} != set(LEGACY):
        raise ValueError('Legacy publication requires exactly four military sources')
    return strict_blocks(feed)


def validate_feed(feed, now=None):
    bounded_json(feed)
    if not isinstance(feed, dict) or not TOP <= feed.keys() or not feed.keys() <= TOP | {'classification_mode'}:
        raise ValueError('Invalid schema-3 fields')
    if type(feed['schema_version']) is not int or feed['schema_version'] != 3 or feed['capture_replay'] is not False:
        raise ValueError('Invalid schema-3 profile')
    if 'classification_mode' in feed and not bounded(feed['classification_mode'], 100):
        raise ValueError('Invalid classification mode')
    if (type(feed['legacy_seq']) is not int or feed['legacy_seq'] < 1
            or type(feed['seq']) is not int or feed['seq'] != feed['legacy_seq'] + 1
            or not isinstance(feed['legacy_sha256'], str)
            or not re.fullmatch(r'[a-f0-9]{64}', feed['legacy_sha256'])):
        raise ValueError('Invalid signed legacy binding')
    value = deepcopy(feed)
    value['schema_version'] = 2
    validate_collector(value, now)
    # The published profile uses the signer's UTC second/millisecond grammar.
    # This avoids differing fractional/timezone parsing across browser and Python.
    stamps = [feed['generated_at'], feed['expires_at']]
    for block in feed['sources']:
        stamps.append(block['last_attempt'])
        if block['last_success'] is not None: stamps.append(block['last_success'])
        if block['window']['to'] > feed['generated_at'][:10]:
            raise ValueError('Source window extends beyond generation day')
        for notice in block['notices']:
            if (not bounded(notice['url'], 500) or not notice['url'].startswith('https://')
                    or re.search(r'%(?![0-9A-Fa-f]{2})', notice['url'])):
                raise ValueError('Noncanonical source URL')
            try: unquote(notice['url'], errors='strict')
            except UnicodeDecodeError as error: raise ValueError('Invalid URL encoding') from error
            if block['source'] not in LEGACY:
                stamps.append(notice['change']['observed_at'])
                for identity in notice['identifiers']:
                    if any(isinstance(v, str) and not v.isascii() for k,v in identity.items() if k != 'url'):
                        raise ValueError('Non-ASCII native identity')
                    if 'url' in identity and (not bounded(identity['url'], 500) or not identity['url'].startswith('https://')):
                        raise ValueError('Noncanonical native URL')
                    if 'url' in identity:
                        path = urlsplit(identity['url']).path
                        if re.search(r'%(?![0-9A-Fa-f]{2})', path): raise ValueError('Invalid native URL encoding')
                        try: unquote(path, errors='strict')
                        except UnicodeDecodeError as error: raise ValueError('Invalid native URL encoding') from error
    if any(not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z', value) for value in stamps):
        raise ValueError('Noncanonical feed timestamp')
    if {block['source'] for block in feed['sources']} != set(ACTIVE) or len(feed['sources']) != len(ACTIVE):
        raise ValueError('Schema 3 requires exactly seven active sources')
    if feed['off_sources'] != [{'source': 'M21_1', 'reason': 'VA blocks automated reads'}]:
        raise ValueError('Schema 3 requires explicit M21-1 off coverage')
    return strict_blocks(feed)


def validate_pair(legacy, feed, now=None):
    validate_legacy(legacy, now)
    validate_feed(feed, now)
    if (feed['legacy_seq'] != legacy['seq']
            or feed['legacy_sha256'] != hashlib.sha256(canonical(legacy)).hexdigest()
            or any(feed[key] != legacy[key] for key in ('generated_at', 'expires_at', 'capture_replay'))
            or canonical([block for block in feed['sources'] if block['source'] in LEGACY]) != canonical(legacy['sources'])):
        raise ValueError('Schema-3 legacy projection binding mismatch')
    return feed


def strict_json_loads(raw):
    """Reject duplicate object keys at every nesting level, including escaped keys."""
    def pairs(items):
        value = {}
        for key, child in items:
            if key in value:
                raise ValueError('Duplicate projection key')
            value[key] = child
        return value
    value = json.loads(raw, object_pairs_hook=pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Invalid JSON constant')))
    return bounded_json(value)
