<!-- Reader: Marines using Muster Out. Effect: understand counts, control, and deletion. -->
# Privacy

Updated 25 OCT 2026.

## Registration and usage by board version

New personally owned boards initialized with registration v3 show the plan first, then ask for a registration agreement on the board. Declining or a failed send leaves the plan usable. The browser registration page sends the count; the board does not POST it. Registration links use a query parameter containing the disclosed count fields and board key. Hosting providers and browser or app link handling can see that initial address. The receiver clears the query and fragment before parsing. A no-referrer policy cannot hide the initial address from the host. Existing fragment links and deletion fragments remain supported.

V3 registration sends a random board key, version, plan path, grade group, campaign code if present and setup day. It sends no name, email, service dates, plan text or medical records. Counts are pseudonymous. They do not verify people. Optional v3 usage is Off and inactive in this build. It requires both a separate agreement and activation; its only activity counters are opens and done actions. Stop counts preserves the plan. Deletion retains a one-way revocation hash and does not remove provider logs or Claude records.

Existing TEL1 schema-2 boards and new flag-off setups retain their own required count agreement, browser registration review, local count collection and update/weekly browser handoff. Registration pending does not withhold their saved plan. Their schema-2 agreement covers fixed usage counts; it is not the separate optional B3 weekly-learning consent described in historical guides. V3 never runs TEL1 enrollment, surveys or weekly count preparation, including after a flag rollback. The sections labeled TEL1 below describe that separate legacy route.

Anthropic hosts your board, conversations, Project records, and optional Ask history in your Claude account. Warfare Command cannot read your board database. Claude reads your plan to answer your questions. Your plan, notes, service-day dates, leave, claim details, contacts, and coach facts are not telemetry. Keep the board private and review sharing permissions. A shared viewer can read shared plan data under Claude's access rules. Telemetry access and pending records use private storage rules.

Your Project is in your Claude account; before uploading records, turn off "Help Improve our AI models" in Settings > Privacy. [Claude privacy controls](https://privacy.claude.com/en/articles/12109829-how-do-i-change-my-model-improvement-privacy-settings). This choice does not erase existing conversations or provider records.

## Release files, the weekly check, and updates
Chat setup, updates, and the weekly check download public files from the release repository at `https://raw.githubusercontent.com/warfarecommand/musterout-release/main/`: `release.json`, the release files it lists, and, for the weekly check, the validated notice feed copied there. Each source has its own coverage and last-success record. The laptop route instead reads `https://musterout.warfarecommand.com/release.json` once per session and the feed named in `config.json`. Each request is a plain GET that sends no identifiers, board data, or installed version. The host receives the normal internet address and request headers. When the signed channel is enabled, an isolated board worker reads public release or feed scripts from npm through unpkg or jsDelivr. Those hosts receive request metadata, including internet address and headers, but no board data, identifiers or installed version supplied by the board. The worker receives no board context; signature verification precedes trust. Failures do not block the board. TEL1 registration status opens its count review and retry; v3 follows the registration agreement described above. The board itself never posts reports or usage counts.

An update runs only after you confirm it. In chat, Claude checks each release file against the manifest's SHA-256 values; on the laptop route, it verifies each changed file against the release manifest and keeps your `my/` files. Both replace the page at your existing board address. Update now publishes only after a tap on the verified offer, preserves drafts, runs migration and verifies records. An unfinished update keeps a marker so the next run can resume. The pasted update remains a recovery path.

## Projects, uploads and connectors

A Claude Project holds your pinned instructions and public pack. You add reviewed board snapshots and files as needed. A snapshot has a capture time and does not sync automatically. Upload only your own records needed for the question, such as a Transition Readiness Seminar (TRS) certificate, orders, LES, VA letter, resume or selected STR/OMPF extracts. Your own records can stay as they are in your private Project, including files with SSNs, DoD IDs, VA claim numbers or similar identifiers. Your coach never repeats these identifiers in replies or writes them to the board or its notes. It strips them and other people's personal details from drafts for others, including call briefs, spouse briefs and advisor notes. The maintainer receives none of those uploads. Claude hosts and processes them under your account's terms. See the [Project guide](PROJECT.md) for setup and the upload checklist.

Gmail, Google Calendar and Google Drive connectors are optional. Review their permissions in Claude; scopes can exceed a single search. The Project instructions request read only unless you ask for a change. Review and approve any proposed message or record change before it runs. Connector data may remain in chats or Project copies. [Claude Google connector guidance](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors).

To remove Project data, delete the uploaded knowledge files and chats that contain it, or delete the Project in Claude. Unarchive a Project first if deletion is unavailable. Archiving alone keeps its data. [Claude Project deletion](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects). Disconnect apps in Customize > Connectors, then remove retrieved copies from chats and Project knowledge. Disconnecting does not delete records in Google; use that account's controls for originals. The maintainer cannot delete your Claude or Google records.

## TEL1 setup and your choices

Before publishing, setup explains the count schema and asks for Yes, continue or No, stop. Agreeing is required for a new supported install. On No, setup stops before publishing and sends no keyed install record. The public guide and isolated fictional demo remain available. The older welcome setup count used product/version only and a salted address hash. The new site setup-button totals are described below.

After intake, a required browser review sends the install record. Your locally verified plan opens immediately after intake. Registration remains pending with a retry until the board verifies the independent server signature and matching payload digest on a completed-install receipt. Usage queues locally while registration is pending. Opening a link, copying a record, pressing Publish, a registered flag, and bare HTTP success do not prove a received record. A failed send preserves your saved answers at the same board address. Registration failure never withholds your saved plan.

## Site setup-button totals

When you tap Copy board setup or Copy coach setup, we add one to that button's daily UTC total. These totals store no IP address, cookie, identifier, or referrer and cannot be linked to your registration. Each button has a site-wide cap of 200 counted taps per UTC hour; extra taps go into a separate daily overflow total. Failed requests can leave taps uncounted. A private weekly summary compares taps with new board registration records in the same UTC week; it does not measure completed setups or individual conversion. Hosting providers receive ordinary connection metadata under their own terms.

## TEL1 count contents

Every schema-2 record has a fixed product/schema, installed version, random install id, and a random submission id. The random install id links your records and supports deletion. These records are pseudonymous, not guaranteed anonymous. The combination of a base group, grade group, EAS month, and unusual progress can narrow a population. We never promise that these combinations cannot identify someone.

| Record | Allowed information |
| --- | --- |
| Install | Broad device type and Claude surface, setup route, EAS/resign/retire path, broad grade group, EAS month and year or Not set, required installation/base group, verified setup steps, bounded failure/error classes |
| Usage requested by update or weekly chat | Observed weeks active, tab-open counts, verified done transitions by public category, late count, Ask question count only, bounded error-class counts |
| Progress milestones | TRS done, SkillBridge participation, VA claim filed before separation, separation counseling done: Yes, No, or unknown only |
| Optional week-4 answers | Would use without a Claude subscription: Yes, No, Not sure; a fixed monthly USD price group. Older boards may also send a legacy week-4 recommend score. |
| Optional recommend answers | A 0 to 10 score labeled as first impression (`setup`) or after use (`after_use`), with Skip for each. The second ask follows opens on three separate local days. Those local dates stay on your board. Each stage is asked once; Skip finishes that stage without sending a score. |

No name, email, account id, unit, precise location, board URL, full service date, plan text, notes, custom category, Ask question/answer, coach fact, medical record, stack trace, or arbitrary text is accepted into these counts. Installation/base group is one of US West, US Central, US East, Hawaii, Japan, Other overseas, Other US location, or Not on an installation. It is not geolocation or an exact installation inventory. Full dates stay on your board. The observable install date is the server's first completed receipt, which can be later than your first attempt. Later activity uses elapsed weeks, not personal dates.

## TEL1 sending and storage

The artifact never contacts ingest. It stores counts on your board until a setup, update, or weekly chat requests a browser handoff. You review the rows at the explicit registration page and choose Send. The temporary handoff uses a fragment, which the page removes immediately. No payload or token enters a URL query, email, referrer, browser localStorage, or sandbox file. A paste-and-review route is available when the link or clipboard fails. The site keeps the request in memory for retries and shows a signed receipt to bring back. Copying alone is not sending.

A server-issued capability authenticates future sends without collecting your identity. Random enrollment and access secrets live in private board storage and the temporary browser handoff. The database stores only their hashes. A person with an access secret can exercise its count/deletion authority, so do not share handoffs or receipts. No plaintext secret appears in dashboards, diagnostics, plan copies, or email. Counts use per-page random week buckets to avoid a persistent device identifier. Browser writes are last-writer-wins with readback; activity can be incomplete after interrupted saves or an offline device. Capped or missing activity is never presented as complete observation.

Supabase stores received count records and operational receipt times. Separate short-lived rate tables contain telemetry-namespaced salted address hashes. They do not store raw addresses and are not joined to email rate hashes. Hosting and network providers can receive ordinary connection metadata under their own terms. Source code review cannot prove their live retention settings.

## Reporting and recipients

The Warfare Command maintainer and authorized operators can view a private reporting dashboard. It uses a dedicated role that can execute only the fixed aggregate reporting function. No public dashboard or client table reads are offered. Database administrators retain administrative raw access; a dashboard restriction does not remove that power.

Every reported cell needs at least 10 distinct completed, eligible install ids. Multiple records do not raise that floor. If any fixed cell is too small, the whole breakdown and complementary totals/rates are withheld. Base, grade, path, or EAS month can be shown one at a time. A report cannot combine base, grade and month. The same floor applies to HTML and CSV. Fixed periods reduce subtraction attacks but are not differential privacy or a promise of nonidentification. Anonymous enrollment does not prove 10 different people. Global setup taps are shown only with at least 10 completed installs for that fixed period; taps are not linked person-level conversions. TEL1 weekly activity measures received chat records. It does not measure every board visit. V3 optional usage remains off and inactive in this build.

No external learning agent receives new raw counts or base/grade/month records under this build. Legacy free-text reports and weekly learning counts are disabled. An independently approved support report has its own payload review; it is not part of required telemetry.

## Stop counts or delete received records

Settings > Counts and progress > Stop new counts saves withdrawal, reads it back, and removes unsent counts. A failed readback is not a confirmed cross-device change. Counts pause locally while you retry. Your existing plan remains usable. Withdrawal is client-side; it does not invalidate a count already copied to a separate browser page or its access proof. Delete received counts to revoke that admission. A changed schema needs a new agreement. A later chat does not silently reenroll you. Existing received records remain until deletion or retention expiry.

To delete, choose Review deletion in the same panel. The browser shows the full scope and requires an explicit delete action. It removes install registration, new counts/answers/funnel/receipt/admission records and any older counts/reports linked to that install id in one transaction. Return the complete signed 14-class receipt to the board to verify deletion. A lost-response retry uses the same proof and returns zero counts within 2 days. Failure or an incomplete receipt means deletion is not confirmed. A separate short-lived hashed retry proof/rate counter stays up to 2 days. Your board, Claude chats, email signup, and provider logs are separate and are not deleted by this request. Contact security@warfarecommand.com for lost access proof or the documented legacy id-based deletion; do not send board text or medical details.

Delete your artifact, chats, Project files and browser drafts through Claude/device controls to remove the copies you control. Disconnecting an optional connector does not delete source records or chat copies. The project cannot delete records from your Claude or Google account.

## Retention

| Record | Retention |
| --- | --- |
| Completed install and admission proof hashes | 24 months from first completed receipt, not extended by use |
| Uncompleted admission and unfinished attempt | 7 days |
| Counts, progress, demand/recommend answers, completed funnel events, received request receipts | 180 days from receipt, or earlier when the install expires |
| Address rate metadata and deletion retry proof | 2 days |
| Setup taps and older laptop counts | 24 months |
| Pending email signup | 7 days |
| Email delivery receipts | 13 months |
| Tool suggestions | 24 months |

The existing cleanup job applies these periods.  Backup retention is not confirmed, so deleting received records does not promise immediate removal from backups. Restoring a backup must preserve prior deletions. Providers retain their own records under their terms. Local unsent counts expire after 180 days with a visible warning; the plan stays.

## Optional email and survey

"Get release notes and an occasional two-minute survey" is a separate optional ask after install. It opens a blank signup and requires double opt-in through the existing email system. No install id, capability, board link, return URL, or telemetry payload is attached. No database join connects email addresses and install ids. Email delivery does not depend on count agreement.

No survey is sent by this build. Email addresses are not linked to board use.

## Email choices
Email signup is optional. Confirm the choices in the email we send before any stream begins. The preference page shows these four ongoing update streams in this order. The coach setup guide is a separate choice:

| Stream | What arrives | Default for a new signup |
| --- | --- | --- |
| Muster Out corrections | A fix to the regulation pack or a release that changes what your board tells you, with the update message | On for Muster Out welcome and registration signups; off otherwise |
| Warfare Command Monthly | What shipped, what is next, one AI move worth trying, and one question. Release notes and new lessons can appear here. | On for update signups; off for coach-guide-only signups |
| Weekly MARADMIN roundup | The week's possible separation and retirement matches from Watch Officer | Off; one click to add |
| New lessons | A single note when AI 102, 103, or 104 opens | On for AI 101 signups; off otherwise |

Existing confirmed subscribers retain corrections only. Their monthly, weekly, and lesson choices start off, regardless of signup source. Older pending confirmation links retain their earlier consent. Any confirmed subscriber can turn each stream on or off using the private Email preferences link. Turning every stream off keeps your address and choices in the database; Unsubscribe from everything deletes the signup.

For ongoing update signups, we send one welcome email per address after confirmation, with your chosen streams, a preference link, and a button to add the weekly roundup. The coach setup guide is one requested email after you confirm your address. It explains how to create a Claude Project and start your coach. It requires its own opt-in and does not subscribe you to setup follow-ups, corrections, Monthly, weekly roundup or lessons. The email has preferences and unsubscribe links. If your address already has confirmed email choices, the request form preserves those choices and you can use the coach guide on the site. Monthly is planned for the first Tuesday of the month and skips empty issues. The weekly roundup runs Mondays at 15:00 UTC, only with at least one match in a feed generated within the last 72 hours. Corrections and lesson launches are selected individually before sending. No standalone release-note or feedback campaign is sent; Monthly carries its question and replies go to `feedback@warfarecommand.com`.

Across Monthly, weekly roundup, and lesson launches, we send at most one campaign email per person per UTC ISO week and four per UTC calendar month. Corrections and the requested coach guide are exempt. The confirmation request and single welcome are consent messages outside these campaign caps. A stream can be skipped when another stream has used its allowance. The weekly sender can be triggered publicly, but each address can receive that roundup only once per ISO week. A stale feed or quiet week sends nothing. No open tracking, click tracking, or tracking pixels are used.

The project's Supabase database stores your address, pending or confirmed status, signup and confirmation timestamps, the last send timestamp, your four ongoing stream choices, the separate coach-guide choice and opt-in timestamp, and the signup source when supplied (`hub`, `musterout`, `register`, `ai101`, or `coach`). It stores a salted IP hash for rate limiting and hashes of confirmation, unsubscribe, and preference tokens. New confirmations bind to the chosen stream flags. Earlier confirmation receipts remain compatible. Source alone never expands earlier consent. Each unsubscribe, preference, and weekly-add link uses a random bearer token. Only hashes are stored, with recent hashes retained; older links can expire. Anyone holding a private link can use its allowed controls, so do not share it.

Separate rate counters retain salted hashes of IP and email addresses for up to 2 days, including after deletion. These counters contain no readable addresses. Delivery receipts retain a salted address hash, campaign identifier, stream, content hash, timestamps, and delivery state to enforce caps and prevent duplicates. Reserved and uncertain attempts consume campaign allowance until reviewed. These receipts hold no readable address, raw token, or email body and remain after unsubscribe for up to 13 months. The coach guide uses these existing receipts to prevent another send for 13 months, including after unsubscribe. A failed or uncertain attempt is held for review rather than retried automatically. Keeping the hash salt stable preserves duplicate prevention. Raw internet addresses and raw tokens are not stored in these tables.

Resend receives the address and message content for delivery. Supabase is the only subscriber list; addresses are not copied into Resend Contacts. We never share or sell your address for anyone else's use. Every email has one-click Unsubscribe from everything and Email preferences links. The unsubscribe link, mail-provider unsubscribe action, and preference-page button delete your signup. The project cannot delete copies already in your inbox or Resend's delivery records.

## Tool suggestions
A suggestion sends an idea of 10 to 1000 characters and an optional reply email address to the alerts endpoint. A hidden website field filters automated submissions. The database stores the idea, optional email, receipt time, and a salted hash of the internet address for rate limiting. The server sends the idea and optional email to `feedback@warfarecommand.com` through Resend. Suggestion text is escaped in the email. It never adds the reply address to the updates list.

Keep names, dates, board data, and medical details out of suggestions. To request deletion, email `security@warfarecommand.com` with enough of the idea or its optional reply address to locate it. Deletion covers the database row and the feedback inbox copy; the maintainer removes both. Rate counters stay for up to 2 days to prevent repeated requests after deletion. Copies already in your inbox and Resend's delivery records are outside the project's control.

## Older records and id-based deletion

Older laptop counts are optional and contain service, path, grade group, version and a random install id, with receipt time and salted address rate metadata. The id stays in `my/receipt.json`. Older install registration contains product, version, path, grade group, channel and a random install id. Legacy feedback reports and usage-week records are separate from schema-2 counts and are disabled.

For an id with no protected schema-2 admission, an id-based delete removes the older laptop count, install registration, feedback reports, usage-week records and private install-cohort correlation record. It does not remove rate counters or setup taps, which have no install id. For a protected schema-2 installation, use Review deletion above; the legacy command is refused.

Use `installId` from `my/receipt.json` or `meta/install.install_id` for `YOUR-INSTALL-ID`. Review the scope before running this command in Terminal on a Mac or Git Bash on Windows:

```
curl -q --max-time 20 --fail-with-body -X POST "https://vfozrzohrdrbohjqkghk.supabase.co/functions/v1/ingest" -H "content-type: application/json" -d '{"kind": "delete", "id": "YOUR-INSTALL-ID"}'
```

Require HTTP success, `ok: true`, and a `deleted` receipt with nonnegative counts for `setup_pings`, `install_registrations`, `feedback_reports` and `usage_weeks`. Keep the receipt. A partial response or failure means deletion is not confirmed; retry the same id. Contact security@warfarecommand.com if you cannot complete the request. Confirmed email signups stay until you unsubscribe or request deletion; turning off all streams keeps your address and choices.


## Access, export, correction, and deletion
Email [security@warfarecommand.com](mailto:security@warfarecommand.com) to request access to, an export of, correction of, or deletion of personal data held by the project. Use the address you signed up with or include your install id or enough of a suggestion to locate it. The maintainer verifies that the request concerns your record before releasing or changing it. Do not send board data or medical details. The project cannot access your board or Claude account; use your Claude account controls for those records.

## Adults and children's data
These tools are for adults in or leaving service. If a child submitted an email address or other personal data, a parent or guardian can request removal at [security@warfarecommand.com](mailto:security@warfarecommand.com). Include enough information to locate the record and state that it belongs to a child. The maintainer verifies the request and removes the project record and any feedback inbox copy.

## Changes to this notice
Changes appear on this page with a new last-updated date. If a change affects what an email signup authorizes, the project asks for confirmation before starting the added stream. Review this page when you return to the tools.

## What never belongs here
Keep these out of the board, the Muster Out folder, and your chats: other people's personal information, anything classified or controlled unclassified, a password, a CAC PIN, or a Social Security number. Do not paste them. The assistant is instructed not to ask for them; if it does, stop and report it. Your own records can stay as they are in your private Project, as described under Projects, uploads and connectors.

## TEL1 registration codes

For TEL1 schema 2, the service issues your registration nonce, a random access code valid for 24 hours before its first use. Your board obtains it through an explicit browser handoff and saves it in private storage before an install record can be sent. The service stores only its hash. The issuance generation is single use, and its nonce cannot recreate a deleted install. Accepted unfinished records reuse the same nonce for their exact retries and later completion.

If the service reports expiry and no verified receipt exists, a reviewed restart uses a newly issued nonce and a new random count id. Your board preserves the plan, original creation metadata, address, optional answers and pending usage. Received records are never silently relabeled. Budget exhaustion leaves registration pending and your plan available. The browser keeps proof only in memory for the handoff; it never saves payloads or access credentials in localStorage.

The optional device backup contains plan details, including medical and coach notes, and uses the platform's save confirmation. Registration credentials, consent, counts and report receipts are excluded from that file. No in-board restore snapshot is created. Nothing is emailed or sent automatically.
