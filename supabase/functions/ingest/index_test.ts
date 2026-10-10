import { createHandler } from "./index.ts";
const assert = (ok: unknown, message = "Assertion failed") => { if (!ok) throw new Error(message); };
const equal = (a: unknown, b: unknown) => assert(JSON.stringify(a) === JSON.stringify(b), `${JSON.stringify(a)} differs from ${JSON.stringify(b)}`);

function fixture() {
  const tables: Record<string, Record<string, unknown>[]> = { ingest_rate: [], setup_intents: [], install_registrations: [], setup_pings: [], lesson_responses: [] };
  let fail = "";
  const db = { from: (table: string) => {
    const filters: [string, unknown][] = [];
    let operation = "select", value: Record<string, unknown> = {}, options: { ignoreDuplicates?: boolean } = {};
    const query = {
      select: () => query,
      eq: (key: string, v: unknown) => { filters.push([key, v]); return query; },
      maybeSingle: async () => ({ data: tables[table].find(row => filters.every(([key, v]) => row[key] === v)), error: fail === table ? {} : null }),
      insert: (row: Record<string, unknown>) => { operation = "insert"; value = row; return query; },
      upsert: (row: Record<string, unknown>, opts = {}) => { operation = "upsert"; value = row; options = opts; return query; },
      delete: () => { operation = "delete"; return query; },
      then: (resolve: (v: unknown) => unknown) => {
        if (fail === table) return Promise.resolve({ error: { message: "private detail" } }).then(resolve);
        if (operation === "delete") tables[table] = tables[table].filter(row => !filters.every(([key, v]) => row[key] === v));
        else if (operation === "insert") tables[table].push(structuredClone(value));
        else if (operation === "upsert") {
          const existing = tables[table].find(row => table === "ingest_rate" ? row.ip_hash === value.ip_hash && row.minute === value.minute : row.install_id === value.install_id);
          if (!existing) tables[table].push(structuredClone(value));
          else if (!options.ignoreDuplicates) Object.assign(existing, value);
        }
        return Promise.resolve({ error: null }).then(resolve);
      }
    };
    return query;
  } };
  const handler = createHandler({ db, env: name => name === "INGEST_SALT" ? "test-salt" : undefined, now: () => Date.parse("2026-10-09T21:00:00Z") });
  const send = (body: unknown, origin = "https://musterout.warfarecommand.com") => handler(new Request("https://endpoint.invalid/ingest", { method: "POST", headers: { origin, "x-forwarded-for": "192.0.2.1" }, body: JSON.stringify(body) }));
  return { tables, handler, send, fail: (table: string) => { fail = table; } };
}
const install = { kind: "install", product: "musterout", version: "0.1.4", path: "eas", grade: "e67", channel: "chat", install_id: "0123456789abcdef0123456789abcdef" };

Deno.test("intent accepts both origins and stores only anonymous allowed fields", async () => {
  for (const origin of ["https://warfarecommand.com", "https://musterout.warfarecommand.com"]) {
    const f = fixture();
    const preflight = await f.handler(new Request("https://endpoint.invalid/ingest", { method: "OPTIONS", headers: { origin } }));
    equal(preflight.headers.get("access-control-allow-origin"), origin);
    const response = await f.send({ kind: "intent", product: "musterout", version: "0.1.4", name: "discard", install_id: "discard" }, origin);
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
  equal((await f.send({ ...install, board_url: "Never store this", name: "Discard" })).status, 200);
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

Deno.test("legacy ping, lesson and receipt deletion still work without a browser origin", async () => {
  const f = fixture();
  const ping = await f.handler(new Request("https://endpoint.invalid/ingest?kind=ping&service=usmc&path=unsure&grade=unsure&version=0.1.3&id=legacy-uuid-1234"));
  equal(ping.status, 200);
  equal(f.tables.setup_pings.length, 1);
  equal((await f.send({ kind: "lesson", token: "study-token-123", score: 4, reflection: "Test reflection", version: "1" })).status, 200);
  equal((await f.send({ kind: "delete", token: "study-token-123", id: "legacy-uuid-1234" })).status, 200);
  equal(f.tables.lesson_responses.length, 0);
  equal(f.tables.setup_pings.length, 0);
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
