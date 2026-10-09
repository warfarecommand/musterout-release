# USMC separation pack

Version: `usmc-2026.10`

This Muster Out pack collects 8 public Marine Corps regulation texts and 3 supplemental public source texts, a seed citation index, a separation glossary, and 10-question FAQs for resignation, retirement, and ordinary EAS. It contains no individual plan or unit contact roster. The copied texts are a fixed source snapshot, not a certification of current policy or personal eligibility.

## Documents

- [MCO 1900.16 CH-3 (MARCORSEPMAN)](regs/mco-1900.16-ch3.txt) - [official source](https://www.marines.mil/Portals/1/Publications/MCO%201900.16%20ADMIN%20CH-3%20%28SECURED%29.pdf)
- [MCO 1050.3J](regs/mco-1050.3j.txt) - [official source](https://www.marines.mil/portals/1/publications/mco%201050.3j.pdf)
- [NAVMC 1700.2B](regs/navmc-1700.2b.txt) - [official source](https://www.marines.mil/Portals/1/Publications/NAVMC%201700.2B%20%28SECURED%29.pdf)
- [MARADMIN 175/24](regs/maradmin-175-24.txt) - [official source](https://www.marines.mil/News/Messages/Messages-Display/Article/3739611/)
- [MARADMIN 045/25](regs/maradmin-045-25.txt) - [official source](https://www.marines.mil/News/Messages/Messages-Display/Article/4047837/)
- [MARADMIN 454/26](regs/maradmin-454-26.txt) - [official source](https://www.marines.mil/News/Messages/Messages-Display/Article/4611823/)
- [MARADMIN 280/24](regs/maradmin-280-24.txt) - [official source](https://www.marines.mil/News/Messages/Messages-Display/Article/3809908/)
- [MARADMIN 625/24](regs/maradmin-625-24.txt) - [official source](https://www.marines.mil/News/Messages/Messages-Display/Article/4015114/advance-notification-of-forthcoming-changes-to-mco-10503j-regulations-for-leave/)

- [2026 DoW SkillBridge MOU](regs/dow-skillbridge-mou.txt) - [official source](https://www.skillbridge.mil/static/docs/2026_DoW_SkillBridge_MOU_BLANK.pdf)
- [VA Benefits and Services Participant Guide v6.1](regs/va-benefits-participant-guide.txt) - [official source](https://tapevents.mil/Assets/ResourceContent/TAP/VA-Benefits-Participant-Guide.pdf), version 6.1 confirmed in the downloaded guide
- [MCCS Transition Readiness Program, Steps to Success](regs/mccs-trp-checklist.txt) - [official source](https://hawaii.usmc-mccs.org/marine-family-support/transition-readiness-program)

## Reading the pack

Use the FAQ for your path, then confirm your dates and eligibility with the office named at the end of each answer. The glossary cites the copied regulations and supplemental texts, and identifies unresolved definitions. REVIEW.md is an unsigned review record pending maintainer approval.

Regulation bodies preserve the supplied extraction, including page headers, page breaks, and apparent revision artifacts. The HTML source was stripped of tags and reduced to the message body. Personal names, individual mailboxes, example personal phone numbers, and named units were replaced with bracketed removal labels to meet the pack's privacy rule. Printed office lines and office mailboxes may remain. Long dashes were changed to short hyphens. These copies are sanitized reading copies; use the official sources for the full originals.

MARADMIN 175/24 directs an 18-to-six-month retirement/resignation window while the manual still prints 14-to-four-month diary limits. MARADMIN 280/24 and 625/24 describe rank category limits and combined absences, while the later NAVMC 1700.2B prints different approval wording and a 180-day boundary. These conflicts require office review. The manual gives a 120-day VGLI no-health-proof period, while the copied VA guide gives 240 days. VA Insurance must confirm the governing deadline and individual eligibility.

## Citation format and checker

`citations.json` contains one entry for each distinct seed `(ref, para)` pair. Line numbers are one-based and inclusive, counting LF lines in the copied file, including its SOURCE header. `quote` retains the seed text exactly. Pairs with multiple distinct quote/URL variants have a `quotes` array containing every variant and its own file, range, and status; the top-level quote and range describe the first variant. The top-level status is true only if all variants verify, null only if every variant is an external web citation, and false otherwise.

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

The SkillBridge MOU and VA participant guide were retrieved on October 8, 2026, and extracted using `pdftotext -layout`. Their SOURCE headers identify the exact downloaded URLs. Long dashes were changed to short hyphens. The TRP checklist steps were verified on October 9, 2026 against the MCCS Marine Corps Base Hawaii Transition Readiness Program page (`regs/mccs-trp-checklist.txt`, Steps to Success, captured from the live page in a browser because the site refuses non browser requests). The `_sources/` directory retains PDF and HTML source captures with a JSON retrieval log.
