<!-- Reader: VA tool maintainers. Effect: refresh official criteria without changing the calculator. -->
# VA self-help source notes

Checked 20 OCT 2026. The VA tools remain free. Records go into the person's Claude Project. Service facts, tier choices and estimates stay in page memory and clear on reload. The person reviews, signs and files their own claim.

## Condition selection

[VA FY2025 Annual Benefits Report](https://www.benefits.va.gov/REPORTS/abr/docs/2025-compensation.pdf), updated May 2026. Use all compensation recipients as of 30 SEP 2025, rather than newly awarded recipients. The ten on printed page 99 are supplemented by the ten highest-count additional individually named conditions on pages 103-106. Each lookup entry carries its count and page. These are disability counts, not a count of distinct people. The report does not publish a national top-20 ranking. TRS approved this selection on 20 OCT 2026.

## Criteria

[38 CFR Part 4 on eCFR](https://www.ecfr.gov/current/title-38/chapter-I/part-4), current through 19 OCT 2026. Current source bytes also come from [GPO's eCFR XML](https://www.govinfo.gov/bulkdata/ECFR/title-38/ECFR-title38.xml). The title's amendment date is 27 AUG 2026. `va-selfhelp.json` preserves official criterion wording and numeric columns; whitespace and layout are normalized. The numbered rows let a person select a specific tier without automated matching.

The report's historical labels do not select a diagnostic code in an individual case. DC 7805 refers disabling effects to an appropriate code. Its lookup includes the referenced scar codes without inventing a DC 7805 tier. DC 7522 now has a 0 percent schedular evaluation, with the special monthly compensation note retained. Arm ratings preserve major and minor columns. Spine and skin entries retain their general formulas and notes.

Hearing Tables VI, VIa and VII are graphics in current eCFR. Their references are `er11my99.005.gif` and `er11my99.006.gif`. Text cells were transcribed and visually checked against [GPO's official 4.85 PDF](https://www.govinfo.gov/content/pkg/CFR-2025-title38-vol1/pdf/CFR-2025-title38-vol1-sec4-85.pdf), printed pages 459-460. The current XML references the same graphics. The layout labels both axes and retains blank triangular cells by omitting undefined combinations. Tables VI/VIa require the conditions stated in 4.85 and 4.86. The lookup does not invent test results or calculate a medical designation.

The peripheral-nerve preface in 4.124a is quoted in full before DC 8520. Wholly sensory choices use mild or at most moderate; unclear findings are left for clinical clarification. DC 7804 Note (2) adds 10 percentage points once to the single scar-count evaluation before combining it with other evaluations. Spine rows identify cervical or thoracolumbar segments across DCs 5237 and 5242. Unfavorable ankylosis of both uses one entire-spine entry. DC 7801 and 7802 identify all six body zones, with marked zones for the combined-area alternative. Duplicate segments, zones under the same code and entire-region alternatives cannot enter twice. Every row requires the person to review the notes and confirm a distinct permitted evaluation. Clinical tier selection and external-code findings remain with the person, clinician and VA.

Source hashes and frozen criterion checks are in `board/_dev/va_selfhelp_sources.json`. W43 primary-source snapshots and the extraction record are in the VAS evidence folder. Review altered source wording before updating the hashes.

## Presumptions and associations

- [VA PACT Act locations and conditions](https://www.va.gov/resources/the-pact-act-and-your-va-benefits/) and [current burn-pit cancer examples](https://www.va.gov/resources/presumptive-cancers-related-to-burn-pit-exposure/).
- [VA Gulf War chronic illness and infection rules](https://www.va.gov/disability/eligibility/hazardous-materials-exposure/gulf-war-illness-southwest-asia/). Chronic illness locations differ from infection locations. VA's PACT Act guidance is broader than the older 3.317 text. The board does not apply the old regulatory cutoff as a universal filing deadline.
- [Agent Orange](https://www.va.gov/disability/eligibility/hazardous-materials-exposure/agent-orange/) and [Camp Lejeune](https://www.va.gov/disability/eligibility/hazardous-materials-exposure/camp-lejeune-water-contamination/).
- [3.307](https://www.ecfr.gov/current/title-38/section-3.307), [3.309](https://www.ecfr.gov/current/title-38/section-3.309), [3.317](https://www.ecfr.gov/current/title-38/section-3.317) and [3.320](https://www.ecfr.gov/current/title-38/section-3.320). Matching an entered location and date generates questions for a VSO. It does not establish diagnosis, service connection or eligibility. The checklist is bounded; other presumptions remain linked and available for review.
- Secondary associations use [3.310](https://www.ecfr.gov/current/title-38/section-3.310), the spine formula's neurologic note in [4.71a](https://www.ecfr.gov/current/title-38/section-4.71a), and [VA diabetes research](https://www.research.va.gov/topics/diabetes.cfm). The person must explicitly report an existing service-connected condition. A possible association does not establish causation or aggravation in that person's case.

## Pay and math

[VA's 2026 compensation table](https://www.va.gov/disability/compensation-rates/veteran-rates/) is effective 1 DEC 2025. All nine published tables, dependent categories and added amounts are retained. The estimate shows the effective date and the table for the combined rating. It does not forecast a deposit, offsets, effective dates or special monthly compensation.

Refresh the data when VA publishes the next compensation rate table or a correction. Recheck eCFR, VA presumptive guidance, the latest ABR, forms and medical-record links at each release. Keep `comb` and `vaMath` unchanged. The self-help flow bounds estimates to 12 separate evaluations to stay within the existing bilateral subset search. It refuses another row instead of silently using the larger-set fallback.

Single bilateral foot evaluations use an eligibility adapter backed by VA's [M21-1 V.iv.1.C.4.b](https://www.knowva.ebenefits.va.gov/system/templates/selfservice/va_ssnew/help/customer/locale/en-US/portal/554400000001018/content/554400000180525/M21-1-Part-V-Subpart-iv-Chapter-1-Section-C-Coded-Conclusion). One foot evaluation enters the factor with an independent compensable evaluation in an involved leg, or independent compensable evaluations in both arms. The adapter counts that percentage once and considers favorable subsets. It calls the unchanged `comb` and `vaMath` functions. It never duplicates a foot evaluation into two ratings or infers a disability.

[VA M21-1 V.iii.10.1.h](https://www.knowva.ebenefits.va.gov/system/templates/selfservice/va_ssnew/help/customer/locale/en-US/portal/554400000001018/content/554400000180515/M21-1-Part-V-Subpart-iii-Chapter-10-Skin-Conditions) permits the factor for separate extremity evaluations under DC 7801 or 7802. The location choices follow the selected scar code; DC 7800 and 7804 do not use that factor. Official VA pages were read and saved on 20 OCT 2026. These manual instructions supplement the CFR's eligibility rules and do not replace its arithmetic.

The test oracle compares all 684 published [4.25 Table I](https://www.ecfr.gov/current/title-38/section-4.25) cells and 43 synthetic whole estimates plus 31 single-bilateral policy cases, including bilateral pooling and the favorable-subset rule in [4.26(d)](https://www.ecfr.gov/current/title-38/section-4.26). For bilateral intermediate values outside the published table's ten-point columns, the independent oracle uses the integer remaining-efficiency rule from 4.25. No medical or personal data appears in these fixtures.

## Evidence and forms

[VA evidence instructions](https://www.va.gov/disability/how-to-file-claim/evidence-needed/), [military records](https://www.va.gov/records/get-military-service-records/) and [VA medical records](https://www.va.gov/health-care/get-medical-records/) support the evidence checklist. The three parts organize records without a sufficiency verdict; a presumption can establish the service link under its own rules.

[VA Form 21-4138](https://www.va.gov/forms/21-4138/) is revised July 2024. [VA Form 21-10210](https://www.va.gov/forms/21-10210/) is revised June 2021. The statement workflow checks current forms, uses only stated facts, leaves identifiers and signatures for private completion and requires the person to edit and sign.
