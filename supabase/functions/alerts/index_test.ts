import { createHandler, ENDPOINT, hash, SITE, ORIGINS, token, streamNames, sendSetup, sendTemplates, SETUP_CONSENT, freshLinks, database } from "./index.ts";
import { readMessage, sendAlert } from "./send_alert.ts";

const assert = (ok: unknown, message = "Assertion failed") => { if (!ok) throw new Error(message); };
const equal = (a: unknown, b: unknown) => assert(JSON.stringify(a) === JSON.stringify(b), `${JSON.stringify(a)} differs from ${JSON.stringify(b)}`);
// A deliberate action after opening an email review page.
const postLink = (url: string) => new Request(url, { method: "POST", body: url.includes("unsubscribe=") ? "List-Unsubscribe=One-Click" : "" });
type Stored = Record<string, unknown>;

// All HTTP is mocked, including PostgREST filters, conflict handling, and CAS.
export function fixture() {
  const tables: Record<string, Stored[]> = { alert_signups: [], ingest_rate: [], suggestions: [], email_delivery_receipts: [], email_setup_claims: [], digest_feed_highwater: [] };
  const calls: { url: URL; method: string; body: unknown; headers: Headers }[] = [];
  const values: Record<string, string> = { SUPABASE_URL: "https://database.invalid", SUPABASE_SERVICE_ROLE_KEY: "test-service-key", RESEND_API_KEY: "test-send-key", IP_HASH_SALT: "test-salt" };
  let now = Date.parse("2026-10-09T21:00:00Z"), seq = 0, mailStatus = 200, templateStatus = 200, templateError: unknown = {}, failDb = false, throwMail = false, badMail = false;
  const matches = (row: Stored, params: URLSearchParams) => [...params].every(([key, filter]) => {
    if (["select", "order", "limit", "on_conflict"].includes(key)) return true;
    if (key === "or") {
      const terms = filter.slice(1, -1).split(",");
      return terms.some(term => {
        const match = /^(unsubscribe_hashes|setup_token_hashes)\.cs\.\{([a-f0-9]{64})\}$/.exec(term);
        assert(match, "Unsupported mock OR filter");
        return ((row[match![1]] ?? []) as string[]).includes(match![2]);
      });
    }
    const dot = filter.indexOf("."), op = filter.slice(0, dot), value = filter.slice(dot + 1);
    if (op === "is") return value === "null" && row[key] === null;
    if (op === "lte") return row[key] != null && String(row[key]) <= value;
    if (op === "gte") return row[key] != null && String(row[key]) >= value;
    if (op === "gt") return String(row[key]) > value;
    if (op === "in") return value.slice(1,-1).split(",").includes(String(row[key]));
    if (op === "cs") return ((row[key] ?? []) as string[]).includes(value.slice(1, -1));
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
      if (throwMail) throw new Error("Network interrupted");
      if (badMail) return reply({ data: [] });
      if ((body as any)?.template && templateStatus !== 200) return reply(templateError, templateStatus);
      return reply(url.pathname.endsWith("batch") ? { data: (body as unknown[]).map(() => ({ id: "mail-id" })) } : { id: "mail-id" }, (body as any)?.template && templateStatus !== 200 ? templateStatus : mailStatus);
    }
    assert(url.origin === "https://database.invalid", "Unexpected network destination");
    assert(headers.get("authorization") === "Bearer test-service-key");
    if (failDb) return reply({ error: "private database detail" }, 500);
    if (url.pathname === "/rest/v1/rpc/digest_feed_accept") {
      const p = body as { p_seq: number; p_sha256: string };
      const saved = tables.digest_feed_highwater[0];
      if (saved && p.p_seq < Number(saved.seq)) return reply({ accepted: false, decision: "rollback" });
      if (saved && p.p_seq === saved.seq) return reply({ accepted: p.p_sha256 === saved.sha256, decision: p.p_sha256 === saved.sha256 ? "retry" : "replacement" });
      tables.digest_feed_highwater[0] = { seq: p.p_seq, sha256: p.p_sha256 };
      return reply({ accepted: true, decision: "advanced" });
    }
    if (url.pathname === "/rest/v1/rpc/email_delivery_gate") {
      const p = body as any, receipts = tables.email_delivery_receipts;
      const prior = receipts.find(r => r.campaign === p.p_campaign && r.recipient_hash === p.p_recipient_hash);
      let decision = "eligible";
      if (prior) decision = ["reserved","unknown","failed"].includes(String(prior.state)) ? "blocked" : p.p_stream === "weekly" || prior.content_hash === p.p_content_hash ? "duplicate" : "changed";
      else if (p.p_stream !== "weekly" && receipts.some(r => r.campaign === p.p_campaign && r.content_hash !== p.p_content_hash)) decision = "changed";
      else if (!["corrections", "setup"].includes(p.p_stream)) {
        const d = new Date(now); d.setUTCHours(0,0,0,0); d.setUTCDate(d.getUTCDate() - (d.getUTCDay()+6)%7);
        const week = d.getTime(), month = Date.UTC(new Date(now).getUTCFullYear(),new Date(now).getUTCMonth(),1);
        const used = receipts.filter(r => r.recipient_hash === p.p_recipient_hash && ["monthly","weekly","lessons"].includes(String(r.stream)) && ["reserved","accepted","unknown"].includes(String(r.state)));
        if (used.filter(r=>Date.parse(String(r.created_at))>=month).length>=4) decision="monthly_cap";
        else if (used.some(r=>Date.parse(String(r.created_at))>=week)) decision="weekly_cap";
      }
      if (p.p_stream === "setup") {
        const claims = tables.email_setup_claims, old = claims.find(r => r.campaign === p.p_campaign && r.recipient_hash === p.p_recipient_hash);
        const step = Number(p.p_campaign[6]);
        assert(/^setup-[123]:v1$/.test(p.p_campaign), "Setup IDs cannot change to evade the lifetime cap");
        if (old) decision = old.content_hash !== p.p_content_hash ? "changed" : ["reserved", "unknown", "failed"].includes(String(old.state)) ? "blocked" : "duplicate";
        else if (claims.some(r => r.campaign === p.p_campaign && r.content_hash !== p.p_content_hash)) decision = "changed";
        else if (claims.filter(r => r.recipient_hash === p.p_recipient_hash).length >= 3) decision = "lifetime_cap";
        else if (step > 1 && !claims.some(r => r.recipient_hash === p.p_recipient_hash && r.campaign === `setup-${step-1}:v1` && r.state === "accepted" && Date.parse(String(r.created_at)) <= now - (step === 2 ? 20 : 24)*3600000)) decision = "sequence_wait";
        if (decision === "eligible" && !p.p_dry) claims.push({campaign: p.p_campaign, recipient_hash: p.p_recipient_hash, content_hash: p.p_content_hash, state: "reserved", created_at: new Date(now).toISOString()});
      }
      if(decision==="eligible"&&!p.p_dry){receipts.push({campaign:p.p_campaign,recipient_hash:p.p_recipient_hash,content_hash:p.p_content_hash,stream:p.p_stream,state:"reserved",created_at:new Date(now).toISOString(),updated_at:new Date(now).toISOString()});decision="claimed";}
      return reply({decision});
    }
    const table = url.pathname.split("/").pop() as string;
    const rows = tables[table];
    assert(rows, "Unknown table");
    if (method === "POST") {
      const entry = body as Stored;
      const duplicate = rows.some((r) => table === "alert_signups" ? r.email === entry.email : table === "ingest_rate" ? r.ip_hash === entry.ip_hash && r.minute === entry.minute : table === "email_delivery_receipts" ? r.campaign === entry.campaign && r.recipient_hash === entry.recipient_hash : false);
      if (duplicate) { assert(headers.get("prefer")?.includes("ignore-duplicates")); return reply([]); }
      const row = table === "alert_signups" ? { id: String(++seq).padStart(8, "0"), created_at: new Date(now).toISOString(), confirmed_at: null, last_sent_at: null, confirm_hash: null, unsubscribe_hashes: [], setup_token_hashes: [], weekly: false, monthly: true, corrections: false, lessons: false, ...entry } : { id: String(++seq), ...entry };
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
    const body = mail().findLast(c => (c.body as any)?.template?.id === "confirm-subscription" || (c.body as any)?.text?.includes("?confirm="))?.body as any;
    const content = body.template ? JSON.stringify(body.template.variables) : body.text;
    return { confirm: content.match(/\?confirm=([a-f0-9]{64})/)?.[1] as string, unsubscribe: content.match(/\?unsubscribe=([a-f0-9]{64})/)?.[1] as string, prefs: content.match(/\?prefs=([a-f0-9]{64})/)?.[1] as string };
  };
  return { tables, calls, values, deps, handler, subscribe, mail, links, advance: (ms: number) => { now += ms; }, mailStatus: (status: number) => { mailStatus = status; }, templateStatus: (status: number, error: unknown = {}) => { templateStatus = status; templateError = error; }, throwMail: () => { throwMail = true; }, badMail: () => { badMail = true; }, failDb: () => { failDb = true; } };
}

Deno.test("honeypot acknowledges without HTTP or stored data", async () => {
  const f = fixture();
  equal((await f.subscribe("bad", "https://bot.invalid")).status, 200);
  equal(f.calls.length, 0);
  equal(f.tables.alert_signups, []);
});

Deno.test("subscribe requires an allowed origin and safe JSON", async () => {
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
  equal(row.confirm_hash, await hash("campaign-streams:v2:" + links.confirm));
  equal(row.unsubscribe_hashes, [await hash(links.unsubscribe), await hash(links.prefs)]);
  assert(!JSON.stringify(f.tables).includes(links.confirm));
  assert(!JSON.stringify(f.tables).includes(links.unsubscribe));
  assert(!JSON.stringify(f.tables).includes("192.0.2.1"));
  const body = f.mail()[0].body as { headers: Record<string, string>; text: string; html: string; to: string[] };
  equal(body.headers["List-Unsubscribe"], `<${ENDPOINT}?unsubscribe=${links.unsubscribe}>`);
  equal(body.headers["List-Unsubscribe-Post"], "List-Unsubscribe=One-Click");
  assert(JSON.stringify(body).includes(links.confirm));
  assert((body as any).template.id === "confirm-subscription");
  assert(!body.html && !body.text);
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
    await f.handler(postLink(`${ENDPOINT}?unsubscribe=${f.links().unsubscribe}`));
  }
  equal(f.tables.alert_signups.length, 0);
  equal((await f.subscribe()).status, 429);
});

Deno.test("deleting a signup does not reset the address confirmation cooldown", async () => {
  const f = fixture();
  await f.subscribe();
  await f.handler(postLink(`${ENDPOINT}?unsubscribe=${f.links().unsubscribe}`));
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
  equal((await f.handler(postLink(`${ENDPOINT}?confirm=${first.confirm}`))).headers.get("location"), `${SITE}/alerts/expired/`);
  assert((f.tables.alert_signups[0].unsubscribe_hashes as string[]).includes(await hash(first.unsubscribe)));
});

Deno.test("daily confirmation cap survives deletion and rotating IPs with the same success response", async () => {
  const f = fixture();
  for (let n = 0; n < 4; n++) {
    equal(await (await f.subscribe("MARINE@example.com", "", `192.0.2.${n}`)).json(), { ok: true });
    if (n < 3) await f.handler(postLink(`${ENDPOINT}?unsubscribe=${f.links().unsubscribe}`));
    f.advance(600000);
  }
  equal(f.mail().length, 3); equal(f.tables.alert_signups.length, 0);
  f.advance(86400000);
  equal((await f.subscribe()).status, 200); equal(f.mail().length, 4);
});

Deno.test("weekly confirmation cap survives deletion after daily slots reopen", async () => {
  const f = fixture();
  for (let n = 0; n < 6; n++) {
    if (n === 3) f.advance(86400000);
    equal(await (await f.subscribe("marine@example.com", "", `192.0.2.${n}`)).json(), { ok: true });
    if (n < 5) await f.handler(postLink(`${ENDPOINT}?unsubscribe=${f.links().unsubscribe}`));
    f.advance(600000);
  }
  equal(f.mail().length, 5); equal(f.tables.alert_signups.length, 0);
  f.advance(7 * 86400000);
  equal((await f.subscribe()).status, 200); equal(f.mail().length, 6);
});

Deno.test("confirmation expiry applies to all token formats at seven days; private links stay valid", async () => {
  for (const format of ["current", "platform", "legacy"]) for (const age of [7 * 86400000, 7 * 86400000 + 1]) {
    const f = fixture(); await f.subscribe(); const links = f.links(), r = f.tables.alert_signups[0];
    const { PLATFORM_SCOPE } = await import("./index.ts");
    if (format !== "current") r.confirm_hash = await hash(format === "platform" ? PLATFORM_SCOPE + ":" + links.confirm : links.confirm);
    f.advance(age);
    const response = await f.handler(postLink(`${ENDPOINT}?confirm=${links.confirm}`));
    equal(response.headers.get("location"), `${SITE}/alerts/${age > 7 * 86400000 ? "expired" : "confirmed"}/`);
    equal(f.mail().length, age > 7 * 86400000 ? 1 : 2);
    f.advance(365 * 86400000);
    equal((await f.handler(new Request(`${ENDPOINT}?prefs=${links.prefs}`))).status, 200);
    await f.handler(postLink(`${ENDPOINT}?unsubscribe=${links.unsubscribe}`)); equal(f.tables.alert_signups.length, 0);
  }
  const f = fixture(); await f.subscribe(); f.tables.alert_signups[0].last_sent_at = null;
  equal((await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`))).headers.get("location"), `${SITE}/alerts/expired/`);
  equal(f.mail().length, 1);
});

Deno.test("Content-Length rejects oversized alerts and preferences before body reads; chunked checks remain", async () => {
  for (const [url, cap] of [[ENDPOINT, 8192], [`${ENDPOINT}?prefs=${token()}`, 1024]] as const) {
    const f = fixture();
    const req = new Request(url, { method: "POST", headers: { origin: SITE, "content-length": String(cap + 1) }, body: "{}" });
    req.text = async () => { throw new Error("Body must not be read"); };
    equal((await f.handler(req)).status, 413); equal(f.calls.length, 0);
  }
  const f = fixture();
  equal((await f.handler(new Request(ENDPOINT, { method: "POST", headers: { origin: SITE }, body: " ".repeat(8193) }))).status, 413);
  await f.subscribe();
  equal((await f.handler(new Request(`${ENDPOINT}?prefs=${f.links().prefs}`, { method: "POST", headers: { origin: SITE }, body: " ".repeat(1025) }))).status, 413);
});

Deno.test("confirm consumes the token and confirmed subscribers get the same response without mail", async () => {
  const f = fixture();
  const initial = await (await f.subscribe()).json();
  const link = `${ENDPOINT}?confirm=${f.links().confirm}`;
  const response = await f.handler(postLink(link));
  equal(response.status, 303);
  equal(response.headers.get("location"), `${SITE}/alerts/confirmed/`);
  equal(f.tables.alert_signups[0].status, "confirmed");
  equal(f.tables.alert_signups[0].confirm_hash, "consent:campaign-streams:v2");
  assert(f.tables.alert_signups[0].confirmed_at);
  equal((await f.handler(postLink(link))).headers.get("location"), `${SITE}/alerts/expired/`);
  equal((await f.handler(postLink(`${ENDPOINT}?confirm=${token()}`))).headers.get("location"), `${SITE}/alerts/expired/`);
  f.advance(600001);
  equal(await (await f.subscribe()).json(), initial);
  equal(f.mail().length, 2);
});

Deno.test("unsubscribe GET is passive; RFC 8058 POST accepts recent hashes and is idempotent", async () => {
  const f = fixture(); await f.subscribe();
  const older = f.links().unsubscribe;
  f.advance(600000); await f.subscribe();
  const link = `${ENDPOINT}?unsubscribe=${older}`;
  const before = JSON.stringify(f.tables), calls = f.calls.length;
  const preview = await f.handler(new Request(link));
  equal(preview.status, 303);
  equal(preview.headers.get("location"), `${SITE}/alerts/action/#unsubscribe=${older}`);
  equal(JSON.stringify(f.tables), before); equal(f.calls.length, calls);
  for (let n = 0; n < 2; n++) {
    const response = await f.handler(postLink(link));
    equal(response.status, 200); equal(response.headers.get("location"), null);
    equal(f.tables.alert_signups.length, 0);
  }
  equal((await f.handler(postLink(`${ENDPOINT}?unsubscribe=${token()}`))).status, 200);
});

Deno.test("delivery and database failures stay visible without exposing details", async () => {
  const f = fixture();
  f.mailStatus(500);
  equal((await f.subscribe()).status, 502);
  await f.subscribe();
  equal(f.mail().length, 1);
  equal(f.tables.email_delivery_receipts[0].state, "unknown");
  const g = fixture();
  g.failDb();
  const response = await g.subscribe();
  equal(response.status, 503);
  equal(await response.json(), { ok: false, error: "unavailable" });
});

const correction = (campaign = "correction-v1", copy = "Read the corrected paragraph.") => JSON.stringify({ template: "correction-alert", campaign, variables: { WHAT_CHANGED: copy, WHO_IS_AFFECTED: "Marines using the planner.", WHAT_TO_DO: "Read the correction.", VERSION: "0.1.4" } });
const row = (id: string, fields: Stored = {}): Stored => ({ id, email: `${id}@example.com`, status: "confirmed", confirm_hash: null, unsubscribe_hashes: [], last_sent_at: null, weekly: false, monthly: true, corrections: true, lessons: false, ...fields });
const monthly = (campaign="monthly-2026-10") => JSON.stringify({template:"monthly",campaign,variables:{SHIPPED:"A reviewed release shipped.",NEXT:"The next release is under review.",AI_MOVE:"Ask Claude to explain an unfamiliar term.",QUESTION:"Which term needs a clearer explanation?"}});
Deno.test("sender dry run reports eligible and skipped counts without link writes or mail",async()=>{
 const f=fixture();f.tables.alert_signups.push(row("one"),row("two",{status:"pending"}),row("three",{monthly:false}));const printed:string[]=[];
 await sendAlert(monthly(),false,{...f.deps,print:line=>printed.push(line)});
 equal(JSON.parse(printed[0]),{dry:true,recipients:1,eligible:1,accepted:0,skipped:0,reasons:{}});
 equal(f.tables.email_delivery_receipts.length,0);equal(f.mail().length,0);equal(f.tables.alert_signups[0].unsubscribe_hashes,[]);
});
Deno.test("sender batches private template links and deduplicates per address after 24 hours", async () => {
  const f = fixture(), old = token(), oldHash = await hash(old);
  for (let n = 0; n < 101; n++) f.tables.alert_signups.push(row(String(n).padStart(8, "0"), { unsubscribe_hashes: [oldHash] }));
  f.tables.alert_signups.push(row("pending", { status: "pending" }));
  const printed: string[] = [];
  await sendAlert(correction(), true, { ...f.deps, print: line => printed.push(line) });
  equal(f.mail().map(c => (c.body as unknown[]).length), [100, 1]);
  const tokens = new Set<string>();
  for (const call of f.mail()) {
    equal(call.url.pathname, "/emails/batch");
    assert(call.headers.get("idempotency-key"));
    for (const message of call.body as any[]) {
      equal(message.to.length, 1);
      equal(message.template.id, "correction-alert");
      assert(!message.html && !message.text);
      const vars = message.template.variables;
      assert(vars.ALERT_UNSUBSCRIBE_URL && vars.PREFS_URL && !vars.RESEND_UNSUBSCRIBE_URL && !vars.UNSUBSCRIBE_URL);
      const unsub = new URL(vars.ALERT_UNSUBSCRIBE_URL).searchParams.get("unsubscribe") as string;
      const prefs = new URL(vars.PREFS_URL).searchParams.get("prefs") as string;
      tokens.add(unsub);tokens.add(prefs);
      assert(unsub !== prefs);
      const r = f.tables.alert_signups.find(r => r.email === message.to[0]) as Stored;
      for (const digest of [oldHash, await hash(unsub), await hash(prefs)]) assert((r.unsubscribe_hashes as string[]).includes(digest));
      equal(message.headers["List-Unsubscribe"], `<${vars.ALERT_UNSUBSCRIBE_URL}>`);
      equal(message.headers["List-Unsubscribe-Post"], "List-Unsubscribe=One-Click");
      assert(r.last_sent_at);
      assert(!JSON.stringify(f.tables).includes(unsub) && !JSON.stringify(f.tables).includes(prefs));
    }
  }
  equal(tokens.size, 202);
  assert(!JSON.stringify(f.tables.email_delivery_receipts).includes("@"));
  f.advance(2 * 86400000);
  await sendAlert(correction(), true, { ...f.deps, print: line => printed.push(line) });
  equal(f.mail().length, 2);
  assert(!printed.join(" ").includes("@"));
});
Deno.test("sender retains visible failures and usable links without automatic retries", async () => {
  for (const uncertain of [false, true]) {
    const f = fixture();f.tables.alert_signups.push(row("one"));
    if (uncertain) f.throwMail(); else f.mailStatus(422);
    let failed = false;
    try { await sendAlert(correction(), true, { ...f.deps, print: () => {} }); } catch { failed = true; }
    assert(failed);
    equal(f.tables.alert_signups[0].last_sent_at, null);
    equal((f.tables.alert_signups[0].unsubscribe_hashes as string[]).length, 2);
    equal(f.tables.email_delivery_receipts[0].state, uncertain ? "unknown" : "failed");
    const printed:string[]=[];await sendAlert(correction(),true,{...f.deps,print:line=>printed.push(line)});equal(JSON.parse(printed[0]).reasons.blocked,1);equal(f.mail().length,1);
  }
});
Deno.test("sender paginates beyond 500 and retains exactly eight recent hashes", async () => {
  const f = fixture(), prior = await Promise.all(Array.from({ length: 8 }, () => hash(token())));
  for (let n = 0; n < 501; n++) f.tables.alert_signups.push(row(String(n).padStart(8, "0"), { unsubscribe_hashes: [...prior] }));
  await sendAlert(correction(), true, { ...f.deps, print: () => {} });
  equal(f.mail().map(call => (call.body as unknown[]).length), [100,100,100,100,100,1]);
  const hashes=f.tables.alert_signups[0].unsubscribe_hashes as string[];
  equal(hashes.length,8);assert(!hashes.includes(prior[0]) && hashes.includes(prior[2]));
});
Deno.test("sender requires reviewed JSON and rejects reserved variables or unknown aliases", () => {
  for (const raw of ["No body", "{}", "null", correction("campaign", "Hello!"), correction("campaign", "Hello\u2014there"), correction("campaign", "<b>HTML</b>"), JSON.stringify({template:"feedback-request",variables:{}}), JSON.stringify({template:["feedback-request"],campaign:"id",variables:{}}), JSON.stringify({template:"welcome",campaign:"id",variables:{}}), JSON.stringify({template:"feedback-request",campaign:"id",variables:{UNSUBSCRIBE_URL:"https://example.com"}})]) {
    let failed=false;try {readMessage(raw);}catch {failed=true;}assert(failed);
  }
  equal(readMessage(correction()).template,"correction-alert");
});
Deno.test("manual templates filter exactly their stream and refuse retired aliases and empty Monthly",async()=>{
 for(const alias of ["monthly","lesson-launch","correction-alert"]){
  const f=fixture();f.tables.alert_signups.push(row("on",{lessons:true}),row("off",{monthly:false,lessons:false,corrections:false}),row("pending",{status:"pending",lessons:true}));
  const raw=alias==="monthly"?monthly():alias==="correction-alert"?correction():JSON.stringify({template:alias,campaign:"lesson-review",variables:{LESSON_TITLE:"Reviewed lesson",LESSON_PROMISE:"Practice one new skill.",LESSON_URL:"https://warfarecommand.com/reviewed-lesson/"}});
  await sendAlert(raw,true,{...f.deps,print:()=>{}});equal((f.mail()[0].body as any[]).map(m=>m.to[0]),["on@example.com"]);
 }
 for(const raw of [JSON.stringify({template:"monthly",campaign:"empty",variables:{SHIPPED:"",NEXT:"",AI_MOVE:"",QUESTION:""}}),JSON.stringify({template:"monthly",campaign:"empty",variables:{SHIPPED:"   ",NEXT:"Next.",AI_MOVE:"A move.",QUESTION:"A question?"}}),...['monthly-update','release-notes','feedback-request'].map(template=>JSON.stringify({template,campaign:"retired",variables:{}}))]){let failed=false;try{readMessage(raw);}catch{failed=true;}assert(failed);}
});
Deno.test("changing content under the same manual campaign is reported without sending",async()=>{
 const f=fixture();f.tables.alert_signups.push(row("one"));await sendAlert(correction(),true,{...f.deps,print:()=>{}});const printed:string[]=[];
 await sendAlert(correction("correction-v1","Changed copy."),true,{...f.deps,print:line=>printed.push(line)});equal(JSON.parse(printed[0]).reasons.changed,1);equal(f.mail().length,1);
});

const request = (body: unknown, origin = SITE) => new Request(ENDPOINT, { method: "POST", headers: { origin, "x-forwarded-for": "192.0.2.10", "content-type": "application/json" }, body: JSON.stringify(body) });

Deno.test("both origins receive matching CORS and subscribe stores only a valid optional source", async () => {
  for (const origin of ORIGINS) {
    const f = fixture();
    const preflight = await f.handler(new Request(ENDPOINT, { method: "OPTIONS", headers: { origin } }));
    equal(preflight.status, 204);
    equal(preflight.headers.get("access-control-allow-origin"), origin);
    equal(preflight.headers.get("vary"), "Origin");
    const response = await f.handler(request({ kind: "subscribe", email: "marine@example.com", website: "", source: "register" }, origin));
    equal(response.status, 200);
    equal(response.headers.get("access-control-allow-origin"), origin);
    equal(f.tables.alert_signups[0].source, "register");
  }
  for (const source of ["hub", "musterout", "register", "ai101"]) {
    const f = fixture();
    equal((await f.handler(request({ kind: "subscribe", email: "marine@example.com", source }))).status, 200);
    equal(f.tables.alert_signups[0].source, source);
  }
  for (const source of ["private", null, {}, 2]) {
    const f = fixture();
    equal((await f.handler(request({ kind: "subscribe", email: "marine@example.com", source }))).status, 400);
    equal(f.calls.length, 0);
  }
  const f = fixture();
  equal((await f.handler(new Request(ENDPOINT, { method: "OPTIONS", headers: { origin: "https://warfarecommand.com.evil.invalid" } }))).status, 403);
});

Deno.test("suggest stores trimmed text and optional email and escapes the branded notice", async () => {
  for (const origin of ORIGINS) {
    const f = fixture();
    const idea = '<script>alert("idea")</script> & another idea';
    const response = await f.handler(request({ kind: "suggest", idea: "  " + idea + "  ", email: " Reply@Example.COM ", website: "", name: "Never store extra fields" }, origin));
    equal(response.status, 200);
    equal(await response.json(), { ok: true });
    const row = f.tables.suggestions[0];
    equal(row.idea, idea);
    equal(row.email, "reply@example.com");
    equal(row.ip_hash, (await hash("test-salt192.0.2.10")).slice(0, 24));
    assert(!("name" in row));
    const message = f.mail()[0].body as { to: string[]; html: string; text: string };
    equal(message.to, ["feedback@warfarecommand.com"]);
    assert(message.html.includes("Warfare Command") && message.html.includes("MUSTER OUT"));
    assert(message.html.includes("&lt;script&gt;alert(&quot;idea&quot;)&lt;/script&gt; &amp; another idea"));
    assert(!message.html.includes(idea) && message.text.includes(idea));
    assert(!message.html.includes("Unsubscribe") && !message.text.includes("undefined"));
    equal(f.tables.alert_signups.length, 0);
  }
  const f = fixture();
  equal((await f.handler(request({ kind: "suggest", idea: "A calendar for appointments" }))).status, 200);
  equal(f.tables.suggestions[0].email, null);
});

Deno.test("suggest boundaries, malformed email, honeypot and disallowed origin", async () => {
  for (const body of [
    { idea: "x".repeat(9) }, { idea: "x".repeat(1001) }, { idea: null },
    { idea: "A useful idea", email: "not an address" }, { idea: "A useful idea", email: null },
    { idea: "A useful idea", email: {} },
  ]) {
    const f = fixture();
    const response = await f.handler(request({ kind: "suggest", ...body }));
    equal(response.status, 400);
    equal(await response.json(), { ok: false, error: "bad_input" });
    equal(f.calls.length, 0);
  }
  for (const length of [10, 1000]) {
    const f = fixture();
    equal((await f.handler(request({ kind: "suggest", idea: "x".repeat(length), email: "" }))).status, 200);
  }
  const f = fixture();
  equal((await f.handler(request({ kind: "suggest", idea: "bad", website: "bot" }))).status, 200);
  equal(f.calls.length, 0);
  equal((await f.handler(request({ kind: "suggest", idea: "A useful tool idea" }, "https://evil.invalid"))).status, 403);
  equal(f.calls.length, 0);
});

Deno.test("suggest reserves three durable slots per IP across concurrent handlers", async () => {
  const f = fixture();
  const responses = await Promise.all(Array.from({ length: 8 }, () => createHandler(f.deps)(request({ kind: "suggest", idea: "A useful tool idea" }))));
  equal(responses.filter(r => r.status === 200).length, 3);
  equal(responses.filter(r => r.status === 429).length, 5);
  equal(f.tables.suggestions.length, 3);
  equal(f.mail().length, 3);
  // Suggestions do not consume the subscribe allowance.
  equal((await f.handler(request({ kind: "subscribe", email: "marine@example.com" }))).status, 200);
  f.advance(3600000);
  equal((await f.handler(request({ kind: "suggest", idea: "A useful tool idea" }))).status, 200);
});

Deno.test("suggest configuration, database and delivery failures remain visible", async () => {
  const f = fixture();
  delete f.values.RESEND_API_KEY;
  equal((await f.handler(request({ kind: "suggest", idea: "A useful tool idea" }))).status, 503);
  equal(f.calls.length, 0);
  const g = fixture();
  g.failDb();
  equal((await g.handler(request({ kind: "suggest", idea: "A useful tool idea" }))).status, 503);
  equal(g.mail().length, 0);
  const h = fixture();
  h.mailStatus(500);
  equal((await h.handler(request({ kind: "suggest", idea: "A useful tool idea" }))).status, 502);
  equal(h.tables.suggestions.length, 1);
});

Deno.test("source-specific stream defaults require the new confirmation; old links keep earlier flags",async()=>{
 for(const source of ["hub","ai101","musterout","register",undefined]){
  const f=fixture();await f.handler(request({kind:"subscribe",email:"marine@example.com",source}));const vars=(f.mail()[0].body as any).template.variables,r=f.tables.alert_signups[0];
  equal(r.corrections,source==="musterout"||source==="register");equal(r.monthly,true);equal(r.weekly,false);equal(r.lessons,source==="ai101");
  assert(vars.CONSENT_SCOPE.includes("Warfare Command Monthly"));equal(vars.CONSENT_SCOPE.includes("Muster Out corrections"),r.corrections);equal(vars.CONSENT_SCOPE.includes("New lessons"),r.lessons);
  await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`));equal(r.confirm_hash,"consent:campaign-streams:v2");
  const before=JSON.stringify(f.tables.alert_signups);await f.handler(request({kind:"subscribe",email:"marine@example.com",source:"ai101"}));equal(JSON.stringify(f.tables.alert_signups),before);
 }
 for(const platform of [false,true]){
  const f=fixture(),raw=token();const {PLATFORM_SCOPE}=await import("./index.ts");f.tables.alert_signups.push(row("old",{status:"pending",monthly:false,corrections:true,lessons:false,last_sent_at:new Date(f.deps.now()).toISOString(),confirm_hash:await hash(platform?PLATFORM_SCOPE+":"+raw:raw)}));
  await f.handler(postLink(`${ENDPOINT}?confirm=${raw}`));equal(f.tables.alert_signups[0].status,"confirmed");equal(f.tables.alert_signups[0].monthly,false);equal(f.tables.alert_signups[0].lessons,false);equal(f.tables.alert_signups[0].corrections,true);
 }
});

Deno.test("www preflight and signup use the supported origin", async () => {
  const f = fixture(), origin = "https://www.warfarecommand.com";
  assert(ORIGINS.includes(origin));
  const preflight = await f.handler(new Request(ENDPOINT, { method: "OPTIONS", headers: { origin } }));
  equal(preflight.status, 204); equal(preflight.headers.get("access-control-allow-origin"), origin);
  equal((await f.handler(request({ kind: "subscribe", email: "marine@example.com", source: "hub" }, origin))).status, 200);
});

Deno.test("confirmation falls back only for explicit template rejection", async () => {
  for (const [status, message] of [[404,"Template not found"], [400,"Template is not published"], [422,"Invalid template variables"], [422,"Missing required template variables"]] as const) {
    const f = fixture(); f.templateStatus(status, { name: "validation_error", message });
    equal((await f.subscribe()).status, 200); equal(f.mail().length, 2);
    const [first, fallback] = f.mail();
    equal((first.body as any).template.id, "confirm-subscription");
    assert((fallback.body as any).html.includes("Confirm your email") && (fallback.body as any).text.includes("Warfare Command Monthly"));
    assert(!(fallback.body as any).template);
    assert(first.headers.get("idempotency-key") !== fallback.headers.get("idempotency-key"));
    equal(f.tables.email_delivery_receipts[0].state, "accepted");
  }
});
Deno.test("server, quota, timeout and conflict responses remain uncertain without fallback", async () => {
  for (const status of [500, 503, 429, 408, 409]) {
    const f = fixture(); f.templateStatus(status, { message: "Template not found" });
    equal((await f.subscribe()).status, 502); equal(f.mail().length, 1);
    equal(f.tables.email_delivery_receipts[0].state, "unknown");
  }
});
Deno.test("unrelated or malformed 4xx rejection never triggers fallback", async () => {
  for (const [status, error] of [[401,{message:"Missing API key"}], [401,{message:"Missing API key for template send"}], [404,{message:"Endpoint not found"}], [422,{message:"Invalid from field"}], [400,{message:"Invalid template request"}], [422,"not JSON error data"]] as const) {
    const f = fixture(); f.templateStatus(status, error);
    equal((await f.subscribe()).status, 502); equal(f.mail().length, 1);
    equal(f.tables.email_delivery_receipts[0].state, "failed");
  }
});
Deno.test("network or malformed success records an uncertain confirmation with no second send", async () => {
  for (const mode of ["network", "malformed"]) {
    const f = fixture(); if (mode === "network") f.throwMail(); else f.badMail();
    equal((await f.subscribe()).status, 503); equal(f.mail().length, 1);
    equal(f.tables.email_delivery_receipts[0].state, "unknown");
  }
});
Deno.test("an inline fallback failure ends the attempt and retains its uncertain receipt", async () => {
  const f = fixture(); f.templateStatus(404, { message: "Template not found" }); f.mailStatus(503);
  equal((await f.subscribe()).status, 502); equal(f.mail().length, 2);
  equal(f.tables.email_delivery_receipts[0].state, "unknown");
  const g = fixture(); g.templateStatus(404, { message: "Template not found" });
  let attempts = 0;
  const handler = createHandler({ ...g.deps, fetch: async (input, init) => {
    if (String(input) === "https://api.resend.com/emails" && ++attempts === 2) throw new Error("Fallback interrupted");
    return g.deps.fetch(input, init);
  } });
  equal((await handler(request({ kind: "subscribe", email: "marine@example.com" }))).status, 503);
  equal(attempts, 2); equal(g.tables.email_delivery_receipts[0].state, "unknown");
});
Deno.test("welcome runs once per address including concurrent confirms and a later resubscription", async () => {
  const f=fixture();await f.subscribe();const link=`${ENDPOINT}?confirm=${f.links().confirm}`;
  const responses=await Promise.all([f.handler(postLink(link)),f.handler(postLink(link))]);
  equal(responses.filter(r=>r.headers.get("location")===`${SITE}/alerts/confirmed/`).length,1);
  const welcome=f.mail().filter(c=>(c.body as any).template?.id==="welcome");equal(welcome.length,1);
  const variables=(welcome[0].body as any).template.variables;
  assert(variables.PREFS_URL && variables.WEEKLY_ON_URL && variables.ALERT_UNSUBSCRIBE_URL);
  equal(f.tables.email_delivery_receipts.find(r=>r.campaign==="welcome:v1")?.state,"accepted");
  await f.handler(postLink(variables.ALERT_UNSUBSCRIBE_URL));f.advance(2*86400000);
  await f.subscribe();await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`));
  equal(f.mail().filter(c=>(c.body as any).template?.id==="welcome").length,1);
});
Deno.test("welcome failure preserves successful confirmation and records the attempt", async () => {
  const f=fixture();await f.subscribe();f.mailStatus(500);
  equal((await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`))).headers.get("location"),`${SITE}/alerts/confirmed/`);
  equal(f.tables.alert_signups[0].status,"confirmed");equal(f.tables.email_delivery_receipts.find(r=>r.campaign==="welcome:v1")?.state,"unknown");
});
Deno.test("preferences require a private token and strict booleans; pending addresses cannot opt in", async () => {
  const f=fixture();await f.subscribe();const link=`${ENDPOINT}?prefs=${f.links().prefs}`;
  equal((await f.handler(new Request(`${ENDPOINT}?prefs=${token()}`))).status,404);
  const pending=await(await f.handler(new Request(link))).json();equal(pending.status,"pending");equal(pending.weekly,false);equal(pending.monthly,true);
  const post=(body:unknown,origin=SITE)=>f.handler(new Request(link,{method:"POST",headers:{origin},body:JSON.stringify(body)}));
  equal((await post({corrections:false,monthly:false,weekly:true,lessons:true})).status,409);
  await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`));
  equal((await post({corrections:false,monthly:false,weekly:true,lessons:true},"https://other.invalid")).status,403);
  for(const body of [{weekly:"true",monthly:false},{weekly:true},{weekly:true,monthly:false,status:"confirmed"},null,[]])equal((await post(body)).status,400);
  const changed=await(await post({corrections:false,monthly:false,weekly:true,lessons:true})).json();equal(changed.weekly,true);equal(changed.monthly,false);equal(changed.email,"marine@example.com");
  equal((await f.handler(new Request(link))).headers.get("cache-control"),"no-store");
  equal((await post({unsubscribe:true})).status,200);equal(f.tables.alert_signups.length,0);equal((await f.handler(new Request(link))).status,404);
});
Deno.test("weekly-add GET is passive and POST consumes the enrollment authorizer", async () => {
  const f=fixture();await f.subscribe();await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`));
  const welcome=f.mail().find(c=>(c.body as any).template?.id==="welcome")?.body as any;
  const url=welcome.template.variables.WEEKLY_ON_URL;
  const raw=new URL(url).searchParams.get("prefs");
  const before = JSON.stringify(f.tables), calls = f.calls.length;
  equal((await f.handler(new Request(url))).headers.get("location"),`${SITE}/alerts/action/#prefs=${raw}&weekly=1`);
  equal(JSON.stringify(f.tables), before); equal(f.calls.length, calls);
  const submit=()=>f.handler(new Request(url,{method:"POST",headers:{origin:SITE},body:JSON.stringify({weekly:true})}));
  equal((await submit()).status,200);
  equal((await submit()).status,404);
  equal(f.tables.alert_signups[0].weekly,true);
  assert(!(f.tables.alert_signups[0].unsubscribe_hashes as string[]).includes(await hash(raw)));
  assert(!JSON.stringify(f.tables).includes(raw));
});

Deno.test("a preference change after link reservation removes the recipient before batch dispatch",async()=>{
  const f=fixture();f.tables.alert_signups.push(row("one"));
  const net:typeof fetch=async(input,init)=>{
    const result=await f.deps.fetch(input,init);
    if(String(input).includes("alert_signups?")&&init?.method==="PATCH"&&String(init.body).includes("unsubscribe_hashes"))f.tables.alert_signups[0].monthly=false;
    return result;
  };
  await sendAlert(monthly("preference-race"),true,{...f.deps,fetch:net,print:()=>{}});
  equal(f.mail().length,0);equal(f.tables.email_delivery_receipts[0].state,"skipped");
});
Deno.test("concurrent sends claim each address once and protect recent token hashes",async()=>{
  const f=fixture();f.tables.alert_signups.push(row("one"));
  const results=await Promise.allSettled([sendAlert(correction(),true,{...f.deps,print:()=>{}}),sendAlert(correction(),true,{...f.deps,print:()=>{}})]);
  assert(results.some(r=>r.status==="fulfilled"));equal(f.mail().length,1);equal(f.tables.email_delivery_receipts.length,1);equal(f.tables.email_delivery_receipts[0].state,"accepted");
});

const recipientHash=(id:string)=>hash("test-saltdelivery:"+id+"@example.com");
async function used(f:ReturnType<typeof fixture>,id:string,dates:string[],state="accepted",stream="weekly"){
 for(const [i,date] of dates.entries())f.tables.email_delivery_receipts.push({campaign:`prior-${id}-${i}`,recipient_hash:await recipientHash(id),content_hash:await hash("prior"),stream,state,created_at:date,updated_at:date});
}
Deno.test("weekly and monthly caps count shared stream receipts; corrections are exempt",async()=>{
 const f=fixture();f.tables.alert_signups.push(row("week"),row("month"),row("free"));
 await used(f,"week",["2026-10-06T12:00:00Z"]);
 await used(f,"month",["2026-10-01T12:00:00Z","2026-10-02T12:00:00Z","2026-10-03T12:00:00Z","2026-10-04T12:00:00Z"]);
 const printed:string[]=[];await sendAlert(monthly(),false,{...f.deps,print:line=>printed.push(line)});const report=JSON.parse(printed[0]);equal(report.recipients,3);equal(report.eligible,1);equal(report.skipped,2);equal(report.reasons,{monthly_cap:1,weekly_cap:1});
 const before=f.tables.email_delivery_receipts.length;await sendAlert(monthly(),true,{...f.deps,print:()=>{}});equal((f.mail()[0].body as any[]).map(m=>m.to[0]),["free@example.com"]);equal(f.tables.email_delivery_receipts.length,before+1);
 await sendAlert(correction(),true,{...f.deps,print:()=>{}});equal((f.mail()[1].body as any[]).length,3);
});
Deno.test("concurrent Monthly and lesson launch share one atomic weekly slot",async()=>{
 const f=fixture();f.tables.alert_signups.push(row("one",{lessons:true}));const lesson=JSON.stringify({template:"lesson-launch",campaign:"launch",variables:{LESSON_TITLE:"Reviewed lesson",LESSON_PROMISE:"Practice one skill.",LESSON_URL:"https://warfarecommand.com/reviewed-lesson/"}});const reports:string[]=[];
 await Promise.all([sendAlert(monthly(),true,{...f.deps,print:line=>reports.push(line)}),sendAlert(lesson,true,{...f.deps,print:line=>reports.push(line)})]);equal(f.mail().length,1);equal(f.tables.email_delivery_receipts.filter(r=>r.state==="accepted").length,1);assert(reports.some(r=>JSON.parse(r).reasons.weekly_cap===1));
});
Deno.test("uncertain reservations consume caps; explicit failures and transactional welcome do not",async()=>{
 for(const state of ["reserved","unknown","failed"]){const f=fixture();f.tables.alert_signups.push(row("one"));await used(f,"one",["2026-10-08T12:00:00Z"],state);const reports:string[]=[];await sendAlert(monthly(),false,{...f.deps,print:r=>reports.push(r)});equal(JSON.parse(reports[0]).eligible,state==="failed"?1:0);}
 const f=fixture();f.tables.alert_signups.push(row("one"));await used(f,"one",["2026-10-08T12:00:00Z"],"accepted","transactional");const reports:string[]=[];await sendAlert(monthly(),false,{...f.deps,print:r=>reports.push(r)});equal(JSON.parse(reports[0]).eligible,1);
});
Deno.test("caps use UTC ISO weeks and calendar months, including a week spanning months",async()=>{
 const f=fixture();f.tables.alert_signups.push(row("one"));await used(f,"one",["2026-10-09T12:00:00Z"]);f.advance(3*86400000);const reports:string[]=[];await sendAlert(monthly("next-week"),false,{...f.deps,print:r=>reports.push(r)});equal(JSON.parse(reports[0]).eligible,1);
 const g=fixture();g.tables.alert_signups.push(row("one"));await used(g,"one",["2026-10-31T12:00:00Z"]);g.advance(Date.parse("2026-11-01T12:00:00Z")-g.deps.now());const out:string[]=[];await sendAlert(monthly("november"),false,{...g.deps,print:r=>out.push(r)});equal(JSON.parse(out[0]).reasons.weekly_cap,1);
});

Deno.test("an ambiguous HTTP server failure retains the campaign cap for later campaigns",async()=>{
 const f=fixture();f.tables.alert_signups.push(row("one",{lessons:true}));f.mailStatus(503);let failed=false;try{await sendAlert(monthly(),true,{...f.deps,print:()=>{}});}catch{failed=true;}assert(failed);equal(f.tables.email_delivery_receipts[0].state,"unknown");
 const reports:string[]=[];await sendAlert(monthly("different-reviewed-campaign"),false,{...f.deps,print:r=>reports.push(r)});equal(JSON.parse(reports[0]).reasons.weekly_cap,1);equal(f.mail().length,1);
});

Deno.test("stream names read as a plain English list", () => {
  equal(streamNames({ corrections: true, monthly: false, weekly: false, lessons: false }), "Muster Out corrections");
  equal(streamNames({ corrections: true, monthly: true, weekly: false, lessons: false }), "Muster Out corrections and Warfare Command Monthly");
  equal(streamNames({ corrections: true, monthly: true, weekly: true, lessons: false }), "Muster Out corrections, Warfare Command Monthly, and Weekly MARADMIN roundup");
  equal(streamNames({ corrections: false, monthly: false, weekly: false, lessons: false }), "No email streams");
});

Deno.test("alerts rejects hostile normal and preference streams before database or provider calls", async () => {
  for (const prefs of [false, true]) for (const mode of ["oversize", "multibyte", "slow", "invalid_utf8"]) {
    const f = fixture(); let cancelled = 0, pulls = 0;
    const cap = prefs ? 1024 : 8192;
    const body = new ReadableStream<Uint8Array>({
      pull(c) {
        pulls++;
        if (mode === "slow") return;
        if (mode === "oversize") c.enqueue(new Uint8Array(pulls === 1 ? cap : 1));
        if (mode === "multibyte") c.enqueue(new TextEncoder().encode("é".repeat(cap / 2 + 1)));
        if (mode === "invalid_utf8") { c.enqueue(new Uint8Array([0xff])); c.close(); }
      }, cancel() { cancelled++; }
    }, { highWaterMark: 0 });
    const handler = createHandler({ ...f.deps, bodyDeadlineMs: 20 });
    const response = await handler(new Request(ENDPOINT + (prefs ? "?prefs=" + "a".repeat(64) : ""), { method: "POST", headers: { origin: SITE, "content-length": "1" }, body, duplex: "half" } as any));
    equal(response.status, mode === "slow" ? 408 : mode === "invalid_utf8" ? 400 : 413);
    equal(f.calls.length, 0); equal(f.mail().length, 0);
    if (mode !== "invalid_utf8") equal(cancelled, 1);
    if (mode === "oversize") equal(pulls, 2);
  }
});
Deno.test("alerts accepts complete JSON at the byte cap including split UTF-8", async () => {
  const f = fixture();
  // A honeypot exits after parsing without any database or provider calls.
  const json = JSON.stringify({ kind: "subscribe", website: "é" });
  const text = json + " ".repeat(8192 - new TextEncoder().encode(json).length);
  const raw = new TextEncoder().encode(text);
  const body = new ReadableStream<Uint8Array>({ start(c) { for (const b of raw) c.enqueue(new Uint8Array([b])); c.close(); } });
  equal((await f.handler(new Request(ENDPOINT, { method: "POST", headers: { origin: SITE }, body, duplex: "half" } as any))).status, 200);
  equal(f.calls.length, 0); equal(f.mail().length, 0);
});


const coachSignup = (f: ReturnType<typeof fixture>, extra: Stored = {}) => f.handler(request({kind: "subscribe", source: "coach", email: "marine@example.com", setup: true, ...extra}));
const confirmCoach = async (f: ReturnType<typeof fixture>) => { f.values.SETUP_EMAIL_ENABLED = "true"; equal((await coachSignup(f)).status,200); return f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`)); };
const setupMail = (f: ReturnType<typeof fixture>) => f.mail().filter(c => c.url.pathname === "/emails/batch").flatMap(c => c.body as any[]).filter(m => /^setup-/.test(m.template.id));

Deno.test("setup requires enabled explicit unchecked-by-default opt-in and rejects telemetry fields",async()=>{
  const f=fixture(); equal((await coachSignup(f)).status,503); equal(f.mail().length,0);
  f.values.SETUP_EMAIL_ENABLED="true";
  for(const extra of [{setup:false},{setup:undefined},{setup:"true"},{install_id:"0123456789abcdef"},{path:"eas"},{board:"private"}]) equal((await coachSignup(f,extra)).status,400);
  equal(f.calls.length,0);
  equal((await f.handler(request({kind:"subscribe",source:"musterout",email:"marine@example.com",setup:true}))).status,400);
});
Deno.test("setup confirmation scope is narrow and setup-1 replaces welcome",async()=>{
  const f=fixture(); f.values.SETUP_EMAIL_ENABLED="true"; await coachSignup(f);
  const r=f.tables.alert_signups[0], vars=(f.mail()[0].body as any).template.variables;
  equal([r.corrections,r.monthly,r.weekly,r.lessons,r.setup],[false,false,false,false,true]);
  assert(String(vars.CONSENT_SCOPE).includes("up to three emails")); equal(setupMail(f).length,0);
  equal((await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`))).status,303);
  equal(r.confirm_hash,SETUP_CONSENT); equal(setupMail(f).map(m=>m.template.id),["setup-1"]);
  assert(!f.mail().some(c=>(c.body as any).template?.id==="welcome"));
  const claims=f.tables.email_setup_claims; equal(claims.length,1);equal(claims[0].state,"accepted");
  assert(!JSON.stringify(claims).includes("marine@example.com"));
});
Deno.test("setup sends at 0, 20 and 44 hours with lifetime cap after deletion and receipt cleanup",async()=>{
  const f=fixture();await confirmCoach(f);
  await sendSetup(f.deps,false);equal(setupMail(f).length,1);
  f.advance(20*3600000-1);await sendSetup(f.deps,false);equal(setupMail(f).length,1);
  f.advance(1);await sendSetup(f.deps,false);equal(setupMail(f).length,2);
  f.advance(24*3600000);await sendSetup(f.deps,false);equal(setupMail(f).map(m=>m.template.id),["setup-1","setup-2","setup-3"]);
  f.tables.alert_signups.length=0;f.tables.email_delivery_receipts.length=0;
  f.advance(400*86400000);await confirmCoach(f);await sendSetup(f.deps,false);
  equal(setupMail(f).length,3);equal(f.tables.email_setup_claims.length,3);
});
Deno.test("late setup cron spaces catchup instead of sending three at once",async()=>{
  const f=fixture();f.values.SETUP_EMAIL_ENABLED="true";await coachSignup(f);
  // Confirm while globally paused, then enable much later.
  f.values.SETUP_EMAIL_ENABLED="false";await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`));
  f.advance(50*3600000);f.values.SETUP_EMAIL_ENABLED="true";await sendSetup(f.deps,false);
  equal(setupMail(f).map(m=>m.template.id),["setup-1"]);
  f.advance(20*3600000);await sendSetup(f.deps,false);equal(setupMail(f).length,2);
  f.advance(24*3600000);await sendSetup(f.deps,false);equal(setupMail(f).length,3);
});
Deno.test("setup dry run makes no claims, tokens or mail and concurrent crons send once",async()=>{
  const f=fixture();f.values.SETUP_EMAIL_ENABLED="true";await coachSignup(f);
  f.values.SETUP_EMAIL_ENABLED="false";await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`));f.values.SETUP_EMAIL_ENABLED="true";
  const snapshot=JSON.stringify(f.tables), mails=f.mail().length;
  const dry=await sendSetup(f.deps);equal(dry[0].eligible,1);equal(JSON.stringify(f.tables),snapshot);equal(f.mail().length,mails);
  await Promise.all([sendSetup(f.deps,false),sendSetup(f.deps,false)]);equal(setupMail(f).length,1);equal(f.tables.email_setup_claims.length,1);
});
Deno.test("setup stop page GET does not opt out; POST stops setup only and expired tokens fail",async()=>{
  const f=fixture();await confirmCoach(f);const r=f.tables.alert_signups[0];r.monthly=true;
  const stop=setupMail(f)[0].template.variables.STOP_SETUP_URL;
  equal((await f.handler(new Request(stop))).status,303);equal(r.setup,true);
  const raw=new URL(stop).searchParams.get("stop_setup")!;
  assert((r.setup_token_hashes as string[]).includes(await hash(raw)));assert(!JSON.stringify(f.tables).includes(raw));
  equal((await f.handler(new Request(stop,{method:"POST"}))).status,200);equal(r.setup,false);equal(r.monthly,true);
  f.advance(48*3600000);await sendSetup(f.deps,false);equal(setupMail(f).length,1);
  equal((await f.handler(new Request(`${ENDPOINT}?stop_setup=${token()}`,{method:"POST"}))).status,404);
});
Deno.test("setup errors remain visible, consume lifetime slot and block later stages",async()=>{
  for(const mode of ["reject","throw","ambiguous"]){
    const f=fixture();f.values.SETUP_EMAIL_ENABLED="true";await coachSignup(f);
    if(mode==="reject")f.mailStatus(500);else if(mode==="throw")f.throwMail();else f.badMail();
    await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`));
    equal(f.tables.alert_signups[0].status,"confirmed");equal(f.tables.email_setup_claims[0].state,"unknown");
    const before=f.mail().length;f.advance(48*3600000);await sendSetup(f.deps,false);equal(f.mail().length,before);equal(f.tables.email_setup_claims.length,1);
  }
});
Deno.test("setup scheduler requires private auth, POST, and enable flag",async()=>{
  const f=fixture(),url=`${ENDPOINT}/setup`;
  equal((await f.handler(new Request(url))).status,405);
  equal((await f.handler(new Request(url,{method:"POST"}))).status,403);
  f.values.SETUP_CRON_SECRET="a-private-test-key";
  equal((await f.handler(new Request(url,{method:"POST",headers:{"x-setup-cron-secret":"wrong"}}))).status,403);
  equal((await f.handler(new Request(url,{method:"POST",headers:{"x-setup-cron-secret":f.values.SETUP_CRON_SECRET}}))).status,503);
  f.values.SETUP_EMAIL_ENABLED="true";
  equal((await f.handler(new Request(url+"?dry=1",{method:"POST",headers:{"x-setup-cron-secret":f.values.SETUP_CRON_SECRET}}))).status,200);equal(f.mail().length,0);
});
Deno.test("legacy preference saves preserve setup, fifth choice can stop but cannot silently enroll",async()=>{
  const f=fixture();await confirmCoach(f);const vars=setupMail(f)[0].template.variables;
  const choices={corrections:false,monthly:false,weekly:false,lessons:false};
  const update=(body:unknown)=>f.handler(new Request(ENDPOINT+"?prefs="+new URL(vars.PREFS_URL).searchParams.get("prefs"),{method:"POST",headers:{origin:SITE},body:JSON.stringify(body)}));
  equal((await update(choices)).status,200);equal(f.tables.alert_signups[0].setup,true);
  equal((await update({...choices,setup:false})).status,200);equal(f.tables.alert_signups[0].setup,false);
  equal((await update({...choices,setup:true})).status,409);
});
Deno.test("confirmed signup cannot change choices or add setup through source spoofing",async()=>{
  const f=fixture();await f.subscribe();await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`));f.values.SETUP_EMAIL_ENABLED="true";
  const saved=JSON.stringify(f.tables.alert_signups),before=f.mail().length;
  equal((await coachSignup(f)).status,200);equal(JSON.stringify(f.tables.alert_signups),saved);equal(f.mail().length,before);equal(setupMail(f).length,0);
});
Deno.test("setup rereads consent before provider send and refuses arbitrary campaigns",async()=>{
  const f=fixture();f.values.SETUP_EMAIL_ENABLED="true";await coachSignup(f);f.values.SETUP_EMAIL_ENABLED="false";await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`));f.values.SETUP_EMAIL_ENABLED="true";
  const net:typeof fetch=async(input,init)=>{if(String(input).includes("alert_signups?")&&init?.method==="PATCH"&&String(init.body).includes("setup_token_hashes"))f.tables.alert_signups[0].setup=false;return f.deps.fetch(input,init);};
  await sendSetup({...f.deps,fetch:net},false);equal(setupMail(f).length,0);equal(f.tables.email_setup_claims[0].state,"skipped");
  let refused=false;try{await sendTemplates("setup-1","setup-1:v2",{}, {setup:"eq.true"},f.deps,"setup");}catch{refused=true;}assert(refused);
});

Deno.test("setup sender refuses legacy or missing consent receipts even with setup flag set", async () => {
  const f = fixture(); await confirmCoach(f);
  const r = f.tables.alert_signups[0];
  f.advance(48 * 3600000); r.confirm_hash = "consent:campaign-streams:v2";
  const before = setupMail(f).length;
  await sendSetup(f.deps, false);
  equal(setupMail(f).length, before);
  equal(f.tables.email_setup_claims.length, 1);
});
Deno.test("proven setup provider rejection stays failed and never retries or advances", async () => {
  const f = fixture(); f.values.SETUP_EMAIL_ENABLED = "true"; await coachSignup(f);
  f.mailStatus(400);
  await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`));
  equal(f.tables.email_setup_claims[0].state, "failed");
  const before = f.mail().length; f.advance(48 * 3600000);
  await sendSetup(f.deps, false);
  equal(f.mail().length, before); equal(f.tables.email_setup_claims.length, 1);
});

async function completeSetupAndRotate() {
  const f = fixture(); await confirmCoach(f);
  f.advance(20 * 3600000); await sendSetup(f.deps, false);
  f.advance(24 * 3600000); await sendSetup(f.deps, false);
  const row = f.tables.alert_signups[0]; row.corrections = true;
  const stable = JSON.stringify(row.setup_token_hashes);
  // Corrections are a permitted ongoing stream outside campaign week caps.
  for (let n = 0; n < 6; n++) {
    equal((await sendTemplates("correction-alert", `footer-regression-${n}`, {}, { corrections: "eq.true" }, f.deps, "corrections")).accepted, 1);
  }
  equal((row.unsubscribe_hashes as string[]).length, 8);
  equal((row.setup_token_hashes as string[]).length, 9);
  equal(JSON.stringify(row.setup_token_hashes), stable);
  equal(setupMail(f).length, 3);
  f.values.SETUP_EMAIL_ENABLED = "false";
  return f;
}
Deno.test("every setup unsubscribe works after all stages and ongoing token rotation", async () => {
  for (let n = 0; n < 3; n++) {
    const f = await completeSetupAndRotate();
    const url = setupMail(f)[n].template.variables.ALERT_UNSUBSCRIBE_URL;
    equal((await f.handler(new Request(url, { method: "POST" }))).status, 200);
    equal(f.tables.alert_signups.length, 0);
    equal(f.tables.email_setup_claims.length, 3);
    // Deleted authorization cannot affect a later signup at the same address.
    f.advance(24 * 3600000); await confirmCoach(f);
    equal((await f.handler(new Request(url, { method: "POST" }))).status, 200);
    equal(f.tables.alert_signups.length, 1); equal(setupMail(f).length, 3);
  }
});
Deno.test("every setup preference link reads and saves after all stages and rotation", async () => {
  const f = await completeSetupAndRotate();
  for (const message of setupMail(f)) {
    const raw = new URL(message.template.variables.PREFS_URL).searchParams.get("prefs");
    const url = `${ENDPOINT}?prefs=${raw}`;
    equal((await f.handler(new Request(url))).status, 200);
    equal((await f.handler(new Request(url, { method: "POST", headers: { origin: SITE }, body: JSON.stringify({ corrections: true, monthly: true, weekly: false, lessons: false }) }))).status, 200);
    equal(f.tables.alert_signups[0].monthly, true); equal(f.tables.alert_signups[0].setup, true);
  }
});
Deno.test("every setup stop control survives all stages, rotation and prior stop", async () => {
  const f = await completeSetupAndRotate();
  for (const message of setupMail(f)) {
    const url = message.template.variables.STOP_SETUP_URL;
    const before = f.tables.alert_signups[0].setup;
    equal((await f.handler(new Request(url))).status, 303);
    equal(f.tables.alert_signups[0].setup, before);
    equal((await f.handler(new Request(url, { method: "POST" }))).status, 200);
    equal(f.tables.alert_signups[0].setup, false); equal(f.tables.alert_signups[0].corrections, true);
    equal((f.tables.alert_signups[0].setup_token_hashes as string[]).length, 9);
  }
});
Deno.test("setup footer retention fails closed for missing schema or a fourth set", async () => {
  const f = await completeSetupAndRotate(), db = database(f.deps.env, f.deps.fetch);
  for (const missing of [false, true]) {
    if (missing) delete f.tables.alert_signups[0].setup_token_hashes;
    let refused = false;
    try { await freshLinks(db, String(f.tables.alert_signups[0].id), { setup: "eq.true" }); } catch { refused = true; }
    assert(refused);
  }
  equal(setupMail(f).length, 3);
});

Deno.test("all email action previews are passive with no database or provider calls", async () => {
  const f = fixture(); await f.subscribe();
  const links = f.links();
  const urls = [`${ENDPOINT}?confirm=${links.confirm}`, `${ENDPOINT}?unsubscribe=${links.unsubscribe}`, `${ENDPOINT}?prefs=${links.prefs}&weekly=1`, `${ENDPOINT}?stop_setup=${links.unsubscribe}`];
  const before = JSON.stringify(f.tables), calls = f.calls.length;
  for (const url of urls) {
    for (let n = 0; n < 2; n++) {
      const response = await f.handler(new Request(url));
      equal(response.status, 303);
      assert(response.headers.get("location")!.startsWith(`${SITE}/alerts/action/#`));
      equal(response.headers.get("cache-control"), "no-store");
      equal(response.headers.get("referrer-policy"), "no-referrer");
    }
    equal((await f.handler(new Request(url, { method: "HEAD" }))).status, 405);
    equal((await f.handler(new Request(url, { method: "PUT" }))).status, 405);
  }
  equal(JSON.stringify(f.tables), before); equal(f.calls.length, calls);
});

Deno.test("JSON button confirmation succeeds once; expired or replaced tokens cannot confirm", async () => {
  const f = fixture(); await f.subscribe();
  const url = `${ENDPOINT}?confirm=${f.links().confirm}`;
  const click = () => f.handler(new Request(url, { method: "POST", headers: { origin: SITE, accept: "application/json" } }));
  equal(await (await click()).json(), { ok: true });
  const after = JSON.stringify(f.tables), calls = f.calls.length;
  equal((await click()).status, 404); equal(JSON.stringify(f.tables), after);
  equal(f.mail().length, 2);
  for (const mode of ["expired", "replaced"]) {
    const g = fixture(); await g.subscribe(); const raw = g.links().confirm;
    if (mode === "expired") g.advance(7 * 86400000 + 1);
    else { g.advance(600000); await g.subscribe(); }
    const before = JSON.stringify(g.tables), mails = g.mail().length;
    equal((await g.handler(new Request(`${ENDPOINT}?confirm=${raw}`, { method: "POST", headers: { accept: "application/json" } }))).status, 404);
    equal(JSON.stringify(g.tables), before); equal(g.mail().length, mails);
  }
  assert(f.calls.length > calls); // Replays check the atomic predicate, never send again.
});

Deno.test("weekly link replay cannot reverse a later opt-out; concurrent clicks enroll once", async () => {
  const f = fixture(); await f.subscribe(); await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`));
  const welcome = (f.mail().find(c => (c.body as any).template?.id === "welcome")!.body as any).template.variables;
  const click = () => f.handler(new Request(welcome.WEEKLY_ON_URL, { method: "POST", headers: { origin: SITE }, body: '{ "weekly": true }' }));
  const replies = await Promise.all([click(), click()]);
  equal(replies.filter(r => r.status === 200).length, 1);
  assert(replies.some(r => [404,409].includes(r.status)));
  f.tables.alert_signups[0].weekly = false;
  const before = JSON.stringify(f.tables);
  equal((await click()).status, 404); equal(JSON.stringify(f.tables), before);
  const g = fixture(); await g.subscribe();
  const url = `${ENDPOINT}?prefs=${g.links().prefs}&weekly=1`;
  equal((await g.handler(new Request(url, { method: "POST", headers: { origin: SITE }, body: '{"weekly":true}' }))).status, 404);
});

Deno.test("evicted footer tokens and foreign-origin POSTs leave the signup intact", async () => {
  const f = fixture(); await f.subscribe(); const old = f.links();
  await f.handler(postLink(`${ENDPOINT}?confirm=${old.confirm}`));
  const weekly = (f.mail().find(c => (c.body as any).template?.id === "welcome")!.body as any).template.variables.WEEKLY_ON_URL;
  const before = JSON.stringify(f.tables), calls = f.calls.length;
  for (const url of [`${ENDPOINT}?confirm=${old.confirm}`, `${ENDPOINT}?unsubscribe=${old.unsubscribe}`, `${ENDPOINT}?stop_setup=${old.unsubscribe}`, weekly]) {
    equal((await f.handler(new Request(url, { method: "POST", headers: { origin: "https://other.invalid" }, body: '{"weekly":true}' }))).status, 403);
  }
  equal(JSON.stringify(f.tables), before); equal(f.calls.length, calls);
  for (let n = 0; n < 4; n++) await freshLinks(database(f.deps.env, f.deps.fetch), String(f.tables.alert_signups[0].id));
  const rotated = JSON.stringify(f.tables);
  equal((await f.handler(new Request(`${ENDPOINT}?stop_setup=${old.unsubscribe}`, { method: "POST" }))).status, 404);
  equal((await f.handler(new Request(weekly, { method: "POST", headers: { origin: SITE }, body: '{"weekly":true}' }))).status, 404);
  equal((await f.handler(postLink(`${ENDPOINT}?unsubscribe=${old.unsubscribe}`))).status, 200);
  equal(JSON.stringify(f.tables), rotated);
});

Deno.test("human unsubscribe reports an expired link honestly while provider retries remain idempotent", async () => {
  const f = fixture(); await f.subscribe(); const old = f.links().unsubscribe;
  await f.handler(postLink(`${ENDPOINT}?confirm=${f.links().confirm}`));
  for (let n = 0; n < 4; n++) await freshLinks(database(f.deps.env, f.deps.fetch), String(f.tables.alert_signups[0].id));
  const url = `${ENDPOINT}?unsubscribe=${old}`, before = JSON.stringify(f.tables);
  const browser = () => f.handler(new Request(url + "&review=1", { method: "POST", headers: { origin: SITE, accept: "application/json" }, body: "List-Unsubscribe=One-Click" }));
  equal((await browser()).status, 404); equal(JSON.stringify(f.tables), before);
  equal((await f.handler(postLink(url))).status, 200); equal(JSON.stringify(f.tables), before);
  equal((await f.handler(new Request(url, { method: "POST", headers: { accept: "application/json" }, body: "List-Unsubscribe=One-Click" }))).status, 200);
  equal((await f.handler(new Request(url + "&review=1", { method: "POST" }))).status, 403);
  const current = (f.tables.alert_signups[0].unsubscribe_hashes as string[])[0];
  // The raw old token cannot be guessed from the stored current hash.
  assert(current !== old);
  const g = fixture(); await g.subscribe(); const valid = `${ENDPOINT}?unsubscribe=${g.links().unsubscribe}`;
  const click = () => g.handler(new Request(valid + "&review=1", { method: "POST", headers: { origin: SITE, accept: "application/json" }, body: "List-Unsubscribe=One-Click" }));
  equal((await click()).status, 200); equal(g.tables.alert_signups.length, 0);
  equal((await click()).status, 404); equal(g.tables.alert_signups.length, 0);
  equal((await g.handler(postLink(valid))).status, 200);
});
