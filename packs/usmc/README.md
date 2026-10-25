# USMC separation pack

Version: `usmc-2026.10`

This Muster Out pack collects 10 public Marine Corps regulation texts and 8 supplemental public source texts, a seed citation index, a separation glossary, and FAQs for resignation, retirement, and ordinary EAS. It contains no individual plan or unit contact roster. The copied texts are a fixed source snapshot, not a certification of current policy or personal eligibility.

## Documents

- [MCO 1700.31A, signed 2 MAR 2026](regs/mco-1700.31a.txt) - [MCPEL current-order entry](https://www.marines.mil/News/Publications/MCPEL/Electronic-Library-Display/Article/900630/mco-170031a/), [official MCCS Okinawa PDF](https://www.okinawa.usmc-mccs.org/modules/media/?do=inline&id=66b20c97-887b-462b-a8a7-97dcd431a6e3&v=1)
- [VA dental care eligibility](regs/va-dental-care.txt) - [official source](https://www.va.gov/health-care/about-va-health-benefits/dental-care/)
- [VA CHAMPVA benefits](regs/va-champva.txt) - [official source](https://www.va.gov/family-and-caregiver-benefits/health-and-disability/champva/)
- [VA intent to file guidance](regs/va-intent-to-file.txt) - [official source](https://www.va.gov/resources/your-intent-to-file-a-va-claim/)
- [JTR final-move paragraphs 052012 and 052013, 1 OCT 2026](regs/jtr-final-move.txt). [Current JTR page](https://www.travel.dod.mil/Policy-Regulations/Joint-Travel-Regulations/). [Official PDF](https://media.defense.gov/2022/Jan/04/2002917147/-1/-1/0/JTR.PDF).
- [MCO 1900.16 CH-3 (MARCORSEPMAN)](regs/mco-1900.16-ch3.txt) - [official source](https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf)
- [MCO 1050.3J](regs/mco-1050.3j.txt) - [official source](https://www.marines.mil/portals/1/publications/mco%201050.3j.pdf)
- [NAVMC 1700.2B](regs/navmc-1700.2b.txt) - [official source](https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf)
- [MARADMIN 175/24](regs/maradmin-175-24.txt) - [official source](https://www.marines.mil/News/Messages/Messages-Display/Article/3739611/)
- [MARADMIN 045/25](regs/maradmin-045-25.txt) - [official source](https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/)
- [MARADMIN 454/26](regs/maradmin-454-26.txt) - [official source](https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/)
- [MARADMIN 280/24](regs/maradmin-280-24.txt) - [official source](https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/)
- [MARADMIN 625/24](regs/maradmin-625-24.txt) - [official source](https://www.marines.mil/News/Messages/Messages-Display/Article/4015114/advance-notification-of-forthcoming-changes-to-mco-10503j-regulations-for-leave/)
- [MARADMIN 326/23](regs/maradmin-326-23.txt) - [official source](https://www.marines.mil/News/Messages/Messages-Display/Article/3441944/enlisted-active-duty-service-limits/)

- [2026 DoW SkillBridge MOU](regs/dow-skillbridge-mou.txt) - [official source](https://www.skillbridge.mil/static/docs/2026_DoW_SkillBridge_MOU_BLANK.pdf)
- [VA Benefits and Services Participant Guide v6.1](regs/va-benefits-participant-guide.txt) - [official source](https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf), version 6.1 confirmed in the downloaded guide
- [MCCS Transition Readiness Program, Steps to Success](regs/mccs-trp-checklist.txt) - [official source](https://hawaii.usmc-mccs.org/marine-family-support/transition-readiness-program)
- [HQMC MMSR-2 enlisted retirement guidance](regs/mmsr-2-enlisted-retirements.txt) - [official source](https://www.manpower.marines.mil/Divisions/Manpower-Management/Separation-and-Retirements-Branch/Active-Duty-Retirements-Separations/)

## Reading the pack

Use the FAQ for your path, then confirm your dates and eligibility with the office named at the end of each answer. The glossary cites the copied regulations and supplemental texts, and identifies unresolved definitions. REVIEW.md is an unsigned review record pending maintainer approval.

Regulation bodies preserve the supplied extraction, including page headers, page breaks, and apparent revision artifacts. The HTML source was stripped of tags and reduced to the message body. Personal names, individual mailboxes, example personal phone numbers, and named units were replaced with bracketed removal labels to meet the pack's privacy rule. Printed office lines and office mailboxes may remain. Long dashes were changed to short hyphens. These copies are sanitized reading copies; use the official sources for the full originals.

Enlisted retirement is covered: FMCR transfer with 20 to 29 years of active service and direct retirement with 30 or more. The reporting unit submits to MMSR-2 through unit diary after eligibility review and CO counseling. The board uses shared transition, SBP and benefits items. Each item names the deciding office for individual eligibility, dates and waivers.

MARADMIN 175/24 directs an 18-to-6-month retirement/resignation window while the manual still prints 14-to-4-month diary limits. For enlisted retirement and FMCR requests, the copied MMSR-2 guidance expressly applies 18 to 6 months. The 9-month board target is inside both windows. IPAC and MMSR-2 must confirm processing and any earlier deadline.

MARADMIN 326/23 prints age 58 while the manual and MMSR page print 55. Overseas tour wording also differs and requires MMSR-2 review. MARADMIN 280/24 and 625/24 describe rank category limits and combined absences, while the later NAVMC 1700.2B prints different approval wording and a 180-day boundary. These conflicts require office review. The manual gives a 120-day VGLI no-health-proof period, while the copied VA guide gives 240 days. VA Insurance must confirm the governing deadline and individual eligibility.

## Citation format and checker

`citations.json` contains one entry for each distinct seed `(ref, para)` pair, including citations on benefit rows. Line numbers are one-based and inclusive, counting LF lines in the copied file, including its SOURCE header. `quote` retains the seed text exactly. Pairs with multiple distinct quote/URL variants have a `quotes` array containing every variant and its own file, range, and status; the top-level quote and range describe the first variant. The top-level status is true only if all variants verify, null only if every variant is an external web citation, and false otherwise.

A true status means the checker found matching text fragments in the stored source span. It normalizes whitespace and curly quotation marks. Literal three-dot ellipses divide a quote into fragments that must appear in order. Page headers and other furniture remain in the text; an ellipsis can skip them, but an unelided fragment must match across them. This establishes neither a verbatim unelided quotation nor paragraph accuracy. Paragraph and page labels still need human review.

Local supplemental pairs record the copied filename, inclusive LF range and fetched `source_url`. That field remains separate from the seed URL. Correctly recorded external web citations have null file, range and status; other unavailable quotes are false. The repaired seed uses copied source text for each citation. Unsupported web instructions were removed or replaced with questions for the responsible office. The copied pack does not settle all TRICARE, dental, drill-pay or combined insurance coverage rules. A matching citation does not settle those questions.

Run from the pack directory:

```sh
python3 check_citations.py
```

The default seed is the repository's `board/seed.json`; use `--seed /path/to/seed.json` for another copy. The checker rechecks all variants against the pack and exits nonzero on missing pairs, altered seed quotes or URLs, incorrect statuses, incorrect files, or incorrect ranges. Correctly recorded false or null citations remain visible but do not count as metadata mismatches. Use `--require-all-verified` to fail on every unavailable or external quote as well. This consistency mode does not mean all quotations have been verified.

## Report a wrong citation

Report the pack version, reference, paragraph, quote, copied filename and line range, and the official source with the text you believe is correct. Include whether the problem is missing text, a wrong paragraph, a revision conflict, or a bad URL. Do not include personal records or contact details. Submit the report through the project's issue process and request a reviewer role and correction; no maintainer address or issue URL was supplied for this pack.

## Supplemental source retrieval

MARADMIN 326/23 and the MMSR-2 active duty retirement page were retrieved from their official marines.mil URLs through Exa on 09 OCT 2026 after direct browser retrieval returned 403. The full retrieved text was read before citation. The saved copies preserve the retrieved body, remove personal contacts and replace long dashes with short hyphens. Their SOURCE headers identify the URLs. They supply enlisted service limits and current FMCR request-window guidance; they do not certify an individual record.

The SkillBridge MOU and VA participant guide were retrieved on October 8, 2026, and extracted using `pdftotext -layout`. Their SOURCE headers identify the exact downloaded URLs. Long dashes were changed to short hyphens. The TRP checklist steps were verified on October 9, 2026 against the MCCS Marine Corps Base Hawaii Transition Readiness Program page (`regs/mccs-trp-checklist.txt`, Steps to Success, captured from the live page in a browser because the site refuses non browser requests). The `_sources/` directory retains PDF and HTML source captures with a JSON retrieval log.

## Current transition, benefits and final-move sources

MCO 1700.31A cancels MCO 1700.31 in main paragraph 2. Its enclosure (2), chapter 5, paragraph 3.a-e, supplies the mandatory 365/365/180/120/90-day gates. Chapter 8, paragraph 4.a-b, supplies the retiree 24-month IC starting period and other Marines' 18-month IC starting period. Gates count from the confirmed EAS on va-service-end, separate from a retirement action date. Confirm that anchor with IPAC and the TRP office. Actual appointments are separate fixed events. The seven-day ROOB preparation lead is a planning target before the actual IC appointment. All transition requirements must be complete before SkillBridge participation under NAVMC 1700.2B, enclosure (2), paragraph 7. The new TRP order's chapter 3, paragraph 16, refers to NAVMC 1700.2A; the pack retains the later NAVMC 1700.2B as a separately named source. Confirm version conflicts with the installation SkillBridge coordinator and approving command.

The official VA dental page supplies Class IV rating, individual unemployability and temporary-rating criteria. The CHAMPVA page supplies family eligibility and the TRICARE exclusion. Each benefit has a cited seed row and task. Its verification office confirms eligibility. The blanket state-tax claim was removed. The VA intent to file page supplies a 1-year claim-completion period from the actual VA intent date. Record that confirmed event and have VA or an accredited VSO confirm the exact calendar-year anniversary before setting the separate fixed rule deadline. The board does not add calendar years to another item automatically.

Every path includes a DMO/TMO counseling target 90 days before the board separation or retirement date. The actual appointment and shipment entitlement/expiration are separate records. JTR paragraphs 052012 (A/C) and 052013 (A/B), with Table 5-52, distinguish separation, qualifying retirement/FMCR, shipment and storage. DMO/TMO must confirm the applicable paragraph, entitlement and exact dates from the orders. No universal final-move deadline is seeded.

Retrieved 09 OCT 2026: the new order was downloaded from MCCS Okinawa and extracted in full with pdftotext. VA page text comes from the main content downloaded from va.gov. Firecrawl retrieved the JTR PDF after direct GET returned 403. Its cover letter is OCTOBER 1, 2026. Complete paragraphs 052012 and 052013 carry the source, edition and retrieval date. Markdown emphasis was removed and long dashes replaced with short hyphens. Source captures are maintained under _sources/w6. The citation checker verifies copied text and provenance; it does not approve individual entitlement.

## Citation review, 21 OCT 2026

`citation-updates.json` adds authority to 13 previously uncited tasks and names a confirming office for the remaining 7. Its source registry records the official URL and access date. The VA26 requirements supply the source mapping; each short quotation was checked against official text retrieved during this review. New reading copies have dated SOURCE headers. eCFR Part 3 was retrieved through its official versioned API, current through 19 OCT 2026. Direct MCO PDF requests returned 403; the existing pack text was cross-checked against an Exa extraction of each official URL on 21 OCT 2026. These citations explain the subject and do not create deadlines or establish personal eligibility.

These planning tasks retain "No regulation cited" and a verify office:

| Task | Why it remains a planning task | Confirm with |
| --- | --- | --- |
| va-conditions | A personal issue list and record inventory | Accredited VSO representative |
| va-reserve | An inquiry about individual affiliation medical qualification | Military medical office and Career Planner |
| sep-tell | An early command discussion without a universal filing date | Commanding officer |
| sb-cert | A provider-specific funded exam and coverage period | SkillBridge provider |
| lv-tsp | A personal account access check | TSP support and unit pay office |
| fam-will | A personal appointment and family document review | Installation legal assistance |
| fam-budget | A personal budget based on actual statements | DFAS, VA and qualified financial or tax help |

Leave accounting and separation leave payment have authority, so lv-ledger and lv-final are cited. Their dates remain planning targets. `build_citations.py` regenerates citation locations after `board/build_seed.py`; `check_citations.py` independently checks the resulting metadata.
