# Published email templates

These six files are the source of the Resend templates with the same aliases: confirm-subscription, welcome, correction-alert, monthly, weekly-roundup, lesson-launch. CAMPAIGN.md is the email framework they follow.

- Resend reserves UNSUBSCRIBE_URL at send time, so every template uses ALERT_UNSUBSCRIBE_URL; the functions send that name (see templateMessage in functions/alerts/index.ts).
- Declare every variable a template uses when you update it in Resend, then publish. A template that names a variable the code does not send fails at send time.
- After any change, run one live check to your own address: subscribe, confirm, and read the welcome receipt state in email_delivery_receipts. Delete the test rows afterward.
