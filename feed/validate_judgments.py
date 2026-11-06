"""Judgment revision 2 consumer contract, vendored from watch c0097d6.

Only the timestamp import differs from judgment_contract.py.
"""
from datetime import date, datetime, timedelta, timezone
import re
import hashlib
import json
import unicodedata

KEYS = {'v', 'kind', 'summary', 'audience', 'fit', 'depends_on', 'action', 'evidence', 'judged'}
PATHS = {'eas', 'resign', 'retire', 'deciding'}


JUDGMENT_SCHEMA = {'anyOf': [
    {'type': 'object', 'additionalProperties': False, 'required': sorted(KEYS), 'properties': {
        'v': {'type': 'integer', 'enum': [1]},
        'kind': {'type': 'string', 'enum': ['action', 'policy', 'news']},
        'summary': {'type': 'string', 'description': 'One sentence, at most 200 characters. No dashes.'},
        'audience': {'type': 'string', 'description': 'A short source audience phrase, preferably under 60 characters, never more than 80.'},
        'fit': {'type': 'object', 'additionalProperties': False, 'required': sorted(PATHS),
                'properties': {p: {'type': 'string', 'enum': ['yes', 'no', 'depends']} for p in sorted(PATHS)}},
        'depends_on': {'type': ['string', 'null'], 'description': 'One condition of at most 100 characters, or null.'},
        'action': {'type': ['string', 'null'], 'description': 'At most 160 characters, null for news or no yes path.'},
        'evidence': {'type': 'string', 'description': 'An exact complete source sentence or clause, at most 300 characters.'},
        'judged': {'type': 'string', 'description': 'Supplied date, YYYY-MM-DD.'},
    }},
    {'type': 'null'},
]}


PROPOSAL_SCHEMA = {'type': 'object', 'additionalProperties': False, 'required': ['judgment'],
                   'properties': {'judgment': JUDGMENT_SCHEMA}}


def plain(value, limit, nullable=False, quote=False):
    if value is None and nullable:
        return
    if (not isinstance(value, str) or not value.strip() or value != value.strip()
            or len(value.encode('utf-16-le')) // 2 > limit
            or re.search(r'[<>`*\x00-\x1f\x7f-\x9f]|https?://|\S+@\S+|\b\d{3}[-. ]\d{3}[-. ]\d{4}\b', value.replace('\n', ' ') if quote else value)
            or any(unicodedata.category(c) in {'So', 'Cf'} for c in value)):
        raise ValueError('Invalid judgment text')


def complete_clause(quote, body=None):
    """A structural clause gate, not a deterministic test of semantic support."""
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", quote)
    if len(words) < 4 or words[-1].lower() in {'a', 'an', 'the', 'of', 'for', 'to', 'and', 'or', 'with', 'during', 'in', 'under', 'their', 'that', 'which', 'shall', 'must', 'will', 'may', 'can', 'should', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'has', 'have', 'had'}:
        return False
    predicate = r'\b(?:is|are|was|were|be|being|must|shall|will|may|can|cannot|should|has|have|had|does|do|applies|apply|requires|require|includes|include|provides|provide|directs|direct|announces|announce|rescinds|rescind|authorizes|authorize|allows|allow|prohibits|prohibit|enrolled|enroll|enrolls|contact|submit|use|review|read|reports|reported|report|ensure|ensures|retain|retains|remain|remains|continue|continues|establishes|establish|serves|serve|covers|cover|transition|discontinue|complete|comply|follow|attend|maintain|request|remove|coordinate|extend|celebrate)\b'
    if not re.search(predicate, quote, re.I):
        return False
    if quote[-1] in '.!?;:':
        return True
    if body is not None:
        for match in re.finditer(re.escape(quote), body):
            tail = body[match.end():].lstrip()
            if not tail or tail[0] in ',;:.!?':
                return True
    return False


def validate_judgment(value, body=None, title=None):
    if not isinstance(value, dict) or set(value) != KEYS or type(value['v']) is not int or value['v'] != 1:
        raise ValueError('Invalid judgment fields or version')
    if value['kind'] not in {'action', 'policy', 'news'}:
        raise ValueError('Invalid judgment kind')
    for key, limit in [('summary', 200), ('audience', 80), ('depends_on', 100), ('action', 160), ('evidence', 300)]:
        try:
            plain(value[key], limit, key in {'depends_on', 'action'}, key == 'evidence')
        except ValueError as error:
            raise ValueError('Invalid judgment ' + key + ': check length, contact details and plain text') from error
    summary = value['summary']
    if (any(c in summary for c in '-\u2010\u2011\u2012\u2013\u2014\u2212')
            or len(re.findall(r'[.!?](?:\s|$)', summary)) != 1 or summary[-1] not in '.!?'
            or (title and summary.rstrip('.!?').casefold() == title.rstrip('.!?').casefold())):
        raise ValueError('Summary must be one plain sentence without dashes or title repeat')
    fit = value['fit']
    if (not isinstance(fit, dict) or set(fit) != PATHS
            or any(type(v) is not str or v not in {'yes', 'no', 'depends'} for v in fit.values())):
        raise ValueError('Invalid separation or retirement relevance fit')
    if ('depends' in fit.values()) != (value['depends_on'] is not None):
        raise ValueError('Depends needs exactly one deciding condition')
    if value['depends_on'] is not None and not re.match(r'^(?:Only if|If|When|Unless)\b', value['depends_on']):
        raise ValueError('Depends must be phrased as a condition')
    if value['kind'] != 'news' and 'yes' in fit.values() and value['action'] is None:
        raise ValueError('A yes path needs an action for a non news notice')
    if value['kind'] == 'news' and value['action'] is not None:
        raise ValueError('News cannot require action')
    if not isinstance(value['judged'], str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value['judged']):
        raise ValueError('Invalid judgment date')
    date.fromisoformat(value['judged'])
    if body is not None and (not isinstance(body, str) or value['evidence'] not in body):
        raise ValueError('Evidence is not verbatim in confirmed source')
    if not complete_clause(value['evidence'], body):
        raise ValueError('Evidence must be a complete supporting sentence or clause')
    return value


def validate_feed(feed, now=None, base=None):
    now = now or datetime.now(timezone.utc)
    if not isinstance(base, dict):
        raise ValueError('Validated base feed is required for judgment publication')
    if not isinstance(feed, dict) or set(feed) != {'schema_version', 'seq', 'generated_at', 'expires_at', 'base_seq', 'base_sha256', 'notices'}:
        raise ValueError('Invalid judgment feed fields')
    if type(feed['schema_version']) is not int or feed['schema_version'] != 1:
        raise ValueError('Invalid judgment feed version')
    if (type(feed['seq']) is not int or not 1 <= feed['seq'] <= 9007199254740991
            or type(feed['base_seq']) is not int or feed['base_seq'] != feed['seq']
            or not isinstance(feed['base_sha256'], str) or not re.fullmatch(r'[a-f0-9]{64}', feed['base_sha256'])):
        raise ValueError('Invalid judgment feed binding')
    from validate_v2 import stamp
    generated, expires = stamp(feed['generated_at']), stamp(feed['expires_at'])
    if generated > now or expires != generated + timedelta(days=8) or now >= expires:
        raise ValueError('Future or expired judgment feed')
    if not isinstance(feed['notices'], list) or len(feed['notices']) > 3500:
        raise ValueError('Invalid judgment notice list')
    ids = set()
    for row in feed['notices']:
        if not isinstance(row, dict) or set(row) != {'id', 'title', 'body_sha256', 'judgment'}:
            raise ValueError('Invalid judgment notice fields')
        plain(row['id'], 250); plain(row['title'], 300)
        if row['id'] in ids or not isinstance(row['body_sha256'], str) or not re.fullmatch(r'[a-f0-9]{64}', row['body_sha256']):
            raise ValueError('Invalid judgment identity or body hash')
        ids.add(row['id'])
        validate_judgment(row['judgment'], title=row['title'])
        if row['judgment']['judged'] > generated.date().isoformat():
            raise ValueError('Judgment from the future')
    validate_binding(feed, base)
    return feed


def validate_binding(feed, base):
    """Join rows to the already validated base in both build and isolated signer."""
    raw = json.dumps(base, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
    if (feed['base_seq'] != base.get('seq') or feed['base_sha256'] != hashlib.sha256(raw).hexdigest()
            or feed['generated_at'] != base.get('generated_at') or feed['expires_at'] != base.get('expires_at')):
        raise ValueError('Judgment generation, expiry or base binding mismatch')
    notices = {}
    for block in base.get('sources', []):
        for notice in block.get('notices', []):
            notices.setdefault(notice['id'], []).append(notice)
    for row in feed['notices']:
        matches = notices.get(row['id'], [])
        if len(matches) != 1 or row['title'] != matches[0]['title']:
            raise ValueError('Judgment row must match exactly one base notice id and title')
        if matches[0].get('series') == 'VA_GOV' and matches[0].get('number', '').startswith('page:'):
            raise ValueError('VA page changes have no model judgment in revision 2')
    return feed
