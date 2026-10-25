"""Sourced IDES tasks. Ordinary seed records are never rewritten here."""
import json
from pathlib import Path


def append_ides_items(items):
    data = json.loads((Path(__file__).resolve().parent.parent / 'packs/usmc/ides.json').read_text())
    seen = {i['id'] for i in items}
    for requirement in data['requirements']:
        for item_id, kind in requirement['newItems'].items():
            if item_id in seen:
                raise ValueError('IDES item collision: ' + item_id)
            label = data['labels'][item_id]
            # Direct quotations are not invented from research summaries.
            # The IDES drawer renders assertion-level source links and locators.
            items.append(dict(id=item_id, loe='va', order=2000 + len(items), kind=kind,
                              title=label, label=label, brief=requirement['brief'],
                              why=requirement['brief'], how=[requirement['action']],
                              owner='You', due=None, window=None, basis='rule',
                              critical=requirement['id'] in {'IDS-R012','IDS-R016','IDS-R018','IDS-R019'},
                              presence=False, cite=[],
                              verify=requirement['office'],
                              status='open', doneOn=None, notes='', user=False,
                              when=['ides'], after=[]))
            seen.add(item_id)
