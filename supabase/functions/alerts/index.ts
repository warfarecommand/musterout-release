// Website correction alerts. Deploy with verify_jwt false. No contact sync.
// Reader: a Marine who requested alerts. Effect: confirm consent or delete the signup.
export const SITE = "https://musterout.warfarecommand.com";
export const ENDPOINT = "https://vfozrzohrdrbohjqkghk.supabase.co/functions/v1/alerts";
export const FROM = "Muster Out <updates@warfarecommand.com>";
export const RECENT_HASHES = 8;
const CORS = { "Access-Control-Allow-Origin": SITE, "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "content-type", "Vary": "Origin" };
const json = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers: { ...CORS, "content-type": "application/json", "Cache-Control": "no-store" } });
const redirect = (page: string) => new Response(null, { status: 303, headers: { Location: `${SITE}/alerts/${page}/`, "Cache-Control": "no-store", "Referrer-Policy": "no-referrer" } });
const success = () => json(200, { ok: true });
const tokenOk = (value: string) => /^[a-f0-9]{64}$/.test(value);
export type Env = (name: string) => string | undefined;
export type Row = { id: string; email: string; status: string; confirm_hash: string | null; unsubscribe_hashes: string[]; last_sent_at: string | null };

export async function hash(value: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function token(): string {
  return Array.from(crypto.getRandomValues(new Uint8Array(32))).map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function emailOk(value: string): boolean {
  return value.length >= 6 && value.length < 254 && /^[^\s@<>\x00-\x1f\x7f]+@[^\s@<>\x00-\x1f\x7f]+\.[^\s@<>\x00-\x1f\x7f]+$/.test(value);
}

export function unsubscribeHeaders(url: string): Record<string, string> {
  return { "List-Unsubscribe": `<${url}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" };
}

export function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c] as string));
}

// PostgREST only. Never return database errors, addresses, or credentials to callers.
export function database(env: Env, net: typeof fetch) {
  const url = env("SUPABASE_URL"), key = env("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !key) throw new Error("Database is not configured");
  const headers = { apikey: key, Authorization: `Bearer ${key}`, "content-type": "application/json" };
  const address = (table: string, params: Record<string, string>) => `${url}/rest/v1/${table}?${new URLSearchParams(params)}`;
  return {
    async rows<T = Row>(table: string, method: string, params: Record<string, string>, body?: unknown, prefer = "return=representation"): Promise<T[]> {
      const response = await net(address(table, params), { method, headers: { ...headers, Prefer: prefer }, body: body === undefined ? undefined : JSON.stringify(body) });
      if (!response.ok) throw new Error("Database request failed");
      if (response.status === 204) return [];
      return await response.json();
    },
    async count(): Promise<number> {
      const response = await net(address("alert_signups", { select: "id", status: "eq.confirmed" }), { method: "HEAD", headers: { ...headers, Prefer: "count=exact" } });
      const total = response.headers.get("content-range")?.split("/")[1];
      if (!response.ok || !total || !/^\d+$/.test(total)) throw new Error("Count request failed");
      return Number(total);
    },
  };
}

type Database = ReturnType<typeof database>;

// Durable slots, separate from ingest's minute counters.
// The fixed minute is a namespace anchor. n is the next eligible Unix minute.
// Conditional PATCH and conflict-ignore INSERT reserve slots across workers.
// Rounding up can extend a one-hour wait by less than a minute.
async function reserveRate(db: Database, namespace: string, slots: number, wait: number, now: number): Promise<boolean> {
  const minute = "2000-01-01T00:00:00Z";
  const current = Math.floor(now / 60000);
  const next = Math.ceil(now / 60000) + wait;
  for (let slot = 0; slot < slots; slot++) {
    const ip_hash = `alerts:${namespace}:${slot}`;
    const where = { ip_hash: `eq.${ip_hash}`, minute: `eq.${minute}` };
    const rows = await db.rows<{ n: number }>("ingest_rate", "GET", { ...where, select: "n" });
    if (rows.length && rows[0].n > current) continue;
    const reserved = rows.length
      ? await db.rows("ingest_rate", "PATCH", { ...where, n: `eq.${rows[0].n}` }, { n: next })
      : await db.rows("ingest_rate", "POST", { on_conflict: "ip_hash,minute" }, { ip_hash, minute, n: next }, "resolution=ignore-duplicates,return=representation");
    if (reserved.length) return true;
  }
  return false;
}

export function createHandler(deps: { env: Env; fetch: typeof fetch; now?: () => number }) {
  return async (req: Request): Promise<Response> => {
    const u = new URL(req.url);
    if (req.method === "OPTIONS") {
      if (req.headers.get("origin") !== SITE) return json(403, { ok: false, error: "origin" });
      return new Response(null, { status: 204, headers: CORS });
    }
    try {
      const unsubscribe = u.searchParams.get("unsubscribe");
      if (unsubscribe !== null && (req.method === "GET" || req.method === "POST")) {
        if (tokenOk(unsubscribe)) {
          await database(deps.env, deps.fetch).rows("alert_signups", "DELETE", { unsubscribe_hashes: `cs.{${await hash(unsubscribe)}}` });
        }
        return redirect("unsubscribed");
      }
      const confirm = u.searchParams.get("confirm");
      if (confirm !== null && req.method === "GET") {
        if (!tokenOk(confirm)) return redirect("expired");
        const rows = await database(deps.env, deps.fetch).rows("alert_signups", "PATCH", { confirm_hash: `eq.${await hash(confirm)}`, status: "eq.pending" }, { status: "confirmed", confirm_hash: null, confirmed_at: new Date(deps.now?.() ?? Date.now()).toISOString() });
        return redirect(rows.length ? "confirmed" : "expired");
      }
      if (req.method !== "POST") return json(405, { ok: false, error: "method" });
      if (req.headers.get("origin") !== SITE) return json(403, { ok: false, error: "origin" });
      const text = await req.text();
      if (text.length > 2048) return json(413, { ok: false, error: "too_large" });
      let body: Record<string, unknown>;
      try {
        body = JSON.parse(text);
        if (!body || typeof body !== "object" || Array.isArray(body)) throw new Error("shape");
      } catch { return json(400, { ok: false, error: "bad_json" }); }
      if (body.kind !== "subscribe") return json(400, { ok: false, error: "kind" });
      if (body.website !== undefined && body.website !== "") return success();
      const resendKey = deps.env("RESEND_API_KEY");
      if (!resendKey) return json(503, { ok: false, error: "not_configured" });
      const salt = deps.env("IP_HASH_SALT") || deps.env("INGEST_SALT");
      if (!salt || !deps.env("SUPABASE_URL") || !deps.env("SUPABASE_SERVICE_ROLE_KEY")) return json(503, { ok: false, error: "not_configured" });
      const db = database(deps.env, deps.fetch);
      const now = deps.now?.() ?? Date.now();
      const ip = req.headers.get("x-forwarded-for")?.split(",")[0].trim() || "0";
      const ip_hash = (await hash(salt + ip)).slice(0, 24);
      if (!await reserveRate(db, `ip:${ip_hash}`, 3, 60, now)) return json(429, { ok: false, error: "rate_limited" });
      const email = typeof body.email === "string" ? body.email.trim().toLowerCase() : "";
      if (!emailOk(email)) return json(400, { ok: false, error: "bad_email" });
      // An address conflict never changes a confirmed row. Reserve pending sends
      // with last_sent_at before calling Resend, including failed send attempts.
      let addressReserved = false;
      for (let attempt = 0; attempt < 3; attempt++) {
        const existing = (await db.rows("alert_signups", "GET", { email: `eq.${email}`, select: "id,email,status,confirm_hash,unsubscribe_hashes,last_sent_at" }))[0];
        if (existing?.status === "confirmed") return success();
        if (existing?.last_sent_at && now - Date.parse(existing.last_sent_at) < 600000) return success();
        // Deleting a signup must not reset its email cooldown. This salted
        // receipt contains no address and remains outside the subscriber list.
        if (!addressReserved) {
          const addressHash = await hash(salt + "email:" + email);
          if (!await reserveRate(db, `email:${addressHash}`, 1, 10, now)) return success();
          addressReserved = true;
        }
        const confirmToken = token(), unsubscribeToken = token();
        const confirm_hash = await hash(confirmToken);
        const unsubscribe_hashes = [...(existing?.unsubscribe_hashes ?? []), await hash(unsubscribeToken)].slice(-RECENT_HASHES);
        const last_sent_at = new Date(now).toISOString();
        const fields = { status: "pending", confirm_hash, unsubscribe_hashes, ip_hash, last_sent_at };
        const reserved = existing
          ? await db.rows("alert_signups", "PATCH", { id: `eq.${existing.id}`, status: "eq.pending", last_sent_at: existing.last_sent_at ? `eq.${existing.last_sent_at}` : "is.null" }, fields)
          : await db.rows("alert_signups", "POST", { on_conflict: "email" }, { email, ...fields }, "resolution=ignore-duplicates,return=representation");
        if (!reserved.length) continue;
        const confirmUrl = `${ENDPOINT}?confirm=${confirmToken}`;
        const unsubscribeUrl = `${ENDPOINT}?unsubscribe=${unsubscribeToken}`;
        const paragraphs = ["You asked for Muster Out correction alerts and release notes.", `Confirm your email: ${confirmUrl}`, "Nothing is sent until you confirm. If you did not ask for this email, you can ignore it.", `Unsubscribe and delete your address: ${unsubscribeUrl}`];
        const html = `<p>${paragraphs[0]}</p><p><a href="${confirmUrl}">Confirm your email</a></p><p>${paragraphs[2]}</p><p><a href="${unsubscribeUrl}">Unsubscribe and delete your address</a></p>`;
        const sent = await deps.fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: `Bearer ${resendKey}`, "content-type": "application/json", "Idempotency-Key": `alerts-confirm-${confirm_hash}` }, body: JSON.stringify({ from: FROM, to: [email], subject: "Confirm Muster Out correction alerts", html, text: paragraphs.join("\n\n"), headers: unsubscribeHeaders(unsubscribeUrl) }) });
        if (!sent.ok) return json(502, { ok: false, error: "send" });
        return success();
      }
      return json(503, { ok: false, error: "retry" });
    } catch { return json(503, { ok: false, error: "unavailable" }); }
  };
}

if (import.meta.main) Deno.serve(createHandler({ env: (name) => Deno.env.get(name), fetch }));
