<!-- Reader: board and release maintainers. Effect: implement the view contract while preserving planning rules and personal records. -->
# Design system and data schema

## View layer

The board is the design system. The view changes density and navigation; the planning engine, seed rules, date resolution, leave math, fingerprints and pack behavior remain intact except the approved migration add step for a plan option change.

Phone navigation has Today, Plan, Timeline, Claim and More in an opaque bottom bar with safe-area clearance. At 900 px and wider, the same destinations use the left rail. The content column is at most 720 px. The approved 18 OCT 2026 prototype geometry supersedes the previous Today dashboard, Plan pill rail and monthly Dates layout. IDs and stored dates are unchanged. The navigation and layout rules in this document define the public view contract.

Today uses a 48 px app bar, compact title/countdown, the Q2 purpose, three next actions sorted after visibility filtering with the existing critical-action priority, a Critical step legend and the earlier-date count with Review aligned right. Why these steps explains ordering. Ask follows, then leave balance with an editor that retains the current destination. A passed date says Date passed. Empty queues direct remaining work to Plan without suggesting Today filters. Save failures and update recovery stay visible.

Plan says Your transition tasks by area. All, 30 days and 60 days share one filter row with an area/status filter sheet. Hairline area disclosures show progress. Retirement is only the displayed name for sep; Reserve commission is the officer display name for dap. Tools contains Critical sequence and Office questions, followed by Add task and Leave and pay tools. Saved CHAMPVA tasks stay reachable through All tasks even when default suggestions hide them.

Timeline says See what's coming up and when. Upcoming windows are assigned once to disjoint horizons: this month, the rest of the quarter, through six months and through the action date. Chart is optional and discloses its first-12 limit. Recorded absences and SkillBridge endpoints remain visible; earlier, missing and later dates route to Plan. Undated boards show relative horizons derived from recorded rules, not invented calendar dates. The months-away preview never writes a date. No planning engine date math changes belong to this redesign.

Q2 state precedence is conditional preview, board completion, unknown date, passed date, empty filters, then ordinary purpose. Completion describes records on this board only. Conditional preview says Explore the steps before you decide. / Preview tasks, grouped by area. / See which steps come first. It retains an existing supported canonical preview path plus person-owned pathDecision=deciding, writes no dated seed marker and disables task edits until explicit path selection. Reserve Not sure exposes sourced options without opting into Reserve tasks.

Each item has three depths:

| Depth | Content and controls |
| --- | --- |
| Row | Seed label, date or relative offset, status meaning, 24 px check graphic within a 48 px button, and full-width title target at least 48 px. No regulation text. |
| Card | Seed brief, owner, date basis, Mark done, Steps and source. Only one card is open per view. |
| Drawer | Full why, how, verify, citations and excerpt, Open source, status, notes, date editor, custom Delete, and Ask about this item prefilled with the title. Escape and Close restore focus. |

Until new seed copy arrives, render title for label and the first sentence of why for brief. Item completion remains two taps from Today. The first phone screen is under 60 words; full critical and undated lists remain reachable.

## Tokens

The token contract is documented below. Automatic and explicit light use one map. Keep embedded IBM Plex fonts and their license. Values below replace the prior look section; use ink tokens for semantic text and matching tints for fills.

| `Token` | Light | Dark |
| `---` | --- | --- |
| `bg` | #f3f2ee | #0a0a0b |
| `bg-2` | #e9e8e3 | #101012 |
| `panel` | #ffffff | #151517 |
| `panel-2` | #f7f6f2 | #1c1c1f |
| `ink` | #1a1a1c | #eeeeee |
| `ink-2` | #4a4a4f | #b3b3b7 |
| `ink-3` | #5f5f65 | #98989e |
| `line` | #d9d8d3 | #343437 |
| `line-2` | #858580 | #737379 |
| `red` | #c8102e | #c8102e |
| `red-ink` | #8f0b21 | #ff4d63 |
| `red-tint` | #fbeaed | #33141b |
| `amber` | #b84e00 | #ff6b00 |
| `amber-ink` | #9a4000 | #ff8f40 |
| `amber-tint` | #f8ede5 | #342318 |
| `green` | #1a7d55 | #1f9d6b |
| `green-ink` | #166a49 | #43d197 |
| `green-tint` | #e8f2ee | #1b2c26 |
| `blue / blue-ink / focus` | #3b5c9a | #9db0d3 |
| `blue-tint` | #ebeff5 | #262c38 |
| `sb-band` | #f2e5db | #271b11 |
| `grid` | #e2e1dd | #242427 |
| `on-accent` | #ffffff | #ffffff |

Plex Sans is for reading; Mono is for dates and short metadata, stamp and wordmark; Condensed is for countdown and numeric summaries. Geometry follows the Density and spacing contract below; the approved V30 view roles are its current destination-specific implementation. Hairlines are 1 px, focus 2 px, and existing editor targets remain at least 48 px; approved V30 navigation and row actions use the 44 px touch role. Cards keep the existing theme appearance. Sheets and toasts retain their existing elevation and scrim.

Expand/collapse measured height and chevrons over 200 ms with `cubic-bezier(.2,0,0,1)`; state feedback is 120 ms. Reduced motion is immediate. Cancel prior animation on rapid toggles. Return focus before hiding a focused card. The bottom bar has layer 6, dialogs 20. Content bottom padding includes bar height, 24 px and safe area. Drawers and sheets trap focus, announce errors and return focus on close; controls remain usable at 200 percent text.

Use one accent per screen. Red denotes the stamp, urgency and primary action. Every semantic signal has words or a shape. White text is approved only on red. Input placeholders are ink-2 at opacity 1. Decorative separators use line; control boundaries use line-2. All text pairs require 4.5:1 in both themes. Verify keyboard, VoiceOver, TalkBack, focus return, reduced motion, 200 percent text and no horizontal scroll at phone and desktop widths.

Dates are `12 OCT 2026` with a four-digit year. The stamp includes date basis when known. E-labels count from the action date: E-120, E-DAY, E+30. The compact Today mark reads MUSTER OUT, red rule, WARFARE COMMAND. Other destinations show a plain title and small stamp. No service insignia.

## Density and spacing

This section is the geometry contract for future board work. The V30 block in the final geometry section adds founder-approved roles --v30-touch=44px, --v30-bar=48px, --v30-nav=56px and --v30-chip=36px; these do not change WC tokens. Normal Today task rows are 56px minimum and grow with wrapped or enlarged text. Today section gaps are 16px on phones; Plan and Timeline use 24px. The app bar and first task target the approved y140 normal phone density. Existing editor controls retain their 48px targets. Use the final DESIGN1 geometry block in `board/template.html`. Earlier CSS owns color, state, visibility, and interaction only. Add or change geometry in that final block; do not append another override layer. The token values and roles below are the public geometry reference.

| Tokens | Values and use |
| --- | --- |
| `--s-0` through `--s-8` | 0, 4, 8, 12, 16, 20, 24, 28, 32 px. Use these for padding, margins, and gaps. |
| `--text-xs/sm/md/lg/xl` | 12, 14, 16, 20, 24 px. Metadata, secondary copy, body and row title, section heading, page title. |
| `--lh-tight/meta/body` | 1.25, 1.333333333, 1.5. Unitless so text enlargement grows the line box. |
| `--text-display`, `--text-brand` | 64 px countdown; 11 px stamp matching the rendered WARFARE COMMAND wordmark. These are display exceptions, not reading sizes. |
| `--target`, `--row-height` | 48 px minimum interactive size; 56 px minimum two-line row. All are minimums and grow with text. |
| `--radius-sm/md/lg/full` | 8, 12, 20, 999 px. Controls, cards and groups, sheets, pills and circular graphics. |
| `--reading-width`, `--sheet-width` | 720 px centered reading column; 560 px maximum sheet width. |
| `--nav-height`, `--rail-width` | 72 px bottom navigation plus safe area below 900 px; 208 px left rail at 900 px and wider. |
| `--brand-width`, `--icon`, `--icon-sm` | 176 px preserved brand SVG; 24 px control graphic; 16 px source marker. |
| `--hairline`, `--stroke`, `--optical` | 1, 2, 1 px. Borders, focus, and the stamp's optical baseline adjustment. |

Page and card gutters are 16 px on both phone and tablet. Sections have 24 px separation, headings have an 8 px content gap, and related content uses 12 px. Keep reading and card edges aligned. Nested panels do not add a second gutter.

Rows share a 48 px completion column, 4 px column gap, 4 px vertical inset, 16 px title, and 12 px metadata. The row grows when titles or dates wrap. Keep the disclosure indicator vertically centered in the title target, with a stable trailing edge. Reserve a metadata end position for the critical diamond so it cannot wrap onto its own line.

Controls have 48 px minimum width and height. Buttons in a shared flex or grid row stretch to the same height. A 32 px filter pill sits inside a full 48 px button; informational chips do not acquire fake touch padding. Forms use 12 px gaps and full-width fields, collapsing to one column on phones.

The Today stamp sits beneath help and shares the WARFARE COMMAND bottom edge. Preserve the 176 px SVG and 11 px stamp, with a 1 px optical adjustment. Large text moves the stamp to a separate row and restores full 48 px date targets.

Ask uses the same 24 px section rhythm. Empty states use a 16 px inset and 24 px icon, without a fixed height. Footer separation is 24 px. Toasts are bounded to the viewport and clear the measured navigation by 16 px.

Sheets use 16 px gutters, a scrollable body, 48 px close and drag targets, and a separate action footer. They retain navigation clearance on phone and tablet. Safe-area insets remain additive. Large text and reduced motion remain supported. Dynamic timeline SVG coordinates and measured lane heights continue to use the existing date and collision layout; never replace those data-dependent dimensions with fixed spacing.

## Intake and trust

Chat delivers verified bytes and ends at Open your board. The page's three cards own path; date, basis and grade; Reserve and SkillBridge. Unknown options show Not set and seed as false. Later Yes runs only the engine's migration add step under its lock. It adds relevant items and preserves existing work. Undated mode resolves relative offsets from seed definitions and writes no dated seed marker. Demo is isolated. Successful dated completion preserves install id, original created time and channel, writes install state and clears setup. Open chats verify rather than rewrite.

Save states are Unsaved, Saving, Saved, Failed, Read-only and Unavailable beside the editor. Saved requires matching readback. Drafts persist before publish and are compared with newer device work on recovery. Update publishing requires files.write or the documented canEdit fallback, distinct from data.write. Signed release verification, publish, migration and install readbacks are required before Updated to is shown. UPDATE.md documents the separate page and chat journal contracts. The first offer is a sheet; Not now snoozes that version for 24 hours and a correction remains on Today. Keep pasted recovery available when the signed channel cannot finish.

Watch coverage is source-specific with checked time and timezone, window, last success, full-text/title-only status and possible matches. Never infer zero from failure or claim uncovered sources checked. Keep the last good result on failure, stale after eight days and use weekly recovery beyond the 30-day feed window. The board never posts. Send report saves and verifies the exact reviewed bytes, then says "Send it from the report page" with Open report page and Copy details in the sheet. The link uses only a fragment, never a query string. The pending report stays queued until a matching receipt is verified by chat. Reporting needs neither db nor sample for review and Copy diagnostic; report queuing requires explicit review, and usage transmission requires the learning gate. SUPPORT.md owns exact failure copy.

## Schema
Documents are keyed by collection and document id (`items/<id>`, `meta/profile`). The key is the identity. `meta/*` and `claim/*` documents have no `id` field. Records in `items`, `loes`, `contacts`, `blocks`, `conditions`, `links`, and `inbox` repeat their key in an `id` field. Unknown values remain `null` until confirmed.

| Collection | Fields |
| --- | --- |
| `meta/profile` | `name, grade (o5, o14, cwo45, wo13, e89, e67, e15), path (resign, retire, eas, ides), optional pathDecision (deciding or selected; absent preserves the existing selected-path behavior), reserve, sb, years, home, base, family, demo, retirementKind (retiredList, fmcr, or null), approvedForDate (action date associated with approval), dateBasis (planned, approved, or null when the person did not say), version, updated` |
| `meta/settings` | `eas, sbStart, sbEnd (null when unknown; the page never substitutes the EAS, and a sb rule resolves when its own endpoint is known while only the missing endpoint stays pending), planSet` |
| `meta/ledger` | `balance, asOf, accrualPerMonth, note, optional sla. With no balance: {"balance": null, "asOf": null, "accrualPerMonth": 2.5, "note": null}, and the Leave section in Dates shows its empty state` |
| `meta/seeding` | `claimedAt, by, profileKey (the claim while a seed runs; renewed every 30 seconds, expired after 2 minutes)` |
| `meta/seeded` | `at, count, profileKey, pack, version, revision. Boards seeded before 09 Oct 2026 have no profileKey; the page shows no mismatch line for them, and the key is attached only when the person makes an explicit keep or reset choice. It records acceptance of the retained plan, not the original seed profile.` |
| `meta/migration` | `from, to, at, revision, updated, added, retired, review[ids], state (running, complete), ops (per-id operation kind, expected field hash and readback flag; no personal values)` |
| `meta/reset` | `at, token (present only while a reset runs)` |
| `meta/watch` | `schemaVersion, feedSeq, feedGeneratedAt, feedExpiresAt, checkedAt, sources[{source, coverage, status, reason, lastAttempt, lastSuccess, window, checkedCount, unclassifiedCount, truncated, bodyAvailable, confidence, matches}]; legacy top-level window, checkedCount, truncated, bodyAvailable, confidence, matches and status project MARADMIN only` |
| `meta/watch_error` | `at, reason (present only when the newest check failed)` |
| `loes/<id>` | `id, n, name, lead, purpose` |
| `items/<id>` | `id, loe, order, kind (task, marker, window, milestone), title, label, brief, why, how[], owner, due (rule or null), window ({from, to} rules or null), basis (optional: rule or target; absent means rule), critical, presence, after (optional prerequisite ID array), cite[{ref, para, quote, url}], verify, status (open, doing, waiting, done, na), doneOn, notes, user, updated` |
| `contacts/<id>` | `id, name, role, org, phone, email, loe, note` |
| `blocks/<id>` | `id, start, end, status (approved, requested, known, planned, cancellation requested, canceled in MOL; legacy cancel is read and migrated as cancellation requested), away, kind (leave, liberty, ptad), note, updated` |
| `conditions/<id>` | `id, name, status (needs visit, in records, seen, in claim, rated), code, side, limb (null, LUE, RUE, LLE, RLE), words, rule, todo[], evidence[], exam, note, record[{date, entry, src}], src[{label, url}], updated` |
| `claim/where` | `rows[{appt, where, home, base, how}], note` |
| `claim/vso` | `rows[{rank, name, why, phone, email}], script, note, updated` |
| `claim/exposure` | `rows[{location, hazards, presumptive, action}], notes[]` |
| `claim/benefits` | `title, label, rows[{what, detail}], note, optional permanentAndTotalConfirmed (owner-confirmed boolean; absent means unknown)` |
| `links/<id>` | `id, title, url, loe, added` |
| `inbox/<id>` | `id, series, number, title, url, date, note, keys[], action, deadline, confidence, body_available, status (new, dismissed), applicability (possible until reviewed), filed` |

Step dependency field: optional seed-owned `after: ["item-id", ...]` lists true prerequisites; absent or [] means none. Each edge has a reason or citation in `packs/usmc/step-dependencies.json`. The builder rejects malformed arrays, duplicates, unknown IDs, self links, cycles and references excluded from a dependent's profile. Dependencies inform and never gate. VA26 says, "Dependencies below are implementation order, never a reason for a user to delay filing or care." `after` never changes a date.

Cards and drawers show nonempty Needs and reverse-derived Unlocks rows, each linking to the related item drawer regardless of its status. Missing saved references say unavailable. Today adds Ready only when nonempty, at most three items outside the unchanged next-three queue, in existing item order. A ready dependent already in that queue gets a small Ready tag in its Today row metadata. Each linked prerequisite must exist, be unretired and have explicit done or na status; missing, covered, approved or retired references do not satisfy it. Ready describes linked task statuses, never filing eligibility or an evidence verdict. Nothing is hidden, disabled, reordered or marked done because of dependencies; waiting remains a personal status. Plan keeps all ordinary actions available.

Migration includes after in seed ownership while preserving absence for released fingerprints. Unchanged 0.3.0 items receive links through the ordinary revision migration without review; edited seed fields retain their existing review flow. Personal and unknown fields remain unchanged. No date, completion or actual event is backfilled.

Seed display fields: label is imperative and at most six words. Brief is at most two sentences at grade 8, grounded entirely in the existing why, how or cite. Both belong to SEED_OWNED_FIELDS and receive released-hash replacement on existing boards; why remains the full drawer text. The brief checker rejects numbers, dates, form numbers and paragraph numbers absent from that item's source fields. Display copy never changes planning rules.

Chat setup state uses `meta/setup` for unfinished progress and `meta/install` for version, original created, channel, install_id and any existing registered or unknown fields. Page completion preserves installation identity and clears setup. A chat update stores stage and the confirmed manifest in `meta/update`; a page update stores from, to, at and state. Never confuse those owners or erase recovery state before verification.

Trust protocol 1 adds public authentication metadata only. Chat/folder update journals retain their existing stage owner and add trust_schema:1 plus target:{package,version,pack,mirrors,install,release,release_sha256,html_sha256,html_size,verifier}. install is the signed install envelope/signature/manifest; release holds the signed release envelope/signature, never HTML. The verifier version and both SHA-256 audit pins never self-authorize execution. The page's from/to/at/state journal stays page-owned and adds only trust_schema:1 and target:{package,version,pack,mirrors,release}. Missing/unknown pins retain recovery state; legacy page completion still verifies the same board. Confirmed chat/folder product retrieval tries the exact-version registry tarball first, then the two fixed CDN mirrors, independent of mutable main/latest. The existing mirrors field keeps its two CDN bases; the verifier separately fixes the registry host and version paths. Registry dist integrity checks transport only; release signatures and per-file hashes remain authority. No personal schema, planning, seed or telemetry behavior changes.

Signed notice writers use independent create-only feed_sequences/<writer-id> records:{highest_seq,envelope,signature,data,accepted_at}. Reverify durable records at their authenticated acceptance time before taking the maximum; unsigned meta/watch fields are not proof. Equal sequence requires the same signed payload digest/time/pack identity. Fresh expiry remains strict. Recheck the maximum around native watch/inbox writes and final success. The browser database has no document version precondition, so its public slots use independent random ids, fresh absence checks and readback. Native chat tools retain their create-only/version preconditions. These existing public-data paths do not carry personal facts.

Learning storage is `usage/<week>-<writer>` for weekly counters and immutable `outbox/<id>` for approved reports, plus consent and receipts in the board's Settings records. Settings uses `meta/usage_consent` with enabled, schema_version, schema_key, sample and approved_at; `receipts/<payload id>` with payload_id, status and acknowledged_at; and `outbox_control/<id>` with cancelled and at. Chat verifies the installed trust-layer contract before sending. Outbox envelopes carry schema_version, kind, id, payload, bytes, approved_at and status; only the frozen reviewed payload bytes go on the wire. Usage documents include local schema_version/status wrappers excluded from the wire payload. Copy diagnostic uses an in-memory error ring independent of these collections. B3's wire schema differs from L5's proposed samples: feedback allows kind, id, install_id, version, pack, path, grade, category, error_class, optional text and created; usage allows kind, install_id, week, writer, version and flat counters. Record schema approval on the board. It does not add a wire key. Reports are deleted from outbox only after matching acknowledgment and receipt readback. Counts are closed-week totals sent once per writer under current fixed-schema consent.

Date rules: `{"date": "YYYY-MM-DD"}`, `{"eas": n}`, `{"easMonths": n}`, `{"sb": "start"|"end"}`, `{"item": "<id>", "days": n}`, with optional `"biz": "prev"` to pull weekends and observed federal holidays back to the preceding business day. The seed uses `{"date": "SETUP"}` for "the day the board was set up". An `sb` rule with a null `sbStart` or `sbEnd` resolves to no date; the date column shows "Date pending SkillBridge approval" and the item sorts after dated items.

Three kinds of date, named the same in the page, the docs, and the skills: a rule deadline (`basis` absent or `"rule"`), the date the cited text sets; a planning target (`basis: "target"`), a date the pack picked inside a wider window, which is a plan and not a deadline; and a confirmed event, a date the person set after an approval or a booking, or a `doneOn`.

Profile key: `path|grade|reserve|sb|eas|sbStart|sbEnd` from `meta/profile` and `meta/settings`, joined with `|`, booleans as `true` or `false`, nulls as the string `null`.

Seeding: the page seeds when it opens with a confirmed dated profile, no `meta/seeded`, and no `meta/reset`. It takes `meta/seeding` with the runtime's `acquire` lease (holder is the tab's seed id, 45 second lease, renewed every 30 seconds); a browser without `acquire` does not seed and says so. A busy or rejected renewal aborts the seed at once. Before each seed write it reads that document fresh and skips it if it exists, so it never overwrites an item, line of effort, contact, or claim document, whoever wrote it. Before writing `meta/seeded` it reads `meta/profile` and `meta/settings` fresh and aborts without the marker if the key changed; the page then shows "Your profile changed while the board was being set up. Run /intake reset in the Muster Out folder to rebuild the plan." While `meta/reset` exists the page refuses every write, closes any open edit form, drops its cached records from the view, and stops claim renewal; when the marker clears it re reads the meta documents fresh before deciding to seed. If `meta/seeded.profileKey` differs from the live key, the page does not reseed; it shows "Your path or dates changed since the plan was seeded. Run /intake reset to rebuild the plan, or Edit profile to keep this one." and still recomputes dates from the live settings.

Pack corrections: after the existing seed checks, a writable page migrates an older seed version under the same `meta/seeding` acquire lease and claim deletion used by first seeding. It also recognizes legacy markers without a version and changes to the embedded seed revision at the same product version. A newer installed seed is never downgraded. A present pack and profile key must agree. Legacy markers without a pack receive the current pack after migration. Resets, profile changes, unavailable locks and failed renewals stop the migration. Release checks use a separately verified isolated worker with no board context; they do not change planning or migration rules.

Item ownership is defined once by `SEED_OWNED_FIELDS`, `PERSON_OWNED_FIELDS`, and `PERSON_OWNED_COLLECTIONS` in `board/template.html`. The builder reads those lists and rejects an emitted item field without an owner. The item key and repeated `id` hold its identity throughout migration.

- Seed fields: `loe`, `order`, `kind`, `title`, `label`, `brief`, `why` (body), `how`, `owner`, `due`, `window`, `basis`, `critical`, `presence`, `attendance`, `cite`, `verify`, `when` (path flags), `phase`, `path`.
- Person fields: `status`, `doneOn`, `eventOn`, `eventForDate`, `notes`, `user`, `updated`, `userDates`, `retired`, `retiredNote`, and every unknown item field. A person's changes to `due` or another seed field require review and stay intact until accepted. Entire `user: true` items belong to the person. Seed status, notes and doneOn values are defaults used only when adding an item.
- Person collections: `blocks`, `contacts`, `conditions`, `inbox`, `links`, `claim`, `meta/ledger`, `meta/settings`, `meta/profile`. Migration never writes these collections. It also preserves all other meta documents and unknown marker fields.

Fingerprints are SHA-256 over UTF-8 JSON of seed fields with object keys recursively sorted, array order retained, and absent fields omitted. The compact embedded map holds each item id's hash for every CHANGELOG release plus the current seed. Release repository commits on the CHANGELOG date supply released snapshots. The release repository starts at 0.1.2; 0.1.0 and 0.1.1 use product commits that wrote their shipped archive on the release date. Same-version reissues contribute additional fingerprints, including all pilot builds. Commit ids are embedded as provenance. Historical source text is never embedded. The map stays below 100,000 bytes. Shipped folder builds reuse the map from their verified page when history is unavailable and fail if a released version is missing.

Older pages stripped `when` and materialized `due.date: SETUP`. Matching restores missing tags from each historical fingerprint's shape and restores SETUP only when the stored date equals `meta/settings.planSet`, or the original `meta/seeded.at` date when planSet is absent. Unknown setup dates are kept for review. Hashes matching any released seed allow replacement of all seed fields. Field patches remove obsolete nested rule keys and preserve every other field. Edited seed fields receive a review entry. New applicable items are added; dropped historical items are retained with `retired: true` and a short `retiredNote`. Unrecognized custom items stay outside migration; retirement preserves status and personal notes on historical seed items.

`meta/migration.ops` journals each planned item write before it runs and its completion after readback. A resume recognizes writes that succeeded before the completion flag was saved, so counts survive interruptions. Every item write, the completed journal, and the final seed marker are read back. Only then does `meta/seeded` advance its version, revision and non-user item count. Retired items remain in that count. A completed version and revision cause subsequent loads to make no writes. Plan shows `Updated to <version>: <n> items corrected, <n> added.` and each review item with an `Accept pack version` button. Acceptance takes the same lock, replaces only seed fields, keeps personal fields, verifies the record, and removes that id from review. A dropped edited item stays in review for Claude to resolve.

The browser database API has no document version precondition. Migration uses the supported cooperative lease, fresh reads before field patches, and readback. Personal notes and completion never appear in replacement patches. A writer that changes seed fields without taking the lease during the final read/write interval cannot be excluded by this API; keep the board idle during the confirmed update and review any concurrent changes before completion.

Reset: while `meta/reset` exists the page never seeds and never claims, still renders the records it has, and shows one line in the Brief: "Reset in progress. Finish it in the Muster Out folder with /intake."

Watch: `/watch` writes `meta/watch` only after a check that passed every feed rule, and on a failed check writes `meta/watch_error` and leaves `meta/watch` as it was; the next good check deletes `meta/watch_error`. A check with `truncated: true` or any `body_available: false` has `confidence: "titles"`, and any "nothing matched" line from it says "by title". The Brief shows "Watch: checked <date>, <n> messages, <confidence label>", and when `meta/watch_error.at` is newer than `meta/watch.checkedAt`, "Last check failed <date>: <reason>. Showing the last good check."

Seed tags: every seed record carries `when`, a list of flags that must all hold for the record to be included: `resign`, `retire`, `eas`, `officer`, `enlisted`, `reserve`, `noreserve`, `sb`, `nosb`, `cat1`, `cat2`, `cat3`, `notretire`. The page computes the flags from the profile.

Leave forecast disclosure: open by default when the projection contains a fiscal loss event. An existing disclosure choice takes precedence, including a saved closed state. Leave loss cards use the board military date format, such as `01 OCT 2027` and the inclusive deadline `by 30 SEP 2027`.

Leave projection credits earned half-days chronologically through each service date before that day's leave charge and SLA ceiling/minimum check (Instruction 1327.06 para 3.9; FMR Vol 7A ch 35 para 2.2.2.6). Daily minima use closing balances after earned credit and charges. Monthly accrual and closing totals retain the existing partial-month convention.

Leave projection: `asOf` includes all accrual and charges through that day. Project only later service days, count the union of charged dates, and stop at the explicit last-active override when recorded, otherwise at EAS for separations, on the entered FMCR release date, or the day before the explicit Retired List effective date (MCO 1900.16 App E, E006.1.c(2)-(3)). The action date remains the anchor for action-based rules. An `asOf` after today or the last active-duty day suppresses the projection and shows a warning.

Optional `meta/ledger.sla`: absent or `null` means unknown; `0` or `{"days": 0, "expires": null}` confirms no special leave accrual. Otherwise use `{"days": <IPAC-confirmed protected excess, 0 to 30>, "expires": "YYYY-MM-DD"}`. `days` is protected excess above the ordinary 60-day carryover cap. The confirmed expiration is the last valid day, inclusive. At the start of 1 October, before that day's charges or accrual, apply the prior 30 September closing balance against `60 + days` while protection remains valid, at most 90 total. Leave above the cap is forfeited, including in the final service year. The projected SLA ceiling declines with the lowest balance, never regrows with later accrual, and disappears at 60 or below, per DoD FMR Vol 7A ch 35 paras 2.2.2.4 and 2.2.2.4.1. This is a local projection only; the saved SLA approval is unchanged. Service ending on or before 30 September has no post-service October forfeiture. Unknown SLA uses the ordinary 60-day cap and keeps the numeric forecast, KPIs, chart and month table. One caution appears in Conflicts when an upcoming loss is projected. Values above 30 remain unchanged and visibly flagged for IPAC review, using no SLA protection until corrected. Saving another ledger field preserves the legacy SLA record exactly; changed above-30 entries fail validation. Authority: 10 U.S.C. 701(b), (e) and Instruction 1327.06 paras 3.6 and 3.8. The earlier SLA transition ended by 30 September 2026.

Use-or-lose cards derive their day counts from model loss events and offer Add leave. Timeline shows future events; Today shows a card when the 30 September deadline is within 120 days, inclusive. Cards explain terminal leave and the ordinary 60-day career sellback cap, subject to prior sales and IPAC confirmation. A projected last-day balance above 60 gets the same planning guidance directly below the KPIs. Neither sold leave nor terminal leave is inferred from a projected balance.

Leave cancellation: legacy `cancel` means cancellation requested. Pending cancellation stays charged and keeps absence conflicts until the person selects `canceled in MOL`. The page migrates legacy statuses only when the live store can be edited and reset checks have finished, and continues charging leave with any unknown status.

## Build
`board/build_seed.py` writes `board/seed.json` and checks every rule target for every profile combination. `board/build_board.py` generates the released fingerprint map and injects it with the seed into `board/template.html` and writes `board/board.html`, the file that gets published. Both refuse to write if an em or en dash or a personal string appears.

CHAMPVA default visibility is presentation only: show fam-champva when a condition is recorded or claim/benefits.permanentAndTotalConfirmed is explicitly true. Estimated or calculated ratings never establish eligibility. All tasks reveals the preserved saved record. Claim > Benefits offers the explicit confirmation; no backfill and no automatic status changes. Retiree TRICARE copy and VA confirmation remain.

## V30 update experience (MTN-98 items 1-4)

Verified signed release notes feed a separate What's new sheet. Update now always requires an explicit tap. The ordinary offer snoozes that version for 24 hours. Seven days after the first verified offer on this installed version, it becomes a banner whose dismissal lasts only this visit. The existing signed correction=true flag is the critical flag, and signed impact supplies its reason. Critical offers ignore persistent snoozes, retain their compact Correction ready banner after the sheet closes, and open the sheet again on the next visit. Neither state auto-applies.

In-board restore snapshots are deferred by TRS's 18 October ruling after a disconnected-writer race failed independent proof. The candidate contains no capture, snapshot storage, purge or sweep code. Original writes, deletion and privacy behavior remain unchanged. Update publication still drains writes, persists drafts and follows the existing pinned journal and migration verification.

Optional Save a backup to this device uses downloads.save after an owner action. Warning: This file contains your plan details. Keep it somewhere private. It exports plan records and profile/settings/ledger, including medical and coach notes, and excludes registration credentials, consent, usage and report receipts. The platform owns save confirmation. No email nudge is implemented.

## MTN-95 planning semantics

Approval coverage is derived. For an applicable approved retirement date, only `ret-request-o`, `ret-request-e`, `ret-receipt-e` and `ret-counsel-e` become Covered by approval. For resignation, only `sep-diary`, `sep-letter` and `sep-counsel` do. Existing explicit Done and Not applicable states win. Covered tasks are closed for action lists and excluded from completion totals; they are never counted completed or waived. Counseling retains an IPAC record-verification note. No stored item states or completion stamps change when coverage is displayed.

Personal `eventOn` records the actual approval, orders-received or office-confirmed appointment date for `ret-approval`, `sep-approval`, `sb-approval`, `ret-orders`, `sep-orders`, `eas-orders` and confirmed appointment rows ending in `-appt`. `eventForDate` associates a personal event with its action date. Missing or cleared `eventOn` is unknown. A legacy fixed `due.date` remains a saved target; `doneOn` is completion bookkeeping. Neither supplies an actual event date. Actual event dependencies use only `eventOn`; generic task dependencies retain completion-date behavior. These fields are person-owned and migration never populates defaults on existing records.

Rules support `{min: [rule, ...]}`, `{sb: "start"|"end", days: integer}`, `{unitDeparture: days}` and `{terminalStart: days}`, in addition to existing fixed, action-date, calendar-month, service-end, item and by-path rules. Minimum aggregation ignores unresolved branches and preserves the known constraint. Cycles terminate without discarding a known sibling. Wrapper traversal must preserve provenance, pending endpoints, dependency validation and export privacy. TRP minimum rules retain the original -365/-365/-180/-120/-90 service-end deadlines and add the day before known SkillBridge start. These are latest completion limits, separate from appointments.

Retired List effective dates project the last active day one day earlier; FMCR release dates are inclusive. An unclassified legacy date retains its original saved-date inference throughout what-if and shows a warning. Explicit kind wins over grade. Unusual calendar dates and officer/FMCR combinations warn without normalization. A valid fixed `va-service-end.due.date` is the common effective last-active override for leave, TRP, BDD and office counts. The default `serviceEnd` rule calls projection directly to avoid a resolver cycle. Office counting uses effective last active day plus one as the exclusive end.

Terminal leave is the inclusive connected union of active chargeable leave intervals reaching effective service end. Adjacent blocks merge. Liberty, PTAD and canceled-in-MOL blocks do not establish terminal leave. A block beyond service end stays unchanged, may supply its original departure start, and warns. Unit departure is the earliest known SkillBridge start, terminal start or service-end-plus-one fallback. End-only SkillBridge never supplies a start. Unit lead offsets remain planning targets and fixed personal dates stay fixed. Seed turnover uses seed-owned `attendance: "interval"`; custom presence windows are attendance intervals, while allowed filing windows scan their target point. Shared inclusive presence warnings identify item and period (`sb` or `leave`) and include nontravel leave and PTAD. The independent cited `terminal-predeparture` rule requires administrative and medical separation processing before terminal departure, including undated work.

Intake stays at three cards: retirement date meaning is on card 2, and optional independent SkillBridge endpoints appear on card 3 after Yes. Profile/date editors share retirement-kind and endpoint validation. End equal to last active day and a one-day participation interval are valid. What-if uses the same warnings without state writes; saving a changed hypothetical date marks it Planned and retains historical approval association, completion and actual event dates. Changing a date in the direct editor defaults its status to Planned before a person explicitly selects Approved.

A legacy unclassified retirement may preview a changed date using its saved inference, but saving that move in what-if, the date editor or the profile editor requires an explicit Retired List or FMCR choice. Keeping the original date may retain Not sure. Verified actual-date saves update the open item summary without resetting focus, scroll or other drafts. Missing SkillBridge endpoints have separate warnings: a known start already anchors preparation even while the end is unknown.

Explicit migration acceptance restores the selected applicable release item's canonical seed fields, including removal of a manual fixed due date or window. Leaving an edit unaccepted keeps its entire record and review entry. Acceptance journals a same-release, same-revision intent containing the selected ID and before/after seed hashes under the existing lease. Only that authorized ID can resume after interruption. Canonical equality verifies and finishes its operation without a duplicate item patch; a concurrent seed edit abandons the intent and keeps the edited row for review. Pending intent remains visibly incomplete until the canonical item, operation journal and seed marker have been verified. Acceptance and its recovery skip unrelated contact and claim quote repair. Every personal or unknown field stays outside the seed-field patch.

The staged-site Ask demo uses a pure projection of the current board rule grammar for its captured built-in demo profile. Its source, answer wording and maximum length remain checked. The projection is independently compared against every applicable seeded demo item and window endpoint before a release.


## IDES confirmed-event path

Reader: Marines navigating IDES and maintainers preserving their records. Effect: track the current confirmed stage and administrative events without predicting an agency decision.

`meta/ides` owns schemaVersion 1, caseId, cycleId, stage, stageConfirmed, outcome and outcomeConfirmed, events, selectedEvents, branchConfirmations, calendarConfirmations and projections. It is a separate document. Ordinary meta/settings writes cannot remove IDES events, and an IDES write cannot change EAS. The profile path stays ides for fit return, severance, PDRL and TDRL. Unknown disposition is a real state.

`events.<eventType>.<occurrenceId>` stores local ISO date, optional appointment time and required timezone for timed appointments, classification actual or issued_future, status, confirmationBasis, confirmedBy=Marine, officeConfirmed, verifierOffice, confirmedAt, opaque local noticeId, supersedesOccurrenceId and selectedForBranch. Case-wide events use the case key; repeatable notices and exams use the explicit review cycle. The person confirms the event on its named task. No medical narratives or documents are parsed or stored in this ledger.

`selectedEvents.<requirementId>.<deadlineIndex>.<occurrenceId>` keeps an object with occurrenceId and confirmed or superseded status for each choice. Confirm one occurrence for each clock. If two saved selections remain confirmed, compare them before deriving a date. `event:<eventType>` selects a factual milestone display. Never select the newest occurrence by sorting. A corrected occurrence supersedes its predecessor and invalidates affected selections until explicitly reconfirmed. Actual facts must be past or present; issued future facts never become actual automatically. Neither task status nor completion bookkeeping supplies receipt, attendance, filing, consent or election evidence.

A meta/ides write takes its cooperative lease and compares a fresh read with the editing baseline. It reads again at the write boundary, renews the same holder lease immediately before update, and sends only changed fields. ArtifactData has no transactions: update deep-merges objects and replaces arrays. IDES never sets this document, including initialization. After update it reads back its changed fields and every field from the last fresh record, with the intended patch applied. Any difference retains the draft and shows a visible save conflict. A stalled update cannot erase a different occurrence. Preserve drafts and reject cross-device conflicts. Failed or disputed events produce no dependent calculation. Readonly views keep care and free counsel reachable. Wounded Warrior support and accredited VA help also remain available.

The dated-plan requirement has an IDES exception. An initialized IDES path with a valid grade can seed tasks without an EAS through the existing seed lock and verification. It never invents a date to obtain a marker. Today shows actions for the current confirmed stage and confirmed response periods. Timeline shows confirmed events and supported dates. All historical records and ordinary seed formulas remain stored; the IDES view suppresses incompatible BDD, EAS and ordinary retirement projections. Fit return preserves history and care while removing departure recommendations.

IDES uses DEP's optional seed-owned after arrays and its related-step and readiness renderer. Edges inform navigation; they never gate care, filing, help or completion. Optional review branches do not all become prerequisites for final disposition. The explicit assembled IDES set includes its 37 new IDs and 51 mapped existing IDs without rewriting ordinary predicates or shared completion meanings.

The date adapter reads saved selected occurrences. Navy and DoD business clocks default to the federal workday calendar, with a visible PEBLO-confirmation label. An optional office-confirmed calendar overrides that default; an invalid or expired custom calendar leaves its date uncalculated. VA calendars remain separate. The shared SML first-year helper supplies the VA workday rule; the 11-month planning target is unshifted and a disputed leap-day anniversary returns no date. Unknown VARR and notice-sufficiency questions stay visible beside immediate counsel help. Office duties, processing goals, minimum notice and presumed-acceptance risk never create a Marine overdue state. SBP displays an exclusive before-entitlement boundary.

Source ownership is the Muster Out maintainer with Navy, Marine and VA source review. The accepted research is dated 20 OCT 2026 and names a 23 OCT review. Every conflict and retrieval limit remains available for review; product acceptance and release stay separate from a person's confirmations.

The IDES money panel compares gross statutory formulas from inputs the person supplies. It does not infer a disposition or write events. Disability percentage is capped at 75 percent; the separate longevity method is compared without inheriting that cap, and TDRL has its 50 percent minimum. Severance rounds additional service at six months and applies the selected statutory minimum and 19-year maximum. Net pay, tax, concurrent receipt and recoupment remain office handoffs.

Unreleased IDES schema amendment, REFIDB round 1: events and selections are occurrence-keyed objects; superseding marks status and never deletes entries. Branch and calendar confirmations remain requirement/calendar-keyed objects with an occurrence-keyed `occurrences` history. Each replacement marks the prior confirmation superseded and appends a confirmed occurrence. Calendar years, workdays and holidays are boolean-keyed objects; false marks a removed member. Confirmation containers never use arrays. If concurrent updates leave multiple confirmed choices or confirmation versions, their records survive, derived dates stay unknown, and the saving device shows a conflict with its draft retained. Saved branch and calendar versions are readable from their confirmation forms. This directly replaces the unreleased shape; no field migration or SQL migration is required. Sparse updates and readback detect conflicts but do not claim transactional fencing.


Watch Officer 0.3.2 uses an installed schema-3 profile with seven active sources. Keep each failed or incomplete source visible, M21-1 explicitly off, and saved four-source history labeled with its actual scope. The digest stays four sources. Feed selection and durable replay history are contract behavior; never offer an unsigned feed/profile switch in the product.
