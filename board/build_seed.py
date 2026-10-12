#!/usr/bin/env python3
"""Build seed.json: the generic starting plan for a Muster Out board.

Every record (line of effort, item, contact) carries `when`, a list of flags that must all be
present for the record to be included on a person's board. An empty list means always.
Flags the setup produces: resign | retire | eas, officer | enlisted, reserve | noreserve,
sb | nosb, cat1 | cat2 | cat3, and notretire (any path but retire).

Date rules follow the board resolver documented in CLAUDE.md. SETUP means the
day the board was installed. The optional biz="prev" moves weekends to Friday.

Run: python3 build_seed.py  (writes seed.json, verifies every quote against the local regulation
texts when they are present, and checks every path combination). --no-verify skips the quote check.
"""
import itertools, json, re, sys
from pathlib import Path
from seed_copy import COPY

HERE = Path(__file__).resolve().parent
DASHES = (chr(0x2014), chr(0x2013))
REGS = HERE.parent / "packs" / "usmc" / "regs"

U175 = "https://www.marines.mil/News/Messages/Messages-Display/Article/3739611/"
U454 = "https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/"
U045 = "https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/"
U280 = "https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/"
UMCO = "https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf"
UNAVMC = "https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf"
U1050 = "https://www.marines.mil/portals/1/publications/mco%201050.3j.pdf"
UBDD = "https://www.va.gov/disability/how-to-file-claim/when-to-file/pre-discharge-claim/"
UREP = "https://www.va.gov/get-help-from-accredited-representative/"
USHA = "https://www.benefits.va.gov/compensation/docs/SHA_DBQ_Part_A_Self-Assessment.pdf"
UVGLI = "https://www.va.gov/life-insurance/options-eligibility/vgli/"
U2122 = "https://www.va.gov/find-forms/about-form-21-22/"
U8951 = "https://www.va.gov/find-forms/about-form-21-8951/"
UVAHC = "https://www.va.gov/health-care/how-to-apply/"
UDENT = "https://www.va.gov/health-care/about-va-health-benefits/dental-care/"
UMILC = "https://milconnect.dmdc.osd.mil/"
UDOL214 = "https://www.dol.gov/node/178814"
UVAEFF = "https://www.va.gov/disability/effective-date/"
UTDP = "https://www.tricare.mil/CoveredServices/Dental/NGRDental"
USGLIH = "https://www.benefits.va.gov/INSURANCE/docs/sgli-vgli-handbook.pdf"
UTRIRET = "https://www.tricare.mil/LifeEvents/Retiring"
UCHCBP = "https://www.tricare.mil/Plans/SpecialPrograms/CHCBP"
UMOU = "https://www.skillbridge.mil/static/docs/2026_DoW_SkillBridge_MOU_BLANK.pdf"
USKB = "https://skillbridge.mil/"
UTRPA = "https://www.okinawa.usmc-mccs.org/modules/media/?do=inline&id=66b20c97-887b-462b-a8a7-97dcd431a6e3&v=1"
UCHAMPVA = "https://www.va.gov/family-and-caregiver-benefits/health-and-disability/champva/"
UITF = "https://www.va.gov/resources/your-intent-to-file-a-va-claim/"
UJTR = "https://media.defense.gov/2022/Jan/04/2002917147/-1/-1/0/JTR.PDF"
TRPA = "MCO 1700.31A"
VDENT = "VA dental care eligibility"
VCHAMPVA = "VA CHAMPVA benefits"
VITF = "VA intent to file guidance"
JTR = "Joint Travel Regulations (1 Oct 2026)"

MCO = "MCO 1900.16 CH-3 (MARCORSEPMAN)"
LVO = "MCO 1050.3J"
VAG = "VA Benefits and Services Participant Guide v6.1"

UTRP = "https://hawaii.usmc-mccs.org/marine-family-support/transition-readiness-program"
U326 = "https://www.marines.mil/News/Messages/Messages-Display/Article/3441944/enlisted-active-duty-service-limits/"
UMMSR = "https://www.manpower.marines.mil/Divisions/Manpower-Management/Separation-and-Retirements-Branch/Active-Duty-Retirements-Separations/"
MMSR = "HQMC MMSR-2 enlisted retirement guidance"

def c(ref, para, quote, url=None):
    return {"ref": ref, "para": para, "quote": quote, "url": url}

# The builder verifies these quotes against the copied regulation texts.
Q175_2 = "requests for retirement or resignation will be submitted not more than 18 months and not less than six months prior to the requested retirement or resignation date."
Q175_3 = "The Director, Manpower Management, may approve a resignation/retirement request for a date other than the date requested based on the needs of the service"
Q5003_1 = "(Date) I request to resign my commission in the Marine Corps Regular component effective (date) and (do) (do not) desire a Reserve commission. I have been counseled per paragraph 5003 of MCO 1900.16."
Q5003_2 = "Submit requests for resignation via the unit diary per reference (cn) MCTFS PRIUM (Online) paragraph 5137... The unit must report the appropriate type transaction code (TTC) request in the unit diary to indicate whether the officer does or does not desire a Reserve commission."
Q5003_3 = "The CMC will also notify the unit via EDFR once a request is approved."
Q5003_4 = "Submit a letter requesting resignation (Figure 5-1) via the chain of command to the CMC (MMSR-2) via an encrypted email to smb.manpower.mmsr2o@usmc.mil when:... a. A waiver of eligibility criteria of paragraph 5002 is required, or b. An officer requests a Reserve commission but is not recommended for one by the commanding officer."
QFIG51 = "The reporting senior must recommend and justify either offering or not offering a Reserve commission to the officer submitting the resignation regardless of whether or not they are obligated by law to accept a Reserve commission."
Q5002_3A = "Officer resignations will not be recommended for approval if: a. The officer has been issued, or notified that he or she will be issued, Permanent Change of Station (PCS) orders before the date of the officer's request."
Q5004_2 = "A request for withdrawal or modification of a resignation may be made any time before 45 days from the effective date of the resignation or commencement of separation leave."
Q5005_1 = "Approval/disapproval of a resignation request and authority to release is issued via the unit diary through MCTFS. Units will be notified via EDFR."
Q2004_1 = "Submit requests for voluntary retirement, not requiring waivers, via the unit diary system in MCTFS per reference (cn) MCTFS PRIUM (Online). The officer requesting retirement is required to sign a copy of Appendix J from this Manual for inclusion in the electronic service record. Requests for retirement will be submitted not more than 14 months and not less than four months prior to the requested retirement date."
Q2004_2 = "Officers requesting retirement are cautioned not to make significant personal commitments (such as buying or selling a house or business, or accepting civilian employment) based upon mere submission of a request."
Q2003_1D = "Retirement requests involving cancellation of PCS orders must be forwarded to the CMC (MMSR-2) with the CMC (MMOA) as an information addressee. Submit the request no later than 10 working days after receipt of orders."
Q252 = "All retirements, except those by reason of physical disability and Reservists who are retiring with pay at age 60, are effective on the 1st day of the month."
Q1406_1 = "A completed election form (DD Form 2656) must be faxed with included Privacy Act form and mailed to DFAS at least 30 days prior to retirement or transfer to FMCR"
Q1406_5 = "Elections other than full coverage require spousal concurrence and must be notarized."
Q1406_6 = "If no election is made prior to the effective date of the retirement, DFAS (by law) will automatically deduct full SBP coverage at the full gross salary rate."
Q1011_2 = "A Marine should schedule a SHPE medical evaluation not less than six months before the effective date of separation to allow time for necessary medical treatment or disability processing."
Q1010_2E = "Do not approve leave in excess of the number of days which the Marine can accrue before the end of current contract (ECC). Leave taken beyond that which can be earned is excess leave and results in nonentitlement to pay and allowances."
Q5004_1B = "Officers without adverse information in any Department of the Navy systems of record are then placed on the non-adverse scroll and routed from HQMC, RA Division via the DC M&RA to the SecDef. The non-adverse transitional scrolling process may require a longer lead time than the minimum length of time required by the resignation process (four months per paragraph 5003 of this Manual)."
QPTAD_A5 = "Officers and enlisted Marines with an approved retirement date are eligible for transition PTAD."
QPTAD_B = "CONUS-based Marines being released from active duty for the reasons described in paragraph 1c(11)(a) of this Order are authorized up to 20 days transition PTAD."
QPTAD_E = "Permissive TAD approved under this program is for house hunting, job hunting, or other activities to facilitate relocation."
QSELL = "Separation payments for unused accrued leave are limited to 60 days during a military career per reference (q)."
QADV = "advance leave shall be limited to the lesser of: (1) 45 days or (2) The amount of leave that shall be earned during the remaining period of active duty"
QADV_D = "Accrued leave shall be expended prior to the authorization of advance leave."
Q454_3A = "Transitioning AC Marines who affiliate with the Selected Reserve without a break in service are eligible for 180 days of premium-free transitional health care under the Transitional Assistance Management Program (TAMP) in accordance with reference (b)."
Q454_3A2 = "Upon completion of TAMP, eligible Selected Reserve Marines may enroll in TRICARE Reserve Select."
Q454_4A = "Transitioning Marines may select an available SMCR or IMA billet at their unit of choice, subject to availability... Upon DAP approval, assignment to the selected billet is guaranteed."
Q454_4C = "Marines affiliating with an SMCR unit through DAP may qualify for monetary incentives in exchange for a specified service obligation."
Q454_5B = "Officers may submit a DAP request no earlier than (NET) 180 days prior to EAS and no later than (NLT) 60 calendar days prior to EAS."
Q454_5B2 = "Officers who do not receive approval for a Reserve commission prior to EAS are not eligible for DAP."
Q454_5C = "Enlisted Marines requesting direct affiliation may submit a DAP request NET 180 days prior to EAS and NLT 30 calendar days prior to EAS."
Q454_5E = "Retiring Marines (including medical retirement) and Marines currently serving in the RC are ineligible for DAP."
Q454_6A = "Marines interested in DAP should contact their unit Career Counselor for information regarding SMCR and IMA opportunities, benefits, incentives, lateral move opportunities, and for assistance with the submission of a DAP request."
Q454_6B = "It is the individual Marine's responsibility to check into the gaining SMCR unit or IMA detachment within 30 calendar days after EAS."
Q045_2 = "Reserve appointments for officers transitioning from the AC to the RC require a minimum of four months from the date received at Headquarters Marine Corps (HQMC) for approval. In cases where the officer was subject to adversity this timeline is increased."
Q045_3B1 = "Once the resignation has been approved and an EAS is populated in the resigning officer's record, CMC(RA) will submit for a Reserve commission via the Secretary of Defense."
Q045_4A = "RA does not directly notify individual officers who are approved for a Reserve commission. Approval is reflected in the planned separations code within Marine Corps Total Force System (MCTFS)."
Q045_5B = "This updated NAVMC 763 must be issued to the separating officer before their separation takes place. The separating officer is responsible for obtaining a signature from an Administering Officer who is higher in grade than the separating officer."
Q280_3A = "Category I E1-E5 Up to 120 days"
Q280_3A2 = "Category II E6-E7, WO-CWO3, and O1-O4 Up to 90 days"
Q280_3A3 = "Category III E8-E9, CWO4-CWO5, O5 and above Up to 90 days"
Q280_3B = "PTAD or leave in conjunction with SkillBridge is authorized. However, the combined period of absence from duties must fall within the three category timeline/duration limits. If used in conjunction, all authorized PTAD (e.g. Transition PTAD and Skillbridge PTAD) must be executed prior to any authorized leave (e.g. Terminal leave)."
Q280_3B2 = "During SkillBridge participation, Marines are subject to the UCMJ and Commanders are required to establish detailed accountability protocols."
Q280_3B3 = "Marines are not authorized to extend obligated service to complete the SkillBridge program."
Q280_3C = "Commanders at the grade of Lieutenant Colonel and above, as defined by reference (c), are designated as the approval authority for Categories I and II. General Officers are designated as the approval authority for Category III, and Category III participation cannot result in a gapped billet."
Q280_4C = "Installation SkillBridge coordinators are in place to guide, direct, and advise both Marines and commands on SkillBridge protocols. The Navy College Management Information System (NCMIS) is the Marine Corps' SkillBridge system of record."
QNAVMC_2 = "SkillBridge is not authorized to further civilian education or for experiential purposes per reference (a); securing meaningful employment is the expectation."
QNAVMC_3C2 = "Complete Developing Your Business Ethics (LLISELF301) MarineNet course, or equivalent, within 12 months prior to the program start date"
QNAVMC_7A4 = "Obtain a program acceptance letter that provides program details to include location, associated cost, length of... training, employment outcome, and POC for the SkillBridge partner."
QNAVMC_11 = "Marines shall return to parent commands if SkillBridge program requirements are less than 20 hours per week or eight hours per day and not be on administrative leave status."

# These web quotes preserve the 08 Oct 2026 source snapshot.
QTRI_90 = "You must enroll in a TRICARE plan within 90 days after your retirement."
QTRI_REENROLL = "If you want to keep TRICARE Prime or TRICARE Select with no break in coverage, you must reenroll within 90 days after your retirement date."
QTRI_FEDVIP = "You and your family members may qualify to purchase dental coverage through the Federal Employees Dental and Vision Insurance Program."
QTRI_ID = "You and your family members need to get new ID cards."
QTRI_SHPE = "Remember to schedule your Separation History and Physical Examination between 90 and 180 days before you retire or start terminal leave."
QCHCBP_60 = "If you qualify for the CHCBP, you can enroll within 60 days of losing your eligibility for TRICARE."
QCHCBP_18 = "Gives you temporary health coverage for 18 to 36 months when you lose eligibility for TRICARE"
QMOU = "online opportunities must include virtual synchronous (i.e., live person-led) training and/or a hybrid with in-person sessions. Asynchronous training (if any) will be less than 50% of the length of the training."

settings = {"eas": "2027-10-01", "sbStart": "2027-07-03", "sbEnd": "2027-09-30", "planSet": "SETUP", "placeholder": True}
ledger = {"asOf": "SETUP", "balance": 0, "accrualPerMonth": 2.5, "note": "Enter the balance from your latest LES."}

loes = [
    {"id": "sep", "n": 1, "name": "Separation", "lead": "CO, IPAC, TAP counselor, MMSR-2", "when": [],
     "purpose": "The request approved, the date fixed, and every transition gate closed on time."},
    {"id": "sb", "n": 2, "name": "SkillBridge", "lead": "Provider, SkillBridge coordinator, approving commander", "when": ["sb"],
     "purpose": "The final weeks in an approved program, away from the unit, inside the category cap."},
    {"id": "va", "n": 3, "name": "VA and medical", "lead": "Accredited VSO, medical", "when": [],
     "purpose": "Every condition on the record before separation and a VA rating decision at or soon after your date."},
    {"id": "dap", "n": 4, "name": "Reserve (DAP)", "lead": "Career Counselor, Reserve Affairs", "when": ["reserve"],
     "purpose": "Reserve affiliation approved before EAS with a guaranteed billet and no break in service."},
    {"id": "leave", "n": 5, "name": "Leave and pay", "lead": "IPAC", "when": [],
     "purpose": "Leave used or sold on purpose, no debt at the end, pay and TSP settled."},
    {"id": "fam", "n": 6, "name": "Family and coverage", "lead": "You and your family", "when": [],
     "purpose": "No gap in health care, dental, life insurance, or family paperwork."},
    {"id": "cmd", "n": 7, "name": "Turnover", "lead": "You, your relief, CO", "when": [],
     "purpose": "Your billet handed over cleanly and your record closed out."},
]

items = []
def item(id, loe, title, why, how=None, owner="You", due=None, window=None, kind="task", critical=False, presence=False,
         cite=None, verify=None, status="open", when=None, notes="", basis="rule"):
    items.append({"id": id, "loe": loe, "order": len([i for i in items if i["loe"] == loe]) + 1, "kind": kind, "title": title,
                  "why": why, "how": how or [], "owner": owner, "due": due, "window": window, "critical": critical,
                  "presence": presence, "cite": cite or [], "verify": verify, "status": status, "doneOn": None,
                  "notes": notes, "when": when or [], "basis": basis})

# ---------------- 1. SEPARATION: every path ----------------
item('sep-tell', 'sep', 'Tell your CO your plan and your date', 'Your reporting senior hears it from you first. The request, any SkillBridge endorsement, and billet cover all run through the CO.',
     how=['Bring the date, the path (resign, retire, or EAS), and whether you want Reserve affiliation.', 'Ask how the CO wants the request routed and who in the unit handles the paperwork.'],
     owner='You',
     due={'eas': -365},
     presence=True,
     cite=[],
     verify='CO: how do you want this routed, and who is my point of contact in the unit?',
     basis='target')
item('sep-ic', 'sep', 'Individualized Initial Counseling (IC)', 'Complete this mandatory TRP gate no later than 365 days before EAS under MCO 1700.31A. Count calendar days from the confirmed end of active service on va-service-end. Keep the Retired List action date separate. Retiree IC may begin as soon as possible during the 24-month period preceding anticipated retirement. Other Marines may complete IC 18 months before separation or release from active duty.',
     how=['Have IPAC and the TRP office confirm the EAS used by the order and record it on va-service-end. The rule date stays separate from the appointment.', 'Record the actual appointment as a fixed date on sep-ic-appt and actual completion as doneOn on this gate.', "Complete IC, pre-separation counseling, TRS workshops, Capstone and Commander's Verification in that order. For SkillBridge, complete all transition requirements before participation under NAVMC 1700.2B, enclosure (2), paragraph 7."], owner='TAP counselor',
     due={'item': 'va-service-end', 'days': -365}, critical=True,
     cite=[c(TRPA, 'Encl (2), Ch 5 para 3.a', 'Individualized Initial Counseling (IC). Must be completed not later than 365 days prior to EAS date.', UTRPA), c(TRPA, 'Encl (2), Ch 8 para 2', 'IC must be completed, in-person, prior to the Pre-separation Counseling Brief.', UTRPA), c(TRPA, 'Encl (2), Ch 8 para 4.a-b', 'For EAS dates due to retirement, this may begin as soon as possible during the 24-month period preceding an anticipated retirement date but no later than 365 days prior to EAS date. ... For EAS dates other than retirement, Marines may complete the IC 18 months before separation or release from AD but no later than 365 days prior to EAS date.', UTRPA)],
     verify='Installation TRP office, UTC and IPAC: confirm EAS, sequencing, completion and any short-notice instructions. SkillBridge coordinator and CO: confirm completion before participation.', basis='rule')
item('sep-ic-appt', 'sep', 'Individualized Initial Counseling (IC): confirmed appointment', 'Record the actual office-confirmed appointment. Keep the separate rule deadline.',
     how=['Give Claude the confirmed appointment date and ask Claude to record a fixed date here. Keep this event undated until confirmation.'],
     owner='TAP counselor', due=None, kind='milestone', presence=True,
     cite=[c(TRPA, 'Encl (2), Ch 5 para 3.a', 'Individualized Initial Counseling (IC). Must be completed not later than 365 days prior to EAS date.', UTRPA)],
     verify='Installation TRP office and UTC; CO for commander verification: confirm the appointment and completion record.', basis='rule')
item('sep-presep', 'sep', 'Pre-separation counseling brief', 'Complete this mandatory TRP gate no later than 365 days before EAS under MCO 1700.31A. Count calendar days from the confirmed end of active service on va-service-end. Keep the Retired List action date separate.',
     how=['Have IPAC and the TRP office confirm the EAS used by the order and record it on va-service-end. The rule date stays separate from the appointment.', 'Record the actual appointment as a fixed date on sep-presep-appt and actual completion as doneOn on this gate.', "Complete IC, pre-separation counseling, TRS workshops, Capstone and Commander's Verification in that order. For SkillBridge, complete all transition requirements before participation under NAVMC 1700.2B, enclosure (2), paragraph 7."], owner='TAP counselor',
     due={'item': 'va-service-end', 'days': -365}, critical=True,
     cite=[c(TRPA, 'Encl (2), Ch 5 para 3.b', 'Pre-separation Counseling Brief. Must be completed not later than 365 days prior to EAS date.', UTRPA), c(TRPA, 'Encl (2), Ch 9 para 2', 'The Pre-separation Counseling Brief must be attended after IC completion and prior to attendance to TRS.', UTRPA)],
     verify='Installation TRP office, UTC and IPAC: confirm EAS, sequencing, completion and any short-notice instructions. SkillBridge coordinator and CO: confirm completion before participation.', basis='rule')
item('sep-presep-appt', 'sep', 'Pre-separation counseling brief: confirmed appointment', 'Record the actual office-confirmed appointment. Keep the separate rule deadline.',
     how=['Give Claude the confirmed appointment date and ask Claude to record a fixed date here. Keep this event undated until confirmation.'],
     owner='TAP counselor', due=None, kind='milestone', presence=True,
     cite=[c(TRPA, 'Encl (2), Ch 5 para 3.b', 'Pre-separation Counseling Brief. Must be completed not later than 365 days prior to EAS date.', UTRPA)],
     verify='Installation TRP office and UTC; CO for commander verification: confirm the appointment and completion record.', basis='rule')
item('sep-trs', 'sep', 'Transition Readiness Seminar workshops', 'Complete this mandatory TRP gate no later than 180 days before EAS under MCO 1700.31A. Count calendar days from the confirmed end of active service on va-service-end. Keep the Retired List action date separate.',
     how=['Have IPAC and the TRP office confirm the EAS used by the order and record it on va-service-end. The rule date stays separate from the appointment.', 'Record the actual appointment as a fixed date on sep-trs-appt and actual completion as doneOn on this gate.', "Complete IC, pre-separation counseling, TRS workshops, Capstone and Commander's Verification in that order. For SkillBridge, complete all transition requirements before participation under NAVMC 1700.2B, enclosure (2), paragraph 7."], owner='You',
     due={'item': 'va-service-end', 'days': -180}, critical=True,
     cite=[c(TRPA, 'Encl (2), Ch 5 para 3.c', 'Transition Readiness Seminar (TRS) Workshops. Must be completed not later than 180 days prior to EAS date.', UTRPA), c(TRPA, 'Encl (2), Ch 10 para 3', 'TRS workshops must be attended after completion of the Pre-separation Counseling Brief.', UTRPA)],
     verify='Installation TRP office, UTC and IPAC: confirm EAS, sequencing, completion and any short-notice instructions. SkillBridge coordinator and CO: confirm completion before participation.', basis='rule')
item('sep-trs-appt', 'sep', 'Transition Readiness Seminar workshops: confirmed appointment', 'Record the actual office-confirmed appointment. Keep the separate rule deadline.',
     how=['Give Claude the confirmed appointment date and ask Claude to record a fixed date here. Keep this event undated until confirmation.'],
     owner='You', due=None, kind='milestone', presence=True,
     cite=[c(TRPA, 'Encl (2), Ch 5 para 3.c', 'Transition Readiness Seminar (TRS) Workshops. Must be completed not later than 180 days prior to EAS date.', UTRPA)],
     verify='Installation TRP office and UTC; CO for commander verification: confirm the appointment and completion record.', basis='rule')
item('sep-roob', 'sep', 'Complete ROOB before IC', 'Complete ROOB as IC prework and confirm the certificate requirement with the installation TRP office.',
     owner='You',
     due={'item': 'sep-ic-appt', 'days': -7},
     cite=[c(TRPA, 'Encl (2), Appendix A, IC Standard Pre-Work Instructions', 'Complete Reserve Obligations & Opportunities Brief (ROOB) - Required Complete ROOB via MarineNet', UTRPA), c(TRPA, 'Encl (2), Ch 8 para 6', 'Eligible Marines must complete all mandatory and standard pre-work, in accordance with chapter 15 of this Order, in preparation for the IC.', UTRPA)],
     verify='Installation TRP office and UTC: confirm ROOB completion and the certificate before the actual IC appointment. The 7-day lead is a planning target.',
     when=['notretire'],
     basis='target')
item('sep-roob-ret', 'sep', 'ROOB before retirement IC', 'Complete ROOB as IC prework and confirm the certificate requirement with the installation TRP office.',
     owner='You',
     due={'item': 'sep-ic-appt', 'days': -7},
     cite=[c(TRPA, 'Encl (2), Appendix A, IC Standard Pre-Work Instructions', 'Complete Reserve Obligations & Opportunities Brief (ROOB) - Required Complete ROOB via MarineNet', UTRPA), c(TRPA, 'Encl (2), Ch 8 para 6', 'Eligible Marines must complete all mandatory and standard pre-work, in accordance with chapter 15 of this Order, in preparation for the IC.', UTRPA)],
     verify='Installation TRP office and UTC: confirm ROOB completion and the certificate before the actual IC appointment. The 7-day lead is a planning target.',
     when=['retire'],
     basis='target')
item('sep-dd2648', 'sep', 'Check the DD 2648 pre-separation checklist: separation type and grade', 'Confirm that the DD 2648 reflects your actual separation path and current grade. Actual retirement, including medical retirement, makes a Marine ineligible for DAP. An erroneous entry needs correction and eligibility review.',
     how=['Ask the installation TRP counselor for the authorized correction procedure.', 'Ask IPAC and the Career Counselor which record determines DAP eligibility.'],
     owner='You',
     due={'eas': -140},
     critical=True,
     cite=[c('MARADMIN 454/26', '5.e', 'Retiring Marines (including medical retirement) and Marines currently serving in the RC are ineligible for DAP.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify='Installation TRP counselor, IPAC and Career Counselor: confirm correction procedure, actual separation status and the DAP eligibility record.',
     basis='target')
item('sep-capstone', 'sep', 'TRP Capstone', 'Complete this mandatory TRP gate no later than 120 days before EAS under MCO 1700.31A. Count calendar days from the confirmed end of active service on va-service-end. Keep the Retired List action date separate.',
     how=['Have IPAC and the TRP office confirm the EAS used by the order and record it on va-service-end. The rule date stays separate from the appointment.', 'Record the actual appointment as a fixed date on sep-capstone-appt and actual completion as doneOn on this gate.', "Complete IC, pre-separation counseling, TRS workshops, Capstone and Commander's Verification in that order. For SkillBridge, complete all transition requirements before participation under NAVMC 1700.2B, enclosure (2), paragraph 7."], owner='TAP counselor',
     due={'item': 'va-service-end', 'days': -120}, critical=True,
     cite=[c(TRPA, 'Encl (2), Ch 5 para 3.d', 'Capstone Review. Must be completed not later than 120 days prior to EAS date.', UTRPA), c(TRPA, 'Encl (2), Ch 12 para 1.c', 'Capstone Review must be completed after completion of TRS workshops and prior to Commander’s Verification.', UTRPA)],
     verify='Installation TRP office, UTC and IPAC: confirm EAS, sequencing, completion and any short-notice instructions. SkillBridge coordinator and CO: confirm completion before participation.', basis='rule')
item('sep-capstone-appt', 'sep', 'TRP Capstone: confirmed appointment', 'Record the actual office-confirmed appointment. Keep the separate rule deadline.',
     how=['Give Claude the confirmed appointment date and ask Claude to record a fixed date here. Keep this event undated until confirmation.'],
     owner='TAP counselor', due=None, kind='milestone', presence=True,
     cite=[c(TRPA, 'Encl (2), Ch 5 para 3.d', 'Capstone Review. Must be completed not later than 120 days prior to EAS date.', UTRPA)],
     verify='Installation TRP office and UTC; CO for commander verification: confirm the appointment and completion record.', basis='rule')
item('sep-cv', 'sep', "Commander's Verification on the DD 2648", 'Complete this mandatory TRP gate no later than 90 days before EAS under MCO 1700.31A. Count calendar days from the confirmed end of active service on va-service-end. Keep the Retired List action date separate.',
     how=['Have IPAC and the TRP office confirm the EAS used by the order and record it on va-service-end. The rule date stays separate from the appointment.', 'Record the actual appointment as a fixed date on sep-cv-appt and actual completion as doneOn on this gate.', "Complete IC, pre-separation counseling, TRS workshops, Capstone and Commander's Verification in that order. For SkillBridge, complete all transition requirements before participation under NAVMC 1700.2B, enclosure (2), paragraph 7."], owner='CO',
     due={'item': 'va-service-end', 'days': -90}, critical=True,
     cite=[c(TRPA, 'Encl (2), Ch 5 para 3.e', 'Commander’s Verification. Must be completed not later than 90 days prior to EAS date.', UTRPA)],
     verify='Installation TRP office, UTC and IPAC: confirm EAS, sequencing, completion and any short-notice instructions. SkillBridge coordinator and CO: confirm completion before participation.', basis='rule')
item('sep-cv-appt', 'sep', "Commander's Verification on the DD 2648: confirmed appointment", 'Record the actual office-confirmed appointment. Keep the separate rule deadline.',
     how=['Give Claude the confirmed appointment date and ask Claude to record a fixed date here. Keep this event undated until confirmation.'],
     owner='CO', due=None, kind='milestone', presence=True,
     cite=[c(TRPA, 'Encl (2), Ch 5 para 3.e', 'Commander’s Verification. Must be completed not later than 90 days prior to EAS date.', UTRPA)],
     verify='Installation TRP office and UTC; CO for commander verification: confirm the appointment and completion record.', basis='rule')
item('sep-ptad', 'sep', 'Transition PTAD: up to 20 days for house and job hunting', 'An approved retirement date qualifies you. CONUS commands can approve up to 20 days, in increments if the approving authority allows, and PTAD runs before any leave.',
     how=['Ask IPAC for the PTAD request route (DTS orders at no cost to the government).', 'Put the dates on the board before you plan leave around them.'],
     owner='You',
     due={'eas': -120},
     cite=[c('MCO 1050.3J', 'Ch 5 para 1.c(11)(a)5', 'Officers and enlisted Marines with an approved retirement date are eligible for transition PTAD.', 'https://www.marines.mil/portals/1/publications/mco%201050.3j.pdf'),
           c('MCO 1050.3J', 'Ch 5 para 1.c(11)(b)', 'CONUS-based Marines being released from active duty for the reasons described in paragraph 1c(11)(a) of this Order are authorized up to 20 days transition PTAD.', 'https://www.marines.mil/portals/1/publications/mco%201050.3j.pdf'),
           c('MCO 1050.3J', 'Ch 5 para 1.c(11)(e)', 'Permissive TAD approved under this program is for house hunting, job hunting, or other activities to facilitate relocation.', 'https://www.marines.mil/portals/1/publications/mco%201050.3j.pdf')],
     verify='CO and IPAC: confirm transition PTAD eligibility and approved duration. Approve the sequence with any leave or SkillBridge.',
     when=['retire'],
     basis='target')
item('sep-dd214', 'sep', 'Review the DD-214 worksheet before you sign', 'IPAC must identify the form edition and review the worksheet with you before the agreed separation processing event. The dental entry is one part of the VA dental eligibility check.',
     how=['Set the review target before the actual processing or permanent departure event for your elected option.', 'Check record of service and separation entries by the field labels IPAC identifies.', 'The date is pending confirmation by IPAC. Give Claude the date the office confirms and ask Claude to record it on this item. Keep the item open until the action is complete.'],
     owner='You',
     due=None,
     critical=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', 'Appendix B, item 17', 'MEMBER WAS PROVIDED COMPLETE DENTAL EXAMINATION AND ALL APPROPRIATE DENTAL SERVICES AND TREATMENT WITHIN 90 DAYS PRIOR TO SEPARATION.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 9.a', 'Depart current PDS within 180 days of EAS on S-PTAD and return to PDS upon completion of SkillBridge to execute the separation process and receipt of DD-214.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 9.b', 'Depart PDS within 180 days of retirement or EAS on S-PTAD, and execute separation process prior to permanently departing and detaching from current PDS to include receipt of separation/retirement orders and DD Form 214 and not return to PDS before separation.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2', 'Terminal leave is not granted until all separation requirements--both administrative and medical--are complete. Terminal leave runs continuously from the first day of leave until the date of EAS or transfer to the Retired List/FMCR.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and MMSR-2: confirm the form edition, worksheet entries and review target before the elected processing or departure event. VA dental confirms eligibility.',
     basis='target')
item('sep-checkout', 'sep', 'Agree the final checkout day with IPAC', 'IPAC confirms whether you complete separation processing before permanent departure or return after SkillBridge. Complete all terminal-leave separation requirements before leave begins.',
     how=['The date is pending confirmation by IPAC and the approving command. Give Claude the date the office confirms and ask Claude to record it on this item. Keep the item open until the action is complete.'],
     owner='IPAC',
     due=None,
     cite=[c('NAVMC 1700.2B', 'Encl (2) para 9.a', 'Depart current PDS within 180 days of EAS on S-PTAD and return to PDS upon completion of SkillBridge to execute the separation process and receipt of DD-214.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 9.b', 'Depart PDS within 180 days of retirement or EAS on S-PTAD, and execute separation process prior to permanently departing and detaching from current PDS to include receipt of separation/retirement orders and DD Form 214 and not return to PDS before separation.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2', 'Terminal leave is not granted until all separation requirements--both administrative and medical--are complete. Terminal leave runs continuously from the first day of leave until the date of EAS or transfer to the Retired List/FMCR.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and approving command: enter the agreed checkout target before terminal leave and confirm the elected processing option with its actual departure or return date.',
     basis='target')
item('sep-eas', 'sep', 'EAS: confirmed service-end date', 'Keep EAS separate from an earlier permanent departure or checkout. Confirm the approved service-end date and processing option with IPAC.',
     owner='You',
     due={'eas': 0},
     kind='milestone',
     critical=True,
     presence=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2', 'Terminal leave is not granted until all separation requirements--both administrative and medical--are complete. Terminal leave runs continuously from the first day of leave until the date of EAS or transfer to the Retired List/FMCR.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 9.a', 'Depart current PDS within 180 days of EAS on S-PTAD and return to PDS upon completion of SkillBridge to execute the separation process and receipt of DD-214.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 9.b', 'Depart PDS within 180 days of retirement or EAS on S-PTAD, and execute separation process prior to permanently departing and detaching from current PDS to include receipt of separation/retirement orders and DD Form 214 and not return to PDS before separation.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf')],
     verify='IPAC: confirm EAS, separation authority and the processing or departure date.',
     when=['notretire'],
     basis='target')
item('ret-day', 'sep', 'Confirm the Retired List or FMCR effective date', 'The manual sets ordinary retirement on the 1st day of the month, except disability and Reserve retirement with pay at age 60, and sets FMCR transfer on the last day of the month. IPAC and MMSR-2 must confirm your approved action and effective date. DFAS must confirm entitlement and the first payment. The last active-duty day is a separate date for BDD. For ordinary retirement it precedes the effective Retired List date by 1 day; IPAC and MMSR-2 must confirm exception and FMCR dates individually.',
     how=['The approved action and service-end dates are pending IPAC and MMSR-2 confirmation. Give Claude each date so the action is recorded here and the last active-duty day on the separate VA service-end milestone. Keep the retirement profile date on the approved action date.'],
     owner='You',
     due={'eas': 0},
     kind='milestone',
     critical=True,
     presence=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', 'Glossary para 252', 'All retirements, except those by reason of physical disability and Reservists who are retiring with pay at age 60, are effective on the 1st day of the month.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '7005.1', 'Retirement must be on the first day of the month. Effective date of transfer to the FMCR will be the last day of the month.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '7007.1.a', 'The first day of the month is the effective date of retirement and the last day of active duty is the preceeding day.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '7007.1.b', 'Transfer to the FMCR is effected on the last day of the month and Marines assume a status in the FMCR on the first day of the following month.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and MMSR-2: confirm Retired List versus FMCR and its effective date. DFAS retired pay: confirm entitlement and first payment.',
     when=['retire'],
     basis='target')
item('ret-fmcr-day', 'sep', 'FMCR transfer: last-day-of-month action', 'If your approved action is FMCR transfer, the manual sets its effective date on the last day of the month. IPAC must enter the approved transfer date; the board cannot derive this action from the retirement profile alone.',
     how=['The date is pending confirmation by IPAC and MMSR-2. Give Claude the date the office confirms and ask Claude to record it on this item. Keep the item open until the action is complete.', 'Ask IPAC and MMSR-2 to distinguish the transfer action, FMCR status start and last active-duty day. Give Claude all confirmed dates to record on this item and the separate VA service-end milestone.'],
     owner='You',
     due=None,
     kind='milestone',
     critical=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '7005.1', 'Retirement must be on the first day of the month. Effective date of transfer to the FMCR will be the last day of the month.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '7007.1.b', 'Transfer to the FMCR is effected on the last day of the month and Marines assume a status in the FMCR on the first day of the following month.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and MMSR-2: confirm whether this action applies, enter the approved last-day-of-month date and mark this item not applicable for a Retired List action.',
     when=['retire', 'enlisted'],
     basis='rule')

# ---------------- 1a. SEPARATION: resigning a regular commission ----------------
item('sep-counsel', 'sep', 'Resignation counseling with the CO and the page 11 entry', 'The CO counsels you and records your Reserve commission choice before submission. MARADMIN 175/24 prints a 6-to-18-month submission window, while the manual diary window is 4 to 14 months. The 7-month date is a planning target. Reserve appointment approval requires at least 4 months from HQMC receipt of that request, after resignation approval and EAS entry permit RA submission.',
     how=['Tell the CO the date you are resigning and whether you want a Reserve commission.', 'The CO counsels you under MCO 1900.16 para 5003. IPAC makes the page 11 entry in the exact wording of para 5003.1.', 'If you want a Reserve commission, ask the CO to record a recommendation in favor (Figure 5-1 Note 1).', 'Supply desired leave and PTAD dates, duration and planned detachment date with the separation request. Ask IPAC and MMSR-2 to check the target against the message window, the manual window and 120 days plus desired leave/PTAD. Resolve any conflict before submission.'],
     owner='CO',
     due={'easMonths': -7, 'biz': 'prev'},
     critical=True,
     presence=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5003.1', '(Date) I request to resign my commission in the Marine Corps Regular component effective (date) and (do) (do not) desire a Reserve commission. I have been counseled per paragraph 5003 of MCO 1900.16.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MARADMIN 175/24', '2', 'requests for retirement or resignation will be submitted not more than 18 months and not less than six months prior to the requested retirement or resignation date.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3739611/'),
           c('MARADMIN 045/25', '2', 'Reserve appointments for officers transitioning from the AC to the RC require a minimum of four months from the date received at Headquarters Marine Corps (HQMC) for approval. In cases where the officer was subject to adversity this timeline is increased.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/'),
           c('MARADMIN 045/25', '3.b.1', "Once the resignation has been approved and an EAS is populated in the resigning officer's record, CMC(RA) will submit for a Reserve commission via the Secretary of Defense.", 'https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2.d', 'If leave is desired in conjunction with a request for separation, the appropriate separation request should be submitted at least 120 days plus the amount of desired leave (to include PTAD) before the effective date of separation. When the request is submitted via unit diary, enter the planned detachment date (PDD) as part of the unit diary request for separation.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2.e', 'Marines anticipating terminal leave in conjunction with separation must inform the CMC (MMSR) of the date and duration of the desired leave upon submission of the request.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5003.2', 'The entry must be made not more than 14 months nor less than four months before the requested date of resignation.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and MMSR-2: confirm routing, submission date, the governing window and 120 days plus desired leave/PTAD before the requested action date.',
     when=['resign'],
     basis='target')
item('sep-diary', 'sep', 'Resignation request entered in MCTFS by unit diary', 'The unit diary reports your requested resignation date and Reserve commission choice. The MARADMIN prints a 6-to-18-month window, while manual 5003.2 prints a 4-to-14-month window and diary rejection outside it. IPAC and MMSR-2 must confirm acceptance and submission timing.',
     how=['IPAC reports the resignation on the unit diary (MCTFS PRIUM para 5137) with your requested date.', 'Confirm the TTC shows your Reserve commission choice.', 'Supply desired leave and PTAD dates, duration and planned detachment date with the separation request. Ask IPAC and MMSR-2 to check the target against the message window, the manual window and 120 days plus desired leave/PTAD. Resolve any conflict before submission.'],
     owner='IPAC',
     due={'easMonths': -7, 'biz': 'prev'},
     critical=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5003.2', 'Submit requests for resignation via the unit diary per reference (cn) MCTFS PRIUM (Online) paragraph 5137... The unit must report the appropriate type transaction code (TTC) request in the unit diary to indicate whether the officer does or does not desire a Reserve commission.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2.d', 'If leave is desired in conjunction with a request for separation, the appropriate separation request should be submitted at least 120 days plus the amount of desired leave (to include PTAD) before the effective date of separation. When the request is submitted via unit diary, enter the planned detachment date (PDD) as part of the unit diary request for separation.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2.e', 'Marines anticipating terminal leave in conjunction with separation must inform the CMC (MMSR) of the date and duration of the desired leave upon submission of the request.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MARADMIN 175/24', '2', 'requests for retirement or resignation will be submitted not more than 18 months and not less than six months prior to the requested retirement or resignation date.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3739611/'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5003.2', 'The entry must be made not more than 14 months nor less than four months before the requested date of resignation.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5003.2', 'MCTFS will not accept resignation requests made via unit diary outside the 4 to 14 month window.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and MMSR-2: confirm routing, submission date, the governing window and 120 days plus desired leave/PTAD before the requested action date.',
     when=['resign'],
     basis='target')
item('sep-letter', 'sep', "Figure 5-1 letter with the CO's endorsement (when required)", "Required only for a waiver or when the CO will not recommend a Reserve commission. Even when optional it puts the CO's recommendation on paper for Reserve Affairs.",
     how=['If IPAC wants it sent, it goes to smb.manpower.mmsr2o@usmc.mil by encrypted email.'],
     owner='You',
     due={'easMonths': -7, 'biz': 'prev'},
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5003.4', 'Submit a letter requesting resignation (Figure 5-1) via the chain of command to the CMC (MMSR-2) via an encrypted email to smb.manpower.mmsr2o@usmc.mil when:... a. A waiver of eligibility criteria of paragraph 5002 is required, or b. An officer requests a Reserve commission but is not recommended for one by the commanding officer.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', 'Figure 5-1 Note 1', 'The reporting senior must recommend and justify either offering or not offering a Reserve commission to the officer submitting the resignation regardless of whether or not they are obligated by law to accept a Reserve commission.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and MMSR-2: confirm whether the Figure 5-1 letter and command endorsement are required and the routing date.',
     when=['resign'],
     basis='target')
item('sep-pcs', 'sep', 'Check PCS orders and the resignation cancellation exception', 'The general rule bars recommendation when PCS orders were issued or notified before the request. The manual permits a cancellation request for an otherwise eligible officer under 5002.3.a(1)-(4). The requested effective date must be no later than the last day of the arrival month. Submission is at least 120 days before estimated arrival and no later than 10 working days after receipt. Paragraph (4) addresses notification less than 120 days before arrival.',
     how=['Ask the monitor and MMSR-2 whether the cancellation exception applies and calculate its deadlines immediately after receipt.', 'Record receipt, notification and estimated arrival dates. Route a written request with command endorsements to MMSR-2. Have the office confirm its working-day calendar.'],
     owner='You',
     due={'easMonths': -7, 'biz': 'prev'},
     critical=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5002.3a', "Officer resignations will not be recommended for approval if: a. The officer has been issued, or notified that he or she will be issued, Permanent Change of Station (PCS) orders before the date of the officer's request.", 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5002.3.a(1)-(4)', 'may request cancellation of the pending assignment provided they request resignation. ... The requested effective date of resignation must be no later than the last day of the month of the estimated date of arrival at the new duty station. ... Resignation requests involving cancellation of PCS orders must be forwarded to the CMC (MMSR-2) via written request with command endorsements. ... Submit the request at least 120 days before the prescribed estimated date of arrival at the new duty station, but no later than 10 working days after receipt of orders. ... Should the notification of orders be less than 120 days from the estimated date of arrival at the new duty station, the effective date of resignation will not be earlier than 120 days from the date of notification, unless the Marine requests otherwise.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='Officer assignments monitor and MMSR-2: confirm eligibility, the paragraph (4) short-notice rule, both submission deadlines and endorsements.',
     when=['resign'],
     basis='target')
item('sep-approval', 'sep', 'Resignation approved and EAS populated in MCTFS', 'Resignation approval and a populated EAS permit RA to submit the Reserve appointment request. The minimum 4-month processing interval starts at HQMC receipt of that request. A 7-month resignation target does not promise Reserve approval by EAS.',
     how=['IPAC sees approval through the EDFR.', 'Check your MOL Basic Individual Record for the EAS.', 'Ask RAM-1 to confirm and record HQMC receipt of the Reserve appointment request.', 'HQMC receipt remains pending RAM-1 confirmation after resignation approval. Give Claude the actual receipt date to record on the separate receipt item; the Reserve decision remains separate.'],
     owner='MMSR-2',
     due=None,
     critical=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5003.3', 'The CMC will also notify the unit via EDFR once a request is approved.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MARADMIN 045/25', '2', 'Reserve appointments for officers transitioning from the AC to the RC require a minimum of four months from the date received at Headquarters Marine Corps (HQMC) for approval. In cases where the officer was subject to adversity this timeline is increased.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/'),
           c('MARADMIN 045/25', '3.b.1', "Once the resignation has been approved and an EAS is populated in the resigning officer's record, CMC(RA) will submit for a Reserve commission via the Secretary of Defense.", 'https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/')],
     verify='IPAC, MMSR-2 and RAM-1: confirm resignation approval, populated EAS and actual HQMC receipt of the Reserve appointment request.',
     status='waiting',
     when=['resign'],
     basis='target')
item('sep-orders', 'sep', 'Separation orders issued', 'The unit issues orders once approval posts.',
     owner='IPAC',
     due=None,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5005.1', 'Approval/disapproval of a resignation request and authority to release is issued via the unit diary through MCTFS. Units will be notified via EDFR.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC: when do orders cut once approval posts?',
     when=['resign'],
     basis='target')
item('sep-modify', 'sep', 'Confirm the resignation change deadline', 'The manual ties a change request to before 45 days from the resignation date or commencement of separation leave. IPAC and MMSR-2 must confirm both actual anchors. Use a conservative target 46 calendar days before the earlier anchor and move a weekend back. The date stays unresolved until the actual leave start or absence of leave is confirmed.',
     how=['The date is pending confirmation by IPAC and MMSR-2. Give Claude the date the office confirms and ask Claude to record it on this item. Keep the item open until the action is complete.'],
     owner='You',
     due=None,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5004.2', 'A request for withdrawal or modification of a resignation may be made any time before 45 days from the effective date of the resignation or commencement of separation leave.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and MMSR-2: confirm the effective resignation date and actual separation-leave start, calculate the earlier boundary and enter the conservative target date.',
     when=['resign'],
     basis='target')

# ---------------- 1b: SEPARATION: retiring ----------------
# Existing category flags also select enlisted grade groups: cat1=e15,
# cat2=e67, cat3=e89. The grade group never establishes retirement eligibility.
item('ret-eligibility-e', 'sep', 'IPAC: verify active service and the retirement action',
     'FMCR transfer requires at least 20 years of active duty. Direct retirement requires at least 30. Service obligations must be met and you must be on a valid enlistment or extension. Your grade group and years entered on the board do not establish eligibility.',
     how=['Ask IPAC to review your Armed Forces Active Duty Base Date (AFADBD), prior active service, lost time and obligations. MMSR verifies creditable service before approval.',
          'Confirm FMCR transfer for 20 to 29 years or direct transfer to the Retired List at 30 or more years. Keep the profile date on the requested or approved action date; record the last active-duty day separately for BDD.',
          'MARADMIN 326/23 applies to the active component and expressly excludes the Marine Corps Reserve. MARADMIN 326/23 sets the enlisted age limit at 58; the manual and MMSR page still print 55. Ask IPAC and MMSR-2 to confirm the applicable age rule before selecting your date. If you are a Reserve Marine retiring on active service, have IPAC and MMSR-2 identify your governing service-limit and age guidance; these MARADMIN limits do not establish it.'],
     owner='You', due={'date': 'SETUP'}, critical=True,
     cite=[c(MCO, '1401.3.b', 'To be eligible for FMCR/retirement, service obligations must be met and the Marine must have 20 or more years of active duty. Enlisted retirement requires at least 30 years of active duty.', UMCO),
           c(MCO, '1401.2', 'The CMC (MMSR) shall verify creditable service toward retirement and the retired pay multiplier (RPM) prior to approval of transfer to the retired list/FMCR.', UMCO),
           c(MCO, '7004.11', 'A Marine must be serving on a valid contract of enlistment or extension to be eligible to retire or transfer to the FMCR.', UMCO),
           c(MCO, '7001.3', 'Enlisted Marines must transfer to the FMCR or retired list not later than the last day of the month in which they reach age 55.', UMCO),
           c('MARADMIN 326/23', '4', 'This MARADMIN is not applicable to the Marine Corps Reserve.', U326),
           c('MARADMIN 326/23', '3.c', 'Effective 1 July 2023, the maximum age limit for enlisted Marines\u2019 service is hereby 58 years old.', U326),
           c(MMSR, 'Traditional Retirement', '20-29 years of active service; transfer to the FMCR on the last day of the month. ... 30 or more years of active service; transfer to the Retired List the first day of the month', UMMSR)],
     verify='IPAC and MMSR-2: verify creditable active service, obligations, contract, age rule and FMCR versus Retired List eligibility.',
     when=['retire', 'enlisted'], basis='target')

for suffix, category, title, explanation, quote in [
    ('e15', 'cat1', 'E-1 to E-5: confirm whether retirement is available',
     'The published Cpl and Sgt limits are 8 and 12 years of active Marine Corps service. They do not establish 20 years of creditable active military service. Ask IPAC to review any prior service or approved exception before relying on this retirement plan.',
     'Cpl: 8 years active Marine Corps service Sgt: 12 years active Marine Corps service'),
    ('e67', 'cat2', 'E-6 to E-7: check your service limit',
     'MARADMIN 326/23 lists SSgt at 20 years and GySgt at 22 years of active military service. Confirm your grade, service limit, obligations and any approval for continued service with IPAC and the career planner.',
     'SSgt: 20 years active military service GySgt: 22 years active military service'),
    ('e89', 'cat3', 'E-8 to E-9: check your service limit',
     'MARADMIN 326/23 lists 1stSgt/MSgt at 27 years and SgtMaj/MGySgt at 30 years of active military service. Confirm your grade and any approved continuation. E-8 alone does not authorize service to 30 years.',
     '1stSgt/MSgt: 27 years active military service SgtMaj/MGySgt: 30 years active military service'),
]:
    item('ret-limits-' + suffix, 'sep', title, 'MARADMIN 326/23 applies to the active component and expressly excludes the Marine Corps Reserve. ' + explanation + ' If you are a Reserve Marine retiring on active service, have IPAC and MMSR-2 identify your governing service-limit and age guidance; these MARADMIN limits do not establish it.',
         how=['These limits do not guarantee continued service. Ask the career planner and IPAC to confirm your record with MMEA for retention and MMSR-2 for retirement processing. Do not assume a waiver.'],
         owner='You', due={'date': 'SETUP'}, critical=True,
         cite=[c('MARADMIN 326/23', '4', 'This MARADMIN is not applicable to the Marine Corps Reserve.', U326),
               c('MARADMIN 326/23', '3.b.1', quote, U326),
               c('MARADMIN 326/23', '2.c', 'These below service limits do not guarantee continued service; rather eligibility for continued service remains based on Marine Corps warfighting requirements, individual performance, and personal conduct.', U326),
               c(MCO, '7004.1', 'An enlisted Marine of the Regular Marine Corps or Marine Corps Reserve who completes 20 or more years of active duty service in the Armed Forces may request transfer to the FMCR.', UMCO)],
         verify='IPAC, unit career planner, MMEA and MMSR-2: confirm actual grade, service limit, creditable active service and any approved exception before relying on retirement eligibility.',
         when=['retire', 'enlisted', category], basis='target')

item('ret-obligations-e', 'sep', 'Review tours, deployments, grade and education obligations',
     'Review eligibility before the unit submits your request. GySgt and above normally require 2 years in grade for FMCR transfer. Tour, deployment and education obligations can affect the date. The grade group cannot distinguish SSgt from GySgt.',
     how=['Ask IPAC and the career planner to review your date of rank and service in grade. A minimum time-in-grade waiver requires DC M&RA approval.',
          'The manual requires requests at least 4 months before deployment and before the unit lock date; carrier deployment requests require at least 9 months. Ask the command and MMSR-2 to confirm applicability and enter any earlier deadline.',
          'Review obligations from PCS orders and courses. The manual bars FMCR transfer before overseas tour completion unless subject to ECFC; the MMSR page allows favorable consideration. Obtain the applicable tour rule and any waiver requirement from MMSR-2.',
          'For attendance under official orders in a military or civilian course lasting 20 weeks or more, 7004.7 requires 24 months of active duty after completion or termination before FMCR transfer. A successfully completed military or civilian course shorter than 20 weeks requires 12 months after completion. Ask MMSR-2 to confirm what applies to your record.'],
     owner='You', due={'item': 'ret-request-e', 'days': -14}, critical=True,
     cite=[c(MCO, '7004.5.a', 'Marines in the grade of gunnery sergeant or above must serve two years in their current grade before transfer to the FMCR. Waiver of this requirement may only be approved by the DC, M&RA.', UMCO),
           c(MCO, '7004.4', 'Submit requests for transfer to the FMCR at least four months before the deployment date and before the unit\u2019s official lock on date. When assigned to, or in direct support of, a carrier (CV) deployment, submit requests at least nine months before deployment.', UMCO),
           c(MCO, '7004.2.a', 'Marines serving on an overseas tour will not be approved for transfer to the FMCR before completion of their tour as prescribed in reference (bq) MCO 1300.8, Marine Corps Personnel Assignment Policy, unless subject to ECFC.', UMCO),
           c(MMSR, 'OCONUS', 'Marines serving on an overseas tour may be given favorable consideration to be approved for transfer to the FMCR before completion of their tour as prescribed in MCO 1300.8, unless subject to ECFC.', UMMSR),
           c(MCO, '7004.7', 'Marines who have attended a military or civilian course lasting 20 weeks or more will not be approved for transfer to the FMCR before the completion of 24 months of active duty following completion of the course, or after they were terminated from the course, if attendance was in compliance with official orders. Marines who have successfully completed a military or civilian course less than 20 weeks in length will not be approved for transfer to the FMCR before the completion of 12 months active duty following completion of the course.', UMCO)],
     verify='IPAC, career planner, CO and MMSR-2: confirm tour, deployment, education and grade obligations, any earlier submission deadline and required waiver; DC M&RA decides minimum time-in-grade waivers.',
     when=['retire', 'enlisted'], basis='target')

item('ret-counsel-e', 'sep', 'CO counseling and Appendix J before submission',
     'You and the CO sign the retirement preapplication checklist before the request is submitted. The CO counsels you on recall and mobilization. The board targets 7 days before submission; the required sequence is counseling before submission.',
     how=['Review Appendix J with the CO, including assignments, promotion eligibility, leave and retirement consequences. Sign it and have the CO sign. The command files it in your service record and retains it until retirement.',
          'Appendix J explains that physical disability retirement requires you to be on active duty when the Secretary of the Navy approves PEB proceedings. If disability processing applies, contact your PEBLO and MMSR-2 before proceeding.'],
     owner='CO', due={'item': 'ret-request-e', 'days': -7}, critical=True, presence=True,
     cite=[c(MCO, '7005.1', 'The Marine requesting action is required to sign a copy of Appendix J from this Manual.', UMCO),
           c(MCO, '7005.4.a(3)', 'Sign the pre-application checklist to certify that the Marine has been advised of the ramifications of retirement/transfer to the FMCR before the request is submitted.', UMCO),
           c(MCO, '7005.4.b', 'Counsel the Marine concerning his or her potential for recall to active duty and/or mobilization.', UMCO),
           c(MCO, 'Appendix J, introduction', 'Upon completion, file a copy of this checklist in the Marine\u2019s service record and forward the request via unit diary or other appropriate means to CMC (MMSR). For administrative purposes, the Marine\u2019s parent command will retain the checklist until the actual retirement date.', UMCO),
           c(MCO, '7005.3', 'in order to qualify for physical disability retirement benefits outlined in 10 U.S.C. Chapter 61, a Marine must be on active duty at the time the Secretary of the Navy approves any proceedings of a Physical Evaluation Board (PEB).', UMCO)],
     verify='CO, IPAC and MMSR-2: confirm counseling, both Appendix J signatures and service-record filing before submission; PEBLO confirms any disability processing.',
     when=['retire', 'enlisted'], basis='target')

item('ret-waiver-e', 'sep', 'Confirm any waiver package before submission',
     'A request needing a waiver goes to MMSR-2 through the chain of command by separate correspondence. A diary entry does not request an eligibility waiver. A request outside the current 6-to-18-month window requires an AA Form, justification and CO endorsement.',
     how=['Ask IPAC and MMSR-2 whether your request needs a waiver. Confirm its form, justification, endorsements and deciding authority before submission. Mark this item not applicable if no waiver is needed.',
          'For a request outside the window, the MMSR page requires O-5 or O-6 CO endorsement. Eligibility and grade waivers have separate approval requirements; a submission does not establish approval.'],
     owner='You', due={'item': 'ret-request-e', 'days': -7},
     cite=[c(MCO, '7004.8.a', 'A Marine requesting waiver of any criteria must submit a written request via the chain of command with justification and endorsements to CMC (MMSR-2). Requests for waivers via unit diary will be disapproved.', UMCO),
           c(MMSR, 'Outside of 6-18 month window', 'Waiver request must be submitted with an AA Form with justification and Commanding Officer Endorsement (O5 or O6) to CMC (MMSR-2E).', UMMSR)],
     verify='IPAC and MMSR-2: determine whether a waiver applies and confirm the package, submission date and deciding authority.',
     when=['retire', 'enlisted'], basis='target')
item('ret-request-o', 'sep', 'Submit the retirement request by unit diary', "The MARADMIN window is 6 to 18 months before the date you request; the order's own window is 4 to 14 months. The board sets a planning target of 9 months out, inside both. The target does not decide when approval comes; HQMC does. Do not make big personal commitments on the strength of a submitted request.",
     how=['Sign Appendix J for the service record.', 'IPAC submits by unit diary with your requested date.', "A request outside the window, or one needing a waiver, goes to MMSR-2 by separate correspondence with the chain's endorsements.", 'Supply desired leave and PTAD dates, duration and planned detachment date with the separation request. Ask IPAC and MMSR-2 to check the target against the message window, the manual window and 120 days plus desired leave/PTAD. Resolve any conflict before submission.'],
     owner='You',
     due={'easMonths': -9, 'biz': 'prev'},
     critical=True,
     presence=True,
     cite=[c('MARADMIN 175/24', '2', 'requests for retirement or resignation will be submitted not more than 18 months and not less than six months prior to the requested retirement or resignation date.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3739611/'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '2004.1', 'Submit requests for voluntary retirement, not requiring waivers, via the unit diary system in MCTFS per reference (cn) MCTFS PRIUM (Online). The officer requesting retirement is required to sign a copy of Appendix J from this Manual for inclusion in the electronic service record. Requests for retirement will be submitted not more than 14 months and not less than four months prior to the requested retirement date.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '2004.2', 'Officers requesting retirement are cautioned not to make significant personal commitments (such as buying or selling a house or business, or accepting civilian employment) based upon mere submission of a request.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2.d', 'If leave is desired in conjunction with a request for separation, the appropriate separation request should be submitted at least 120 days plus the amount of desired leave (to include PTAD) before the effective date of separation. When the request is submitted via unit diary, enter the planned detachment date (PDD) as part of the unit diary request for separation.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2.e', 'Marines anticipating terminal leave in conjunction with separation must inform the CMC (MMSR) of the date and duration of the desired leave upon submission of the request.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and MMSR-2: confirm routing, submission date, the governing window and 120 days plus desired leave/PTAD before the requested action date.',
     when=['retire', 'officer'],
     basis='target')
item('ret-request-e', 'sep', 'Unit diary: submit the enlisted retirement or FMCR request', 'The current MMSR-2 guidance applies the 6-to-18-month window to retirement and FMCR requests. Manual 7005.1 still prints 4 to 14 months. The board targets 9 months, inside both. Submission does not approve your date; do not make major personal commitments based on submission alone.',
     how=['After eligibility review and CO counseling, give the reporting unit your signed Appendix J and requested action date. The reporting unit submits by MCTFS unit diary to MMSR-2; IPAC confirms local processing.', 'Supply desired leave and PTAD dates, duration and planned detachment date with the request. Ask IPAC and MMSR-2 to check 120 days plus desired leave/PTAD and any earlier deployment deadline. Move the target earlier if needed, within the current window.', 'A request outside the current window goes by separate correspondence with justification and endorsements to MMSR-2. Confirm the AA Form and endorsements on the waiver item.'],
     owner='Reporting unit / IPAC',
     due={'easMonths': -9, 'biz': 'prev'},
     window={'from': {'easMonths': -18}, 'to': {'easMonths': -6}},
     kind='window',
     critical=True,
     presence=True,
     cite=[c('MARADMIN 175/24', '2', 'requests for retirement or resignation will be submitted not more than 18 months and not less than six months prior to the requested retirement or resignation date.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3739611/'),
           c(MMSR, 'Traditional Retirement', 'Reporting units must submit requests for retirement/transfer to the FMCR via the unit diary system per (MARADMIN 175/24) MCTFS PRIUM (100210) after having fully determined the Marine\u2019s eligibility based upon the criteria. Timeline. Submit requests for retirement/transfer to the FMCR not more than 18 months and not less than six months before the requested date.', UMMSR),
           c(MCO, '7005.1', 'Reporting units must submit requests for retirement/transfer to the FMCR via the unit diary system per reference (cn) MCTFS PRIUM (Online).', UMCO),
           c(MCO, '7005.2', 'Marines requesting retirement/transfer to the FMCR are cautioned not to make significant personal commitments (such as buying or selling a house or business) based upon mere submission of a request.', UMCO),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2.d', 'If leave is desired in conjunction with a request for separation, the appropriate separation request should be submitted at least 120 days plus the amount of desired leave (to include PTAD) before the effective date of separation. When the request is submitted via unit diary, enter the planned detachment date (PDD) as part of the unit diary request for separation.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2.e', 'Marines anticipating terminal leave in conjunction with separation must inform the CMC (MMSR) of the date and duration of the desired leave upon submission of the request.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '7005.1', 'Submit requests for retirement/transfer to the FMCR not more than 14 months and not less than four months before the requested date. Requests submitted outside this time frame are not accepted in MCTFS and must be submitted, with justification and endorsements, by separate correspondence or message to CMC (MMSR-2)', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '7005.1', 'Retirement must be on the first day of the month. Effective date of transfer to the FMCR will be the last day of the month.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '7005.1', 'The Marine requesting action is required to sign a copy of Appendix J from this Manual.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and MMSR-2: confirm routing, submission date, the governing window and 120 days plus desired leave/PTAD before the requested action date.',
     when=['retire', 'enlisted'],
     basis='target')
item('ret-receipt-e', 'sep', 'Confirm diary acceptance and HQMC receipt separately',
     'A request flag is not HQMC receipt or approval. The reporting unit confirms acceptance through EDFR and TRF. MMSR-2 acknowledges receipt with a pending flag. The board targets a check 7 days after submission; no source promises receipt within 7 days.',
     how=['Ask IPAC for the EDFR acceptance and requested date. A request RER flag of 5 or 6 records submission; a pending A or B flag records MMSR-2 acknowledgment.', 'Record actual submission and HQMC acknowledgment separately in the notes. Keep the approval item waiting until the approved flag posts.'],
     owner='IPAC', due={'item': 'ret-request-e', 'days': 7},
     cite=[c(MCO, '7006.1', 'Acceptance of the unit diary request will be indicated on the reporting unit\u2019s electronic diary feedback report (EDFR) and the Transaction Research File (TRF). A \u201crequest\u201d \u201c5\u201d or \u201c6\u201d ... (RER) flag will post in MCTFS indicating a request submission.', UMCO),
           c(MCO, '7006.2', 'A \u201crequest\u201d RER flag does not indicate receipt at Headquarters Marine Corps (HQMC). CMC (MMSR-2) acknowledges receipt of the request by entering a \u201cpending\u201d \u201cA\u201d or \u201cB\u201d RER flag in the unit diary system.', UMCO)],
     verify='IPAC and MMSR-2: confirm diary acceptance, requested date and separate HQMC acknowledgment; neither is retirement approval.',
     when=['retire', 'enlisted'], basis='target')
item('ret-pcs-e', 'sep', 'PCS cancellation: submit within 10 working days of receipt',
     'If your FMCR request involves canceling PCS orders, send it to MMSR-2 with MMEA or RAM as an information addressee within 10 working days after receipt. MMEA is not the retirement request destination. MMSR-2 must confirm the requested FMCR date against the PCS criteria.',
     how=['On receipt of orders, contact IPAC and the assignments monitor. Have them count 10 working days using the applicable office calendar. Give Claude the confirmed deadline and ask Claude to record it on this item. Keep it open until submitted.', 'Confirm the date rules in 7004.3 with MMSR-2 before requesting PCS cancellation. Mark this item not applicable if no PCS cancellation is involved.'],
     owner='You', due=None, critical=True,
     cite=[c(MCO, '7004.3.c', 'Requests involving cancellation of PCS orders and transfer to the FMCR must be forwarded to CMC (MMSR-2), with CMC (MMEA or RAM) as an information addressee. Submit the request no later than 10 working days after receipt of orders.', UMCO)],
     verify='IPAC, assignments monitor and MMSR-2: confirm receipt, the 10-working-day deadline and FMCR date; include MMEA or RAM for information.',
     when=['retire', 'enlisted'], basis='rule')
item('ret-report-e', 'sep', 'Tell the command about changes after submission',
     'After submission, the command must immediately notify MMSR-2 about medical disqualification, reassignment, promotion or selection, disciplinary action, lost time or death. The requirement continues after approval. The setup date is a planning reminder to review this duty.',
     how=['Tell IPAC and the command promptly if your status changes. They notify MMSR-2, and MMPR-2 for promotion or selection. If you are referred to IDES, contact your PEBLO; the command requests MMSR-2 disposition instructions. Do not assume the approved release can proceed.'],
     owner='CO / IPAC', due={'date': 'SETUP'},
     cite=[c(MCO, '7005.6', 'Once the request for retirement/transfer to the FMCR has been submitted, immediately notify CMC (MMSR-2) if the Marine is: ... Found not physically qualified ... Deceased; ... Reassigned; ... Promoted or selected for promotion (also notify MMPR-2); ... Processed for disciplinary action; or ... Subject of lost time (include number of days and reason).', UMCO),
           c(MCO, '7005.6.a', 'If the Marine is referred to the Integrated Disability Evaluation System, notify CMC (MMSR-2) with pertinent details and request disposition instructions.', UMCO),
           c(MCO, '7007.3', 'Once the CMC approval authority is received, immediately notify CMC (MMSR-2) by message when any of the conditions outlined in paragraph 7005.6 occur.', UMCO)],
     verify='CO, IPAC and MMSR-2: confirm required notifications and release instructions; MMPR-2 handles promotion notice and PEBLO handles disability processing.',
     when=['retire', 'enlisted'], basis='target')
item('ret-modify-e', 'sep', 'If changing the request, submit by 45 days before the action',
     'A request to modify or cancel enlisted retirement or FMCR transfer requires justification and endorsements by separate correspondence to MMSR-2 no later than 45 days before the effective date. Unit diary cannot submit it. MMSR-2 must confirm whether your reason meets the approval criteria.',
     how=['If you need a change, contact IPAC and MMSR-2 early and submit by the rule deadline. If no change is needed, mark this item not applicable. The board date counts from your action date; have IPAC confirm it against the effective date in your paperwork.', 'Cancellation requires an unconditional agreement to serve at least 2 years from approval and not request FMCR transfer during that period except for hardship or approaching service limits. It does not authorize service beyond ECFC limits.', 'After transfer to the FMCR or Retired List, a change request goes to BCNR. Before transfer, MMSR-2 confirms the route and approving authority.'],
     owner='You', due={'eas': -45}, critical=True,
     cite=[c(MCO, '7005.8.a', 'Submit requests to modify or cancel a retirement/transfer to the FMCR with justification and endorsements via separate correspondence to CMC ... not later than 45 days before the effective date. Requests can not be submitted by unit diary.', UMCO),
           c(MCO, '7005.8.e', 'Cancellation requests are unconditional and must include a statement from the Marine agreeing to extend the enlistment for an appropriate service obligation of no less than 2 years from the date the request for cancellation is approved. The Marine must also agree to not submit a request for transfer to the FMCR during that period, except for reasons of hardship or approaching service limits. A Marine will not be authorized service beyond ECFC service limits to meet a cancellation obligation.', UMCO),
           c(MCO, '7019.3', 'Requests to change previously approved FMCR/retirement requests after the member has been transferred to the FMCR or retired list must be submitted to the Board for Correction of Naval Records (BCNR).', UMCO)],
     verify='IPAC and MMSR-2: confirm applicability, effective date, the 45-day deadline, endorsements and cancellation obligation; BCNR handles changes after transfer.',
     when=['retire', 'enlisted'], basis='rule')
item('ret-pcs', 'sep', 'PCS orders and the retirement request', 'A retirement request involving PCS cancellation must be submitted no later than 10 working days after receipt of orders to MMSR-2, with MMOA as an information addressee. The deadline is unresolved until receipt and the office working-day calendar are confirmed.',
     how=['Record the PCS orders receipt date. Have the monitor and IPAC count 10 working days using the office-confirmed calendar. Enter that deadline; weekend adjustment alone cannot count working days.', 'The date is pending confirmation by the assignments monitor, IPAC and MMSR-2. Give Claude the date the office confirms and ask Claude to record it on this item. Keep the item open until the action is complete.'],
     owner='You',
     due=None,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '2003.1.d(1)(c)', 'Retirement requests involving cancellation of PCS orders must be forwarded to the CMC (MMSR-2) with the CMC (MMOA) as an information addressee. Submit the request no later than 10 working days after receipt of orders.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='Officer assignments monitor, IPAC, MMSR-2 and MMOA: confirm orders receipt, the 10-working-day deadline, submission route and information addressee.',
     when=['retire', 'officer'],
     basis='rule')
item('ret-approval', 'sep', 'Retirement or FMCR approved and the date populated in MCTFS', 'Confirm the approved action and date before relying on release authority. For enlisted Marines, MMSR-2 posts approval on EDFR with an approved RER flag of 7 or 8. A request or pending flag is not approval.',
     how=['Ask IPAC for approval and the approved date. Confirm the last active-duty day separately for BDD.', 'For enlisted requests, DC M&RA is the final Retired List approval authority; the Director, Manpower Management, has delegated FMCR approval authority. MMSR-2 processes and posts the decision. Do not use a staffing estimate as an approval deadline.'],
     owner='MMSR-2',
     due=None,
     critical=True,
     cite=[c(MCO, '7001.4', 'Final approval authority of requests for transfer to the retired list rests with the DC M&RA. The DC M&RA has delegated approval authority for requests to transfer to the FMCR to the Director, Manpower Management.', UMCO),
           c(MCO, '7006.3', 'CMC (MMSR-2) posts approvals in MCTFS which reflect on the unit\u2019s EDFR with an \u201capproved\u201d RER flag. Written authority for release or issuance of orders is not provided. The \u201capproved\u201d \u201c7\u201d or \u201c8\u201d RER flag is the authority to release.', UMCO)],
     verify='IPAC and MMSR-2: confirm approval, action and date; for enlisted requests, DC M&RA decides Retired List approval and the Director, Manpower Management, decides FMCR approval.',
     status='waiting',
     when=['retire'],
     basis='target')
item('ret-orders', 'sep', 'Retirement or FMCR orders issued', 'The responsible unit issues orders after approval. For enlisted Marines, use Figure 7-1 for FMCR or Figure 7-2 for the Retired List. Release must match the MMSR-2 approved date.',
     how=['Ask IPAC to confirm the approved date and applicable orders format. Complete the shared transition, STR, SBP and benefits items; this item does not replace those gates.'],
     owner='IPAC',
     due=None,
     cite=[c(MCO, '7006.3', 'The responsible order writing unit will issue orders and provide any required documents.', UMCO),
           c(MCO, '7007.4.a', 'Issue orders per the format contained in Figure 7-1 or 7-2.', UMCO),
           c(MCO, '7007.2', 'Release from active duty will not be made on a date other than as directed by the CMC (MMSR-2), unless a modification to the approved date is granted by the CMC (MMSR-2).', UMCO)],
     verify='IPAC, order writing unit and MMSR-2: confirm approval, applicable orders format and release date.',
     when=['retire'],
     basis='target')
item('ret-sbp', 'sep', 'Survivor Benefit Plan: counseling and the DD 2656 to DFAS 30 days before retirement', "DFAS must have the completed DD 2656 at least 30 days before your date; the board targets 45 to leave slack. Any election short of full coverage needs your spouse's notarized concurrence. No election means full coverage is deducted automatically.",
     how=['Take the MarineNet SBP counseling course together.', 'Complete the DD 2656 with IPAC; notarize the spousal concurrence if you elect less than full coverage.', 'Send it to DFAS by the date on the board and keep the receipt.'],
     owner='You and spouse',
     due={'eas': -45, 'biz': 'prev'},
     critical=True,
     presence=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1406.1', 'A completed election form (DD Form 2656) must be faxed with included Privacy Act form and mailed to DFAS at least 30 days prior to retirement or transfer to FMCR', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1406.5', 'Elections other than full coverage require spousal concurrence and must be notarized.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1406.6', 'If no election is made prior to the effective date of the retirement, DFAS (by law) will automatically deduct full SBP coverage at the full gross salary rate.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and DFAS retired pay: confirm DD 2656 submission and receipt at least 30 days before the approved action, election and spousal concurrence.',
     when=['retire'],
     basis='target')
item('ret-pay', 'sep', 'Retired pay account: DD 2656, direct deposit, myPay', 'DFAS pays retired pay from the DD 2656 data. Confirm the direct deposit account and your myPay retiree login before your date.',
     owner='You',
     due={'eas': -45},
     cite=[],
     verify='DFAS: confirm receipt of the DD 2656 and when the first retired pay posts.',
     when=['retire'],
     basis='target')
item('ret-ceremony', 'sep', 'Retirement ceremony: date, venue, guests, flag, certificates', 'Command practice, not regulation. Settle it early enough for family travel.',
     owner='You',
     due={'eas': -60},
     cite=[],
     verify='CO: the date, the venue, and who speaks.',
     when=['retire'],
     basis='target')

# ---------------- 1c: SEPARATION: EAS ----------------
item('eas-orders', 'sep', 'Separation orders and the final checkout schedule from IPAC', 'No request is needed to separate at EAS. Orders and the checkout schedule come from IPAC; confirm nothing is pending that extends you.',
     how=['Tell the career planner you are not reenlisting, in writing if asked.', 'Confirm your EAS in MOL matches the board.'],
     owner='IPAC',
     due={'eas': -30},
     cite=[],
     verify='IPAC: when do orders cut for an EAS separation at your unit?',
     when=['eas'],
     basis='target')

# ---------------- 2. SKILLBRIDGE ----------------
item('sb-coord', 'sb', 'Installation SkillBridge coordinator and the NCMIS application', 'NCMIS is the system of record. NAVMC directs return to the parent command for requirements below 20 hours per week or 8 hours per day. Confirm how both printed thresholds apply before selecting a program.',
     how=['Ask the coordinator to verify the approval route and specific provider/program MOU.', 'Obtain daily and weekly training hours in writing before choosing the program.', 'This date is a preparation target counted from the proposed start until approval. Give Claude any office-confirmed target date to record. Replace proposed dates on written approval and recheck prerequisites before departure.'],
     owner='You',
     due={'item': 'sb-start', 'days': -90},
     cite=[c('MARADMIN 280/24', '4.c', "Installation SkillBridge coordinators are in place to guide, direct, and advise both Marines and commands on SkillBridge protocols. The Navy College Management Information System (NCMIS) is the Marine Corps' SkillBridge system of record.", 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('NAVMC 1700.2B', '11', 'Marines shall return to parent commands if SkillBridge program requirements are less than 20 hours per week or eight hours per day and not be on administrative leave status.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf')],
     verify='Installation SkillBridge coordinator and approving command: confirm daily and weekly hours, application of both NAVMC thresholds and the governing approval route.',
     when=['sb'],
     basis='target')
item('sb-provider', 'sb', 'Pick the program and get the acceptance letter', 'Have the coordinator verify the specific program and provider approval/MOU before applying. Online opportunities must include live person-led training and/or a hybrid with in-person sessions. Asynchronous training must be less than 50 percent of training length.',
     how=['Get the acceptance letter with location, cost, length, employment outcome and provider contact.', 'Obtain daily and weekly hours in writing. NAVMC prints return-to-command thresholds below 20 hours per week or 8 hours per day; get their application confirmed before selection.', 'This date is a preparation target counted from the proposed start until approval. Give Claude any office-confirmed target date to record. Replace proposed dates on written approval and recheck prerequisites before departure.'],
     owner='You',
     due={'item': 'sb-start', 'days': -75},
     critical=True,
     cite=[c('NAVMC 1700.2B', 'Para 7.a(4)', 'Obtain a program acceptance letter that provides program details to include location, associated cost, length of... training, employment outcome, and POC for the SkillBridge partner.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Para 2', 'SkillBridge is not authorized to further civilian education or for experiential purposes per reference (a); securing meaningful employment is the expectation.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('2026 DoW SkillBridge MOU', '4.2.7', 'online opportunities must include virtual synchronous (i.e., live person-led) training and/or a hybrid with in-person sessions. Asynchronous training (if any) will be less than 50% of the length of the training.', 'https://www.skillbridge.mil/static/docs/2026_DoW_SkillBridge_MOU_BLANK.pdf'),
           c('NAVMC 1700.2B', '11', 'Marines shall return to parent commands if SkillBridge program requirements are less than 20 hours per week or eight hours per day and not be on administrative leave status.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', '7.a(3)', 'Verify the program meets the required criteria as outlined in Section (4d) above. Verification of DoD approved program with MOU via SkillBridge are located at web portal', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf')],
     verify='Installation SkillBridge coordinator: confirm specific program/provider approval and MOU, online format and both daily and weekly hours before selection.',
     when=['sb'],
     basis='target')
item('sb-ethics', 'sb', 'Ethics course: Developing Your Business Ethics (LLISELF301)', 'Complete ethics before packet submission and within 12 calendar months before the actual program start. The 61-day lead from a proposed start is a preparation target while approval is pending. Recheck completion and validity against the approved start.',
     how=['This date is a preparation target counted from the proposed start until approval. Give Claude any office-confirmed target date to record. Replace proposed dates on written approval and recheck prerequisites before departure.'],
     owner='You',
     due={'item': 'sb-start', 'days': -61},
     critical=True,
     cite=[c('NAVMC 1700.2B', 'Para 3.c(2)', 'Complete Developing Your Business Ethics (LLISELF301) MarineNet course, or equivalent, within 12 months prior to the program start date', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', '7.a(5)-(6)', "(5) Complete Developing Your Business Ethics (LLISELF301) MarineNet course, or equivalent, within 12 months prior to the program start date per reference (i). ... (6) Obtain commanding officer's endorsement and application approval.", 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf')],
     verify='Installation SkillBridge coordinator and approving command: confirm ethics completion before packet submission and validity within 12 calendar months before the actual start.',
     when=['sb'],
     basis='target')
item('sb-ethics-validity', 'sb', 'Check ethics validity against the actual start', 'NAVMC requires ethics completion within 12 calendar months before the actual SkillBridge start. Have the coordinator calculate the valid completion window and recheck it if the start changes.',
     how=['The date is pending confirmation by the installation SkillBridge coordinator. Give Claude the date the office confirms and ask Claude to record it on this item. Keep the item open until the action is complete.', "Give Claude the office-confirmed first and last valid ethics completion dates to record as this item's window. Record the actual program start in its notes. The office-confirmed date for this check is a target; the separate ethics completion target stays on its own item."],
     owner='You',
     due=None,
     critical=True,
     cite=[c('NAVMC 1700.2B', 'Para 3.c(2)', 'Complete Developing Your Business Ethics (LLISELF301) MarineNet course, or equivalent, within 12 months prior to the program start date', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', '7.a(5)-(6)', "(5) Complete Developing Your Business Ethics (LLISELF301) MarineNet course, or equivalent, within 12 months prior to the program start date per reference (i). ... (6) Obtain commanding officer's endorsement and application approval.", 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf')],
     verify='Installation SkillBridge coordinator and approving command: calculate the exact 12-calendar-month window from the actual start and verify the ethics completion date falls inside it before departure.',
     when=['sb'],
     basis='target')
item('sb-cover', 'sb', "CO's plan to cover your billet", 'MARADMIN 280/24 sets 120/90-day category limits and rank-based approval, while NAVMC 1700.2B uses a 180-day boundary, CO/OIC approval and no added rank/grade restrictions; authority and duration remain unresolved.',
     how=['This date is a preparation target counted from the proposed start until approval. Give Claude any office-confirmed target date to record. Replace proposed dates on written approval and recheck prerequisites before departure.'],
     owner='CO',
     due={'item': 'sb-start', 'days': -65},
     critical=True,
     cite=[c('MARADMIN 280/24', '3.c', 'Commanders at the grade of Lieutenant Colonel and above, as defined by reference (c), are designated as the approval authority for Categories I and II. General Officers are designated as the approval authority for Category III, and Category III participation cannot result in a gapped billet.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.a', 'Category I E1-E5 Up to 120 days', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.a', 'Category II E6-E7, WO-CWO3, and O1-O4 Up to 90 days', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.a', 'Category III E8-E9, CWO4-CWO5, O5 and above Up to 90 days', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('NAVMC 1700.2B', '4.a(1)', 'SkillBridge requests are forwarded to, reviewed, and approved by the first commanding officer or officer in charge (OIC) with Uniform Code of Military Justice authority.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 2', 'SkillBridge program participation is to be executed within 180 days of the end of active service (EAS)/retirement date, including leave while awaiting separation and PTAD per reference (a).', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 2.d', 'Commands shall not implement any additional restrictions on participation based on such criteria as rank/grade, education, skills, length of service, etc.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf')],
     verify='Installation SkillBridge coordinator and approving command: provide the governing version and approval route in writing. Confirm the approved total absence against the combined absence cap. Approve the sequence before dates are used.',
     when=['sb', 'cat3'],
     basis='target')
item('sb-packet', 'sb', 'SkillBridge packet to the approving commander', 'MARADMIN 280/24 sets 120/90-day category limits and rank-based approval, while NAVMC 1700.2B uses a 180-day boundary, CO/OIC approval and no added rank/grade restrictions; authority and duration remain unresolved.',
     how=['Submit the NCMIS application with the provider acceptance letter and ethics certificate.', 'Obtain the CO endorsement, billet cover plan and accountability plan.', 'Complete ethics before submission. Have the coordinator confirm the actual packet deadline before the approved start. The 60-day lead is a planning target.', "Verify completed TRS, Capstone and Commander's Verification before S-PTAD.", 'This date is a preparation target counted from the proposed start until approval. Give Claude any office-confirmed target date to record. Replace proposed dates on written approval and recheck prerequisites before departure.'],
     owner='You',
     due={'item': 'sb-start', 'days': -60},
     critical=True,
     cite=[c('MARADMIN 280/24', '3.a', 'Category I E1-E5 Up to 120 days', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.a', 'Category II E6-E7, WO-CWO3, and O1-O4 Up to 90 days', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.a', 'Category III E8-E9, CWO4-CWO5, O5 and above Up to 90 days', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.c', 'Commanders at the grade of Lieutenant Colonel and above, as defined by reference (c), are designated as the approval authority for Categories I and II. General Officers are designated as the approval authority for Category III, and Category III participation cannot result in a gapped billet.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('NAVMC 1700.2B', '4.a(1)', 'SkillBridge requests are forwarded to, reviewed, and approved by the first commanding officer or officer in charge (OIC) with Uniform Code of Military Justice authority.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 2', 'SkillBridge program participation is to be executed within 180 days of the end of active service (EAS)/retirement date, including leave while awaiting separation and PTAD per reference (a).', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 2.d', 'Commands shall not implement any additional restrictions on participation based on such criteria as rank/grade, education, skills, length of service, etc.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 7', 'Commanders are responsible for ensuring all Marines participating in S-PTAD have completed all pre-separation and transition requirements in accordance with reference (a).', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 3.c', 'Have attended and completed requirements of the Transition Readiness Seminar 180 days prior to separation.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf')],
     verify='Installation SkillBridge coordinator and approving command: provide the governing version and approval route in writing. Confirm the approved total absence against the combined absence cap. Approve the sequence before dates are used.',
     when=['sb'],
     basis='target')
item('sb-approval', 'sb', 'SkillBridge approved', 'Written command approval is required before participation. Use a proposed start to schedule the acceptance letter, ethics course and packet beforehand. On approval, give Claude the approved dates to replace the proposal and record the approval date separately. Recheck completed prerequisites and ethics validity before departure.',
     owner='Approving commander',
     due=None,
     critical=True,
     cite=[c('NAVMC 1700.2B', '7.a(5)-(6)', "(5) Complete Developing Your Business Ethics (LLISELF301) MarineNet course, or equivalent, within 12 months prior to the program start date per reference (i). ... (6) Obtain commanding officer's endorsement and application approval.", 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf')],
     verify='Installation SkillBridge coordinator and approving command: confirm written approval, actual approval date and approved start/end before participation.',
     status='waiting',
     when=['sb'],
     basis='target')
item('sb-sequence', 'sb', 'Confirm the approved total absence and sequence', 'MARADMIN 280/24 sets 120/90-day category limits and rank-based approval, while NAVMC 1700.2B uses a 180-day boundary, CO/OIC approval and no added rank/grade restrictions; authority and duration remain unresolved.',
     how=['Give the coordinator and approving command the complete SkillBridge, PTAD, leave and liberty calendar.', 'MARADMIN 280/24 requires PTAD before leave within its category cap. Obtain written confirmation of the governing duration policy and total absence before departure.', 'This date is a preparation target counted from the proposed start until approval. Give Claude any office-confirmed target date to record. Replace proposed dates on written approval and recheck prerequisites before departure.'],
     owner='You',
     due={'item': 'sb-start', 'days': -65},
     critical=True,
     cite=[c('MARADMIN 280/24', '3.b', 'PTAD or leave in conjunction with SkillBridge is authorized. However, the combined period of absence from duties must fall within the three category timeline/duration limits. If used in conjunction, all authorized PTAD (e.g. Transition PTAD and Skillbridge PTAD) must be executed prior to any authorized leave (e.g. Terminal leave).', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.a', 'Category I E1-E5 Up to 120 days', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.a', 'Category II E6-E7, WO-CWO3, and O1-O4 Up to 90 days', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.a', 'Category III E8-E9, CWO4-CWO5, O5 and above Up to 90 days', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.c', 'Commanders at the grade of Lieutenant Colonel and above, as defined by reference (c), are designated as the approval authority for Categories I and II. General Officers are designated as the approval authority for Category III, and Category III participation cannot result in a gapped billet.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('NAVMC 1700.2B', '4.a(1)', 'SkillBridge requests are forwarded to, reviewed, and approved by the first commanding officer or officer in charge (OIC) with Uniform Code of Military Justice authority.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 2', 'SkillBridge program participation is to be executed within 180 days of the end of active service (EAS)/retirement date, including leave while awaiting separation and PTAD per reference (a).', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 2.d', 'Commands shall not implement any additional restrictions on participation based on such criteria as rank/grade, education, skills, length of service, etc.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf')],
     verify='Installation SkillBridge coordinator and approving command: provide the governing version and approval route in writing. Confirm the approved total absence against the combined absence cap. Approve the sequence before dates are used.',
     when=['sb'],
     basis='target')
item('sb-account', 'sb', 'Accountability plan with the unit', 'The command must establish detailed accountability protocols during participation. Confirm the plan before the proposed or approved start; the 65-day lead is a planning target.',
     how=['This date is a preparation target counted from the proposed start until approval. Give Claude any office-confirmed target date to record. Replace proposed dates on written approval and recheck prerequisites before departure.'],
     owner='You',
     due={'item': 'sb-start', 'days': -65},
     cite=[c('MARADMIN 280/24', '3.b', 'During SkillBridge participation, Marines are subject to the UCMJ and Commanders are required to establish detailed accountability protocols.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/')],
     verify='Installation SkillBridge coordinator and approving command: confirm the contact schedule and accountability plan before departure.',
     when=['sb'],
     basis='target')
item('sb-run', 'sb', 'SkillBridge', 'MARADMIN 280/24 sets 120/90-day category limits and rank-based approval, while NAVMC 1700.2B uses a 180-day boundary, CO/OIC approval and no added rank/grade restrictions; authority and duration remain unresolved. Confirm the approved start/end and all prerequisites before S-PTAD. MARADMIN 280/24 prohibits extending obligated service to finish the program.',
     owner='You',
     due={'sb': 'start'},
     window={'from': {'sb': 'start'}, 'to': {'sb': 'end'}},
     kind='window',
     critical=True,
     cite=[c('MARADMIN 280/24', '3.b', 'Marines are not authorized to extend obligated service to complete the SkillBridge program.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.a', 'Category I E1-E5 Up to 120 days', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.a', 'Category II E6-E7, WO-CWO3, and O1-O4 Up to 90 days', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.a', 'Category III E8-E9, CWO4-CWO5, O5 and above Up to 90 days', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('MARADMIN 280/24', '3.c', 'Commanders at the grade of Lieutenant Colonel and above, as defined by reference (c), are designated as the approval authority for Categories I and II. General Officers are designated as the approval authority for Category III, and Category III participation cannot result in a gapped billet.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/'),
           c('NAVMC 1700.2B', '4.a(1)', 'SkillBridge requests are forwarded to, reviewed, and approved by the first commanding officer or officer in charge (OIC) with Uniform Code of Military Justice authority.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 2', 'SkillBridge program participation is to be executed within 180 days of the end of active service (EAS)/retirement date, including leave while awaiting separation and PTAD per reference (a).', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 2.d', 'Commands shall not implement any additional restrictions on participation based on such criteria as rank/grade, education, skills, length of service, etc.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf')],
     verify='Installation SkillBridge coordinator and approving command: provide the governing version and approval route in writing. Confirm the approved total absence against the combined absence cap. Approve the sequence before dates are used.',
     when=['sb'],
     basis='target')
item('sb-start', 'sb', 'SkillBridge start: proposed, then approved', 'Use a proposed program start in your profile to plan preparation while approval is pending. Preparation dates are targets. Replace the proposal with the approved start after written command approval and recheck prerequisites, ethics validity and the absence sequence. Recording approval does not change the scheduled start.',
     how=['Give Claude the proposed start and ask Claude to record it in the profile with a note that approval is pending.', 'On written approval, give Claude the approved start/end dates to replace the proposal and the actual approval date to record in notes.'],
     owner='You',
     due={'sb': 'start'},
     kind='milestone',
     cite=[c('NAVMC 1700.2B', '4.a(1)', 'SkillBridge requests are forwarded to, reviewed, and approved by the first commanding officer or officer in charge (OIC) with Uniform Code of Military Justice authority.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 2', 'SkillBridge program participation is to be executed within 180 days of the end of active service (EAS)/retirement date, including leave while awaiting separation and PTAD per reference (a).', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', 'Encl (2) para 2.d', 'Commands shall not implement any additional restrictions on participation based on such criteria as rank/grade, education, skills, length of service, etc.', 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf'),
           c('NAVMC 1700.2B', '7.a(5)-(6)', "(5) Complete Developing Your Business Ethics (LLISELF301) MarineNet course, or equivalent, within 12 months prior to the program start date per reference (i). ... (6) Obtain commanding officer's endorsement and application approval.", 'https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf')],
     verify='Installation SkillBridge coordinator and approving command: confirm the proposed schedule, then written approval and the final start/end before participation.',
     when=['sb'],
     basis='target')
item('sb-cert', 'sb', 'Certification exam before the program ends', 'Sit any funded exam while the program still covers it.',
     owner='You',
     due={'sb': 'end'},
     cite=[],
     verify='Provider: the exam date and what the program funds.',
     when=['sb'],
     basis='target')

# ---------------- 3. VA AND MEDICAL ----------------
item('va-vso', 'va', 'Pick an accredited VSO and sign VA Form 21-22', 'Your lead for the claim, at no cost. They build and file the BDD claim with you and represent you after.',
     how=['Choose an accredited VSO that can assist with your claim and confirm its intake availability.', 'Appoint the recognized VSO on VA Form 21-22.'],
     owner='You',
     due={'eas': -200, 'biz': 'prev'},
     critical=True,
     cite=[c('VA Benefits and Services Participant Guide v6.1', 'Module 3, p. 80', 'Chartered VSOs offer these services for free.', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf'),
           c('VA Benefits and Services Participant Guide v6.1', 'Module 3', 'To appoint a recognized VSO as your representative, download the VA Form 21-22', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf')],
     verify='VA benefits office or accredited VSO: confirm accreditation, appointment on VA Form 21-22 and actual intake date.',
     basis='target')
item('va-shpe', 'va', 'Schedule the separation physical (SHPE)', 'The manual says schedule SHPE at least 6 months before separation. The VA guide says a completed SHA returned to DoD at least 30 days before separation can satisfy the discharge examination requirement. Confirm the clinic accepts the completed and returned SHA; a scheduled VA exam alone does not satisfy this condition.',
     owner='You',
     due={'easMonths': -6},
     critical=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1011.2', 'A Marine should schedule a SHPE medical evaluation not less than six months before the effective date of separation to allow time for necessary medical treatment or disability processing.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('VA Benefits and Services Participant Guide v6.1', 'Module 3', 'If you complete your SHA exam and return it to DOD at least 30 days before separation, it will serve as your DOD discharge exam, and you will not need to complete a SHPE.', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf')],
     verify='Military medical clinic and VA: confirm scheduling, SHA completion and return to DoD, and whether a separate SHPE remains required.',
     basis='rule')
item('va-records', 'va', 'Export complete medical, dental and service records', 'Keep personal copies for your BDD claim and record review. The VA guide requires scanned physical, electronic and applicable civilian records for your entire service history. Personal export does not satisfy delivery of the complete STR to IPAC.',
     how=['Request complete military medical and dental records, including older paper records.', 'Request civilian medical and dental records. Confirm the export needed for the claim and STR.', 'Complete the separate STR delivery gate before the first applicable absence or separation action.'],
     owner='You',
     due={'eas': -190},
     cite=[c('VA Benefits and Services Participant Guide v6.1', 'Module 3', 'Provide a copy of your scanned physical records, electronic medical records and outsourced civilian records (if applicable) for your entire service history.', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1101.7.b', 'Every Marine must submit their Service Treatment Record (STR) to their Marine Corps activity effecting separations (IPAC/Administration RUC) prior to execution of transitional PTAD, terminal leave, transfer to the IRR, separation or retirement. A complete STR includes: Service provided medical and dental documentation, civilian provided medical and dental documentation, Armed Forces Health Longitudinal Technology Application (AHLTA) web print (AWP) information, and a completed DD Form 2963.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='Military medical records office, VA and IPAC: confirm complete exports, records for BDD and STR delivery/acceptance before the first applicable action.',
     basis='target')
item('va-service-end', 'va', 'Confirmed last day of active duty', 'The BDD window uses the last active-duty day. For ordinary Retired List retirement, the manual makes that the day before the effective retirement date. IPAC and MMSR-2 must confirm FMCR, exception and other individual service-end dates separately from the approved action date.',
     how=['The last active-duty day is pending IPAC and MMSR-2 confirmation. Give Claude that date and the separate approved retirement or FMCR action date. Ask Claude to record the confirmed last active-duty day here and the action date on the retirement/FMCR item.', "Have VA or your accredited VSO confirm both BDD window endpoints. Keep this milestone's date equal to the confirmed last active-duty day when recording completion."],
     owner='You',
     due=None,
     kind='milestone',
     critical=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '7007.1.a', 'The first day of the month is the effective date of retirement and the last day of active duty is the preceeding day.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '7007.1.b', 'Transfer to the FMCR is effected on the last day of the month and Marines assume a status in the FMCR on the first day of the following month.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('VA Benefits and Services Participant Guide v6.1', 'Module 3', 'Submit your BDD claims between 180 and 90 days before the very last day of service on active duty. For BDD purposes, this separation date is not when you start Transitional or Terminal Leave or Permissive Temporary Duty for seeking a home.', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf')],
     verify='IPAC and MMSR-2: confirm the last active-duty day separately from the Retired List/FMCR action. VA benefits office or accredited VSO: confirm the BDD window counted from that service-end date.',
     basis='rule')
item('va-str', 'va', 'Deliver the complete STR before absence or separation', 'Submit the complete STR to IPAC/Administration RUC before transition PTAD, terminal leave, IRR transfer, separation or retirement. Include service and civilian medical/dental records, the required AHLTA web print and DD Form 2963. Confirm the required export with medical records and IPAC.',
     how=['The date is pending confirmation by the military medical records office and IPAC. Give Claude the date the office confirms and ask Claude to record it on this item. Keep the item open until the action is complete.'],
     owner='You',
     due=None,
     critical=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1101.7.b', 'Every Marine must submit their Service Treatment Record (STR) to their Marine Corps activity effecting separations (IPAC/Administration RUC) prior to execution of transitional PTAD, terminal leave, transfer to the IRR, separation or retirement. A complete STR includes: Service provided medical and dental documentation, civilian provided medical and dental documentation, Armed Forces Health Longitudinal Technology Application (AHLTA) web print (AWP) information, and a completed DD Form 2963.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='Military medical records office and IPAC: enter the delivery deadline and confirm the required export and acceptance of the complete STR before the first applicable action.',
     basis='rule')
item('va-conditions', 'va', 'Build the condition list', 'Every issue, documented or not. The VSO works from this list.',
     owner='You',
     due={'eas': -185},
     critical=True,
     cite=[],
     verify=None,
     basis='target')
item('va-sickcall', 'va', 'Get every undocumented condition seen at medical', 'A condition first documented after separation is much harder to service connect.',
     owner='You',
     due={'eas': -120},
     critical=True,
     cite=[],
     verify=None,
     basis='target')
item('va-hearing', 'va', 'Separation hearing test on record', 'Baseline for any hearing or tinnitus claim.',
     owner='You',
     due={'eas': -120},
     cite=[],
     verify=None,
     basis='target')
item('va-exposure', 'va', 'Get your deployment exposures on record', 'Open ILER, save the Individual Exposure Summary, add missing events, and put every exposure in front of military medical before you file.',
     owner='You',
     due={'eas': -120},
     cite=[],
     verify='VSO: ILER review for every deployment.',
     basis='target')
item('va-bh', 'va', 'Get a behavioral health evaluation on record', 'Sleep, stress, mood: documented in service, not after.',
     how=['Tell it straight: sleep, stress, work and home.'],
     owner='You',
     due={'eas': -120},
     critical=True,
     cite=[],
     verify=None,
     basis='target')
item('va-reserve', 'va', 'Confirm DAP medical qualification with medical and the Career Counselor', 'Settle how a claim interacts with Reserve medical standards before the DAP request goes in.',
     owner='You',
     due={'eas': -150},
     cite=[],
     verify=None,
     when=['reserve'],
     basis='target')
item('va-parta', 'va', 'SHA Part A self-assessment', 'Must be filed with the BDD claim.',
     owner='You',
     due={'item': 'va-file', 'days': 0},
     cite=[c('VA Benefits and Services Participant Guide v6.1', 'Module 3', 'Provide a completed Separation Health Assessment (SHA)-Part A Self-Assessment.', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf')],
     verify='VA benefits office or accredited VSO: confirm the completed Part A is included with the actual BDD submission.',
     basis='rule')
item('va-file', 'va', 'File the BDD claim (VA 21-526EZ) with your VSO', 'Needs a known separation date. File early in the window. You must be available for VA exams for 45 days after you file, so plan travel around that.',
     how=['The filing window is pending the confirmed last active-duty day. Give Claude the date IPAC confirms to record on the service-end milestone. VA or your VSO must confirm the endpoints before filing. The filing target may move back for a weekend; the actual window endpoints do not.'],
     owner='VSO',
     due={'item': 'va-service-end', 'days': -150, 'biz': 'prev'},
     window={'from': {'item': 'va-service-end', 'days': -180}, 'to': {'item': 'va-service-end', 'days': -90}},
     kind='window',
     critical=True,
     cite=[c('VA Benefits and Services Participant Guide v6.1', 'Module 3', "You'll need to have a known Separation Date and do the following:", 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf'),
           c('VA Benefits and Services Participant Guide v6.1', 'Module 3', 'Submit your BDD claims between 180 and 90 days before the very last day of service on active duty. For BDD purposes, this separation date is not when you start Transitional or Terminal Leave or Permissive Temporary Duty for seeking a home.', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf'),
           c('VA Benefits and Services Participant Guide v6.1', 'Module 3', 'Be available 45 days after submitting your BDD claim to attend the required medical exam(s)', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf')],
     verify='VA benefits office or accredited VSO: confirm the known service-end date, actual filing date, required records, Part A and 45-day examination availability.',
     basis='target')
item('va-exams', 'va', 'VA exams (you must be available 45 days after filing)', 'A planning target. Until you mark the BDD filing done, this window is projected from the filing target; once it is done, it counts from the day you filed. VA schedules the exams after you file, and you must be available for 45 days from the filing date. Where the exams are, and whether exam days count as duty time, are questions for VA and IPAC.',
     owner='You',
     due={'item': 'va-file', 'days': 45},
     window={'from': {'item': 'va-file', 'days': 0}, 'to': {'item': 'va-file', 'days': 45}},
     kind='window',
     presence=True,
     cite=[c('VA Benefits and Services Participant Guide v6.1', 'Module 3', 'Be available 45 days after submitting your BDD claim to attend the required medical exam(s)', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf')],
     verify='VSO: the day the claim was filed and the exam dates VA gives you. VA and IPAC: exam location, and duty status for exam days.',
     basis='target')
item('va-add', 'va', 'Confirm late additions with VA before BDD closes', 'The copied guide establishes BDD filing between 180 and 90 days before the final active-duty day. It does not establish the procedure for adding conditions to an existing BDD claim. Confirm that procedure with VA before the window closes.',
     how=['Day 90 before the last active-duty day is a planning target for confirming additions with VA or your accredited VSO. The additions procedure and actual deadline remain pending VA confirmation.', 'Give Claude any deadline VA confirms to record as a date rule on this task or a separate actionable task. Record the confirming office and its confirmation in notes. Label that date a confirmed event and preserve the day-90 planning target separately. Use basis rule only if a quoted source sets the deadline.'],
     owner='You',
     due={'item': 'va-service-end', 'days': -90},
     kind='task',
     critical=True,
     cite=[c('VA Benefits and Services Participant Guide v6.1', 'Module 3', 'Submit your BDD claims between 180 and 90 days before the very last day of service on active duty. For BDD purposes, this separation date is not when you start Transitional or Terminal Leave or Permissive Temporary Duty for seeking a home.', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf')],
     verify='VA benefits office or accredited VSO: confirm the procedure and actual deadline for adding conditions to your existing claim.',
     basis='target')
item('va-sha', 'va', 'SHA return cutoff if using it instead of a SHPE', 'If the SHA is used instead of a separate SHPE, return completed results to DoD at least 30 days before your confirmed last active-duty day. The military medical clinic and VA must confirm applicability, return and acceptance. The cutoff stays pending until the office confirms your service-end date.',
     owner='Medical',
     due={'item': 'va-service-end', 'days': -30},
     cite=[c('VA Benefits and Services Participant Guide v6.1', 'Module 3', 'If you complete your SHA exam and return it to DOD at least 30 days before separation, it will serve as your DOD discharge exam, and you will not need to complete a SHPE.', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf')],
     verify='Military medical clinic and VA: confirm completed SHA results returned to DoD by the required date and whether SHPE is still needed.',
     basis='rule')
item('va-intent', 'va', 'VA intent to file: confirmed receipt date', 'BDD is the preferred route; intent to file protects the potential effective date when BDD is missed.',
     how=['If BDD is missed, ask VA or your accredited VSO about an intent to file. Keep the VA receipt or automatic online intent confirmation.', 'Give Claude the actual date VA records and ask Claude to record that fixed date here. Do not substitute EAS, setup day or a planned submission date.', 'At the same time, have VA or your VSO confirm the calendar anniversary and ask Claude to set that fixed rule deadline on va-itf-complete. Keep this event undated until the actual intent is recorded. Mark it not applicable if no intent is needed.'],
     due=None, kind='milestone',
     cite=[c(VITF, "What's an intent to file?", 'An intent to file sets a potential start date (or effective date) for your benefits.', UITF), c(VITF, 'How long do I have to file my claim after I notify VA of my intent?', 'After you notify us of your intent to file, you have 1 year to complete and file your claim.', UITF), c(VAG, 'Module 3', 'Submit your BDD claims between 180 and 90 days before the very last day of service on active duty.', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf')],
     verify='VA benefits office or accredited VSO: confirm whether an intent is needed, the actual VA intent date and the potential effective date.', basis='rule')
item('va-itf-complete', 'va', 'Complete the VA claim within 1 year of intent to file', 'Complete and file your claim within 1 year of the actual VA intent date on va-intent. This boundary is separate from the existing separation effective-date item.',
     how=['After recording va-intent, give Claude the exact calendar-year deadline confirmed by VA or your VSO and ask Claude to set a fixed rule date here. Keep it undated until the actual intent date is known.', 'Use a calendar year, including leap years. The board cannot add calendar years to another item automatically; do not use a 365-day approximation.', 'Confirm VA received the completed claim before this deadline and retain the receipt. VA decides the effective date and entitlement. Mark this item not applicable if no intent is needed.'],
     due=None, critical=True,
     cite=[c(VITF, 'How long do I have to file my claim after I notify VA of my intent?', 'After you notify us of your intent to file, you have 1 year to complete and file your claim.', UITF)],
     verify='VA benefits office or accredited VSO: confirm the exact 1-year filing deadline from the actual intent date and receipt of the completed claim.', basis='rule')
item('va-decision', 'va', 'VA rating decision', 'BDD aims for a decision at or soon after separation.',
     owner='VA',
     due={'eas': 30},
     kind='milestone',
     cite=[],
     verify=None,
     status='waiting',
     basis='target')
item('va-health', 'va', 'Enroll in VA health care', 'The guide permits application no earlier than 1 year before separation and any time afterward. It sets no general application deadline. Have VA confirm individual eligibility and coordinate your other coverage.',
     owner='You',
     due={'eas': 30},
     cite=[c('VA Benefits and Services Participant Guide v6.1', 'Module 2, p. 41', 'You may apply no earlier than one year before separation, but any time after separation. There is no deadline to apply for VA health care.', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf')],
     verify='VA benefits office: confirm eligibility, application status and the care start date.',
     basis='target')
item('va-drill', 'va', 'Set up the yearly VA and drill pay reconciliation', 'The copied pack does not establish how to count paid training days or complete the VA waiver notice. Have VA and your gaining Reserve unit reconcile actual fiscal-year paid days and confirm the notice deadline. Do not assume every 2-day weekend has 4 paid assemblies.',
     how=['Ask VA and the unit for the applicable notice and instructions. Compare the actual paid assemblies and active-duty days with the notice and respond by its confirmed deadline.', 'Paid-day counting, the applicable notice instructions and response deadline remain pending VA benefits office and gaining Reserve unit administration confirmation.'],
     owner='You',
     due={'eas': 60},
     cite=[],
     verify='VA benefits office and gaining Reserve unit administration: confirm paid-day counting, discrepancies, the applicable notice and response deadline.',
     when=['reserve'],
     basis='target')
item('va-dental', 'va', 'Confirm VA dental eligibility and application deadline', 'The manual prints 180 days of service and application within 90 days after release. It also uses the DD 214 certification of a complete exam and all appropriate treatment within 90 days before separation. The copied pack does not establish current Class II criteria. VA dental must settle your eligibility and deadline promptly.',
     how=['Current Class II criteria and application deadline remain pending VA dental clinic confirmation.'],
     owner='You',
     due={'eas': 30},
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1101.4.e(1)-(3)', 'The veteran must have served not less than 180 days of active duty to be eligible for dental treatment provided by VA. ... Application for VA dental treatment must be made within 90 days of discharge or release from active duty. ... The veteran will not be eligible for dental treatment if the DD Form 214 contains a statement that the veteran was provided a complete dental ... examination and all appropriate dental services and treatment were completed within 90 days before separation from active duty.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='VA dental clinic and accredited VSO: confirm current Class II service/discharge criteria, the DD 214 examination/treatment entry and actual application deadline. IPAC: confirm the entry.',
     basis='target')
item('va-net', 'va', 'Confirm the claim effective date and 1-year filing boundary', 'The guide illustrates a claim received within 1 year of separation becoming effective the day after separation. That example does not decide individual entitlement. Have VA confirm your claim effective date and filing deadline.',
     owner='You',
     due={'easMonths': 12},
     kind='marker',
     cite=[c('VA Benefits and Services Participant Guide v6.1', 'Module 3, p. 73', 'Because VA received it within one year of your separation, your claim is effective on October 19, 2019', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf')],
     verify='VA benefits office or accredited VSO: confirm the individual effective date, entitlement and filing deadline before the 1-year boundary.',
     basis='target')

# ---------------- 4. RESERVE (DAP) ----------------
item('dap-ram1', 'dap', 'Email RAM-1: Reserve commission timeline', 'Resignation approval and a populated EAS permit RA submission. Reserve appointment approval requires at least 4 months from HQMC receipt of the request, with more time for adverse cases. Record and confirm that receipt date; the resignation planning target does not promise approval by EAS.',
     how=['Give RAM-1 the requested separation date and ask about the applicable scroll.', 'Confirm and record HQMC receipt of the Reserve appointment request with RAM-1.', 'Ask RAM-1 to confirm processing time and Reserve appointment status.', 'Give Claude the actual HQMC receipt date that RAM-1 confirms to record on the separate receipt item. The date RAM-1 replies is not the receipt date.'],
     owner='You',
     due={'easMonths': -7, 'biz': 'prev'},
     critical=True,
     cite=[c('MARADMIN 045/25', '2', 'Reserve appointments for officers transitioning from the AC to the RC require a minimum of four months from the date received at Headquarters Marine Corps (HQMC) for approval. In cases where the officer was subject to adversity this timeline is increased.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/'),
           c('MARADMIN 045/25', '3.b.1', "Once the resignation has been approved and an EAS is populated in the resigning officer's record, CMC(RA) will submit for a Reserve commission via the Secretary of Defense.", 'https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5004 (Reserve commission scrolling)', 'Officers without adverse information in any Department of the Navy systems of record are then placed on the non-adverse scroll and routed from HQMC, RA Division via the DC M&RA to the SecDef. The non-adverse transitional scrolling process may require a longer lead time than the minimum length of time required by the resignation process (four months per paragraph 5003 of this Manual).', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='RAM-1, IPAC and MMSR-2: confirm HQMC receipt date, populated EAS, scroll and remaining processing interval.',
     when=['reserve', 'resign'],
     basis='target')
item('dap-receipt', 'dap', 'RAM-1 confirms HQMC receipt of the Reserve appointment request', 'The minimum 4-month processing interval starts at HQMC receipt of the Reserve appointment request. EAS minus 4 calendar months is the latest ordinary receipt planning boundary, not an approval guarantee. Adverse cases need more time. Actual receipt remains pending RAM-1 confirmation.',
     how=['Ask RAM-1 for the actual HQMC receipt date. Give Claude that date and ask Claude to record completion with the actual receipt date on this item. Keep it waiting until RAM-1 confirms receipt.', 'The Reserve appointment decision is separate. IPAC and RAM-1 must confirm approval in MCTFS on the existing commission item.'],
     owner='You',
     due={'easMonths': -4},
     critical=True,
     cite=[c('MARADMIN 045/25', '2', 'Reserve appointments for officers transitioning from the AC to the RC require a minimum of four months from the date received at Headquarters Marine Corps (HQMC) for approval. In cases where the officer was subject to adversity this timeline is increased.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/'),
           c('MARADMIN 045/25', '3.b.1', "Once the resignation has been approved and an EAS is populated in the resigning officer's record, CMC(RA) will submit for a Reserve commission via the Secretary of Defense.", 'https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '5004.1.b(1)', "The non-adverse transitional scrolling process does not begin until HQMC (RA Division) receives notice of an officer's commission request.", 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='RAM-1, IPAC and MMSR-2: confirm the actual HQMC receipt date separately from resignation approval and the Reserve appointment decision.',
     status='waiting',
     when=['reserve', 'resign'],
     basis='target')
item('dap-cc', 'dap', 'Career Counselor: DAP brief, SMCR or IMA, billet options', 'The counselor submits the DAP request with you.',
     owner='You',
     due={'easMonths': -7, 'biz': 'prev'},
     cite=[c('MARADMIN 454/26', '6.a', 'Marines interested in DAP should contact their unit Career Counselor for information regarding SMCR and IMA opportunities, benefits, incentives, lateral move opportunities, and for assistance with the submission of a DAP request.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify='Reserve career planner, Career Counselor and RAC-3: confirm SMCR or IMA options and the DAP submission route.',
     when=['reserve'],
     basis='target')
item('dap-billet', 'dap', 'Choose the billet at your unit of choice', 'Guaranteed once DAP is approved.',
     owner='You',
     due={'eas': -190},
     cite=[c('MARADMIN 454/26', '4.a', 'Transitioning Marines may select an available SMCR or IMA billet at their unit of choice, subject to availability... Upon DAP approval, assignment to the selected billet is guaranteed.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify='Reserve career planner, Career Counselor and RAC-3: confirm billet availability and the assignment guaranteed by actual DAP approval.',
     when=['reserve'],
     basis='target')
item('dap-bonus', 'dap', 'Check TFRS for SMCR affiliation incentives', 'Bonuses carry a service obligation. Read the terms.',
     owner='Career Counselor',
     due={'eas': -190},
     cite=[c('MARADMIN 454/26', '4.c', 'Marines affiliating with an SMCR unit through DAP may qualify for monetary incentives in exchange for a specified service obligation.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify='Career Counselor and RAC-3: confirm the offered incentive, eligibility and its service obligation before acceptance.',
     when=['reserve'],
     basis='target')
item('dap-package', 'dap', 'DAP package ready with the Career Counselor', 'Have the billet choice and the request ready before the window opens, so it goes in on the first day.',
     owner='You',
     due={'eas': -185},
     critical=True,
     cite=[c('MARADMIN 454/26', '5.b', 'Officers may submit a DAP request no earlier than (NET) 180 days prior to EAS and no later than (NLT) 60 calendar days prior to EAS.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/'),
           c('MARADMIN 454/26', '5.c', 'Enlisted Marines requesting direct affiliation may submit a DAP request NET 180 days prior to EAS and NLT 30 calendar days prior to EAS.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify='Career Counselor and RAC-3: check package completeness against the applicable officer or enlisted DAP window.',
     when=['reserve'],
     basis='target')
item('dap-request-o', 'dap', 'Submit the DAP request', 'The officer window opens 180 days out and closes 60 days out. Submit on the first day.',
     owner='You',
     due={'eas': -180},
     window={'from': {'eas': -180}, 'to': {'eas': -60}},
     kind='window',
     critical=True,
     cite=[c('MARADMIN 454/26', '5.b', 'Officers may submit a DAP request no earlier than (NET) 180 days prior to EAS and no later than (NLT) 60 calendar days prior to EAS.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify='Career Counselor and RAC-3: confirm officer eligibility and submit within the 180-to-60-day window. Day 180 is the board target.',
     when=['reserve', 'officer'],
     basis='target')
item('dap-request-e', 'dap', 'Submit the DAP request', 'The enlisted window opens 180 days out and closes 30 days out. Submit on the first day.',
     owner='You',
     due={'eas': -180},
     window={'from': {'eas': -180}, 'to': {'eas': -30}},
     kind='window',
     critical=True,
     cite=[c('MARADMIN 454/26', '5.c', 'Enlisted Marines requesting direct affiliation may submit a DAP request NET 180 days prior to EAS and NLT 30 calendar days prior to EAS.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify='Career Counselor and RAC-3: confirm enlisted eligibility and submit within the 180-to-30-day window. Day 180 is the board target.',
     when=['reserve', 'enlisted'],
     basis='target')
item('dap-commission', 'dap', 'Reserve commission approved', 'Reserve Affairs does not notify you. Approval shows as the planned separation code in MCTFS. Check monthly. No approval before EAS means no DAP.',
     how=['The Reserve appointment decision remains pending RAM-1 and IPAC confirmation in the MCTFS record.'],
     owner='Reserve Affairs',
     due={'eas': -30},
     critical=True,
     cite=[c('MARADMIN 045/25', '4.a', 'RA does not directly notify individual officers who are approved for a Reserve commission. Approval is reflected in the planned separations code within Marine Corps Total Force System (MCTFS).', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/'),
           c('MARADMIN 454/26', '5.b', 'Officers who do not receive approval for a Reserve commission prior to EAS are not eligible for DAP.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify='RAM-1 and IPAC: confirm Reserve commission approval and the MCTFS separation code before EAS.',
     status='waiting',
     when=['reserve', 'resign'],
     basis='target')
item('dap-763', 'dap', 'NAVMC 763 signed before separation', 'The legal record of your Reserve commission. An administering officer senior to you signs it before you separate.',
     how=['Get it from IPAC, get the signature, return it for upload to your OMPF.'],
     owner='IPAC',
     due={'eas': -10},
     critical=True,
     presence=True,
     cite=[c('MARADMIN 045/25', '5.b', 'This updated NAVMC 763 must be issued to the separating officer before their separation takes place. The separating officer is responsible for obtaining a signature from an Administering Officer who is higher in grade than the separating officer.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/')],
     verify='IPAC and higher-grade administering officer: confirm issue, signature, return and OMPF upload before separation.',
     when=['reserve', 'resign'],
     basis='target')
item('dap-checkin', 'dap', 'Check in to the gaining SMCR unit or IMA detachment', 'Miss it and you can be moved to the IRR and lose DAP benefits.',
     owner='You',
     due={'eas': 30},
     critical=True,
     cite=[c('MARADMIN 454/26', '6.b', "It is the individual Marine's responsibility to check into the gaining SMCR unit or IMA detachment within 30 calendar days after EAS.", 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify='Gaining SMCR/IMA administration and Reserve career planner: confirm check-in within 30 calendar days after EAS.',
     when=['reserve'],
     basis='rule')

# ---------------- 5. LEAVE AND PAY ----------------
item('lv-ledger', 'leave', 'Enter your leave balance from the LES', 'The leave model needs the real number. Update it each month.',
     owner='You',
     due={'date': 'SETUP'},
     cite=[],
     verify=None,
     basis='target')
item('lv-plan', 'leave', 'Leave plan: decide the balance you want at the end, then plan the blocks', 'The desired final balance is your planning choice. Sellback depends on honorable separation, prior sales and any chapter 2, 2.b exception to the 60-day career cap. A projected negative balance does not authorize advance leave. Confirm the urgent, personal or emergency purpose, limits and CO approval. A negative balance at discharge becomes excess leave subject to collection from pay.',
     how=['The payable amount and any cap exception remain pending IPAC and disbursing confirmation.'],
     owner='You',
     due={'eas': -180},
     critical=True,
     cite=[c('MCO 1050.3J', 'Ch 2 para 9.c(9)', 'Separation payments for unused accrued leave are limited to 60 days during a military career per reference (q).', 'https://www.marines.mil/portals/1/publications/mco%201050.3j.pdf'),
           c('MCO 1050.3J', 'Ch 2 para 2.b', 'A Marine who is separated or released from active duty under honorable conditions may elect to receive payment for a portion of the unused leave ... Payment of leave for Reserve Component (RC) Marines or Retired Marines activated in support of a contingency operation or RC Marines on Active Duty Operational Support (ADOS) orders not exceeding 365 days are exempt from the 60-day leave payment limitation per reference (q).', 'https://www.marines.mil/portals/1/publications/mco%201050.3j.pdf'),
           c('MCO 1050.3J', 'Ch 2 para 6.a', 'Advance leave is a means whereby Marines with limited or no accrued leave may be granted leave to resolve urgent, personal, or emergency situations. ... advance leave resulting in a negative leave balance on date of discharge, or release from active duty, becomes excess leave and is subject to checkage of pay and allowances.', 'https://www.marines.mil/portals/1/publications/mco%201050.3j.pdf'),
           c('MCO 1050.3J', 'Ch 2 para 6', 'advance leave shall be limited to the lesser of: (1) 45 days or (2) The amount of leave that shall be earned during the remaining period of active duty', 'https://www.marines.mil/portals/1/publications/mco%201050.3j.pdf'),
           c('MCO 1050.3J', 'Ch 2 para 6.d', 'Accrued leave shall be expended prior to the authorization of advance leave.', 'https://www.marines.mil/portals/1/publications/mco%201050.3j.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2e', 'Do not approve leave in excess of the number of days which the Marine can accrue before the end of current contract (ECC). Leave taken beyond that which can be earned is excess leave and results in nonentitlement to pay and allowances.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC, disbursing and CO: confirm qualifying sellback, prior sales, any cap exception and advance-leave purpose, limits and approval.',
     basis='target')
item('lv-terminal', 'leave', 'Confirm the previously requested terminal leave and PTAD dates', 'Supply desired leave/PTAD dates, duration and planned detachment date with the advance separation request. The manual says to allow 120 days plus desired leave/PTAD lead time. The 90-day board date is a final planning confirmation target. Confirm STR acceptance and all separation requirements before the first applicable absence.',
     owner='You',
     due={'eas': -90},
     cite=[c('MCO 1050.3J', 'Ch 5 para 1.c(11)(a)5', 'Officers and enlisted Marines with an approved retirement date are eligible for transition PTAD.', 'https://www.marines.mil/portals/1/publications/mco%201050.3j.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2.d', 'If leave is desired in conjunction with a request for separation, the appropriate separation request should be submitted at least 120 days plus the amount of desired leave (to include PTAD) before the effective date of separation. When the request is submitted via unit diary, enter the planned detachment date (PDD) as part of the unit diary request for separation.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2.e', 'Marines anticipating terminal leave in conjunction with separation must inform the CMC (MMSR) of the date and duration of the desired leave upon submission of the request.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1010.2', 'Terminal leave is not granted until all separation requirements--both administrative and medical--are complete. Terminal leave runs continuously from the first day of leave until the date of EAS or transfer to the Retired List/FMCR.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1101.7.b', 'Every Marine must submit their Service Treatment Record (STR) to their Marine Corps activity effecting separations (IPAC/Administration RUC) prior to execution of transitional PTAD, terminal leave, transfer to the IRR, separation or retirement. A complete STR includes: Service provided medical and dental documentation, civilian provided medical and dental documentation, Armed Forces Health Longitudinal Technology Application (AHLTA) web print (AWP) information, and a completed DD Form 2963.', 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and MMSR-2: confirm the earlier separation request and leave/PTAD lead time. IPAC, medical records and CO: confirm STR acceptance, all separation gates and approved absence dates.',
     basis='target')
item('lv-requests', 'leave', 'Leave requests in MOL for every block', 'Each block approved by the CO.',
     owner='You',
     due={'eas': -150},
     cite=[],
     verify=None,
     basis='target')
item('lv-risk-r', 'leave', 'If HQMC sets a different date, the leave math changes', 'The Director, Manpower Management can approve a different date. Watch the approval.',
     owner='You',
     due={'item': 'sep-approval', 'days': 0},
     kind='marker',
     cite=[c('MARADMIN 175/24', '3', 'The Director, Manpower Management, may approve a resignation/retirement request for a date other than the date requested based on the needs of the service', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3739611/')],
     verify='IPAC, MMSR-2 and disbursing: confirm the approved resignation date and recalculate leave if it differs from the request.',
     when=['resign'],
     basis='target')
item('lv-risk-t', 'leave', 'If HQMC sets a different date, the leave math changes', 'The Director, Manpower Management can approve a different date. Watch the approval.',
     owner='You',
     due={'item': 'ret-approval', 'days': 0},
     kind='marker',
     cite=[c('MARADMIN 175/24', '3', 'The Director, Manpower Management, may approve a resignation/retirement request for a date other than the date requested based on the needs of the service', 'https://www.marines.mil/News/Messages/Messages-Display/Article/3739611/')],
     verify='IPAC, MMSR-2 and disbursing: confirm the approved retirement or FMCR date and recalculate leave if it differs from the request.',
     when=['retire'],
     basis='target')
item('lv-final', 'leave', 'Final LES: leave balance as planned, no debt', 'Check the last LES and the DD-214 leave block.',
     owner='You',
     due={'eas': 0},
     cite=[],
     verify=None,
     basis='target')
item('lv-tsp', 'leave', 'TSP stays put', 'No action needed beyond confirming your login. Drill pay can keep contributing if you affiliate.',
     owner='You',
     due={'eas': 30},
     cite=[],
     verify=None,
     basis='target')

# ---------------- 6. FAMILY AND COVERAGE ----------------
item('fam-tamp', 'fam', 'TAMP: 180 days of premium free TRICARE', 'MARADMIN 454/26 describes 180 days of premium-free TAMP for qualifying Selected Reserve affiliation without a break in service. Confirm the award and actual start/end dates; the Reserve profile choice does not prove coverage.',
     owner='You and spouse',
     due={'eas': 1},
     window={'from': {'eas': 1}, 'to': {'eas': 180}},
     kind='window',
     cite=[c('MARADMIN 454/26', '3.a', 'Transitioning AC Marines who affiliate with the Selected Reserve without a break in service are eligible for 180 days of premium-free transitional health care under the Transitional Assistance Management Program (TAMP) in accordance with reference (b).', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify='IPAC, DEERS and TRICARE: confirm TAMP qualifying status, award and actual sponsor/dependent coverage dates.',
     when=['reserve'],
     basis='target')
item('fam-trs', 'fam', 'Enroll in TRICARE Reserve Select before TAMP ends', "Eligible Selected Reserve Marines may enroll in TRICARE Reserve Select after TAMP. Ask TRICARE and DEERS to confirm eligibility, each family member's enrollment and the effective date. Day 170 is a planning target, not a coverage promise.",
     owner='You and spouse',
     due={'eas': 170},
     cite=[c('MARADMIN 454/26', '3.a', 'Upon completion of TAMP, eligible Selected Reserve Marines may enroll in TRICARE Reserve Select.', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify="TRICARE, DEERS and IPAC: confirm TAMP end, TRS eligibility, each family member's enrollment and actual effective date.",
     when=['reserve'],
     basis='target')
item('fam-chcbp', 'fam', 'Confirm coverage after active duty and CHCBP eligibility', 'The copied pack establishes one qualifying Selected Reserve TAMP route. It does not establish all TAMP categories or CHCBP eligibility, sponsor/dependent durations or enrollment deadlines. Ask IPAC, DEERS and TRICARE to check every qualifying status before choosing coverage.',
     how=['CHCBP eligibility, sponsor/dependent durations and enrollment deadlines remain pending IPAC, DEERS, TRICARE and contractor confirmation.'],
     owner='You and spouse',
     due={'eas': -60},
     critical=True,
     cite=[c('MARADMIN 454/26', '3.a', 'Transitioning AC Marines who affiliate with the Selected Reserve without a break in service are eligible for 180 days of premium-free transitional health care under the Transitional Assistance Management Program (TAMP) in accordance with reference (b).', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify="IPAC, DEERS/TRICARE and CHCBP contractor: confirm all TAMP categories, each person's CHCBP eligibility, duration and actual enrollment deadline.",
     when=['noreserve', 'notretire'],
     basis='target')
item('fam-tricare-ret', 'fam', 'Prepare for retirement TRICARE enrollment', 'Prepare 30 days before the approved retirement or FMCR action. The copied pack does not establish enrollment and retroactive-enrollment windows, fees or unpaid-claim handling. Have TRICARE confirm the plan, effective date and actual deadlines before action.',
     how=['Regular and retroactive enrollment deadlines, fees and unpaid-claim handling remain pending TRICARE contractor and DEERS confirmation.'],
     owner='You and spouse',
     due={'eas': -30},
     kind='window',
     critical=True,
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1407.1-5', "It is the Marine's responsibility to ensure that family members' information is current and accurate in DEERS. ... See the TRICARE website (www.tricare.mil) for an explanation of retired/FMCR medical benefits.", 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify="TRICARE benefits office/contractor and DEERS: confirm each person's eligibility, regular and retroactive enrollment deadlines, coverage dates, fees and unpaid-claim handling.",
     when=['retire'],
     basis='target')
item('fam-fedvip', 'fam', 'Check FEDVIP dental eligibility and enroll if you choose it', "Ask whether you and your family qualify to purchase FEDVIP dental coverage. Confirm the enrollment window, premium and effective date before active-duty family dental coverage ends. The 30-day date is a preparation target; the copied pack does not establish this option's eligibility or deadlines.",
     how=['FEDVIP eligibility, enrollment window and the deciding enrollment office remain pending TRICARE dental benefits office confirmation.'],
     owner='You and spouse',
     due={'eas': -30},
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1407.1-5', "It is the Marine's responsibility to ensure that family members' information is current and accurate in DEERS. ... See the TRICARE website (www.tricare.mil) for an explanation of retired/FMCR medical benefits.", 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='TRICARE dental benefits office: confirm coverage transition and FEDVIP eligibility, enrollment window, premium and effective date with the enrollment office it identifies.',
     when=['retire'],
     basis='target')
item('ret-id', 'fam', 'Confirm retired ID cards and DEERS changes', "Confirm the ID card actions for the approved retirement or FMCR status and keep each family member's DEERS information current. The next-day date is a planning target.",
     owner='You and spouse',
     due={'eas': 1},
     cite=[c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1407.1-5', "It is the Marine's responsibility to ensure that family members' information is current and accurate in DEERS. ... See the TRICARE website (www.tricare.mil) for an explanation of retired/FMCR medical benefits.", 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='IPAC and DEERS: confirm the approved retirement or FMCR status and the required ID card updates for each eligible family member.',
     when=['retire'],
     basis='target')
item('fam-dental-tdp', 'fam', 'Confirm Reserve sponsor and family dental coverage', 'Confirm sponsor and dependent dental coverage separately. Ask about TAMP dental eligibility, when sponsor TDP may begin and whether family enrollment continues. The pre-EAS date is a preparation target. The copied pack does not establish dental enrollment or premium rules.',
     how=['TAMP dental eligibility, sponsor TDP start, family continuation and premiums remain pending TRICARE dental benefits office and DEERS confirmation.'],
     owner='You and spouse',
     due={'eas': -30, 'biz': 'prev'},
     cite=[c('MARADMIN 454/26', '3.a', 'Transitioning AC Marines who affiliate with the Selected Reserve without a break in service are eligible for 180 days of premium-free transitional health care under the Transitional Assistance Management Program (TAMP) in accordance with reference (b).', 'https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/')],
     verify='TRICARE dental benefits office and DEERS: confirm TAMP dental eligibility, sponsor TDP start, family continuation, enrollment and premiums separately.',
     when=['reserve', 'notretire'],
     basis='target')
item('fam-dental-civ', 'fam', 'Line up civilian dental before your date', 'Active duty dental coverage ends with your service.',
     owner='You and spouse',
     due={'eas': -60},
     cite=[],
     verify='Your dental clinic: when does coverage end for you and your family?',
     when=['noreserve', 'notretire'],
     basis='target')
item('fam-id', 'fam', 'DEERS and family ID cards', "The family's status changes at your date.",
     owner='You and spouse',
     due={'eas': 14},
     cite=[],
     verify='ID card office: what changes for your family at EAS?',
     when=['notretire'],
     basis='target')
item('fam-sgli', 'fam', 'Confirm SGLI continuation or VGLI conversion', 'For eligible SGLI-insured Marines, the VA guide gives 240 days after separation without proof of good health, while the manual gives 120 days. VA Insurance must settle the applicable deadline, Ready Reserve SGLI continuation, conversion eligibility and combined coverage maximum before you select amounts. Day 120 is a planning target.',
     how=['Individual eligibility, Ready Reserve continuation, combined coverage maximum and the 120/240-day policy difference remain pending VA Insurance/OSGLI confirmation.'],
     owner='You',
     due={'eas': 120},
     cite=[c('VA Benefits and Services Participant Guide v6.1', 'Converting SGLI to VGLI', 'You can convert your SGLI to VGLI within 240 days after separation without proof of good health', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf'),
           c('MCO 1900.16 CH-3 (MARCORSEPMAN)', '1101.3.a', "Marines on active duty entitled to full-time SGLI coverage per reference (bu) MCO 1741.8 can convert to Veteran's Group Life Insurance (VGLI) without proof of health by submitting the premium within 120 days following the date of separation from service.", 'https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf')],
     verify='VA Insurance/OSGLI and Reserve personnel office: confirm governing deadline, individual eligibility, SGLI continuation and the combined SGLI/VGLI maximum before choosing coverage.',
     basis='target')
item('fam-teb', 'fam', 'GI Bill transfer: confirm the obligation is served', 'A transfer carries a service obligation. Leaving before it is done cancels the transfer.',
     owner='You',
     due={'eas': -120},
     cite=[c('VA Benefits and Services Participant Guide v6.1', 'Module 4, p. 94', 'You must complete your entire service obligation or your transfer will be disqualified. If this occurs, and your beneficiary already used benefits, you will incur debt in the full amount of funds spent on their behalf.', 'https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf')],
     verify='Education office: confirm the transfer obligation end date.',
     basis='target')
item('fam-hhg-counsel', 'fam', 'Final household goods move: DMO/TMO counseling', 'Arrange your final household goods (HHG) move with the installation Distribution Management Office (DMO) or Transportation Management Office (TMO). The appointment target is 90 days before your board separation or retirement date.',
     how=['Contact DMO/TMO for counseling and bring your separation, retirement or FMCR orders, destination and requested move dates.', 'Record the actual appointment as a fixed date on fam-hhg-appt. The 90-day target is a pack planning choice.', 'Have DMO/TMO confirm shipment eligibility, weight allowance, authorized destination, excess costs, storage and the applicable expiration on fam-hhg-entitlement.'],
     due={'eas': -90}, basis='target',
     cite=[c(JTR, '052012.A.1', 'A Service member on active duty who is separated from the Service or relieved from active duty under par. 051002, is authorized HHG transportation, limited to the authorized PCS weight allowance, to the HOR or PLEAD, whichever the Service member selects.', UJTR), c(JTR, '052013.A.1.b', 'Retired with pay for any other reason, including transfer to the Fleet Reserve or Fleet Marine Corps Reserve. The retirement must occur immediately following 8 years or more of continuous active duty with no single break in service of 91 or more days.', UJTR)],
     verify='Installation DMO/TMO: confirm the counseling appointment and your orders-based final move entitlement.')
item('fam-hhg-appt', 'fam', 'Final HHG move: confirmed DMO/TMO appointment', 'Record the actual counseling appointment separately from the planning target and shipment expiration.',
     how=['Give Claude the appointment date DMO/TMO confirms and ask Claude to record a fixed date here. Keep it undated until confirmation.'],
     due=None, kind='milestone', presence=True,
     cite=[c(JTR, '052012.C.1', 'The Transportation Officer or designated representative determines the reasonableness on a case-by-case basis.', UJTR)],
     verify='Installation DMO/TMO: confirm the actual appointment.', basis='rule')
item('fam-hhg-entitlement', 'fam', 'Final HHG shipment entitlement and expiration: confirm with DMO/TMO', 'Your shipment entitlement and time limit require DMO/TMO confirmation against your orders and active-duty termination date. For ordinary separation under JTR 052012, the authorized destination is home of record (HOR) or place last entered active duty (PLEAD), within 180-day authority and a timely written-request provision. For qualifying retirement or FMCR under JTR 052013, home of selection (HOS) authority requires turnover within 3 years for termination dates on or after 24 JUN 2022, subject to exceptions. DMO/TMO must confirm the separate storage expiration.',
     how=['Ask DMO/TMO which JTR paragraph applies to your orders, including any special separation-pay category. Confirm the authorized destination, PCS weight limit, excess costs and storage expiration.', 'Under 052012.C, authority ends on the 181st day following separation or relief unless the written HHG request reaches the transportation officer before the end of the 180th day. Timely applications require turnover as soon as practicable; DMO/TMO determines reasonableness.', 'JTR paragraph 052013 (B) sets a 3-year turnover limit with exceptions and extensions. Table 5-52 ends non-temporary storage 1 year from active-duty termination unless its exceptions apply. DMO/TMO must confirm any storage costs after expiration.', 'Have DMO/TMO give you the exact shipment or application deadline and storage limit in writing. Give Claude those dates and ask Claude to set the fixed shipment rule date here and record the storage date in notes. Keep this date unknown until office confirmation. After shipment, record the actual date and retain the receipts DMO/TMO requires.'],
     due=None, critical=True,
     cite=[c(JTR, '052012.A.1', 'A Service member on active duty who is separated from the Service or relieved from active duty under par. 051002, is authorized HHG transportation, limited to the authorized PCS weight allowance, to the HOR or PLEAD, whichever the Service member selects.', UJTR), c(JTR, '052012.C', 'Authority for HHG transportation is limited to 180 days. Such authority ends on the 181st day following separation from the Service or relief from active duty, unless a written request for HHG transportation is submitted to a Transportation Officer or designated representative before the end of the 180th day.', UJTR), c(JTR, '052013.A.1', 'A Service member on active duty is authorized HHG transportation ... to the Service member’s HOS when the Service member is: ... Retired with pay for any other reason, including transfer to the Fleet Reserve or Fleet Marine Corps Reserve. The retirement must occur immediately following 8 years or more of continuous active duty with no single break in service of 91 or more days.', UJTR), c(JTR, '052013.B', 'HHG must be turned over for transportation within 3 years following active duty termination, except as in Table 5-33. A Service member is eligible for the 3 year time limitation if the active duty termination effective date is on or after June 24, 2022.', UJTR), c(JTR, '052013, Table 5-52, item 1', 'The authority begins on the date the order is issued and ends 1 year from the active-duty termination date, unless otherwise indicated in this paragraph.', UJTR)],
     verify='Installation DMO/TMO: confirm the applicable JTR category, shipment entitlement, destination, weight, exact time limit, storage expiration and any extension approval.', basis='rule')
item('fam-va-dental-iv', 'fam', 'Confirm VA dental: Class IV', 'A qualifying 100 percent service-connected rating or individual unemployability paid at the 100 percent rate may qualify you for any needed dental care. Permanence is not required. A temporary 100 percent rating does not qualify for Class IV.',
     how=['Ask the eligibility office to review your VA decision and confirm the applicable benefit before relying on it.'],
     due=None, cite=[c(VDENT, 'Class IV: rating and unemployability statements', 'I have 1 or more service-connected disabilities rated 100% disabling ... Class IV ... Any needed dental care ... If you’re being paid at the 100% disabling rate based on a temporary rating (for a reason such as a long stay in the hospital or rehab care), that doesn’t qualify you for this benefit. ... I’m unemployable (unable to work), and I get disability compensation at the 100% disabling rate due to service-connected conditions ... Class IV ... Any needed dental care', UDENT)], verify='VA dental clinic eligibility office: confirm Class IV eligibility and the temporary-rating exclusion.', basis='target')
item('fam-champva', 'fam', 'Confirm CHAMPVA for qualifying family members', 'A spouse or dependent child of a veteran rated permanent and total for a service-connected disability may qualify. Anyone eligible for TRICARE cannot get CHAMPVA; retiree families eligible for TRICARE are excluded. Ask the VA CHAMPVA eligibility office about survivor categories when the veteran has died.',
     how=['Ask the eligibility office to review your VA decision and confirm the applicable benefit before relying on it.'],
     due=None, cite=[c(VCHAMPVA, 'Eligibility for CHAMPVA', 'You’re the spouse or dependent child of a Veteran who’s been rated permanently and totally disabled from a service-connected disability, ... If you’re eligible for or enrolled in TRICARE, you can’t get CHAMPVA benefits.', UCHAMPVA)], verify='VA CHAMPVA eligibility office and DEERS/TRICARE benefits office: confirm family eligibility and the TRICARE exclusion.', basis='target')
item('fam-will', 'fam', 'Will and POA at base legal', 'Free while on active duty.',
     owner='You and spouse',
     due={'eas': -120},
     cite=[],
     verify=None,
     basis='target')
item('fam-budget', 'fam', 'Family budget on the new income', 'No active duty pay after the date. Count retired pay, drill pay, VA compensation and civilian pay only as each one is approved.',
     owner='You and spouse',
     due={'eas': -90},
     cite=[],
     verify=None,
     basis='target')

# ---------------- 7. TURNOVER ----------------
item('cmd-plan', 'cmd', 'Turnover plan with the CO: who takes your billet and when', 'Settle it early; it shapes your leave and any SkillBridge cover plan.',
     owner='CO',
     due={'eas': -120},
     presence=True,
     cite=[],
     verify='CO: who takes your billet and when?',
     basis='target')
item('cmd-award', 'cmd', 'Final fitness report or evaluation and end of tour award submitted', 'Command practice. Ask early; awards take weeks.',
     owner='CO',
     due={'eas': -90},
     cite=[],
     verify='CO and S-1: award and final report submitted?',
     basis='target')
item('cmd-binder', 'cmd', 'Turnover binder: battle rhythm, open actions, contacts, accounts', 'What your relief needs on day one.',
     owner='You',
     due={'eas': -45},
     cite=[],
     verify=None,
     basis='target')
item('cmd-turnover', 'cmd', 'Turnover with your relief', 'Three to five days, face to face.',
     owner='You',
     due={'eas': -45},
     window={'from': {'eas': -45}, 'to': {'eas': -40}},
     kind='window',
     presence=True,
     cite=[],
     verify='Your relief: dates that work.',
     basis='target')
item('cmd-checkout', 'cmd', 'Unit checkout sheet: gear, library, armory, IT accounts, travel card', 'The formal checkout.',
     owner='You',
     due={'eas': -7},
     cite=[],
     verify='IPAC: the unit checkout sheet.',
     basis='target')

# TRP counts from confirmed EAS, which is separate from retirement action dates.
for rec in items:
    if rec['id'] in ('sep-ic', 'sep-presep', 'sep-trs', 'sep-capstone', 'sep-cv'):
        rec['cite'].append(c('NAVMC 1700.2B', 'Encl (2) para 7', 'Commanders are responsible for ensuring all Marines participating in S-PTAD have completed all pre-separation and transition requirements in accordance with reference (a).', UNAVMC))
    if rec['id'] == 'va-service-end':
        rec['how'].append('IPAC, the installation TRP office and UTC must also confirm this is the EAS used to count the MCO 1700.31A transition deadlines. Record the confirmed date here before relying on those dates.')
        rec['cite'].append(c(TRPA, 'Encl (2), Ch 5 para 3.a', 'Individualized Initial Counseling (IC). Must be completed not later than 365 days prior to EAS date.', UTRPA))
        rec['verify'] += ' Installation TRP office and UTC: confirm EAS for TRP deadlines.'

# Current TRP order enforces SkillBridge procedures through reference (p).
for rec in items:
    if rec['id'] in ('sb-coord', 'sb-packet', 'sb-approval', 'sb-sequence', 'sb-run', 'sb-start'):
        rec['how'].append("Complete IC, pre-separation counseling, TRS workshops, Capstone and Commander's Verification before SkillBridge participation. Meet the MCO 1700.31A EAS deadlines as well. Confirm completion with the TRP office, UTC, SkillBridge coordinator and CO.")
        rec['cite'].extend([c(TRPA, 'Encl (2), Ch 3 para 16', 'Enforce Marine Corps SkillBridge Program requirements and procedures as outlined in reference (p).', UTRPA), c('NAVMC 1700.2B', 'Encl (2) para 7', 'Commanders are responsible for ensuring all Marines participating in S-PTAD have completed all pre-separation and transition requirements in accordance with reference (a).', UNAVMC)])
        rec['verify'] += ' Installation TRP office and UTC: verify completion before SkillBridge participation.'

contacts = [
    {"id": "c-co", "name": "", "role": "Commanding Officer (reporting senior)", "org": "Your unit", "phone": "", "email": "", "loe": "sep", "note": "Counseling, endorsements, billet cover.", "when": []},
    {"id": "c-ipac", "name": "", "role": "IPAC", "org": "", "phone": "", "email": "", "loe": "sep", "note": "Unit diary, orders, leave, DD-214.", "when": []},
    {"id": "c-tap", "name": "", "role": "TAP counselor", "org": "", "phone": "", "email": "", "loe": "sep", "note": "DD 2648, Capstone.", "when": []},
    {"id": "c-cc", "name": "", "role": "Career Counselor", "org": "", "phone": "", "email": "", "loe": "dap", "note": "DAP request and billet search.", "when": ["reserve"]},
    {"id": "c-sbc", "name": "", "role": "Installation SkillBridge coordinator", "org": "MCCS", "phone": "", "email": "", "loe": "sb", "note": "NCMIS application.", "when": ["sb"]},
    {"id": "c-vso", "name": "", "role": "Accredited VSO (to be chosen)", "org": "VFW, DAV, American Legion, or your state", "phone": "", "email": "", "loe": "va", "note": "Appoint on VA Form 21-22.", "when": []},
    {"id": "c-mmsr2", "name": "MMSR-2 office", "role": "Separations and retirements", "org": "HQMC", "phone": "703-784-9324", "email": "smb.manpower.mmsr2o@usmc.mil", "loe": "sep", "note": "Requests outside the window or needing a waiver, by encrypted email.", "when": ["notretire"]},
    {"id": "c-mmsr2-r", "name": "MMSR-2 office", "role": "Separations and retirements", "org": "HQMC", "phone": "703-784-9324", "email": "smb.manpower.mmsr2o@usmc.mil", "loe": "sep", "note": "Requests outside the window or needing a waiver, by encrypted email.", "when": ["retire"]},
    {"id": "c-ram1", "name": "RAM-1", "role": "Reserve commissions", "org": "HQMC Reserve Affairs", "phone": "703-432-9590", "email": "RAM-1@usmc.mil", "loe": "dap", "note": "POC on MARADMIN 045/25.", "when": ["reserve", "resign"]},
    {"id": "c-rac3", "name": "RAC-3 Retention", "role": "DAP program office", "org": "HQMC Reserve Affairs", "phone": "", "email": "SMB_RA_RETENTION@usmc.mil", "loe": "dap", "note": "MARADMIN 454/26.", "when": ["reserve"]},
    {"id": "c-hqmcsb", "name": "HQMC SkillBridge", "role": "SkillBridge program office", "org": "HQMC MFR", "phone": "", "email": "HQMC_SKILLBRIDGE@USMC.ONMICROSOFT.COM", "loe": "sb", "note": "POC on MARADMIN 280/24.", "when": ["sb"]},
    {"id": "c-va", "name": "VA benefits line", "role": "VA", "org": "VA", "phone": "800-827-1000", "email": "", "loe": "va", "note": "General VA benefits help.", "when": []},
    {"id": "c-dfas", "name": "DFAS retired pay", "role": "Retired pay and SBP", "org": "DFAS", "phone": "800-321-1080", "email": "", "loe": "sep", "note": "DD 2656, direct deposit, first payment.", "when": ["retire"]},
    {"id": "c-chcbp", "name": "Humana Military", "role": "CHCBP enrollment", "org": "TRICARE", "phone": "800-444-5445", "email": "", "loe": "fam", "note": "Continued Health Care Benefit Program.", "when": ["noreserve", "notretire"]},
    {"id": "c-state-vso", "name": "", "role": "State department of veterans services", "org": "Your state", "phone": "", "email": "", "loe": "va", "note": "Accredited state representatives.", "when": []},
]
# c-mmsr2 is split into two records so the resign and retire paths each get it and the eas path does not
contacts = [x for x in contacts if x["id"] != "c-mmsr2"] + [dict(x, id="c-mmsr2", when=["resign"]) for x in contacts if x["id"] == "c-mmsr2"]

blocks = []
conditions = []
claim = {
    "where": {"rows": [
        {"appt": "Separation physical and hearing test", "where": "Branch Health Clinic on base", "home": "", "base": "", "how": "You call. The clinic confirms where the hearing test is done. Required SHPE travel goes on command-funded TAD."},
        {"appt": "BDD exams", "where": "Contractor site VA assigns near your home address", "home": "", "base": "", "how": "The contractor calls you. VA aims for 50 miles for general exams and 100 for specialty. Clear the days with the command; no VA travel pay while on active duty."},
        {"appt": "Primary care after your date", "where": "Nearest VA community clinic", "home": "", "base": "", "how": "VA enrollment and scheduling."},
        {"appt": "Specialty care", "where": "VA Medical Center", "home": "", "base": "", "how": "By VA referral."},
        {"appt": "Benefits office and VSOs", "where": "VA Regional Benefit Office", "home": "", "base": "", "how": "Walk in or book through VERA. Set up VSO intake separately."},
        {"appt": "Readjustment counseling", "where": "Vet Center or telehealth", "home": "", "base": "", "how": "You request it. Open to active duty members who served in a combat theater. Records reach VA only with your permission."},
        {"appt": "Mental health care now", "where": "Base PCM, then a military or TRICARE provider", "home": "", "base": "", "how": "PCM referral for civilian care. MFLC keeps no records, so use clinical care for anything the claim needs."}],
        "note": "Enter your own drive times. They are one way estimates."},
    "vso": {"rows": [
        {"rank": 1, "name": "VFW Pre-Discharge", "why": "Publishes remote BDD routing for bases without a VFW representative.", "phone": "202-543-2239", "email": "bdd@vfw.org"},
        {"rank": 2, "name": "DAV regional office", "why": "Accredited office at the VA regional office, plus DAV's national transition program.", "phone": "", "email": ""},
        {"rank": 3, "name": "State department of veterans services", "why": "Accredited state team. Intake waits of 30 to 90 days are common, so call early.", "phone": "", "email": ""}],
        "script": "I serve on active duty, separate on (your date), and plan to file a BDD claim around (date). I want an accredited representative on a 21-22 before I file. Can you take me on, and what do you need from me first?",
        "note": "The ranking is a judgment call, and intake capacity is unknown until you call. Check any representative on VA's accreditation search before you sign VA Form 21-22."},
    "exposure": {"rows": [], "notes": [
        "Open ILER with your CAC, save the Individual Exposure Summary, and add missing events. Self reports do not overwrite official records.",
        "Put every exposure in SHA Part A Section 7 and in front of military medical before you file.",
        "At VA enrollment, ask for the Toxic Exposure Screening. It records concerns; it does not prove exposure.",
        "Confirm you are in the Burn Pit Registry. It does not replace the claim.",
        "Exposure alone is not a disability. It matters when a condition shows up, now or years from now."]},
    "benefits": {"title": "What a rating can mean", "label": "Thresholds are statutory; amounts come from VA's current table", "rows": [
        {"what": "Monthly pay, tax free", "detail": "Set by VA's rate table for your rating and dependents. Rises with the cost of living each year."},
        {"what": "Retired pay and VA pay", "detail": "At 50 percent or higher, CRDP pays retired pay in full on top of VA pay (10 USC 1414)."},
        {"what": "Health care", "detail": "50 percent or higher is VA Priority Group 1: free care with no copays, service connected or not."},
        {"what": "VA home loan", "detail": "Funding fee waived on a purchase or refinance."},
        {"what": "Education and training (VR&E)", "detail": "At 20 percent or higher with an employment handicap finding, VA pays for a degree or training plus a monthly allowance. The old 12 year limit does not apply to discharges on or after 1 January 2013. Check eligibility on va.gov."},
        {"what": "Federal jobs", "detail": "30 percent or higher: 10 point preference in the top category and a noncompetitive hiring authority."},
        {"what": "Smaller benefits", "detail": "VALife whole life insurance up to $40,000 with no medical underwriting. Commissary and exchange access."},
        {"what": "Protections", "detail": "Ratings can go up as conditions age, and you file for increases. A rating held 20 years cannot drop below that level. Cuts require proven improvement."},
        {"id": 'benefit-va-dental-iv', "what": 'VA dental: Class IV', "detail": 'A qualifying 100 percent service-connected rating or individual unemployability paid at the 100 percent rate may qualify you for any needed dental care. Permanence is not required. A temporary 100 percent rating does not qualify for Class IV.', "cite": [c(VDENT, 'Class IV: rating and unemployability statements', 'I have 1 or more service-connected disabilities rated 100% disabling ... Class IV ... Any needed dental care ... If you’re being paid at the 100% disabling rate based on a temporary rating (for a reason such as a long stay in the hospital or rehab care), that doesn’t qualify you for this benefit. ... I’m unemployable (unable to work), and I get disability compensation at the 100% disabling rate due to service-connected conditions ... Class IV ... Any needed dental care', UDENT)], "verify": 'VA dental clinic eligibility office: confirm Class IV eligibility and the temporary-rating exclusion.'},
        {"id": 'benefit-champva', "what": 'CHAMPVA for qualifying family members', "detail": 'A spouse or dependent child of a veteran rated permanent and total for a service-connected disability may qualify. Anyone eligible for TRICARE cannot get CHAMPVA; retiree families eligible for TRICARE are excluded. Ask the VA CHAMPVA eligibility office about survivor categories when the veteran has died.', "cite": [c(VCHAMPVA, 'Eligibility for CHAMPVA', 'You’re the spouse or dependent child of a Veteran who’s been rated permanently and totally disabled from a service-connected disability, ... If you’re eligible for or enrolled in TRICARE, you can’t get CHAMPVA benefits.', UCHAMPVA)], "verify": 'VA CHAMPVA eligibility office and DEERS/TRICARE benefits office: confirm family eligibility and the TRICARE exclusion.'},
        {"what": "Reserve drill pay", "detail": "Each year you waive VA pay for drill days or the reverse, whichever pays more."}],
        "note": "VA decides the rating from the evidence and the exams. Nothing on this board predicts it."},
}

PACK = json.loads((HERE.parent / "config.json").read_text()).get("pack")

def merge_copy(records, copy):
    """Require exact item coverage before adding the seed-owned display copy."""
    errors = []
    item_ids = {record["id"] for record in records}
    for key in sorted(set(copy) - item_ids):
        errors.append(f"COPY key names no seeded item: {key}")
    for record in records:
        entry = copy.get(record["id"])
        for field in ("label", "brief"):
            value = entry.get(field) if isinstance(entry, dict) else None
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{record['id']}: missing COPY {field}")
    if errors:
        raise SystemExit("SEED COPY CHECK FAILED\n" + "\n".join(" - " + error for error in errors))
    for record in records:
        record.update({field: copy[record["id"]][field] for field in ("label", "brief")})

merge_copy(items, COPY)
seed = {"pack": PACK, "settings": settings, "ledger": ledger, "loes": loes, "items": items, "contacts": contacts, "blocks": blocks, "conditions": conditions, "claim": claim}

# ---------------- checks ----------------
errs = []
ids = [i["id"] for i in items]
if len(ids) != len(set(ids)): errs.append("duplicate item ids")
if len({x["id"] for x in contacts}) != len(contacts): errs.append("duplicate contact ids")
loe_ids = {l["id"] for l in loes}
FLAGS = {"resign", "retire", "eas", "officer", "enlisted", "reserve", "noreserve", "sb", "nosb", "cat1", "cat2", "cat3", "notretire"}
def check_rule(r, where):
    if r is None: return
    keys = set(r) - {"biz"}
    if keys not in ({"date"}, {"eas"}, {"easMonths"}, {"sb"}, {"item", "days"}): errs.append(f"{where}: bad rule {r}")
    if "item" in r and r["item"] not in ids: errs.append(f"{where}: unknown item {r['item']}")
    if "date" in r and r["date"] != "SETUP" and not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", r["date"]): errs.append(f"{where}: bad date {r['date']}")
for i in items:
    if i["loe"] not in loe_ids: errs.append(f"{i['id']}: unknown loe")
    check_rule(i["due"], i["id"])
    if i["window"]: check_rule(i["window"]["from"], i["id"] + ".from"); check_rule(i["window"]["to"], i["id"] + ".to")
    if i["status"] not in ("open", "doing", "waiting", "done", "na"): errs.append(f"{i['id']}: bad status")
    if set(i["when"]) - FLAGS: errs.append(f"{i['id']}: unknown flag {i['when']}")
    for ct in i["cite"]:
        if not ct["ref"] or not ct["quote"]: errs.append(f"{i['id']}: empty cite")
        if ct["url"] is not None and not ct["url"].startswith("https://"): errs.append(f"{i['id']}: bad url")
    if not i["cite"] and not i["verify"] and i["kind"] not in ("milestone",) and i["id"] not in ("va-conditions", "va-sickcall", "va-hearing", "va-bh", "va-reserve", "sb-approval", "lv-ledger", "lv-requests", "lv-final", "lv-tsp", "fam-will", "fam-budget", "cmd-binder", "va-decision"):
        errs.append(f"{i['id']}: no cite and no verify")
for x in contacts + loes:
    if set(x["when"]) - FLAGS: errs.append(f"{x['id']}: unknown flag {x['when']}")

def fits(rec, flags): return all(f in flags for f in rec["when"])
def combos():
    for path in ("resign", "retire", "eas"):
        for grade in ("officer", "enlisted"):
            if path == "resign" and grade == "enlisted": continue
            for res in ("reserve", "noreserve"):
                if path == "retire" and res == "reserve": continue
                for sb in ("sb", "nosb"):
                    for cat in (("cat2", "cat3") if grade == "officer" else ("cat1", "cat2", "cat3")):
                        flags = {path, grade, res, sb, cat}
                        if path != "retire": flags.add("notretire")
                        yield flags
counts = {}
for flags in combos():
    inc = [i for i in items if fits(i, flags)]; inc_ids = {i["id"] for i in inc}
    inc_loes = {l["id"] for l in loes if fits(l, flags)}
    key = " ".join(sorted(flags))
    counts[key] = len(inc)
    for i in inc:
        if i["loe"] not in inc_loes: errs.append(f"{key}: {i['id']} included but its line of effort is not")
        for r in [i["due"]] + ([i["window"]["from"], i["window"]["to"]] if i["window"] else []):
            if r and "item" in r and r["item"] not in inc_ids: errs.append(f"{key}: {i['id']} points at {r['item']} which is excluded")
            if r and "sb" in r and "sb" not in flags: errs.append(f"{key}: {i['id']} uses a SkillBridge rule without SkillBridge")

def _leak_words():
    p = Path.home() / ".musterout" / "leak_words.txt"
    if not p.exists():
        print("leak guard skipped: no private word list at ~/.musterout/leak_words.txt")
        return []
    return [w for w in p.read_text(encoding="utf-8").splitlines() if w]

blob = json.dumps(seed, ensure_ascii=False)
if any(d in blob for d in DASHES): errs.append("em or en dash in seed text")
# The verbatim 7005.4.b quote uses generic pronouns, not a personal fact.
# Exempt only that exact quote; its official source is verified below.
privacy_blob = blob.replace('Counsel the Marine concerning his or her potential for recall to active duty and/or mobilization.', '')
PERSONAL = _leak_words()
for p in PERSONAL:
    if p in privacy_blob: errs.append(f"personal string in seed: {p!r}")

# ---------------- quote verification against the local regulation texts ----------------
LOCAL = {TRPA: "mco-1700.31a.txt", VDENT: "va-dental-care.txt", VCHAMPVA: "va-champva.txt", VITF: "va-intent-to-file.txt", JTR: "jtr-final-move.txt", MCO: "mco-1900.16-ch3.txt", LVO: "mco-1050.3j.txt", "MARADMIN 175/24": "maradmin-175-24.txt",
         "MARADMIN 326/23": "maradmin-326-23.txt", MMSR: "mmsr-2-enlisted-retirements.txt",
         "MARADMIN 454/26": "maradmin-454-26.txt", "MARADMIN 045/25": "maradmin-045-25.txt",
         "MARADMIN 280/24": "maradmin-280-24.txt", "NAVMC 1700.2B": "navmc-1700.2b.txt"}
def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()
if "--no-verify" not in sys.argv and REGS.exists():
    texts = {k: norm(open(REGS / v, encoding="utf-8", errors="ignore").read()) for k, v in LOCAL.items() if (REGS / v).exists()}
    seen = set()
    for i in items + claim["benefits"]["rows"]:
        for ct in i.get("cite", []):
            if ct["ref"] in texts and (ct["ref"], ct["quote"]) not in seen:
                seen.add((ct["ref"], ct["quote"]))
                for part in ct["quote"].split("..."):
                    if norm(part) and norm(part) not in texts[ct["ref"]]: errs.append(f"{i['id']}: quote not found in {ct['ref']}: {part[:70]!r}")
    print(f"quotes verified against {len(texts)} local texts: {len(seen)} distinct quotes checked")
else:
    print("quote verification skipped")

if errs:
    print("SEED CHECK FAILED"); [print(" -", e) for e in errs]; sys.exit(1)
(HERE / "seed.json").write_text(json.dumps(seed, ensure_ascii=False, indent=1))
print(f"seed.json: {len(loes)} lines of effort, {len(items)} items, {len(contacts)} contacts, {len(blob)//1024} KB. Checks passed.")
print("items per path combination:")
for k, v in sorted(counts.items()): print(f"  {v:3}  {k}")
