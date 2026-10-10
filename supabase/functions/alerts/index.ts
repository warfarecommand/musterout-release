// Website correction alerts. Deploy with verify_jwt false. No contact sync.
// Reader: a Marine who requested alerts. Effect: confirm consent or delete the signup.
export const SITE = "https://musterout.warfarecommand.com";
export const ORIGINS = [SITE, "https://warfarecommand.com"];
const SOURCES = ["hub", "musterout", "register", "ai101"];
export const ENDPOINT = "https://vfozrzohrdrbohjqkghk.supabase.co/functions/v1/alerts";
export const FROM = "Muster Out <updates@warfarecommand.com>";
export const RECENT_HASHES = 8;
export const PLATFORM_SCOPE = "Warfare Command updates: new tools, new lessons, Muster Out corrections, and release notes";
export const MUSTEROUT_SCOPE = "correction alerts and release notes";
// A confirmed row retains this consent receipt in the existing nullable field.
// Pending platform tokens use a scope-bound hash; legacy pending links stay narrow.
export const PLATFORM_CONSENT = "consent:platform-updates:v1";
const platformConfirmHash = (raw: string) => hash(PLATFORM_SCOPE + ":" + raw);
const CORS = { "Access-Control-Allow-Origin": SITE, "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "content-type", "Vary": "Origin" };
const redirect = (page: string) => new Response(null, { status: 303, headers: { Location: `${SITE}/alerts/${page}/`, "Cache-Control": "no-store", "Referrer-Policy": "no-referrer" } });
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
// Branded email in the Field Desk house style: paper ground, ink type, red only where it means something.
// Table layout and inline styles so Gmail, Outlook, and Apple Mail render it the same. Light only by design.
const INK = "#1a1a1c", INK2 = "#4a4a4f", INK3 = "#5f5f65", RED = "#C8102E", REDINK = "#8f0b21", PAPER = "#f3f2ee", PANEL = "#ffffff", LINE = "#dcdad3";
const SANS = "'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif";
const COND = "'IBM Plex Sans Condensed','Arial Narrow','IBM Plex Sans',Helvetica,Arial,sans-serif";
const MONO = "'IBM Plex Mono',ui-monospace,Menlo,Consolas,'Courier New',monospace";
export type EmailParts = { preheader: string; eyebrow: string; heading: string; paragraphs: string[]; button?: { label: string; url: string }; callout?: { label: string; body: string }; note?: string; reason: string; unsubscribeUrl?: string };
export function renderEmail(m: EmailParts): { html: string; text: string } {
  const e = escapeHtml;
  const para = (t: string) => `<p style="margin:0 0 16px;font:400 16px/1.6 ${SANS};color:${INK};">${e(t)}</p>`;
  const button = m.button ? `<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 20px;"><tr><td bgcolor="${RED}" style="background:${RED};border-radius:3px;"><a href="${e(m.button.url)}" style="display:inline-block;padding:15px 22px;font:600 14px/1 ${MONO};letter-spacing:.06em;color:#ffffff;text-decoration:none;text-transform:uppercase;">${e(m.button.label)}</a></td></tr></table><p style="margin:0 0 20px;font:400 13px/1.5 ${SANS};color:${INK3};">Or paste this link into your browser:<br><a href="${e(m.button.url)}" style="font:400 12px/1.5 ${MONO};color:${REDINK};word-break:break-all;">${e(m.button.url)}</a></p>` : "";
  const callout = m.callout ? `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 20px;"><tr><td style="border-left:2px solid ${RED};padding:4px 0 4px 14px;"><div style="font:600 11px/1.4 ${MONO};letter-spacing:.12em;text-transform:uppercase;color:${INK3};margin-bottom:6px;">${e(m.callout.label)}</div><div style="font:400 13px/1.55 ${MONO};color:${INK};word-break:break-word;">${e(m.callout.body)}</div></td></tr></table>` : "";
  const note = m.note ? `<p style="margin:0;font:400 14px/1.55 ${SANS};color:${INK2};">${e(m.note)}</p>` : "";
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="supported-color-schemes" content="light"><title>${e(m.heading)}</title><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+Condensed:wght@600&family=IBM+Plex+Sans:wght@400;600&display=swap" rel="stylesheet"><style>body{margin:0;padding:0;background:${PAPER};}a{color:${REDINK};}@media (max-width:620px){.wrap{width:100%!important;}.pad{padding:24px 20px!important;}h1{font-size:28px!important;}}</style></head>
<body style="margin:0;padding:0;background:${PAPER};"><div style="display:none;max-height:0;overflow:hidden;opacity:0;color:${PAPER};">${e(m.preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${PAPER}" style="background:${PAPER};"><tr><td align="center" style="padding:28px 12px 36px;">
<table role="presentation" class="wrap" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:600px;">
<tr><td style="padding:0 4px 14px;border-bottom:2px solid ${RED};"><img src="https://musterout.warfarecommand.com/assets/brand/email-header-600@2x.png" width="300" height="56" alt="Warfare Command" title="MUSTER OUT" style="display:block;width:300px;max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,Menlo,Consolas,'Courier New',monospace;font-size:12px;line-height:1.3;color:#8f0b21;font-weight:600;letter-spacing:.16em;"></td></tr>
<tr><td style="height:20px;line-height:20px;font-size:0;">&nbsp;</td></tr>
<tr><td class="pad" bgcolor="${PANEL}" style="background:${PANEL};border:1px solid ${LINE};border-top:3px solid ${RED};padding:32px 32px 28px;">
<div style="font:600 12px/1.3 ${MONO};letter-spacing:.14em;text-transform:uppercase;color:${REDINK};margin-bottom:10px;">${e(m.eyebrow)}</div>
<h1 style="margin:0 0 18px;font:600 32px/1.12 ${COND};color:${INK};">${e(m.heading)}</h1>
${m.paragraphs.map(para).join("")}${button}${callout}${note}
</td></tr>
<tr><td style="padding:22px 4px 0;font:400 12px/1.6 ${SANS};color:${INK3};"><p style="margin:0 0 8px;">${e(m.reason)}${m.unsubscribeUrl ? ` <a href="${e(m.unsubscribeUrl)}" style="color:${INK2};">Unsubscribe and delete your address</a>.` : ""}</p><p style="margin:0;">Muster Out, a Warfare Command tool. Unofficial pilot. Not affiliated with the Department of Defense or the Marine Corps. <a href="${SITE}" style="color:${INK2};">musterout.warfarecommand.com</a></p></td></tr>
</table></td></tr></table></body></html>`;
  const text = ["MUSTER OUT | Warfare Command", m.heading, ...m.paragraphs, ...(m.button ? [`${m.button.label}: ${m.button.url}`] : []), ...(m.callout ? [`${m.callout.label}: ${m.callout.body}`] : []), ...(m.note ? [m.note] : []), m.unsubscribeUrl ? `${m.reason} Unsubscribe and delete your address: ${m.unsubscribeUrl}` : m.reason, "Muster Out, a Warfare Command tool. Unofficial pilot. Not affiliated with the Department of Defense or the Marine Corps."].join("\n\n");
  return { html, text };
}

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
    async count(filters: Record<string, string> = {}): Promise<number> {
      const response = await net(address("alert_signups", { select: "id", status: "eq.confirmed", ...filters }), { method: "HEAD", headers: { ...headers, Prefer: "count=exact" } });
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
    const origin = req.headers.get("origin") || "";
    const cors = { ...CORS, "Access-Control-Allow-Origin": ORIGINS.includes(origin) ? origin : SITE };
    const json = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers: { ...cors, "content-type": "application/json", "Cache-Control": "no-store" } });
    const success = () => json(200, { ok: true });
    const u = new URL(req.url);
    if (req.method === "OPTIONS") {
      if (!ORIGINS.includes(origin)) return json(403, { ok: false, error: "origin" });
      return new Response(null, { status: 204, headers: cors });
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
        const db = database(deps.env, deps.fetch);
        const confirmed_at = new Date(deps.now?.() ?? Date.now()).toISOString();
        const platform = await db.rows("alert_signups", "PATCH", { confirm_hash: `eq.${await platformConfirmHash(confirm)}`, status: "eq.pending" }, { status: "confirmed", confirm_hash: PLATFORM_CONSENT, confirmed_at });
        if (platform.length) return redirect("confirmed");
        const legacy = await db.rows("alert_signups", "PATCH", { confirm_hash: `eq.${await hash(confirm)}`, status: "eq.pending" }, { status: "confirmed", confirm_hash: null, confirmed_at });
        return redirect(legacy.length ? "confirmed" : "expired");
      }
      if (req.method !== "POST") return json(405, { ok: false, error: "method" });
      if (!ORIGINS.includes(origin)) return json(403, { ok: false, error: "origin" });
      const text = await req.text();
      if (text.length > 8192) return json(413, { ok: false, error: "too_large" });
      let body: Record<string, unknown>;
      try {
        body = JSON.parse(text);
        if (!body || typeof body !== "object" || Array.isArray(body)) throw new Error("shape");
      } catch { return json(400, { ok: false, error: "bad_json" }); }
      if (body.kind !== "subscribe" && body.kind !== "suggest") return json(400, { ok: false, error: "kind" });
      if (body.website !== undefined && body.website !== "") return success();
      const email = typeof body.email === "string" ? body.email.trim().toLowerCase() : "";
      const idea = typeof body.idea === "string" ? body.idea.trim() : "";
      if (body.kind === "suggest" && (Array.from(idea).length < 10 || Array.from(idea).length > 1000 || (body.email !== undefined && body.email !== "" && !emailOk(email)))) return json(400, { ok: false, error: "bad_input" });
      if (body.kind === "subscribe" && body.source !== undefined && (typeof body.source !== "string" || !SOURCES.includes(body.source))) return json(400, { ok: false, error: "bad_input" });
      const resendKey = deps.env("RESEND_API_KEY");
      if (!resendKey) return json(503, { ok: false, error: "not_configured" });
      const salt = deps.env("IP_HASH_SALT") || deps.env("INGEST_SALT");
      if (!salt || !deps.env("SUPABASE_URL") || !deps.env("SUPABASE_SERVICE_ROLE_KEY")) return json(503, { ok: false, error: "not_configured" });
      const db = database(deps.env, deps.fetch);
      const now = deps.now?.() ?? Date.now();
      const ip = req.headers.get("x-forwarded-for")?.split(",")[0].trim() || "0";
      const ip_hash = (await hash(salt + ip)).slice(0, 24);
      if (!await reserveRate(db, `${body.kind === "suggest" ? "suggest:" : ""}ip:${ip_hash}`, 3, 60, now)) return json(429, { ok: false, error: "rate_limited" });
      if (body.kind === "suggest") {
        const rows = await db.rows<{ id: string }>("suggestions", "POST", {}, { idea, email: email || null, ip_hash });
        const { html, text } = renderEmail({
          preheader: "A tool idea was submitted to Warfare Command.", eyebrow: "Tool suggestion", heading: "New tool suggestion",
          paragraphs: [idea], callout: email ? { label: "Reply address", body: email } : undefined,
          reason: "Sent from the Warfare Command tool suggestion form.",
        });
        const sent = await deps.fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: `Bearer ${resendKey}`, "content-type": "application/json", "Idempotency-Key": `suggestion-${rows[0].id}` }, body: JSON.stringify({ from: FROM, to: ["feedback@warfarecommand.com"], subject: "Warfare Command tool suggestion", html, text }) });
        if (!sent.ok) return json(502, { ok: false, error: "send" });
        return success();
      }
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
        const platform = body.source === "hub" || body.source === "ai101";
        const confirm_hash = platform ? await platformConfirmHash(confirmToken) : await hash(confirmToken);
        const unsubscribe_hashes = [...(existing?.unsubscribe_hashes ?? []), await hash(unsubscribeToken)].slice(-RECENT_HASHES);
        const last_sent_at = new Date(now).toISOString();
        const fields = { status: "pending", confirm_hash, unsubscribe_hashes, ip_hash, last_sent_at, source: body.source ?? null };
        const reserved = existing
          ? await db.rows("alert_signups", "PATCH", { id: `eq.${existing.id}`, status: "eq.pending", last_sent_at: existing.last_sent_at ? `eq.${existing.last_sent_at}` : "is.null" }, fields)
          : await db.rows("alert_signups", "POST", { on_conflict: "email" }, { email, ...fields }, "resolution=ignore-duplicates,return=representation");
        if (!reserved.length) continue;
        const confirmUrl = `${ENDPOINT}?confirm=${confirmToken}`;
        const unsubscribeUrl = `${ENDPOINT}?unsubscribe=${unsubscribeToken}`;
        const { html, text } = renderEmail({
          preheader: platform ? "Confirm your address to get Warfare Command updates." : "Confirm your address to get Muster Out correction alerts.",
          eyebrow: platform ? "Warfare Command updates" : "Correction alerts",
          heading: "Confirm your email",
          paragraphs: [platform ? `Confirm your address to receive ${PLATFORM_SCOPE}.` : `Confirm your address to receive Muster Out ${MUSTEROUT_SCOPE}.`],
          button: { label: "Confirm my email", url: confirmUrl },
          note: "If you did not request this, you can ignore it.",
          reason: platform ? "This address was entered at warfarecommand.com." : "This address was entered at musterout.warfarecommand.com.",
          unsubscribeUrl,
        });
        const sent = await deps.fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: `Bearer ${resendKey}`, "content-type": "application/json", "Idempotency-Key": `alerts-confirm-${confirm_hash}` }, body: JSON.stringify({ from: FROM, to: [email], subject: platform ? "Confirm Warfare Command updates" : "Confirm Muster Out correction alerts", html, text, headers: unsubscribeHeaders(unsubscribeUrl) }) });
        if (!sent.ok) return json(502, { ok: false, error: "send" });
        return success();
      }
      return json(503, { ok: false, error: "retry" });
    } catch { return json(503, { ok: false, error: "unavailable" }); }
  };
}

if (import.meta.main) Deno.serve(createHandler({ env: (name) => Deno.env.get(name), fetch }));
