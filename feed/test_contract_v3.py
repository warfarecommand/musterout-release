"""Cross-profile publication rules using recorded public collector output."""
from copy import deepcopy
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import unittest

from validate_v3 import ACTIVE, canonical, validate_feed, validate_pair, validate_legacy

FIXTURES = Path(__file__).with_name('fixtures')


def pair():
    legacy = json.loads((FIXTURES / 'legacy.json').read_bytes())
    feed = json.loads((FIXTURES / 'page.json').read_bytes())
    feed.update(schema_version=3, seq=legacy['seq'] + 1, legacy_seq=legacy['seq'],
                legacy_sha256=hashlib.sha256(canonical(legacy)).hexdigest())
    return legacy, feed


class ContractTest(unittest.TestCase):
    def setUp(self):
        self.legacy, self.feed = pair()
        self.now = datetime.fromisoformat(self.feed['generated_at'].replace('Z', '+00:00')) + timedelta(seconds=1)

    def test_pair_and_original_projection(self):
        validate_pair(self.legacy, self.feed, self.now)
        self.assertEqual(len(self.legacy['sources']), 4)
        self.assertEqual({b['source'] for b in self.feed['sources']}, set(ACTIVE))
        self.assertEqual(canonical(self.feed['sources'][:4]), canonical(self.legacy['sources']))

    def test_schema_and_capture_are_explicit(self):
        for key, value in [('schema_version', 2), ('schema_version', True), ('capture_replay', None),
                           ('capture_replay', 0), ('capture_replay', True), ('legacy_seq', True)]:
            with self.subTest(key=key, value=value):
                feed = deepcopy(self.feed); feed[key] = value
                with self.assertRaises(ValueError): validate_feed(feed, self.now)
        for key in ['capture_replay', 'off_sources', 'legacy_sha256']:
            feed = deepcopy(self.feed); del feed[key]
            with self.assertRaises(ValueError): validate_feed(feed, self.now)

    def test_exact_seven_active_and_explicit_off(self):
        for kind in ['missing', 'duplicate', 'off_active', 'unknown', 'bad_off']:
            feed = deepcopy(self.feed)
            if kind == 'missing': feed['sources'].pop()
            if kind == 'duplicate': feed['sources'][-1] = deepcopy(feed['sources'][0])
            if kind == 'off_active': feed['sources'][-1]['source'] = 'M21_1'
            if kind == 'unknown': feed['sources'][-1]['source'] = 'NEWS'
            if kind == 'bad_off': feed['off_sources'][0]['reason'] = 'Not checked today'
            with self.subTest(kind=kind), self.assertRaises(ValueError): validate_feed(feed, self.now)

    def test_utf16_board_limit_and_legacy_exclusion(self):
        for profile in [self.feed, self.legacy]:
            feed = deepcopy(profile); feed['sources'][0].update(status='failed', reason='\U00010000' * 250)
            validator = validate_feed if profile['schema_version'] == 3 else validate_legacy
            validator(feed, self.now)
            feed['sources'][0]['reason'] += 'x'
            with self.assertRaises(ValueError): validator(feed, self.now)
        legacy = deepcopy(self.legacy); legacy['sources'].append(deepcopy(self.feed['sources'][-1]))
        with self.assertRaises(ValueError): validate_legacy(legacy, self.now)

    def test_signed_binding_requires_exact_canonical_military_values(self):
        feed = deepcopy(self.feed); feed['legacy_sha256'] = '0' * 64
        with self.assertRaises(ValueError): validate_pair(self.legacy, feed, self.now)
        # Python equality would treat these as equal; canonical parity must not.
        feed = deepcopy(self.feed); feed['sources'][0]['notices'][0]['relevant'] = 1
        with self.assertRaises(ValueError): validate_pair(self.legacy, feed, self.now)

    def test_canonical_resource_and_key_bounds(self):
        for value in [1.5, 9_007_199_254_740_992, {'nonascii\u0100': 1}, [None] * 50_001]:
            feed = deepcopy(self.feed)
            feed['sources'][0]['notices'][0]['extra'] = value
            with self.assertRaises(ValueError): validate_feed(feed, self.now)

    def test_va_evidence_summary_url_and_applicability(self):
        for mutation in ['summary', 'host', 'evidence', 'applicability']:
            feed = deepcopy(self.feed)
            notice = next(b for b in feed['sources'] if b['source'] == 'VA_GOV')['notices'][0]
            if mutation == 'summary': notice['summary'] = 'The source confirms your eligibility.'
            if mutation == 'host': notice['url'] = notice['url'].replace('news.va.gov', 'news.va.gov.example.com')
            if mutation == 'evidence': notice['source_evidence']['source_sha256'] = '0' * 64
            if mutation == 'applicability': notice['applicability'] = {'grades': ['e67']}
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): validate_feed(feed, self.now)


if __name__ == '__main__': unittest.main()
