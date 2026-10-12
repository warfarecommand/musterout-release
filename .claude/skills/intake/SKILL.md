---
name: intake
description: Set up, resume, update, or reset a person's Muster Out board. Use when the person says "set me up", "/intake", "start over", "change my date", when my/board.json is missing, when my/pending.json exists, or when the live board has meta/reset. A short interview, then publish once, write the profile, verify, and hand off.
---

# /intake

Goal: a live board in the person's own Claude account in under ten minutes, with nothing invented, one board per person, and nothing declared done that was not checked.

## Which branch
Before the branch check, if `my/receipt.json` exists with `"consent": true` and `"sentAt": null`, run the send in step 7 once more with the same `installId`, then continue. This runs on every branch, including update and reset, and after the first real setup that follows a demo reset.

Check in this order and take the first that fits.
1. `my/pending.json` exists: a setup stopped partway. **Resume**, step 10. If its `url` is not null, the board exists at that URL; never publish again.
2. `my/board.json` exists and the live board has `meta/reset`: a reset stopped partway. **Reset**, step 9, from the first unfinished step.
3. `my/board.json` exists and the person wants a change (date, date basis, path, Reserve, SkillBridge, name, leave balance): **update**, step 8.
4. `my/board.json` exists and the person says start over, or wants demo data replaced with their own: **reset**, step 9.
5. Neither file exists: **new board**, steps 1 to 7.

## 1. Screen first
Ask the person to choose: resigning a regular commission, retiring, separating at EAS, or something else. Other paths include medical separation, involuntary separation, Guard or Reserve and another service. Something else means stop here: open `SUPPORT.md`, give the "who to call" line for their case, and do not build a board. Say plainly that the board would look complete and would be wrong for them.

Covered enlisted retirement means at least 20 years of creditable active service: FMCR transfer at 20 to 29 years or direct retirement at 30 or more. Ask whether they mean active service retirement or nonregular Reserve retirement if unclear. IPAC and MMSR-2 confirm eligibility and dates. E-6 and above can reach 20 under the published service limits; an E-1 to E-5 grade group requires a record review of prior active service or an approved exception. A grade group alone does not establish eligibility. The board includes the review item for each enlisted grade group and reuses transition, SBP and benefits items.

## 2. The three required answers
1. **Path**: `resign` (officer resigning a regular commission), `retire` (20 or more years, officer or enlisted), or `eas` (separating at the end of a contract). Ask what they intend, not what they qualify for; an officer with 20 years who means to resign is `resign`.
2. **Date**: the date they are planning to, in `YYYY-MM-DD`. If it is not approved yet, record it as a planning date (`dateBasis: "planned"`); if orders or an approval exist, `dateBasis: "approved"`. If they do not say, `dateBasis` is `null`. Ordinary officer and enlisted Retired List actions are effective on the 1st of a month. Enlisted FMCR transfer is on the last day of a month, with FMCR status starting on the next day (MCO 1900.16, 7007.1). Take the action date they have and tell them to confirm it and the separate last active-duty day with IPAC and MMSR-2. Never infer the action from the grade group. Explain that the plan computes every deadline from the entered date before approval. Dates counted from it say "From planned date" unless it is approved; they move when the date moves. The service-end milestone projects the path-specific last active-duty day; a fixed date the person sets overrides it. Never invent an approval, orders or appointment date.
3. **Grade group**: `o5` (O-5 and above), `o14` (O-1 to O-4), `cwo45`, `wo13`, `e89`, `e67`, `e15`.
If any answer is unknown, offer a demo board or a pause. Mark demo data on the page and replace it through step 9 when they have their answers.

## 3. The optional answers
Offer the list once: Reserve affiliation through DAP (`reserve` true or false), SkillBridge (`sb` true or false; start and end dates only if they have them), name as it should appear on the board, years of service, home town, duty station, a family note, leave balance and LES date. "Not sure" is false for now. Skipped is unknown: write `null`; never fill a date, a balance, or a SkillBridge period for them. If they want SkillBridge but have no dates, write `sb: true` with `sbStart` and `sbEnd` null and say the SkillBridge items will show "Date pending SkillBridge approval" until the dates exist. The page never uses the EAS in their place.

## 4. Confirm
Read the profile back in six lines and the three JSON documents below. Fix anything they correct.

## 5. Publish and write
Check Artifact `list` for "Muster Out" before publishing. Ask the person to confirm whether an existing board belongs to their interrupted setup. Reuse that confirmed URL and record `stage: "published"` in `my/pending.json`; no new publish is needed.

Publish `board/board.html` with the Artifact tool: title "Muster Out", icon "calendar", `capabilities: {"db": {}, "user": {}, "sample": {}}`. The person sees one permission prompt; tell them it is coming and what it means. If the publish is denied or fails without a URL, stop, write nothing to `my/`, and tell them what happened. The next run starts here again, after the same `list` check.

The moment the tool returns a URL, write `my/pending.json`. That URL is the only board URL from now on.
```json
{"url": "https://claude.ai/artifact/EXAMPLE", "pack": "usmc-2026.10", "version": "0.1.4", "created": "2026-10-09T15:00:00Z", "stage": "published"}
```
`pack` and `version` come from `config.json`. `created` is now in ISO 8601 UTC.

Write exactly these three documents with ArtifactData `batch` on that URL. The keys below are the document paths. Use JSON booleans, numbers and nulls for values. Do not store yes or no as words.
```json
{
  "meta/profile": {"name": "Capt A.B. Smith, USMC", "grade": "o14", "path": "resign", "reserve": true, "sb": false, "years": 9, "home": null, "base": null, "family": null, "demo": false, "dateBasis": "planned", "version": "0.1.4", "updated": "2026-10-09T15:00:00Z"},
  "meta/settings": {"eas": "2027-09-01", "sbStart": null, "sbEnd": null, "planSet": "2026-10-09"},
  "meta/ledger": {"balance": null, "asOf": null, "accrualPerMonth": 2.5, "note": null}
}
```
Use the version from `config.json`, today for `planSet`, and the current ISO 8601 UTC timestamp for `updated`. With SkillBridge dates: `"sb": true` in the profile and `"sbStart": "2027-06-03", "sbEnd": "2027-08-31"` in settings. With a leave balance: `"balance": 52.0, "asOf": "2026-09-30"`, using the LES month-end date for `asOf`.

Read all three back with ArtifactData `get` and compare field by field. After every field matches, set `stage` in `my/pending.json` to `"meta-written"` and continue.

If the batch fails twice, hand off to the page's own setup form: the person opens the URL and presses "Set up my board". The form uses the same nullable fields as this skill. Optional fields may be blank and are stored as `null`; it never invents a leave balance, an LES date, or SkillBridge dates, and a blank balance gives the ledger above. When they finish, read the three documents back, compare them with the answers they gave you, fix any field that differs with a pinned update, and set the stage to `"meta-written"`.

## 6. Open, seed, verify
Give the person the URL and ask them to open it in a browser signed in to the same Claude account (laptop first; then on the phone, claude.ai, same sign in). The page seeds itself from the profile on first open and says "Board ready".

Verify with ArtifactData:
- `get meta/seeded` exists.
- Its `profileKey` equals the live key: `path|grade|reserve|sb|eas|sbStart|sbEnd` from `meta/profile` and `meta/settings`, joined with `|`, booleans as `true` or `false`, nulls as the string `null`. Example: `resign|o14|true|false|2027-09-01|null|null`.
- `list items` (follow every page) returns a count of documents without `user: true` that equals `meta/seeded.count`.

If the page shows "Setting up your board" for more than two minutes, ask them to reload once. A seed claim expires after two minutes, and the next open resumes and writes only the records that are missing. Never write the seed by hand.

When all three checks pass, set `stage` in `my/pending.json` to `"seeded"`. Then write `my/board.json` and delete `my/pending.json`. The pointer holds exactly four fields and no profile:
```json
{"url": "https://claude.ai/artifact/EXAMPLE", "pack": "usmc-2026.10", "version": "0.1.4", "created": "2026-10-09T15:00:00Z"}
```

## 7. The count, then hand off
If `config.json` `ping_url` is null, say nothing about a count and skip to the hand off. If `meta/profile.demo` is true, do not ask yet; ask after a reset puts their own answers on the board.

An `askedAt` in `my/receipt.json` means the consent question is complete. If it says `consent: true` and `sentAt: null`, retry the send once with the same `installId` under that recorded consent.

Otherwise ask once: "One anonymous count goes to the project. It sends five fields: service, path, grade group, version, and a random install id so a repeated setup is not counted twice. Say skip to skip."

Before any request, write `my/receipt.json`:
```json
{"installId": "3f1c2a9e-8b7d-4e21-9a5c-0d6e4f7b8a12", "consent": true, "askedAt": "2026-10-09T15:20:00Z", "sentAt": null}
```
`installId` is a random UUID. Make it with `uuidgen` after saying it prints a random id and nothing else, or write one yourself. On skip, write the same file with `"consent": false` and send nothing.

On yes: `GET <ping_url>?kind=ping&service=usmc&path=<path>&grade=<grade>&version=<version>&id=<installId>`. Those five query fields are all that goes. Only when the response is a 2xx with `{"ok": true}`, set `sentAt` to now. On any other answer, leave `sentAt` null, tell the person it did not go, and say the next `/intake` will try once more with the same id.

Hand off: the three ways back are `/intake` (profile), `/board` (anything on the board), `/watch` (Mondays). `/watch` and new versions need this folder on a laptop; the board itself works on the phone. Then run `/board` once so the first real question gets answered.

## 8. Update
Read `my/board.json` for the URL. Ask what changed. Read `meta/profile`, `meta/settings`, and `meta/ledger` with ArtifactData, change only the fields that changed, and write them back pinned with `if_version`. A new leave balance goes to `meta/ledger` (`balance`, `asOf`). When an approval arrives, set `dateBasis` to `"approved"`; the date is now a confirmed event. Keep the URL; never publish a new page for an update.

A change to path, grade, Reserve, SkillBridge, the EAS, or the SkillBridge dates changes the profile key, and the page then says: "Your path or dates changed since the plan was seeded. Ask Claude to rebuild the plan, or Edit profile to keep this one." Tell the person before you write, and offer the two choices:
- Keep this plan. If the path, Reserve, or SkillBridge changed, list the items the change adds or retires (by `when` tag in `board/seed.json`) and offer to add or retire them one by one with cites. Then pin the update of `meta/seeded.profileKey` to the new live key. For a date change alone, this is the usual choice: dates counted from the EAS recompute, and fixed dates and dates hung on a done item stay.
- Rebuild the plan: step 9.

## 9. Reset
Reset keeps the same URL. Never publish a second board for a reset.

First run steps 1 to 4 for the new answers. Then say once, in plain words, what is lost: "This deletes every item, line of effort, contact, and claim document on your board. Every note and status you put on them goes too. Your existing leave blocks, conditions, links and notices stay at the same board address." If `meta/profile.demo` is true, add: "Say so if you also want the demo leave blocks, conditions, links, and notices cleared." Get one yes. Do not ask again at each step.

Then, in this exact order:
1. Write `meta/reset` with ArtifactData `set` and read it back. The page sees it and stops seeding and claiming; it shows "Reset in progress. Finish it in Claude."
```json
{"at": "2026-10-09T15:00:00Z", "token": "k7Q2m9Xa4p"}
```
`token` is 8 or more random letters and digits.
2. Delete `meta/seeded` and `meta/seeding` if they exist.
3. List `items`, `loes`, `contacts`, and `claim`, and delete every document in batches of 50. Pin each delete with `if_version`. Do the same for `blocks`, `conditions`, `links`, and `inbox` only if the person asked. List again; each cleared collection must be empty. Wait 10 seconds and list once more, because a write another open tab sent before it saw the marker can still land; delete anything that appeared.
4. Write the new `meta/profile`, `meta/settings`, and `meta/ledger` with `set` as whole documents shaped as in step 5. Pin each write with `if_version` from your read. Read all three back and compare field by field.
5. Delete `meta/reset`. Read it back; `get` must find nothing.
6. Tell the person to reload the same URL they already have. The page seeds the new plan.
7. Verify as in step 6: `meta/seeded` exists, its `profileKey` matches the new live key, and the count of items without `user: true` matches `meta/seeded.count`.

If anything fails in steps 1 to 5, leave `meta/reset` in place. The page stays parked, which is safe. The next run sees `meta/reset`, reads the live `meta/profile` and `meta/settings`, and asks the person to confirm the new answers again in one message (the marker holds only `at` and `token`, so the answers live in the conversation and nowhere else). Then it repeats the clearing and the readbacks from step 2 before it releases the marker; every delete and set above is safe to repeat. Keep `my/board.json` as it is, except `version` if a new version was installed. Keep `my/receipt.json` and its `installId`; do not ask the count again, and do not send again when `sentAt` is set.

## 10. Resume
Read `my/pending.json` and act on its `stage`. Resume at the existing URL when one is recorded.
- `"published"`: the page exists; the three meta documents may be missing or partial. Read them. If the answers from the earlier conversation are gone, ask steps 2 and 3 again, using what is on the board as the starting point, and confirm per step 4. Write what is missing or wrong, read back, and set the stage to `"meta-written"`.
- `"meta-written"`: the three documents match the confirmed answers. Go to step 6.
- `"seeded"`: the seed was verified. Write `my/board.json`, delete `my/pending.json`, and go to step 7.
- `url` is null: no publish ever returned a URL. Run the `list` check in step 5 before you publish anything.

## Never
The page owns item writes during setup; skipped values stay empty. Tell the person the board is ready only after step 6 passes. Keep one board per person and keep profile facts, leave balances, medical details and family notes out of `my/`.
