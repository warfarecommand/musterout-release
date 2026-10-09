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
| `meta/ledger` | balance, asOf, accrualPerMonth, note. With no balance: `{"balance": null, "asOf": null, "accrualPerMonth": 2.5, "note": null}`, and the Leave tab shows its empty state |
| `meta/seeding` | claimedAt, by, profileKey (the claim while a seed runs; renewed every 30 seconds, expired after 2 minutes) |
| `meta/seeded` | at, count, profileKey, pack. Boards seeded before 09 Oct 2026 have no `profileKey`; the page shows no mismatch line for them, and the key is attached only when the person makes an explicit keep or reset choice. It records acceptance of the retained plan, not the original seed profile. |
| `meta/reset` | at, token (present only while a reset runs) |
| `meta/watch` | checkedAt, feedGeneratedAt, window {from, to}, checkedCount, truncated, bodyAvailable, confidence (full, titles), matches[{id, title, date, why, url}], status (ok) |
| `meta/watch_error` | at, reason (present only when the newest check failed) |
| `loes/<id>` | id, n, name, lead, purpose |
| `items/<id>` | id, loe, order, kind (task, marker, window, milestone), title, why, how[], owner, due (rule or null), window ({from, to} rules or null), basis (optional: rule or target; absent means rule), critical, presence, cite[{ref, para, quote, url}], verify, status (open, doing, waiting, done, na), doneOn, notes, user, updated |
| `contacts/<id>` | id, name, role, org, phone, email, loe, note |
| `blocks/<id>` | id, start, end, status (approved, requested, known, planned, cancel), away, kind (leave, liberty, ptad), note, updated |
| `conditions/<id>` | id, name, status (needs visit, in records, seen, in claim, rated), code, side, limb (null, LUE, RUE, LLE, RLE), words, rule, todo[], evidence[], exam, note, record[{date, entry, src}], src[{label, url}], updated |
| `claim/where` | rows[{appt, where, home, base, how}], note |
| `claim/vso` | rows[{rank, name, why, phone, email}], script, note, updated |
| `claim/exposure` | rows[{location, hazards, presumptive, action}], notes[] |
| `claim/benefits` | title, label, rows[{what, detail}], note |
| `links/<id>` | id, title, url, loe, added |
| `inbox/<id>` | id, number, title, url, date, note, keys[], action, deadline, confidence, body_available, status (new, dismissed), filed |

Date rules: `{"date": "YYYY-MM-DD"}`, `{"eas": n}`, `{"easMonths": n}`, `{"sb": "start"|"end"}`, `{"item": "<id>", "days": n}`, with optional `"biz": "prev"` to pull a weekend date back to Friday. The seed uses `{"date": "SETUP"}` for "the day the board was set up". An `sb` rule with a null `sbStart` or `sbEnd` resolves to no date; the date column shows "Date pending SkillBridge approval" and the item sorts after dated items.

Three kinds of date, named the same in the page, the docs, and the skills: a rule deadline (`basis` absent or `"rule"`), the date the cited text sets; a planning target (`basis: "target"`), a date the pack picked inside a wider window, which is a plan and not a deadline; and a confirmed event, a date the person set after an approval or a booking, or a `doneOn`.

Profile key: `path|grade|reserve|sb|eas|sbStart|sbEnd` from `meta/profile` and `meta/settings`, joined with `|`, booleans as `true` or `false`, nulls as the string `null`.

Seeding: the page seeds when it opens with a profile, no `meta/seeded`, and no `meta/reset`. It takes `meta/seeding` with the runtime's `acquire` lease (holder is the tab's seed id, 45 second lease, renewed every 30 seconds); a browser without `acquire` does not seed and says so. A busy or rejected renewal aborts the seed at once. Before each seed write it reads that document fresh and skips it if it exists, so it never overwrites an item, line of effort, contact, or claim document, whoever wrote it. Before writing `meta/seeded` it reads `meta/profile` and `meta/settings` fresh and aborts without the marker if the key changed; the page then shows "Your profile changed while the board was being set up. Run /intake reset in the Muster Out folder to rebuild the plan." While `meta/reset` exists the page refuses every write, closes any open edit form, drops its cached records from the view, and stops claim renewal; when the marker clears it re reads the meta documents fresh before deciding to seed. If `meta/seeded.profileKey` differs from the live key, the page does not reseed; it shows "Your path or dates changed since the plan was seeded. Run /intake reset to rebuild the plan, or Edit profile to keep this one." and still recomputes dates from the live settings.

Reset: while `meta/reset` exists the page never seeds and never claims, still renders the records it has, and shows one line in the Brief: "Reset in progress. Finish it in the Muster Out folder with /intake."

Watch: `/watch` writes `meta/watch` only after a check that passed every feed rule, and on a failed check writes `meta/watch_error` and leaves `meta/watch` as it was; the next good check deletes `meta/watch_error`. A check with `truncated: true` or any `body_available: false` has `confidence: "titles"`, and any "nothing matched" line from it says "by title". The Brief shows "Watch: checked <date>, <n> messages, <confidence label>", and when `meta/watch_error.at` is newer than `meta/watch.checkedAt`, "Last check failed <date>: <reason>. Showing the last good check."

Seed tags: every seed record carries `when`, a list of flags that must all hold for the record to be included: `resign`, `retire`, `eas`, `officer`, `enlisted`, `reserve`, `noreserve`, `sb`, `nosb`, `cat1`, `cat2`, `cat3`, `notretire`. The page computes the flags from the profile.

## Build
`board/build_seed.py` writes `board/seed.json` and checks every rule target for every profile combination. `board/build_board.py` injects the seed into `board/template.html` and writes `board/board.html`, the file that gets published. Both refuse to write if an em or en dash or a personal string appears.
