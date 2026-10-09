// Muster Out ingest: the only write path into the telemetry tables.
// POST JSON {kind: "lesson" | "ping" | "delete", ...}; GET ?kind=ping&service=&path=&grade=&version=&id=
// Validates shape and size, rate limits by hashed IP (20 a minute), inserts with the service role.
// No reads are served here. Deploy with --no-verify-jwt; the anon key alone cannot touch the tables.
import { createClient } from "npm:@supabase/supabase-js@2";

const SERVICES = ["usmc"];
const PATHS = ["resign", "retire", "eas", "unsure"];
const GRADES = ["o5", "o14", "cwo45", "wo13", "e89", "e67", "e15", "unsure"];
const CORS = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "content-type" };
const json = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers: { ...CORS, "content-type": "application/json" } });
const short = (v: unknown, n: number) => (typeof v === "string" ? v.slice(0, n) : null);
const idOk = (v: unknown) => typeof v === "string" && /^[A-Za-z0-9_-]{8,64}$/.test(v);

async function ipHash(req: Request): Promise<string> {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0].trim() || "0";
  const salt = Deno.env.get("INGEST_SALT") || "musterout";
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(salt + ip));
  return Array.from(new Uint8Array(buf)).slice(0, 12).map((b) => b.toString(16).padStart(2, "0")).join("");
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
  const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
  const ip = await ipHash(req);

  // rate limit: 20 writes a minute per hashed address
  const minute = new Date(Math.floor(Date.now() / 60000) * 60000).toISOString();
  const { data: rate } = await db.from("ingest_rate").select("n").eq("ip_hash", ip).eq("minute", minute).maybeSingle();
  const n = (rate?.n ?? 0) + 1;
  if (n > 20) return json(429, { ok: false, error: "rate_limited" });
  await db.from("ingest_rate").upsert({ ip_hash: ip, minute, n });

  let body: Record<string, unknown> = {};
  if (req.method === "GET") {
    const u = new URL(req.url); u.searchParams.forEach((v, k) => { body[k] = v; });
  } else if (req.method === "POST") {
    const text = await req.text(); if (text.length > 20000) return json(413, { ok: false, error: "too_large" });
    try { body = JSON.parse(text); } catch { return json(400, { ok: false, error: "bad_json" }); }
  } else return json(405, { ok: false, error: "method" });

  if (body.kind === "ping") {
    const service = short(body.service, 16), path = short(body.path, 16), grade = short(body.grade, 16), version = short(body.version, 16), id = body.id ?? body.install_id;
    if (!SERVICES.includes(service ?? "") || !PATHS.includes(path ?? "") || !GRADES.includes(grade ?? "") || !version || !idOk(id)) return json(400, { ok: false, error: "bad_ping" });
    const { error } = await db.from("setup_pings").upsert({ install_id: id as string, service, path, grade, version, ip_hash: ip }, { onConflict: "install_id", ignoreDuplicates: true });
    if (error) return json(500, { ok: false, error: "write" });
    return json(200, { ok: true });
  }

  if (body.kind === "lesson") {
    const token = body.token;
    if (!idOk(token)) return json(400, { ok: false, error: "bad_token" });
    const score = Number.isInteger(body.score) && (body.score as number) >= 0 && (body.score as number) <= 20 ? (body.score as number) : null;
    const answers = body.answers && typeof body.answers === "object" && JSON.stringify(body.answers).length < 4000 ? body.answers : null;
    const row = { token: token as string, nickname: short(body.nickname, 40), score, answers, reflection: short(body.reflection, 600), go_deeper: typeof body.go_deeper === "boolean" ? body.go_deeper : null, sections_done: Number.isInteger(body.sections_done) ? (body.sections_done as number) : null, version: short(body.version, 16), ip_hash: ip };
    const { error } = await db.from("lesson_responses").insert(row);
    if (error) return json(500, { ok: false, error: "write" });
    return json(200, { ok: true });
  }

  if (body.kind === "delete") {
    // the study token is the deletion receipt for a lesson response; the install id is the receipt for a count
    const token = body.token, id = body.id ?? body.install_id;
    if (!idOk(token) && !idOk(id)) return json(400, { ok: false, error: "bad_token" });
    if (idOk(token)) {
      const { error } = await db.from("lesson_responses").delete().eq("token", token as string);
      if (error) return json(500, { ok: false, error: "write" });
    }
    if (idOk(id)) {
      const { error } = await db.from("setup_pings").delete().eq("install_id", id as string);
      if (error) return json(500, { ok: false, error: "write" });
    }
    return json(200, { ok: true });
  }

  return json(400, { ok: false, error: "kind" });
});
