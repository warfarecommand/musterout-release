# Email scopes

The default sender audience is Muster Out correction alerts and release notes. Use `--platform` for Warfare Command updates: new tools, new lessons, Muster Out corrections, and release notes. That audience includes only rows with a confirmed platform consent receipt. Signup origin alone does not expand consent.

New platform confirmation tokens bind their hash to the stated scope. Confirmation consumes the pending token and retains `consent:platform-updates:v1` in the existing `confirm_hash` field. Old pending links still confirm the narrower scope and clear that field. Existing confirmed rows are never upgraded by another signup request. A subscriber can unsubscribe and sign up again to confirm a different scope. No migration is required for this distinction.

Platform receipt filtering applies during the count, ID snapshot, recipient read, and unsubscribe-link reservation. Use the default audience only for the common correction and release-note scope.

The board update callout appears only with `--musterout-update`. Use it when the message concerns a Muster Out update. Tool and lesson announcements use `--platform` without that flag.

Run the owner-controlled sender without `--send` to print only the eligible confirmed count:

```sh
deno run --allow-env --allow-net --allow-read supabase/functions/alerts/send_alert.ts message.txt --platform
```

The message file contains a subject line, a blank line, and one line per paragraph. Add `--send` only to send an approved message. The branded header, individual unsubscribe links, and one-click unsubscribe headers are retained for both scopes.
