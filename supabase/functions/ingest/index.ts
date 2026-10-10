// Muster Out ingest: the only write path into the telemetry tables.
// POST JSON {kind: "ping" | "intent" | "install" | "delete", ...}; GET ?kind=ping&service=&path=&grade=&version=&id=
// Validates shape and size, rate limits by hashed IP (20 a minute), inserts with the service role.
// No reads are served here. Deploy with --no-verify-jwt; the anon key alone cannot touch the tables.

const SERVICES = ["usmc"];
const PATHS = ["resign", "retire", "eas", "unsure"];
const GRADES = ["o5", "o14", "cwo45", "wo13", "e89", "e67", "e15", "unsure"];
const ORIGINS = ["https://warfarecommand.com", "https://www.warfarecommand.com", "https://musterout.warfarecommand.com"];
const PRODUCTS = ["musterout"];
const CHANNELS = ["chat", "laptop"];
const versionOk = (v: unknown) => typeof v === "string" && v.length <= 32 && /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.test(v);
const installIdOk = (v: unknown) => typeof v === "string" && /^[a-f0-9]{16,32}$/.test(v);
const CORS = { "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "content-type", "Vary": "Origin" };
const short = (v: unknown, n: number) => (typeof v === "string" ? v.slice(0, n) : null);
const idOk = (v: unknown) => typeof v === "string" && /^[A-Za-z0-9_-]{8,64}$/.test(v);

async function ipHash(req: Request, env: (name: string) => string | undefined): Promise<string> {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0].trim() || "0";
  const salt = env("IP_HASH_SALT") || env("INGEST_SALT");
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(salt + ip));
  return Array.from(new Uint8Array(buf)).slice(0, 12).map((b) => b.toString(16).padStart(2, "0")).join("");
}

// The production client is loaded only by the Deno entrypoint; tests inject a database.
export function createHandler(deps: { env: (name: string) => string | undefined; db: any; now?: () => number }) {
 return async (req: Request): Promise<Response> => {
  const origin = req.headers.get("origin");
  const cors = { ...CORS, ...(origin && ORIGINS.includes(origin) ? { "Access-Control-Allow-Origin": origin } : {}) };
  const json = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers: { ...cors, "content-type": "application/json", "Cache-Control": "no-store" } });
  if (origin && !ORIGINS.includes(origin)) return json(403, { ok: false, error: "origin" });
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
  if (Number(req.headers.get("content-length")) > 20000) return json(413, { ok: false, error: "too_large" });
  try {
  const db = deps.db;
  if (!deps.env("IP_HASH_SALT") && !deps.env("INGEST_SALT")) return json(503, { ok: false, error: "not_configured" });
  const ip = await ipHash(req, deps.env);

  // rate limit: 20 writes a minute per hashed address
  const minute = new Date(Math.floor((deps.now?.() ?? Date.now()) / 60000) * 60000).toISOString();
  const { data: n, error: rateError } = await db.rpc("ingest_rate_hit", { p_ip_hash: ip, p_minute: minute });
  if (rateError || !Number.isInteger(n) || n < 1) return json(503, { ok: false, error: "unavailable" });
  if (n > 20) return json(429, { ok: false, error: "rate_limited" });

  let body: Record<string, unknown> = {};
  if (req.method === "GET") {
    const u = new URL(req.url); u.searchParams.forEach((v, k) => { body[k] = v; });
  } else if (req.method === "POST") {
    const text = await req.text(); if (text.length > 20000) return json(413, { ok: false, error: "too_large" });
    try { body = JSON.parse(text); if (!body || typeof body !== "object" || Array.isArray(body)) throw new Error("shape"); } catch { return json(400, { ok: false, error: "bad_json" }); }
  } else return json(405, { ok: false, error: "method" });

  if (body.kind === "intent" || body.kind === "install") {
    if (req.method !== "POST" || !PRODUCTS.includes(body.product as string) || !versionOk(body.version)) return json(400, { ok: false, error: "bad_input" });
    const row = { product: body.product, version: body.version, ip_hash: ip };
    if (body.kind === "intent") {
      const { error } = await db.from("setup_intents").insert(row);
      if (error) return json(500, { ok: false, error: "write" });
    } else {
      if (!PATHS.slice(0, 3).includes(body.path as string) || !GRADES.slice(0, 7).includes(body.grade as string) || !CHANNELS.includes(body.channel as string) || !installIdOk(body.install_id)) return json(400, { ok: false, error: "bad_input" });
      const { error } = await db.from("install_registrations").upsert({ ...row, path: body.path, grade: body.grade, channel: body.channel, install_id: body.install_id }, { onConflict: "install_id", ignoreDuplicates: true });
      if (error) return json(500, { ok: false, error: "write" });
    }
    return json(200, { ok: true });
  }

  if (body.kind === "ping") {
    const service = short(body.service, 16), path = short(body.path, 16), grade = short(body.grade, 16), version = short(body.version, 16), id = body.id ?? body.install_id;
    if (!SERVICES.includes(service ?? "") || !PATHS.includes(path ?? "") || !GRADES.includes(grade ?? "") || !version || !idOk(id)) return json(400, { ok: false, error: "bad_ping" });
    const { error } = await db.from("setup_pings").upsert({ install_id: id as string, service, path, grade, version, ip_hash: ip }, { onConflict: "install_id", ignoreDuplicates: true });
    if (error) return json(500, { ok: false, error: "write" });
    return json(200, { ok: true });
  }

  if (body.kind === "delete") {
    // The install id is the deletion receipt for a count.
    const id = body.id ?? body.install_id;
    if (!idOk(id)) return json(400, { ok: false, error: "bad_token" });
    if (idOk(id)) {
      for (const table of ["setup_pings", "install_registrations"]) {
        const { error } = await db.from(table).delete().eq("install_id", id as string);
        if (error) return json(500, { ok: false, error: "write" });
      }
    }
    return json(200, { ok: true });
  }

  return json(400, { ok: false, error: "kind" });
  } catch { return json(503, { ok: false, error: "unavailable" }); }
 };
}

if (import.meta.main) {
  const { createClient } = await import("npm:@supabase/supabase-js@2");
  const env = (name: string) => Deno.env.get(name);
  const db = createClient(env("SUPABASE_URL")!, env("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
  Deno.serve(createHandler({ env, db }));
}
