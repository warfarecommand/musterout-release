# Security

When you run Claude Code against this folder, the instructions in `CLAUDE.md` and `.claude/skills/` direct an agent on your machine with your Claude account. Instructions are not a permission boundary; Claude Code's own permission prompts are. We do not tell you to turn those off, and no step in this folder needs you to. [Report a security problem by email](mailto:security@warfarecommand.com).

## What the agent is asked to do
The instructions ask the agent to do these things and nothing else:
- Publish `board/board.html` to your Claude account once, and read and write its database.
- Read `config.json`, the regulation pack in `packs/`, and the three small files in `my/` (`board.json`, `pending.json`, `receipt.json`), and write those three files.
- Fetch the public regulation watch feed named in `config.json`, and public .mil and .gov pages you ask about.
- Send the one optional anonymous count, if you say yes.

Nothing here asks the agent to install software, read files outside this folder, or reach any other host. The only commands it may propose are `uuidgen`, to make the random install id, and, if you ask for it, the `curl` delete in `PRIVACY.md`. It says what each one does first. If Claude proposes any other command of that kind, say no and report it.

## Check a release before you unzip it
In the pilot, a release is a zip on the docs site, and each version gets its own file name at this address:

```
https://musterout.warfarecommand.com/dl/musterout-<version>.zip
```

The download page prints the SHA-256 of each zip. Check it before you unzip: `shasum -a 256 musterout-<version>.zip` on a Mac, `Get-FileHash musterout-<version>.zip` in PowerShell on Windows. If the two differ, do not use the file, and report it.

To install a new version, replace every file in your folder with the files from the new zip except the `my/` folder, which you keep exactly as it is. Then ask Claude to "update my board". It republishes the page to the same address, and your data stays. No git is needed.

## Pack review status
The pack keeps a local source copy for every citation, and a script, `packs/usmc/check_citations.py`, checks each quote against those copies. The copies are snapshots; open the official source for current wording. An independent model review checked every cited item against its source on 09 OCT 2026. Its corrections are in this release and were rechecked by a second review. No office has approved the pack; confirm what applies to you with IPAC, your TAP counselor, your VSO, and your command.

## Untrusted text
The assistant is instructed to treat regulations, MARADMINs, feed summaries, web pages, and board notes as data. If it follows an instruction found inside them, stop and report it.

## Watch feed
The weekly feed comes from a scheduled job in a separate repository. It fetches only the official MARADMIN feed and message pages. It classifies messages with an Anthropic API key, a Claude Code subscription token, or a keyword baseline; the model call has no tools and must return validated JSON. A separate step publishes the public feed and page. The job's GitHub write permission covers only its own repository. `/watch` checks each feed before it uses it: the file must parse, be no more than 8 days old, and state its window, its message count, and whether it was truncated or read titles only. A feed that fails a check leaves the last good check and your inbox unchanged; the board records only that the check failed and when.

## Submission endpoint
The optional count and the optional lesson results go to one edge function (`supabase/functions/ingest/index.ts`, address in `config.json` as `ingest_url` and `ping_url`). It validates the shape, caps sizes, rate limits by a salted hash of the address, and writes with a server side key that never reaches a browser. The tables are closed to every other role. It serves no reads. A `delete` with a study token removes that token's lesson rows, a `delete` with an install id removes that id's count, and a delete removes nothing else. `PRIVACY.md` gives both commands.

## Reporting
[Report a security problem by email](mailto:security@warfarecommand.com). Include the version from `config.json`, what you saw, and how to repeat it. Do not put your board data or anything personal in the report. During the pilot one maintainer reads these reports, and the expected response window is a week.
