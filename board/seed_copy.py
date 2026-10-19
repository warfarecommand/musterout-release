"""Plain task copy for Marines leaving active duty and their families.

Reader: Marines and family members. Audience: mil-public.
Effect: one recognizable title and a concrete next step for every item.
Dates, eligibility and source quotations remain in build_seed.py.
"""

COPY = {'sep-tell': {'label': 'Tell your commander your plan',
              'brief': 'Tell your commanding officer how and when you plan to leave active duty so the unit '
                       'can arrange your request and replacement.',
              'how': ['Ask your commanding officer for a time to discuss your plan.',
                      'Bring your planned date, whether you will separate or retire, and whether you want to '
                      'join the Reserves or use SkillBridge.',
                      'Ask who handles your request and who will cover your job while you are away.'],
              'why': 'Your commander handles your request and any SkillBridge endorsement. An early '
                     'conversation helps the unit plan your departure.',
              'verify': 'Confirm with your commanding officer who handles the request and how it should be '
                        'routed.',
              'owner': 'You'},
 'sep-ic': {'label': 'Complete your initial counseling',
            'brief': 'Book the counseling that starts your required transition program. Keep the appointment '
                     'date separate from the rule deadline.',
            'how': ['Call your installation transition office to book initial counseling.',
                    'Ask the Transition Readiness Program (TRP) counselor what to bring and confirm the rule '
                    'deadline from your last active-duty day. The rule requires completion no later than 365 '
                    'days before that day.',
                    'Record the confirmed visit on "Record your initial counseling appointment" and record '
                    'completion on this task. If the date has passed, ask for the earliest available '
                    'appointment.',
                    'Complete initial counseling, pre-separation counseling, transition workshops, Capstone '
                    'review and command verification in that order. Complete all transition requirements '
                    'before SkillBridge participation.'],
            'why': 'Initial counseling starts the required transition program. Retirement counseling may '
                   'begin during the 24 months before retirement; other Marines may begin 18 months before '
                   'separation. Ask the transition office to confirm your dates.',
            'verify': 'Installation Transition Readiness Program (TRP) office, unit transition coordinator '
                      '(UTC) and Installation Personnel Administration Center: confirm end of active '
                      'service, sequencing, completion and any short-notice instructions. SkillBridge '
                      'coordinator and commanding officer (CO): confirm completion before participation.',
            'owner': 'Transition counselor'},
 'sep-ic-appt': {'label': 'Record your initial counseling appointment',
                 'brief': 'Save the date the transition office gives you so you know when to attend.',
                 'how': ['Ask the installation transition office to confirm your initial counseling '
                         'appointment.',
                         'Record the confirmed date here. Leave it undated until the office gives you a '
                         'date.',
                         'Keep the completion rule deadline on "Complete your initial counseling". Mark that '
                         'task done after attending.'],
                 'why': 'An appointment is the date you attend. It is separate from the rule deadline for '
                        'completing counseling.',
                 'verify': 'Installation Transition Readiness Program (TRP) office and unit transition '
                           'coordinator (UTC); commanding officer (CO) for commander verification: confirm '
                           'the appointment and completion record.',
                 'owner': 'Transition counselor'},
 'sep-presep': {'label': 'Complete your separation counseling',
                'brief': 'Book the required pre-separation counseling brief and ask what to bring.',
                'how': ['Call your installation transition office to book pre-separation counseling.',
                        'Confirm the rule deadline from your last active-duty day. Complete this brief no '
                        'later than 365 days before that day; ask for the earliest appointment if the date '
                        'has passed.',
                        'Record the visit on "Record your separation counseling appointment". After '
                        'attending, record completion on this task.',
                        'Complete initial counseling first, then this brief, transition workshops, Capstone '
                        'review and command verification. Finish all transition requirements before '
                        'SkillBridge participation.'],
                'why': 'This required counseling explains your transition benefits and responsibilities. The '
                       'appointment and completion deadline are separate dates.',
                'verify': 'Installation Transition Readiness Program (TRP) office, unit transition '
                          'coordinator (UTC) and Installation Personnel Administration Center: confirm end '
                          'of active service, sequencing, completion and any short-notice instructions. '
                          'SkillBridge coordinator and commanding officer (CO): confirm completion before '
                          'participation.',
                'owner': 'Transition counselor'},
 'sep-presep-appt': {'label': 'Record your separation counseling appointment',
                     'brief': 'Save the confirmed date for your pre-separation counseling brief.',
                     'how': ['Ask the installation transition office to confirm the counseling date.',
                             'Record the confirmed appointment here and ask what to bring.',
                             'Leave this item undated until confirmation. Record actual completion on '
                             '"Complete your separation counseling".'],
                     'why': 'A confirmed appointment tells you when to attend; the completion rule deadline '
                            'does not reserve a place.',
                     'verify': 'Installation Transition Readiness Program (TRP) office and unit transition '
                               'coordinator (UTC); commanding officer (CO) for commander verification: '
                               'confirm the appointment and completion record.',
                     'owner': 'Transition counselor'},
 'sep-trs': {'label': 'Complete your transition workshops',
             'brief': 'Arrange the required workshops with your transition counselor, then keep your '
                      'completion records.',
             'how': ['Ask your installation transition office to enroll you in the required workshops.',
                     'Confirm which Transition Readiness Seminar (TRS) workshops you need and what to bring. '
                     'Complete initial and pre-separation counseling first.',
                     'Record the visit on "Record your transition workshop appointment". Keep completion '
                     'records for Capstone review and command verification.',
                     'Finish the workshops no later than 180 days before your last active-duty day and '
                     'before SkillBridge participation. Confirm your dates with the transition office.'],
             'why': 'The workshops are required before Capstone review and command verification. Ask your '
                    'transition counselor to confirm your required sessions.',
             'verify': 'Installation Transition Readiness Program (TRP) office, unit transition coordinator '
                       '(UTC) and Installation Personnel Administration Center: confirm end of active '
                       'service, sequencing, completion and any short-notice instructions. SkillBridge '
                       'coordinator and commanding officer (CO): confirm completion before participation.',
             'owner': 'You'},
 'sep-trs-appt': {'label': 'Record your transition workshop appointment',
                  'brief': 'Save your confirmed workshop date so you can plan to attend.',
                  'how': ['Ask the installation transition office to confirm your workshop schedule.',
                          'Record the confirmed date here and keep any session details in notes.',
                          'Leave it undated until confirmed; record actual completion on "Complete your '
                          'transition workshops".'],
                  'why': 'A workshop appointment is separate from the rule deadline for completing the '
                         'workshops.',
                  'verify': 'Installation Transition Readiness Program (TRP) office and unit transition '
                            'coordinator (UTC); commanding officer (CO) for commander verification: confirm '
                            'the appointment and completion record.',
                  'owner': 'You'},
 'sep-roob': {'label': 'Finish your transition prework',
              'brief': 'Ask the transition office which online prework to finish before initial counseling.',
              'how': ['Ask your transition counselor how to access the Reserve Obligations and Opportunities '
                      'Brief (ROOB).',
                      'Complete the required prework and ask which certificate to bring to initial '
                      'counseling.',
                      'The board targets completion 7 days before your confirmed counseling appointment. '
                      'Confirm the actual requirement with the transition office.'],
              'why': 'Complete Reserve Obligations and Opportunities Brief (ROOB) as Individualized Initial '
                     'Counseling (IC) prework and confirm the certificate requirement with the installation '
                     'Transition Readiness Program (TRP) office.',
              'verify': 'Installation Transition Readiness Program (TRP) office and unit transition '
                        'coordinator (UTC): confirm Reserve Obligations and Opportunities Brief (ROOB) '
                        'completion and the certificate before the actual Individualized Initial Counseling '
                        '(IC) appointment. The 7-day lead is a planning target.',
              'owner': 'You'},
 'sep-roob-ret': {'label': 'Finish your retirement counseling prework',
                  'brief': 'Ask the transition office which online prework to finish before retirement '
                           'counseling.',
                  'how': ['Ask your transition counselor how to access the Reserve Obligations and '
                          'Opportunities Brief (ROOB) for retirement.',
                          'Complete the prework and confirm which certificate to bring to initial '
                          'counseling.',
                          'The board targets completion 7 days before your confirmed counseling appointment. '
                          'Confirm the actual requirement with the transition office.'],
                  'why': 'Complete Reserve Obligations and Opportunities Brief (ROOB) as Individualized '
                         'Initial Counseling (IC) prework and confirm the certificate requirement with the '
                         'installation Transition Readiness Program (TRP) office.',
                  'verify': 'Installation Transition Readiness Program (TRP) office and unit transition '
                            'coordinator (UTC): confirm Reserve Obligations and Opportunities Brief (ROOB) '
                            'completion and the certificate before the actual Individualized Initial '
                            'Counseling (IC) appointment. The 7-day lead is a planning target.',
                  'owner': 'You'},
 'sep-dd2648': {'label': 'Check your separation type and grade',
                'brief': 'Review your transition checklist with your counselor so it reflects your actual '
                         'path and grade.',
                'how': ['Ask your transition counselor to review your DD Form 2648 checklist with you.',
                        'Check the separation type, grade and any Reserve affiliation entry. Ask the '
                        'counselor to correct an error.',
                        'If you plan Reserve affiliation, ask the career counselor to recheck Direct '
                        'Affiliation Program eligibility. Retiring Marines are not eligible for that '
                        'program.'],
                'why': 'Confirm that the DD 2648 reflects your actual separation path and current grade. '
                       'Actual retirement, including medical retirement, makes a Marine ineligible for '
                       'Direct Affiliation Program. An erroneous entry needs correction and eligibility '
                       'review.',
                'verify': 'Installation Transition Readiness Program (TRP) counselor, Installation Personnel '
                          'Administration Center and Career Counselor: confirm correction procedure, actual '
                          'separation status and the Direct Affiliation Program eligibility record.',
                'owner': 'You'},
 'sep-capstone': {'label': 'Complete your final transition review',
                  'brief': 'Book Capstone, the final transition review, after your workshops and before '
                           'command verification.',
                  'how': ['Call your installation transition office to book the Capstone review.',
                          'Finish initial counseling, pre-separation counseling and transition workshops '
                          'first. Ask the counselor which completion records and documents to bring to the '
                          'final review.',
                          'Record the visit on "Record your final review appointment". Complete the review '
                          'no later than 120 days before your last active-duty day.',
                          'Complete command verification afterward and all transition requirements before '
                          'SkillBridge participation.'],
                  'why': 'Capstone checks your transition readiness before command verification. Your '
                         'counselor confirms what remains to complete.',
                  'verify': 'Installation Transition Readiness Program (TRP) office, unit transition '
                            'coordinator (UTC) and Installation Personnel Administration Center: confirm end '
                            'of active service, sequencing, completion and any short-notice instructions. '
                            'SkillBridge coordinator and commanding officer (CO): confirm completion before '
                            'participation.',
                  'owner': 'Transition counselor'},
 'sep-capstone-appt': {'label': 'Record your final review appointment',
                       'brief': 'Save the confirmed Capstone appointment, your final transition review.',
                       'how': ['Ask the installation transition office to confirm your Capstone review '
                               'appointment.',
                               'Record the confirmed date here and ask which records to bring.',
                               'Leave this item undated until confirmed; record completion on "Complete your '
                               'final transition review".'],
                       'why': 'The appointment tells you when to attend the final review. It does not '
                              'replace the completion deadline.',
                       'verify': 'Installation Transition Readiness Program (TRP) office and unit transition '
                                 'coordinator (UTC); commanding officer (CO) for commander verification: '
                                 'confirm the appointment and completion record.',
                       'owner': 'Transition counselor'},
 'sep-cv': {'label': 'Get your command verification',
            'brief': 'Arrange the command review that closes your required transition sequence.',
            'how': ['Ask your unit transition coordinator to arrange command verification.',
                    'Complete initial counseling, pre-separation counseling, workshops and Capstone review '
                    'first. Bring the records the coordinator requests.',
                    'Confirm command verification on DD Form 2648 no later than 90 days before your last '
                    'active-duty day and before SkillBridge participation.',
                    'Record the appointment separately on "Record your command verification appointment" and '
                    'completion here.'],
            'why': 'Command verification closes the required transition sequence. Ask the transition office '
                   'and your unit coordinator to confirm completion.',
            'verify': 'Installation Transition Readiness Program (TRP) office, unit transition coordinator '
                      '(UTC) and Installation Personnel Administration Center: confirm end of active '
                      'service, sequencing, completion and any short-notice instructions. SkillBridge '
                      'coordinator and commanding officer (CO): confirm completion before participation.',
            'owner': 'Commanding officer'},
 'sep-cv-appt': {'label': 'Record your command verification appointment',
                 'brief': 'Save the confirmed time for your command transition review.',
                 'how': ['Ask your unit transition coordinator to confirm the command verification '
                         'appointment.',
                         'Record the confirmed date here and ask what to bring.',
                         'Keep it undated until confirmed; record actual completion on "Get your command '
                         'verification".'],
                 'why': 'An appointment gives you a visit date to plan around. It is separate from the '
                        'completion rule deadline.',
                 'verify': 'Installation Transition Readiness Program (TRP) office and unit transition '
                           'coordinator (UTC); commanding officer (CO) for commander verification: confirm '
                           'the appointment and completion record.',
                 'owner': 'Commanding officer'},
 'sep-ptad': {'label': 'Plan your house and job hunting',
              'brief': 'Ask your personnel office whether you qualify for transition permissive temporary '
                       'additional duty, time for house and job hunting.',
              'how': ['Ask your installation personnel office to check your eligibility for transition '
                      'permissive temporary additional duty (PTAD).',
                      'Confirm command approval, allowed days, travel arrangements and where this time falls '
                      'before leave.',
                      'If you also use SkillBridge, have the coordinator check the full absence calendar '
                      'before you rely on the dates.'],
              'why': 'An approved retirement date qualifies you. continental United States (CONUS) commands '
                     'can approve up to 20 days, in increments if the approving authority allows, and '
                     'permissive temporary additional duty (PTAD) runs before any leave.',
              'verify': 'Confirm with your Installation Personnel Administration Center (IPAC) and approving '
                        'command: eligibility, authorized days, travel arrangements and the full absence '
                        'sequence before leave.',
              'owner': 'You'},
 'sep-dd214': {'label': 'Review your service discharge record',
               'brief': 'Check your discharge worksheet with the personnel office before signing it.',
               'how': ['Ask your installation personnel office for your DD Form 214 worksheet.',
                       'Review service, awards, separation details and the dental treatment entry. Ask the '
                       'office to correct errors before you sign.',
                       'Keep a complete copy of the final record for benefits and employment.'],
               'why': 'Installation Personnel Administration Center must identify the form edition and '
                      'review the worksheet with you before the agreed separation processing event. The '
                      'dental entry is one part of the Department of Veterans Affairs (VA) dental '
                      'eligibility check.',
               'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                         'retirement desk (MMSR-2): confirm the form edition, worksheet entries and review '
                         'target before the elected processing or departure event. Department of Veterans '
                         'Affairs (VA) dental confirms eligibility.',
               'owner': 'You'},
 'sep-checkout': {'label': 'Confirm your final checkout day',
                  'brief': 'Confirm when the personnel office expects you to finish checkout and which '
                           'requirements must be complete.',
                  'how': ['Ask your installation personnel office to confirm your final checkout day.',
                          'Review the unit checklist against your SkillBridge, leave and return plans.',
                          'Confirm that separation requirements are complete before terminal leave. Keep '
                          'checkout separate from your last active-duty day.'],
                  'why': 'Installation Personnel Administration Center confirms whether you complete '
                         'separation processing before permanent departure or return after SkillBridge. '
                         'Complete all terminal-leave separation requirements before leave begins.',
                  'verify': 'Installation Personnel Administration Center and approving command: enter the '
                            'agreed checkout target before terminal leave and confirm the elected processing '
                            'option with its actual departure or return date.',
                  'owner': 'Personnel office'},
 'sep-eas': {'label': 'Confirm your service end date',
             'brief': 'Check your approved end of active service date with the personnel office.',
             'how': ['Ask your installation personnel office to confirm your end of active service date.',
                     'Compare the approved date with your orders and board profile. Ask the office about any '
                     'difference.',
                     'Keep checkout and departure dates separate; leaving the unit earlier does not by '
                     'itself end active duty.'],
             'why': 'Keep end of active service separate from an earlier permanent departure or checkout. '
                    'Confirm the approved service-end date and processing option with Installation Personnel '
                    'Administration Center.',
             'verify': 'Installation Personnel Administration Center: confirm end of active service, '
                       'separation authority and the processing or departure date.',
             'owner': 'You'},
 'ret-day': {'label': 'Confirm your retirement effective date',
             'brief': 'Check the approved retirement action date separately from your last active-duty day.',
             'how': ['Ask your installation personnel office to confirm your approved retirement action and '
                     'effective date.',
                     'Confirm whether the action is retirement or transfer to the Fleet Marine Corps Reserve '
                     '(FMCR). Record your last active-duty day on its separate item.',
                     'Ask retired pay support to confirm when your first payment is expected.'],
             'why': 'The manual sets ordinary retirement on the 1st day of the month, except disability and '
                    'Reserve retirement with pay at age 60, and sets Fleet Marine Corps Reserve (FMCR) '
                    'transfer on the last day of the month. Installation Personnel Administration Center '
                    '(IPAC) and Marine Corps separation and retirement desk (MMSR-2) must confirm your '
                    'approved action and effective date. Defense Finance and Accounting Service (DFAS) must '
                    'confirm entitlement and the first payment. The last active-duty day is a separate date '
                    'for Benefits Delivery at Discharge (BDD). For ordinary retirement it precedes the '
                    'effective Retired List date by 1 day; IPAC and MMSR-2 must confirm exception and FMCR '
                    'dates individually.',
             'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                       'retirement desk (MMSR-2): confirm Retired List versus Fleet Marine Corps Reserve '
                       '(FMCR) and its effective date. Defense Finance and Accounting Service (DFAS) retired '
                       'pay: confirm entitlement and first payment.',
             'owner': 'You'},
 'ret-fmcr-day': {'label': 'Confirm your Fleet Reserve transfer date',
                  'brief': 'Confirm whether your enlisted retirement action is a transfer to the Fleet '
                           'Marine Corps Reserve and which date applies.',
                  'how': ['Ask your installation personnel office whether your action is a Fleet Marine '
                          'Corps Reserve (FMCR) transfer.',
                          'Confirm the approved transfer date and last active-duty day with the enlisted '
                          'retirement desk.',
                          'Keep the action date in your profile and record your last active-duty day '
                          'separately for your benefits claim.'],
                  'why': 'If your approved action is Fleet Marine Corps Reserve (FMCR) transfer, the manual '
                         'sets its effective date on the last day of the month. Installation Personnel '
                         'Administration Center must enter the approved transfer date; the board cannot '
                         'derive this action from the retirement profile alone.',
                  'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                            'retirement desk (MMSR-2): confirm whether this action applies, enter the '
                            'approved last-day-of-month date and mark this item not applicable for a Retired '
                            'List action.',
                  'owner': 'You'},
 'sep-counsel': {'label': 'Discuss your resignation with your commander',
                 'brief': 'Meet with your commander to record your Reserve choice before your resignation '
                          'request is submitted.',
                 'how': ['Ask your commanding officer for resignation counseling.',
                         'Explain whether you want a Reserve commission and confirm the required '
                         'service-record entry.',
                         'Ask your personnel office and the officer separation desk to confirm routing and '
                         'the applicable submission window.'],
                 'why': 'The commanding officer (CO) counsels you and records your Reserve commission choice '
                        'before submission. Marine administrative message (MARADMIN) 175/24 prints a '
                        '6-to-18-month submission window, while the manual diary window is 4 to 14 months. '
                        'The 7-month date is a planning target. Reserve appointment approval requires at '
                        'least 4 months from Headquarters Marine Corps (HQMC) receipt of that request, after '
                        'resignation approval and end of active service entry permit Reserve Affairs (RA) '
                        'submission.',
                 'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                           'retirement desk (MMSR-2): confirm routing, submission date, the governing window '
                           'and 120 days plus desired leave/permissive temporary additional duty (PTAD) '
                           'before the requested action date.',
                 'owner': 'Commanding officer'},
 'sep-diary': {'label': 'Confirm your resignation request was entered',
               'brief': 'Ask your personnel office to confirm it entered your requested resignation date and '
                        'Reserve choice.',
               'how': ['Ask your installation personnel office to confirm your resignation request was '
                       'submitted.',
                       'Check the requested date and Reserve choice in the unit diary, the personnel system '
                       'submission record.',
                       'Ask the officer separation desk to confirm acceptance and the applicable submission '
                       'window. Keep submission separate from approval.'],
               'why': 'The unit diary reports your requested resignation date and Reserve commission choice. '
                      'The Marine administrative message (MARADMIN) prints a 6-to-18-month window, while '
                      'manual 5003.2 prints a 4-to-14-month window and diary rejection outside it. '
                      'Installation Personnel Administration Center and Marine Corps separation and '
                      'retirement desk (MMSR-2) must confirm acceptance and submission timing.',
               'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                         'retirement desk (MMSR-2): confirm routing, submission date, the governing window '
                         'and 120 days plus desired leave/permissive temporary additional duty (PTAD) before '
                         'the requested action date.',
               'owner': 'Personnel office'},
 'sep-letter': {'label': 'Check whether resignation needs a letter',
                'brief': 'Ask your personnel office whether your resignation needs a waiver letter or '
                         'command endorsement.',
                'how': ['Ask your installation personnel office whether your case requires the Figure 5-1 '
                        'resignation letter.',
                        'Confirm whether a waiver or unfavorable Reserve recommendation makes the letter '
                        'necessary.',
                        'If required, prepare the letter with command endorsements and confirm its route and '
                        'submission date with the officer separation desk.'],
                'why': 'Required only for a waiver or when the commanding officer (CO) will not recommend a '
                       "Reserve commission. Even when optional it puts the CO's recommendation on paper for "
                       'Reserve Affairs.',
                'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                          'retirement desk (MMSR-2): confirm whether the Figure 5-1 letter and command '
                          'endorsement are required and the routing date.',
                'owner': 'You'},
 'sep-pcs': {'label': 'Check orders affecting your resignation',
             'brief': 'Contact your assignments monitor immediately if new orders could affect your '
                      'resignation.',
             'how': ['Ask your assignments monitor and the officer separation desk whether your orders allow '
                     'a cancellation request.',
                     'Record when you received the permanent change of station (PCS) orders, when you were '
                     'notified, and your estimated arrival date.',
                     'Have the office calculate both submission deadlines and any short-notice exception. '
                     'Route the written request with command endorsements.'],
             'why': 'The general rule bars recommendation when permanent change of station (PCS) orders were '
                    'issued or notified before the request. The manual permits a cancellation request for an '
                    'otherwise eligible officer under 5002.3.a(1)-(4). The requested effective date must be '
                    'no later than the last day of the arrival month. Submission is at least 120 days before '
                    'estimated arrival and no later than 10 working days after receipt. Paragraph (4) '
                    'addresses notification less than 120 days before arrival.',
             'verify': 'Officer assignments monitor and Marine Corps separation and retirement desk '
                       '(MMSR-2): confirm eligibility, the paragraph (4) short-notice rule, both submission '
                       'deadlines and endorsements.',
             'owner': 'You'},
 'sep-approval': {'label': 'Confirm resignation approval and service end',
                  'brief': 'Verify your resignation approval and service end date. A Reserve commission has '
                           'a separate receipt and approval process.',
                  'how': ['Ask your installation personnel office to confirm resignation approval and your '
                          'end of active service date.',
                          'Check approval in the electronic diary feedback report (EDFR) and the date in '
                          'Marine Online (MOL).',
                          '[Reserve only] Ask the Reserve officer appointments desk (RAM-1) to confirm '
                          'headquarters receipt and the separate appointment decision.'],
                  'why': 'Confirm resignation approval and the end of active service shown in Marine Corps '
                         'Total Force System (MCTFS) with Installation Personnel Administration Center. If '
                         'you choose a Reserve commission, its receipt and approval are separate steps.',
                  'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                            'retirement desk (MMSR-2): confirm resignation approval and the populated end of '
                            'active service. If you choose a Reserve commission, ask Reserve officer '
                            'appointments desk (RAM-1) to confirm its separate receipt and processing.',
                  'owner': 'Marine Corps separation and retirement desk (MMSR-2)'},
 'sep-orders': {'label': 'Get your separation orders',
                'brief': 'Your personnel office issues separation orders after approval. Check when yours '
                         'will be ready.',
                'how': ['Ask your installation personnel office for the status of your separation orders.',
                        'Check the approved date and separation details when the orders arrive.',
                        'Keep a copy and confirm your final checkout schedule with the office.'],
                'why': 'The unit issues orders once approval posts.',
                'verify': 'Confirm with your installation personnel office when separation orders can be '
                          'issued after approval.',
                'owner': 'Personnel office'},
 'sep-modify': {'label': 'Confirm your resignation change cutoff',
                'brief': 'Have the separation desk calculate your change cutoff from both your resignation '
                         'and separation-leave dates.',
                'how': ['Contact your installation personnel office if you need to change or withdraw your '
                        'resignation.',
                        'Confirm the actual resignation date and start of separation leave. Ask the officer '
                        'separation desk to calculate the earlier boundary.',
                        'Keep the conservative planning target 46 calendar days before the earlier anchor, '
                        'moved earlier for a weekend, unless the office confirms a different date.'],
                'why': 'The manual ties a change request to before 45 days from the resignation date or '
                       'commencement of separation leave. Installation Personnel Administration Center and '
                       'Marine Corps separation and retirement desk (MMSR-2) must confirm both actual '
                       'anchors. Use a conservative target 46 calendar days before the earlier anchor and '
                       'move a weekend back. The entered resignation date gives a projection; earlier '
                       'separation leave requires an earlier target.',
                'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                          'retirement desk (MMSR-2): confirm the effective resignation date and actual '
                          'separation-leave start, calculate the earlier boundary and enter the conservative '
                          'target date.',
                'owner': 'You'},
 'ret-eligibility-e': {'label': 'Check your enlisted retirement eligibility',
                       'brief': 'Have the personnel office check retirement eligibility against your actual '
                                'service record.',
                       'how': ['Ask your installation personnel office to review your creditable active '
                               'service and retirement eligibility.',
                               'Confirm your Armed Forces Active Duty Base Date (AFADBD), prior service, '
                               'lost time, enlistment and remaining obligations.',
                               'For 20 to 29 years of active service, ask about transfer to the Fleet Marine '
                               'Corps Reserve (FMCR); at 30 or more, ask about direct retirement. Confirm '
                               'the applicable age rule and any Reserve-service exception with the enlisted '
                               'retirement desk.',
                               'Keep the requested or approved action date in your profile and your last '
                               'active-duty day on its separate item.'],
                       'why': 'Transfer to the Fleet Marine Corps Reserve (FMCR) requires at least 20 years '
                              'of active duty; direct retirement requires at least 30. Both require '
                              'eligibility review. Ask the personnel office to check creditable service, '
                              'obligations and your enlistment. Confirm the applicable age rule and any '
                              'Reserve-service exception with the enlisted retirement desk.',
                       'verify': 'Installation Personnel Administration Center and Marine Corps separation '
                                 'and retirement desk (MMSR-2): verify creditable active service, '
                                 'obligations, contract, age rule and Fleet Marine Corps Reserve (FMCR) '
                                 'versus Retired List eligibility.',
                       'owner': 'You'},
 'ret-limits-e15': {'label': 'Check whether retirement is available',
                    'brief': 'Ask the personnel office to review your service limit, prior service and any '
                             'approved exception.',
                    'how': ['Ask your installation personnel office and career planner to check your actual '
                            'grade and creditable service.',
                            'Confirm any approved exception with the enlisted assignments and retirement '
                            'offices before relying on a retirement plan.',
                            'If you are a Reserve Marine retiring on active service, ask which service-limit '
                            'and age guidance governs your record.'],
                    'why': 'For active-component Marines, Marine administrative message (MARADMIN) 326/23 '
                           'lists Corporal at 8 years and Sergeant at 12 years of active Marine Corps '
                           'service. Those limits do not establish 20 years of creditable active military '
                           'service. Ask the personnel office about prior service or an approved exception. '
                           'Reserve Marines retiring on active service need their governing service-limit '
                           'and age rules confirmed separately.',
                    'verify': 'Installation Personnel Administration Center, unit career planner, Manpower '
                              'Management Enlisted Assignments (MMEA) and Marine Corps separation and '
                              'retirement desk (MMSR-2): confirm actual grade, service limit, creditable '
                              'active service and any approved exception before relying on retirement '
                              'eligibility.',
                    'owner': 'You'},
 'ret-limits-e67': {'label': 'Check your grade service limit',
                    'brief': 'Have the personnel office check your actual grade, obligations and any '
                             'approval to continue serving.',
                    'how': ['Ask your installation personnel office and career planner to check your grade '
                            'service limit.',
                            'Check creditable active service and remaining obligations. Ask whether any '
                            'continuation or exception was approved.',
                            'Ask the enlisted retirement desk which rule applies if you are a Reserve Marine '
                            'retiring on active service.'],
                    'why': 'For active-component Marines, Marine administrative message (MARADMIN) 326/23 '
                           'lists Staff Sergeant at 20 years and Gunnery Sergeant at 22 years of active '
                           'military service. Confirm your actual grade, obligations and any '
                           'continued-service approval. Reserve Marines retiring on active service need '
                           'their governing service-limit and age rules confirmed separately.',
                    'verify': 'Installation Personnel Administration Center, unit career planner, Manpower '
                              'Management Enlisted Assignments (MMEA) and Marine Corps separation and '
                              'retirement desk (MMSR-2): confirm actual grade, service limit, creditable '
                              'active service and any approved exception before relying on retirement '
                              'eligibility.',
                    'owner': 'You'},
 'ret-limits-e89': {'label': 'Confirm your allowed service length',
                    'brief': 'Confirm the limit for your actual grade; the board grade group does not '
                             'establish continued-service approval.',
                    'how': ['Ask your installation personnel office and career planner to confirm the limit '
                            'for your actual grade.',
                            'Review your service record and any approved continuation; do not assume an '
                            'exception.',
                            'Ask the enlisted retirement desk which service-limit and age rules apply to any '
                            'Reserve-service case.'],
                    'why': 'For active-component Marines, Marine administrative message (MARADMIN) 326/23 '
                           'lists First Sergeant and Master Sergeant at 27 years and Sergeant Major and '
                           'Master Gunnery Sergeant at 30 years of active military service. Being an E-8 '
                           'does not authorize service to 30 years. Confirm any continuation; Reserve '
                           'Marines retiring on active service need their governing service-limit and age '
                           'rules confirmed separately.',
                    'verify': 'Installation Personnel Administration Center, unit career planner, Manpower '
                              'Management Enlisted Assignments (MMEA) and Marine Corps separation and '
                              'retirement desk (MMSR-2): confirm actual grade, service limit, creditable '
                              'active service and any approved exception before relying on retirement '
                              'eligibility.',
                    'owner': 'You'},
 'ret-obligations-e': {'label': 'Check your remaining service obligations',
                       'brief': 'Review grade, tour, deployment and education obligations before choosing '
                                'your retirement date.',
                       'how': ['Ask your installation personnel office and career planner to review your '
                               'remaining service obligations.',
                               'Check your date of rank, time in grade, orders, course attendance and '
                               'deployment schedule.',
                               'Ask the enlisted retirement desk to confirm any earlier submission deadline, '
                               'overseas-tour rule or waiver. Get any required approval before relying on '
                               'the date.'],
                       'why': 'Review eligibility before the unit submits your request. Gunnery Sergeant and '
                              'above normally require 2 years in grade for Fleet Marine Corps Reserve (FMCR) '
                              'transfer. Tour, deployment and education obligations can affect the date. The '
                              'grade group cannot distinguish Staff Sergeant from Gunnery Sergeant.',
                       'verify': 'Installation Personnel Administration Center, career planner, commanding '
                                 'officer (CO) and Marine Corps separation and retirement desk (MMSR-2): '
                                 'confirm tour, deployment, education and grade obligations, any earlier '
                                 'submission deadline and required waiver; Deputy Commandant for Manpower '
                                 'and Reserve Affairs (DC M&RA) decides minimum time-in-grade waivers.',
                       'owner': 'You'},
 'ret-counsel-e': {'label': 'Complete retirement counseling with your commander',
                   'brief': 'Review and sign the retirement checklist with your commander before submission.',
                   'how': ['Ask your commanding officer to schedule retirement counseling and review '
                           'Appendix J.',
                           'Review the checklist, including recall, mobilization, assignments, leave and '
                           'retirement consequences. You and the commander sign before submission.',
                           'Confirm the command files the signed checklist in your service record. If '
                           'disability processing applies, contact your disability case liaison and '
                           'retirement desk before proceeding.'],
                   'why': 'You and the commanding officer (CO) sign the retirement preapplication checklist '
                          'before the request is submitted. The CO counsels you on recall and mobilization. '
                          'The board targets 7 days before submission; the required sequence is counseling '
                          'before submission.',
                   'verify': 'commanding officer (CO), Installation Personnel Administration Center and '
                             'Marine Corps separation and retirement desk (MMSR-2): confirm counseling, both '
                             'Appendix J signatures and service-record filing before submission; Physical '
                             'Evaluation Board Liaison Officer (PEBLO) confirms any disability processing.',
                   'owner': 'Commanding officer'},
 'ret-waiver-e': {'label': 'Confirm any required retirement waiver',
                  'brief': 'Find out whether you need a waiver before the unit submits your request.',
                  'how': ['Ask your installation personnel office and enlisted retirement desk whether your '
                          'request needs a waiver.',
                          'If needed, confirm the form, justification, command endorsements, submission date '
                          'and deciding authority.',
                          'A request outside the current 6-to-18-month window needs separate correspondence. '
                          'Ask about the Administrative Action (AA) Form and required endorsement. Mark this '
                          'task not applicable if no waiver is needed.'],
                  'why': 'A request needing a waiver goes to Marine Corps separation and retirement desk '
                         '(MMSR-2) through the chain of command by separate correspondence. A diary entry '
                         'does not request an eligibility waiver. A request outside the current '
                         '6-to-18-month window requires an AA Form, justification and commanding officer '
                         '(CO) endorsement.',
                  'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                            'retirement desk (MMSR-2): determine whether a waiver applies and confirm the '
                            'package, submission date and deciding authority.',
                  'owner': 'You'},
 'ret-request-o': {'label': 'Submit your officer retirement request',
                   'brief': 'Have the personnel office confirm your submission window, then submit the '
                            'signed retirement checklist and requested date.',
                   'how': ['Ask your installation personnel office and officer retirement desk to confirm '
                           'the submission window and route.',
                           'Sign Appendix J for your service record. Give the unit your requested date, '
                           'leave and permissive temporary additional duty (PTAD) dates, duration and '
                           'planned departure.',
                           'Confirm unit diary submission, the electronic personnel transaction. Have the '
                           'office check 120 days plus desired leave and authorized absence before your '
                           'requested date.',
                           'Confirm any waiver or outside-window request by separate correspondence. The '
                           'board uses a 9-month planning target; submission is not approval.'],
                   'why': 'Marine administrative message (MARADMIN) 175/24 gives a 6-to-18-month request '
                          'window; the older order prints 4 to 14 months. Confirm the governing window with '
                          'the retirement desk. Your board uses a 9-month planning target inside both. '
                          'Headquarters decides approval and may set a different date; confirm approval '
                          'before making major personal commitments.',
                   'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                             'retirement desk (MMSR-2): confirm routing, submission date, the governing '
                             'window and 120 days plus desired leave/permissive temporary additional duty '
                             '(PTAD) before the requested action date.',
                   'owner': 'You'},
 'ret-request-e': {'label': 'Submit your enlisted retirement request',
                   'brief': 'Have the personnel office confirm the route and window for your retirement or '
                            'Fleet Reserve transfer request.',
                   'how': ['Ask your installation personnel office and enlisted retirement desk to confirm '
                           'the submission window and route.',
                           'After eligibility review and commander counseling, give the reporting unit your '
                           'signed Appendix J and requested retirement or Fleet Marine Corps Reserve (FMCR) '
                           'action date.',
                           'Include desired leave, permissive temporary additional duty (PTAD), duration and '
                           'planned departure. Ask the office to check 120 days plus desired absence and any '
                           'earlier deployment deadline.',
                           'Confirm the reporting unit submits through the Marine Corps Total Force System '
                           '(MCTFS) unit diary to the retirement desk (MMSR-2). Ask about any outside-window '
                           'waiver. Use the 9-month date as a planning target and keep checking for actual '
                           'approval.'],
                   'why': 'Current enlisted retirement desk guidance uses a 6-to-18-month request window for '
                          'retirement and Fleet Marine Corps Reserve (FMCR) transfer; the older manual '
                          'prints 4 to 14 months. Confirm the governing window with the desk. The board uses '
                          'a 9-month planning target inside both. Submission is not approval; confirm the '
                          'approved date before making major personal commitments.',
                   'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                             'retirement desk (MMSR-2): confirm routing, submission date, the governing '
                             'window and 120 days plus desired leave/permissive temporary additional duty '
                             '(PTAD) before the requested action date.',
                   'owner': 'Reporting unit / Installation Personnel Administration Center'},
 'ret-receipt-e': {'label': 'Confirm your retirement request was received',
                   'brief': 'Check unit acceptance and headquarters receipt. Keep approval as a separate '
                            'step until the decision posts.',
                   'how': ['Ask your installation personnel office whether the unit diary accepted your '
                           'request.',
                           'Ask the enlisted retirement desk to confirm its separate acknowledgment and '
                           'requested date.',
                           'Record submission and headquarters receipt separately in notes. Keep the '
                           'approval task waiting until the approved decision posts; the 7-day check is a '
                           'planning target.'],
                   'why': 'Unit diary acceptance and headquarters receipt are separate checks. Neither is '
                          'retirement approval. Ask your personnel office and the retirement desk to confirm '
                          'both stages and the requested date. The board targets a check 7 days after '
                          'submission; no source promises receipt within 7 days.',
                   'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                             'retirement desk (MMSR-2): confirm diary acceptance, requested date and '
                             'separate Headquarters Marine Corps (HQMC) acknowledgment; neither is '
                             'retirement approval.',
                   'owner': 'Personnel office'},
 'ret-pcs-e': {'label': 'Check orders affecting your Fleet transfer',
               'brief': 'Contact the personnel office immediately if your Fleet Reserve request requires '
                        'canceling assignment orders.',
               'how': ['On receipt of assignment orders, contact your installation personnel office and '
                       'assignments monitor.',
                       'If canceling permanent change of station (PCS) orders for Fleet Marine Corps Reserve '
                       '(FMCR) transfer, have the office count the 10-working-day submission deadline.',
                       'Confirm the requested transfer date and cancellation criteria with the enlisted '
                       'retirement desk. Record the confirmed deadline and keep this task open until '
                       'submission; mark it not applicable if no cancellation is involved.'],
               'why': 'If your Fleet Marine Corps Reserve (FMCR) request involves canceling permanent change '
                      'of station (PCS) orders, send it to Marine Corps separation and retirement desk '
                      '(MMSR-2) with Manpower Management Enlisted Assignments (MMEA) or RAM as an '
                      'information addressee within 10 working days after receipt. MMEA is not the '
                      'retirement request destination. MMSR-2 must confirm the requested FMCR date against '
                      'the PCS criteria.',
               'verify': 'Confirm with your personnel office, assignments monitor and enlisted retirement '
                         'desk: orders receipt, the 10-working-day deadline and Fleet Reserve transfer date. '
                         'Include enlisted assignments or Reserve Affairs for information as directed by the '
                         'retirement desk.',
               'owner': 'You'},
 'ret-report-e': {'label': 'Report changes after your retirement request',
                  'brief': 'Tell your command promptly about changes that could affect your retirement '
                           'request, including after approval.',
                  'how': ['Tell your installation personnel office and command promptly if your status '
                          'changes after submission.',
                          'Report medical, assignment, promotion, disciplinary or lost-time changes so the '
                          'command can obtain retirement desk instructions.',
                          'If referred for disability evaluation, contact your disability case liaison. '
                          'Confirm release instructions before relying on an earlier approval.'],
                  'why': 'Your command must immediately report changes that can affect retirement, including '
                         'medical disqualification, reassignment, promotion, disciplinary action or lost '
                         'time. This duty continues after approval. The board uses setup day as a planning '
                         'reminder; ask your command what must be reported.',
                  'verify': 'commanding officer (CO), Installation Personnel Administration Center and '
                            'Marine Corps separation and retirement desk (MMSR-2): confirm required '
                            'notifications and release instructions; Marine Corps promotion office (MMPR-2) '
                            'handles promotion notice and Physical Evaluation Board Liaison Officer (PEBLO) '
                            'handles disability processing.',
                  'owner': 'commanding officer (CO) / Installation Personnel Administration Center'},
 'ret-modify-e': {'label': 'Confirm your retirement change cutoff',
                  'brief': 'Ask the retirement desk about changing or canceling your request before the '
                           '45-day rule deadline.',
                  'how': ['Contact your installation personnel office and enlisted retirement desk if you '
                          'need a change.',
                          'Confirm the effective date and submit justification and endorsements by separate '
                          'correspondence no later than 45 days before it.',
                          'Ask about the cancellation service obligation and approval criteria before '
                          'submitting. Mark this task not applicable if no change is needed.',
                          'Before canceling, confirm the required unconditional agreement to serve at least '
                          '2 years from approval and the limits on requesting Fleet Reserve transfer during '
                          'that period. Ask about hardship or approaching service-limit exceptions; '
                          'cancellation does not authorize service beyond your limit.'],
                  'why': 'A request to modify or cancel enlisted retirement or Fleet Marine Corps Reserve '
                         '(FMCR) transfer requires justification and endorsements by separate correspondence '
                         'to Marine Corps separation and retirement desk (MMSR-2) no later than 45 days '
                         'before the effective date. Unit diary cannot submit it. MMSR-2 must confirm '
                         'whether your reason meets the approval criteria.',
                  'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                            'retirement desk (MMSR-2): confirm applicability, effective date, the 45-day '
                            'deadline, endorsements and cancellation obligation; Board for Correction of '
                            'Naval Records (BCNR) handles changes after transfer.',
                  'owner': 'You'},
 'ret-pcs': {'label': 'Check orders affecting your officer retirement',
             'brief': 'Contact your assignments monitor immediately if retirement requires canceling '
                      'assignment orders.',
             'how': ['Tell your assignments monitor and installation personnel office when you receive '
                     'permanent change of station (PCS) orders.',
                     'Have them count the 10-working-day retirement-request deadline using the office '
                     'calendar.',
                     'Confirm routing to the officer retirement desk and the required information addressee. '
                     'Record the office-confirmed deadline and keep the task open until submission.'],
             'why': 'A retirement request involving permanent change of station (PCS) cancellation must be '
                    'submitted no later than 10 working days after receipt of orders to Marine Corps '
                    'separation and retirement desk (MMSR-2), with Manpower Management Officer Assignments '
                    '(MMOA) as an information addressee. The deadline is unresolved until receipt and the '
                    'office working-day calendar are confirmed.',
             'verify': 'Officer assignments monitor, Installation Personnel Administration Center, Marine '
                       'Corps separation and retirement desk (MMSR-2) and Manpower Management Officer '
                       'Assignments (MMOA): confirm orders receipt, the 10-working-day deadline, submission '
                       'route and information addressee.',
             'owner': 'You'},
 'ret-approval': {'label': 'Confirm retirement approval and your date',
                  'brief': 'Get confirmation of the approved action and date before relying on permission to '
                           'leave active duty.',
                  'how': ['Ask your installation personnel office for the retirement decision and approved '
                          'action date.',
                          'Confirm whether the decision is retirement or Fleet Marine Corps Reserve (FMCR) '
                          'transfer. A request or pending flag is not approval.',
                          'Record your last active-duty day separately and recheck leave and benefits dates '
                          'if approval differs from your request.'],
                  'why': 'Confirm the approved action and date before relying on authority to leave active '
                         'duty. For enlisted requests, the retirement desk posts the approval in the '
                         'personnel transaction feedback report. A request or pending flag is not approval.',
                  'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                            'retirement desk (MMSR-2): confirm approval, action and date; for enlisted '
                            'requests, Deputy Commandant for Manpower and Reserve Affairs (DC M&RA) decides '
                            'Retired List approval and the Director, Manpower Management, decides Fleet '
                            'Marine Corps Reserve (FMCR) approval.',
                  'owner': 'Marine Corps separation and retirement desk (MMSR-2)'},
 'ret-orders': {'label': 'Get your retirement orders',
                'brief': 'Ask the personnel office to issue or confirm your orders after retirement '
                         'approval.',
                'how': ['Ask your installation personnel office for the status of your retirement or Fleet '
                        'Marine Corps Reserve (FMCR) orders.',
                        'Check the approved action, date and orders format with the office.',
                        'Keep copies and complete the separate transition, medical-record, survivor-benefit '
                        'and coverage tasks before departure.'],
                'why': 'The responsible unit issues orders after approval. For enlisted Marines, use Figure '
                       '7-1 for Fleet Marine Corps Reserve (FMCR) or Figure 7-2 for the Retired List. '
                       'Release must match the Marine Corps separation and retirement desk (MMSR-2) approved '
                       'date.',
                'verify': 'Installation Personnel Administration Center, order writing unit and Marine Corps '
                          'separation and retirement desk (MMSR-2): confirm approval, applicable orders '
                          'format and release date.',
                'owner': 'Personnel office'},
 'ret-sbp': {'label': 'Choose your survivor benefit coverage',
             'brief': 'Review the Survivor Benefit Plan with your spouse and confirm the election, any '
                      'required notarized agreement and form receipt.',
             'how': ['Ask your personnel office to arrange Survivor Benefit Plan (SBP) counseling for you '
                     'and your spouse.',
                     'Take the MarineNet counseling course together and review the available survivor '
                     'coverage choices.',
                     'Complete DD Form 2656 with the personnel office. If electing less than full coverage, '
                     "obtain your spouse's notarized agreement.",
                     'Send the completed form to the Defense Finance and Accounting Service (DFAS) and keep '
                     'proof of receipt. The rule requires receipt at least 30 days before the action; the '
                     'board targets 45 days.'],
             'why': 'The survivor coverage you elect can provide monthly income to an eligible spouse or '
                    'children after a retiree dies. Review the Survivor Benefit Plan (SBP) options together. '
                    'The pay office must receive DD Form 2656 at least 30 days before your action; the board '
                    'targets 45 days. Less than full coverage requires notarized spousal agreement; no '
                    'election means automatic full coverage deductions.',
             'verify': 'Installation Personnel Administration Center and Defense Finance and Accounting '
                       'Service (DFAS) retired pay: confirm DD 2656 submission and receipt at least 30 days '
                       'before the approved action, election and spousal concurrence.',
             'owner': 'You and spouse'},
 'ret-pay': {'label': 'Check your retired pay account',
             'brief': 'Confirm the pay office received your retirement pay form and has the right direct '
                      'deposit information.',
             'how': ['Ask the Defense Finance and Accounting Service (DFAS) to confirm receipt of DD Form '
                     '2656.',
                     'Check your direct deposit details and access to your retiree myPay account.',
                     'Ask when the first retired payment is expected and keep the confirmation.'],
             'why': 'Defense Finance and Accounting Service (DFAS) pays retired pay from the DD 2656 data. '
                    'Confirm the direct deposit account and your myPay retiree login before your date.',
             'verify': 'Defense Finance and Accounting Service (DFAS): confirm receipt of the DD 2656 and '
                       'when the first retired pay posts.',
             'owner': 'You'},
 'ret-ceremony': {'label': 'Arrange your retirement ceremony',
                  'brief': 'Settle the ceremony date and arrangements with your command so your family can '
                           'plan travel.',
                  'how': ['Ask your command to confirm who coordinates your retirement ceremony.',
                          'Agree on the date, venue, guests, speaker, flag and certificates.',
                          'Share confirmed arrangements with your family before booking travel.'],
                  'why': 'Ceremony arrangements follow command practice. Confirm the details early enough '
                         'for family travel.',
                  'verify': 'commanding officer (CO): the date, the venue, and who speaks.',
                  'owner': 'You'},
 'eas-orders': {'label': 'Confirm your orders and checkout schedule',
                'brief': 'Confirm your service end date, orders and final checkout schedule with the '
                         'personnel office.',
                'how': ['Ask your installation personnel office when your separation orders and checkout '
                        'schedule will be ready.',
                        'Tell your career planner you do not plan to reenlist, in writing if asked.',
                        'Check your end of active service date in Marine Online (MOL) against the board and '
                        'ask about anything that could extend service.'],
                'why': 'No request is needed to separate at end of active service. Orders and the checkout '
                       'schedule come from Installation Personnel Administration Center; confirm nothing is '
                       'pending that extends you.',
                'verify': 'Confirm with your installation personnel office when orders can be issued and '
                          'what local checkout requires.',
                'owner': 'Personnel office'},
 'sb-coord': {'label': 'Talk to your SkillBridge coordinator',
              'brief': 'Ask your installation coordinator about SkillBridge, a program for civilian job '
                       'training before leaving active duty.',
              'how': ['Contact your installation SkillBridge coordinator to discuss job-training options.',
                      'Ask the coordinator to verify the specific provider, program agreement and approval '
                      'route. Get daily and weekly training hours in writing before choosing.',
                      'Have the coordinator confirm how the printed 20-hours-per-week and 8-hours-per-day '
                      'thresholds apply. Record proposed dates as planning targets until written approval.',
                      'Complete initial counseling, pre-separation counseling, transition workshops, '
                      'Capstone review and command verification before SkillBridge participation. Confirm '
                      'completion and the separate transition rule deadlines with your transition office.'],
              'why': 'SkillBridge provides civilian job training and employment experience before leaving '
                     'active duty. Your coordinator confirms program requirements and uses the Navy College '
                     'Management Information System (NCMIS) for the application.',
              'verify': 'Installation SkillBridge coordinator and approving command: confirm daily and '
                        'weekly hours, application of both NAVMC thresholds and the governing approval '
                        'route. Installation Transition Readiness Program (TRP) office and unit transition '
                        'coordinator (UTC): verify completion before SkillBridge participation.',
              'owner': 'You'},
 'sb-provider': {'label': 'Choose a program and get accepted',
                 'brief': 'Have your coordinator verify a SkillBridge program before you apply, then get its '
                          'acceptance letter.',
                 'how': ['Ask your SkillBridge coordinator to verify the specific provider and program '
                         'agreement before applying.',
                         'Get an acceptance letter listing location, cost, length, employment outcome and '
                         'the provider contact.',
                         'Obtain daily and weekly training hours in writing. For online training, confirm '
                         'the required live or in-person format and that self-paced training is less than 50 '
                         'percent.',
                         'Keep dates proposed until written approval. Ask the coordinator to confirm how '
                         'both printed training-hour thresholds apply.'],
                 'why': 'Have the coordinator verify the specific program and provider approval/memorandum '
                        'of understanding (MOU) before applying. Online opportunities must include live '
                        'person-led training and/or a hybrid with in-person sessions. Asynchronous training '
                        'must be less than 50 percent of training length.',
                 'verify': 'Installation SkillBridge coordinator: confirm specific program/provider approval '
                           'and memorandum of understanding (MOU), online format and both daily and weekly '
                           'hours before selection.',
                 'owner': 'You'},
 'sb-ethics': {'label': 'Complete your SkillBridge ethics course',
               'brief': 'Finish the required ethics course before submitting your SkillBridge packet and '
                        'check that it will still be valid at the actual start.',
               'how': ['Complete Developing Your Business Ethics (LLISELF301) on MarineNet, or ask the '
                       'coordinator to confirm an accepted equivalent.',
                       'Save the completion certificate for your packet.',
                       'Have the coordinator check completion within 12 calendar months before your actual '
                       'start. The 61-day preparation date is a planning target; recheck if the start '
                       'changes.'],
               'why': 'Complete ethics before packet submission and within 12 calendar months before the '
                      'actual program start. The 61-day lead from a proposed start is a preparation target '
                      'while approval is pending. Recheck completion and validity against the approved '
                      'start.',
               'verify': 'Installation SkillBridge coordinator and approving command: confirm ethics '
                         'completion before packet submission and validity within 12 calendar months before '
                         'the actual start.',
               'owner': 'You'},
 'sb-ethics-validity': {'label': 'Check your ethics course is valid',
                        'brief': 'Compare your ethics completion date with your actual SkillBridge start '
                                 'before departure.',
                        'how': ['Ask your SkillBridge coordinator to check your ethics certificate against '
                                'the actual program start.',
                                'Confirm the exact 12-calendar-month completion window and record the '
                                'office-confirmed dates here.',
                                'Keep this check date a planning target and the course completion target on '
                                'its separate task. Recheck after a start-date change.'],
                        'why': 'The SkillBridge guidance requires ethics completion within 12 calendar '
                               'months before the actual program start. Have the coordinator calculate the '
                               'valid completion window and recheck it if the start changes.',
                        'verify': 'Installation SkillBridge coordinator and approving command: calculate the '
                                  'exact 12-calendar-month window from the actual start and verify the '
                                  'ethics completion date falls inside it before departure.',
                        'owner': 'You'},
 'sb-cover': {'label': 'Confirm who covers your job',
              'brief': 'Agree with your commander on who covers your duties during SkillBridge and get the '
                       'absence plan checked.',
              'how': ['Ask your commanding officer who will cover your duties during SkillBridge.',
                      'Record the coverage plan and give it to your SkillBridge coordinator for the packet.',
                      'Have the coordinator and approving command confirm the governing duration policy and '
                      'full absence calendar in writing before relying on dates.'],
              'why': 'Your unit needs a plan for your duties during SkillBridge. Confirm the applicable '
                     'duration and approval rules with the coordinator and approving command before '
                     'departure.',
              'verify': 'Installation SkillBridge coordinator and approving command: provide the governing '
                        'version and approval route in writing. Confirm the approved total absence against '
                        'the combined absence cap. Approve the sequence before dates are used.',
              'owner': 'Commanding officer'},
 'sb-packet': {'label': 'Submit your SkillBridge packet',
               'brief': 'Review the application and supporting documents with your coordinator before '
                        'sending them for command approval.',
               'how': ['Ask your SkillBridge coordinator to review your application packet before '
                       'submission.',
                       'Include the provider acceptance letter, ethics certificate, command endorsement, job '
                       'coverage plan and unit contact plan. Submit through the Navy College Management '
                       'Information System (NCMIS).',
                       'Confirm the actual submission deadline and approval route. The 60-day lead is a '
                       'planning target; keep proposed dates separate from approved dates.',
                       'Complete initial counseling, pre-separation counseling, transition workshops, '
                       'Capstone review and command verification before SkillBridge participation.'],
               'why': 'The packet gives the approving command your program, preparation and absence plan. '
                      'Ask the coordinator to confirm the governing duration policy and approval authority '
                      'in writing.',
               'verify': 'Installation SkillBridge coordinator and approving command: provide the governing '
                         'version and approval route in writing. Confirm the approved total absence against '
                         'the combined absence cap. Approve the sequence before dates are used. Installation '
                         'Transition Readiness Program (TRP) office and unit transition coordinator (UTC): '
                         'verify completion before SkillBridge participation.',
               'owner': 'You'},
 'sb-approval': {'label': 'Get written SkillBridge approval',
                 'brief': 'Get written command approval and approved start and end dates before '
                          'participating.',
                 'how': ['Ask your SkillBridge coordinator for the written command decision on your '
                         'application.',
                         'On approval, replace proposed start and end dates with the approved dates. Record '
                         'the approval date separately.',
                         'Recheck your ethics certificate, provider acceptance and full absence sequence '
                         'before departure.',
                         'Complete initial counseling, pre-separation counseling, transition workshops, '
                         'Capstone review and command verification before SkillBridge participation.'],
                 'why': 'Written command approval is required before participation. Use a proposed start to '
                        'schedule the acceptance letter, ethics course and packet beforehand. On approval, '
                        'give Claude the approved dates to replace the proposal and record the approval date '
                        'separately. Recheck completed prerequisites and ethics validity before departure.',
                 'verify': 'Installation SkillBridge coordinator and approving command: confirm written '
                           'approval, actual approval date and approved start/end before participation. '
                           'Installation Transition Readiness Program (TRP) office and unit transition '
                           'coordinator (UTC): verify completion before SkillBridge participation.',
                 'owner': 'Approving commander'},
 'sb-sequence': {'label': 'Confirm your full absence plan',
                 'brief': 'Have the coordinator and command review SkillBridge, authorized administrative '
                          'absence, leave and liberty as one calendar.',
                 'how': ['Give your SkillBridge coordinator and approving command your complete absence '
                         'calendar.',
                         'Include SkillBridge, permissive temporary additional duty (PTAD), leave and '
                         'liberty. Ask for written confirmation of the governing duration cap and sequence.',
                         'Marine administrative message (MARADMIN) 280/24 requires authorized administrative '
                         'absence before leave within its category cap. Confirm which policy governs before '
                         'departure; replace proposed dates after written approval.',
                         'Complete initial counseling, pre-separation counseling, transition workshops, '
                         'Capstone review and command verification before SkillBridge participation.'],
                 'why': 'Your full absence plan must fit the policy the approving command confirms. Have the '
                        'coordinator resolve duration and sequence questions before you rely on the '
                        'calendar.',
                 'verify': 'Installation SkillBridge coordinator and approving command: provide the '
                           'governing version and approval route in writing. Confirm the approved total '
                           'absence against the combined absence cap. Approve the sequence before dates are '
                           'used. Installation Transition Readiness Program (TRP) office and unit transition '
                           'coordinator (UTC): verify completion before SkillBridge participation.',
                 'owner': 'You'},
 'sb-account': {'label': 'Set your unit contact schedule',
                'brief': 'Agree with your unit on when and how you will check in during SkillBridge.',
                'how': ['Ask your command to confirm your SkillBridge contact and check-in schedule.',
                        'Record who you report to, how to reach them and the schedule the command approves.',
                        'Confirm the plan before departure. The 65-day lead is a planning target.'],
                'why': 'The command must establish detailed accountability protocols during participation. '
                       'Confirm the plan before the proposed or approved start; the 65-day lead is a '
                       'planning target.',
                'verify': 'Installation SkillBridge coordinator and approving command: confirm the contact '
                          'schedule and accountability plan before departure.',
                'owner': 'You'},
 'sb-run': {'label': 'Confirm you can begin SkillBridge',
            'brief': 'Check written approval, final dates and completed transition requirements before you '
                     'leave for the program.',
            'how': ['Ask your SkillBridge coordinator to confirm you are cleared to begin the approved '
                    'program.',
                    'Check written approval and the actual program dates with your coordinator. Have the '
                    'coordinator review your ethics certificate and daily training schedule against the '
                    'approved absence plan.',
                    'Complete initial counseling, pre-separation counseling, transition workshops, Capstone '
                    'review and command verification before SkillBridge participation.',
                    'Confirm the governing duration and approval rules with the command. Do not plan to '
                    'extend obligated service to finish SkillBridge.'],
            'why': 'Participation requires written approval and completed prerequisites. Confirm the '
                   'governing duration policy with your coordinator and command before departure; '
                   'SkillBridge does not authorize extending obligated service.',
            'verify': 'Installation SkillBridge coordinator and approving command: provide the governing '
                      'version and approval route in writing. Confirm the approved total absence against the '
                      'combined absence cap. Approve the sequence before dates are used. Installation '
                      'Transition Readiness Program (TRP) office and unit transition coordinator (UTC): '
                      'verify completion before SkillBridge participation.',
            'owner': 'You'},
 'sb-start': {'label': 'Plan your SkillBridge start',
              'brief': 'Use a proposed start for preparation, then replace it with the start date the '
                       'command approves.',
              'how': ['Record your proposed SkillBridge start in your profile and note that approval is '
                      'pending.',
                      'After written approval, replace the proposed start and end with approved dates. '
                      'Record the actual approval date separately.',
                      'Recheck ethics validity and the complete absence calendar.',
                      'Complete initial counseling, pre-separation counseling, transition workshops, '
                      'Capstone review and command verification before SkillBridge participation.'],
              'why': 'Use a proposed program start in your profile to plan preparation while approval is '
                     'pending. Preparation dates are targets. Replace the proposal with the approved start '
                     'after written command approval and recheck prerequisites, ethics validity and the '
                     'absence sequence. Recording approval does not change the scheduled start.',
              'verify': 'Installation SkillBridge coordinator and approving command: confirm the proposed '
                        'schedule, then written approval and the final start/end before participation. '
                        'Installation Transition Readiness Program (TRP) office and unit transition '
                        'coordinator (UTC): verify completion before SkillBridge participation.',
              'owner': 'You'},
 'sb-cert': {'label': 'Take your funded certification exam',
             'brief': 'Confirm the exam date and program funding before SkillBridge ends.',
             'how': ['Ask your provider which certification exam the program funds and when you must take '
                     'it.',
                     'Arrange the exam within the confirmed program coverage period.',
                     'Keep the exam result and any certification record.'],
             'why': 'Sit any funded exam while the program still covers it.',
             'verify': 'Provider: the exam date and what the program funds.',
             'owner': 'You'},
 'va-vso': {'label': 'Choose someone to help your claim',
            'brief': 'Find an accredited veterans service organization representative to help prepare and '
                     'file your disability claim at no cost.',
            'how': ['Find an accredited veterans service organization representative who can take your case.',
                    'Use https://www.va.gov/get-help-from-accredited-representative/ to check accreditation '
                    'and ask about intake availability.',
                    'Review and sign Department of Veterans Affairs (VA) Form 21-22 to appoint the '
                    'organization. Ask what records to bring and when to meet.'],
            'why': 'An accredited veterans service organization representative helps prepare and file your '
                   'Department of Veterans Affairs (VA) claim and can represent you afterward. Chartered '
                   'organizations provide these services at no cost to you.',
            'verify': 'Department of Veterans Affairs (VA) benefits office or accredited veterans service '
                      'organization: confirm accreditation, appointment on VA Form 21-22 and actual intake '
                      'date.',
            'owner': 'You'},
 'va-shpe': {'label': 'Schedule your separation physical',
             'brief': 'Call your military clinic to schedule your separation physical and confirm whether a '
                      'completed benefits assessment can satisfy it.',
             'how': ['Call your military medical clinic to arrange the Separation History and Physical '
                     'Examination (SHPE).',
                     'Ask about the manual requirement to schedule at least 6 months before separation and '
                     'which records to bring.',
                     'If using the Separation Health Assessment (SHA) instead, have the clinic confirm '
                     'completed results were returned to the Department of Defense (DoD) at least 30 days '
                     'before separation. A scheduled exam alone is not enough.'],
             'why': 'The manual says schedule Separation History and Physical Examination (SHPE) at least 6 '
                    'months before separation. The Department of Veterans Affairs (VA) guide says a '
                    'completed Separation Health Assessment (SHA) returned to Department of Defense (DoD) at '
                    'least 30 days before separation can satisfy the discharge examination requirement. '
                    'Confirm the clinic accepts the completed and returned SHA; a scheduled VA exam alone '
                    'does not satisfy this condition.',
             'verify': 'Military medical clinic and Department of Veterans Affairs (VA): confirm scheduling, '
                       'Separation Health Assessment (SHA) completion and return to Department of Defense '
                       '(DoD), and whether a separate Separation History and Physical Examination (SHPE) '
                       'remains required.',
             'owner': 'You'},
 'va-records': {'label': 'Keep complete copies of your records',
                'brief': 'Request your full military and civilian medical, dental and service records for '
                         'your claim and personal files.',
                'how': ['Ask your military records office for complete medical and dental records, including '
                        'older paper records.',
                        'Request applicable civilian records and keep your complete service history for your '
                        'Department of Veterans Affairs (VA) claim.',
                        'Ask the records office and personnel office which export they need. Keeping '
                        'personal copies does not replace delivery of your complete Service Treatment '
                        'Record.'],
                'why': 'Keep personal copies for your Benefits Delivery at Discharge (BDD) claim and record '
                       'review. The Department of Veterans Affairs (VA) guide requires scanned physical, '
                       'electronic and applicable civilian records for your entire service history. Personal '
                       'export does not satisfy delivery of the complete Service Treatment Record to '
                       'Installation Personnel Administration Center.',
                'verify': 'Military medical records office, Department of Veterans Affairs (VA) and '
                          'Installation Personnel Administration Center: confirm complete exports, records '
                          'for Benefits Delivery at Discharge (BDD) and Service Treatment Record '
                          'delivery/acceptance before the first applicable action.',
                'owner': 'You'},
 'va-service-end': {'label': 'Confirm your last active duty day',
                    'brief': 'Ask the personnel office to confirm the last day of active duty used for your '
                             'claim and transition deadlines.',
                    'how': ['Ask your installation personnel office to confirm your actual last active-duty '
                            'day.',
                            'Keep this date separate from the retirement action date. If the confirmed day '
                            'differs from the projection, record that fixed date here.',
                            'Have the Department of Veterans Affairs (VA) or an accredited veterans service '
                            'organization representative confirm both Benefits Delivery at Discharge (BDD) '
                            'filing-window endpoints.',
                            'Ask your installation transition office to confirm the date used for transition '
                            "rule deadlines. Record completion without changing this milestone's service-end "
                            'date.'],
                    'why': 'Your entered date projects the last active-duty day and the Benefits Delivery at '
                           'Discharge (BDD) and transition deadlines. end of active service, resignation and '
                           'month-end Fleet Marine Corps Reserve (FMCR) use that day; ordinary Retired List '
                           'retirement uses the preceding day. A confirmed date you set here overrides the '
                           'projection. Confirm exceptions with Installation Personnel Administration Center '
                           'and Marine Corps separation and retirement desk (MMSR-2).',
                    'verify': 'Installation Personnel Administration Center and Marine Corps separation and '
                              'retirement desk (MMSR-2): confirm the last active-duty day separately from '
                              'the Retired List/Fleet Marine Corps Reserve (FMCR) action. Department of '
                              'Veterans Affairs (VA) benefits office or accredited veterans service '
                              'organization: confirm the Benefits Delivery at Discharge (BDD) window counted '
                              'from that service-end date. Installation Transition Readiness Program (TRP) '
                              'office and unit transition coordinator (UTC): confirm end of active service '
                              'for TRP deadlines.',
                    'owner': 'You'},
 'va-str': {'label': 'Deliver your complete medical service record',
            'brief': 'Ask your records and personnel offices when to deliver your complete medical record '
                     'before your first applicable absence or separation.',
            'how': ['Ask medical records and your installation personnel office for the deadline and '
                    'required Service Treatment Record export.',
                    'Include required military and civilian medical and dental records, the medical system '
                    'web print and DD Form 2963.',
                    'Deliver before the first applicable transition administrative absence, terminal leave, '
                    'Individual Ready Reserve (IRR) transfer, separation or retirement. Record an earlier '
                    'office-confirmed date if needed.',
                    'Get confirmation that the personnel office accepted the complete record.'],
            'why': 'Submit the complete Service Treatment Record to Installation Personnel Administration '
                   'Center (IPAC)/Administration reporting unit code (RUC) before transition permissive '
                   'temporary additional duty (PTAD), terminal leave, Individual Ready Reserve (IRR) '
                   'transfer, separation or retirement. Include service and civilian medical/dental records, '
                   'the required Armed Forces Health Longitudinal Technology Application (AHLTA) web print '
                   'and DD Form 2963. Confirm the required export with medical records and IPAC.',
            'verify': 'Military medical records office and Installation Personnel Administration Center: '
                      'enter the delivery deadline and confirm the required export and acceptance of the '
                      'complete Service Treatment Record before the first applicable action.',
            'owner': 'You'},
 'va-conditions': {'label': 'List health issues for your claim',
                   'brief': 'Write down the health issues you want your accredited representative to review, '
                            'including issues missing from your records.',
                   'how': ['List the health issues you want to discuss with your claim representative.',
                           'For each issue, note where it appears in your records and what documentation is '
                           'missing.',
                           'Review the list with an accredited veterans service organization representative; '
                           'do not guess a diagnosis.'],
                   'why': 'Your representative works from this list when preparing your disability claim. '
                          'Include issues that still need a medical visit.',
                   'verify': None,
                   'owner': 'You'},
 'va-sickcall': {'label': 'Have undocumented health issues evaluated',
                 'brief': 'Arrange a medical visit for health issues that are missing from your service '
                          'records.',
                 'how': ['Call your military clinic about a health issue that is not yet documented.',
                         'Describe the symptoms, when they began and how they affect daily activities.',
                         'Keep the visit record and review it with your accredited claim representative.'],
                 'why': 'An in-service medical record can support later review of whether a health issue is '
                        'connected to service. Your clinic and claim representative can help identify '
                        'missing records.',
                 'verify': None,
                 'owner': 'You'},
 'va-hearing': {'label': 'Get your hearing test on record',
                'brief': 'Ask your clinic to arrange your separation hearing test and keep the result.',
                'how': ['Ask your military clinic where to complete your separation hearing test.',
                        'Tell the clinician about hearing changes or ringing in your ears.',
                        'Keep a copy of the result with the records for your disability claim.'],
                'why': 'Baseline for any hearing or tinnitus claim.',
                'verify': None,
                'owner': 'You'},
 'va-exposure': {'label': 'Record your deployment exposures',
                 'brief': 'Review your deployment exposure record with your military medical office before '
                          'filing your claim.',
                 'how': ['Ask your military medical or exposure office to help review your Individual '
                         'Exposure Summary.',
                         'Ask how to access the exposure record system, save the summary and report missing '
                         'deployment events.',
                         'Discuss each exposure with medical before filing and review the record with your '
                         'accredited claim representative.'],
                 'why': 'Your medical office and claim representative need an accurate exposure history. Ask '
                        'them to review missing events before you file.',
                 'verify': 'veterans service organization: Individual Longitudinal Exposure Record (ILER) '
                           'review for every deployment.',
                 'owner': 'You'},
 'va-bh': {'label': 'Get behavioral health concerns evaluated',
           'brief': 'Tell your clinic about sleep, stress, mood or other behavioral health concerns while '
                    'you are still serving.',
           'how': ['Ask your military clinic for a behavioral health evaluation.',
                   'Describe sleep, stress, mood and effects on work and home plainly.',
                   'Keep the clinical record with your medical files for review with your claim '
                   'representative.'],
           'why': 'Clinical care addresses current concerns and documents what you report during service. '
                  'Your clinic can help arrange the appropriate evaluation.',
           'verify': None,
           'owner': 'You'},
 'va-reserve': {'label': 'Confirm your Reserve medical qualification',
                'brief': 'Ask medical and your career counselor how your claim and medical record affect '
                         'Reserve qualification.',
                'how': ['Ask your military medical office and career counselor to review Reserve medical '
                        'qualification.',
                        'Discuss your claim and medical record before the Direct Affiliation Program request '
                        'is submitted.',
                        "Record the offices' answers and any remaining medical requirements."],
                'why': 'Settle how a claim interacts with Reserve medical standards before the Direct '
                       'Affiliation Program request goes in.',
                'verify': None,
                'owner': 'You'},
 'va-parta': {'label': 'Complete your claim self assessment',
              'brief': 'Complete the health self-assessment that must go with your pre-discharge claim.',
              'how': ['Ask your accredited claim representative for Separation Health Assessment (SHA) Part '
                      'A.',
                      'Complete the self-assessment using your full health history and records.',
                      'Have your representative confirm the completed Part A is included with your Benefits '
                      'Delivery at Discharge (BDD) submission.'],
              'why': 'Include your completed Separation Health Assessment (SHA) Part A with the Benefits '
                     'Delivery at Discharge (BDD) claim. Your accredited representative can confirm the '
                     'self-assessment is complete before submission.',
              'verify': 'Department of Veterans Affairs (VA) benefits office or accredited veterans service '
                        'organization: confirm the completed Part A is included with the actual Benefits '
                        'Delivery at Discharge (BDD) submission.',
              'owner': 'You'},
 'va-file': {'label': 'File your pre-discharge disability claim',
             'brief': 'Prepare your disability claim with an accredited representative and file within the '
                      'confirmed pre-discharge window.',
             'how': ['Ask your accredited representative to prepare your Department of Veterans Affairs (VA) '
                     'pre-discharge disability claim.',
                     'Confirm your last active-duty day with the personnel office. Benefits Delivery at '
                     'Discharge (BDD) accepts claims 180 to 90 days before that day; have VA or your '
                     'representative confirm both endpoints.',
                     'Review VA Form 21-526EZ, complete service medical records and Separation Health '
                     'Assessment (SHA) Part A with your representative before filing.',
                     'File within the confirmed window, keep confirmation of submission and record the '
                     'actual filing day. Keep 45 days after filing available for exams. The board filing '
                     'target may move for a weekend; the actual window does not.'],
             'why': 'Benefits Delivery at Discharge (BDD) is the Department of Veterans Affairs (VA) '
                    'pre-discharge disability claim route. It needs a known separation date, complete '
                    'records and the health self-assessment. File within the confirmed 180-to-90-day window '
                    'and keep 45 days after filing available for exams.',
             'verify': 'Department of Veterans Affairs (VA) benefits office or accredited veterans service '
                       'organization: confirm the known service-end date, actual filing date, required '
                       'records, Part A and 45-day examination availability.',
             'owner': 'Accredited claim representative'},
 'va-exams': {'label': 'Keep time free for disability exams',
              'brief': 'Confirm the actual filing day and keep the following examination period clear while '
                       'you wait for appointments.',
              'how': ['Confirm your actual disability claim filing date with the Department of Veterans '
                      'Affairs (VA) or your accredited representative.',
                      'Keep 45 days after filing available for examinations and record each confirmed '
                      'appointment.',
                      'Ask VA about exam locations and your personnel office about duty status. Plan travel '
                      'around the appointments.',
                      'Until actual filing is recorded, the board examination period is a planning target '
                      'projected from the filing target.'],
              'why': 'A planning target. Until you mark the Benefits Delivery at Discharge (BDD) filing '
                     'done, this window is projected from the filing target; once it is done, it counts from '
                     'the day you filed. Department of Veterans Affairs (VA) schedules the exams after you '
                     'file, and you must be available for 45 days from the filing date. Where the exams are, '
                     'and whether exam days count as duty time, are questions for VA and Installation '
                     'Personnel Administration Center.',
              'verify': 'veterans service organization: the day the claim was filed and the exam dates '
                        'Department of Veterans Affairs (VA) gives you. VA and Installation Personnel '
                        'Administration Center: exam location, and duty status for exam days.',
              'owner': 'You'},
 'va-add': {'label': 'Confirm how to add claim issues',
            'brief': 'Ask the benefits office how to add a health issue to your existing pre-discharge claim '
                     'before its filing window closes.',
            'how': ['Ask the Department of Veterans Affairs (VA) or your accredited representative how to '
                    'add health issues to your existing claim.',
                    'Confirm the procedure and actual deadline before the Benefits Delivery at Discharge '
                    '(BDD) window closes.',
                    "Record the confirming office and deadline. Keep the board's day-90 planning target "
                    'separate; use a rule deadline only when the source sets one.'],
            'why': 'Adding health issues to an existing claim needs a confirmed procedure and deadline. Ask '
                   'the benefits office or your accredited representative before the pre-discharge window '
                   'closes.',
            'verify': 'Department of Veterans Affairs (VA) benefits office or accredited veterans service '
                      'organization: confirm the procedure and actual deadline for adding conditions to your '
                      'existing claim.',
            'owner': 'You'},
 'va-sha': {'label': 'Confirm your health assessment was returned',
            'brief': 'Ask your military clinic whether it received and accepted the completed health '
                     'assessment used instead of a separate separation physical.',
            'how': ['Ask your military clinic whether your completed Separation Health Assessment (SHA) has '
                    'been returned and accepted.',
                    'If using it instead of the Separation History and Physical Examination (SHPE), confirm '
                    'the Department of Veterans Affairs (VA) returned completed results to the Department of '
                    'Defense (DoD).',
                    'Have the clinic confirm receipt at least 30 days before your last active-duty day and '
                    'whether you still need a separate physical.',
                    'Record the confirmation and keep a copy of the completed results.'],
            'why': 'If the Separation Health Assessment (SHA) is used instead of a separate Separation '
                   'History and Physical Examination (SHPE), return completed results to Department of '
                   'Defense (DoD) at least 30 days before your confirmed last active-duty day. The military '
                   'medical clinic and Department of Veterans Affairs (VA) must confirm applicability, '
                   'return and acceptance. The cutoff stays pending until the office confirms your '
                   'service-end date.',
            'verify': 'Military medical clinic and Department of Veterans Affairs (VA): confirm completed '
                      'Separation Health Assessment (SHA) results returned to Department of Defense (DoD) by '
                      'the required date and whether Separation History and Physical Examination (SHPE) is '
                      'still needed.',
            'owner': 'Medical'},
 'va-intent': {'label': 'Record your intent to file receipt',
               'brief': 'If you miss the pre-discharge claim route, ask about an intent to file and save the '
                        'actual receipt date.',
               'how': ['If Benefits Delivery at Discharge (BDD) is missed, ask the Department of Veterans '
                       'Affairs (VA) or your accredited representative whether to submit an intent to file.',
                       'Keep the VA receipt or automatic online confirmation and record the actual intent '
                       'date here. Do not substitute a planned date or service end date.',
                       'Have VA confirm the potential effective date and the calendar anniversary on '
                       '"Complete your claim after filing intent". Leave this item undated until receipt; '
                       'mark it not applicable if no intent is needed.'],
               'why': 'Benefits Delivery at Discharge (BDD) is the preferred route in this plan. If you miss '
                      'it, an intent to file can protect a potential effective date; ask the Department of '
                      'Veterans Affairs (VA) or your accredited representative whether it applies.',
               'verify': 'Department of Veterans Affairs (VA) benefits office or accredited veterans service '
                         'organization: confirm whether an intent is needed, the actual VA intent date and '
                         'the potential effective date.',
               'owner': 'You'},
 'va-itf-complete': {'label': 'Complete your claim after filing intent',
                     'brief': 'Use the actual intent receipt date to confirm when your completed claim must '
                              'reach the benefits office.',
                     'how': ['Ask the Department of Veterans Affairs (VA) or your accredited representative '
                             'to confirm the filing deadline from your actual intent receipt date.',
                             'Record that receipt on "Record your intent to file receipt" so the '
                             'calendar-year deadline can be calculated.',
                             'Complete and submit the claim within 1 year of the actual intent date. Keep '
                             'proof of receipt and record any different deadline the office confirms.'],
                     'why': 'Complete and file your claim within 1 year of the actual Department of Veterans '
                            'Affairs (VA) intent date on the "Record your intent to file receipt" item. It '
                            'stays undated until the actual intent event is recorded; it is separate from '
                            'the separation effective-date item.',
                     'verify': 'Department of Veterans Affairs (VA) benefits office or accredited veterans '
                               'service organization: confirm the exact 1-year filing deadline from the '
                               'actual intent date and receipt of the completed claim.',
                     'owner': 'You'},
 'va-decision': {'label': 'Check for your disability claim decision',
                 'brief': 'Check claim status while you wait. Review the decision with your accredited '
                          'representative when it arrives.',
                 'how': ['Check your disability claim status with the Department of Veterans Affairs (VA).',
                         'When a decision arrives, talk through it with the person helping you file.',
                         'Save the decision and ask what to do next. The board does not promise a decision '
                         'date.'],
                 'why': 'Benefits Delivery at Discharge (BDD) aims for a decision at or soon after '
                        'separation.',
                 'verify': None,
                 'owner': 'Department of Veterans Affairs (VA)'},
 'va-health': {'label': 'Apply for veterans health care',
               'brief': 'Ask the benefits office about health care enrollment and how it fits with your '
                        'other coverage.',
               'how': ['Ask the Department of Veterans Affairs (VA) to confirm your health care eligibility '
                       'and enrollment options.',
                       'Use https://www.va.gov/health-care/how-to-apply/ to review the application process.',
                       'Confirm application status and when care can begin. Coordinate other family coverage '
                       'separately; the guide sets no general application deadline.'],
               'why': 'The guide permits application no earlier than 1 year before separation and any time '
                      'afterward. It sets no general application deadline. Have Department of Veterans '
                      'Affairs (VA) confirm individual eligibility and coordinate your other coverage.',
               'verify': 'Department of Veterans Affairs (VA) benefits office: confirm eligibility, '
                         'application status and the care start date.',
               'owner': 'You'},
 'va-drill': {'label': 'Reconcile disability and Reserve drill pay',
              'brief': 'Compare the benefits office notice with your actual paid Reserve training days '
                       'before choosing a pay waiver.',
              'how': ['Ask the Department of Veterans Affairs (VA) and your Reserve unit for the '
                      'paid-training notice and instructions.',
                      'Compare paid assemblies and active-duty days with the notice and resolve differences '
                      'with both offices.',
                      'Confirm how days are counted and the actual response deadline before submitting the '
                      'waiver. Do not assume each weekend has the same paid-day count.'],
              'why': 'Reserve training pay and disability compensation need a yearly reconciliation. The '
                     'benefits office and your unit must confirm actual paid days, the notice instructions '
                     'and its response deadline.',
              'verify': 'Department of Veterans Affairs (VA) benefits office and gaining Reserve unit '
                        'administration: confirm paid-day counting, discrepancies, the applicable notice and '
                        'response deadline.',
              'owner': 'You'},
 'va-dental': {'label': 'Confirm one-time veterans dental care',
               'brief': 'Ask the veterans dental clinic to check eligibility and accept your application '
                        'promptly.',
               'how': ['Ask the Department of Veterans Affairs (VA) dental clinic to check your eligibility '
                       'for one-time Class II dental care.',
                       'Have the clinic review qualifying service, discharge status and the dental treatment '
                       'entry on DD Form 214.',
                       'Apply promptly and keep proof of receipt. The board day-30 date is a planning '
                       'target; the current VA source gives a 180-day application window after discharge or '
                       'release.',
                       "Ask the clinic to resolve any exception and the older manual's different service and "
                       'application limits before relying on them.'],
               'why': 'The current Department of Veterans Affairs (VA) source provides one-time Class II '
                      'dental care for qualifying Persian Gulf War-era active service of 90 days or more. '
                      'All conditions must be met: no dishonorable discharge, application within 180 days of '
                      'discharge or release, and a DD214 that does not show a complete dental exam and all '
                      'needed treatment before discharge. VA dental must confirm your individual eligibility '
                      'and application deadline.',
               'verify': 'Confirm with the veterans dental clinic and your accredited claim representative: '
                         'Class II eligibility, DD Form 214 entry, application receipt deadline and any '
                         'exception. Ask the clinic to resolve differences between the older manual and '
                         'current guidance; ask the personnel office to confirm the discharge record entry.',
               'owner': 'You'},
 'va-net': {'label': 'Check your claim filing anniversary',
            'brief': 'Have the benefits office confirm your individual receipt deadline and effective date '
                     'before the displayed filing anniversary.',
            'how': ['Ask the Department of Veterans Affairs (VA) or your accredited representative to '
                    'confirm your individual filing deadline and potential effective date.',
                    'Check the calendar anniversary from your confirmed last active-duty day, including any '
                    'fixed date recorded on the board.',
                    'Arrange filing before the confirmed deadline. The board does not extend this '
                    'anniversary for weekends or holidays.'],
            'why': 'The guide illustrates a claim received within 1 year of separation becoming effective '
                   'the day after separation. This calendar anniversary counts from the last active-duty '
                   'day, including any confirmed override. It does not decide individual entitlement or '
                   'exceptions. Have Department of Veterans Affairs (VA) or your accredited veterans service '
                   'organization confirm the actual receipt deadline and effective date before this '
                   'boundary.',
            'verify': 'Department of Veterans Affairs (VA) benefits office or accredited veterans service '
                      'organization: confirm the individual effective date, entitlement, receipt deadline '
                      'and any applicable exception. The board does not extend the anniversary for weekends '
                      'or holidays.',
            'owner': 'You'},
 'va-net-confirm': {'label': 'Confirm your claim receipt deadline',
                    'brief': 'Contact the benefits office before the separate filing anniversary so you can '
                             'confirm the deadline and file in time.',
                    'how': ['Ask the Department of Veterans Affairs (VA) or your accredited representative '
                            'to confirm your actual claim receipt deadline.',
                            'Confirm the effective date and any individual exception, then arrange filing '
                            'before the deadline.',
                            'Record the office and confirmed date. Keep the separate 1-year boundary '
                            'visible; this 11-month check is a planning target.'],
                    'why': 'Contact the Department of Veterans Affairs (VA) or your accredited '
                           'representative before the separate 1-year filing boundary. The board targets '
                           'this check 11 calendar months after your last active-duty day. It moves the '
                           'planning target earlier for a weekend or federal holiday. Arrange filing before '
                           'the confirmed deadline.',
                    'verify': 'Department of Veterans Affairs (VA) benefits office or accredited veterans '
                              'service organization: confirm the receipt deadline and effective date before '
                              'the separately displayed 1-year boundary.',
                    'owner': 'You'},
 'dap-ram1': {'label': 'Ask about your Reserve commission timeline',
              'brief': 'Ask the Reserve officer appointments desk to confirm headquarters receipt and the '
                       'time needed for your commission decision.',
              'how': ['Contact the Reserve officer appointments desk (RAM-1) about your requested separation '
                      'date.',
                      'Ask which appointment approval list applies and confirm when Headquarters Marine '
                      'Corps (HQMC) received your Reserve appointment request.',
                      'Ask about processing time and status. Record actual headquarters receipt on "Confirm '
                      'receipt of your commission request"; the day the desk replies is not the receipt '
                      'date.'],
              'why': 'Resignation approval and a populated end of active service (EAS) permit Reserve '
                     'Affairs (RA) submission. Reserve appointment approval requires at least 4 months from '
                     'Headquarters Marine Corps (HQMC) receipt of the request, with more time for adverse '
                     'cases. Record and confirm that receipt date; the resignation planning target does not '
                     'promise approval by EAS.',
              'verify': 'Reserve officer appointments desk (RAM-1), Installation Personnel Administration '
                        'Center and Marine Corps separation and retirement desk (MMSR-2): confirm '
                        'Headquarters Marine Corps (HQMC) receipt date, populated end of active service, '
                        'scroll and remaining processing interval.',
              'owner': 'You'},
 'dap-receipt': {'label': 'Confirm receipt of your commission request',
                 'brief': 'Get the actual headquarters receipt date from the Reserve officer appointments '
                          'desk and keep it separate from approval.',
                 'how': ['Ask the Reserve officer appointments desk (RAM-1) when headquarters received your '
                         'appointment request.',
                         'Record the actual confirmed receipt date here. Keep the task waiting until receipt '
                         'is confirmed.',
                         'Check the separate commission approval with the desk and personnel office. The '
                         'minimum 4-month processing interval starts at headquarters receipt; it does not '
                         'promise approval by your departure.'],
                 'why': 'The minimum 4-month processing interval starts at Headquarters Marine Corps (HQMC) '
                        'receipt of the Reserve appointment request. end of active service minus 4 calendar '
                        'months is the latest ordinary receipt planning boundary, not an approval guarantee. '
                        'Adverse cases need more time. Actual receipt remains pending Reserve officer '
                        'appointments desk (RAM-1) confirmation.',
                 'verify': 'Reserve officer appointments desk (RAM-1), Installation Personnel Administration '
                           'Center and Marine Corps separation and retirement desk (MMSR-2): confirm the '
                           'actual Headquarters Marine Corps (HQMC) receipt date separately from resignation '
                           'approval and the Reserve appointment decision.',
                 'owner': 'You'},
 'dap-cc': {'label': 'Discuss Reserve options with your counselor',
            'brief': 'Ask your career counselor about Reserve jobs and whether direct affiliation fits your '
                     'separation plan.',
            'how': ['Arrange a meeting with your career counselor about the Direct Affiliation Program.',
                    'Ask about Selected Marine Corps Reserve (SMCR) unit jobs and Individual Mobilization '
                    'Augmentee (IMA) positions.',
                    'Confirm eligibility, available positions and the submission route with the counselor '
                    'and Reserve retention office.'],
            'why': 'The counselor submits the Direct Affiliation Program request with you.',
            'verify': 'Reserve career planner, Career Counselor and Reserve retention office (RAC-3): '
                      'confirm Selected Marine Corps Reserve (SMCR) or Individual Mobilization Augmentee '
                      '(IMA) options and the Direct Affiliation Program submission route.',
            'owner': 'You'},
 'dap-billet': {'label': 'Choose your Reserve job',
                'brief': 'Choose an available Reserve job with your counselor and check the position in your '
                         'actual affiliation approval.',
                'how': ['Ask your career counselor which Reserve jobs are available at your preferred unit.',
                        'Review the job, unit and requirements before choosing a billet, the military '
                        'position you will fill.',
                        'Confirm the assignment in the actual Direct Affiliation Program approval. A '
                        'preference alone does not guarantee the position.'],
                'why': 'Guaranteed once Direct Affiliation Program is approved.',
                'verify': 'Reserve career planner, Career Counselor and Reserve retention office (RAC-3): '
                          'confirm billet availability and the assignment guaranteed by actual Direct '
                          'Affiliation Program approval.',
                'owner': 'You'},
 'dap-bonus': {'label': 'Read your Reserve incentive terms',
               'brief': 'An affiliation incentive carries a service obligation. Read the offered terms with '
                        'your counselor.',
               'how': ['Ask your career counselor for the written terms of any offered Reserve affiliation '
                       'incentive.',
                       'Have the counselor check current incentive information in the Total Force Retention '
                       'System (TFRS).',
                       'Confirm eligibility, the offered amount and required service obligation with the '
                       'Reserve retention office before accepting.'],
               'why': 'Bonuses carry a service obligation. Read the terms.',
               'verify': 'Career Counselor and Reserve retention office (RAC-3): confirm the offered '
                         'incentive, eligibility and its service obligation before acceptance.',
               'owner': 'Career Counselor'},
 'dap-package': {'label': 'Prepare your Reserve affiliation package',
                 'brief': 'Get the document list from your career counselor, gather the package and review '
                          'the correct submission window.',
                 'how': ['Ask your career counselor for the Direct Affiliation Program package requirements.',
                         'Confirm your chosen Reserve position and gather the documents the counselor '
                         'requests.',
                         'Review completeness and the applicable officer or enlisted submission window with '
                         'the counselor and Reserve retention office.'],
                 'why': 'Have the billet choice and the request ready before the window opens, so it goes in '
                        'on the first day.',
                 'verify': 'Career Counselor and Reserve retention office (RAC-3): check package '
                           'completeness against the applicable officer or enlisted Direct Affiliation '
                           'Program window.',
                 'owner': 'You'},
 'dap-request-o': {'label': 'Submit your officer Reserve affiliation request',
                   'brief': 'Submit through your career counselor within the confirmed officer affiliation '
                            'window.',
                   'how': ['Ask your career counselor to submit your officer Direct Affiliation Program '
                           'request when the window opens.',
                           'Confirm eligibility and the 180-to-60-day window before your end of active '
                           'service. The board targets day 180.',
                           'Keep confirmation of submission and check your separate Reserve commission '
                           'approval before departure.'],
                   'why': 'The officer window opens 180 days out and closes 60 days out. Submit on the first '
                          'day.',
                   'verify': 'Career Counselor and Reserve retention office (RAC-3): confirm officer '
                             'eligibility and submit within the 180-to-60-day window. Day 180 is the board '
                             'target.',
                   'owner': 'You'},
 'dap-request-e': {'label': 'Submit your enlisted Reserve affiliation request',
                   'brief': 'Submit through your career counselor within the confirmed enlisted affiliation '
                            'window.',
                   'how': ['Ask your career counselor to submit your enlisted Direct Affiliation Program '
                           'request when the window opens.',
                           'Confirm eligibility and the 180-to-30-day window before your end of active '
                           'service. The board targets day 180.',
                           'Keep confirmation of submission and check the decision with your counselor.'],
                   'why': 'The enlisted window opens 180 days out and closes 30 days out. Submit on the '
                          'first day.',
                   'verify': 'Career Counselor and Reserve retention office (RAC-3): confirm enlisted '
                             'eligibility and submit within the 180-to-30-day window. Day 180 is the board '
                             'target.',
                   'owner': 'You'},
 'dap-commission': {'label': 'Check your Reserve commission approval',
                    'brief': 'Have the personnel office confirm your Reserve commission decision in the '
                             'official record before departure.',
                    'how': ['Ask your installation personnel office and Reserve officer appointments desk '
                            '(RAM-1) to check commission approval.',
                            'Have them confirm the planned separation code in the Marine Corps Total Force '
                            'System (MCTFS).',
                            'Keep appointment approval separate from resignation approval and request '
                            'receipt. No Reserve commission approval before end of active service means no '
                            'Direct Affiliation Program.'],
                    'why': 'Reserve Affairs does not notify you. Approval shows as the planned separation '
                           'code in Marine Corps Total Force System (MCTFS). Check monthly. No approval '
                           'before end of active service means no Direct Affiliation Program.',
                    'verify': 'Reserve officer appointments desk (RAM-1) and Installation Personnel '
                              'Administration Center: confirm Reserve commission approval and the Marine '
                              'Corps Total Force System (MCTFS) separation code before end of active '
                              'service.',
                    'owner': 'Reserve Affairs'},
 'dap-763': {'label': 'Get your Reserve commission record signed',
             'brief': 'Get the appointment record signed before separation, then confirm it was returned and '
                      'filed.',
             'how': ['Ask your installation personnel office for NAVMC Form 763, Appointment Acceptance and '
                     'Record.',
                     'Arrange signature by an administering officer higher in grade than you before '
                     'separation.',
                     'Return the signed record and confirm upload to your Official Military Personnel File.'],
             'why': 'The legal record of your Reserve commission. An administering officer senior to you '
                    'signs it before you separate.',
             'verify': 'Installation Personnel Administration Center and higher-grade administering officer: '
                       'confirm issue, signature, return and Official Military Personnel File upload before '
                       'separation.',
             'owner': 'Personnel office'},
 'dap-checkin': {'label': 'Check in to your Reserve unit',
                 'brief': 'Arrange check-in with your gaining Reserve unit. Confirm the location, documents '
                          'and required date.',
                 'how': ['Contact your gaining Reserve unit or detachment to arrange check-in.',
                         'Confirm the location, documents and check-in date with the unit administration '
                         'office.',
                         'Check in within 30 calendar days after end of active service. Keep confirmation '
                         'and ask your career counselor about any problem before the deadline.'],
                 'why': 'Miss it and you can be moved to the Individual Ready Reserve (IRR) and lose Direct '
                        'Affiliation Program benefits.',
                 'verify': 'Gaining Selected Marine Corps Reserve (SMCR)/Individual Mobilization Augmentee '
                           '(IMA) administration and Reserve career planner: confirm check-in within 30 '
                           'calendar days after end of active service.',
                 'owner': 'You'},
 'lv-ledger': {'label': 'Enter your current leave balance',
               'brief': 'Use the closing leave balance from your latest pay statement as the starting point '
                        'for your leave plan.',
               'how': ['Open your latest Leave and Earnings Statement (LES) and find the closing leave '
                       'balance.',
                       'Enter the balance and statement date in the leave planner.',
                       'Update the balance each month from your latest pay statement.'],
               'why': 'The leave planner needs your actual balance. Update it from your pay statement each '
                      'month.',
               'verify': None,
               'owner': 'You or a family member helping with the plan'},
 'lv-plan': {'label': 'Plan your remaining leave',
             'brief': 'Choose your desired final leave balance, then have the personnel and pay offices '
                      'check selling leave or requesting advance leave.',
             'how': ['Decide how much leave you want to use and what balance you want at the end of active '
                     'duty.',
                     'Enter planned leave blocks and review the projected balance.',
                     'Ask your personnel and pay offices to confirm any leave sale, prior sales and '
                     'exception to the 60-day career cap.',
                     'If the projection goes negative, ask about advance-leave eligibility and command '
                     'approval. A projection does not authorize leave you have not earned.'],
             'why': 'The desired final balance is your planning choice. Sellback depends on honorable '
                    'separation, prior sales and any chapter 2, 2.b exception to the 60-day career cap. A '
                    'projected negative balance does not authorize advance leave. Confirm the urgent, '
                    'personal or emergency purpose, limits and commanding officer (CO) approval. A negative '
                    'balance at discharge becomes excess leave subject to collection from pay.',
             'verify': 'Installation Personnel Administration Center, disbursing and commanding officer '
                       '(CO): confirm qualifying sellback, prior sales, any cap exception and advance-leave '
                       'purpose, limits and approval.',
             'owner': 'You'},
 'lv-terminal': {'label': 'Confirm your final leave dates',
                 'brief': 'Review approved terminal leave and administrative absence dates with the '
                          'personnel office, including the separation requirements that come first.',
                 'how': ['Ask your installation personnel office to confirm the terminal leave and '
                         'administrative absence dates already requested.',
                         'Check that the advance separation request included dates, duration and planned '
                         'departure. Have the office verify 120 days plus desired leave and permissive '
                         'temporary additional duty (PTAD).',
                         'Before the first absence, confirm complete medical record acceptance and all '
                         'separation requirements with the personnel office, medical records and command. '
                         "The board's 90-day date is a final planning target."],
                 'why': 'Supply desired leave/permissive temporary additional duty (PTAD) dates, duration '
                        'and planned detachment date with the advance separation request. The manual says to '
                        'allow 120 days plus desired leave/PTAD lead time. The 90-day board date is a final '
                        'planning confirmation target. Confirm Service Treatment Record acceptance and all '
                        'separation requirements before the first applicable absence.',
                 'verify': 'Installation Personnel Administration Center (IPAC) and Marine Corps separation '
                           'and retirement desk (MMSR-2): confirm the earlier separation request and '
                           'leave/permissive temporary additional duty (PTAD) lead time. IPAC, medical '
                           'records and commanding officer (CO): confirm Service Treatment Record '
                           'acceptance, all separation gates and approved absence dates.',
                 'owner': 'You'},
 'lv-requests': {'label': 'Submit each leave request',
                 'brief': 'Submit each planned leave block in Marine Online and confirm command approval.',
                 'how': ['Enter each leave block in Marine Online (MOL).',
                         'Check dates against the full absence plan before submitting.',
                         'Confirm your commanding officer approved each request before relying on it.'],
                 'why': 'Each block approved by the commanding officer (CO).',
                 'verify': None,
                 'owner': 'You'},
 'lv-risk-r': {'label': 'Recheck leave after resignation approval',
               'brief': 'Recalculate leave if the approved resignation date differs from your request.',
               'how': ['Ask your installation personnel office to confirm the approved resignation date.',
                       'Compare it with the requested date and update your board profile if needed.',
                       'Review leave projections with the personnel and pay offices before changing '
                       'requests.'],
               'why': 'The Director, Manpower Management can approve a different date. Watch the approval.',
               'verify': 'Installation Personnel Administration Center, Marine Corps separation and '
                         'retirement desk (MMSR-2) and disbursing: confirm the approved resignation date and '
                         'recalculate leave if it differs from the request.',
               'owner': 'You'},
 'lv-risk-t': {'label': 'Recheck leave after retirement approval',
               'brief': 'Your approved retirement action date may differ from your request. Check it before '
                        'relying on leave projections.',
               'how': ['Ask your installation personnel office to confirm the approved retirement or Fleet '
                       'Marine Corps Reserve (FMCR) date.',
                       'Compare it with the requested date and update your profile if needed.',
                       'Review leave projections with the personnel and pay offices before changing '
                       'requests.'],
               'why': 'The Director, Manpower Management can approve a different date. Watch the approval.',
               'verify': 'Installation Personnel Administration Center, Marine Corps separation and '
                         'retirement desk (MMSR-2) and disbursing: confirm the approved retirement or Fleet '
                         'Marine Corps Reserve (FMCR) date and recalculate leave if it differs from the '
                         'request.',
               'owner': 'You'},
 'lv-final': {'label': 'Check your final leave balance',
              'brief': 'Check your final pay statement for the leave balance you expected and ask the pay '
                       'office about any difference.',
              'how': ['Review the leave balance on your final Leave and Earnings Statement (LES).',
                      'Compare it with the leave entry on DD Form 214 and your approved leave records.',
                      'Ask your personnel or pay office to resolve any difference or leave debt.'],
              'why': 'Check the last Leave and Earnings Statement (LES) and the DD-214 leave block.',
              'verify': None,
              'owner': 'You'},
 'lv-tsp': {'label': 'Check your retirement savings login',
            'brief': 'Confirm you can access your retirement savings account before leaving active duty.',
            'how': ['Sign in to your Thrift Savings Plan (TSP) account.',
                    'Confirm you can access the account and keep your login recovery information secure.',
                    'If joining the Reserves, ask the pay office how drill pay contributions will work.'],
            'why': 'Your retirement savings account remains after active duty. Confirm access now and ask '
                   'the pay office about any future Reserve contributions.',
            'verify': None,
            'owner': 'You'},
 'fam-tamp': {'label': 'Confirm your transitional health coverage',
              'brief': 'Ask the benefits office to confirm whether you and each eligible family member '
                       'qualify for transitional coverage and its actual dates.',
              'how': ['Ask your personnel and TRICARE benefits offices whether the Transitional Assistance '
                      'Management Program (TAMP) applies to your family.',
                      'For qualifying Selected Reserve affiliation without a break in service, confirm the '
                      'award of 180 days of premium-free coverage.',
                      "Check each family member's eligibility and actual start and end dates in the Defense "
                      'Enrollment Eligibility Reporting System (DEERS). A Reserve profile choice does not '
                      'prove coverage.'],
              'why': 'Marine administrative message (MARADMIN) 454/26 describes 180 days of premium-free '
                     'Transitional Assistance Management Program (TAMP) for qualifying Selected Reserve '
                     'affiliation without a break in service. Confirm the award and actual start/end dates; '
                     'the Reserve profile choice does not prove coverage.',
              'verify': 'Installation Personnel Administration Center, Defense Enrollment Eligibility '
                        'Reporting System (DEERS) and TRICARE: confirm Transitional Assistance Management '
                        'Program (TAMP) qualifying status, award and actual sponsor/dependent coverage '
                        'dates.',
              'owner': 'You and spouse'},
 'fam-trs': {'label': 'Arrange coverage after transitional benefits',
             'brief': "Confirm your family's next health plan before transitional coverage ends.",
             'how': ['Ask TRICARE whether you and your family qualify for TRICARE Reserve Select after '
                     'transitional coverage ends.',
                     "Confirm the Transitional Assistance Management Program (TAMP) end date, each person's "
                     'enrollment steps and the actual new coverage start.',
                     'Check family records with the Defense Enrollment Eligibility Reporting System (DEERS) '
                     'office and keep enrollment confirmation. Day 170 is a planning target, not a coverage '
                     'promise.'],
             'why': 'Eligible Selected Reserve Marines may enroll in TRICARE Reserve Select after '
                    'Transitional Assistance Management Program (TAMP) coverage. Confirm eligibility, '
                    'enrollment and the actual start date for each family member with TRICARE. Day 170 is a '
                    'planning target, not a coverage promise.',
             'verify': 'Confirm with TRICARE, the Defense Enrollment Eligibility Reporting System (DEERS) '
                       'office and your personnel office: transitional coverage end, TRICARE Reserve Select '
                       "eligibility, each family member's enrollment and the actual new coverage date.",
             'owner': 'You and spouse'},
 'fam-chcbp': {'label': 'Confirm coverage after active duty',
               'brief': "Ask the benefits office when each family member's active-duty coverage ends and "
                        'which replacement plans they can use.',
               'how': ['Ask your personnel and TRICARE benefits offices when coverage ends for you, your '
                       'spouse and children.',
                       'Confirm whether the Transitional Assistance Management Program (TAMP) or Continued '
                       'Health Care Benefit Program (CHCBP) applies to each person.',
                       'Ask about eligibility, duration, cost and enrollment deadline. Keep confirmation of '
                       'the replacement coverage and its effective date.'],
               'why': 'Your family needs a coverage plan for the day active-duty coverage ends. Eligibility '
                      "and enrollment dates depend on each person's status.",
               'verify': 'Installation Personnel Administration Center, Defense Enrollment Eligibility '
                         'Reporting System (DEERS)/TRICARE and Continued Health Care Benefit Program (CHCBP) '
                         'contractor: confirm all Transitional Assistance Management Program (TAMP) '
                         "categories, each person's CHCBP eligibility, duration and actual enrollment "
                         'deadline.',
               'owner': 'You and spouse'},
 'fam-tricare-ret': {'label': "Plan your family's retirement coverage",
                     'brief': 'You, your eligible spouse and children can continue TRICARE through retiree '
                              'enrollment. Call your regional contractor to confirm the change in plans, '
                              'costs and coverage dates.',
                     'how': ['Call your regional TRICARE contractor to plan retiree enrollment for you, your '
                             'eligible spouse and children.',
                             'Review https://www.tricare.mil/LifeEvents/Retiring together. Active-duty '
                             'enrollment does not simply carry over; confirm plan choices, costs, effective '
                             'dates and enrollment deadlines for each person.',
                             'Find your regional contractor at https://www.tricare.mil/ContactUs/CallUs and '
                             'ask how to avoid a gap. Ask about existing referrals, prescriptions and any '
                             'unpaid claims.',
                             'Update retirement status and family records in the Defense Enrollment '
                             'Eligibility Reporting System (DEERS), arrange required identification cards '
                             'and keep enrollment confirmation. Either partner can help prepare the '
                             'questions.'],
                     'why': 'Retirement changes enrollment and costs for you and your family. Eligible '
                            'spouses and children can remain covered through retiree TRICARE enrollment. The '
                            "board's 30-day preparation date is a planning target; confirm actual deadlines "
                            'with your regional contractor.',
                     'verify': 'Confirm eligibility, enrollment deadlines, coverage dates and costs for each '
                               'person with your TRICARE contractor. Ask the Defense Enrollment Eligibility '
                               'Reporting System (DEERS) office to check retirement status and family '
                               'records.',
                     'owner': 'You and your family'},
 'fam-fedvip': {'label': 'Check your retirement dental options',
                'brief': 'Retirement dental coverage needs its own decision. Ask the benefits office about '
                         'family eligibility, enrollment and costs.',
                'how': ['Ask the TRICARE dental benefits office about the Federal Employees Dental and '
                        'Vision Insurance Program (FEDVIP).',
                        'Confirm eligibility for you and each family member, the enrollment office, window, '
                        'premium and effective date.',
                        "Compare the new plan with when active-duty family dental coverage ends. The board's "
                        '30-day date is a preparation target.'],
                'why': 'Retirement dental coverage needs its own enrollment decision. Ask the benefits '
                       "office to confirm your family's options, actual deadlines and coverage dates.",
                'verify': 'TRICARE dental benefits office: confirm coverage transition and Federal Employees '
                          'Dental and Vision Insurance Program (FEDVIP) eligibility, enrollment window, '
                          'premium and effective date with the enrollment office it identifies.',
                'owner': 'You and spouse'},
 'ret-id': {'label': 'Update retirement cards and family records',
            'brief': 'Arrange required identification card updates for you, your eligible spouse and '
                     'children with the card office.',
            'how': ['Contact your identification card office to arrange retirement card updates for eligible '
                    'family members.',
                    'Confirm the approved retirement or Fleet Marine Corps Reserve (FMCR) status with your '
                    'personnel office.',
                    "Check each person's record in the Defense Enrollment Eligibility Reporting System "
                    '(DEERS). Ask which documents to bring and who must attend.',
                    'Confirm the record changes and required cards. The next-day date on the board is a '
                    'planning target.'],
            'why': 'Confirm the identification card actions for the approved retirement or Fleet Marine '
                   "Corps Reserve (FMCR) status and keep each family member's Defense Enrollment Eligibility "
                   'Reporting System (DEERS) information current. The next-day date is a planning target.',
            'verify': 'Installation Personnel Administration Center and Defense Enrollment Eligibility '
                      'Reporting System (DEERS): confirm the approved retirement or Fleet Marine Corps '
                      'Reserve (FMCR) status and the required identification card updates for each eligible '
                      'family member.',
            'owner': 'You and spouse'},
 'fam-dental-tdp': {'label': 'Check Reserve and family dental coverage',
                    'brief': 'Have the dental benefits office check your coverage and each family member’s '
                             'coverage separately.',
                    'how': ['Ask the TRICARE dental benefits office what dental coverage you and each family '
                            'member can use.',
                            'Confirm any Transitional Assistance Management Program (TAMP) dental '
                            'eligibility and when the sponsor can start the TRICARE Dental Program (TDP).',
                            'Ask whether current family enrollment continues, what premiums apply and when '
                            'replacement coverage starts. Check family records with the Defense Enrollment '
                            'Eligibility Reporting System (DEERS) office.'],
                    'why': 'Sponsor and family dental coverage can have different requirements. Ask the '
                           'benefits office to confirm enrollment, premiums and actual coverage dates for '
                           'each person.',
                    'verify': 'TRICARE dental benefits office and Defense Enrollment Eligibility Reporting '
                              'System (DEERS): confirm Transitional Assistance Management Program (TAMP) '
                              'dental eligibility, sponsor TRICARE Dental Program (TDP) start, family '
                              'continuation, enrollment and premiums separately.',
                    'owner': 'You and spouse'},
 'fam-dental-civ': {'label': 'Arrange your civilian dental coverage',
                    'brief': 'Line up replacement dental coverage for anyone who needs it. Your clinic can '
                             'confirm when military coverage ends.',
                    'how': ['Ask your dental clinic when coverage ends for you and each family member.',
                            'Compare available replacement plans, costs and effective dates with your '
                            'family.',
                            'Keep enrollment confirmation and ask the benefits office to resolve any gap.'],
                    'why': 'Active duty dental coverage ends with your service.',
                    'verify': 'Your dental clinic: when does coverage end for you and your family?',
                    'owner': 'You and spouse'},
 'fam-id': {'label': 'Check your family records and cards',
            'brief': 'Review family benefit records with the identification card office and ask what changes '
                     'when active duty ends.',
            'how': ["Ask your identification card office to review your family's Defense Enrollment "
                    'Eligibility Reporting System (DEERS) records.',
                    "Confirm the separation date and each family member's status and required card changes.",
                    'Ask which documents to bring and who must attend. Check that the changes were '
                    'recorded.'],
            'why': "The family's status changes at your date.",
            'verify': 'Confirm with the identification card office which family records and cards must '
                      'change when active duty ends.',
            'owner': 'You and spouse'},
 'fam-sgli': {'label': 'Confirm your life insurance options',
              'brief': 'Ask the veterans insurance office which continuation or conversion rules apply '
                       'before choosing coverage for your family.',
              'how': ['Ask the Department of Veterans Affairs (VA) insurance office to confirm your '
                      'applicable insurance deadline.',
                      "Review Servicemembers' Group Life Insurance (SGLI) continuation and Veterans' Group "
                      'Life Insurance (VGLI) conversion options, including any Ready Reserve coverage.',
                      'Have the office resolve the 120/240-day source difference, proof-of-health '
                      'requirement and combined coverage maximum before choosing amounts. Day 120 on the '
                      'board is a planning target.'],
              'why': 'Your family needs a clear life insurance decision before coverage changes. The guide '
                     'and older manual print different proof-of-health windows; the veterans insurance '
                     'office must confirm the rule for your case. The guide gives 240 days without proof of '
                     'good health for eligible insured Marines; the manual prints 120 days. Ask the '
                     'insurance office which applies.',
              'verify': "Department of Veterans Affairs (VA) Insurance/Office of Servicemembers' Group Life "
                        'Insurance (OSGLI) and Reserve personnel office: confirm governing deadline, '
                        "individual eligibility, Servicemembers' Group Life Insurance (SGLI) continuation "
                        "and the combined SGLI/Veterans' Group Life Insurance (VGLI) maximum before choosing "
                        'coverage.',
              'owner': 'You'},
 'fam-teb': {'label': 'Check your education transfer obligation',
             'brief': 'Confirm that you completed the service obligation tied to transferring education '
                      'benefits to your family.',
             'how': ['Ask your education office to confirm the end date of your GI Bill benefit-transfer '
                     'service obligation.',
                     'Compare that date with your planned service end date.',
                     'Resolve any difference with the education office before relying on the transfer for '
                     'your spouse or children.'],
             'why': 'A transfer carries a service obligation. Leaving before it is done cancels the '
                    'transfer.',
             'verify': 'Education office: confirm the transfer obligation end date.',
             'owner': 'You'},
 'fam-hhg-counsel': {'label': 'Arrange your final move counseling',
                     'brief': 'Call your installation moving office about your final household move and '
                              'bring your orders, destination and requested dates.',
                     'how': ['Call your installation Distribution Management Office (DMO) or Transportation '
                             'Management Office (TMO) for final move counseling.',
                             'Bring your separation, retirement or Fleet Marine Corps Reserve (FMCR) orders, '
                             'destination and requested move dates.',
                             'Record the confirmed visit on "Record your move counseling appointment". The '
                             '90-day preparation date is a planning target.',
                             'Ask the moving office about shipment eligibility, weight, destination, excess '
                             'costs and storage. Keep its actual shipment and storage limits on the separate '
                             'move-limits task.'],
                     'why': 'Your installation moving office confirms the final move your orders authorize. '
                            'The board targets counseling 90 days before your separation or retirement date; '
                            'the office confirms the actual appointment.',
                     'verify': 'Installation Distribution Management Office (DMO)/Transportation Management '
                               'Office (TMO): confirm the counseling appointment and your orders-based final '
                               'move entitlement.',
                     'owner': 'You'},
 'fam-hhg-appt': {'label': 'Record your move counseling appointment',
                  'brief': 'Save the confirmed date for your installation moving-office visit.',
                  'how': ['Ask your installation moving office to confirm your final move counseling '
                          'appointment.',
                          'Record the actual confirmed date here and ask what to bring.',
                          'Leave it undated until confirmed; keep the preparation target and shipment '
                          'expiration on their separate tasks.'],
                  'why': 'Record the actual counseling appointment separately from the planning target and '
                         'shipment expiration.',
                  'verify': 'Installation Distribution Management Office (DMO)/Transportation Management '
                            'Office (TMO): confirm the actual appointment.',
                  'owner': 'You'},
 'fam-hhg-entitlement': {'label': 'Confirm your move and storage limits',
                         'brief': 'Get your shipment and storage deadlines from the installation moving '
                                  'office in writing; they have separate limits.',
                         'how': ['Ask your installation moving office to confirm the final move your orders '
                                 'authorize and its exact deadline.',
                                 'Confirm the applicable Joint Travel Regulations (JTR) category, '
                                 'destination, weight allowance, excess costs and any exception.',
                                 'For ordinary separation, ask about the 180-day application limit and '
                                 'timely written-request requirement. For qualifying retirement or Fleet '
                                 'Marine Corps Reserve (FMCR) transfer, confirm the 3-year turnover limit '
                                 'and any exception.',
                                 'Confirm the separate storage expiration and costs. Record any '
                                 'office-confirmed fixed shipment deadline here and storage date in notes. '
                                 'Keep required receipts after shipment.',
                                 'Ask the moving office to check the separate non-temporary storage limit: '
                                 'Table 5-52 ends storage 1 year from active-duty termination unless an '
                                 'exception applies. Confirm any costs after expiration.'],
                         'why': 'Your shipment entitlement and time limit require Distribution Management '
                                'Office (DMO)/Transportation Management Office (TMO) confirmation against '
                                'your orders and active-duty termination date. For ordinary separation under '
                                'Joint Travel Regulations (JTR) 052012, the authorized destination is home '
                                'of record (HOR) or place last entered active duty (PLEAD), within 180-day '
                                'authority and a timely written-request provision. For qualifying retirement '
                                'or Fleet Marine Corps Reserve (FMCR) under JTR 052013, home of selection '
                                '(HOS) authority requires turnover within 3 years for termination dates on '
                                'or after 24 JUN 2022, subject to exceptions. DMO/TMO must confirm the '
                                'separate storage expiration.',
                         'verify': 'Installation Distribution Management Office (DMO)/Transportation '
                                   'Management Office (TMO): confirm the applicable Joint Travel Regulations '
                                   '(JTR) category, shipment entitlement, destination, weight, exact time '
                                   'limit, storage expiration and any extension approval.',
                         'owner': 'You'},
 'fam-va-dental-iv': {'label': 'Check your veterans dental benefit',
                      'brief': 'Ask the veterans dental clinic whether your disability decision qualifies '
                               'you for Class IV dental care.',
                      'how': ['Ask the Department of Veterans Affairs (VA) dental eligibility office to '
                              'review your disability decision.',
                              'Confirm whether a qualifying 100 percent service-connected rating or '
                              'individual unemployability at that payment rate qualifies you for Class IV.',
                              'Permanence is not required for this class; a temporary 100 percent rating '
                              'does not qualify. Ask the clinic to confirm before relying on the benefit.'],
                      'why': 'A qualifying 100 percent service-connected rating or individual '
                             'unemployability paid at the 100 percent rate may qualify you for any needed '
                             'dental care. Permanence is not required. A temporary 100 percent rating does '
                             'not qualify for Class IV.',
                      'verify': 'Department of Veterans Affairs (VA) dental clinic eligibility office: '
                                'confirm Class IV eligibility and the temporary-rating exclusion.',
                      'owner': 'You'},
 'fam-champva': {'label': 'Check whether family veterans coverage applies',
                 'brief': 'Retiree families use TRICARE. For other families, ask the veterans benefits '
                          'office to confirm eligibility for its separate family health benefit.',
                 'how': ['Retiree families use TRICARE. Ask the veterans family-benefits office to review a '
                         'permanent and total disability decision.',
                         'Review the eligibility information at '
                         'https://www.va.gov/family-and-caregiver-benefits/health-and-disability/champva/ '
                         'and ask the office to confirm your family relationship and disability decision.',
                         'Check TRICARE eligibility with your benefits office before applying; anyone '
                         'eligible for TRICARE cannot receive this separate benefit.'],
                 'why': 'Retiree families use TRICARE. The Civilian Health and Medical Program of the '
                        'Department of Veterans Affairs (CHAMPVA) is for some families of veterans the '
                        'agency rates as permanently and totally disabled. The agency decides eligibility.',
                 'verify': 'Confirm family eligibility with the Department of Veterans Affairs (VA). Its '
                           'guidance describes permanent and total disability as 100 percent disabling and '
                           'not expected to improve. Ask the office to interpret your actual decision; '
                           'confirm the TRICARE exclusion with your benefits office.',
                 'owner': 'You'},
 'fam-will': {'label': 'Arrange your will and legal authority',
              'brief': 'Ask base legal to review your will and any power of attorney your family needs '
                       'before leaving active duty.',
              'how': ['Contact base legal to arrange a will and power of attorney appointment.',
                      'Discuss with your family who may act for you and which documents need review.',
                      'Ask legal what to bring and keep the completed documents where the people you name '
                      'can find them.'],
              'why': 'Base legal can help with your will and power of attorney while you are on active duty. '
                     'Ask what documents and appointments your family needs.',
              'verify': None,
              'owner': 'You and spouse'},
 'fam-budget': {'label': "Plan your family's new budget",
                'brief': 'Build a family budget using income and benefit decisions that are actually '
                         'approved.',
                'how': ['List your expected household expenses and confirmed income after active duty.',
                        'Count retired pay, Reserve drill pay, veterans compensation and civilian pay only '
                        'as each is approved.',
                        'Review coverage costs and any gap before the first payment with your family. Update '
                        'the plan when an amount or start date is confirmed.'],
                'why': 'No active duty pay after the date. Count retired pay, drill pay, Department of '
                       'Veterans Affairs (VA) compensation and civilian pay only as each one is approved.',
                'verify': None,
                'owner': 'You and spouse'},
 'cmd-plan': {'label': 'Agree who takes your job',
              'brief': 'Settle with your commander who takes over your duties and when.',
              'how': ['Ask your commanding officer who will replace you and when to hand over your duties.',
                      'Compare the handoff with your leave and any SkillBridge absence.',
                      'Record the person, dates and duties that need coverage.'],
              'why': 'Settle it early; it shapes your leave and any SkillBridge cover plan.',
              'verify': 'Confirm with your commanding officer who takes over your duties and when.',
              'owner': 'Commanding officer'},
 'cmd-award': {'label': 'Check your final report and award',
               'brief': 'Ask your command about the final performance report and any end-of-tour award early '
                        'enough to resolve missing work.',
               'how': ['Ask your commanding officer or unit personnel section about your final performance '
                       'report and any end-of-tour award.',
                       'Confirm who prepares each document and whether it has been submitted.',
                       'Follow up on missing information before checkout.'],
               'why': 'Your command confirms the final report and any award requirements. Ask early so there '
                      'is time to resolve missing information.',
               'verify': 'Confirm with your commander and unit personnel section whether the final report '
                         'and any award were submitted.',
               'owner': 'Commanding officer'},
 'cmd-binder': {'label': 'Prepare your handoff notes',
                'brief': 'Write down the routines, open actions and contacts your replacement will need on '
                         'the first day.',
                'how': ['Prepare handoff notes for the person taking over your duties.',
                        'Include recurring duties, open actions, contacts and accounts they will need.',
                        'Review the notes together and follow unit procedures for account access; do not '
                        'include passwords.'],
                'why': 'What your relief needs on day one.',
                'verify': None,
                'owner': 'You'},
 'cmd-turnover': {'label': 'Meet with your replacement',
                  'brief': 'Arrange time with the person taking over your job to walk through duties, open '
                           'actions and contacts.',
                  'how': ['Agree on handoff dates with the person replacing you.',
                          'Walk through your handoff notes, recurring duties, open actions and key contacts '
                          'together.',
                          'Record any remaining questions and who will resolve them before you leave.'],
                  'why': 'A direct handoff helps your replacement take over the job. Confirm the meeting '
                         'dates and required preparation together.',
                  'verify': 'Your relief: dates that work.',
                  'owner': 'You'},
 'cmd-checkout': {'label': 'Complete your unit checkout sheet',
                  'brief': 'Get the unit checklist and finish each required stop before final checkout.',
                  'how': ['Ask your installation personnel office for the unit checkout sheet and required '
                          'completion date.',
                          'Complete the listed equipment, library, armory, account and travel-card checks.',
                          'Confirm the unit accepted the completed sheet before final checkout.'],
                  'why': 'The formal checkout.',
                  'verify': 'Installation Personnel Administration Center: the unit checkout sheet.',
                  'owner': 'You'}}
