#!/usr/bin/env python3
"""Verify W6 source rules and date behavior using the actual board resolver."""
import copy
import itertools
import json
import re
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'packs/usmc'
SEED = json.loads((ROOT / 'board/seed.json').read_text())
ITEMS = {item['id']: item for item in SEED['items']}
GATES = {'sep-ic': 365, 'sep-presep': 365, 'sep-trs': 180,
         'sep-capstone': 120, 'sep-cv': 90}
MOVE = {'fam-hhg-counsel', 'fam-hhg-appt', 'fam-hhg-entitlement'}
INTENT = {'va-intent', 'va-itf-complete'}
NEW_ITEMS = MOVE | INTENT | {id + '-appt' for id in GATES} | {
    'fam-va-dental-iv', 'fam-champva'}


def require(value, message):
    if not value:
        raise AssertionError(message)


def check():
    for id, days in GATES.items():
        record = ITEMS[id]
        require(record['basis'] == 'rule', id + ': deadline basis')
        require(record['due'] == {'item': 'va-service-end', 'days': -days},
                id + ': exact EAS day count without business-day adjustment')
        require(any(c['ref'] == 'MCO 1700.31A' for c in record['cite']),
                id + ': current TRP source')
        appointment = ITEMS[id + '-appt']
        require(appointment['kind'] == 'milestone' and appointment['due'] is None,
                id + ': separate confirmed appointment')
    for id in NEW_ITEMS | set(GATES) | {'sep-roob', 'sep-roob-ret', 'va-service-end'}:
        require(ITEMS[id]['cite'] and ITEMS[id]['verify'], id + ': source and office')
    for id in ('sep-roob', 'sep-roob-ret'):
        require(ITEMS[id]['due'] == {'item': 'sep-ic-appt', 'days': -7}
                and ITEMS[id]['basis'] == 'target', id + ': prework before appointment')
    for id in ('sb-coord', 'sb-packet', 'sb-approval', 'sb-sequence', 'sb-run', 'sb-start'):
        record = ITEMS[id]
        require('before SkillBridge participation' in ' '.join(record['how']),
                id + ': transition completion prerequisite')
        require(any(c['ref'] == 'NAVMC 1700.2B' and c['para'] == 'Encl (2) para 7'
                    for c in record['cite']), id + ': prerequisite source')
    require(ITEMS['fam-hhg-counsel']['basis'] == 'target', 'HHG appointment target')
    require(ITEMS['fam-hhg-entitlement']['due'] == {'byPath': {'eas': {'item': 'va-service-end', 'days': 180}, 'resign': {'item': 'va-service-end', 'days': 180}, 'retire': {'item': 'va-service-end', 'months': 36}}}, 'Path-specific HHG authority from service end')
    require(ITEMS['va-intent']['kind'] == 'milestone' and ITEMS['va-intent']['due'] is None,
            'Intent receipt must be an actual confirmed event')
    require(ITEMS['va-itf-complete']['basis'] == 'rule'
            and ITEMS['va-itf-complete']['due'] == {'item': 'va-intent', 'months': 12}, 'Calendar-year deadline follows confirmed receipt')
    require('calendar-year' in ' '.join(ITEMS['va-itf-complete']['how']), 'No 365-day ITF rule')
    rows = SEED['claim']['benefits']['rows']
    dental = next(row for row in rows if row.get('id') == 'benefit-va-dental-iv')
    champva = next(row for row in rows if row.get('id') == 'benefit-champva')
    require('Permanence is not required' in dental['detail'] and 'temporary' in dental['detail'],
            'Dental permanence and temporary-rating criteria')
    require('TRICARE' in champva['detail'] and 'permanent and total' in champva['detail'],
            'CHAMPVA criteria and exclusion')
    require(not re.search(r'state (?:property )?tax', json.dumps(rows).lower()),
            'No blanket state-tax benefit')
    for row in (dental, champva):
        require(row['cite'] and row['verify'], row['id'] + ': source and office')
    paths = 0
    for path, grade, reserve, sb, cat in itertools.product(
            ('resign', 'retire', 'eas'), ('officer', 'enlisted'),
            ('reserve', 'noreserve'), ('sb', 'nosb'), ('cat1', 'cat2', 'cat3')):
        if (path == 'resign' and grade == 'enlisted') or (path == 'retire' and reserve == 'reserve'):
            continue
        if grade == 'officer' and cat == 'cat1':
            continue
        flags = {path, grade, reserve, sb, cat}
        if path != 'retire':
            flags.add('notretire')
        included = {i['id'] for i in SEED['items'] if set(i['when']) <= flags}
        require(MOVE | INTENT | set(GATES) <= included, 'Missing coverage on ' + str(flags))
        paths += 1
    template = (ROOT / 'board/template.html').read_text()
    resolver = re.search(r'function resolve\(rule, c, depth\)\{.*?\n\}', template, re.S)
    require(resolver, 'Actual board date resolver is available')
    script = """const assert = require('node:assert/strict');
const DAY = 86400000;
const parseD = s => s ? Date.parse(s + 'T00:00:00Z') : null;
const addDays = (t, n) => t + n * DAY;
const addMonths = (t,n) => {const d=new Date(t),y=d.getUTCFullYear(),m=d.getUTCMonth()+n;return Date.UTC(y,m,Math.min(d.getUTCDate(),new Date(Date.UTC(y,m+1,0)).getUTCDate()));};
const INPUT = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const S = {items: INPUT.items,profile:{path:'eas'}};
""" + resolver.group() + """
const gates = INPUT.gates;
const c = {eas: parseD('2027-10-01')};
for (const end of ['2027-09-30', '2028-03-01', '2028-09-30']) {
  S.items['va-service-end'].due = {date: end};
  S.items['va-service-end'].doneOn = '2026-10-09';
  for (const [id, days] of Object.entries(gates)) {
    assert.equal(resolve(S.items[id].due, c), parseD(end) - days * DAY);
    S.items[id + '-appt'].due = {date: '2026-11-15'};
    assert.equal(resolve(S.items[id].due, {eas: parseD('2030-01-01')}), parseD(end) - days * DAY);
  }
}
S.items['va-service-end'].due = null;
for (const id of Object.keys(gates)) assert.equal(resolve(S.items[id].due, c), null);
for (const [receipt,deadline] of [['2027-03-01','2028-03-01'],['2028-02-29','2029-02-28']]) {
  S.items['va-intent'].due = {date: receipt};
  S.items['va-intent'].doneOn = '2026-10-09'; // completion day is not receipt day
  assert.equal(resolve(S.items['va-itf-complete'].due, c),parseD(deadline));
  assert.equal(resolve(S.items['va-itf-complete'].due,{eas:parseD('2030-01-01')}),parseD(deadline));
}
S.items['va-intent'].due=null;
assert.equal(resolve(S.items['va-itf-complete'].due,c),null);
for(const end of ['2027-08-31','2028-02-29'])for(const path of ['eas','resign','retire']) {
  S.profile.path=path;S.items['va-service-end'].due={date:end};
  const expected=path==='retire'?addMonths(parseD(end),36):addDays(parseD(end),180);
  assert.equal(resolve(S.items['fam-hhg-entitlement'].due,c),expected);
  assert.equal(resolve(S.items['fam-hhg-entitlement'].due,{eas:parseD('2030-01-01')}),expected);
}
S.items['va-service-end'].due=null;
assert.equal(resolve(S.items['fam-hhg-entitlement'].due,c),null);

"""
    # Script and data go through a file and stdin: Linux caps argv size (E2BIG on hosted CI).
    with tempfile.NamedTemporaryFile('w', suffix='.cjs', delete=False) as handle:
        handle.write(script)
    try:
        result = subprocess.run(['node', handle.name], input=json.dumps({'items': copy.deepcopy(ITEMS), 'gates': GATES}),
                                text=True, capture_output=True)
    finally:
        os.unlink(handle.name)
    require(result.returncode == 0, result.stderr)
    for filename in ('README.md', 'REVIEW.md', 'faq-eas.md', 'faq-retire.md', 'faq-resign.md', 'glossary.md'):
        text = (PACK / filename).read_text()
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' not in target and not target.startswith('#'):
                require('QC' not in target and '_sources' not in target, filename + ': private report link')
                require((PACK / target.split('#', 1)[0]).exists(), filename + ': missing local target')
    print(f'PASS: W6 rules, benefits, office confirmation and coverage on {paths} paths; '
          'actual board resolver checks EAS anchors, fixed appointments and leap-year intent deadlines.')


if __name__ == '__main__':
    check()
