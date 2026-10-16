# Muster Out

A personal separation and retirement planner for Marines. It shows what is due next for your separation and the regulation text each task cites.

Your board lives in your own Claude account, and Anthropic hosts it under your login. The maintainers have no account on it, and this build sends them nothing from it. Each cited item carries its quoted source text. Every citation has a local source copy in the pack, and a script checks each quote against it; those copies are snapshots, so open the official source for current wording. The board also models your leave, keeps a claim tab for the VA timeline and evidence, and answers questions from your board through an Ask box.

The page shows three kinds of date and labels each one:
- A **rule deadline** is a date or window the cited text requires. It may depend on your separation date or on another event.
- A **planning target** is a date selected for planning, and the board marks it as a target. Any window a regulation sets still governs it.
- A **confirmed event** is a date you set after an approval or a booking.

Pilot. Marine Corps only for now. Paths covered: resigning a regular commission, retiring, separating at EAS; officer and enlisted; Reserve affiliation and SkillBridge as options. Enlisted retirement covers FMCR transfer with 20 to 29 years of active service and direct retirement with 30 or more. The reporting unit submits to MMSR-2 through unit diary; IPAC confirms eligibility and dates. `SUPPORT.md` lists covered paths and the offices for paths outside the pack.

## Set up in one message
Muster Out works on Claude Free. Claude Pro at $20 a month gives more room for long coach chats. Send this message in a Claude chat that can run the security check: the Claude app on a phone, claude.ai, or the desktop app, including Claude Code and the desktop Code tab.

```text
Set up Muster Out for me. Check https://cdn.jsdelivr.net/npm/musterout@0.2.14/verify.cjs (SHA-256 540dbd2d782e85a62d3d51e3d8000c57f2809999c3b6eb3c4f9ab3d35f75ce88) and https://cdn.jsdelivr.net/npm/musterout@0.2.14/verify.py (SHA-256 968eecc40477d527a6bcffd96ae25f451dafad8594f1fc83ce0b3482a8d3e512). Download https://registry.npmjs.org/musterout/-/musterout-0.2.14.tgz with your own tools, read package/verify.cjs or package/verify.py in memory, and check the same SHA-256 pin before running stage-tarball. Then follow the setup guide they verify.
```

Claude authenticates the publisher signature and exact board and guide bytes with the independently pinned verifier. If the chat cannot run the security check, setup stops before publishing. Existing boards keep working. It asks you to tap Publish for your private board, then gives you the board link. Open it and answer a few questions there: path, date, and grade group. Every other answer is optional, and the board builds your plan from them. Setup takes about 5 minutes in a Claude chat on a phone or computer. If the phone app cannot open the board, use claude.ai in your phone browser.

The 20 minute lesson is optional background for anyone new to AI. Take it before or after setup.

## Developer folder installs
Developers can clone [the public release repository](https://github.com/warfarecommand/musterout-release). Folder updates authenticate the signed install manifest and exact-version package, keep `my/`, and republish at the existing board address. Everyone can use the setup message above in Claude Code or the desktop Code tab.

## What it costs and what it sends
Muster Out costs nothing beyond the Claude plan. At the end of setup, Claude offers a link that registers your board anonymously so the maintainer knows how many boards exist. Opening it sends path, grade group, version, and a random install id so a repeated setup is not counted twice. Nothing is sent unless you open it. Your board, your dates, and anything medical stay in your Claude account. `PRIVACY.md` lists the submission fields and how to delete them.

## How to keep it current
Your board shows both messages below under Talk to Claude, each with a Copy button.
- **Your date moved.** Use Edit profile on the board, or tell Claude what changed. Dates counted from your date recompute. Review fixed dates yourself.
- **The weekly check.** During setup, Claude offers a Monday check when the chat can schedule one. The check files possible MARADMIN matches for your path and the lines of effort on your board. It also checks for new versions. VA and DoD changes are outside the feed. If only titles were read, it says "by title". To run it yourself, send:

  ```text
  Run the Muster Out weekly check. Use the signed feed. Check https://cdn.jsdelivr.net/npm/musterout@0.2.14/verify.cjs (SHA-256 540dbd2d782e85a62d3d51e3d8000c57f2809999c3b6eb3c4f9ab3d35f75ce88) and https://cdn.jsdelivr.net/npm/musterout@0.2.14/verify.py (SHA-256 968eecc40477d527a6bcffd96ae25f451dafad8594f1fc83ce0b3482a8d3e512). Download https://registry.npmjs.org/musterout/-/musterout-0.2.14.tgz with your own tools, read package/verify.cjs or package/verify.py in memory, and check the same SHA-256 pin before running stage-tarball. Then follow the weekly guide they verify.
  ```
- **A new version.** When a weekly check finds a newer version and records the notice, the board shows this message. Paste it into any Claude chat. Claude shows the release changes, asks you to confirm, verifies the files, and republishes at the same board address with your data intact.

  ```text
  Update Muster Out. Keep my existing board at the same address. Check https://cdn.jsdelivr.net/npm/musterout@0.2.14/verify.cjs (SHA-256 540dbd2d782e85a62d3d51e3d8000c57f2809999c3b6eb3c4f9ab3d35f75ce88) and https://cdn.jsdelivr.net/npm/musterout@0.2.14/verify.py (SHA-256 968eecc40477d527a6bcffd96ae25f451dafad8594f1fc83ce0b3482a8d3e512). Download https://registry.npmjs.org/musterout/-/musterout-0.2.14.tgz with your own tools, read package/verify.cjs or package/verify.py in memory, and check the same SHA-256 pin before running stage-tarball. Then follow the update guide they verify.
  ```

## How to delete
Delete the artifact from its claude.ai page menu. If you cloned a folder install, delete the Muster Out folder too. That removes the board and its database from your account. Three things remain: your own chat history with Claude, which you control in your Claude settings; anything you copied or exported; and the anonymous count or lesson result, if you sent one. `PRIVACY.md` says how to have the count or a lesson result deleted.

## Not advice
Muster Out cites regulations and tracks dates. It is not legal, financial, or medical advice, and it does not predict VA ratings. IPAC, your TAP counselor, your VSO, and your command decide what applies to you; confirm with them before you act.

Warfare Command publishes Muster Out under the MIT license, and the docs are at musterout.warfarecommand.com. To contribute, read `CONTRIBUTING.md`.
