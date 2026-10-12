<!-- Reader: Marines using Muster Out. Effect: understand the next step and the records the project holds. -->
# What Muster Out covers

Pack usmc-2026.10 covers the situations in the first table. For the situations in the second table, the assistant names the office to call first and builds no plan. Covered items name the office that confirms your eligibility, dates and any detail left to that office.

## Covered paths
| Situation | Covered | Notes |
| --- | --- | --- |
| Officer resigning a regular commission | Yes | MCO 1900.16 chapter 5, MARADMIN 175/24 timing |
| Officer retiring (20 or more years) | Yes | MCO 1900.16 chapter 2 retirement procedures, SBP, retired pay, TRICARE retiree enrollment |
| Enlisted retiring with 20 or more years of active service | Yes | FMCR transfer at 20 to 29 years; direct retirement at 30 or more. MCO 1900.16 chapter 7, MARADMIN 175/24, MARADMIN 326/23 and MMSR-2 guidance. The reporting unit submits to MMSR-2 through unit diary; IPAC confirms your record and dates. Shared transition, SBP and benefits items apply. |
| Enlisted or officer separating at EAS | Yes | No retirement or resignation request; confirm separation processing with IPAC. Transition gates, orders, and benefits tasks remain. |
| Reserve affiliation through DAP | Yes | Officer and enlisted windows, NAVMC 763, check in |
| SkillBridge | Yes | Category caps and approval rules from MARADMIN 280/24 and NAVMC 1700.2B. The sources conflict on approval and absence limits; confirm the applicable rule with the SkillBridge coordinator and approving command. |
| VA pre discharge claim through BDD | Yes | Timeline, evidence tasks, condition list. No rating predictions. |
| Leave | Yes | Advance leave limits, sell back cap, transition PTAD where the order allows it |

## Paths referred to an office
| Situation | Who to call first |
| --- | --- |
| Medical separation or disability retirement | PEBLO and Wounded Warrior Regiment |
| Involuntary separation | IPAC and legal assistance |
| Guard or Reserve retirement with nonregular pay | Unit Career Planner and Reserve Affairs |
| Another service | Your service personnel office |

## Setup help

### Claude plan requirement
You need Claude Pro or higher to save board data. The Free plan cannot store it. Muster Out adds no charge.

### Publishing your board
Tap Publish when Claude asks. Publishing creates the board page in your Claude account; keep its visibility private and share its link only with people you choose.

### Resume after the chat closes
Paste the setup message into a new Claude chat. Claude looks for your existing board. Open that same board to resume the setup cards; the page saves completion even if the chat closed. Never create a second board to recover.

### Board tools unavailable in the app
Open [claude.ai in a browser](https://claude.ai) and paste the setup message to give Claude access to the board tools.

### Access from a personal device
Use a personal phone or computer to open [claude.ai](https://claude.ai), then paste the setup message.

## Set up your board
If your path is covered, send this one message in any Claude chat: the Claude app on a phone, claude.ai, or the desktop app, including Claude Code and the desktop Code tab. You need Pro or higher; the Free plan cannot store board data.

```
Set up Muster Out for me. Read https://raw.githubusercontent.com/warfarecommand/musterout-release/main/SETUP.md and follow it.
```

Claude checks the release files, asks you to tap Publish for your private board, and says "Open your board." You answer the setup cards on the board. If you do not have a date yet, use the undated plan and add your date later. If the phone app cannot open the board, use claude.ai in your phone browser. The [welcome page](https://musterout.warfarecommand.com/#setup) has a Copy button for the message.

Claude Code and desktop Code tab users paste the same setup message. Developers who want a folder install can clone [the public release repository](https://github.com/warfarecommand/musterout-release). Folder updates verify each changed file against `release.json` and keep `my/`.

## Keep it current
Your board shows the weekly and update messages under Talk to Claude, each with a Copy button.

Weekly message:

```
Run the Muster Out weekly check. Read https://raw.githubusercontent.com/warfarecommand/musterout-release/main/WEEKLY.md and follow it.
```

Update message:

```
Update Muster Out. Read https://raw.githubusercontent.com/warfarecommand/musterout-release/main/UPDATE.md and follow it.
```

- **Weekly check.** During setup, Claude offers a Monday check if the chat supports recurring tasks. Confirm your timezone and time. If scheduling is unavailable or you skip it, send the weekly message any week. The check files possible matches from the sources actually covered for your path and lines of effort. It also checks for new versions. The board shows watch status itself once the signed feed reaches it. Missing coverage or a failed check is never a clean result. More > Watch coverage names each source, checked window, last success and any failed attempt. ALNAV and cited orders are not yet covered.
- **Updates.** Open your board and tap Update now when it offers a verified release. More > Updates reopens the offer. Not now snoozes that version for 24 hours; a correction keeps its Today banner. On an older board, paste the update message once to add the update capability while keeping the same address and data. If Update now is unavailable, the paste message remains the recovery path. A publish is complete only after migration and data readback pass.

If your path is not covered, call the office listed above.

## Save and access help

Save status is beside the editor. Saved means the write was read back and matched. Keep an unsaved draft on its original device until recovery finishes. When both a draft and saved work changed, compare them before choosing Keep my draft or Use saved version.

| State or diagnostic | Message and recovery |
| --- | --- |
| Unsaved / Saving / Saved | `Unsaved changes.` / `Saving...` / `Saved.` Wait for readback before leaving an editor. |
| `db.unavailable` or unknown db error | Save failed. Your changes are kept on this device. Retry once, then Copy changes. |
| `db.resource_exhausted` | Saving paused. Try again later when fewer changes are pending. Copy changes. |
| `db.quota_exceeded` | Board storage is full. Your changes have not saved. Copy changes / Get help. Do not delete records automatically. |
| `db.invalid_argument`, `db.transform_error`, ref `TypeError` | This change could not be saved. Copy diagnostic. Do not repeat a malformed write. |
| Confirmed data-write permission false | This view is read-only. You can view saved work. Open the owner's view to edit. |
| Missing db or host; `revoked`, `not_granted`, `capability_disabled`, `capability_removed` | Saving is unavailable in this view. Open your board in Claude / Copy diagnostic. A retained snapshot is a Last loaded copy. |
| Terminal refresh listener error, including `queue_overflow` | Saved data could not refresh. Reload once / Copy diagnostic. A repeated write does not repair a stopped listener. |
| Free confirmed by account evidence | Claude Pro is required to save this board. Free cannot store your plan. View demo / Copy setup message. A missing permission alone does not identify your plan. |
| Seed still running after two minutes | Open the same board and reload once. The expired claim can resume missing writes. Never change counts or seed by hand. |
| `DRAFT_STORAGE_FAILED` | Your draft could not be kept on this device. Copy changes before continuing. Do not update or reload until the draft is preserved. |
| A reset or profile mismatch | Resume the confirmed reset through SETUP at the same URL, or choose Keep my plan after reviewing the changes. Never clear a reset marker to dismiss a warning. |

## Planned dates

Enter your proposed EAS, resignation, retirement or FMCR date to see the whole plan. Deadlines compute before approval and say "From planned date" until your date is approved. Tap the date on Today, edit it, and Save to move the deadlines. Dates you set on individual items stay fixed.

EAS and resignation use the entered date as the last active-duty day. Ordinary retirement uses the preceding day; an enlisted month-end retirement-path date projects FMCR service end on that day. Confirm the action and any exception with IPAC and MMSR-2. A fixed date you set on the last-active-duty milestone overrides the projection. Approvals, orders and appointments remain undated until you record them.

## Update help

| State or diagnostic | Message and recovery |
| --- | --- |
| `artifact.not_writer`, `not_granted`, `consent_required` | This view cannot publish updates. Copy update message. Data editing may still work. |
| Artifact missing; `not_declared`, `capability_disabled`, `capability_removed` | Updates are unavailable in this view. Copy update message. |
| `artifact.conflict` | Another version is opening. Your draft is kept. Wait for that page and check its actual version; do not publish blindly. |
| `artifact.upstream_error` or unknown artifact error | The update did not finish. Your draft is kept. Retry once; then Copy diagnostic. |
| `artifact.rate_limited` | Updates are paused. Try again later when this board has finished publishing. |
| `artifact.too_large` | This update is too large to publish. Copy diagnostic and use the verified pasted update path. |
| `artifact.invalid_content`, `transform_error`, `read_only_path` | This update cannot be published here. Copy diagnostic. |
| `UPDATE_UNTRUSTED`, `UPDATE_TIMEOUT`, `UPDATE_OVERSIZE`, `UPDATE_FLOOD` | This update could not be verified. Keep using your current board. Copy diagnostic. Never bypass a signature or hash check. |
| `UPDATE_VERIFY_FAILED` | The update opened, but verification is incomplete. Copy diagnostic / Get help. Keep the recovery journal; never downgrade or alter seed counts. |
| `SNOOZE_SAVE_FAILED` | This reminder could not be saved. It may appear again. Continue. |

An interrupted update resumes at the same address. A chat journal keeps a saved manifest and stage. A page journal keeps its state and target version. Let the owning path resume; do not delete either journal or treat one as the other. A failed save takes priority over an update offer. Correct a bad release with a higher version. Never downgrade. If signed delivery cannot recover, paste the verified UPDATE message above.

## Watch and Claude help

| State or diagnostic | Message and recovery |
| --- | --- |
| `WATCH_FAILED` | Last attempt failed. Showing the last good check. With no success: No successful check yet. Run the pasted weekly check. |
| `FEED_UNTRUSTED` | The new watch feed could not be verified. Showing the last good check. Keep the last good result. |
| `FEED_STALE` / `FEED_GAP` | Watch results are over 8 days old. / Some notices fall outside this feed's 30-day window. Copy weekly check message. |
| Sample absent or permission/capability disabled | Claude is unavailable in this view. Continue with the fields / Copy diagnostic. Intake and report fields still work. Ask says Ask is unavailable in this view. Copy your question into Claude. |
| `sample.tools_unavailable` | Claude cannot use page tools here. Continue with the fields. Plain Ask may still work. |
| `sample.rate_limited` | Claude usage is limited right now. Continue with the fields. Try manually later; no reset time is promised. |
| `sample.session_expired` | Sign in to Claude again to ask. Copy your draft first. |
| `sample.refused` | Claude could not rewrite these details. Edit the details in the field above. |
| `sample.invalid_json` / `empty_completion` | Claude did not return usable wording. Edit the details / Try again. |
| `sample.invalid_request`, `prompt_too_large`, `transform_error`, `queue_overflow` | Claude could not process this request. Continue with the fields / Copy diagnostic. |
| `sample.upstream_error` or unknown sample error | Claude's response was interrupted. Continue with the fields / Try again. |
| `sample.cancelled` | Keep your original details and continue. |
| Permissions denied or unavailable | Claude is off for this board. Open permissions. / Permissions are unavailable here. Use the artifact's Permissions menu. |
| `permissions.manage.unavailable` / `upstream_error` | Open the artifact's Permissions menu to change access. Declined grants are not requested repeatedly. |

Watch notices are possible matches until reviewed. Saving one does not establish applicability or change your plan. Coverage lists only sources actually shipped. Daily status requires both daily collection and sync; pasted weekly checking remains available.

## Copy diagnostic and report a problem

Report a problem is available on every screen, including an empty board. Copy diagnostic works without board data or Claude. It copies version, pack, screen, capability states and a bounded in-memory list of error classes. It excludes notes, records, values and stack traces. You can paste it into your own Claude chat to review a known repair. Copy changes is different: it may contain your draft, so keep it in your own account.

The report starts with structured fields and optional details. Keep names, service dates, board links and record details out of the text. If you request a rewrite, Claude uses only those entered details. Review the final payload again after any edit. Manual Copy payload is available before the learning channel ships. Queue report appears only after that channel passes its gate; Queue approves transmission of exactly the shown bytes. Queued does not mean Sent.

If chat cannot send or cannot confirm acknowledgment, open [the report page](https://musterout.warfarecommand.com/report/), paste the payload, review it and tap Send. The link carries no payload. Keep the same report id when retrying. Only a matching success receipt proves it was received. Bring that receipt back to Claude before clearing the queued report. If copying fails, select and copy the displayed text yourself; keep the sheet open until you have it.

| Report state | Recovery |
| --- | --- |
| Outbox write failed | Report not queued. Copy payload. Keep the stable id and reviewed bytes for retry. |
| `REPORT_TRANSPORT_UNAVAILABLE` / `REPORT_SEND_FAILED` | Report not sent. Copy payload / Open report page. Keep unknown outcomes pending. |
| `REPORT_VALIDATION_FAILED` | Review the highlighted fields before continuing. Do not send raw rewrite output. |
| `CONSENT_SCHEMA_CHANGED` | Counts paused. Review the new schema to allow sending. |
| Off could not be saved | Counts paused on this device. Off could not be saved for other devices. Get help. Stop the recurring sending task until the board consent reads back Off. |
| `REPORT_DELETE_FAILED` | Deletion is not confirmed. Keep this receipt and try again. |

Reports and counts have separate consent. Counts start off and require a filled sample of the fixed schema. Settings lets you inspect consent and receipts, turn counts Off, cancel an unsent report, or request deletion. Text and profile fields need approval of each exact report. Off does not revoke a separately approved report. Received reports and counts are kept for 180 days. Use the [privacy deletion procedure](PRIVACY.md) to request removal and keep its receipt.

## Project help

Use [PROJECT.md](PROJECT.md) after your first useful board. It includes the full instructions, uploads and optional connector guidance. A Project uses your own Claude account and records; its drafts still need verification. If Claude cannot read the board, upload a reviewed snapshot with its capture time. Finish setup on a computer if the phone path is unavailable. The [starter workflows](PROJECT.md#starter-workflows) name the evidence and confirming office for each draft.
