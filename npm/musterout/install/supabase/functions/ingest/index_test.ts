import { createHandler } from "./index.ts";
const assert = (ok: unknown, message = "Assertion failed") => { if (!ok) throw new Error(message); };
const equal = (a: unknown, b: unknown) => assert(JSON.stringify(a) === JSON.stringify(b), `${JSON.stringify(a)} differs from ${JSON.stringify(b)}`);

function fixture() {
  let now = Date.parse("2026-10-09T21:00:00Z");
  const budgets: Record<string, { accepted: number; text_units: number; overflow: number }> = {};
  const tables: Record<string, Record<string, unknown>[]> = { ingest_rate: [], setup_intents: [], install_registrations: [], setup_pings: [], feedback_reports: [], usage_weeks: [], learn_install_cohorts: [], telemetry_admissions: [] };
  let fail = "";
  const db = { rpc: async (name: string, args: any) => {
    if (name === "learn_abuse_admit") {
      if (fail === "abuse") return { data: null, error: {} };
      if (fail === "abuse_shape") return { data: { admitted: "yes" }, error: null };
      const date = new Date(now); date.setUTCDate(date.getUTCDate() - (date.getUTCDay() + 6) % 7); date.setUTCHours(0, 0, 0, 0);
      const key = `${date.toISOString()}:${args.p_kind}:`;
      const g = budgets[key + "global"] ??= { accepted: 0, text_units: 0, overflow: 0 };
      const feedbackKind = args.p_kind === "feedback";
      if (g.accepted >= (feedbackKind ? 90 : 2000) || (feedbackKind && g.text_units + args.p_text_units > 100000)) {
        g.overflow++; if (budgets[key + args.p_ip_hash]) budgets[key + args.p_ip_hash].overflow++;
        return { data: { admitted: false, quarantined: false }, error: null };
      }
      const ip = budgets[key + args.p_ip_hash] ??= { accepted: 0, text_units: 0, overflow: 0 };
      if (ip.accepted >= (feedbackKind ? 20 : 100)) {
        g.overflow++; ip.overflow++; return { data: { admitted: false, quarantined: false }, error: null };
      }
      for (const b of [g, ip]) { b.accepted++; b.text_units += args.p_text_units; }
      const cohorts = tables.learn_install_cohorts;
      let row = cohorts.find(r => r.install_id === args.p_install_id);
      if (!row) { row = { install_id: args.p_install_id, ip_hash: args.p_ip_hash, first_seen: now, quarantined: false }; cohorts.push(row); }
      const recent = cohorts.filter(r => r.ip_hash === args.p_ip_hash && Number(r.first_seen) >= now - 3600000);
      if (recent.length > 5) for (const r of recent) r.quarantined = true;
      return { data: { admitted: true, quarantined: row.quarantined }, error: null };
    }
    equal(name, "ingest_rate_hit");
    if (fail === "ingest_rate" || (fail === "ingest_rate_kind" && args.p_ip_hash.startsWith("learn:"))) return { data: null, error: { message: "private detail" } };
    let row = tables.ingest_rate.find(r => r.ip_hash === args.p_ip_hash && r.minute === args.p_minute);
    if (!row) { row = { ip_hash: args.p_ip_hash, minute: args.p_minute, n: 0 }; tables.ingest_rate.push(row); }
    row.n = Number(row.n) + 1;
    return { data: fail === "ingest_rate_bad_data" ? "1" : row.n, error: null };
  }, from: (table: string) => {
    assert(table !== "ingest_rate", "Rate hits must use the atomic RPC");
    const filters: [string, unknown][] = [];
    let count = 0;
    let operation = "select", value: Record<string, unknown> = {}, options: { ignoreDuplicates?: boolean } = {};
    const query = {
      select: () => query,
      eq: (key: string, v: unknown) => { filters.push([key, v]); return query; },
      maybeSingle: async () => ({ data: tables[table].find(row => filters.every(([key, v]) => row[key] === v)), error: fail === table || fail === table + ":select" ? {} : null }),
      insert: (row: Record<string, unknown>) => { operation = "insert"; value = row; return query; },
      upsert: (row: Record<string, unknown>, opts = {}) => { operation = "upsert"; value = row; options = opts; return query; },
      delete: () => { operation = "delete"; return query; },
      then: (resolve: (v: unknown) => unknown) => {
        if (fail === "throw") throw new Error("private detail");
        if (fail === table) return Promise.resolve({ error: { message: "private detail" } }).then(resolve);
        if (operation === "delete") {
          count = tables[table].filter(row => filters.every(([key, v]) => row[key] === v)).length;
          tables[table] = tables[table].filter(row => !filters.every(([key, v]) => row[key] === v));
        }
        else if (operation === "insert") {
          const conflict = tables[table].some(row => table === "feedback_reports" ? row.id === value.id : table === "usage_weeks" ? row.install_id === value.install_id && row.week === value.week && row.writer === value.writer : false);
          if (conflict) return Promise.resolve({ error: { code: "23505" } }).then(resolve);
          tables[table].push(structuredClone(value));
        }
        else if (operation === "upsert") {
          const existing = tables[table].find(row => table === "ingest_rate" ? row.ip_hash === value.ip_hash && row.minute === value.minute : row.install_id === value.install_id);
          if (!existing) tables[table].push(structuredClone(value));
          else if (!options.ignoreDuplicates) Object.assign(existing, value);
        }
        return Promise.resolve({ error: null, count: fail === "bad_count" ? null : count }).then(resolve);
      }
    };
    return query;
  } };
  const handler = createHandler({ db, env: name => name === "INGEST_SALT" ? "test-salt" : undefined, now: () => now });
  const send = (body: unknown, origin = "https://musterout.warfarecommand.com", address = "192.0.2.1") => handler(new Request("https://endpoint.invalid/ingest", { method: "POST", headers: { origin, "x-forwarded-for": address }, body: JSON.stringify(body) }));
  return { tables, budgets, advance: (ms: number) => { now += ms; }, handler, send, fail: (table: string) => { fail = table; } };
}
const install = { kind: "install", product: "musterout", version: "0.1.4", path: "eas", grade: "e67", channel: "chat", install_id: "0123456789abcdef0123456789abcdef" };

Deno.test("ingest rejects hostile and malformed bodies before accessing the database", async () => {
  for (const mode of ["oversize", "multibyte", "slow", "invalid_utf8", "malformed_json"]) {
    let dbAccesses = 0, pulls = 0, cancelled = 0;
    const handler = createHandler({
      get db() { dbAccesses++; throw new Error("Database must not be accessed"); },
      env: () => "synthetic-salt", bodyDeadlineMs: 20,
    });
    const body = new ReadableStream<Uint8Array>({
      pull(c) {
        pulls++;
        if (mode === "slow") return;
        if (mode === "oversize") c.enqueue(new Uint8Array(pulls === 1 ? 20000 : 1));
        if (mode === "multibyte") c.enqueue(new TextEncoder().encode("é".repeat(10001)));
        if (mode === "invalid_utf8") { c.enqueue(new Uint8Array([0xff])); c.close(); }
        if (mode === "malformed_json") { c.enqueue(new TextEncoder().encode("{")); c.close(); }
      }, cancel() { cancelled++; }
    }, { highWaterMark: 0 });
    const response = await handler(new Request("https://endpoint.invalid/ingest", { method: "POST", headers: { "content-length": "1" }, body, duplex: "half" } as any));
    equal(response.status, mode === "slow" ? 408 : ["invalid_utf8", "malformed_json"].includes(mode) ? 400 : 413);
    equal(dbAccesses, 0);
    if (["oversize", "multibyte", "slow"].includes(mode)) equal(cancelled, 1);
    if (mode === "oversize") equal(pulls, 2);
  }
});
Deno.test("ingest accepts an exact-schema JSON body at its byte cap with split chunks", async () => {
  const f = fixture();
  const json = JSON.stringify({ kind: "intent", product: "musterout", version: "0.1.4" });
  const raw = new TextEncoder().encode(json + " ".repeat(20000 - new TextEncoder().encode(json).length));
  const splitAt = Math.floor(raw.length / 2);
  const body = new ReadableStream<Uint8Array>({ start(c) { c.enqueue(raw.slice(0, splitAt)); c.enqueue(raw.slice(splitAt)); c.close(); } });
  equal((await f.handler(new Request("https://endpoint.invalid/ingest", { method: "POST", body, duplex: "half" } as any))).status, 200);
  equal(f.tables.setup_intents.length, 1); equal(f.tables.ingest_rate[0].n, 1);
});
Deno.test("intent accepts all supported origins and stores only anonymous allowed fields", async () => {
  for (const origin of ["https://warfarecommand.com", "https://www.warfarecommand.com", "https://musterout.warfarecommand.com"]) {
    const f = fixture();
    const preflight = await f.handler(new Request("https://endpoint.invalid/ingest", { method: "OPTIONS", headers: { origin } }));
    equal(preflight.headers.get("access-control-allow-origin"), origin);
    const response = await f.send({ kind: "intent", product: "musterout", version: "0.1.4" }, origin);
    equal(response.status, 200);
    equal(response.headers.get("access-control-allow-origin"), origin);
    equal(Object.keys(f.tables.setup_intents[0]).sort(), ["ip_hash", "product", "version"]);
    assert(!JSON.stringify(f.tables).includes("192.0.2.1"));
  }
});

Deno.test("install fixed lists and version/id validation reject unknown values", async () => {
  for (const [key, values] of Object.entries({ product: ["other", null], version: ["v0.1.4", "00.1.4", "0.1", null, "1.2.3extra"], path: ["unsure", "other", null], grade: ["unsure", "e6", null], channel: ["other", null], install_id: ["short", "x".repeat(32), "f".repeat(33), null, "F".repeat(16)] })) {
    for (const value of values) {
      const f = fixture();
      equal((await f.send({ ...install, [key]: value })).status, 400);
      equal(f.tables.install_registrations.length, 0);
    }
  }
  for (const path of ["resign", "retire", "eas"]) for (const grade of ["o5", "o14", "cwo45", "wo13", "e89", "e67", "e15"]) for (const channel of ["chat", "laptop"]) {
    const f = fixture();
    equal((await f.send({ ...install, path, grade, channel, install_id: "f".repeat(16) })).status, 200);
  }
  for (const version of ["1.2.3", "0.1.4", "0.0.0"]) {
    const f = fixture();
    equal((await f.send({ kind: "intent", product: "musterout", version })).status, 200);
  }
});

Deno.test("install deduplicates the id without replacing fields and deletion removes only matching counts", async () => {
  const f = fixture();
  equal((await f.send(install)).status, 200);
  equal((await f.send({ ...install, path: "retire", grade: "o5" })).status, 200);
  equal(f.tables.install_registrations.length, 1);
  equal(f.tables.install_registrations[0].path, "eas");
  assert(!("board_url" in f.tables.install_registrations[0]));
  await f.send({ ...install, install_id: "a".repeat(32) });
  await f.send({ kind: "ping", id: install.install_id, service: "usmc", path: "eas", grade: "e67", version: "0.1.3" });
  await f.send({ kind: "delete", install_id: install.install_id });
  equal(f.tables.setup_pings.length, 0);
  equal(f.tables.install_registrations.map(row => row.install_id), ["a".repeat(32)]);
  assert(f.tables.ingest_rate.length > 0);
});

Deno.test("legacy ping and receipt deletion still work without a browser origin", async () => {
  const f = fixture();
  const ping = await f.handler(new Request("https://endpoint.invalid/ingest?kind=ping&service=usmc&path=unsure&grade=unsure&version=0.1.3&id=3f1c2a9e-8b7d-4e21-9a5c-0d6e4f7b8a12"));
  equal(ping.status, 200);
  equal(f.tables.setup_pings.length, 1);
  equal((await f.send({ kind: "delete", id: "3f1c2a9e-8b7d-4e21-9a5c-0d6e4f7b8a12" })).status, 200);
  equal(f.tables.setup_pings.length, 0);
});

Deno.test("unknown kinds return 400 without telemetry writes", async () => {
  const f = fixture();
  equal((await f.send({ kind: "unknown" })).status, 400);
  equal(f.tables.setup_intents.length + f.tables.install_registrations.length + f.tables.setup_pings.length, 0);
});

Deno.test("30 concurrent rate hits admit exactly 20 writes", async () => {
  const f = fixture();
  const responses = await Promise.all(Array.from({ length: 30 }, () => f.send({ kind: "intent", product: "musterout", version: "0.1.4" })));
  equal(responses.filter(r => r.status === 200).length, 20);
  equal(responses.filter(r => r.status === 429).length, 10);
  equal(f.tables.setup_intents.length, 20);
  equal(f.tables.ingest_rate[0].n, 30);
});

Deno.test("oversized Content-Length is rejected before reading or database calls; chunked bodies remain capped", async () => {
  const f = fixture();
  const req = new Request("https://endpoint.invalid/ingest", { method: "POST", headers: { "content-length": "20001" }, body: "{}" });
  req.text = async () => { throw new Error("Body must not be read"); };
  equal((await f.handler(req)).status, 413);
  equal(f.tables.ingest_rate.length, 0);
  equal((await f.handler(new Request("https://endpoint.invalid/ingest", { method: "POST", body: " ".repeat(20001) }))).status, 413);
});

Deno.test("new kinds share the minute rate limit and failures are visible", async () => {
  const f = fixture();
  for (let i = 0; i < 20; i++) equal((await f.send(i % 2 ? install : { kind: "intent", product: "musterout", version: "0.1.4" })).status, 200);
  equal((await f.send(install)).status, 429);
  for (const table of ["ingest_rate", "setup_intents", "install_registrations"]) {
    const g = fixture(); g.fail(table);
    const response = await g.send(table === "setup_intents" ? { kind: "intent", product: "musterout", version: "0.1.4" } : install);
    assert(response.status >= 500);
    assert(!(await response.text()).includes("private detail"));
  }
  const g = fixture();
  equal((await g.send(install, "https://evil.invalid")).status, 403);
  equal(g.tables.ingest_rate.length, 0);
  equal((await g.send(null)).status, 400);
  equal((await g.send([])).status, 400);
});

const feedback = { kind: "feedback", id: "report_123456", install_id: install.install_id, version: "0.2.2", pack: "usmc-2026.10", path: "eas", grade: "e67", category: "bug", error_class: "save", text: "Synthetic save failed", created: "2026-10-09T20:00:00Z" };
const usage = { kind: "usage", install_id: install.install_id, week: "2026-W41", writer: "a".repeat(16), version: "0.2.2", counters: { opens: 3, errors_save: 1 } };

Deno.test("feedback validates every required field, rejects extras, and bounds text before stripping", async () => {
  const invalid: Record<string, unknown[]> = { id: [null, "tiny", "a".repeat(65), "report/1234"], install_id: [null, "X".repeat(16)], version: [null, "1.2", "01.2.3", "1.2.3-01", "1.2.3-", "1.2.3+", "1.2.3+" + "a".repeat(64)], pack: [null, "usmc-2026.13", "other"], path: [null, "other"], grade: [null, "e6"], category: [null, "security"], error_class: [null, "secret"], text: [9, {}, "x".repeat(1001), "\u0000".repeat(1001)], created: [null, "2026-02-30T00:00:00Z", "2026-10-09", "2026-10-09T22:00:00Z", "2026-10-09T20:00:00+00:00"] };
  for (const [key, values] of Object.entries(invalid)) {
    for (const value of values) { const f = fixture(); equal((await f.send({ ...feedback, [key]: value })).status, 400); equal(f.tables.feedback_reports.length, 0); }
    if (key !== "text") { const f = fixture(), row: Record<string, unknown> = { ...feedback }; delete row[key]; equal((await f.send(row)).status, 400); }
  }
  for (const key of ["name", "received", "board_url", "__proto__"]) { const f = fixture(); equal((await f.send({ ...feedback, [key]: "extra" })).status, 400); }
  for (const text of [undefined, null, "", "x".repeat(1000), "\u{1f600}".repeat(1000)]) { const f = fixture(); equal((await f.send({ ...feedback, text })).status, 200); }
  const f = fixture(); equal((await f.send({ ...feedback, text: "a\n\t\u0000\u0085b" })).status, 200); equal(f.tables.feedback_reports[0].text, "ab");
  assert(!("ip_hash" in f.tables.feedback_reports[0]));
});

Deno.test("feedback enumerations, semver prerelease and build metadata are accepted", async () => {
  for (const category of ["bug", "content", "usability", "other"]) for (const error_class of ["none", "save", "update", "feed", "storage", "sample", "unavailable", "other"]) { const f = fixture(); equal((await f.send({ ...feedback, category, error_class, path: "unsure", grade: "unsure" })).status, 200); }
  for (const version of ["0.0.0", "1.2.3-rc.1", "1.2.3+build.01", "1.2.3-0+build"]) { const f = fixture(); equal((await f.send({ ...feedback, version })).status, 200); equal((await f.send({ ...usage, version })).status, 200); }
});

Deno.test("usage requires a real ISO week, bounded writer and only capped integer counters", async () => {
  const invalid: Record<string, unknown[]> = { install_id: [null, "tiny"], writer: [null, "x".repeat(16), "a".repeat(33)], version: [null, "v1.2.3"], week: [null, "2026-W00", "2026-W54", "2025-W53", "2026-W1", "26-W41", "0000-W01"], counters: [null, [], {}, { secret: 1 }, { opens: -1 }, { opens: 1.1 }, { opens: 10001 }, { opens: "1" }, { opens: true }, { opens: null }, { errors: { save: 1 } }] };
  for (const [key, values] of Object.entries(invalid)) {
    for (const value of values) { const f = fixture(); equal((await f.send({ ...usage, [key]: value })).status, 400); equal(f.tables.usage_weeks.length, 0); }
    const f = fixture(), row: Record<string, unknown> = { ...usage }; delete row[key]; equal((await f.send(row)).status, 400);
  }
  const f = fixture(); equal((await f.send({ ...usage, text: "extra" })).status, 400);
  for (const week of ["2026-W53", "2020-W53", "2026-W01"]) { const g = fixture(); equal((await g.send({ ...usage, week, counters: { opens: 0, errors_other: 10000 } })).status, 200); }
});

Deno.test("learning duplicates acknowledge immutable records and distinct writers remain separate", async () => {
  const f = fixture();
  equal(await (await f.send(feedback)).json(), { ok: true, receipt: { id: feedback.id }, duplicate: false });
  equal(await (await f.send({ ...feedback, text: "Retry changed" })).json(), { ok: true, receipt: { id: feedback.id }, duplicate: true });
  equal(f.tables.feedback_reports[0].text, feedback.text);
  equal((await f.send({ ...feedback, install_id: "b".repeat(16) })).status, 409);
  equal((await f.send(usage)).status, 200);
  equal(await (await f.send({ ...usage, counters: { opens: 99 } })).json(), { ok: true, receipt: { install_id: usage.install_id, week: usage.week, writer: usage.writer }, duplicate: true });
  equal(f.tables.usage_weeks[0].counters, usage.counters);
  equal((await f.send({ ...usage, writer: "b".repeat(16) })).status, 200);
  equal(f.tables.usage_weeks.length, 2);
});

Deno.test("delete receipts count all four tables and leave other installations alone", async () => {
  const f = fixture(); await f.send(feedback); await f.send(usage); await f.send(install);
  await f.send({ kind: "ping", id: install.install_id, service: "usmc", path: "eas", grade: "e67", version: "0.1.3" });
  await f.send({ ...feedback, id: "other_report", install_id: "b".repeat(16) });
  equal(await (await f.send({ kind: "delete", install_id: install.install_id })).json(), { ok: true, deleted: { setup_pings: 1, install_registrations: 1, feedback_reports: 1, usage_weeks: 1 } });
  equal(f.tables.feedback_reports.length, 1);
  equal(await (await f.send({ kind: "delete", id: install.install_id })).json(), { ok: true, deleted: { setup_pings: 0, install_registrations: 0, feedback_reports: 0, usage_weeks: 0 } });
  for (const body of [{ kind: "delete", id: "bad" }, { kind: "delete", id: install.install_id, text: "extra" }, { kind: "delete", id: install.install_id, install_id: "b".repeat(16) }]) { const g = fixture(); equal((await g.send(body)).status, 400); }
  const g = fixture(); g.fail("feedback_reports"); const res = await g.send({ kind: "delete", id: install.install_id }); equal(res.status, 500); equal((await res.json()).deleted, { setup_pings: 0, install_registrations: 0 });
});

Deno.test("per-kind learning ceilings use namespaced hashed IPs and the global ceiling still applies", async () => {
  for (const [body, cap] of [[feedback, 5], [usage, 10], [{ kind: "delete", id: install.install_id }, 5]] as const) {
    const f = fixture(); const responses = await Promise.all(Array.from({ length: cap + 2 }, () => f.send(body)));
    equal(responses.filter(r => r.status === 200).length, cap); equal(responses.filter(r => r.status === 429).length, 2);
    assert(f.tables.ingest_rate.some(r => String(r.ip_hash).startsWith(`learn:${body.kind}:`)));
    assert(!JSON.stringify(f.tables.ingest_rate).includes("192.0.2.1"));
  }
  const f = fixture(); for (let i = 0; i < 20; i++) await f.send({ kind: "intent", product: "musterout", version: "0.1.4" }); equal((await f.send(usage)).status, 429);
});

Deno.test("learning GETs, body oversize bytes, malformed JSON and dependency failures fail closed", async () => {
  const f = fixture();
  for (const kind of ["feedback", "usage"]) equal((await f.handler(new Request(`https://endpoint.invalid/ingest?kind=${kind}`))).status, 400);
  for (const body of ["{", "null", "[]"]) { const g = fixture(); equal((await g.handler(new Request("https://endpoint.invalid/ingest", { method: "POST", body }))).status, 400); }
  equal((await fixture().handler(new Request("https://endpoint.invalid/ingest", { method: "POST", body: "é".repeat(10001) }))).status, 413);
  for (const [table, body] of [["feedback_reports", feedback], ["usage_weeks", usage], ["setup_pings", { kind: "ping", id: install.install_id, service: "usmc", path: "eas", grade: "e67", version: "0.1.4" }]] as const) { const g = fixture(); g.fail(table); const res = await g.send(body); equal(res.status, 500); assert(!(await res.text()).includes("private detail")); }
  const missing = createHandler({ db: {}, env: () => undefined }); equal((await missing(new Request("https://endpoint.invalid/ingest", { method: "POST", body: "{}" }))).status, 503);
  equal((await fixture().handler(new Request("https://endpoint.invalid/ingest", { method: "PUT" }))).status, 405);
});

Deno.test("rate kind dependency, duplicate lookup, delete counts, invalid UTF-8 and thrown failures are bounded", async () => {
  for (const mode of ["ingest_rate_kind", "ingest_rate_bad_data"]) { const f = fixture(); f.fail(mode); const r = await f.send(feedback); equal(r.status, 503); equal((await r.json()).error, "unavailable"); }
  const f = fixture(); await f.send(feedback); f.fail("feedback_reports:select"); equal((await f.send(feedback)).status, 500);
  const g = fixture(); g.fail("bad_count"); const r = await g.send({ kind: "delete", id: install.install_id }); equal(r.status, 500); equal((await r.json()).deleted, {});
  const h = fixture(); h.fail("throw"); const failed = await h.send(feedback); equal(failed.status, 503); assert(!(await failed.text()).includes("private detail"));
  const bad = await fixture().handler(new Request("https://endpoint.invalid/ingest", { method: "POST", body: new Uint8Array([0xff,0xfe]) })); equal(bad.status, 400);
});

Deno.test("weekly per-IP and global ceilings reject with stable overflow counters, reset by server week", async () => {
  for (const [body, ipCap, globalCap, table] of [[feedback, 20, 90, "feedback_reports"], [usage, 100, 2000, "usage_weeks"]] as const) {
    const f = fixture();
    for (let i = 0; i < ipCap; i++) {
      f.advance(60001);
      equal((await f.send({ ...body, ...(body.kind === "feedback" ? { id: `budget_${i.toString().padStart(8, "0")}` } : { writer: i.toString(16).padStart(16, "0") }) })).status, 200);
    }
    f.advance(60001);
    const denied = await f.send(body); equal(denied.status, 429); equal(await denied.json(), { ok: false, error: "budget_exceeded" });
    equal(f.tables[table].length, ipCap);
    equal(Object.values(f.budgets).filter(b => b.overflow === 1).length, 2);
    const g = fixture();
    for (let i = 0; i <= globalCap; i++) {
      const r = await g.send({ ...body, ...(body.kind === "feedback" ? { id: `global_${i.toString().padStart(8, "0")}` } : { writer: i.toString(16).padStart(16, "0") }) }, "", `192.0.${Math.floor(i / 250)}.${i % 250}`);
      equal(r.status, i === globalCap ? 429 : 200);
    }
    equal(g.tables[table].length, globalCap);
    equal(Object.keys(g.budgets).length, globalCap + 1);
    equal(Object.entries(g.budgets).find(([key]) => key.endsWith(":global"))![1].overflow, 1);
    g.advance(7 * 86400000); equal((await g.send({ ...body, ...(body.kind === "feedback" ? { id: "next_week_report" } : { writer: "f".repeat(16) }) })).status, 200);
  }
});

Deno.test("correlated new IDs quarantine retroactively across kinds; established IDs and old cohorts remain separate", async () => {
  const f = fixture();
  for (let i = 0; i < 10; i++) {
    f.advance(60001);
    const install_id = (i + 1).toString(16).padStart(16, "0");
    equal((await f.send({ ...feedback, install_id, id: `cohort_${i.toString().padStart(8, "0")}` }, "")).status, 200);
    equal((await f.send({ ...usage, install_id, writer: install_id }, "")).status, 200);
  }
  equal(f.tables.learn_install_cohorts.filter(r => r.quarantined).length, 10);
  equal(f.tables.feedback_reports.filter(r => !f.tables.learn_install_cohorts.find(c => c.install_id === r.install_id)!.quarantined).length, 0);
  const g = fixture();
  for (let i = 0; i < 6; i++) { g.advance(3600001); equal((await g.send({ ...usage, install_id: (i + 1).toString(16).padStart(16, "0") })).status, 200); }
  equal(g.tables.learn_install_cohorts.filter(r => r.quarantined).length, 0);
  // New IPs cannot change an established ID's original correlation record.
  g.advance(60001); await g.send(usage, "", "192.0.2.9");
  const first = g.tables.learn_install_cohorts.find(r => r.install_id === usage.install_id)!;
  g.advance(60001); await g.send(usage, "", "192.0.2.10"); equal(g.tables.learn_install_cohorts.find(r => r.install_id === usage.install_id), first);
  await f.send({ kind: "delete", id: f.tables.learn_install_cohorts[0].install_id }); equal(f.tables.learn_install_cohorts.length, 9);
});

Deno.test("escaped text budget prevents prompt overflow, invalid payloads spend no budget, dependencies fail closed", async () => {
  const f = fixture();
  for (let i = 0; i < 9; i++) {
    const r = await f.send({ ...feedback, id: `text_${i.toString().padStart(8, "0")}`, text: "\u{10000}".repeat(1000) }, "", `192.0.2.${i + 1}`);
    equal(r.status, i < 8 ? 200 : 429);
  }
  equal(f.tables.feedback_reports.length, 8);
  equal(Object.keys(f.budgets).length, 9);
  equal(Object.entries(f.budgets).find(([key]) => key.endsWith(":global"))![1].text_units, 96016);
  const g = fixture(); equal((await g.send({ ...feedback, category: "unknown" })).status, 400); equal(Object.keys(g.budgets).length, 0);
  for (const mode of ["abuse", "abuse_shape"]) { const h = fixture(); h.fail(mode); for (const body of [feedback, usage]) { const r = await h.send(body); equal(r.status, 503); equal((await r.json()).error, "unavailable"); } equal(h.tables.feedback_reports.length + h.tables.usage_weeks.length, 0); }
});

Deno.test("correlation deletion failure preserves the complete source deletion receipt", async () => {
  const f = fixture(); await f.send(feedback); await f.send(usage);
  f.fail("learn_install_cohorts"); const r = await f.send({ kind: "delete", id: feedback.install_id });
  equal(r.status, 500); equal((await r.json()).deleted, { setup_pings: 0, install_registrations: 0, feedback_reports: 1, usage_weeks: 1 });
  equal(f.tables.learn_install_cohorts.length, 1);
  f.fail(""); equal((await f.send({ kind: "delete", id: feedback.install_id })).status, 200); equal(f.tables.learn_install_cohorts.length, 0);
});

Deno.test("legacy install and intent reject extra identity fields, protected v2 install needs capability deletion", async () => {
 for (const body of [{...install,name:"Private"},{kind:"intent",product:"musterout",version:"0.2.9",email:"private@example.invalid"}]) {const f=fixture();equal((await f.send(body)).status,400);equal(f.tables.install_registrations.length+f.tables.setup_intents.length,0);}
 const f=fixture();f.tables.telemetry_admissions.push({install_id:install.install_id});equal((await f.send({kind:"delete",install_id:install.install_id})).status,403);
});

Deno.test("legacy ping rejects text metadata, extra keys, readable ids and duplicate query keys", async () => {
 for(const method of ["GET","POST"])for(const patch of [{version:"person@x.test"},{version:"2026-10-14"},{version:"PRIVATE NOTES"},{notes:"private"},{id:"person_name_123"},{version:"1.2.3-extra"}]){
  const f=fixture(),body={kind:"ping",id:"0123456789abcdef",service:"usmc",path:"eas",grade:"e67",version:"0.2.9",...patch};
  const response=method==="GET"?await f.handler(new Request("https://endpoint.invalid/ingest?"+new URLSearchParams(body as any))):await f.send(body);
  equal(response.status,400);equal(f.tables.setup_pings.length,0);
 }
 const f=fixture();equal((await f.handler(new Request("https://endpoint.invalid/ingest?kind=ping&kind=ping"))).status,400);
});
Deno.test("legacy telemetry address hash is domain separated from subscriber hashes",async()=>{
 const f=fixture();await f.send({kind:"ping",id:"0123456789abcdef",service:"usmc",path:"eas",grade:"e67",version:"0.2.9"});
 const raw=new TextEncoder().encode("test-salt"+"192.0.2.1"),old=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",raw))).slice(0,12).map(b=>b.toString(16).padStart(2,"0")).join("");
 assert(f.tables.setup_pings[0].ip_hash!==old);
});
