# Manual email campaigns

Reader: The owner or an authorized operator. Use this procedure to prepare and send a correction alert, the Monthly, or a lesson launch. Every manual send requires the owner's OK for the reviewed JSON file and its dry report. An operator cannot approve their own send.

[DEPLOY_ALERTS.md](../../DEPLOY_ALERTS.md) is the canonical deployment, verification, and receipt recovery runbook. This file is the canonical manual sender procedure. The stream rules and owner approval requirement come from the [campaign policy](../../../_cook/email_library/CAMPAIGN.md).

## Prepare the reviewed file

The file `reviewed-message.json` contains exactly three keys: `template`, `campaign`, and `variables`. `variables` is an object containing exactly the keys in this table, with nonempty strings as values. The sender rejects text files, retired aliases, extra keys, arbitrary HTML, and template placeholders.

| Template | Audience | Required variables |
| --- | --- | --- |
| `correction-alert` | Corrections enabled after confirmation | `WHAT_CHANGED`, `WHO_IS_AFFECTED`, `WHAT_TO_DO`, `VERSION` |
| `monthly` | Monthly enabled after confirmation | `SHIPPED`, `NEXT`, `AI_MOVE`, `QUESTION` |
| `lesson-launch` | Lessons enabled after confirmation | `LESSON_TITLE`, `LESSON_PROMISE`, `LESSON_URL` |

Choose a campaign identifier with 1 to 100 characters matching `[A-Za-z0-9_-]`. Freeze the identifier and reviewed copy before approval. Receipts use `template:campaign`. Every retry uses the same file and identifier. Changing an identifier can evade duplicate protection after a cap window; it is not a recovery procedure. Changing copy under an existing identifier is refused.

Use plain reviewed copy within the sender's limits. Footer and preference URLs are generated per subscriber. The owner must verify that `LESSON_URL` is the actual published HTTPS lesson at `https://warfarecommand.com`. Do not send a sample URL. The Monthly is planned for the first Tuesday; skip an issue with nothing worth saying. The owner judges the editorial value and timing.

Monthly, weekly, and lesson sends share a limit of one per salted address per UTC ISO week and four per UTC calendar month. Corrections are exempt. A Monday roundup can consume the allowance before Tuesday's Monthly. Reserved, accepted, and uncertain campaign receipts consume the allowance. Confirmation and welcome receipts are separate transactional messages.

## Dry report, approval, send

Run from the repository root with credentials already supplied through private process tooling: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `RESEND_API_KEY`, and either existing `IP_HASH_SALT` or `INGEST_SALT`. Do not rotate the salt, print credentials, or put them in the message file or an `.env` file.

Run a dry report first:

```sh
deno run --allow-env=SUPABASE_URL,SUPABASE_SERVICE_ROLE_KEY,RESEND_API_KEY,IP_HASH_SALT,INGEST_SALT --allow-net=vfozrzohrdrbohjqkghk.supabase.co,api.resend.com --allow-read=reviewed-message.json supabase/functions/alerts/send_alert.ts reviewed-message.json
```

The dry report prints `dry`, `recipients`, `eligible`, `accepted`, `skipped`, and `reasons`. It reads subscribers and calls the delivery gate in dry mode. It creates no receipts or links and sends no mail. Review the audience and every skipped reason. Keep the report with the frozen file and obtain the owner's OK for that file and campaign before sending. If the reviewed file changes, repeat the dry report and obtain a new OK.

After the owner's OK, use the same command with `--send`:

```sh
deno run --allow-env=SUPABASE_URL,SUPABASE_SERVICE_ROLE_KEY,RESEND_API_KEY,IP_HASH_SALT,INGEST_SALT --allow-net=vfozrzohrdrbohjqkghk.supabase.co,api.resend.com --allow-read=reviewed-message.json supabase/functions/alerts/send_alert.ts reviewed-message.json --send
```

Run one manual sender at a time. It rechecks confirmed stream choices, reserves delivery receipts, and sends batches of at most 100 with one address per message. Fresh unsubscribe and preference links are saved as hashes before the batch goes to Resend. Deletion after the final consent check can leave one email already in flight.

## Review receipts and recover

Review `email_delivery_receipts` and Resend request history after every send, including a command that exits with an error. `accepted` means provider acceptance; it does not prove inbox delivery. `duplicate`, `weekly_cap`, and `monthly_cap` are expected skips. `blocked` means an existing `reserved`, `failed`, or `unknown` attempt requires investigation. The sender does not retry it automatically.

For each blocked receipt, match the frozen campaign, salted recipient hash, content hash, attempt time, and provider request history. Keep the evidence in the supervisor's private operations record. If acceptance is proven, reconcile the receipt to `accepted` and do not resend. If delivery remains uncertain, retain `unknown` and stop recovery for that recipient. If rejection or nonacceptance is proven, the supervisor can remove only that reconciled receipt after recording the evidence. Recheck consent and dry counts, obtain the owner's OK for the recovery, and rerun the frozen file and identifier. Shared caps still apply. Never clear a campaign's receipts or change its identifier merely to force a retry. These steps also cover a batch that was accepted before its response was lost.

## Optional Setup help proposal (14 OCT 2026)

This cook adds a disabled setup series. Do not deploy or enable it under the old no-drip promise. The supervisor's handoff is [_cook/coach/build/SETUP_EMAIL_RUNBOOK.md](../../../_cook/coach/build/SETUP_EMAIL_RUNBOOK.md). Founder-applied SQL lives under that cook's build/sql, outside migrations. Apply schema before this function because ROW_FIELDS now selects setup, setup_opted_at, confirmed_at, and setup_token_hashes. Preserve the existing source trigger defaults while adding coach-only explicit enrollment.

Setup help uses source coach and the setup stream, explicit setup: true, and an address confirmation bound to consent:setup-help:v1. It enrolls none of the four ongoing streams. setup-1 replaces welcome. Fixed campaigns setup-1:v1 to setup-3:v1 use the atomic email_delivery_gate and permanent email_setup_claims. Failed or unknown delivery blocks later stages and is never automatically retried. The separate lifetime cap is 3, including after signup deletion and 13-month receipt cleanup. Keep the existing delivery salt stable and do not delete the permanent claims to force another send.

POST /functions/v1/alerts/setup requires x-setup-cron-secret matching private SETUP_CRON_SECRET and SETUP_EMAIL_ENABLED=true. Add ?dry=1 for a report that creates no claims, links, or mail. With the flag absent, coach signup and cron fail closed; legacy alerts keep their existing behavior after schema application. The 15-minute cron is proposed separately and installed only after approval. Manual campaign CLI accepts none of the setup aliases.

Every setup email includes a distinct hashed stop token. GET stop_setup opens a confirmation page without opting out; POST stops setup only. This avoids link-preview opt-outs. Existing preference requests with four choices preserve setup; an optional fifth boolean can turn it off. True does not enroll an address that never opted in or has stopped. Unsubscribe still deletes the signup. Final consent reread prevents future batches after stop; one message already in flight may arrive.

All nine setup footer authorization hashes use the separate setup_token_hashes array. Keep it until signup deletion, including after setup stops and after ongoing streams rotate their eight recent hashes. All footer routes accept either array. The sender uses compare-and-set on its own array, never evicts a setup hash, and refuses a missing durable field or more than nine hashes. Existing issued links whose hashes were already discarded cannot be recovered; this feature must remain disabled until the schema and fix are verified. No setup emails were sent by this cook.
