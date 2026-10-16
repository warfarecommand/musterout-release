---
name: intake
description: Set up, resume, update, or reset a person's Muster Out board. Use when the person says "set me up", "/intake", "start over", "change my date", when my/board.json is missing, when my/pending.json exists, or when the live board has meta/reset. Routes installation through verified SETUP.md and preserves the existing board address.
---

# /intake

New and resumed installations use the same verified SETUP.md contract as chat setup. Never use an older optional ping, URL-query sender, or my/receipt.json as approval or evidence of registration. Keep existing receipt files as historical state only; do not send them.

## Which branch
1. Read my/board.json and my/pending.json for an existing URL. Confirm that URL with Artifact list/get, following every page. A failed read is not a missing board. Preserve the same address and all sharing settings. Never publish a second board to recover a failure.
2. For a new board, or any pending install, load SETUP.md from the same verified release as this folder. Authenticate the full signed exact-version package with the independently pinned verifier, then use its verified SETUP.md and dependency set. An unchecked clone or raw release.json cannot authorize setup. If verification or required tools fail, stop writes and explain the missing check; the existing plan stays usable.
3. Follow SETUP.md in full before any new publish or installation write: explicit count agreement Yes/No, licenseAcknowledgmentRequired OFF/ON contract and separate unchecked legal acknowledgment when ON, required coarse base, and actual owner-only capability-rule readback. No stops before publishing. Missing or stale agreement is not assent. New HTML is published once; resumed HTML is updated only at its known URL.
4. For a completed board without TEL1 rules, run SETUP.md, Existing-board enrollment, at the same URL before enabling counts. Do not recreate meta/setup. Ordinary profile changes use section 8 below; a reset uses section 9. The seven owner-only prefixes must be read back before private count state is written.
5. SETUP.md controls local completion and registration: the locally verified dated or undated plan opens immediately under RULINGS Amendment A1. Registration stays pending with a persistent browser retry; usage drafts queue locally. Only a signed matching receipt confirms registration. No sandbox POST or GET count sender is authorized.
6. After local plan verification, read meta/install and write my/board.json with exactly url, pack, version, created from verified installation metadata. Preserve original values and the same address. Delete my/pending.json only after pointer readback and successful local completion. A pending server receipt does not delay first value. Offer the one-time optional recommend score with Skip. Email remains separately optional, blank and double opt-in.

## 8. Update
Read `my/board.json` for the URL. Ask what changed. Read `meta/profile`, `meta/settings`, and `meta/ledger` with ArtifactData, change only the fields that changed, and write them back pinned with `if_version`. A new leave balance goes to `meta/ledger` (`balance`, `asOf`). When an approval arrives, set `dateBasis` to `"approved"`; the date is now a confirmed event. Keep the URL; never publish a new page for an update.

A change to path, grade, Reserve, SkillBridge, the EAS, or the SkillBridge dates changes the profile key, and the page then says: "Your path or dates changed since the plan was seeded. Ask Claude to rebuild the plan, or Edit profile to keep this one." Tell the person before you write, and offer the two choices:
- Keep this plan. If the path, Reserve, or SkillBridge changed, list the items the change adds or retires (by `when` tag in `board/seed.json`) and offer to add or retire them one by one with cites. Then pin the update of `meta/seeded.profileKey` to the new live key. For a date change alone, this is the usual choice: dates counted from the EAS recompute, and fixed dates and dates hung on a done item stay.
- Rebuild the plan: step 9.

## 9. Reset
Reset keeps the same URL. Never publish a second board for a reset.

First use the existing board intake cards for the new answers, following verified SETUP.md. Do not publish a new board. Preserve the count agreement, private rule contract, and legal acknowledgment rules. Then say once, in plain words, what is lost: "This deletes every item, line of effort, contact, and claim document on your board. Every note and status you put on them goes too. Your existing leave blocks, conditions, links and notices stay at the same board address." If `meta/profile.demo` is true, add: "Say so if you also want the demo leave blocks, conditions, links, and notices cleared." Get one yes. Do not ask again at each step.

Then, in this exact order:
1. Write `meta/reset` with ArtifactData `set` and read it back. The page sees it and stops seeding and claiming; it shows "Reset in progress. Finish it in Claude."
```json
{"at": "2026-10-09T15:00:00Z", "token": "k7Q2m9Xa4p"}
```
`token` is 8 or more random letters and digits.
2. Delete `meta/seeded` and `meta/seeding` if they exist.
3. List `items`, `loes`, `contacts`, and `claim`, and delete every document in batches of 50. Pin each delete with `if_version`. Do the same for `blocks`, `conditions`, `links`, and `inbox` only if the person asked. List again; each cleared collection must be empty. Wait 10 seconds and list once more, because a write another open tab sent before it saw the marker can still land; delete anything that appeared.
4. Write the new `meta/profile`, `meta/settings`, and `meta/ledger` with `set` as whole documents shaped as in SETUP.md step 7. Pin each write with `if_version` from your read. Read all three back and compare field by field.
5. Delete `meta/reset`. Read it back; `get` must find nothing.
6. Tell the person to reload the same URL they already have. The page seeds the new plan.
7. Verify as in SETUP.md step 8: `meta/seeded` exists, its `profileKey` matches the new live key, and the count of items without `user: true` matches `meta/seeded.count`.

If anything fails in steps 1 to 5, leave `meta/reset` in place. The page stays parked, which is safe. The next run sees `meta/reset`, reads the live `meta/profile` and `meta/settings`, and asks the person to confirm the new answers again in one message (the marker holds only `at` and `token`, so the answers live in the conversation and nowhere else). Then it repeats the clearing and the readbacks from step 2 before it releases the marker; every delete and set above is safe to repeat. Keep `my/board.json` as it is, except `version` if a new version was installed. Keep historical receipt files unchanged. They are not count agreement or verified telemetry receipts. New counts follow the current explicit consent and browser handoff contract.
