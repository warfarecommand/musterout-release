# Published email templates

These six files are the source of the Resend templates with the same aliases: confirm-subscription, welcome, correction-alert, monthly, weekly-roundup, lesson-launch. CAMPAIGN.md is the email framework they follow.

- Resend reserves UNSUBSCRIBE_URL at send time, so every template uses ALERT_UNSUBSCRIBE_URL; the functions send that name (see templateMessage in functions/alerts/index.ts).
- Declare every variable a template uses when you update it in Resend, then publish. A template that names a variable the code does not send fails at send time.
- After any change, run one live check to your own address: subscribe, confirm, and read the welcome receipt state in email_delivery_receipts. Delete the test rows afterward.

Setup help is an optional, disabled proposal. setup-1, setup-2, and setup-3 each have HTML, text, and JSON metadata with subject, preheader, and alt text. The exact variables are STOP_SETUP_URL, PREFS_URL, and ALERT_UNSUBSCRIBE_URL. No per-recipient image URL is used. The three metadata + HTML + text hashes are pinned in alerts/index.ts. Freeze the provider aliases at those approved bytes; publishing different template copy under a pinned alias would defeat that review. Do not publish or send until the owner approves the privacy proposal and frozen copy, the supervisor captures all six GIFs, and the View with pictures route is verified. See _cook/coach/build/SETUP_EMAIL_RUNBOOK.md.
