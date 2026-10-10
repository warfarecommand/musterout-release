# Privacy

Anthropic hosts your board inside your own Claude account. The project receives no board data. The welcome page counts setup message button taps. Opening the optional registration link sends an anonymous install count. Correction alerts require a separate email signup and confirmation. Tool suggestions go to the project's database and feedback inbox.

## Where your data is
| Place | What is there | Who controls it |
| --- | --- | --- |
| Your board's database on claude.ai | Your profile, items, dates, notes, leave, conditions, contacts, notices | You, and anyone you share the page with. Anthropic hosts it under its consumer terms. |
| The Ask box | When you press Ask, the page sends your board (items, notes, dates, condition list, regulation excerpts) to Claude on your account for that one answer | Your account |
| Your Claude conversations and saved transcripts | Whatever you and the assistant said, including anything you pasted | You, through your Claude account settings, under Anthropic's retention rules |
| Claude's temporary workspace during chat setup, updates, and weekly checks | Public release files and a random anonymous registration id. The instructions forbid writing personal facts there. | Anthropic, for that chat |
| The Muster Out folder, on the laptop route only | `my/board.json` holds the board pointer. `my/receipt.json` holds your count choice and its random install id. `my/pending.json` adds the setup stage to the pointer. During an update, `my/update.json` keeps installation progress and record counts with public release details. These files hold no personal facts. | You |
| Your browser | Tab and filter preferences. The plan itself only if you used the board as a local file before publishing. The registration page saves the random install id after a successful count so it sends once per id in that browser. | You |

The board page itself is a generic template. A copy of the page carries none of your data.

Anthropic's privacy and training settings change, so this page does not restate them. Read them in your Claude account settings before you put medical detail on the board.

## Release files, the weekly check, and updates
Chat setup, updates, and the weekly check download public files from the release repository at `https://raw.githubusercontent.com/warfarecommand/musterout-release/main/`: `release.json`, the release files it lists, and, for the weekly check, the MARADMIN feed copied there. The laptop route instead reads `https://musterout.warfarecommand.com/release.json` once per session and the feed named in `config.json`. Each request is a plain GET that sends no identifiers, board data, or installed version. The host receives the normal internet address and request headers. The board page makes no release request. Its registration banner opens the optional registration page; the board itself sends no telemetry.

An update runs only after you confirm it. In chat, Claude checks each release file against the manifest's SHA-256 values; on the laptop route, it checks the zip from the docs site and keeps your `my/` files. Both replace the page at your existing board address. An unfinished update keeps a marker so the next run can resume.

## What this project collects
The project collects these submissions separately from your board.
- **Setup intent.** Tapping Copy setup message on the welcome page sends `kind: intent`, `product: musterout`, and the product version. It counts a setup attempt, not a completed board. It sends no install id or profile facts. The server stores the product, version, receipt time, and a salted hash of the internet address for rate limiting. This request runs in the browser; Claude does not send it from chat or the sandbox.
- **Install registration.** Opening the registration link in your setup chat or board banner is optional. The payload contains `kind: install` and `product: musterout` with the version. It includes the path (`resign`, `retire`, or `eas`) and grade group. Its channel is `chat` or `laptop`; `install_id` is a random 16 to 32 character hex id. The server stores those fields, receipt time, and a salted IP hash. It counts each install id once. Names and dates stay on the board. The request contains no board URL or free text. The id stays on your board in `meta/install.install_id`, in the registration link, and in browser local storage after a successful count. You can keep it for deletion. The banner hides after you tap its link; that tap does not prove registration succeeded or sign you up for email.
- **The count, laptop route only.** Chat setup does not send this older count. In the laptop setup, Claude asks once. On yes it sends exactly five fields: `service`, `path` (resign, retire, eas), `grade` (the grade group), `version` (the product version), and `id`, a random install id so a repeated setup is not counted twice. The install id is kept in `my/receipt.json` in the Muster Out folder and does not link to your name or account. Your choice is saved in that file before anything is sent, so a retry or a reset reuses the same id and you are not asked again. The endpoint also records the time it received the count and a salted hash of the internet address it came from, used for rate limiting. It keeps no name, date, unit, or board data. Say skip and nothing is sent.
- **The AI 101 result.** AI 101 works without sending anything. If you choose to send, the project receives exactly these fields: a random study token, your quiz score and your eight answers, your one sentence reflection, your yes or no on going deeper, the number of sections you completed, and the lesson version. The reflection goes as you typed it, with the spaces at the start and end removed, up to 600 characters; the server keeps the first 600 characters and drops the rest. With each result, the server stores the time it arrived and a salted hash of your internet address, used for rate limiting. The results form asks for no name, email, or date. The separate updates form asks for an email address. Your practice brief stays in this browser and is not included in results. Keep names, dates, and medical details out of the reflection.

These counts and lesson results are stored in the project's database. The maintainer reads them in aggregate. Setup intent has no deletion id, so the project cannot identify one attempt for deletion. The welcome page carries Cloudflare Web Analytics, a cookieless page counter that records no personal data. The lesson carries no analytics script at all.

## Updates and correction alerts by email
Email signup is optional. Platform signups on the Warfare Command hub and AI 101 are for Warfare Command updates: new tools, new lessons, Muster Out corrections, and release notes. Muster Out signups on the welcome and registration pages are for correction alerts and release notes. Confirm your address through the email we send; every email has an unsubscribe link. Existing subscribers keep their confirmed scope. A signup source alone does not establish broader consent. To change your scope, unsubscribe and sign up again from the appropriate form.

The project's Supabase database stores your email address, pending or confirmed status, signup and confirmation timestamps, the last email send timestamp, the signup source when supplied (`hub`, `musterout`, `register`, or `ai101`), and a salted hash of your internet address for rate limiting. It also stores hashes of confirmation and unsubscribe tokens. New platform confirmation links bind the token hash to the stated scope. After confirmation, that field retains a scope receipt for filtering platform emails. Older confirmed and pending signups keep correction alerts and release notes; their signup source does not expand consent. Separate rate counters use salted hashes of IP and email addresses to prevent repeated requests; they hold no readable email address and remain after an unsubscribe. Raw tokens and raw internet addresses are not stored in these tables.

Resend sends the emails and receives your address and the email content to deliver them. The project's database is the only subscriber list; addresses are not copied into a Resend contact list. We never share or sell your address for anyone else's use.

Every email includes a one-click unsubscribe that deletes your address from the project's database. The unsubscribe link in the email body does the same. The project cannot delete copies already delivered to your inbox or delivery records held by Resend.

## Tool suggestions
A suggestion sends an idea of 10 to 1000 characters and an optional reply email address to the alerts endpoint. A hidden website field filters automated submissions. The database stores the idea, optional email, receipt time, and a salted hash of the internet address for rate limiting. The server sends the idea and optional email to `feedback@warfarecommand.com` through Resend. Suggestion text is escaped in the email. It never adds the reply address to the updates list.

Keep names, dates, board data, and medical details out of suggestions. To request deletion, email `security@warfarecommand.com` with enough of the idea or its optional reply address to locate it. Deletion covers the database row and the feedback inbox copy; the maintainer removes both. Rate counters stay in the database to prevent repeated requests after deletion. Copies already in your inbox and Resend's delivery records are outside the project's control.

## How to delete
- **The board.** Delete the page from claude.ai. On the laptop route, delete the Muster Out folder too.
- **Copies the project cannot reach.** Your own Claude chats and transcripts, device backups, anything you copied or exported, and any text message you sent stay where they are until you delete them yourself.
- **A lesson result, laptop count, or install registration.** Send a delete request. Run the line you need in Terminal on a Mac, or in Git Bash on Windows. On the laptop route, you can also ask Claude in the Muster Out folder to send it; it shows you the command first. A reply of `{"ok":true}` means nothing remains under that key in the project's database. The study token is the only key to a lesson result, and the install id is the only key to a laptop count or install registration. Deletion does not reset rate counters.

Replace `YOUR-STUDY-TOKEN` with your lesson study token:

```
curl -X POST "https://vfozrzohrdrbohjqkghk.supabase.co/functions/v1/ingest" -H "content-type: application/json" -d '{"kind": "delete", "token": "YOUR-STUDY-TOKEN"}'
```

Use the id from your registration link, registration page, or `meta/install.install_id` for `YOUR-INSTALL-ID`. For the older laptop count, use `installId` from `my/receipt.json`. The same command deletes either count under that id:

```
curl -X POST "https://vfozrzohrdrbohjqkghk.supabase.co/functions/v1/ingest" -H "content-type: application/json" -d '{"kind": "delete", "id": "YOUR-INSTALL-ID"}'
```

The address is `ingest_url` in `config.json`. If either request fails, or you cannot run it, [email security@warfarecommand.com](mailto:security@warfarecommand.com) with the token or the id, and the maintainer deletes the row by hand.

## What never belongs here
Keep these out of the board, the Muster Out folder, and your chats: other people's personal information, anything classified or controlled unclassified, a password, a CAC PIN, or a Social Security number. Do not paste them. The assistant is instructed not to ask for them; if it does, stop and report it.
