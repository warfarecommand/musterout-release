# Deploy and operate email functions

Reader: The supervisor or an authorized operator. Apply the reviewed schema, deploy the three functions, and verify behavior before inviting users. Every manual send, including a recovery, needs the owner's OK. This runbook and [alerts/README.md](functions/alerts/README.md) are the canonical operator instructions for corrections, the Monthly, and lesson launches.

## Prerequisites and SQL

Run from the repository root. Use private credential tooling to provide process secrets. Do not read or write `.env` files or print credentials. The edge runtime supplies `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`. Keep the existing `IP_HASH_SALT` or `INGEST_SALT` without rotation. Keep `RESEND_API_KEY` restricted to sending on the verified `warfarecommand.com` domain. Set a private `DIGEST_OPS_KEY` for detailed digest dry reports; when unset, dry requests return only `{"ok":true}`.

Match the live schema to `supabase/schema.sql` and these founder-authored migrations before applying missing schema:

- `supabase/migrations/20261009210000_alert_signups.sql`
- `supabase/migrations/20261009230000_platform_telemetry.sql`
- `supabase/migrations/20261010010000_email_streams.sql`

Do not overwrite an incompatible table or reset existing preferences. Verify all four stream columns, the source-default trigger, `email_delivery_receipts`, and the service-only `email_delivery_gate` RPC. Preserve the legacy consent backfill. Application tables must have RLS with no public data policies or client grants.

Apply the reviewed W1 SQL before deploying ingest:

1. `_cook/audit/fixes/A-02.sql` adds the atomic `ingest_rate_hit` RPC. Verify the existing `(ip_hash, minute)` primary key, pinned search path, invoker security, and EXECUTE for service_role only.
2. `_cook/audit/fixes/A-09.sql` locks the retired lesson table and drops it and `lesson_summary` only when empty. A notice means data was preserved for the supervisor's decision.
3. Apply only the function section of `_cook/audit/fixes/A-16.sql`, through `commit`, first. Review `select * from public.cleanup_retained_data(true);` before applying the schedule section. Dry mode returns six table counts and deletes nothing.

Pending signups expire seven days after `last_sent_at`. When no send timestamp exists, cleanup uses `created_at`. Confirmation links older than seven days cannot confirm or send a welcome. Confirmed preference and unsubscribe links have no time expiry; the existing recent-hash limit still applies.

Cleanup removes ordinary ingest minute counters after two days. Alerts rate slots have a fixed 2000 timestamp, so they are retained until two days after the expiry minute stored in `n`. This preserves the ten-minute throttle and the rolling address limits of three confirmations per day and five per week, including after signup deletion. Cleanup removes setup intents, install registrations, and suggestions after 24 months, and email delivery receipts after 13 months. Campaign duplicate and welcome suppression receipts are bounded by that retention window.

## Templates, deployment, and verification

In Resend's domain settings, verify open and click tracking are disabled. Compare the six approved templates, variables, sender, subject, and reply-to with the reviewed email library. Publish only `confirm-subscription`, `welcome`, `correction-alert`, `monthly`, `weekly-roundup`, and `lesson-launch`. Do not sync contacts or send the retired aliases. Template publication does not send mail.

Deploy with JWT verification disabled:

```sh
supabase functions deploy alerts --project-ref vfozrzohrdrbohjqkghk --no-verify-jwt
supabase functions deploy digest --project-ref vfozrzohrdrbohjqkghk --no-verify-jwt
supabase functions deploy ingest --project-ref vfozrzohrdrbohjqkghk --no-verify-jwt
```

Read back ACTIVE status and `verify_jwt=false` for each function. Verify website preflights for `https://warfarecommand.com`, `https://www.warfarecommand.com`, and `https://musterout.warfarecommand.com`. Publish the reviewed static pages through the supervisor's site procedure and verify `/alerts/confirmed/`, `/alerts/expired/`, `/alerts/unsubscribed/`, and `/alerts/preferences/`. For the MTN-68 repair, publish `/alerts/action/`, `/assets/email-action.js`, `/assets/email-action.css`, and the reviewed `_headers` before deploying the alerts handler. Old emailed URLs redirect to this first-party page with the token in its fragment. GET and reload do not call the database or mail provider; its single button sends a POST. Keep `form-action` blocked and permit the existing first-party script and Supabase `connect-src`.

Public digest dry requests must return exactly `{"ok":true}` with no counts. Supply `x-ops-key` from private process tooling to obtain a detailed dry report. The header must match `DIGEST_OPS_KEY` exactly. An incorrect key or unset secret returns the same public result. Do not print or record the header value. Dry mode must create no receipts, token hashes, or mail.

Use an explicitly owner-authorized test address for live mail verification. Check source-specific confirmation choices, HTML and text content, one welcome, four preferences, weekly-add, body unsubscribe, and provider POST unsubscribe. Preview each link before pressing its button and verify unchanged consent, signup existence, token hashes, and receipt counts. Weekly enrollment consumes its link atomically; replay cannot reverse a later opt-out. Confirmation replay and tokens older than seven days fail. Recent footer links remain valid according to their existing retention rules; deleted and evicted footer authorizations cannot change a new signup. Provider one-click POST must return 200 without a redirect, cookies, authentication, or a second confirmation. Verify the delivered DKIM signature covers List-Unsubscribe and List-Unsubscribe-Post, as required by [RFC 8058](https://www.rfc-editor.org/rfc/rfc8058). Repeated signup within ten minutes sends nothing; confirmed signup sends no new confirmation. Verify the daily and weekly confirmation caps with isolated supervisor test data rather than unsolicited inbox traffic. An expired confirmation POST returns 404 to the JSON button client, or redirects a navigation client to `/alerts/expired/`, without a welcome. GET itself does not look up token expiry. Preference and unsubscribe links remain usable after seven days.

Confirmation fallback is allowed only for an explicit 4xx template rejection naming a missing or unpublished template or invalid variables. Server, quota, and network failures record an `unknown` receipt and send no second email. Review those receipts against provider history before any recovery. [Resend's error reference](https://resend.com/docs/api-reference/errors) describes the HTTP and error-type conventions.

After verification, apply the retention schedule section last and read back the named `musterout-retention-cleanup` job at `17 3 * * *` (03:17 UTC daily). Inspect its first run and returned deletion counts. Preserve the existing `musterout-weekly-digest` job at `0 15 * * 1` (Mondays 15:00 UTC), two hours after Watch. Its pg_net request uses Content-Type and `{}` without an ops header or authorization requirement. Inspect cron and pg_net outcomes plus receipt states; keep failures visible.

## Manual correction, Monthly, or lesson launch

Follow the [manual sender procedure](functions/alerts/README.md). Prepare `reviewed-message.json` with exactly `template`, `campaign`, and `variables`. The accepted templates and variable keys are:

| Template | Required variables |
| --- | --- |
| `correction-alert` | `WHAT_CHANGED`, `WHO_IS_AFFECTED`, `WHAT_TO_DO`, `VERSION` |
| `monthly` | `SHIPPED`, `NEXT`, `AI_MOVE`, `QUESTION` |
| `lesson-launch` | `LESSON_TITLE`, `LESSON_PROMISE`, `LESSON_URL` |

Use reviewed nonempty copy and an owner-verified HTTPS lesson URL on warfarecommand.com. Skip an empty Monthly; its planned cadence is the first Tuesday. Monthly, weekly, and lessons share one send per UTC ISO week and four per UTC calendar month per address. Corrections are exempt. The sender filters each audience by its confirmed stream preference.

Supply `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `RESEND_API_KEY`, and either existing salt in the private process environment. Freeze the campaign identifier and copy. Run the dry report:

```sh
deno run --allow-env=SUPABASE_URL,SUPABASE_SERVICE_ROLE_KEY,RESEND_API_KEY,IP_HASH_SALT,INGEST_SALT --allow-net=vfozrzohrdrbohjqkghk.supabase.co,api.resend.com --allow-read=reviewed-message.json supabase/functions/alerts/send_alert.ts reviewed-message.json
```

Review `recipients`, `eligible`, `skipped`, and `reasons`; the dry run creates no receipts or links and sends no mail. Obtain the owner's OK for the exact reviewed file and dry report. Every manual send requires this OK. Then run:

```sh
deno run --allow-env=SUPABASE_URL,SUPABASE_SERVICE_ROLE_KEY,RESEND_API_KEY,IP_HASH_SALT,INGEST_SALT --allow-net=vfozrzohrdrbohjqkghk.supabase.co,api.resend.com --allow-read=reviewed-message.json supabase/functions/alerts/send_alert.ts reviewed-message.json --send
```

Review provider history and receipts even if the command fails. This service-only query summarizes receipt states without readable addresses or links:

```sql
select campaign, state, count(*) as receipts
from public.email_delivery_receipts
group by campaign, state
order by campaign, state;
```

`accepted` records provider acceptance. Inbox delivery requires separate evidence. A `blocked` result requires receipt investigation before a retry. Recovery requires matching campaign, salted recipient hash, content hash, attempt time, and provider history. Record the evidence privately. Reconcile proven acceptance to `accepted` and do not resend. Retain `unknown` if acceptance remains uncertain. For proven nonacceptance, the supervisor may remove only the reconciled receipt after recording evidence, recheck consent and dry counts, obtain the owner's OK for recovery, and rerun the same frozen file and identifier. Shared caps still apply. Never clear campaign receipts or change the identifier merely to force a retry.

## Local checks

All HTTP in the suites is mocked. The focused browser integration is `supabase/functions/_test/email_action_check.mjs`; set EMAIL_STAGE to a `docs/_deploy.sh --stage-only` output and EMAIL_OUTPUT to the evidence folder. It verifies the actual handler GET response and follows its location in an offline browser with all requests intercepted. Run each from its function directory:

```sh
node --experimental-strip-types /Users/joelsartain/dev/musterout/_cook/audit/deno_shim_run.mjs "$PWD/index_test.ts"
```

Run alerts, digest, and ingest after every change. SQL application, live delivery, deployed secrets, tracking settings, and cron execution require supervisor verification.

The browser review page marks human unsubscribe POSTs with `review=1`, which requires the Muster Out Origin. A nonmatching or evicted token returns 404 in that mode instead of claiming removal. Direct provider URL POSTs retain idempotent 200, even with an application/json Accept header. The action page bounds both response headers and body reads to 15 seconds, then restores the button and explains that the result may already have been saved. It never retries automatically.
