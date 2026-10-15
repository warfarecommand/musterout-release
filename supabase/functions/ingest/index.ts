// Muster Out ingest: the only write path into the telemetry tables.
// POST JSON {kind: "ping" | "intent" | "install" | "feedback" | "usage" | "delete", ...}; GET ?kind=ping&service=&path=&grade=&version=&id=
// Validates shape and size, rate limits by hashed IP (20 a minute plus learning kind caps), inserts with the service role.
// No reads are served here. Deploy with --no-verify-jwt; the anon key alone cannot touch the tables.
import { telemetryV2 } from "../_shared/telemetry_v2.ts";
import { BodyReadError, readBody } from "../_shared/body.ts";

const SERVICES = ["usmc"];
const PATHS = ["resign", "retire", "eas", "unsure"];
const GRADES = ["o5", "o14", "cwo45", "wo13", "e89", "e67", "e15", "unsure"];
const ORIGINS = ["https://warfarecommand.com", "https://www.warfarecommand.com", "https://musterout.warfarecommand.com"];
const PRODUCTS = ["musterout"];
const CHANNELS = ["chat", "laptop"];
const versionOk = (v: unknown) => typeof v === "string" && v.length <= 32 && /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.test(v);
const installIdOk = (v: unknown) => typeof v === "string" && /^[a-f0-9]{16,32}$/.test(v);
const CORS = { "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "content-type", "Vary": "Origin" };
const legacyInstallIdOk = (v: unknown) => installIdOk(v) || typeof v === "string" && /^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(v);
const idOk = (v: unknown) => typeof v === "string" && /^[A-Za-z0-9_-]{8,64}$/.test(v);

// Learning schema v1. Update consent before changing keys or meanings.
export const COUNTER_KEYS = ["opens", "tab_today", "tab_plan", "tab_dates", "tab_claim", "items_done", "drawers_opened", "update_taps", "errors_save", "errors_update", "errors_feed", "errors_storage", "errors_sample", "errors_other"];
export const CATEGORIES = ["bug", "content", "usability", "other"];
export const ERROR_CLASSES = ["none", "save", "update", "feed", "storage", "sample", "unavailable", "other"];
const learningVersionOk = (v: unknown) => typeof v === "string" && v.length <= 64 && /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$/.test(v);
const exactKeys = (body: Record<string, unknown>, keys: string[]) => Object.keys(body).every(k => keys.includes(k));
const plainObject = (v: unknown): v is Record<string, unknown> => !!v && typeof v === "object" && !Array.isArray(v);
export function weekOk(v: unknown): boolean {
  if (typeof v !== "string" || !/^[2-9]\d{3}-W(0[1-9]|[1-4]\d|5[0-3])$/.test(v)) return false;
  if (!v.endsWith("W53")) return true;
  const year = Number(v.slice(0, 4)), first = new Date(Date.UTC(year, 0, 1)).getUTCDay();
  return first === 4 || (first === 3 && year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0));
}
export function countersOk(v: unknown): boolean {
  return plainObject(v) && Object.keys(v).length > 0 && Object.entries(v).every(([key, n]) => COUNTER_KEYS.includes(key) && typeof n === "number" && Number.isInteger(n) && n >= 0 && n <= 10000);
}
const createdOk = (v: unknown, now: number) => typeof v === "string" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/.test(v) && Number.isFinite(Date.parse(v)) && new Date(Date.parse(v)).toISOString().replace(".000Z", "Z") === v.replace(".000Z", "Z") && Date.parse(v) <= now + 300000;
const stripControls = (s: string) => s.replace(/[\u0000-\u001f\u007f-\u009f]/g, "");

async function ipHash(req: Request, env: (name: string) => string | undefined): Promise<string> {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0].trim() || "0";
  const salt = env("IP_HASH_SALT") || env("INGEST_SALT");
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode("musterout-legacy-telemetry-v2\n" + salt + "\n" + ip));
  return Array.from(new Uint8Array(buf)).slice(0, 12).map((b) => b.toString(16).padStart(2, "0")).join("");
}

// The production client is loaded only by the Deno entrypoint; tests inject a database.
export function createHandler(deps: { env: (name: string) => string | undefined; db: any; now?: () => number; bodyDeadlineMs?: number }) {
 return async (req: Request): Promise<Response> => {
  const origin = req.headers.get("origin");
  const cors = { ...CORS, ...(origin && ORIGINS.includes(origin) ? { "Access-Control-Allow-Origin": origin } : {}) };
  const json = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers: { ...cors, "content-type": "application/json", "Cache-Control": "no-store" } });
  if (origin && !ORIGINS.includes(origin)) return json(403, { ok: false, error: "origin" });
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
  if (Number(req.headers.get("content-length")) > 20000) return json(413, { ok: false, error: "too_large" });
  try {
  // Read, decode, and parse before even accessing the injected database.
  let body: Record<string, unknown> = {};
  let rawBody = "";
  if (req.method === "GET") {
    const u = new URL(req.url); for (const [k,v] of u.searchParams) { if(Object.hasOwn(body,k))return json(400,{ok:false,error:"bad_input"});body[k]=v; }
  } else if (req.method === "POST") {
    const text = await readBody(req.body, 20000, deps.bodyDeadlineMs);
    rawBody = text;
    try { body = JSON.parse(text); if (!body || typeof body !== "object" || Array.isArray(body)) throw new Error("shape"); }
    catch { return json(400, { ok: false, error: "bad_json" }); }
  } else return json(405, { ok: false, error: "method" });

  if (body.kind === "enroll" || ["schema_version", "records", "access"].some(k => Object.hasOwn(body, k))) return await telemetryV2(req, rawBody, deps, json);

  const db = deps.db;
  if (!deps.env("IP_HASH_SALT") && !deps.env("INGEST_SALT")) return json(503, { ok: false, error: "not_configured" });
  const ip = await ipHash(req, deps.env);

  // rate limit: 20 writes a minute per hashed address
  const minute = new Date(Math.floor((deps.now?.() ?? Date.now()) / 60000) * 60000).toISOString();
  const { data: n, error: rateError } = await db.rpc("ingest_rate_hit", { p_ip_hash: ip, p_minute: minute });
  if (rateError || !Number.isInteger(n) || n < 1) return json(503, { ok: false, error: "unavailable" });
  if (n > 20) return json(429, { ok: false, error: "rate_limited" });

  // Learning reports are POST-only and never accept URL-carried data.
  if (body.kind === "feedback" || body.kind === "usage" || body.kind === "delete") {
    if (body.kind !== "delete" && req.method !== "POST") return json(400, { ok: false, error: "bad_input" });
    const ceiling = body.kind === "feedback" ? 5 : body.kind === "usage" ? 10 : 5;
    const { data: hits, error } = await db.rpc("ingest_rate_hit", { p_ip_hash: `learn:${body.kind}:${ip}`, p_minute: minute });
    if (error || !Number.isInteger(hits) || hits < 1) return json(503, { ok: false, error: "unavailable" });
    if (hits > ceiling) return json(429, { ok: false, error: "rate_limited" });
  }

  // Reserve before insertion. Database time and fixed ceilings are authoritative;
  // duplicate requests and failed writes conservatively consume admission budget.
  const admit = async (text: string | null = null): Promise<Response | null> => {
    // Python ensure_ascii text encoding uses at most 12 bytes per astral scalar.
    const textUnits = text === null ? 0 : JSON.stringify(text).replace(/[\u007f-\uffff]/g, c => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0")).length;
    const result = await db.rpc("learn_abuse_admit", { p_kind: body.kind, p_ip_hash: ip, p_install_id: body.install_id, p_text_units: textUnits });
    if (result.error || !result.data || typeof result.data.admitted !== "boolean" || typeof result.data.quarantined !== "boolean") return json(503, { ok: false, error: "unavailable" });
    return result.data.admitted ? null : json(429, { ok: false, error: "budget_exceeded" });
  };

  if (body.kind === "feedback") {
    const now = deps.now?.() ?? Date.now();
    if (!exactKeys(body, ["kind", "id", "install_id", "version", "pack", "path", "grade", "category", "error_class", "text", "created"]) || !idOk(body.id) || !installIdOk(body.install_id) || !learningVersionOk(body.version) || typeof body.pack !== "string" || !/^usmc-20\d{2}\.(0[1-9]|1[0-2])$/.test(body.pack) || !PATHS.includes(body.path as string) || !GRADES.includes(body.grade as string) || !CATEGORIES.includes(body.category as string) || !ERROR_CLASSES.includes(body.error_class as string) || !createdOk(body.created, now) || (body.text !== undefined && body.text !== null && (typeof body.text !== "string" || Array.from(body.text).length > 1000))) return json(400, { ok: false, error: "bad_input" });
    const row = { id: body.id, install_id: body.install_id, version: body.version, pack: body.pack, path: body.path, grade: body.grade, category: body.category, error_class: body.error_class, text: typeof body.text === "string" ? stripControls(body.text) : null, created: body.created };
    const denied = await admit(row.text); if (denied) return denied;
    const { error } = await db.from("feedback_reports").insert(row);
    if (error?.code === "23505") {
      const existing = await db.from("feedback_reports").select("install_id").eq("id", body.id).maybeSingle();
      if (existing.error) return json(500, { ok: false, error: "write" });
      if (existing.data?.install_id !== body.install_id) return json(409, { ok: false, error: "id_conflict" });
    } else if (error) return json(500, { ok: false, error: "write" });
    return json(200, { ok: true, receipt: { id: body.id }, duplicate: !!error });
  }

  if (body.kind === "usage") {
    if (!exactKeys(body, ["kind", "install_id", "week", "writer", "version", "counters"]) || !installIdOk(body.install_id) || !installIdOk(body.writer) || !learningVersionOk(body.version) || !weekOk(body.week) || !countersOk(body.counters)) return json(400, { ok: false, error: "bad_input" });
    const denied = await admit(); if (denied) return denied;
    const { error } = await db.from("usage_weeks").insert({ install_id: body.install_id, week: body.week, writer: body.writer, version: body.version, counters: body.counters });
    if (error && error.code !== "23505") return json(500, { ok: false, error: "write" });
    return json(200, { ok: true, receipt: { install_id: body.install_id, week: body.week, writer: body.writer }, duplicate: !!error });
  }

  if (body.kind === "intent" || body.kind === "install") {
    if (!exactKeys(body, body.kind === "intent" ? ["kind","product","version"] : ["kind","product","version","path","grade","channel","install_id"])) return json(400, {ok:false,error:"bad_input"});
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
    const service=body.service,path=body.path,grade=body.grade,version=body.version,id=body.id ?? body.install_id;
    if(!exactKeys(body,["kind","service","path","grade","version","id","install_id"]) || !SERVICES.includes(service as string) || !PATHS.includes(path as string) || !GRADES.includes(grade as string) || !versionOk(version) || !legacyInstallIdOk(id) || body.id!==undefined && body.install_id!==undefined && body.id!==body.install_id)return json(400,{ok:false,error:"bad_ping"});
    const { error } = await db.from("setup_pings").upsert({ install_id: id as string, service, path, grade, version, ip_hash: ip }, { onConflict: "install_id", ignoreDuplicates: true });
    if (error) return json(500, { ok: false, error: "write" });
    return json(200, { ok: true });
  }

  if (body.kind === "delete") {
    const id = body.id ?? body.install_id;
    if (!exactKeys(body, ["kind", "id", "install_id"]) || !idOk(id) || (body.id !== undefined && body.install_id !== undefined && body.id !== body.install_id)) return json(400, { ok: false, error: "bad_token" });
    const protectedInstall = await db.from("telemetry_admissions").select("install_id").eq("install_id", id as string).maybeSingle();
    if (protectedInstall.error) return json(503, {ok:false,error:"unavailable"});
    if (protectedInstall.data) return json(403, {ok:false,error:"capability_required"});
    const deleted: Record<string, number> = {};
    for (const table of ["setup_pings", "install_registrations", "feedback_reports", "usage_weeks"]) {
      const { error, count } = await db.from(table).delete({ count: "exact" }).eq("install_id", id as string);
      if (error || !Number.isInteger(count) || count < 0) return json(500, { ok: false, error: "write", deleted });
      deleted[table] = count;
    }
    // Remove the private correlation record without changing the four-table receipt.
    const correlation = await db.from("learn_install_cohorts").delete().eq("install_id", id as string);
    if (correlation.error) return json(500, { ok: false, error: "write", deleted });
    return json(200, { ok: true, deleted });
  }

  return json(400, { ok: false, error: "kind" });
  } catch (error) {
    if (error instanceof BodyReadError) return json(error.status, { ok: false, error: error.code });
    return json(503, { ok: false, error: "unavailable" });
  }
 };
}

if (import.meta.main) {
  const { createClient } = await import("npm:@supabase/supabase-js@2");
  const env = (name: string) => Deno.env.get(name);
  const db = createClient(env("SUPABASE_URL")!, env("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
  Deno.serve(createHandler({ env, db }));
}
