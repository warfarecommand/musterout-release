# Deploy correction alerts

Supervisor only. This build has not applied SQL, deployed the function or site, or sent email. Run from the repository root. Do not write an `.env` file or print credentials.

The founder-authored migration is `supabase/migrations/20261009210000_alert_signups.sql`. Leave it unchanged. The function also uses the existing service-only `ingest_rate` table from `supabase/schema.sql`; it must already exist. `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are supplied by the edge runtime.

The only new secret the owner sets is `RESEND_API_KEY`. Use a Resend key with sending access only and restrict it to the verified `warfarecommand.com` domain. The sender is `Muster Out <updates@warfarecommand.com>`. Confirm that this sender is permitted before opening signups. Do not create or sync a Resend contact list.

The alerts function uses existing `IP_HASH_SALT`, with existing `INGEST_SALT` as a fallback because ingest reads that name. The supervisor must verify that one is present. Alerts fail closed if neither exists; there is no public default salt.

Load the existing management access token into the process environment as `SUPABASE_ACCESS_TOKEN` through the supervisor's credential tooling. Have the owner supply `RESEND_API_KEY` in the process environment through the same secure method. The following commands do not read or write any `.env` file.

## 1. Check prerequisites and set the one new secret

This lists secret names only internally and checks the existing rate table. It does not print values. The POST sets `RESEND_API_KEY` through the [management secrets endpoint](https://supabase.com/docs/reference/api/v1-create-secrets).

```sh
python3 - <<'PY'
import json, os, urllib.request
base = 'https://api.supabase.com/v1/projects/vfozrzohrdrbohjqkghk'
headers = {'Authorization': 'Bearer ' + os.environ['SUPABASE_ACCESS_TOKEN'], 'Content-Type': 'application/json'}
def call(path, method='GET', body=None):
    payload = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(base + path, data=payload, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)
names = {entry['name'] for entry in call('/secrets')}
assert names & {'IP_HASH_SALT', 'INGEST_SALT'}, 'Existing IP salt is missing; stop'
call('/database/query', 'POST', {'query': 'select ip_hash, minute, n from public.ingest_rate limit 0;', 'read_only': True})
key = os.environ['RESEND_API_KEY']
assert key, 'RESEND_API_KEY is empty'
call('/secrets', 'POST', [{'name': 'RESEND_API_KEY', 'value': key}])
print('Prerequisites checked; Resend secret set')
PY
```

## 2. Apply the founder's migration through the SQL endpoint

This sends the exact local migration to the [management SQL endpoint](https://supabase.com/docs/reference/api/v1-run-a-query). The verification prints only schema properties. Stop if an existing table has a different shape; this migration's `if not exists` does not repair an incompatible table.

```sh
python3 - <<'PY'
import json, os, pathlib, urllib.request
url = 'https://api.supabase.com/v1/projects/vfozrzohrdrbohjqkghk/database/query'
headers = {'Authorization': 'Bearer ' + os.environ['SUPABASE_ACCESS_TOKEN'], 'Content-Type': 'application/json'}
def sql(query, read_only):
    request = urllib.request.Request(url, data=json.dumps({'query': query, 'read_only': read_only}).encode(), headers=headers, method='POST')
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)
sql(pathlib.Path('supabase/migrations/20261009210000_alert_signups.sql').read_text(), False)
columns = sql("select column_name, data_type from information_schema.columns where table_schema = 'public' and table_name = 'alert_signups' order by ordinal_position;", True)
expected = ['id', 'email', 'status', 'confirm_hash', 'unsubscribe_hashes', 'ip_hash', 'created_at', 'confirmed_at', 'last_sent_at']
assert [row['column_name'] for row in columns] == expected, 'Unexpected alert_signups schema'
assert next(row['data_type'] for row in columns if row['column_name'] == 'unsubscribe_hashes') == 'ARRAY'
rls = sql("select relrowsecurity from pg_class where oid = 'public.alert_signups'::regclass;", True)
assert rls[0]['relrowsecurity'] is True
policies = sql("select count(*)::int as n from pg_policies where schemaname = 'public' and tablename = 'alert_signups';", True)
assert policies[0]['n'] == 0
print('Migration applied; expected columns, RLS, and no policies verified')
PY
```

## 3. Deploy alerts through the multipart endpoint

The [management deploy endpoint](https://supabase.com/docs/reference/api/v1-deploy-a-function) takes a `file` part and JSON `metadata`. Upload only `index.ts`; `send_alert.ts` runs locally and tests are not deployed. The metadata below sets `verify_jwt` to false. The readback must show the same value and an active function.

```sh
python3 - <<'PY'
import json, os, pathlib, urllib.request, uuid
base = 'https://api.supabase.com/v1/projects/vfozrzohrdrbohjqkghk'
boundary = 'alerts-' + uuid.uuid4().hex
metadata = json.dumps({'entrypoint_path': 'index.ts', 'name': 'alerts', 'verify_jwt': False}).encode()
source = pathlib.Path('supabase/functions/alerts/index.ts').read_bytes()
body = (
    ('--' + boundary + '\r\nContent-Disposition: form-data; name="metadata"\r\nContent-Type: application/json\r\n\r\n').encode()
    + metadata
    + ('\r\n--' + boundary + '\r\nContent-Disposition: form-data; name="file"; filename="index.ts"\r\nContent-Type: application/typescript\r\n\r\n').encode()
    + source + ('\r\n--' + boundary + '--\r\n').encode()
)
auth = {'Authorization': 'Bearer ' + os.environ['SUPABASE_ACCESS_TOKEN']}
request = urllib.request.Request(base + '/functions/deploy?slug=alerts', data=body, headers={**auth, 'Content-Type': 'multipart/form-data; boundary=' + boundary}, method='POST')
with urllib.request.urlopen(request, timeout=120) as response:
    result = json.load(response)
assert result['slug'] == 'alerts' and result['verify_jwt'] is False
with urllib.request.urlopen(urllib.request.Request(base + '/functions/alerts', headers=auth), timeout=60) as response:
    live = json.load(response)
assert live['verify_jwt'] is False and live['status'] == 'ACTIVE'
print('Alerts deployed; active with verify_jwt false')
PY
```

## 4. Publish the site and verify with an address the owner controls

Run `cd docs && python3 _build_pages.py`, then `bash _deploy.sh` using the supervisor's existing site deployment credentials. The allowlist includes the confirmed, unsubscribed, and expired pages.

On the live website, request alerts with an address the owner controls. Verify that the form displays the inbox message, the confirmation email has both text and HTML plus both unsubscribe headers, the confirmation link opens `/alerts/confirmed/`, and using it again opens `/alerts/expired/`. Repeating a signup within ten minutes must send no second email. A confirmed signup must give the same form response and send no confirmation email.

Use the body unsubscribe link and verify the address row is deleted. Repeat the link and verify `/alerts/unsubscribed/` again. Also verify the email provider's one-click unsubscribe, which sends POST to the same token URL with `List-Unsubscribe=One-Click`. This endpoint needs no website Origin header for deletion. Complete this check with a separate owner-controlled signup if the first row has already been deleted.

Before deployment, local mocked tests can run without any runtime secrets or network permission:

```sh
deno test supabase/functions/alerts/index_test.ts
```

## 5. Send an alert by hand

Use credential tooling to provide the existing `SUPABASE_SERVICE_ROLE_KEY` and sending-only `RESEND_API_KEY` in the local process environment, and set `SUPABASE_URL` to `https://vfozrzohrdrbohjqkghk.supabase.co`. Keep credentials out of the message file.

The local message file's first line is the subject. Add a blank line and a short body. Write each paragraph on one line, with blank lines between paragraphs. Use plain words, short hyphens, no emoji, and no exclamation points. Example file contents:

```text
Muster Out correction note

Read the correction described in the release notes before using the affected task.
```

This example is a format example; the owner supplies the actual correction and the page to read before sending.

The default dry run performs one count-only HEAD request, prints only the confirmed count, and does no database writes or email sends:

```sh
deno run --allow-env=SUPABASE_URL,SUPABASE_SERVICE_ROLE_KEY,RESEND_API_KEY --allow-net=vfozrzohrdrbohjqkghk.supabase.co,api.resend.com --allow-read=message.txt supabase/functions/alerts/send_alert.ts message.txt
```

Only the explicit send command writes token hashes and sends mail:

```sh
deno run --allow-env=SUPABASE_URL,SUPABASE_SERVICE_ROLE_KEY,RESEND_API_KEY --allow-net=vfozrzohrdrbohjqkghk.supabase.co,api.resend.com --allow-read=message.txt supabase/functions/alerts/send_alert.ts message.txt --send
```

Run one sender at a time. It reads confirmed IDs in pages of 500, rechecks consent, and sends batches of at most 100, with one recipient per message. It generates a fresh 32-byte unsubscribe token for each message, appends only its SHA-256 hash, and keeps the last eight hashes. A recent link remains valid until eight newer tokens replace its hash. Raw tokens exist only in the running process and the delivered email. There is no raw-token file or permanent contact sync.

Hashes are saved before Resend receives the batch, so unsubscribe links work even when delivery succeeds but the response is lost. `last_sent_at` is updated after accepted batch delivery. The script stops on a failed or uncertain batch and does not automatically retry. Review Resend delivery records before another run; a new run has fresh tokens and may duplicate mail already accepted. Deletion between the final consent check and Resend accepting a batch can allow one email already in flight.

The confirmation path reserves `last_sent_at` before sending, so failed attempts also wait ten minutes before another confirmation attempt. Rate receipts live in `ingest_rate`, under `alerts:ip:` and `alerts:email:` prefixes. They use a fixed `minute` anchor of `2000-01-01T00:00:00Z`; `n` is the next eligible Unix minute. Conditional writes protect each of three IP slots and the single email slot across workers. Rounding up can extend either wait by less than a minute. No cleanup process is required for correctness. These receipts do not contain a readable address and remain after signup deletion.
