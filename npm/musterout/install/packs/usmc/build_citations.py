#!/usr/bin/env python3
"""Rebuild citation locations from the generated seed and registered source texts."""
import json
from check_citations import PACK, DEFAULT_SEED, REG_FILES, SUPPLEMENTAL_SOURCES, seed_pairs, locate, is_web


def main():
    path = PACK / 'citations.json'
    prior = {(r['ref'], r['para']): r for r in json.loads(path.read_text())}
    rows = []
    pairs = seed_pairs(json.loads(DEFAULT_SEED.read_text()))
    ordered = [key for key in prior if key in pairs] + [key for key in pairs if key not in prior]
    for key in ordered:
        variants = pairs[key]
        previous = prior.get(key, {})
        old_records = previous.get('quotes', [previous])
        records = []
        for variant in variants:
            record = next((dict(r) for r in old_records if r.get('quote') == variant['quote'] and r.get('url') == variant.get('url')), {})
            supplemental = SUPPLEMENTAL_SOURCES.get(key)
            file = supplemental[0] if supplemental else REG_FILES.get(key[0])
            span = locate((PACK / file).read_text(), variant['quote']) if file else None
            record.update(variant, file=file, line_start=span[0] if span else None,
                          line_end=span[1] if span else None,
                          verified=bool(span) if file else None if is_web(variant.get('url')) else False)
            record.pop('quotes', None)
            if supplemental:
                record['source_url'] = supplemental[1]
            records.append(record)
        row = dict(previous)
        row.update(records[0])
        row.update(ref=key[0], para=key[1])
        statuses = [r['verified'] for r in records]
        row['verified'] = True if all(s is True for s in statuses) else None if all(s is None for s in statuses) else False
        if len(records) > 1:
            row['quotes'] = records
        else:
            row.pop('quotes', None)
        rows.append(row)
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n')
    print(f'Updated {len(rows)} citation pairs.')


if __name__ == '__main__':
    main()
