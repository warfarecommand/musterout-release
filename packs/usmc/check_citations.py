#!/usr/bin/env python3
"""Check seed coverage, all quote variants, statuses, and inclusive line ranges."""
import argparse
import bisect
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

PACK = Path(__file__).resolve().parent
DEFAULT_SEED = PACK.parent.parent / 'board' / 'seed.json'
REG_FILES = {
    'MCO 1900.16 CH-3 (MARCORSEPMAN)': 'regs/mco-1900.16-ch3.txt',
    'MCO 1050.3J': 'regs/mco-1050.3j.txt',
    'NAVMC 1700.2B': 'regs/navmc-1700.2b.txt',
    'MARADMIN 175/24': 'regs/maradmin-175-24.txt',
    'MARADMIN 045/25': 'regs/maradmin-045-25.txt',
    'MARADMIN 454/26': 'regs/maradmin-454-26.txt',
    'MARADMIN 280/24': 'regs/maradmin-280-24.txt',
    'MARADMIN 326/23': 'regs/maradmin-326-23.txt',
}
SUPPLEMENTAL_SOURCES = {
    ('HQMC MMSR-2 enlisted retirement guidance', 'Traditional Retirement'): (
        'regs/mmsr-2-enlisted-retirements.txt',
        'https://www.manpower.marines.mil/Divisions/Manpower-Management/Separation-and-Retirements-Branch/Active-Duty-Retirements-Separations/'),
    ('HQMC MMSR-2 enlisted retirement guidance', 'Outside of 6-18 month window'): (
        'regs/mmsr-2-enlisted-retirements.txt',
        'https://www.manpower.marines.mil/Divisions/Manpower-Management/Separation-and-Retirements-Branch/Active-Duty-Retirements-Separations/'),
    ('HQMC MMSR-2 enlisted retirement guidance', 'OCONUS'): (
        'regs/mmsr-2-enlisted-retirements.txt',
        'https://www.manpower.marines.mil/Divisions/Manpower-Management/Separation-and-Retirements-Branch/Active-Duty-Retirements-Separations/'),
    ('USMC TRP checklist', 'Step One'): (
        'regs/mccs-trp-checklist.txt',
        'https://hawaii.usmc-mccs.org/marine-family-support/transition-readiness-program'),
    ('USMC TRP checklist', 'Step Four'): (
        'regs/mccs-trp-checklist.txt',
        'https://hawaii.usmc-mccs.org/marine-family-support/transition-readiness-program'),
    ('USMC TRP checklist', 'Step Five'): (
        'regs/mccs-trp-checklist.txt',
        'https://hawaii.usmc-mccs.org/marine-family-support/transition-readiness-program'),
    ('2026 DoW SkillBridge MOU', '4.2.7'): (
        'regs/dow-skillbridge-mou.txt',
        'https://www.skillbridge.mil/static/docs/2026_DoW_SkillBridge_MOU_BLANK.pdf'),
    ('VA Benefits and Services Participant Guide v6.1', 'Module 3'): (
        'regs/va-benefits-participant-guide.txt',
        'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf'),
    ('VA Benefits and Services Participant Guide v6.1', 'Module 3, p. 72'): (
        'regs/va-benefits-participant-guide.txt',
        'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf'),
    ('USMC TRP checklist', 'Step Two'): (
        'regs/mccs-trp-checklist.txt',
        'https://hawaii.usmc-mccs.org/marine-family-support/transition-readiness-program'),
    ('USMC TRP checklist', 'Step Three'): (
        'regs/mccs-trp-checklist.txt',
        'https://hawaii.usmc-mccs.org/marine-family-support/transition-readiness-program'),
    ('VA Benefits and Services Participant Guide v6.1', 'Module 3, p. 80'): (
        'regs/va-benefits-participant-guide.txt',
        'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf'),
    ('VA Benefits and Services Participant Guide v6.1', 'Module 2, p. 41'): (
        'regs/va-benefits-participant-guide.txt',
        'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf'),
    ('VA Benefits and Services Participant Guide v6.1', 'Module 3, p. 73'): (
        'regs/va-benefits-participant-guide.txt',
        'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf'),
    ('VA Benefits and Services Participant Guide v6.1', 'Converting SGLI to VGLI'): (
        'regs/va-benefits-participant-guide.txt',
        'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf'),
    ('VA Benefits and Services Participant Guide v6.1', 'Module 4, p. 94'): (
        'regs/va-benefits-participant-guide.txt',
        'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf'),
}
WEB_HOSTS = {'va.gov', 'benefits.va.gov', 'tricare.mil', 'dol.gov',
             'milconnect.dmdc.osd.mil'}


def normalize(text):
    # whitespace, curly quotes, and the page furniture the PDFs leave between lines do not change what a quote says
    text = text.replace(chr(0x2019), "'").replace(chr(0x2018), "'").replace(chr(0x201c), '"').replace(chr(0x201d), '"')
    return ' '.join(text.split())

def fragments_match(quote, haystack):
    # a quote may elide text with "..."; every fragment must appear in order
    parts = [normalize(x) for x in quote.split("...") if normalize(x)]
    pos = 0
    for part in parts:
        i = haystack.find(part, pos)
        if i < 0: return False
        pos = i + len(part)
    return bool(parts)


def is_web(url):
    host = urlparse(url or '').hostname or ''
    return host.removeprefix('www.') in WEB_HOSTS


def seed_pairs(seed):
    pairs = {}
    for item in seed['items']:
        for cite in item.get('cite', []):
            key = (cite['ref'], cite['para'])
            variants = pairs.setdefault(key, [])
            value = {'quote': cite['quote'], 'url': cite.get('url')}
            if value not in variants:
                variants.append(value)
    return pairs


def locate(text, quote):
    """Whitespace only normalization; preserve punctuation and page furniture."""
    tokens = list(re.finditer(r'\S+', text))
    flat = ' '.join(m.group() for m in tokens).replace(chr(0x2019), "'").replace(chr(0x2018), "'").replace(chr(0x201c), '"').replace(chr(0x201d), '"')
    starts = []
    offset = 0
    for token in tokens:
        starts.append(offset)
        offset += len(token.group()) + 1
    parts = [normalize(x) for x in quote.split('...') if normalize(x)]
    if not parts:
        return None
    pos = flat.find(parts[0])
    if pos < 0:
        return None
    end = pos + len(parts[0])
    for part in parts[1:]:
        nxt = flat.find(part, end)
        if nxt < 0:
            return None
        end = nxt + len(part)
    first = bisect.bisect_right(starts, pos) - 1
    last = bisect.bisect_right(starts, end - 1) - 1
    # Count LF only: form feed is a page break, not an extra numbered line.
    return (text.count('\n', 0, tokens[first].start()) + 1,
            text.count('\n', 0, tokens[last].end()) + 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=Path, default=DEFAULT_SEED)
    parser.add_argument('--require-all-verified', action='store_true',
                        help='Also fail on accurately recorded unavailable quotes.')
    args = parser.parse_args()
    try:
        pairs = seed_pairs(json.loads(args.seed.read_text()))
        entries = json.loads((PACK / 'citations.json').read_text())
        if not isinstance(entries, list):
            raise ValueError('citations.json must be an array')
        errors = []
        actual = {}
        texts = {}
        for entry in entries:
            key = (entry['ref'], entry['para'])
            if key in actual:
                errors.append(f'Duplicate pair: {key}')
            actual[key] = entry
        if set(actual) != set(pairs):
            errors.append(f'Seed coverage differs: missing={set(pairs)-set(actual)}, extra={set(actual)-set(pairs)}')
        counts = {True: 0, False: 0, None: 0}
        quotes_checked = 0
        for key, variants in pairs.items():
            if key not in actual:
                continue
            entry = actual[key]
            records = entry.get('quotes', [entry])
            if [(r['quote'], r.get('url')) for r in records] != [(v['quote'], v['url']) for v in variants]:
                errors.append(f'Seed quote or URL variants differ: {key}')
                continue
            for record in records:
                quotes_checked += 1
                supplemental = SUPPLEMENTAL_SOURCES.get(key)
                expected_file = supplemental[0] if supplemental else REG_FILES.get(key[0])
                if supplemental and record.get('source_url') != supplemental[1]:
                    errors.append(f'Wrong supplemental source URL: {key}')
                expected_status = None if expected_file is None and is_web(record.get('url')) else False
                span = None
                if expected_file:
                    if expected_file not in texts:
                        texts[expected_file] = (PACK / expected_file).read_text()
                    span = locate(texts[expected_file], record['quote'])
                    expected_status = span is not None
                if record['verified'] is not expected_status or record['file'] != expected_file:
                    errors.append(f'Wrong status or file: {key}: {record["quote"][:65]}')
                stored_span = (record['line_start'], record['line_end'])
                if stored_span != (span or (None, None)):
                    errors.append(f'Wrong line range: {key}: stored={stored_span}, expected={span}')
                if span and not fragments_match(record['quote'], normalize('\n'.join(texts[expected_file].split('\n')[span[0]-1:span[1]]))):
                    errors.append(f'Quote missing from recorded span: {key}')
                if args.require_all_verified and expected_status is not True:
                    errors.append(f'Unavailable or external quote: {key}')
            # Pair status is true only when every variant is found, null only
            # when every variant is a web citation, otherwise false.
            statuses = [r['verified'] for r in records]
            aggregate = True if all(s is True for s in statuses) else None if all(s is None for s in statuses) else False
            if entry['verified'] is not aggregate:
                errors.append(f'Wrong pair aggregate: {key}')
            if len(records) > 1:
                for field in ('quote', 'url', 'file', 'line_start', 'line_end'):
                    if entry.get(field) != records[0].get(field):
                        errors.append(f'Primary quote field differs: {key}: {field}')
            counts[aggregate] += 1
        expected_files = (set(REG_FILES.values()) | {'regs/maradmin-625-24.txt'}
                          | {source[0] for source in SUPPLEMENTAL_SOURCES.values()})
        found_files = {str(p.relative_to(PACK)) for p in (PACK / 'regs').glob('*.txt')}
        if found_files != expected_files:
            errors.append('Source file set differs from the required texts')
        source_urls = {}
        for (ref, para), variants in pairs.items():
            if ref in REG_FILES:
                source_urls[REG_FILES[ref]] = variants[0]['url']
        source_urls.update({file: url for file, url in SUPPLEMENTAL_SOURCES.values()})
        source_urls['regs/maradmin-625-24.txt'] = (
            'https://www.marines.mil/News/Messages/Messages-Display/Article/4015114/'
            'advance-notification-of-forthcoming-changes-to-mco-10503j-regulations-for-leave/')
        for path in sorted((PACK / 'regs').glob('*.txt')):
            first = path.read_text().split('\n', 1)[0]
            relative = str(path.relative_to(PACK))
            expected_url = source_urls.get(relative)
            if expected_url and first != 'SOURCE: ' + expected_url:
                errors.append(f'SOURCE header differs from seed: {path.name}')
            if not expected_url or first != 'SOURCE: ' + expected_url:
                errors.append(f'Missing official SOURCE header: {path.name}')
        if errors:
            for error in errors:
                print('FAIL:', error, file=sys.stderr)
            return 1
        print(f'PASS: {len(entries)} pairs, {quotes_checked} unique quote/URL variants; '
              f'{counts[True]} verified, {counts[False]} unverified, {counts[None]} external web pairs. '
              'All statuses, seed quotes, URLs, and line ranges match.')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
