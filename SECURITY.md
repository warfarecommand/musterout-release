# Security

Claude follows the chat setup, weekly check, and update instructions. The laptop alternative uses `CLAUDE.md` and `.claude/skills/` on your machine. These instructions are not a permission boundary. Read Claude's permission prompts before you approve an action. No setup step asks you to turn those prompts off. [Report a security problem by email](mailto:security@warfarecommand.com).

## What the agent is asked to do
The instructions ask the agent to do these things and nothing else:
- Publish `board/board.html` to your Claude account once during setup, and read and write its database. An update replaces the page at the same address.
- Read verified public release files and the regulation pack. The laptop alternative also keeps its board pointer, setup progress, count choice, and update progress in `my/`.
- Fetch the public regulation watch feed named in `config.json`, and public .mil and .gov pages you ask about.
- Send the one optional anonymous count, if you say yes.

Chat setup and updates download public release files into a temporary workspace and check their hashes before publishing. Personal facts stay in the chat and the board. No instruction asks you to install software or give Claude your credentials.

## Check a release before you unzip it
In the pilot, a release is a zip on the docs site, and each version gets its own file name at this address:

```
https://musterout.warfarecommand.com/dl/musterout-<version>.zip
```

The download page prints the SHA-256 of each zip. Check it before you unzip: `shasum -a 256 musterout-<version>.zip` on a Mac, `Get-FileHash musterout-<version>.zip` in PowerShell on Windows. If the two differ, do not use the file, and report it.

To install a new version, send: "Update Muster Out. Read https://raw.githubusercontent.com/warfarecommand/musterout-release/main/UPDATE.md and follow it." Claude asks you to confirm, checks the files, and republishes the page at the same address with your data intact. Your `my/` files stay in place when you use the laptop alternative.

## Pack review status
The pack keeps a local source copy for every citation, and a script, `packs/usmc/check_citations.py`, checks each quote against those copies. The copies are snapshots; open the official source for current wording. An independent model review checked every cited item against its source on 09 OCT 2026. Its corrections are in this release and were rechecked by a second review. No office has approved the pack; confirm what applies to you with IPAC, your TAP counselor, your VSO, and your command.

## Untrusted text
The assistant is instructed to treat regulations, MARADMINs, feed summaries, web pages, and board notes as data. If it follows an instruction found inside them, stop and report it.

## Watch feed
The weekly feed comes from a scheduled job in a separate repository. It fetches only the official MARADMIN feed and message pages. It classifies messages with an Anthropic API key, a Claude subscription token, or a keyword baseline; the model call has no tools and must return validated JSON. A separate step publishes the public feed and page. The job's GitHub write permission covers only its own repository. The weekly check validates each feed before it uses it: the file must parse, be no more than 8 days old, and state its window, its message count, and whether it was truncated or read titles only. A feed that fails a check leaves the last good check and your inbox unchanged; the board records only that the check failed and when.

For notices, send: "Run the Muster Out weekly check. Read https://raw.githubusercontent.com/warfarecommand/musterout-release/main/WEEKLY.md and follow it." Your board shows both messages under Talk to Claude.

## Submission endpoint
The optional count and the optional lesson results go to one edge function (`supabase/functions/ingest/index.ts`, address in `config.json` as `ingest_url` and `ping_url`). It validates the shape, caps sizes, rate limits by a salted hash of the address, and writes with a server side key that never reaches a browser. The tables are closed to every other role. It serves no reads. A `delete` with a study token removes that token's lesson rows, a `delete` with an install id removes that id's count, and a delete removes nothing else. `PRIVACY.md` gives both commands.

## Reporting
[Report a security problem by email](mailto:security@warfarecommand.com). Include the version from `config.json`, what you saw, and how to repeat it. Do not put your board data or anything personal in the report. During the pilot one maintainer reads these reports, and the expected response window is a week.
