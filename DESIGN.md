# Design system and data schema

## Look
The board is the design system. Everything the product shows (the docs site, the lesson, the watch page) uses the same tokens.

- **Surfaces, dark:** `#0a0a0b` page, `#101012` secondary, `#151517` panel, `#1c1c1f` raised panel. Hairlines at 8 and 15 percent white.
- **Surfaces, light:** `#f3f4f5` page, `#e9ebed` secondary, `#ffffff` panel, `#f6f7f8` raised. Hairlines at 10 and 18 percent near black. The page follows the viewer's theme; both are first class.
- **Ink, dark:** white at 93, 66, and 56 percent. Light: near black at the same steps. Labels never drop below 4.5:1 against their surface.
- **Signal colors, semantic only:** red `#C8102E` (ink `#ff4d63` on dark) for the critical path, late, and the brand stroke; amber `#FF6B00` for warnings and the SkillBridge band; green `#1f9d6b` for done; blue `#9db0d3` for information. Red is not decoration.
- **Type:** IBM Plex Sans for reading, IBM Plex Sans Condensed for dense rows and the Timeline, IBM Plex Mono for dates, labels, the stamp, and the wordmark. Minimum 12 px for body text and for labels.
- **Dates:** `12 OCT 2026` in mono caps everywhere, always with a four digit year, the date column included. The EAS carries its basis as a label when one is set: `EAS 1 MAY 2027, planned`. E-labels count from the date: `E-120`, `E-DAY`, `E+30`. Long form `Mon 12 Oct 2026` in prose.
- **Components:** the stamp (red stroke box, EAS or RET over the date), the hero countdown, the LOE strip with progress bars, item rows with the regulation drawer, the Timeline with office days, the Do next panel, the Flags list, toasts with save state.
- **Mark:** the stamp. The wordmark is MUSTER OUT in Plex Mono caps inside the stamp stroke. No service insignia, ever.
- **Voice in the interface:** short declaratives, "you", no exclamation points, no emoji, short hyphens only.

## Schema
Documents are keyed by collection and document id (`items/<id>`, `meta/profile`). The key is the identity. `meta/*` and `claim/*` documents have no `id` field. Records in `items`, `loes`, `contacts`, `blocks`, `conditions`, `links`, and `inbox` repeat their key in an `id` field. Unknown values are stored as `null`, never invented.

| Collection | Fields |
| --- | --- |
| `meta/profile` | name, grade (o5, o14, cwo45, wo13, e89, e67, e15), path (resign, retire, eas), reserve, sb, years, home, base, family, demo, dateBasis (planned, approved, or null when the person did not say), version, updated |
| `meta/settings` | eas, sbStart, sbEnd (null when unknown; the page never substitutes the EAS, and a `sb` rule resolves when its own endpoint is known while only the missing endpoint stays pending), planSet |
| `meta/ledger` | balance, asOf, accrualPerMonth, note, optional sla. With no balance: `{"balance": null, "asOf": null, "accrualPerMonth": 2.5, "note": null}`, and the Leave tab shows its empty state |
| `meta/seeding` | claimedAt, by, profileKey (the claim while a seed runs; renewed every 30 seconds, expired after 2 minutes) |
| `meta/seeded` | at, count, profileKey, pack, version, revision. Boards seeded before 09 Oct 2026 have no `profileKey`; the page shows no mismatch line for them, and the key is attached only when the person makes an explicit keep or reset choice. It records acceptance of the retained plan, not the original seed profile. |
| `meta/migration` | from, to, at, revision, updated, added, retired, review[ids], state (running, complete), ops (per-id operation kind, expected field hash and readback flag; no personal values) |
| `meta/reset` | at, token (present only while a reset runs) |
| `meta/watch` | checkedAt, feedGeneratedAt, window {from, to}, checkedCount, truncated, bodyAvailable, confidence (full, titles), matches[{id, title, date, why, url}], status (ok) |
| `meta/watch_error` | at, reason (present only when the newest check failed) |
| `loes/<id>` | id, n, name, lead, purpose |
| `items/<id>` | id, loe, order, kind (task, marker, window, milestone), title, why, how[], owner, due (rule or null), window ({from, to} rules or null), basis (optional: rule or target; absent means rule), critical, presence, cite[{ref, para, quote, url}], verify, status (open, doing, waiting, done, na), doneOn, notes, user, updated |
| `contacts/<id>` | id, name, role, org, phone, email, loe, note |
| `blocks/<id>` | id, start, end, status (approved, requested, known, planned, cancellation requested, canceled in MOL; legacy cancel is read and migrated as cancellation requested), away, kind (leave, liberty, ptad), note, updated |
| `conditions/<id>` | id, name, status (needs visit, in records, seen, in claim, rated), code, side, limb (null, LUE, RUE, LLE, RLE), words, rule, todo[], evidence[], exam, note, record[{date, entry, src}], src[{label, url}], updated |
| `claim/where` | rows[{appt, where, home, base, how}], note |
| `claim/vso` | rows[{rank, name, why, phone, email}], script, note, updated |
| `claim/exposure` | rows[{location, hazards, presumptive, action}], notes[] |
| `claim/benefits` | title, label, rows[{what, detail}], note |
| `links/<id>` | id, title, url, loe, added |
| `inbox/<id>` | id, number, title, url, date, note, keys[], action, deadline, confidence, body_available, status (new, dismissed), filed |

Date rules: `{"date": "YYYY-MM-DD"}`, `{"eas": n}`, `{"easMonths": n}`, `{"sb": "start"|"end"}`, `{"item": "<id>", "days": n}`, with optional `"biz": "prev"` to pull weekends and observed federal holidays back to the preceding business day. The seed uses `{"date": "SETUP"}` for "the day the board was set up". An `sb` rule with a null `sbStart` or `sbEnd` resolves to no date; the date column shows "Date pending SkillBridge approval" and the item sorts after dated items.

Three kinds of date, named the same in the page, the docs, and the skills: a rule deadline (`basis` absent or `"rule"`), the date the cited text sets; a planning target (`basis: "target"`), a date the pack picked inside a wider window, which is a plan and not a deadline; and a confirmed event, a date the person set after an approval or a booking, or a `doneOn`.

Profile key: `path|grade|reserve|sb|eas|sbStart|sbEnd` from `meta/profile` and `meta/settings`, joined with `|`, booleans as `true` or `false`, nulls as the string `null`.

Seeding: the page seeds when it opens with a profile, no `meta/seeded`, and no `meta/reset`. It takes `meta/seeding` with the runtime's `acquire` lease (holder is the tab's seed id, 45 second lease, renewed every 30 seconds); a browser without `acquire` does not seed and says so. A busy or rejected renewal aborts the seed at once. Before each seed write it reads that document fresh and skips it if it exists, so it never overwrites an item, line of effort, contact, or claim document, whoever wrote it. Before writing `meta/seeded` it reads `meta/profile` and `meta/settings` fresh and aborts without the marker if the key changed; the page then shows "Your profile changed while the board was being set up. Run /intake reset in the Muster Out folder to rebuild the plan." While `meta/reset` exists the page refuses every write, closes any open edit form, drops its cached records from the view, and stops claim renewal; when the marker clears it re reads the meta documents fresh before deciding to seed. If `meta/seeded.profileKey` differs from the live key, the page does not reseed; it shows "Your path or dates changed since the plan was seeded. Run /intake reset to rebuild the plan, or Edit profile to keep this one." and still recomputes dates from the live settings.

Pack corrections: after the existing seed checks, a writable page migrates an older seed version under the same `meta/seeding` acquire lease and claim deletion used by first seeding. It also recognizes legacy markers without a version and changes to the embedded seed revision at the same product version. A newer installed seed is never downgraded. A present pack and profile key must agree. Legacy markers without a pack receive the current pack after migration. Resets, profile changes, unavailable locks and failed renewals stop the migration. The page makes no release request.

Item ownership is defined once by `SEED_OWNED_FIELDS`, `PERSON_OWNED_FIELDS`, and `PERSON_OWNED_COLLECTIONS` in `board/template.html`. The builder reads those lists and rejects an emitted item field without an owner. The item key and repeated `id` hold its identity throughout migration.

- Seed fields: `loe`, `order`, `kind`, `title`, `why` (body), `how`, `owner`, `due`, `window`, `basis`, `critical`, `presence`, `cite`, `verify`, `when` (path flags), `phase`, `path`.
- Person fields: `status`, `doneOn`, `notes`, `user`, `updated`, `userDates`, `retired`, `retiredNote`, and every unknown item field. A person's changes to `due` or another seed field require review and stay intact until accepted. Entire `user: true` items belong to the person. Seed status, notes and doneOn values are defaults used only when adding an item.
- Person collections: `blocks`, `contacts`, `conditions`, `inbox`, `links`, `claim`, `meta/ledger`, `meta/settings`, `meta/profile`. Migration never writes these collections. It also preserves all other meta documents and unknown marker fields.

Fingerprints are SHA-256 over UTF-8 JSON of seed fields with object keys recursively sorted, array order retained, and absent fields omitted. The compact embedded map holds each item id's hash for every CHANGELOG release plus the current seed. Release repository commits on the CHANGELOG date supply released snapshots. The release repository starts at 0.1.2; 0.1.0 and 0.1.1 use product commits that wrote their shipped archive on the release date. Same-version reissues contribute additional fingerprints, including all pilot builds. Commit ids are embedded as provenance. Historical source text is never embedded. The map stays below 100,000 bytes. Shipped folder builds reuse the map from their verified page when history is unavailable and fail if a released version is missing.

Older pages stripped `when` and materialized `due.date: SETUP`. Matching restores missing tags from each historical fingerprint's shape and restores SETUP only when the stored date equals `meta/settings.planSet`, or the original `meta/seeded.at` date when planSet is absent. Unknown setup dates are kept for review. Hashes matching any released seed allow replacement of all seed fields. Field patches remove obsolete nested rule keys and preserve every other field. Edited seed fields receive a review entry. New applicable items are added; dropped historical items are retained with `retired: true` and a short `retiredNote`. Unrecognized custom items stay outside migration; retirement preserves status and personal notes on historical seed items.

`meta/migration.ops` journals each planned item write before it runs and its completion after readback. A resume recognizes writes that succeeded before the completion flag was saved, so counts survive interruptions. Every item write, the completed journal, and the final seed marker are read back. Only then does `meta/seeded` advance its version, revision and non-user item count. Retired items remain in that count. A completed version and revision cause subsequent loads to make no writes. The Brief shows `Updated to <version>: <n> items corrected, <n> added.` and each review item with an `Accept pack version` button. Acceptance takes the same lock, replaces only seed fields, keeps personal fields, verifies the record, and removes that id from review. A dropped edited item stays in review for Claude to resolve.

The browser database API has no document version precondition. Migration uses the supported cooperative lease, fresh reads before field patches, and readback. Personal notes and completion never appear in replacement patches. A writer that changes seed fields without taking the lease during the final read/write interval cannot be excluded by this API; keep the board idle during the confirmed update and review any concurrent changes before completion.

Reset: while `meta/reset` exists the page never seeds and never claims, still renders the records it has, and shows one line in the Brief: "Reset in progress. Finish it in the Muster Out folder with /intake."

Watch: `/watch` writes `meta/watch` only after a check that passed every feed rule, and on a failed check writes `meta/watch_error` and leaves `meta/watch` as it was; the next good check deletes `meta/watch_error`. A check with `truncated: true` or any `body_available: false` has `confidence: "titles"`, and any "nothing matched" line from it says "by title". The Brief shows "Watch: checked <date>, <n> messages, <confidence label>", and when `meta/watch_error.at` is newer than `meta/watch.checkedAt`, "Last check failed <date>: <reason>. Showing the last good check."

Seed tags: every seed record carries `when`, a list of flags that must all hold for the record to be included: `resign`, `retire`, `eas`, `officer`, `enlisted`, `reserve`, `noreserve`, `sb`, `nosb`, `cat1`, `cat2`, `cat3`, `notretire`. The page computes the flags from the profile.

Leave projection: `asOf` includes all accrual and charges through that day. Project only later service days, count the union of charged dates, and stop at EAS for separations or the day before the retirement/transfer action date for retirements. The action date remains the anchor for action-based rules. An `asOf` after today or the last active-duty day suppresses the projection and shows a warning.

Optional `meta/ledger.sla`: absent or `null` means unknown; `0` or `{"days": 0, "expires": null}` confirms no special leave accrual. Otherwise use `{"days": <IPAC-confirmed protected excess, 0 to 60>, "expires": "YYYY-MM-DD"}`. `days` is the protected amount above the ordinary 60-day carryover cap, not a second balance. The confirmed expiration date comes from IPAC under the applicable SLA authority; the page never infers eligibility or retention from a deployment. On 30 September, after that day's accrual and charges, cap at `60 + days` while the protection remains valid, at most 120 total. Protection expiring on that boundary is no longer retained. When SLA is unknown and the balance crosses that boundary above 60, suppress exact projected balances and show an IPAC caution. Existing ledgers remain valid with this field absent. MCO 1050.3J chapter 2 paragraphs 2.a and 9 provide the ordinary cap, SLA eligibility, verification, limits, and differing retention periods.

Leave cancellation: legacy `cancel` means cancellation requested. Pending cancellation stays charged and keeps absence conflicts until the person selects `canceled in MOL`. The page migrates legacy statuses only when the live store can be edited and reset checks have finished, and continues charging leave with any unknown status.

## Build
`board/build_seed.py` writes `board/seed.json` and checks every rule target for every profile combination. `board/build_board.py` generates the released fingerprint map and injects it with the seed into `board/template.html` and writes `board/board.html`, the file that gets published. Both refuse to write if an em or en dash or a personal string appears.
