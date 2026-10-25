"""MTN-115 bounded VA actions. Existing record schema and person-owned state stay intact."""
from copy import deepcopy
import json
from pathlib import Path

BDD = 'https://www.va.gov/disability/how-to-file-claim/when-to-file/pre-discharge-claim/'
FILE = 'https://www.va.gov/disability/how-to-file-claim/'
HELP = 'https://www.va.gov/get-help-from-accredited-representative/'
MTF = 'https://www.health.mil/Military-Health-Topics/Access-Cost-Quality-and-Safety/DES/Separation-Health-Assessment?type=FAQ'
COURT = 'https://www.uscourts.cavc.gov/appeal.php'


def apply_va115(items, claim, contacts):
    by_id = {i['id']: i for i in items}

    def change(id, title=None, why=None, how=None, verify=None, **fields):
        i = by_id[id]
        if title:
            i.update(title=title, label=title)
        if why:
            i.update(why=why, brief=why)
        if how is not None:
            i['how'] = list(how)
        if verify is not None:
            i['verify'] = verify
        i.update(fields)
        return i

    def add(id, title, why, how, verify, url, order):
        i = deepcopy(by_id['va-records'])
        i.update(id=id, title=title, label=title, why=why, brief=why, how=list(how),
                 verify=verify, owner='You', due=None, window=None, basis='rule',
                 when=[], order=order, critical=False, presence=False,
                 cite=[])
        items.append(i)
        by_id[id] = i

    # R001: the shared resolver already distinguishes action types. Confirmation
    # of a future last-active date is planning evidence, never actual release.
    service = change('va-service-end',
        why='Confirm the last active-duty day with IPAC and MMSR-2. Keep it separate from the action date, earlier leave and actual release.',
        how=[
            'Identify EAS, regular-commission resignation, Fleet Marine Corps Reserve (FMCR) transfer or Retired List placement with IPAC and MMSR-2.',
            'For ordinary Retired List retirement, the last active-duty day is the day before the effective retirement date. Ordinary FMCR and resignation use the action date. IPAC and MMSR-2 must confirm your action and any exception.',
            'Keep projected, approved and actual events distinct. A confirmed future date or a completed task does not prove you have left active duty.',
            'Record the office role, what date was confirmed and when it was confirmed in optional notes. Leave and SkillBridge dates never replace service end.'
        ])
    for id in ['sep-eas', 'ret-day', 'ret-fmcr-day']:
        by_id[id]['how'].append('Retain the projected or approved action separately from actual release. IPAC and MMSR-2 must confirm your last active-duty day; a future confirmed date is still a plan.')

    change('va-file', title='Check the BDD filing route',
        why='BDD uses a known anticipated release date 180 through 90 days away, full-time active duty and 45-day exam availability. VA decides program handling; these dates alone do not establish acceptance.',
        how=[
            'Check the official VA pre-discharge route. Qualifying full-time active Reserve service can be included; a Reserve affiliation choice does not establish duty status.',
            'The 180-to-90-day date window includes both endpoints and does not move for weekends. The earlier 150-day date is only a planning target.',
            'For BDD or IDES, complete SHA Part A and submit it with the claim. Part A is your history, not the clinical assessment. Finish every phase of the VA and DoD separation exam before release, following the responsible offices\' instructions.',
            'For BDD, be available for exams for 45 days from actual VA claim receipt. Ask VA about exclusions, missing-document handling and VA-caused exam-delay exceptions; no automatic loss of BDD is inferred.',
            'Confirm filing channel and records with VA. Keep the actual claim receipt separately from a draft, upload or local task completion. Standard filing stays available while records or help are being obtained.'
        ], verify='VA BDD office: Does this duty status, anticipated release date, actual receipt, exam availability and any exception qualify for BDD handling? Completion evidence: the specific VA response and, only if filed, the actual receipt.',
        due={'item': 'va-service-end', 'days': -150},
        window={'from': {'item': 'va-service-end', 'days': -180}, 'to': {'item': 'va-service-end', 'days': -90}}, basis='target')

    add('va-standard', 'File through the standard claim route',
        'Standard filing stays available before or after discharge, including when BDD is early, unavailable or uncertain. Do not wait for a complete local checklist.',
        ['Use VA\'s official disability claim instructions. Under 90 days, ask VA about a standard pre-discharge claim; you do not have to wait until discharge.',
         'Submit available evidence through the official route and ask VA for help obtaining the rest. A VSO appointment, paid document, upload or diagnosis entered on this board is not a filing prerequisite.',
         'Keep the actual VA receipt if you file. Opening a form, saving a draft or selecting this route does not submit a claim.'],
        'VA or an accredited representative: Which standard route applies to this release date and duty status? Completion evidence: the route selected, with actual VA receipt recorded separately if submitted.', FILE, 1)

    change('va-parta', title='Complete SHA Part A for BDD or IDES',
        why='SHA Part A is the member history for BDD or IDES. The clinical assessment and DoD acceptance are separate events; Part A alone does not complete the separation exam.',
        how=['For BDD or IDES, complete the official SHA Part A member history and confirm its inclusion and receipt with the claim.',
             'Keep member-history completion, submission and VA receipt separate from the clinical assessment, report receipt and DoD acceptance.',
             'Outside BDD or with fewer than 90 days remaining, contact your military treatment facility (MTF) for the separation-exam route. Care does not wait for a claim.',
             'Finish every phase of the VA and DoD separation exam before release, following the responsible offices\' instructions. Ask the MTF what additional exam or acceptance step is required.'],
        verify='VA and the MTF: Was Part A received, who conducts the clinical assessment, and what completes DoD acceptance? Completion evidence: only the particular history, receipt, clinical or acceptance event that actually occurred.', due=None, window=None, basis='rule')

    change('va-records', title='Request records and confirm VA receipt',
        why='Keep personal copies and ask which records VA has received for your filing channel. A request, local possession, sending records and confirmed VA receipt are different actions.',
        how=['For online BDD, VA.gov says VA retrieves service treatment records. Other official channel instructions still request member-provided records. Confirm the instructions for your actual channel.',
             'Request your personal medical and dental copies from the custodian. Keep record requests, collected copies and what you sent separate.',
             'Ask VA or your accredited representative which records VA has received and how to address missing records. A status-screen omission does not by itself prove nonreceipt of mailed records.',
             'Use the standard claim route while records are being obtained. The 190-day reminder is a planning target, not a filing barrier.'],
        verify='VA or an accredited representative: For this filing channel, which STRs must you provide, what has VA received, and how should missing records be addressed? Completion evidence: the specific request, collected record set or confirmed receipt, kept separate.',
        due={'item': 'va-service-end', 'days': -190}, basis='target')

    change('va-exams', title='Confirm your claim exam instructions',
        why='Follow actual VA or contractor notices. An appointment, attendance, report receipt and an agency decision are separate facts. This help applies outside BDD too.',
        how=['Confirm each actual appointment, location, needed accommodations and exam instructions with VA or the contractor.',
             'For BDD only, the 45-day exam-availability condition runs from actual VA claim receipt. It is not a deadline to finish every appointment; the board does not calculate an availability window.',
             'If an appointment conflicts or has been missed, contact VA or the contractor promptly about rescheduling and good cause. Do not skip an agency exam because you have a private DBQ.',
             'Ask VA about VA-caused delays and program exceptions. Record scheduling, attendance or a rescheduling request and report receipt separately.'],
        verify='VA or the exam contractor: Which exams, availability instructions, accommodations or rescheduling steps apply, and has VA received the report? Completion evidence: the particular notice, attended exam, rescheduling request or confirmed report receipt.', due=None, window=None, basis='rule')

    change('va-decision', title='Record what the decision notice says',
        why='Use the actual notice, not an expected decision date. A status reminder, effective date, payment month and deposit are separate facts.',
        how=['Read the actual decision notice privately. Identify its issuing body, notice type, issuance or mailing date and the issues it decides.',
             'Keep deferred or undecided issues unresolved. A decision on one issue is not a decision on the whole claim.',
             'Follow the notice\'s review instructions with VA or an accredited representative. Identify the notice, issue and procedural lane before using a review period; a generic decision date cannot supply every deadline.',
             'If useful, record only the office role, notice type, issue label and relevant event date in optional notes. No document upload or health narrative is required.'],
        verify='VA or an accredited representative: Which issues were decided, what notice date controls and which review instructions apply? Completion evidence: the actual notice and decided issues, with deferred issues retained. No automatic review deadline.', due=None, window=None, basis='rule')

    # R060/R061 retain shared engines and existing SkillBridge minimum rules.
    trp_ids = ['sep-ic', 'sep-ic-appt', 'sep-presep', 'sep-presep-appt', 'sep-trs', 'sep-trs-appt', 'sep-capstone', 'sep-capstone-appt', 'sep-cv', 'sep-cv-appt', 'sep-dd2648']
    for id in trp_ids:
        i = by_id[id]
        i['why'] = 'For Marines required to complete TRP. ' + i['why']
        i['brief'] = i['why']
        i['how'].append('Ask the installation TRP office which phases and exceptions apply, including short-notice, Reserve-demobilization and deployment cases. Phase validity is separate from curriculum exemptions; see the TRP validity inquiry.')
        i['verify'] += ' Completion evidence: the actual phase-specific completion record or confirmed appointment, not a single overall readiness status.'
    change('sep-trs', title='Complete Transition Readiness Seminar workshops')
    change('sep-trs-appt', title='Record your Transition Readiness Seminar appointment')
    for id in ['sep-roob', 'sep-roob-ret']:
        i = by_id[id]
        i['how'].append('Complete current ROOB and VA registration prework required by TRP. Retirement does not create a blanket exemption. Keep accepted prework evidence separate from attendance at counseling.')
    for id in ['ret-request-o', 'ret-request-e']:
        i = by_id[id]
        i['why'] = 'For applicable retirement or FMCR requests, current guidance uses 18 to 6 calendar months before the requested action date, superseding older 14-to-4-month text. The 9-month date is a planning target. A request is not approval.'
        i['brief'] = i['why']
        i['window'] = {'from': {'easMonths': -18}, 'to': {'easMonths': -6}}
        i['how'].append('IPAC and MMSR-2 confirm the applicable window, exceptions and outside-window correspondence. This retirement action does not cover resignation; use the resignation request inquiry.')
    add('va-urgent-review-referral', 'Get help with a final Board decision',
        'For an identified final Board decision, contact qualified court help promptly. The ordinary CAVC appeal period is 120 days; court computation and exceptions require qualified review.',
        ['Use the Court of Appeals for Veterans Claims public filing instructions and qualified court help for an identified final Board decision.',
         'An AOJ decision or an unidentified notice is not a final Board decision. Use VA or accredited help to identify the notice and required response.',
         'Keep the actual notice and court filing event separate. No automatic one-year, 150-day period, extension or election is supplied here.'],
        'Qualified court practitioner or CAVC filing office: Which actual Board notice, filing event, period and exception apply? Completion evidence: actual contact and the specific notice identified, not a link click.', COURT, 90)
    add('va-exception-help', 'Get help with an unclear or urgent notice',
        'Contested, reduction, legacy, late or unidentified matters need qualified VA or accredited help. Filing, care and help stay available while facts are uncertain.',
        ['Ask qualified help to identify the issuing body, actual notice, issue, procedural stage, required response and governing period.',
         'Ask separately about character-of-service review, records assistance or hardship priority processing when relevant. An inquiry does not establish entitlement, a valid election, an extension or an award date.',
         'For an identified final Board decision, use the separate court-help route. An ordinary AOJ notice is not routed directly to court.'],
        'VA or an accredited representative: Which notice, character, records or hardship route applies? Completion evidence: only the specific inquiry or office response that actually occurred.', HELP, 89)

    # R071 removes unsupported canonical shortcuts from new seeds. Migration
    # compares exact historical rows; user-authored or edited rows are preserved.
    claim['benefits']['rows'] = [r for r in claim['benefits']['rows'] if r['what'] not in ['Federal jobs', 'Smaller benefits', 'Protections']]
    claim['benefits']['title'] = 'Confirm benefit requirements'
    claim['benefits']['label'] = 'Each program has its own eligibility and evidence rules'
    claim['benefits']['note'] = 'Sources support the listed topics only. The Muster Out product maintainer owns corrections. Research reviewed 20 OCT 2026; review due 24 OCT 2026. This is not comprehensive VA coverage or confirmation of your eligibility.'

    # G2b: public discovery only. Research predicates never become profile fields.
    data = json.loads((Path(__file__).resolve().parent.parent / 'packs/usmc/va115.json').read_text())
    contact_copy = {
        'c-vso': {'role': 'Accredited representative to choose', 'org': 'Check the VA directory', 'note': 'Verify the individual\'s accreditation and availability. A directory listing is not an appointment. Use VA Form 21-22 if you choose to appoint a VSO.'},
        'c-va': {'note': 'General VA benefits help. Weekdays, 8 a.m. to 9 p.m. Eastern time. Filing and accredited help remain separate choices.'},
        'c-state-vso': {'note': 'Check the individual\'s current accreditation, availability and any actual appointment.'},
        'c-dfas': {'note': 'Confirm retirement category, actual retired pay, SBP and concurrent-receipt limits. A rating threshold alone does not establish full concurrent payment.'}
    }
    for contact in contacts:
        contact.update(contact_copy.get(contact['id'], {}))
    for route in data['routes']:
        if route['requirement'] in ['T3-R018', 'T3-R029']:
            continue
        how = [route['action']] + route['rules'] + [
            'Official route: ' + route['url'],
            'Ask ' + route['office'] + ': ' + route['question'],
            'Completion evidence: ' + route['evidence'],
            'Opening a link is not contact, receipt, eligibility, an election or an award. Record only the action that occurred. No upload or health narrative is required.'
        ]
        for id in route['existing_ids']:
            if id not in by_id:
                continue
            # Current program rules remain textual when event identity cannot
            # be represented. In particular, no release or receipt from doneOn.
            fields = dict(due=None, window=None, when=[])
            if id == 'va-shpe':
                fields.update(due={'item': 'va-service-end', 'months': -6}, basis='target')
            change(id, why=route['rules'][0], how=how,
                   verify=route['office'] + ': ' + route['question'] + ' Completion evidence: ' + route['evidence'], **fields)
        for id in route['proposed_ids']:
            if id not in by_id:
                add(id, route['title'], route['rules'][0], how,
                    route['office'] + ': ' + route['question'] + ' Completion evidence: ' + route['evidence'], route['url'], 100)
                by_id[id]['loe'] = 'fam' if id.startswith('fam-') else 'sep' if id.startswith('trp-') else 'va'

    # R063's resignation inquiry is text-only and does not reuse retirement_date.
    by_id['sep-diary']['due'] = {'easMonths': -7, 'biz': 'prev'}
    by_id['sep-diary']['basis'] = 'target'
    by_id['sep-diary']['when'] = ['resign', 'officer']

    # Seed benefit and office copy is general inquiry, never an entitlement.
    benefit_routes = {'Monthly pay, tax free': 'T3-R058', 'Retired pay and VA pay': 'T3-R054',
                      'Health care': 'T3-R033', 'VA home loan': 'T3-R048',
                      'Education and training (VR&E)': 'T3-R045', 'VA dental: Class IV': 'T3-R035',
                      'Family veterans health coverage': 'T3-R043', 'Reserve drill pay': 'T3-R027'}
    routes = {r['requirement']: r for r in data['routes']}
    for row in claim['benefits']['rows']:
        route = routes.get(benefit_routes.get(row['what']))
        if route:
            row.update(detail=route['rules'][0], verify=route['office'] + ': ' + route['question'])
    claim['vso'] = {
        'rows': [{'name': 'VA accredited representative directory', 'why': 'Check the individual\'s current accreditation and availability. A directory listing is not an appointment.', 'phone': '', 'email': ''}],
        'script': 'I want information about filing a VA disability claim. Are you currently accredited for this role and available to help? How do I confirm an appointment? I can also file directly.',
        'note': 'Choose direct filing or accredited help. VSO help is free. Confirm the individual\'s role, availability and any actual appointment separately. No ranking, wait estimate or partnership is implied.'}
    offices = ['Confirm the separation exam office with your MTF', 'VA or its assigned exam contractor',
               'Confirm with VA health-access staff', 'Ask the clinical service about the referral route',
               'Check the individual in VA\'s accredited directory', 'Ask the Vet Center which route applies',
               'Ask your military clinical service or VA mental-health service']
    for index, row in enumerate(claim['where']['rows']):
        row['where'] = offices[index]
        row['how'] = 'Confirm the actual office, appointment, travel and privacy instructions with VA, the scheduling contractor or your military treatment facility. A link or local task does not book an appointment.'
    claim['where']['note'] = 'Office and travel arrangements depend on the appointment. Ask the responsible office; no universal mileage, reimbursement or confidentiality rule is supplied.'
    claim['exposure']['notes'] = routes['T3-R023']['rules'] + ['Ask VA or an accredited representative which service, location, timing and condition facts apply. Exposure records do not establish a diagnosis, entitlement or a requirement to delay filing.']

    for route in data['routes']:
        if route.get('timing'):
            for id in route['existing_ids'] + route['proposed_ids']:
                if id in by_id:
                    by_id[id]['how'].append('Timing: ' + route['timing'])

    for id, details in {'va-parta': {'timing': 'For BDD or IDES, submit SHA Part A with the claim. Finish all VA and DoD separation-exam phases before release. Outside BDD or under 90 days, ask the MTF for its route.', 'url': 'https://benefits.va.gov/BENEFITS/separation-health-assessment.asp'}, 'va-exams': {'timing': 'Follow actual appointment notices. For BDD, the 45-day exam-availability condition begins with actual VA receipt; it is not a deadline to finish every appointment.', 'url': 'https://www.va.gov/disability/va-claim-exam/'}, 'va-decision': {'timing': 'Use the actual notice, issue and review lane for any response period. There is no universal EAS-based decision deadline. Ask VA or accredited help about any uncertain notice.', 'url': 'https://www.va.gov/decision-reviews/'}}.items():
        by_id[id]['how'].append('Timing: ' + details['timing'])
        by_id[id]['how'].append('Official route: ' + details['url'])

    # Existing quote evidence stays unchanged. Presentation identifies its scope.
    affected = set(trp_ids + ['sep-roob', 'sep-roob-ret', 'ret-request-o', 'ret-request-e',
                             'va-service-end', 'sep-eas', 'ret-day', 'ret-fmcr-day',
                             'va-file', 'va-parta', 'va-records', 'va-exams', 'va-decision'])
    affected.update(id for r in data['routes'] for id in r['existing_ids'])
    for id in affected:
        if id not in by_id:
            continue
        for citation in by_id[id]['cite']:
            citation.update(reviewed='2026-10-20', review_due='2026-10-24',
                            maintenance_owner='Muster Out product maintainer',
                            scope='Bounded source review only; this does not confirm your event or eligibility.')
            if citation['ref'] == 'VA Benefits and Services Participant Guide v6.1':
                citation['version'] = 'Version 6.1, July 2026'
                if id in ['va-net', 'va-net-confirm']:
                    citation['locator'] = 'Module 3, printed page 74 (PDF page 87); replaces the old page 73 reference'
                elif id in ['va-service-end', 'va-file', 'va-parta', 'va-records', 'va-exams', 'va-add', 'va-intent']:
                    citation['locator'] = 'Module 3, printed page 72 (PDF page 85)'
                else:
                    citation['locator'] = 'Original pack locator: ' + citation['para']
                    citation['limitation'] = 'This topic page was not reverified against the July 2026 edition. Confirm current instructions through the official program route.'

    # Reader: Marines and families. Effect: distinguish actual release, a planning target and a conditional rule deadline.
    for id, months, basis in [('va-net', 11, 'target'), ('va-net-confirm', 12, 'rule')]:
        rule = {'actualServiceEnd': True, 'months': months}
        if months == 12:
            rule['roll'] = 'nextWorkday'
        i = by_id[id]
        i.update(due=rule, window=None, basis=basis)
        i['how'] = [step for step in i['how'] if not step.startswith('Timing: ') and not step.startswith('Use the calendar rule')]
        i['how'].append('Record actual release through Copy actual-release record in Claim. The source is va-service-end.eventOn, a valid date on or before today associated with this plan by eventForDate. A planned date, status or doneOn does not establish release.')
        i['how'].append('Planning target: 11 calendar months after actual release. Rule deadline: file by the one-year anniversary, moving forward to the next workday if it falls on a Saturday, Sunday or federal holiday under 38 CFR 3.110(a). A 29 FEB anniversary needs VA or accredited help to confirm the date. VA decides effective-date treatment; filing later remains available.')
        i['cite'].extend([
            {'ref': '38 CFR Part 3 (eCFR, 19 Oct 2026)', 'para': '3.400(b)(2)(i)',
             'quote': 'if claim is received within 1 year after separation from service',
             'url': 'https://www.ecfr.gov/api/versioner/v1/full/2026-10-19/title-38.xml?part=3', 'accessed': '2026-10-21'},
            {'ref': '38 CFR Part 3 (eCFR, 19 Oct 2026)', 'para': '3.110(a)',
             'quote': 'Where the time limit would expire on a Saturday, Sunday, or holiday, the next succeeding workday will be included in the computation.',
             'url': 'https://www.ecfr.gov/api/versioner/v1/full/2026-10-19/title-38.xml?part=3', 'accessed': '2026-10-21'}
        ])
