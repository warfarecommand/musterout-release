"""Feed v2 data validation. Safe to copy into the release feed directory."""
from datetime import date, datetime, timedelta, timezone
import re
from urllib.parse import urlsplit, unquote

LINES = {'separation', 'retirement', 'va', 'skillbridge', 'reserve', 'leave', 'family'}
PATHS = {'resign', 'retire', 'eas', 'all'}
SOURCES = {'MARADMIN', 'ALMAR', 'ALNAV', 'ORDER'}


def clean(value):
    if isinstance(value, str) and re.search(r'[\x00-\x1f\x7f-\x9f]', value):
        raise ValueError('Control character in feed')
    if isinstance(value, dict):
        for key, item in value.items():
            clean(key)
            clean(item)
    elif isinstance(value, list):
        for item in value:
            clean(item)


def day(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Invalid ISO date')
    return date.fromisoformat(value)


def stamp(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', value):
        raise ValueError('Invalid timestamp')
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)


def official_url(source, value):
    if not isinstance(value, str) or len(value) > 500 or re.search(r'[\s<>\\?#]', value):
        raise ValueError('Invalid source URL')
    u = urlsplit(value)
    if u.scheme != 'https' or u.username or u.password or u.port or u.query or u.fragment:
        raise ValueError('Invalid source URL authority')
    # Encoded path separators and dot segments must not bypass the path check.
    if re.search(r'%2f|%5c', u.path, re.I) or any(p in {'.', '..'} for p in unquote(u.path).split('/')):
        raise ValueError('Invalid source URL path')
    if source in {'MARADMIN', 'ALMAR'}:
        valid = u.netloc == 'www.marines.mil' and re.fullmatch(r'/News/Messages/Messages-Display/Article/\d+/[A-Za-z0-9-]+/', u.path)
    elif source == 'ALNAV':
        valid = u.netloc == 'www.mynavyhr.navy.mil' and (u.path.startswith('/References/Messages/') or u.path.startswith('/Portals/55/Messages/'))
    elif source == 'ORDER':
        valid = u.netloc == 'www.marines.mil' and (u.path.startswith('/News/Publications/MCPEL/') or u.path.startswith('/Portals/1/Publications/'))
    else:
        valid = False
    if not valid:
        raise ValueError('URL does not belong to source')
    return value


def text(value, limit):
    if not isinstance(value, str) or not value.strip() or len(value.encode('utf-16-le')) // 2 > limit or re.search(r'[<>]', value):
        raise ValueError('Invalid notice text')


def validate_block(block, now=None):
    now = now or datetime.now(timezone.utc)
    clean(block)
    required = {'source', 'coverage', 'status', 'reason', 'last_attempt', 'last_success', 'window', 'checked_count', 'unclassified_count', 'truncated', 'body_available', 'notices'}
    if not isinstance(block, dict) or not required <= block.keys() or block['source'] not in SOURCES:
        raise ValueError('Invalid source block')
    source = block['source']
    text(block['coverage'], 2000)
    if block['status'] not in {'ok', 'failed'}:
        raise ValueError('Invalid source status')
    if block['status'] == 'ok' and block['reason'] is not None:
        raise ValueError('Successful source has a failure reason')
    if block['status'] == 'failed':
        text(block['reason'], 2000)
    attempt = stamp(block['last_attempt'])
    success = stamp(block['last_success']) if block['last_success'] is not None else None
    if attempt > now or (success and success > attempt) or (block['status'] == 'ok' and success is None):
        raise ValueError('Invalid source timestamps')
    window = block['window']
    if not isinstance(window, dict) or not {'from', 'to'} <= window.keys():
        raise ValueError('Invalid source window')
    start, end = day(window['from']), day(window['to'])
    if end < start or end - start > timedelta(days=30) or end > now.date():
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
        text(number, 200)
        if source == 'ORDER':
            expected = 'ORDER-' + re.sub(r'[^A-Z0-9]+', '-', number.upper()).strip('-')
        else:
            if not re.fullmatch(r'\d{1,3}/\d{2}', number):
                raise ValueError('Invalid notice number')
            expected = source + '-' + number.replace('/', '-')
        if n.get('id') != expected or expected in identities:
            raise ValueError('Invalid or duplicate notice identity')
        identities.add(expected)
        text(n.get('title'), 300)
        if 'summary' in n:
            text(n['summary'], 1000)
        official_url(source, n.get('url'))
        if not start <= day(n.get('posted')) <= end:
            raise ValueError('Notice outside source window')
        if type(n.get('body_available')) is not bool or (block['body_available'] and not n['body_available']):
            raise ValueError('Invalid notice body flag')
        for key, allowed in (('lines', LINES), ('paths', PATHS)):
            values = n.get(key)
            if not isinstance(values, list) or not values or any(not isinstance(v, str) or v not in allowed for v in values) or len(values) != len(set(values)):
                raise ValueError('Invalid notice classification')
        if n.get('action', 'informational') not in {'required', 'informational'} or n.get('confidence', 'low') not in {'high', 'medium', 'low'}:
            raise ValueError('Invalid notice action or confidence')
        if n.get('deadline') is not None:
            day(n['deadline'])
    return block


def validate_feed(feed, now=None):
    now = now or datetime.now(timezone.utc)
    clean(feed)
    if not isinstance(feed, dict) or type(feed.get('schema_version')) is not int or feed['schema_version'] != 2:
        raise ValueError('Invalid feed schema')
    if type(feed.get('seq')) is not int or not 1 <= feed['seq'] <= 9007199254740991:
        raise ValueError('Invalid feed sequence')
    generated, expires = stamp(feed.get('generated_at')), stamp(feed.get('expires_at'))
    if generated > now or expires != generated + timedelta(days=8) or now >= expires:
        raise ValueError('Future or expired feed')
    if type(feed.get('capture_replay', False)) is not bool:
        raise ValueError('Invalid capture flag')
    blocks = feed.get('sources')
    if not isinstance(blocks, list) or not blocks or len(blocks) > len(SOURCES):
        raise ValueError('Invalid sources')
    labels = set()
    for block in blocks:
        validate_block(block, now)
        if block['source'] in labels or stamp(block['last_attempt']) > generated:
            raise ValueError('Duplicate source or attempt after generation')
        labels.add(block['source'])
    return feed
