# VA source rules copied from musterout-watch 9d8dfd7fb4ce30237ff378e74266c7092485dc2a.
# Original protocol.py SHA-256: 393d4082b986e92095430784f40998214d6d20d8a5a25e0e0e1dfb7515eede4f
"""Feed v2 data validation. Safe to copy into the release feed directory."""
from datetime import date, datetime, timedelta, timezone
import re
from urllib.parse import urlsplit, unquote

LINES = {'separation', 'retirement', 'va', 'skillbridge', 'reserve', 'leave', 'family'}
PATHS = {'resign', 'retire', 'eas', 'all'}
VA_SOURCES = {'ECFR', 'FEDERAL_REGISTER', 'M21_1', 'VA_GOV'}
SOURCES = {'MARADMIN', 'ALMAR', 'ALNAV', 'ORDER'} | VA_SOURCES
# Explicit standing rulings only. Enabled-source errors cannot opt themselves out.
OFF_SOURCE_REASONS = {'M21_1': 'VA blocks automated reads'}
VA_FALLBACK = 'The official source records a possible VA rule or program change. Read the official text before acting.'
APPLICABILITY = {
    'grades': {'o5', 'o14', 'cwo45', 'wo13', 'e89', 'e67', 'e15'},
    'service_types': {'officer', 'enlisted'},
    'reserve': {True, False}, 'skillbridge': {True, False},
}


SOURCE_BLOCK_FIELDS_BY_VERSION = {3: frozenset({'source', 'coverage', 'status', 'reason', 'last_attempt', 'last_success', 'window', 'checked_count', 'unclassified_count', 'truncated', 'body_available', 'notices'})}
ORDER_BLOCK_FIELDS = frozenset({'unresolved_count', 'unresolved_items'})


def validate_source_block_fields(block, schema_version=3):
    required = SOURCE_BLOCK_FIELDS_BY_VERSION[schema_version]
    allowed = required | (ORDER_BLOCK_FIELDS if block.get('source') == 'ORDER' else frozenset())
    if not required <= block.keys() or not block.keys() <= allowed:
        raise ValueError('Invalid schema-3 source-block fields')
    return block


def failure_reason(value):
    """Bound public failure summaries to the installed board's 500 UTF-16 units."""
    value = re.sub(r'[<>\x00-\x1f\x7f-\x9f]', ' ', str(value)).strip()
    raw = value.encode('utf-16-le')
    if len(raw) > 1000:
        value = raw[:994].decode('utf-16-le', errors='ignore').rstrip() + '...'
    return value


def validate_applicability(notice):
    if 'applicability' not in notice:
        if any(k in notice for k in ('applicability_evidence', 'applicability_version')):
            raise ValueError('Applicability metadata without dimensions')
        return
    value = notice['applicability']
    if not isinstance(value, dict) or not value.keys() <= APPLICABILITY.keys():
        raise ValueError('Invalid notice applicability')
    for key, values in value.items():
        kind = bool if key in {'reserve', 'skillbridge'} else str
        if (not isinstance(values, list) or not values
                or any(type(v) is not kind or v not in APPLICABILITY[key] for v in values)
                or len(values) != len(set(values))):
            raise ValueError('Invalid applicability dimension')
    if 'applicability_version' in notice and (
            type(notice['applicability_version']) is not int or notice['applicability_version'] != 1):
        raise ValueError('Invalid applicability rule version')
    if 'applicability_evidence' in notice:
        evidence = notice['applicability_evidence']
        if not isinstance(evidence, dict) or evidence.keys() != value.keys():
            raise ValueError('Applicability evidence differs from dimensions')
        for phrases in evidence.values():
            if not isinstance(phrases, list) or not 1 <= len(phrases) <= 4:
                raise ValueError('Invalid applicability evidence list')
            for phrase in phrases:
                text(phrase, 500)
                if '@' in phrase or re.search(r'https?://|\b\d{3}[-. ]\d{3}[-. ]\d{4}\b', phrase):
                    raise ValueError('Contact information in applicability evidence')


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
    elif source == 'ECFR':
        valid = u.netloc == 'www.ecfr.gov' and re.fullmatch(r'/current/title-38/chapter-I/part-[34]/section-[34]\.\d+[a-z]?(?:-(?:[34]\.)?\d+[a-z]?)?', u.path)
    elif source == 'FEDERAL_REGISTER':
        valid = u.netloc == 'www.federalregister.gov' and re.fullmatch(r'/documents/\d{4}/\d{2}/\d{2}/\d{4}-\d{4,6}/[A-Za-z0-9-]+/?', u.path)
    elif source == 'M21_1':
        valid = u.netloc == 'www.knowva.ebenefits.va.gov' and re.fullmatch(r'/system/templates/selfservice/va_ssnew/help/customer/locale/en-[Uu][Ss]/portal/\d+/content/\d+/[A-Za-z0-9-]+', u.path)
    elif source == 'VA_GOV':
        valid = ((u.netloc == 'www.va.gov' and u.path.startswith(('/resources/', '/disability/', '/health-care/')))
                 or (u.netloc == 'news.va.gov' and re.fullmatch(r'/(?:press-room/[A-Za-z0-9-]+|\d+/[A-Za-z0-9-]+)/', u.path)))
    else:
        valid = False
    if not valid:
        raise ValueError('URL does not belong to source')
    return value


def text(value, limit):
    if not isinstance(value, str) or not value.strip() or len(value.encode('utf-16-le')) // 2 > limit or re.search(r'[<>]', value):
        raise ValueError('Invalid notice text')


VA_NOTICE_FIELDS = {
    'series', 'number', 'id', 'title', 'url', 'posted', 'relevant', 'lines', 'paths',
    'action', 'summary', 'confidence', 'deadline', 'body_available', 'identifiers',
    'change', 'source_evidence', 'rule_type', 'comments_close_on', 'cfr_parts',
    'diagnostic_code_evidence', 'applicability', 'applicability_evidence', 'applicability_version',
}


def va_summary(notice):
    """Canonical VA prose from validated structured facts, never source/model text."""
    source = notice['series']
    if source not in VA_SOURCES:
        raise ValueError('Invalid VA summary source')
    identifiers = notice['identifiers']
    for identity in identifiers:
        validate_native_id(identity)
    cfr = sorted({f"{i['title']} CFR {i['section']}" for i in identifiers if 'section' in i})
    codes = sorted({i['dc'] for i in identifiers if 'dc' in i})
    manuals = sorted({i['m21_1'] for i in identifiers if 'm21_1' in i})
    documents = sorted({i['document_number'] for i in identifiers if 'document_number' in i})
    def bounded(values):
        return ', '.join(values[:3]) + (f" and {len(values)-3} more" if len(values) > 3 else '')
    def date_label(value):
        d = day(value)
        months = ('JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC')
        return f'{d.day:02} {months[d.month-1]} {d.year:04}'
    change = notice['change']
    kind = change['kind']
    if kind not in {'published', 'amended', 'removed', 'added', 'updated', 'version_changed'}:
        raise ValueError('Invalid VA summary change')
    if source == 'FEDERAL_REGISTER':
        rule = {'final': 'final rule', 'proposed': 'proposed rule'}[notice['rule_type']]
        target = bounded(cfr) if cfr else 'Federal Register document ' + bounded(documents)
        result = f'VA published a {rule} about {target}'
    elif source == 'ECFR':
        action = {'amended': 'an amendment to', 'added': 'the addition of', 'removed': 'the removal of',
                  'published': 'a publication of', 'updated': 'an update to', 'version_changed': 'a version change to'}[kind]
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


def validate_va_summary(summary, notice=None):
    if not isinstance(notice, dict) or summary != va_summary(notice):
        raise ValueError('VA summary differs from the structured template')
    text(summary, 1000)
    return summary


def refresh_va_notice(notice):
    """Discard legacy generated fields and reconstruct prose without reading it."""
    for key in list(notice):
        if key not in VA_NOTICE_FIELDS or key == 'summary':
            del notice[key]
    notice['summary'] = va_summary(notice)
    return notice


def validate_native_id(value):
    """Native official identity, never an inferred topic or a local rule key."""
    if not isinstance(value, dict):
        raise ValueError('Invalid native identifier')
    keys = set(value)
    if keys == {'title', 'part', 'section'}:
        if (type(value['title']) is int and 1 <= value['title'] <= 50
                and type(value['part']) is int and value['part'] > 0
                and isinstance(value['section'], str)
                and re.fullmatch(str(value['part']) + r'\.\d+[a-z]?(?:-(?:' + str(value['part']) + r'\.)?\d+[a-z]?)?', value['section'])):
            return value
    elif keys == {'dc'}:
        if isinstance(value['dc'], str) and re.fullmatch(r'\d{4}', value['dc']):
            return value
    elif keys == {'m21_1'}:
        if isinstance(value['m21_1'], str) and re.fullmatch(r'[IVX]+(?:\.[A-Za-z0-9]+){1,7}', value['m21_1']):
            return value
    elif keys == {'document_number'}:
        if isinstance(value['document_number'], str) and re.fullmatch(r'\d{4}-\d{4,6}', value['document_number']):
            return value
    elif keys == {'form_number'}:
        if isinstance(value['form_number'], str) and re.fullmatch(r'(?:VA|DD|NAVMC) [A-Za-z0-9][A-Za-z0-9 ()-]{0,60}', value['form_number']):
            return value
    elif keys in ({'issuance', 'paragraph'}, {'issuance', 'paragraph', 'volume'}):
        if (isinstance(value['issuance'], str) and re.fullmatch(r'(?:DoDI|DoDM|DoDD|MCO|SECNAVINST) \d+[A-Za-z0-9. -]{0,40}', value['issuance'])
                and isinstance(value['paragraph'], str) and re.fullmatch(r'[A-Za-z0-9.()]{1,40}', value['paragraph'])
                and ('volume' not in value or (value['issuance'].startswith('DoDM ') and type(value['volume']) is int and value['volume'] > 0))):
            return value
    elif keys == {'url'}:
        if not isinstance(value['url'], str) or len(value['url']) > 500 or re.search(r'[\s<>\\]', value['url']):
            raise ValueError('Invalid native document URL')
        parsed = urlsplit(value['url'])
        official_url('VA_GOV', parsed._replace(query='', fragment='').geturl())
        return value
    raise ValueError('Invalid native identifier')


def validate_va_notice(notice):
    import json
    if not notice.keys() <= VA_NOTICE_FIELDS:
        raise ValueError('Unsupported VA notice fields')
    validate_va_summary(notice.get('summary'), notice)
    identifiers = notice.get('identifiers')
    if not isinstance(identifiers, list) or not 1 <= len(identifiers) <= 200:
        raise ValueError('Invalid native identifier list')
    seen = set()
    for value in identifiers:
        validate_native_id(value)
        key = json.dumps(value, sort_keys=True)
        if key in seen:
            raise ValueError('Duplicate native identifier')
        seen.add(key)
    source = notice['series']
    number = notice['number']
    if source == 'FEDERAL_REGISTER':
        if ({'document_number': number} not in identifiers or '/' + number + '/' not in notice['url']
                or notice.get('rule_type') not in {'final', 'proposed'}):
            raise ValueError('Federal Register native identity mismatch')
        if notice.get('comments_close_on') != notice.get('deadline'):
            raise ValueError('Federal Register comment deadline mismatch')
    elif source == 'ECFR':
        parts = number.split(':')
        if (len(parts) != 5 or parts[0] != '38' or parts[1] not in {'3', '4'}
                or {'title': 38, 'part': int(parts[1]), 'section': parts[2]} not in identifiers
                or not notice['url'].endswith('/section-' + parts[2])):
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
        if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
            raise ValueError('Invalid VA source hash')
    if change.get('scope') not in {'identified', 'section', 'document'}:
        raise ValueError('Invalid VA change scope')
    if type(change.get('effective_unknown')) is not bool or change['effective_unknown'] != (change.get('effective_from') is None):
        raise ValueError('Invalid VA effective-date certainty')
    for key in ('published_at', 'effective_from', 'effective_to'):
        if change.get(key) is not None:
            day(change[key])
    stamp(change.get('observed_at'))
    if change.get('effective_from') and change.get('effective_to') and change['effective_to'] < change['effective_from']:
        raise ValueError('Invalid VA effective-date interval')
    evidence = notice.get('source_evidence')
    if (not isinstance(evidence, dict) or evidence.get('basis') not in {'official_metadata', 'official_body', 'snapshot_diff'}
            or evidence.get('source_sha256') != change['after_hash']):
        raise ValueError('Invalid VA source evidence')
    text(evidence.get('quote'), 500)
    if '@' in evidence['quote'] or re.search(r'https?://|\b\d{3}[-. ]\d{3}[-. ]\d{4}\b', evidence['quote']):
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
            text(row.get('quote'), 500)
    if 'cfr_parts' in notice:
        if (not isinstance(notice['cfr_parts'], list) or len(notice['cfr_parts']) > 100
                or any(not isinstance(ref, dict) or set(ref) != {'title', 'part'}
                       or type(ref['title']) is not int or not 1 <= ref['title'] <= 50
                       or type(ref['part']) is not int or ref['part'] < 1 for ref in notice['cfr_parts'])):
            raise ValueError('Invalid official CFR part references')
    # Existing military applicability rules cannot establish VA eligibility.
    if notice.get('applicability'):
        raise ValueError('VA applicability requires a supported evidence rule')


def validate_block(block, now=None):
    now = now or datetime.now(timezone.utc)
    clean(block)
    required = {'source', 'coverage', 'status', 'reason', 'last_attempt', 'last_success', 'window', 'checked_count', 'unclassified_count', 'truncated', 'body_available', 'notices'}
    if not isinstance(block, dict) or not required <= block.keys() or block['source'] not in SOURCES:
        raise ValueError('Invalid source block')
    source = block['source']
    text(block['coverage'], 2000)
    if block['status'] not in {'ok', 'failed', 'off'}:
        raise ValueError('Invalid source status')
    if block['status'] == 'off':
        if (source not in OFF_SOURCE_REASONS or block['reason'] != OFF_SOURCE_REASONS[source]
                or block['last_success'] is not None or block['notices'] != []
                or block['checked_count'] != 0 or block['unclassified_count'] != 0
                or block['truncated'] is not False or block['body_available'] is not False):
            raise ValueError('Invalid off source')
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
        if source in VA_SOURCES:
            if not re.fullmatch(r'[A-Za-z0-9.:-]{1,200}', number):
                raise ValueError('Invalid VA notice number')
            expected = source + '-' + number
            validate_va_notice(n)
            if stamp(n['change']['observed_at']) > attempt:
                raise ValueError('VA change observed after source attempt')
        elif source == 'ORDER':
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
        validate_applicability(n)
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
        if block['status'] == 'off':
            raise ValueError('Off sources belong in off_sources, not checked sources')
        if block['source'] in labels or stamp(block['last_attempt']) > generated:
            raise ValueError('Duplicate source or attempt after generation')
        labels.add(block['source'])
    off_sources = feed.get('off_sources', [])
    if not isinstance(off_sources, list) or len(off_sources) > len(OFF_SOURCE_REASONS):
        raise ValueError('Invalid off_sources')
    for off in off_sources:
        if (not isinstance(off, dict) or set(off) != {'source', 'reason'}
                or off.get('source') not in OFF_SOURCE_REASONS or off['source'] in labels
                or off.get('reason') != OFF_SOURCE_REASONS[off['source']]):
            raise ValueError('Invalid or duplicate off source')
        labels.add(off['source'])
    return feed
