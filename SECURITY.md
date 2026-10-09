# Security

Muster Out installs from a public, release-only repository, [github.com/warfarecommand/musterout-release](https://github.com/warfarecommand/musterout-release). In a chat, before Claude publishes or replaces your board, it checks every release file against the SHA-256 values in that repository's manifest and stops on any mismatch. The instructions Claude follows are not a permission boundary; Claude's permission prompts are. Read each prompt before you approve an action. No setup step asks you to turn those prompts off. [Report a security problem by email](mailto:security@warfarecommand.com).

## The release repository
Development happens in a separate private repository. Each release is published to the public release repository, which holds the release files only. In a chat, Claude follows `SETUP.md`, `UPDATE.md`, and `WEEKLY.md` from it. `release.json`, the manifest, lists every release file with its SHA-256 value.

One file changes between releases: `feed/latest.json`, the weekly MARADMIN feed. A scheduled job copies it from the public watch site each Monday after checking its shape. It sits outside the manifest's hash list, and the instructions treat it as data that Claude never runs.

## The check before Claude publishes your board
Chat setup and updates follow these steps:
- **Fetch.** Claude reads `release.json` with a plain GET that sends no identifiers, into a fresh temporary workspace, and rejects a manifest with unsafe paths or missing fields.
- **Verify.** Claude downloads every file the manifest lists and compares each file's SHA-256 with the manifest value. A missing file, a failed download, or a mismatch stops the run before anything is published or written to your board. The instructions forbid running downloaded code.
- **Publish.** After you tap Publish, Claude publishes the verified board page unchanged. An update waits for your yes, then republishes the page at the same address with your data intact.

A matching hash is not a signature. It proves the files are the ones the manifest lists. Personal facts stay in your chat and on your board, and the instructions forbid writing them to the temporary workspace. No instruction asks you to install software or give Claude your credentials.

To update, copy the message from Talk to Claude on your board and paste it into any Claude chat:

```
Update Muster Out. Read https://raw.githubusercontent.com/warfarecommand/musterout-release/main/UPDATE.md and follow it.
```

## What Claude is asked to do
The setup, update, and weekly instructions cover these actions:
- Publish `board/board.html` to your Claude account once during setup, and read and write its database. An update replaces the page at the same address.
- Read the verified release files and the regulation pack. On the laptop route, write `my/board.json`, `my/pending.json`, `my/receipt.json`, and `my/update.json`, which hold the board address, the setup stage, your count choice, and update progress, and no personal facts.
- Fetch the weekly MARADMIN feed: the copy in the release repository in chat, or the feed named in `config.json` on the laptop route. Fetch public .mil and .gov pages you ask about.
- On the laptop route only, send the one optional anonymous count, if you say yes.
- Offer a recurring Monday check if the chat supports it. Confirm your timezone and time and obtain any schedule approval before creating the task. If recurring tasks are unavailable, give you the weekly message to send yourself.

## Laptop route: check the zip before you unzip it
On the laptop route, a release is a zip on the docs site, and each version gets its own file name at this address:

```
https://musterout.warfarecommand.com/dl/musterout-<version>.zip
```

The download page prints the SHA-256 of each zip. Check it before you unzip: `shasum -a 256 musterout-<version>.zip` on a Mac, `Get-FileHash musterout-<version>.zip` in PowerShell on Windows. If the two differ, do not use the file, and report it. An update on this route keeps your `my/` files in place.

## Pack review status
The pack keeps a local source copy for every citation, and a script, `packs/usmc/check_citations.py`, checks each quote against those copies. The copies are snapshots; open the official source for current wording. An independent model review checked every cited item against its source on 09 OCT 2026. Its corrections are in this release and were rechecked by a second review. No office has approved the pack; confirm what applies to you with IPAC, your TAP counselor, your VSO, and your command.

## Untrusted text
The assistant is instructed to treat regulations, MARADMINs, feed summaries, release notes, web pages, and board notes as data. If it follows an instruction found inside them, stop and report it.

## Watch feed
The weekly feed comes from a scheduled job in a separate repository. It fetches only the official MARADMIN feed and message pages. It classifies messages with an Anthropic API key, a Claude subscription token, or a keyword baseline; the model call has no tools and must return validated JSON. A separate step publishes the public feed and page. The job's GitHub write permission covers only its own repository. The weekly check validates each feed before it uses it: the file must parse, be no more than 8 days old, and state its window, its message count, and whether it was truncated or read titles only. A feed that fails a check leaves the last good check and your inbox unchanged; the board records only that the check failed and when.

## Submission endpoint
The optional count and the optional lesson results go to one edge function (`supabase/functions/ingest/index.ts`, address in `config.json` as `ingest_url` and `ping_url`). It validates the shape, caps sizes, rate limits by a salted hash of the address, and writes with a server side key that never reaches a browser. The tables are closed to every other role. It serves no reads. A `delete` with a study token removes that token's lesson rows, a `delete` with an install id removes that id's count, and a delete removes nothing else. `PRIVACY.md` gives both commands.

## Correction alerts
Website signups go to the separate `alerts` edge function. The service role alone can access `alert_signups`; the table has row level security and no client policies. It stores email addresses, consent status, timestamps, salted IP hashes, and token hashes. The existing service-only rate table holds separate salted IP and email hash counters for subscribe requests and confirmation sends. Deletion does not reset either rate limit.

The function accepts signups from the website origin only, checks a honeypot and the email format, and limits subscribe requests to three per hashed IP per hour and confirmation emails to one per address per ten minutes. Confirmation and unsubscribe tokens contain 32 random bytes; only their SHA-256 hashes are stored. A used confirmation link cannot confirm again. GET and one-click POST unsubscribe delete the matching row. The last eight unsubscribe token hashes are retained so links from recent emails remain valid.

Resend receives addresses only for delivery, with a sending-only key. It holds no synced contact list. The owner sends correction alerts by hand to confirmed addresses; the send script defaults to a count-only dry run. See `PRIVACY.md` for the stored fields and how to delete a signup.

## Reporting
[Report a security problem by email](mailto:security@warfarecommand.com). Include the version from `config.json`, what you saw, and how to repeat it. Do not put your board data or anything personal in the report. During the pilot one maintainer reads these reports, and the expected response window is a week.
