import { createHandler, ENDPOINT, hash, SITE, token } from "./index.ts";
import { readMessage, sendAlert } from "./send_alert.ts";

const assert = (ok: unknown, message = "Assertion failed") => { if (!ok) throw new Error(message); };
const equal = (a: unknown, b: unknown) => assert(JSON.stringify(a) === JSON.stringify(b), `${JSON.stringify(a)} differs from ${JSON.stringify(b)}`);
type Stored = Record<string, unknown>;

// All HTTP is mocked, including PostgREST filters, conflict handling, and CAS.
function fixture() {
  const tables: Record<string, Stored[]> = { alert_signups: [], ingest_rate: [] };
  const calls: { url: URL; method: string; body: unknown; headers: Headers }[] = [];
  const values: Record<string, string> = { SUPABASE_URL: "https://database.invalid", SUPABASE_SERVICE_ROLE_KEY: "test-service-key", RESEND_API_KEY: "test-send-key", IP_HASH_SALT: "test-salt" };
  let now = Date.parse("2026-10-09T21:00:00Z"), seq = 0, mailStatus = 200, failDb = false;
  const matches = (row: Stored, params: URLSearchParams) => [...params].every(([key, filter]) => {
    if (["select", "order", "limit", "on_conflict"].includes(key)) return true;
    const dot = filter.indexOf("."), op = filter.slice(0, dot), value = filter.slice(dot + 1);
    if (op === "is") return value === "null" && row[key] === null;
    if (op === "gt") return String(row[key]) > value;
    if (op === "cs") return (row[key] as string[]).includes(value.slice(1, -1));
    if (op === "eq" && Array.isArray(row[key])) return `{${(row[key] as string[]).join(",")}}` === value;
    if (op === "eq") return String(row[key]) === value;
    throw new Error(`Unsupported mock filter: ${filter}`);
  });
  const reply = (body: unknown, status = 200, headers = {}) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", ...headers } });
  const net: typeof fetch = async (input, init) => {
    const url = new URL(String(input)), method = init?.method ?? "GET", headers = new Headers(init?.headers);
    const body = init?.body ? JSON.parse(String(init.body)) : undefined;
    calls.push({ url, method, body, headers });
    if (url.origin === "https://api.resend.com") {
      assert(url.pathname === "/emails" || url.pathname === "/emails/batch", "Never sync contacts");
      return reply(url.pathname.endsWith("batch") ? { data: (body as unknown[]).map(() => ({ id: "mail-id" })) } : { id: "mail-id" }, mailStatus);
    }
    assert(url.origin === "https://database.invalid", "Unexpected network destination");
    assert(headers.get("authorization") === "Bearer test-service-key");
    if (failDb) return reply({ error: "private database detail" }, 500);
    const table = url.pathname.split("/").pop() as string;
    const rows = tables[table];
    assert(rows, "Unknown table");
    if (method === "POST") {
      const entry = body as Stored;
      const duplicate = rows.some((r) => table === "alert_signups" ? r.email === entry.email : r.ip_hash === entry.ip_hash && r.minute === entry.minute);
      if (duplicate) { assert(headers.get("prefer")?.includes("ignore-duplicates")); return reply([]); }
      const row = table === "alert_signups" ? { id: String(++seq).padStart(8, "0"), created_at: new Date(now).toISOString(), confirmed_at: null, last_sent_at: null, confirm_hash: null, unsubscribe_hashes: [], ...entry } : { ...entry };
      rows.push(row);
      return reply([row]);
    }
    let found = rows.filter((row) => matches(row, url.searchParams));
    if (method === "HEAD") return new Response(null, { headers: { "content-range": `0-0/${found.length}` } });
    if (method === "PATCH") found.forEach((row) => Object.assign(row, body));
    if (method === "DELETE") tables[table] = rows.filter((row) => !found.includes(row));
    if (url.searchParams.has("order")) found = found.sort((a, b) => String(a.id).localeCompare(String(b.id)));
    if (url.searchParams.has("limit")) found = found.slice(0, Number(url.searchParams.get("limit")));
    const select = url.searchParams.get("select");
    return reply(select ? found.map((r) => Object.fromEntries(select.split(",").map((key) => [key, r[key]]))) : found);
  };
  const deps = { env: (name: string) => values[name], fetch: net, now: () => now };
  const handler = createHandler(deps);
  const subscribe = (email: unknown = "marine@example.com", website: unknown = "", ip = "192.0.2.1", origin = SITE) => handler(new Request(ENDPOINT, { method: "POST", headers: { origin, "x-forwarded-for": ip, "content-type": "application/json" }, body: JSON.stringify({ kind: "subscribe", email, website }) }));
  const mail = () => calls.filter((c) => c.url.origin === "https://api.resend.com");
  const links = () => {
    const body = mail().at(-1)?.body as { text: string };
    return { confirm: body.text.match(/\?confirm=([a-f0-9]{64})/)?.[1] as string, unsubscribe: body.text.match(/\?unsubscribe=([a-f0-9]{64})/)?.[1] as string };
  };
  return { tables, calls, values, deps, handler, subscribe, mail, links, advance: (ms: number) => { now += ms; }, mailStatus: (status: number) => { mailStatus = status; }, failDb: () => { failDb = true; } };
}

Deno.test("honeypot acknowledges without HTTP or stored data", async () => {
  const f = fixture();
  equal((await f.subscribe("bad", "https://bot.invalid")).status, 200);
  equal(f.calls.length, 0);
  equal(f.tables.alert_signups, []);
});

Deno.test("subscribe requires the exact website origin and safe JSON", async () => {
  const f = fixture();
  equal((await f.subscribe("marine@example.com", "", "192.0.2.1", "https://other.invalid")).status, 403);
  equal((await f.handler(new Request(ENDPOINT, { method: "POST", body: "null", headers: { origin: SITE } }))).status, 400);
  equal((await f.handler(new Request(ENDPOINT, { method: "POST", body: "{", headers: { origin: SITE } }))).status, 400);
  equal(f.calls.length, 0);
  const preflight = await f.handler(new Request(ENDPOINT, { method: "OPTIONS", headers: { origin: SITE } }));
  equal(preflight.status, 204);
  equal(preflight.headers.get("access-control-allow-origin"), SITE);
});

Deno.test("email validation and lowercase normalization", async () => {
  for (const email of ["a@b", "a@@example.com", "a b@example.com", "@example.com", "marine@", "m\n@example.com", "a".repeat(242) + "@example.com", null]) {
    const f = fixture();
    equal((await f.subscribe(email)).status, 400);
    equal(f.tables.alert_signups.length, 0);
    equal(f.mail().length, 0);
  }
  const f = fixture();
  equal((await f.subscribe("  Marine@Example.COM  ")).status, 200);
  equal(f.tables.alert_signups[0].email, "marine@example.com");
});

Deno.test("missing Resend key writes nothing", async () => {
  const f = fixture();
  delete f.values.RESEND_API_KEY;
  const response = await f.subscribe();
  equal(response.status, 503);
  equal(await response.json(), { ok: false, error: "not_configured" });
  equal(f.calls.length, 0);
});

Deno.test("salt is required, with the existing ingest salt supported", async () => {
  const f = fixture();
  delete f.values.IP_HASH_SALT;
  equal((await f.subscribe()).status, 503);
  equal(f.calls.length, 0);
  f.values.INGEST_SALT = "existing-salt";
  equal((await f.subscribe()).status, 200);
  equal(f.tables.alert_signups[0].ip_hash, (await hash("existing-salt192.0.2.1")).slice(0, 24));
});

Deno.test("tokens are 32 random bytes and only SHA-256 hashes are stored", async () => {
  const f = fixture();
  await f.subscribe();
  const links = f.links(), row = f.tables.alert_signups[0];
  assert(/^[a-f0-9]{64}$/.test(links.confirm));
  assert(/^[a-f0-9]{64}$/.test(links.unsubscribe));
  assert(links.confirm !== links.unsubscribe && token() !== token());
  equal(await hash("abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
  equal(row.confirm_hash, await hash(links.confirm));
  equal(row.unsubscribe_hashes, [await hash(links.unsubscribe)]);
  assert(!JSON.stringify(f.tables).includes(links.confirm));
  assert(!JSON.stringify(f.tables).includes(links.unsubscribe));
  assert(!JSON.stringify(f.tables).includes("192.0.2.1"));
  const body = f.mail()[0].body as { headers: Record<string, string>; text: string; html: string; to: string[] };
  equal(body.headers["List-Unsubscribe"], `<${ENDPOINT}?unsubscribe=${links.unsubscribe}>`);
  equal(body.headers["List-Unsubscribe-Post"], "List-Unsubscribe=One-Click");
  assert(body.html.includes(links.confirm) && body.text.includes("you can ignore it"));
  equal(body.to, ["marine@example.com"]);
});

Deno.test("subscribe limit persists across handler instances and resists concurrent requests", async () => {
  const f = fixture();
  const responses = await Promise.all(Array.from({ length: 10 }, (_, n) => f.subscribe(`marine${n}@example.com`)));
  equal(responses.filter((r) => r.status === 200).length, 3);
  equal(responses.filter((r) => r.status === 429).length, 7);
  equal(f.mail().length, 3);
  const next = createHandler(f.deps);
  const request = () => new Request(ENDPOINT, { method: "POST", headers: { origin: SITE, "x-forwarded-for": "192.0.2.1" }, body: JSON.stringify({ kind: "subscribe", email: "next@example.com" }) });
  f.advance(3599999);
  equal((await next(request())).status, 429);
  f.advance(1);
  equal((await next(request())).status, 200);
});

Deno.test("IP limit survives deleting the signup", async () => {
  const f = fixture();
  for (let n = 0; n < 3; n++) {
    await f.subscribe(`marine${n}@example.com`);
    await f.handler(new Request(`${ENDPOINT}?unsubscribe=${f.links().unsubscribe}`));
  }
  equal(f.tables.alert_signups.length, 0);
  equal((await f.subscribe()).status, 429);
});

Deno.test("deleting a signup does not reset the address confirmation cooldown", async () => {
  const f = fixture();
  await f.subscribe();
  await f.handler(new Request(`${ENDPOINT}?unsubscribe=${f.links().unsubscribe}`));
  equal(f.tables.alert_signups.length, 0);
  equal((await f.subscribe("marine@example.com", "", "192.0.2.2")).status, 200);
  equal(f.mail().length, 1);
  equal(f.tables.alert_signups.length, 0);
  f.advance(600000);
  await f.subscribe("marine@example.com", "", "192.0.2.3");
  equal(f.mail().length, 2);
});

Deno.test("one confirmation per address per ten minutes, including concurrent requests", async () => {
  const f = fixture();
  await Promise.all(Array.from({ length: 8 }, (_, n) => f.subscribe("marine@example.com", "", `192.0.2.${n}`)));
  equal(f.mail().length, 1);
  const first = f.links();
  f.advance(599999);
  equal((await f.subscribe("MARINE@example.com", "", "192.0.2.99")).status, 200);
  equal(f.mail().length, 1);
  f.advance(1);
  await f.subscribe("marine@example.com", "", "192.0.2.100");
  equal(f.mail().length, 2);
  equal((await f.handler(new Request(`${ENDPOINT}?confirm=${first.confirm}`))).headers.get("location"), `${SITE}/alerts/expired/`);
  assert((f.tables.alert_signups[0].unsubscribe_hashes as string[]).includes(await hash(first.unsubscribe)));
});

Deno.test("confirm consumes the token and confirmed subscribers get the same response without mail", async () => {
  const f = fixture();
  const initial = await (await f.subscribe()).json();
  const link = `${ENDPOINT}?confirm=${f.links().confirm}`;
  const response = await f.handler(new Request(link));
  equal(response.status, 303);
  equal(response.headers.get("location"), `${SITE}/alerts/confirmed/`);
  equal(f.tables.alert_signups[0].status, "confirmed");
  equal(f.tables.alert_signups[0].confirm_hash, null);
  assert(f.tables.alert_signups[0].confirmed_at);
  equal((await f.handler(new Request(link))).headers.get("location"), `${SITE}/alerts/expired/`);
  equal((await f.handler(new Request(`${ENDPOINT}?confirm=${token()}`))).headers.get("location"), `${SITE}/alerts/expired/`);
  f.advance(600001);
  equal(await (await f.subscribe()).json(), initial);
  equal(f.mail().length, 1);
});

Deno.test("unsubscribe accepts any recent hash, works with one-click POST, and is idempotent", async () => {
  for (const method of ["GET", "POST"]) {
    const f = fixture();
    await f.subscribe();
    const older = f.links().unsubscribe;
    f.advance(600000);
    await f.subscribe();
    const link = `${ENDPOINT}?unsubscribe=${older}`;
    for (let n = 0; n < 2; n++) {
      const response = await f.handler(new Request(link, { method, ...(method === "POST" ? { body: "List-Unsubscribe=One-Click" } : {}) }));
      equal(response.status, 303);
      equal(response.headers.get("location"), `${SITE}/alerts/unsubscribed/`);
      equal(f.tables.alert_signups.length, 0);
    }
    equal((await f.handler(new Request(`${ENDPOINT}?unsubscribe=${token()}`))).status, 303);
  }
});

Deno.test("delivery and database failures stay visible without exposing details", async () => {
  const f = fixture();
  f.mailStatus(500);
  equal((await f.subscribe()).status, 502);
  await f.subscribe();
  equal(f.mail().length, 1);
  const g = fixture();
  g.failDb();
  const response = await g.subscribe();
  equal(response.status, 503);
  equal(await response.json(), { ok: false, error: "unavailable" });
});

Deno.test("sender dry run prints only the confirmed count and performs no writes or mail", async () => {
  const f = fixture();
  f.tables.alert_signups.push({ id: "one", status: "confirmed", email: "private@example.com" }, { id: "two", status: "pending" });
  const printed: string[] = [];
  await sendAlert("A correction\n\nRead the corrected paragraph.\n", false, { ...f.deps, print: (line) => printed.push(line) });
  equal(printed, ["1"]);
  equal(f.calls.length, 1);
  equal(f.calls[0].method, "HEAD");
  equal(f.calls[0].url.searchParams.get("select"), "id");
});

Deno.test("sender batches separate addresses with private links, keeps recent links, and timestamps delivery", async () => {
  const f = fixture();
  const old = token();
  const oldHash = await hash(old);
  for (let n = 0; n < 101; n++) f.tables.alert_signups.push({ id: String(n).padStart(8, "0"), email: `marine${n}@example.com`, status: "confirmed", unsubscribe_hashes: [oldHash], last_sent_at: null });
  f.tables.alert_signups.push({ id: "pending", email: "pending@example.com", status: "pending", unsubscribe_hashes: [] });
  const printed: string[] = [];
  await sendAlert("A correction\n\nRead <the corrected paragraph>.\n", true, { ...f.deps, print: (line) => printed.push(line) });
  equal(f.mail().map((call) => (call.body as unknown[]).length), [100, 1]);
  const links = new Set<string>();
  for (const call of f.mail()) {
    equal(call.url.pathname, "/emails/batch");
    for (const message of call.body as { to: string[]; text: string; html: string; headers: Record<string, string> }[]) {
      equal(message.to.length, 1);
      assert(message.html.includes("&lt;the corrected paragraph&gt;"));
      const raw = message.text.match(/unsubscribe=([a-f0-9]{64})/)?.[1] as string;
      links.add(raw);
      const row = f.tables.alert_signups.find((r) => r.email === message.to[0]) as Stored;
      assert((row.unsubscribe_hashes as string[]).includes(await hash(raw)));
      assert((row.unsubscribe_hashes as string[]).includes(oldHash));
      equal(message.headers["List-Unsubscribe"], `<${ENDPOINT}?unsubscribe=${raw}>`);
      equal(message.headers["List-Unsubscribe-Post"], "List-Unsubscribe=One-Click");
      assert(row.last_sent_at);
      assert(!JSON.stringify(row).includes(raw));
    }
  }
  equal(links.size, 101);
  assert(!printed.join(" ").includes("@"));
  equal((await f.handler(new Request(`${ENDPOINT}?unsubscribe=${old}`))).status, 303);
  equal(f.tables.alert_signups.filter((r) => r.status === "confirmed").length, 0);
});

Deno.test("sender stops on failure and retains usable unsubscribe hashes", async () => {
  const f = fixture();
  f.tables.alert_signups.push({ id: "one", email: "marine@example.com", status: "confirmed", unsubscribe_hashes: [], last_sent_at: null });
  f.mailStatus(500);
  let failed = false;
  try { await sendAlert("A correction\n\nA short paragraph.\n", true, { ...f.deps, print: () => {} }); } catch { failed = true; }
  assert(failed);
  equal(f.tables.alert_signups[0].last_sent_at, null);
  equal((f.tables.alert_signups[0].unsubscribe_hashes as string[]).length, 1);
});

Deno.test("sender paginates beyond 500 and retains exactly eight recent hashes", async () => {
  const f = fixture();
  const prior = await Promise.all(Array.from({ length: 8 }, () => hash(token())));
  for (let n = 0; n < 501; n++) f.tables.alert_signups.push({ id: String(n).padStart(8, "0"), email: `marine${n}@example.com`, status: "confirmed", unsubscribe_hashes: [...prior], last_sent_at: null });
  await sendAlert("A correction\n\nA short paragraph.\n", true, { ...f.deps, print: () => {} });
  equal(f.mail().map((call) => (call.body as unknown[]).length), [100, 100, 100, 100, 100, 1]);
  const hashes = f.tables.alert_signups[0].unsubscribe_hashes as string[];
  equal(hashes.length, 8);
  assert(!hashes.includes(prior[0]) && hashes.includes(prior[1]));
});

Deno.test("sender requires a subject and body and rejects forbidden prose", () => {
  for (const text of ["No body", "Subject\nNo blank line", "Subject\n\nHello!", "Subject\n\nHello\u2014there", "Subject\n\n\ud83d\ude00"]) {
    let failed = false;
    try { readMessage(text); } catch { failed = true; }
    assert(failed);
  }
  equal(readMessage("Subject\n\nFirst paragraph.\n\nSecond paragraph.\n"), { subject: "Subject", paragraphs: ["First paragraph.", "Second paragraph."] });
});
