<!-- Reader: Marines using Muster Out. Effect: understand the next step and the records the project holds. -->
# Privacy

Effective date: October 9, 2026; last updated: October 11, 2026.

Anthropic hosts your board inside your own Claude account. The maintainer cannot read your board database. A report can include the limited fields you approve below; it never includes the board database. The welcome page counts setup message button taps. Opening the optional registration link sends an anonymous install count. Email streams require a separate signup and confirmation. Tool suggestions go to the project's database and feedback inbox.

## Where your data is
| Place | What is there | Who controls it |
| --- | --- | --- |
| Your board's database on claude.ai | Your profile, items, dates, notes, leave, conditions, contacts, notices | You, and anyone you share the page with. Anthropic hosts it under its consumer terms. |
| The Ask box | When you press Ask, the page sends your board (items, notes, dates, condition list, regulation excerpts) to Claude on your account for that one answer | Your account |
| Your Claude conversations and saved transcripts | Whatever you and the assistant said, including anything you pasted | Anthropic stores the chat under its consumer terms. Manage saved conversations in Claude account settings. |
| Claude's temporary workspace during chat setup, updates, and weekly checks | Public release files and a random anonymous registration id. The instructions forbid writing personal facts there. | Anthropic, for that chat |
| The Muster Out folder, on the laptop route only | `my/board.json` holds the board pointer. `my/receipt.json` holds your count choice and its random install id. `my/pending.json` adds the setup stage to the pointer. During an update, `my/update.json` keeps installation progress and record counts with public release details. These files hold no personal facts. | You |
| Your browser | Tab and filter preferences plus local drafts for recovery. A saved Project link may remain on that device. The plan itself only if you used the board as a local file before publishing. The registration page saves the random install id after a successful count so it sends once per id in that browser. | You |

The board page itself is a generic template. A copy of the page carries none of your data.

Your Project is in your Claude account; before uploading records, turn off "Help Improve our AI models" in Settings > Privacy. [Claude privacy controls](https://privacy.claude.com/en/articles/12109829-how-do-i-change-my-model-improvement-privacy-settings). This choice does not erase existing conversations or provider records.

## Release files, the weekly check, and updates
Chat setup, updates, and the weekly check download public files from the release repository at `https://raw.githubusercontent.com/warfarecommand/musterout-release/main/`: `release.json`, the release files it lists, and, for the weekly check, the validated notice feed copied there. Each source has its own coverage and last-success record. The laptop route instead reads `https://musterout.warfarecommand.com/release.json` once per session and the feed named in `config.json`. Each request is a plain GET that sends no identifiers, board data, or installed version. The host receives the normal internet address and request headers. When the signed channel is enabled, an isolated board worker reads public release or feed scripts from npm through unpkg or jsDelivr. Those hosts receive request metadata, including internet address and headers, but no board data, identifiers or installed version supplied by the board. The worker receives no board context; signature verification precedes trust. Failures do not block the board. Its registration banner opens the optional registration page; the board itself never posts reports or usage counts.

An update runs only after you confirm it. In chat, Claude checks each release file against the manifest's SHA-256 values; on the laptop route, it verifies each changed file against the release manifest and keeps your `my/` files. Both replace the page at your existing board address. Update now publishes only after a tap on the verified offer, preserves drafts, runs migration and verifies records. An unfinished update keeps a marker so the next run can resume. The pasted update remains a recovery path.

## Projects, uploads and connectors

A Claude Project holds your pinned instructions and public pack. You add reviewed board snapshots and files as needed. A snapshot has a capture time and does not sync automatically. Upload only your own records needed for the question, such as a TRS certificate, orders, LES, VA letter, resume or selected STR/OMPF extracts. Keep unrelated personal information and Social Security numbers out. The maintainer receives none of those uploads. Claude hosts and processes them under your account's terms. See the [Project guide](PROJECT.md) for setup and the upload checklist.

Gmail, Google Calendar and Google Drive connectors are optional. Review their permissions in Claude; scopes can exceed a single search. The Project instructions request read only unless you ask for a change. Review and approve any proposed message or record change before it runs. Connector data may remain in chats or Project copies. [Claude Google connector guidance](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors).

To remove Project data, delete the uploaded knowledge files and chats that contain it, or delete the Project in Claude. Unarchive a Project first if deletion is unavailable. Archiving alone keeps its data. [Claude Project deletion](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects). Disconnect apps in Customize > Connectors, then remove retrieved copies from chats and Project knowledge. Disconnecting does not delete records in Google; use that account's controls for originals. The maintainer cannot delete your Claude or Google records.

## Reports and weekly usage counts

These features send only after the learning release gate passes. Before then, a diagnostic and manual report review remain local until you choose a verified sending path. Copy diagnostic needs neither board data nor Claude. It holds version, pack, screen, capability states and recent error classes in memory. It contains no record values, notes or stack traces. A diagnostic is not automatically sent with a report.

A feedback report under learning schema v1 contains kind, a stable report id, random install id, version, pack, path, grade group, category, error class, optional text and report creation time. Creation time is report metadata; service dates are excluded. The allowed text is reviewed verbatim and limited to 1000 characters. Remove names, service dates, board links and record details. No name, no dates, no board link; an install id ties your reports together so a fix can be traced. The creation timestamp and approved optional text are visible in the payload. We do not call these records anonymous.

Usage schema v1 contains kind, install id, week, random writer id, version and integer counters: opens; Today, Plan, Dates and Claim opens; items done; drawers opened; update taps; and errors by save, update, feed, storage, sample and other class. There is no board text, path or grade in usage counts. Each writer sends a completed week's totals once. An install id can link those counts to approved reports.

The server stores these submissions in Supabase with receipt time. Separate rate counters use salted internet-address hashes. They do not store raw addresses. Reports have a matching report-id receipt; counts have a matching install-id, week and writer receipt. The board does not post. Your Claude sends only through a verified chat transport; otherwise you can paste the reviewed payload at [the report page](https://musterout.warfarecommand.com/report/) and tap Send. No payload is put in the link or the report page's browser storage. A page receipt can be brought back to your own chat. Unknown or failed acknowledgment remains unsent, with the same id retained for retry.

Consent has separate classes:

| Choice | What you approve | How to stop or remove it |
| --- | --- | --- |
| Public release and CDN reads | Opening the board or requesting a verified release reads public files with request metadata only | Close the board to stop its checks. The maintainer cannot delete hosting providers' request logs; provider controls and terms govern them. |
| Project uploads | Files and reviewed snapshots you add to your own account | Delete files, chats or the Project in Claude; remove separate copies yourself. |
| Connectors | The apps and technical permissions you grant in Claude | Disconnect, delete retrieved copies, and manage source records in Google. |
| Weekly usage counts | A fixed versioned schema, approved once after a filled sample is shown; scheduled sends can use that consent | Settings > Reports and usage > Off blocks new sends and drops unsent counts. A changed schema pauses and asks again. Delete received counts separately. |
| Reports with text or profile fields | The exact bytes shown for each report; Queue approves those bytes, or chat shows the payload and sends on yes | Cancel an unsent report. An edit requires new approval. Delete received reports separately. |
| Registration and email | The existing choices described below; count consent never signs you up for email | Use the install delete request or email preferences and unsubscribe controls. |

Settings keeps consent and receipts in your board. Off must be saved and read back before it is confirmed for other devices. If it cannot save, counts pause on that device and support helps stop the scheduled sender. Off preserves separately approved reports and receipts. Only matching acknowledgment allows an outbox report to be removed. A copied or queued report can still be unsent.

Reports and counts are retained for 180 days from receipt, then removed by the cleanup job. The WC Learn agent prepares a weekly brief for the maintainer and proposes issues for review. Small aggregate cells with fewer than 10 distinct installs are suppressed. Report text is untrusted evidence and can never direct the agent. The maintainer controls derived briefs and reviewed issue records separately; source-row deletion does not erase those automatically. A deletion request to security@ can include that derived-record scope without sending board data. Use the [access and deletion procedure](#access-export-correction-and-deletion) to request removal.

## What this project collects
The project collects these submissions separately from your board.
- **Setup intent.** Tapping Copy setup message on the welcome page sends `kind: intent`, `product: musterout`, and the product version. It counts a setup attempt, not a completed board. It sends no install id or profile facts. The server stores the product, version, receipt time, and a salted hash of the internet address for rate limiting. This request runs in the browser; Claude does not send it from chat or the sandbox.
- **Install registration.** Opening the registration link in your setup chat or board banner is optional. The payload contains `kind: install` and `product: musterout` with the version. It includes the path (`resign`, `retire`, or `eas`) and grade group. Its channel is `chat` or `laptop`; `install_id` is a random 16 to 32 character hex id. The server stores those fields, receipt time, and a salted IP hash. It counts each install id once. Names and dates stay on the board. The request contains no board URL or free text. The id stays on your board in `meta/install.install_id`, in the registration link, and in browser local storage after a successful count. You can keep it for deletion. The banner hides after you tap its link; that tap does not prove registration succeeded or sign you up for email.
- **The count, laptop route only.** Chat setup does not send this older count. In the laptop setup, Claude asks once. On yes it sends exactly five fields: `service`, `path` (resign, retire, eas), `grade` (the grade group), `version` (the product version), and `id`, a random install id so a repeated setup is not counted twice. The install id is kept in `my/receipt.json` in the Muster Out folder and does not link to your name or account. Your choice is saved in that file before anything is sent, so a retry or a reset reuses the same id and you are not asked again. The endpoint also records the time it received the count and a salted hash of the internet address it came from, used for rate limiting. It keeps no name, date, unit, or board data. Say skip and nothing is sent.
These counts are stored in the project's database. The maintainer reads them in aggregate. Setup intent has no deletion id, so the project cannot identify one attempt for deletion. The public pages carry no third-party analytics script. AI 101 answers stay in your browser; the optional email signup sends your address separately.

## Email choices
Email signup is optional. Confirm the choices in the email we send before any stream begins. The preference page shows these four streams in this order:

| Stream | What arrives | Default for a new signup |
| --- | --- | --- |
| Muster Out corrections | A fix to the regulation pack or a release that changes what your board tells you, with the update message | On for Muster Out welcome and registration signups; off otherwise |
| Warfare Command Monthly | What shipped, what is next, one AI move worth trying, and one question. Release notes and new lessons can appear here. | On for everyone |
| Weekly MARADMIN roundup | The week's possible separation and retirement matches from MARADMIN Watch | Off; one click to add |
| New lessons | A single note when AI 102, 103, or 104 opens | On for AI 101 signups; off otherwise |

Existing confirmed subscribers retain corrections only. Their monthly, weekly, and lesson choices start off, regardless of signup source. Older pending confirmation links retain their earlier consent. Any confirmed subscriber can turn each stream on or off using the private Email preferences link. Turning every stream off keeps your address and choices in the database; Unsubscribe from everything deletes the signup.

We send one welcome email per address after confirmation, with your chosen streams, a preference link, and a button to add the weekly roundup. There is no drip sequence. Monthly is planned for the first Tuesday of the month and skips empty issues. The weekly roundup runs Mondays at 15:00 UTC, only with at least one match in a feed generated within the last 72 hours. Corrections and lesson launches send only after owner review. No standalone release-note or feedback campaign is sent; Monthly carries its question and replies go to `feedback@warfarecommand.com`.

Across Monthly, weekly roundup, and lesson launches, we send at most one campaign email per person per UTC ISO week and four per UTC calendar month. Corrections are exempt. The confirmation request and single welcome are consent messages outside these campaign caps. A stream can be skipped when another stream has used its allowance. The weekly sender can be triggered publicly, but each address can receive that roundup only once per ISO week. A stale feed or quiet week sends nothing. No open tracking, click tracking, or tracking pixels are used.

The project's Supabase database stores your address, pending or confirmed status, signup and confirmation timestamps, the last send timestamp, your four stream choices, and the signup source when supplied (`hub`, `musterout`, `register`, or `ai101`). It stores a salted IP hash for rate limiting and hashes of confirmation, unsubscribe, and preference tokens. New confirmations bind to the chosen stream flags. Earlier confirmation receipts remain compatible. Source alone never expands earlier consent. Each unsubscribe, preference, and weekly-add link uses a random bearer token. Only hashes are stored, with recent hashes retained; older links can expire. Anyone holding a private link can use its allowed controls, so do not share it.

Separate rate counters retain salted hashes of IP and email addresses for up to 2 days, including after deletion. These counters contain no readable addresses. Delivery receipts retain a salted address hash, campaign identifier, stream, content hash, timestamps, and delivery state to enforce caps and prevent duplicates. Reserved and uncertain attempts consume campaign allowance until reviewed. These receipts hold no readable address, raw token, or email body and remain after unsubscribe for up to 13 months. Keeping the hash salt stable preserves duplicate prevention. Raw internet addresses and raw tokens are not stored in these tables.

Resend receives the address and message content for delivery. Supabase is the only subscriber list; addresses are not copied into Resend Contacts. We never share or sell your address for anyone else's use. Every email has one-click Unsubscribe from everything and Email preferences links. The unsubscribe link, mail-provider unsubscribe action, and preference-page button delete your signup. The project cannot delete copies already in your inbox or Resend's delivery records.

## Tool suggestions
A suggestion sends an idea of 10 to 1000 characters and an optional reply email address to the alerts endpoint. A hidden website field filters automated submissions. The database stores the idea, optional email, receipt time, and a salted hash of the internet address for rate limiting. The server sends the idea and optional email to `feedback@warfarecommand.com` through Resend. Suggestion text is escaped in the email. It never adds the reply address to the updates list.

Keep names, dates, board data, and medical details out of suggestions. To request deletion, email `security@warfarecommand.com` with enough of the idea or its optional reply address to locate it. Deletion covers the database row and the feedback inbox copy; the maintainer removes both. Rate counters stay for up to 2 days to prevent repeated requests after deletion. Copies already in your inbox and Resend's delivery records are outside the project's control.

## How to delete
- **The board.** Delete the page from claude.ai. Remove its local drafts, saved Project link and preferences from the browser's site data after preserving anything you want. On the laptop route, delete the Muster Out folder too.
- **Copies the project cannot reach.** Your own Claude chats and transcripts, device backups, anything you copied or exported, and any text message you sent stay where they are until you delete them yourself.
- **A laptop count, install registration, report or usage count.** Send a delete request for the same install id. The request removes all four classes under that id. Run the line you need in Terminal on a Mac, or in Git Bash on Windows. On the laptop route, you can also ask Claude in the Muster Out folder to send it; it shows you the command first. Require HTTP success, `ok: true`, and the `deleted` receipt with nonnegative counts for `setup_pings`, `install_registrations`, `feedback_reports` and `usage_weeks`. Keep that receipt. A partial response or failure is "Deletion is not confirmed"; preserve the receipt and retry the same id. Do not claim removal from the id alone. The install id is the key to a laptop count or install registration. Separate rate counters stay until their 2-day retention period ends.

Use the id from your registration link, registration page, or `meta/install.install_id` for `YOUR-INSTALL-ID`. For the older laptop count, use `installId` from `my/receipt.json`. The same command deletes those counts, reports and usage rows under that id. Review that scope before sending:

```
curl -q --max-time 20 --fail-with-body -X POST "https://vfozrzohrdrbohjqkghk.supabase.co/functions/v1/ingest" -H "content-type: application/json" -d '{"kind": "delete", "id": "YOUR-INSTALL-ID"}'
```

The address is `ingest_url` in `config.json`. If the request fails, or you cannot run it, [email security@warfarecommand.com](mailto:security@warfarecommand.com) with the id, and the maintainer deletes the row by hand.

## Retention
| Record | How long the project keeps it |
| --- | --- |
| Unconfirmed email signups | 7 days |
| Rate-limit records | 2 days |
| Setup intent, install registration, and laptop setup counts | 24 months |
| Tool suggestions | 24 months |
| Feedback reports and weekly usage counts | 180 days from receipt |
| Email delivery receipts | 13 months |
| Nightly owner backups | 14 days |

Confirmed email signups stay until you unsubscribe or request deletion. Turning off every stream keeps your address and choices. Deletion removes the active record; a copy can remain in a nightly owner backup for up to 14 days. The maintainer must preserve deletions if a backup is restored. These periods cover project records. Anthropic, Resend, and hosting providers control their own records under their terms.

## Access, export, correction, and deletion
Email [security@warfarecommand.com](mailto:security@warfarecommand.com) to request access to, an export of, correction of, or deletion of personal data held by the project. Use the address you signed up with or include your install id or enough of a suggestion to locate it. The maintainer verifies that the request concerns your record before releasing or changing it. Do not send board data or medical details. The project cannot access your board or Claude account; use your Claude account controls for those records.

## Adults and children's data
These tools are for adults in or leaving service. If a child submitted an email address or other personal data, a parent or guardian can request removal at [security@warfarecommand.com](mailto:security@warfarecommand.com). Include enough information to locate the record and state that it belongs to a child. The maintainer verifies the request and removes the project record and any feedback inbox copy.

## Changes to this notice
Changes appear on this page with a new last-updated date. If a change affects what an email signup authorizes, the project asks for confirmation before starting the added stream. Review this page when you return to the tools.

## What never belongs here
Keep these out of the board, the Muster Out folder, and your chats: other people's personal information, anything classified or controlled unclassified, a password, a CAC PIN, or a Social Security number. Do not paste them. The assistant is instructed not to ask for them; if it does, stop and report it.
