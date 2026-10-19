---
name: board
description: Read and update the person's live Muster Out board. Use for any question about dates, status, what is due, adding or changing an item, leave blocks, conditions, contacts, or changing the EAS. Reads before it writes, cites the pack, pins every write.
---

# /board

The URL is in `my/board.json`; that file holds the URL, pack, version, and created date, and no profile. Every personal fact comes from the live board. The board is the source of truth; read it before you answer.

## Read
- Overview: ArtifactData `get` on `meta/profile`, `meta/settings`, `meta/ledger`, `meta/seeded`, `meta/reset`, `meta/watch`, then `list` on `items` (limit 200, follow every page). If `meta/reset` exists, a reset stopped partway; say so and send the person to `/intake` before you change anything.
- Resolve dates the way the page does: `date` as given; `eas` plus N days; `serviceEnd` projects EAS/resignation on the entered day, ordinary retirement on the preceding day, and an enlisted month-end retirement-path date on that day for FMCR, plus its day offset; `byPath` selects the rule for the live path; `easMonths` by calendar month (clamped to the last day when the month is shorter); `sb` from `meta/settings.sbStart` or `sbEnd`, and when that value is null the item has no date and shows "Date pending SkillBridge approval" (never use the EAS in its place); `item` uses the referenced item's `doneOn` if set and its `kind` is not `milestone`; otherwise resolve its `due`. Add N days, or N calendar months when the rule has `months`, to that base in either case. Resolve at most 5 levels deep. Milestone references always use the scheduled due date. Task/window completion can use `doneOn`; actual `va-file.doneOn` anchors the VA exam period. `biz: "prev"` pulls a Saturday or Sunday back to Friday and nothing else. A rule that points at an item with no date resolves to nothing. Items with no date sort after dated items.
- Late means: a task or milestone whose resolved due is before today; a window whose `to` is before today. Markers are never late. Items with status done or na are never late. An item with no resolved date belongs in "Needs a date".
- There are three kinds of date. Name them the same way everywhere:
  - **Rule deadline**: `basis: "rule"` or no `basis`. The date the cited text sets. It is counted from the person's date.
  - **Planning target**: `basis: "target"`. A date the pack picked inside a wider window the regulation allows. When you quote one, say what it is: "That is a planning target, not a deadline. The rule allows <window>." A target does not make an approval come faster and does not change any other item's rule.
  - **Confirmed event**: a date the person set after something happened or was approved. Record it with a `date` rule from orders or approval, or with `doneOn`.
- Deadlines counted from the entered date compute before approval. When profile.dateBasis is not approved, quote them as "From planned date" and say they move if the entered date moves. Actual approvals, orders and appointments stay undated until supplied. A fixed va-service-end date overrides its projection.
- Next: open items due in the next 14 days, critical first, then open windows that are open today, then critical items with no date.
- Read `blocks` for leave. Read `conditions` and `claim` for the claim. Contacts and sources use `contacts`, `links` and `inbox`.

## Seed records the page keeps
You read these; you never write them during a seed. The page writes them.
- `meta/seeding`, the claim while a seed runs. The page takes it, renews `claimedAt` every 30 seconds, and treats it as expired after two minutes.
```json
{"claimedAt": "2026-10-09T15:05:00Z", "by": "a8K3pq", "profileKey": "resign|o14|true|false|2027-09-01|null|null"}
```
- `meta/seeded`, the marker after a seed. `count` is the number of seeded items; `pack` is the pack version.
```json
{"at": "2026-10-09T15:06:10Z", "count": 74, "profileKey": "resign|o14|true|false|2027-09-01|null|null", "pack": "usmc-2026.10"}
```
- The page seeds only under the runtime's `acquire` lease on `meta/seeding`. A browser without it shows a lock message and does not seed; tell the person to open the board in a current browser or the Claude app. Never write the seed by hand.
- The profile key is `path|grade|reserve|sb|eas|sbStart|sbEnd` from `meta/profile` and `meta/settings`, joined with `|`, booleans as `true` or `false`, nulls as the string `null`.
- Mismatch rule: when `meta/seeded.profileKey` differs from the live key, the page does not reseed. It shows "Your path or dates changed since the plan was seeded. Run /intake reset to rebuild the plan, or Edit profile to keep this one." It still recomputes dates from the live settings. To keep the plan, pin the update of `meta/seeded.profileKey` to the live key. To rebuild it, `/intake` reset.
- A seed writes only ids that are absent. It never overwrites an item, line of effort, contact, or claim document that exists.

## Write
Every write to an existing document carries `if_version` from the read. Prefer one `batch` over many calls.
- Status: update `items/<id>` with `status` and, for done, `doneOn` in YYYY-MM-DD. Ask when it happened when another item's date depends on it; use today only if they say today. Statuses: open, doing, waiting, done, na.
- Notes: update `notes` on the item. Keep the person's words.
- New item: set `items/<id>` with every field: id, loe, order, kind, title, why, how, owner, due, window, basis, critical, presence, cite, verify, status, doneOn, notes and user. Use a kebab id with prefix `u-`. Kind is task, marker, window or milestone. Use lists for how and cite; each citation has ref, para, quote and url. Due is a rule; window is null or from and to rules. Basis defaults to `"rule"`; use `"target"` for a planning target. Start with status open, doneOn null, notes "" and user true. Cite the pack or set `verify`. A date the person sets from orders or an approval is a confirmed event: write it as a `date` rule and say so in `notes`.
- Change a date rule: set the whole item, or update with the old rule key as `{"__delete__": true}` in the same write. Update alone deep merges and leaves the old key, and the old key wins.
- Change the EAS: first list what stays put: items with a `date` rule and references anchored to a non-milestone item's `doneOn`. Milestone references follow the milestone's scheduled due rule even after confirmation is checked off. A fixed milestone date stays fixed; an EAS-based milestone moves with EAS; a SkillBridge milestone follows `sbStart` or `sbEnd`. Actual filing completion still anchors the VA exam period. Show the fixed dates and ask which should change too. Then update `meta/settings` `eas` with `if_version` from the read. Update `sbStart` and `sbEnd` if the SkillBridge period changes with it. In the same batch, update `meta/seeded.profileKey` to the new live key, because the person chose to keep this plan. The page recomputes every date counted from the EAS. If the date is now approved, update `meta/profile.dateBasis` to `"approved"`.
- Leave block: set `blocks/<id>` with id, start, end, status (approved, requested, known, planned, cancel), away (true if out of the area), kind (leave, liberty, ptad), note and updated.
- Condition: set `conditions/<id>` with `{id, name, status, code, side, limb, words, rule, todo, evidence, exam, note, record, src, updated}`. `status` is one of needs visit, in records, seen, in claim or rated. `limb` is null or one of LUE, RUE, LLE, RLE (the page's bilateral math reads it). `todo` and `evidence` are lists of strings; `record` is a list of `{date, entry, src}`; `src` is a list of `{label, url}` with https URLs only. Never write `est` or `scen`; the board does not estimate ratings.
- Claim documents, each with exactly these keys: `claim/where` `{rows: [{appt, where, home, base, how}], note}`; `claim/vso` `{rows: [{rank, name, why, phone, email}], script, note, updated}`; `claim/exposure` `{rows: [{location, hazards, presumptive, action}], notes: [string]}`; `claim/benefits` `{title, label, rows: [{what, detail}], note}`.
- Contact: update `contacts/<id>` name, phone, email, note.
- Profile: update `meta/profile`; changing path, grade, Reserve, or SkillBridge after seeding does not add or remove items, and it changes the profile key. Offer two choices: keep this plan (add or retire the affected items by hand, citing the pack, then update `meta/seeded.profileKey` to the live key) or `/intake` reset to rebuild it.

## Answering
Lead with the answer, then the rule and its paragraph, then who confirms it. Say which kind of date you are quoting. Label "Known facts", "Needs confirmation", "Draft for your review". Under 200 words unless they ask for more.

## Monday review
Run when asked or after /watch.
Late items, the next 14 days, open questions by who answers them, leave balance against the plan, and one recommended action. Offer to draft any email that action needs.

The primary chat path downloads the exact https://registry.npmjs.org/musterout/-/musterout-0.2.22.tgz with the model's own tools, reads package/verify.cjs or package/verify.py in memory, and checks the independently supplied SHA-256 pin before execution. Use stage-tarball VERSION TARBALL_PATH PRIVATE_PARENT; updates use stage-update-tarball TARGET CURRENT TARBALL_PATH PRIVATE_PARENT and confirmed-target recovery uses stage-resume-tarball VERSION TARBALL_PATH PRIVATE_PARENT with the public target on standard input. These offline commands require the publisher signature and every file hash, with optional dist integrity for transport only. For weekly checks, download feed.js from either fixed signed feed URL and use feed-file FEED_PATH with public now/pack/records JSON on standard input. Optional network mode honors HTTPS_PROXY or https_proxy using CONNECT and verified origin TLS, without redirects or ambient cookies.
