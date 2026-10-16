"""Row labels and card briefs for the complete seed, including conditional items.

Reader: Marines leaving active duty and their families. Audience: mil-public.
Existing titles, instructions, date rules and source quotes stay in the drawer.
"""

COPY = {
    "sep-tell": {
        "label": "Tell your CO your plan",
        "brief": "Your CO handles your request, SkillBridge endorsement, and billet cover. Tell them your plan early so those steps can be arranged together.",
    },
    "sep-ic": {
        "label": "Complete your initial counseling",
        "brief": "Initial counseling starts the required transition sequence. Missing it leaves a required step unfinished and can keep you from starting SkillBridge.",
    },
    "sep-ic-appt": {
        "label": "Record your initial counseling appointment",
        "brief": "A confirmed appointment tells you when to attend initial counseling. Leaving it unset keeps your appointment separate from the rule deadline but gives you no visit date to plan around.",
    },
    "sep-presep": {
        "label": "Complete your separation counseling",
        "brief": "This required brief is part of your transition sequence. Missing it leaves a required step unfinished before separation or SkillBridge.",
    },
    "sep-presep-appt": {
        "label": "Record your separation counseling appointment",
        "brief": "Your confirmed counseling appointment gives you a visit date to plan around. The rule deadline alone does not tell you when the brief will happen.",
    },
    "sep-trs": {
        "label": "Complete your transition workshops",
        "brief": "These workshops are required before Capstone and command verification. Leaving them unfinished breaks that sequence and can keep you from starting SkillBridge.",
    },
    "sep-trs-appt": {
        "label": "Record your transition workshop appointment",
        "brief": "A confirmed workshop appointment helps you plan the required transition sequence. Without it, the board shows a rule deadline but no confirmed time to attend.",
    },
    "sep-roob": {
        "label": "Finish ROOB before counseling",
        "brief": "ROOB is prework for your initial counseling. Confirm the certificate with the TRP office so you arrive with the required prework complete.",
    },
    "sep-roob-ret": {
        "label": "Finish ROOB before retirement counseling",
        "brief": "Your retirement counseling needs ROOB prework. Check the certificate requirement with the TRP office so missing prework does not leave you unprepared for the appointment.",
    },
    "sep-dd2648": {
        "label": "Check your separation type and grade",
        "brief": "Your checklist must show your actual separation path and grade. A wrong entry needs correction and a DAP eligibility review; actual retirement makes you ineligible for DAP.",
    },
    "sep-capstone": {
        "label": "Complete your Capstone",
        "brief": "Capstone is a required step before command verification. Leaving it unfinished keeps your transition sequence incomplete and can block SkillBridge participation.",
    },
    "sep-capstone-appt": {
        "label": "Record your Capstone appointment",
        "brief": "A confirmed Capstone appointment helps you finish the required sequence. Without that date, you have a rule deadline but no confirmed visit to plan around.",
    },
    "sep-cv": {
        "label": "Get your command verification",
        "brief": "Command verification closes the required transition sequence. Missing it leaves a required step unfinished before separation or SkillBridge.",
    },
    "sep-cv-appt": {
        "label": "Record your command verification appointment",
        "brief": "Your confirmed appointment tells you when command verification will happen. Record it so you know when to attend; the rule deadline alone does not give you that visit date.",
    },
    "sep-ptad": {
        "label": "Confirm your transition PTAD",
        "brief": "An approved retirement date can qualify you for transition PTAD for house and job hunting. Confirm approval and its place before leave so you do not plan around an unapproved absence.",
    },
    "sep-dd214": {
        "label": "Review your DD-214 before signing",
        "brief": "Your worksheet records your service and separation details, including an entry used to check VA dental eligibility. Review it with IPAC before signing so errors can be caught during processing.",
    },
    "sep-checkout": {
        "label": "Confirm your final checkout day",
        "brief": "Your checkout plan must fit your departure or return after SkillBridge. Confirm it with IPAC so terminal leave starts only after all separation requirements are complete.",
    },
    "sep-eas": {
        "label": "Confirm your service end date",
        "brief": "Your service ends on the approved EAS, which can differ from checkout or departure. Confirm it with IPAC so you do not mistake an earlier departure for the end of active duty.",
    },
    "ret-day": {
        "label": "Confirm your retirement effective date",
        "brief": "Your approved retirement action and last active duty day are separate dates. Confirm both and your first payment so your claim and pay plans use the right dates.",
    },
    "ret-fmcr-day": {
        "label": "Confirm your FMCR transfer date",
        "brief": "An FMCR transfer needs its own approved date. Ask IPAC to confirm whether it applies so your retirement profile does not stand in for the actual transfer action.",
    },
    "sep-counsel": {
        "label": "Discuss your resignation with your CO",
        "brief": "Your CO must record your Reserve choice before submission. Confirm routing and timing with IPAC and MMSR-2 so conflicting published windows do not leave your request outside the accepted window.",
    },
    "sep-diary": {
        "label": "Confirm your resignation request was entered",
        "brief": "The unit diary reports your resignation date and Reserve choice. Ask IPAC and MMSR-2 to confirm timing and acceptance because published windows differ and the diary can reject a request outside its window.",
    },
    "sep-letter": {
        "label": "Confirm whether you need a letter",
        "brief": "A waiver or an unfavorable Reserve recommendation requires a resignation letter with command endorsement. Check with IPAC and MMSR-2 so a required letter is included and routed correctly.",
    },
    "sep-pcs": {
        "label": "Check PCS effects on your resignation",
        "brief": "PCS orders can prevent a resignation recommendation unless the cancellation exception applies. Contact your monitor and MMSR-2 promptly so you can confirm eligibility and avoid missing the submission deadlines.",
    },
    "sep-approval": {
        "label": "Confirm resignation approval and EAS",
        "brief": "Ask IPAC to confirm resignation approval and your recorded EAS. If you choose a Reserve commission, confirm its receipt and approval separately.",
    },
    "sep-orders": {
        "label": "Get your separation orders",
        "brief": "Your unit issues separation orders after approval posts. Confirm issuance with IPAC so you know whether the orders step is complete.",
    },
    "sep-modify": {
        "label": "Confirm your resignation change cutoff",
        "brief": "Your resignation date and separation leave start both affect the change cutoff. Confirm the earlier boundary with IPAC and MMSR-2 so a change request does not arrive too late.",
    },
    "ret-eligibility-e": {
        "label": "Check whether you can retire",
        "brief": "Your grade and years on the board do not prove retirement eligibility. Ask IPAC to check your service, obligations, and contract before you rely on a retirement date.",
    },
    "ret-limits-e15": {
        "label": "Check whether retirement is available",
        "brief": "Your published grade limit does not prove you have enough creditable service to retire. Ask IPAC to review prior service and any approved exception before relying on this plan.",
    },
    "ret-limits-e67": {
        "label": "Check your grade service limit",
        "brief": "Your actual grade sets the service limit that must be checked. Confirm it and any continued service approval with IPAC and the career planner before choosing a retirement date.",
    },
    "ret-limits-e89": {
        "label": "Confirm your allowed service length",
        "brief": "Your grade group alone does not establish how long you may serve. Confirm your actual grade and any continued service approval so your retirement plan does not assume extra time.",
    },
    "ret-obligations-e": {
        "label": "Check your remaining service obligations",
        "brief": "Tour, deployment, education, and grade obligations can change when you may leave. Review them with IPAC and MMSR-2 before submission so an unmet obligation does not conflict with your requested date.",
    },
    "ret-counsel-e": {
        "label": "Complete retirement counseling with your CO",
        "brief": "You and your CO must sign the retirement checklist before submission. Finish counseling and filing first so your request follows the required sequence.",
    },
    "ret-waiver-e": {
        "label": "Confirm any required retirement waiver",
        "brief": "A diary entry does not request an eligibility waiver. Ask IPAC and MMSR-2 to confirm any separate package so submission does not leave a required waiver unrequested.",
    },
    "ret-request-o": {
        "label": "Submit your retirement request",
        "brief": "HQMC must approve your retirement date after submission. Confirm the submission window with MMSR-2 and hold major commitments until approval so you do not rely on the requested date alone.",
    },
    "ret-request-e": {
        "label": "Submit your retirement or FMCR request",
        "brief": "Submission starts the process but does not approve your date. Confirm timing with MMSR-2 and hold major commitments until approval so your plans do not depend on an unapproved request.",
    },
    "ret-receipt-e": {
        "label": "Confirm your retirement request was received",
        "brief": "Diary acceptance and HQMC receipt are separate checks. Confirm both with IPAC and MMSR-2 so a submitted request is not mistaken for receipt or approval.",
    },
    "ret-pcs-e": {
        "label": "Check your FMCR PCS cancellation cutoff",
        "brief": "Canceling PCS orders for an FMCR request has a deadline tied to receipt. Contact IPAC and your monitor promptly so the request reaches MMSR-2 within the confirmed working day limit.",
    },
    "ret-report-e": {
        "label": "Report changes after your retirement request",
        "brief": "Status changes after submission require command notice to MMSR-2, even after approval. Tell IPAC and your command promptly so release instructions can be checked before you proceed.",
    },
    "ret-modify-e": {
        "label": "Confirm your retirement change cutoff",
        "brief": "Changing or canceling retirement requires separate correspondence and endorsements. Confirm the deadline and any added service obligation with MMSR-2 so a late request or unexpected obligation does not disrupt your plan.",
    },
    "ret-pcs": {
        "label": "Check your retirement PCS cancellation cutoff",
        "brief": "A retirement request involving PCS cancellation has a deadline counted from orders receipt. Confirm the working day calendar with your monitor and IPAC so the request reaches MMSR-2 in time.",
    },
    "ret-approval": {
        "label": "Confirm retirement approval and your date",
        "brief": "Only the approved action and date establish your release authority. Confirm them with IPAC and MMSR-2 so a request or pending flag is not mistaken for permission to leave.",
    },
    "ret-orders": {
        "label": "Get your retirement or FMCR orders",
        "brief": "Your orders must match the approved action and release date. Check them with IPAC so you use the right orders and still complete the separate transition requirements.",
    },
    "ret-sbp": {
        "label": "Choose your survivor benefit coverage",
        "brief": "Your survivor benefit election affects deductions from retired pay. Confirm DFAS receipt and any required spouse concurrence; without an election, full coverage is deducted automatically.",
    },
    "ret-pay": {
        "label": "Check your retired pay account",
        "brief": "DFAS uses your election form data to pay retired pay. Confirm receipt, direct deposit, and your myPay login so you can check the first payment and the account receiving it.",
    },
    "ret-ceremony": {
        "label": "Arrange your retirement ceremony",
        "brief": "Your ceremony date affects family travel plans. Settle the date and venue with your CO early so your family can plan around the event.",
    },
    "eas-orders": {
        "label": "Confirm your orders and checkout schedule",
        "brief": "IPAC supplies your EAS separation orders and checkout schedule. Confirm nothing is pending that extends you so you do not plan departure around a date that may change.",
    },
    "sb-coord": {
        "label": "Talk to your SkillBridge coordinator",
        "brief": "Your program hours and approval route need confirmation before selection. Ask the coordinator to check both daily and weekly requirements so you do not choose a program that requires return to the command.",
    },
    "sb-provider": {
        "label": "Choose a program and get accepted",
        "brief": "Your specific provider and program must be checked before you apply. Confirm approval, training format, and hours with the coordinator so an unsuitable program does not become your plan.",
    },
    "sb-ethics": {
        "label": "Complete your SkillBridge ethics course",
        "brief": "Ethics completion is required before packet submission and must remain valid for the actual start. Recheck it when dates change so an expired course does not leave a prerequisite unmet.",
    },
    "sb-ethics-validity": {
        "label": "Check your ethics course is valid",
        "brief": "The actual SkillBridge start determines whether your ethics course is still valid. Have the coordinator check the completion window so a changed start does not leave you with an expired prerequisite.",
    },
    "sb-cover": {
        "label": "Confirm who covers your billet",
        "brief": "Your billet cover plan needs the command's approval under the governing SkillBridge rules. Get the approval route and allowed absence in writing because the published rules differ.",
    },
    "sb-packet": {
        "label": "Submit your SkillBridge packet",
        "brief": "Your packet needs completed prerequisites and the correct approval route. Confirm the governing rules in writing with the coordinator and command so conflicting published limits do not become assumed approval.",
    },
    "sb-approval": {
        "label": "Get written SkillBridge approval",
        "brief": "Written command approval is required before you participate. Confirm approved dates and completed prerequisites before departure so a proposed start is not treated as permission to begin.",
    },
    "sb-sequence": {
        "label": "Confirm your full absence plan",
        "brief": "Your SkillBridge, PTAD, and leave must fit the rules your command applies. Get the total absence and sequence confirmed in writing because the published limits differ.",
    },
    "sb-account": {
        "label": "Set your unit contact schedule",
        "brief": "Your command must set an accountability plan during SkillBridge. Confirm the contact schedule before departure so you know how to meet that requirement while away.",
    },
    "sb-run": {
        "label": "Confirm you can begin SkillBridge",
        "brief": "Your approved program dates and completed prerequisites must be checked before participation. Confirm the governing absence rules with your command; you cannot extend obligated service to finish the program.",
    },
    "sb-start": {
        "label": "Plan your SkillBridge start",
        "brief": "A proposed start helps plan preparation while approval is pending. Replace it with the written approved dates and recheck prerequisites so targets are not treated as permission to depart.",
    },
    "sb-cert": {
        "label": "Take your funded certification exam",
        "brief": "Your program may cover a certification exam while you participate. Confirm the exam date and funding with the provider so you sit it before that coverage ends.",
    },
    "va-vso": {
        "label": "Choose an accredited VSO",
        "brief": "An accredited VSO helps prepare and file your claim at no cost. Confirm availability and appoint them on VA Form 21-22 so they can represent you during filing and afterward.",
    },
    "va-shpe": {
        "label": "Schedule your separation physical",
        "brief": "Your clinic must confirm that your separation exam meets the requirement. Schedule the physical or confirm acceptance of the completed VA assessment; a scheduled VA exam alone does not satisfy it.",
    },
    "va-records": {
        "label": "Keep complete copies of your records",
        "brief": "Your complete records support your claim and later reviews. Keep personal copies and confirm separate delivery to IPAC, since saving your own copies does not satisfy that delivery requirement.",
    },
    "va-service-end": {
        "label": "Confirm your last active duty day",
        "brief": "Your last active duty day projects from your entered date and sets the BDD window and transition deadlines. A confirmed date you set here replaces the projection.",
    },
    "va-str": {
        "label": "Deliver your complete service treatment record",
        "brief": "IPAC needs your complete service treatment record before the first applicable absence or separation action. Confirm delivery and acceptance so a personal export is not mistaken for completing this required step.",
    },
    "va-conditions": {
        "label": "List conditions for your claim",
        "brief": "Your VSO works from your condition list. Add every issue you want to discuss, including those missing from your records, so the list does not leave out a claim concern.",
    },
    "va-sickcall": {
        "label": "Get undocumented conditions seen at medical",
        "brief": "Medical visits put your conditions on record while you still serve. Waiting until after separation makes it much harder to connect a newly documented condition to your service.",
    },
    "va-hearing": {
        "label": "Get your hearing test on record",
        "brief": "Your separation hearing test provides a baseline for a hearing or tinnitus claim. Get it on record so that baseline is available for your claim.",
    },
    "va-exposure": {
        "label": "Record your deployment exposures",
        "brief": "Your exposure record should include every deployment and any missing events. Review it with your VSO and military medical before filing so missing exposures are brought to their attention.",
    },
    "va-bh": {
        "label": "Get behavioral health concerns on record",
        "brief": "A behavioral health evaluation records sleep, stress, and mood concerns during service. Describe their effect at work and home so those concerns are documented before you leave.",
    },
    "va-reserve": {
        "label": "Confirm your Reserve medical qualification",
        "brief": "Your claim needs review against Reserve medical standards before the DAP request. Discuss it with medical and the Career Counselor so qualification questions are settled before submission.",
    },
    "va-parta": {
        "label": "Complete your claim self assessment",
        "brief": "Your BDD claim must include the completed Part A self assessment. Confirm it is in the actual submission so a required part of your claim is not missing.",
    },
    "va-file": {
        "label": "File your BDD claim",
        "brief": "Filing starts the 45-day period when you must be available for VA exams. Confirm your separation date and filing window with your VSO so travel does not conflict with that requirement.",
    },
    "va-exams": {
        "label": "Keep time free for VA exams",
        "brief": "You must be available for VA exams after filing. Record your actual filing date and confirm the scheduled exams so you do not plan around the board's projected window.",
    },
    "va-add": {
        "label": "Confirm how to add claim conditions",
        "brief": "Adding conditions to an existing BDD claim needs VA confirmation. Ask about the procedure and actual deadline before the window closes so you do not rely on the board's planning target.",
    },
    "va-sha": {
        "label": "Confirm your completed assessment was returned",
        "brief": "A completed assessment can replace a separate SHPE only if the clinic confirms it meets the requirement. Confirm return to DoD and acceptance so an unfinished assessment is not treated as a completed exam.",
    },
    "va-intent": {
        "label": "Record your intent to file receipt",
        "brief": "An intent to file can protect a potential effective date when BDD is missed. Keep VA's actual receipt date so a planned date does not set the completed claim deadline.",
    },
    "va-itf-complete": {
        "label": "Complete your claim after filing intent",
        "brief": "Completing your claim within 1 year of the actual intent date protects its potential effective date. Confirm the exact deadline and VA receipt so the intent does not expire before the completed claim arrives.",
    },
    "va-decision": {
        "label": "Check for your VA decision",
        "brief": "BDD aims for a decision at or soon after separation. Check for the actual decision so that aim is not treated as a confirmed decision date.",
    },
    "va-health": {
        "label": "Apply for VA health care",
        "brief": "VA must confirm your health care eligibility and care start date. Coordinate that date with your other coverage so you know which care is available after active duty.",
    },
    "va-drill": {
        "label": "Reconcile your VA and drill pay",
        "brief": "VA and your Reserve unit must reconcile actual paid training days. Confirm the notice instructions and deadline so guessed day counts do not become your waiver response.",
    },
    "va-dental": {
        "label": "Confirm Class II dental care and apply",
        "brief": "VA's current Class II criteria include 90 days of Persian Gulf War-era active service, no dishonorable discharge, application within 180 days and no DD214 certification of a complete dental exam and all needed treatment. Ask VA dental to confirm your eligibility and receipt deadline; the older manual is a source conflict.",
    },
    "va-net": {
        "label": "1-year VA claim filing boundary",
        "brief": "The calendar anniversary counts from your last active-duty day, including a confirmed override. Have VA or your VSO confirm your receipt deadline, effective date and any exception before this boundary. The board does not extend it for weekends or holidays.",
    },
    "va-net-confirm": {
        "label": "Confirm your VA claim receipt deadline",
        "brief": "Ask VA or your VSO to confirm your claim receipt deadline and effective date before the separate 1-year boundary. This planning target is 11 calendar months after service end, moved earlier for weekends and federal holidays. Arrange filing before the confirmed deadline.",
    },
    "dap-ram1": {
        "label": "Ask RAM-1 about your Reserve commission",
        "brief": "Reserve appointment processing starts at HQMC receipt after resignation approval allows submission. Confirm receipt and status with RAM-1 so the resignation target is not mistaken for guaranteed approval before EAS.",
    },
    "dap-receipt": {
        "label": "Confirm HQMC received your appointment request",
        "brief": "HQMC receipt starts the Reserve appointment processing interval. Record the actual date RAM-1 confirms so a planning boundary is not treated as receipt or an approval guarantee.",
    },
    "dap-cc": {
        "label": "Discuss Reserve options with your counselor",
        "brief": "Your Career Counselor submits the DAP request with you. Confirm billet options and the submission route together so you know how your request will proceed.",
    },
    "dap-billet": {
        "label": "Choose your Reserve billet",
        "brief": "DAP approval guarantees assignment to the selected available billet. Confirm availability with your counselor so you do not rely on a billet before the request is approved.",
    },
    "dap-bonus": {
        "label": "Read your affiliation incentive terms",
        "brief": "An affiliation bonus carries a service obligation. Confirm eligibility and read the offered terms before acceptance so you know what service you are agreeing to provide.",
    },
    "dap-package": {
        "label": "Prepare your DAP package",
        "brief": "A ready package lets your counselor submit when the DAP window opens. Confirm the billet choice and package contents beforehand so missing details do not hold up submission.",
    },
    "dap-request-o": {
        "label": "Submit your officer DAP request",
        "brief": "Your officer DAP request must be submitted within its allowed window. Confirm eligibility and timing with your counselor so the first day target does not become a missed submission window.",
    },
    "dap-request-e": {
        "label": "Submit your enlisted DAP request",
        "brief": "Your enlisted DAP request must be submitted within its allowed window. Confirm eligibility and timing with your counselor so preparation is complete when the window opens.",
    },
    "dap-commission": {
        "label": "Check your Reserve commission approval",
        "brief": "Reserve Affairs does not notify you directly when your commission is approved. Check the MCTFS record with RAM-1 and IPAC; without approval before EAS, you are ineligible for DAP.",
    },
    "dap-763": {
        "label": "Get your Reserve commission record signed",
        "brief": "Your commission record needs a higher grade administering officer's signature before separation. Obtain and return it for your service record so the legal record of your Reserve commission is complete.",
    },
    "dap-checkin": {
        "label": "Check in to your Reserve unit",
        "brief": "Checking in completes your arrival at the gaining Reserve unit. Missing the required check in can move you to the IRR and cost you DAP benefits.",
    },
    "lv-ledger": {
        "label": "Enter your LES leave balance",
        "brief": "Your leave forecast needs the real balance from your LES. Update it each month so the model does not use an outdated number.",
    },
    "lv-plan": {
        "label": "Plan your remaining leave",
        "brief": "Your final leave balance affects sellback and possible debt. Confirm approved leave and payable days with IPAC and disbursing; a negative balance at discharge can be collected from your pay.",
    },
    "lv-terminal": {
        "label": "Confirm your leave and PTAD dates",
        "brief": "Your requested leave and PTAD must fit the earlier separation request and completed separation requirements. Confirm approved dates and records acceptance so a final planning check is not mistaken for the initial request.",
    },
    "lv-requests": {
        "label": "Submit each leave block in MOL",
        "brief": "Each leave block needs CO approval. Submit every block in MOL so your planned leave is presented for approval.",
    },
    "lv-risk-r": {
        "label": "Recheck leave after resignation approval",
        "brief": "HQMC can approve a different resignation date from the one requested. Recalculate leave using the approved date so the leave math does not keep using the old plan.",
    },
    "lv-risk-t": {
        "label": "Recheck leave after retirement approval",
        "brief": "HQMC can approve a different retirement or FMCR date from the one requested. Recalculate leave using the approved date so your balance forecast matches the actual plan.",
    },
    "lv-final": {
        "label": "Check your final leave balance",
        "brief": "Your last LES and separation record show the final leave balance. Check them against your plan so a balance difference or leave debt is not missed.",
    },
    "lv-tsp": {
        "label": "Confirm your TSP login works",
        "brief": "Your TSP stays in place after active duty, and drill pay can keep contributing if you affiliate. Confirm your login so you can still reach the account.",
    },
    "fam-tamp": {
        "label": "Confirm your TAMP coverage dates",
        "brief": "Qualifying Selected Reserve affiliation can provide TAMP coverage without a break in service. Confirm the award and actual family coverage dates so your Reserve profile choice is not treated as proof of coverage.",
    },
    "fam-trs": {
        "label": "Arrange coverage after TAMP ends",
        "brief": "Eligible Selected Reserve Marines may enroll in TRICARE Reserve Select after TAMP. Confirm each family member's enrollment and effective date so the planning target is not mistaken for actual coverage.",
    },
    "fam-chcbp": {
        "label": "Confirm coverage after active duty",
        "brief": "Your status after active duty determines which coverage may apply. Ask IPAC, DEERS, and TRICARE to confirm eligibility and actual enrollment deadlines before choosing a plan you may not qualify for.",
    },
    "fam-tricare-ret": {
        "label": "Prepare your retirement health coverage",
        "brief": "Retirement changes your health coverage and enrollment choices. Confirm the plan, effective date, and actual deadlines with TRICARE so a preparation target is not treated as an enrollment deadline or proof of coverage.",
    },
    "fam-fedvip": {
        "label": "Check your FEDVIP dental options",
        "brief": "You and your family may qualify to purchase FEDVIP dental coverage. Confirm eligibility, cost, and enrollment timing before current coverage ends so you do not rely on an unconfirmed option.",
    },
    "ret-id": {
        "label": "Update retired IDs and family records",
        "brief": "Your approved retirement or FMCR status determines the ID updates needed. Confirm each family member's DEERS details so the planning target is not mistaken for a completed status change.",
    },
    "fam-dental-tdp": {
        "label": "Check Reserve and family dental coverage",
        "brief": "Reserve sponsor and family dental coverage need separate checks. Confirm eligibility, enrollment, and premiums with TRICARE and DEERS so family continuation is not assumed from the sponsor's coverage.",
    },
    "fam-dental-civ": {
        "label": "Arrange your civilian dental coverage",
        "brief": "Active duty dental coverage ends with your service. Confirm when yours and your family's coverage ends so civilian dental can be arranged around that change.",
    },
    "fam-id": {
        "label": "Check your family's DEERS and IDs",
        "brief": "Your family's status changes at EAS. Ask the ID card office what changes so you know which family records and cards need attention.",
    },
    "fam-sgli": {
        "label": "Confirm your life insurance options",
        "brief": "Your life insurance continuation and conversion options need individual confirmation. Ask VA Insurance about the governing deadline and combined coverage limit so conflicting printed windows do not lead you to miss your opportunity.",
    },
    "fam-teb": {
        "label": "Check your GI Bill transfer obligation",
        "brief": "Your GI Bill transfer carries a service obligation. Confirm its end date with the education office because leaving before it is complete cancels the transfer.",
    },
    "fam-hhg-counsel": {
        "label": "Arrange your final move counseling",
        "brief": "DMO/TMO counseling checks your final move against your orders. Book the visit and confirm entitlement so the appointment target is not mistaken for the shipment expiration.",
    },
    "fam-hhg-appt": {
        "label": "Record your confirmed move counseling appointment",
        "brief": "Your confirmed counseling appointment gives you an actual visit date. Record it separately so a planning target or shipment expiration is not treated as the appointment.",
    },
    "fam-hhg-entitlement": {
        "label": "Confirm your move and storage limits",
        "brief": "Your orders determine the final shipment entitlement and time limit. Get shipment and storage limits from DMO/TMO in writing so an expired entitlement or added storage cost does not catch you unprepared.",
    },
    "fam-va-dental-iv": {
        "label": "Check your VA dental benefit",
        "brief": "A qualifying rating or individual unemployability may provide needed VA dental care. Confirm eligibility with the VA dental clinic before relying on it; a temporary rating does not qualify for Class IV.",
    },
    "fam-champva": {
        "label": "Check your family's CHAMPVA eligibility",
        "brief": "A permanent and total service connected disability may qualify your spouse or child for CHAMPVA. Confirm eligibility before relying on coverage because anyone eligible for TRICARE is excluded.",
    },
    "fam-will": {
        "label": "Arrange your will and POA",
        "brief": "Base legal provides a will and power of attorney at no cost while you serve. Arrange them before leaving so you can use that free service during active duty.",
    },
    "fam-budget": {
        "label": "Plan your family's new budget",
        "brief": "Active duty pay ends at your date. Count retired pay, drill pay, VA compensation, and civilian pay only when approved so your family budget does not depend on unconfirmed income.",
    },
    "cmd-plan": {
        "label": "Agree who takes your billet",
        "brief": "Your relief and turnover dates shape leave and SkillBridge cover. Settle them with your CO early so those plans can account for who takes your billet and when.",
    },
    "cmd-award": {
        "label": "Check your final report and award",
        "brief": "Your final report and award need command attention, and awards take weeks. Ask your CO and S-1 early so submission is not left until departure.",
    },
    "cmd-binder": {
        "label": "Prepare your turnover binder",
        "brief": "Your relief needs open actions, contacts, and account details from the start. Put them in the binder before the handoff.",
    },
    "cmd-turnover": {
        "label": "Meet with your relief for turnover",
        "brief": "Face to face turnover gives you time with your relief before you leave. Agree on dates that work so the handoff has time set aside.",
    },
    "cmd-checkout": {
        "label": "Complete your unit checkout sheet",
        "brief": "Your checkout sheet records the formal unit checkout. Confirm it with IPAC so gear and account checkout steps are not left unfinished.",
    },
}
