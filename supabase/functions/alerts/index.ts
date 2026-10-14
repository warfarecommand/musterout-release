// Website correction alerts. Deploy with verify_jwt false. No contact sync.
// Reader: a Marine who requested alerts. Effect: confirm consent or delete the signup.
import { BodyReadError, readBody } from "../_shared/body.ts";
export const SITE = "https://musterout.warfarecommand.com";
export const ORIGINS = [SITE, "https://warfarecommand.com", "https://www.warfarecommand.com"];
const SOURCES = ["hub", "musterout", "register", "ai101"];
export const ENDPOINT = "https://vfozrzohrdrbohjqkghk.supabase.co/functions/v1/alerts";
export const FROM = "Muster Out <updates@warfarecommand.com>";
export const RECENT_HASHES = 8;
export const PLATFORM_SCOPE = "Warfare Command updates: new tools, new lessons, Muster Out corrections, and release notes";
export const MUSTEROUT_SCOPE = "correction alerts and release notes";
// A confirmed row retains this consent receipt in the existing nullable field.
// Pending platform tokens use a scope-bound hash; legacy pending links stay narrow.
export const PLATFORM_CONSENT = "consent:platform-updates:v1";
const streamConfirmHash = (raw: string) => hash("campaign-streams:v2:" + raw);
export const STREAM_CONSENT = "consent:campaign-streams:v2";
export function streamDefaults(source: unknown) {
  return { corrections: source === "musterout" || source === "register", monthly: true, weekly: false, lessons: source === "ai101" };
}
export function streamNames(row: Pick<Row, "corrections" | "monthly" | "weekly" | "lessons">): string {
  const names = [row.corrections ? "Muster Out corrections" : "", row.monthly ? "Warfare Command Monthly" : "", row.weekly ? "Weekly MARADMIN roundup" : "", row.lessons ? "New lessons" : ""].filter(Boolean);
  // Plain English list: "A", "A and B", "A, B, and C".
  return names.length > 2 ? names.slice(0, -1).join(", ") + ", and " + names[names.length - 1] : names.join(" and ") || "No email streams";
}
const platformConfirmHash = (raw: string) => hash(PLATFORM_SCOPE + ":" + raw);
const CORS = { "Access-Control-Allow-Origin": SITE, "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "content-type", "Vary": "Origin" };
const redirect = (page: string) => new Response(null, { status: 303, headers: { Location: `${SITE}/alerts/${page}/`, "Cache-Control": "no-store", "Referrer-Policy": "no-referrer" } });
const tokenOk = (value: string) => /^[a-f0-9]{64}$/.test(value);
export type Env = (name: string) => string | undefined;
export type Row = { id: string; email: string; status: string; confirm_hash: string | null; unsubscribe_hashes: string[]; last_sent_at: string | null; weekly: boolean; monthly: boolean; corrections: boolean; lessons: boolean };
export const ROW_FIELDS = "id,email,status,confirm_hash,unsubscribe_hashes,last_sent_at,weekly,monthly,corrections,lessons";

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
export type EmailParts = { preheader: string; eyebrow: string; heading: string; paragraphs: string[]; button?: { label: string; url: string }; callout?: { label: string; body: string }; note?: string; reason: string; unsubscribeUrl?: string; prefsUrl?: string };
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
<tr><td style="padding:22px 4px 0;font:400 12px/1.6 ${SANS};color:${INK3};"><p style="margin:0 0 8px;">${e(m.reason)}${m.prefsUrl ? ` <a href="${e(m.prefsUrl)}" style="color:${INK2};">Email preferences</a>.` : ""}${m.unsubscribeUrl ? ` <a href="${e(m.unsubscribeUrl)}" style="color:${INK2};">Unsubscribe from everything</a>.` : ""}</p><p style="margin:0;">Warfare Command. Free tools built by a Marine. Unofficial; not affiliated with the Department of Defense or the Marine Corps. <a href="${SITE}" style="color:${INK2};">musterout.warfarecommand.com</a></p></td></tr>
</table></td></tr></table></body></html>`;
  const text = ["MUSTER OUT | Warfare Command", m.heading, ...m.paragraphs, ...(m.button ? [`${m.button.label}: ${m.button.url}`] : []), ...(m.callout ? [`${m.callout.label}: ${m.callout.body}`] : []), ...(m.note ? [m.note] : []), m.unsubscribeUrl ? `${m.reason} Unsubscribe from everything: ${m.unsubscribeUrl}` : m.reason, ...(m.prefsUrl ? [`Email preferences: ${m.prefsUrl}`] : []), "Warfare Command. Free tools built by a Marine. Unofficial; not affiliated with the Department of Defense or the Marine Corps."].join("\n\n");
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
    async rpc<T>(name: string, body: unknown): Promise<T> {
      const response = await net(`${url}/rest/v1/rpc/${name}`, { method: "POST", headers, body: JSON.stringify(body) });
      if (!response.ok) throw new Error("Database claim failed");
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

export type Database = ReturnType<typeof database>;

// Resend reserves UNSUBSCRIBE_URL on sends. Local designs use that name;
// published payloads and sends map it to the custom ALERT_UNSUBSCRIBE_URL.
export function templateMessage(row: Row, alias: string, variables: Record<string, string | number>, links: LinkSet) {
  return { from: ["monthly", "lesson-launch", "welcome"].includes(alias) ? "Warfare Command <updates@warfarecommand.com>" : FROM, to: [row.email], reply_to: "feedback@warfarecommand.com", template: { id: alias, variables: { ...variables, ALERT_UNSUBSCRIBE_URL: links.UNSUBSCRIBE_URL, PREFS_URL: links.PREFS_URL } }, headers: unsubscribeHeaders(links.UNSUBSCRIBE_URL) };
}
export type LinkSet = { UNSUBSCRIBE_URL: string; PREFS_URL: string; WEEKLY_ON_URL: string };
export async function freshLinks(db: Database, id: string, filters: Record<string, string> = {}, includeWeekly = false): Promise<{ row: Row; links: LinkSet } | undefined> {
  const unsub = token(), prefs = token(), weekly = token();
  const additions = await Promise.all([unsub, prefs, ...(includeWeekly ? [weekly] : [])].map(hash));
  for (let attempt = 0; attempt < 3; attempt++) {
    const row = (await db.rows("alert_signups", "GET", { id: `eq.${id}`, ...filters, select: ROW_FIELDS }))[0];
    if (!row) return;
    const updated = (await db.rows("alert_signups", "PATCH", { id: `eq.${id}`, ...filters, unsubscribe_hashes: `eq.{${row.unsubscribe_hashes.join(",")}}` }, { unsubscribe_hashes: [...row.unsubscribe_hashes, ...additions].slice(-RECENT_HASHES) }))[0];
    if (updated) return { row: updated, links: { UNSUBSCRIBE_URL: `${ENDPOINT}?unsubscribe=${unsub}`, PREFS_URL: `${SITE}/alerts/preferences/?prefs=${prefs}`, WEEKLY_ON_URL: includeWeekly ? `${ENDPOINT}?prefs=${weekly}&weekly=1` : "" } };
  }
  throw new Error("Concurrent preference update prevented a send");
}
export type SendDeps = { env: Env; fetch: typeof fetch; now?: () => number };
type Receipt = { campaign: string; recipient_hash: string; content_hash: string; state: string };
async function claimDelivery(db: Database, row: Row, campaign: string, content: string, env: Env, blockUncertain = false): Promise<Receipt | undefined> {
  const salt = env("IP_HASH_SALT") || env("INGEST_SALT");
  if (!salt) throw new Error("Email hash salt is not configured");
  const receipt = { campaign, recipient_hash: await hash(salt + "delivery:" + row.email), content_hash: await hash(content), stream: "transactional", state: "reserved" };
  const inserted = await db.rows<Receipt>("email_delivery_receipts", "POST", { on_conflict: "campaign,recipient_hash" }, receipt, "resolution=ignore-duplicates,return=representation");
  if (inserted.length) return receipt;
  const existing = (await db.rows<Receipt>("email_delivery_receipts", "GET", { campaign: `eq.${campaign}`, recipient_hash: `eq.${receipt.recipient_hash}` }))[0];
  if (!existing || existing.content_hash !== receipt.content_hash) throw new Error("Campaign content changed; use a new reviewed campaign ID");
  if (blockUncertain && !["accepted", "skipped"].includes(existing.state)) throw new Error("Prior delivery failed or is uncertain; review receipts before retrying");
}
async function deliveryState(db: Database, receipt: Receipt, state: string, now: number) {
  await db.rows("email_delivery_receipts", "PATCH", { campaign: `eq.${receipt.campaign}`, recipient_hash: `eq.${receipt.recipient_hash}` }, { state, updated_at: new Date(now).toISOString() });
}
// A generic rejection, quota error, or ambiguous response cannot authorize
// another send with a different idempotency key.
async function templateRejected(response: Response): Promise<boolean> {
  if (response.status < 400 || response.status >= 500 || [408, 409, 429].includes(response.status)) return false;
  try {
    const error = await response.json();
    const detail = `${typeof error.name === "string" ? error.name : ""} ${typeof error.message === "string" ? error.message : ""}`.replaceAll("_", " ");
    return /\btemplate\b/i.test(detail) && /not found|does not exist|unpublished|not published|missing\s+(?:email\s+)?template|template\s+(?:is\s+)?missing|(?:invalid|missing|required).*variables?|variables?.*(?:invalid|missing|required)/i.test(detail);
  } catch { return false; }
}
export async function sendWelcome(row: Row, deps: SendDeps) {
  const db = database(deps.env, deps.fetch);
  // Claim before sending. Reconfirmation after deletion also keeps one welcome
  // per salted address. Receipts never contain the readable address.
  const receipt = await claimDelivery(db, row, "welcome:v1", "welcome:v1", deps.env);
  if (!receipt) return;
  const now = deps.now?.() ?? Date.now();
  try {
    const ready = await freshLinks(db, row.id, { status: "eq.confirmed" }, true);
    if (!ready) { await deliveryState(db, receipt, "skipped", now); return; }
    const key = deps.env("RESEND_API_KEY");
    if (!key) { await deliveryState(db, receipt, "failed", now); return; }
    const response = await deps.fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: `Bearer ${key}`, "content-type": "application/json", "Idempotency-Key": `welcome-${receipt.recipient_hash}` }, body: JSON.stringify(templateMessage(ready.row, "welcome", { WEEKLY_ON_URL: ready.links.WEEKLY_ON_URL, SUBSCRIBED_STREAMS: streamNames(ready.row) }, ready.links)) });
    if (!response.ok) { await deliveryState(db, receipt, response.status >= 500 || [408,409].includes(response.status) ? "unknown" : "failed", now); return; }
    const result = await response.json();
    if (!result.id) throw new Error("Uncertain welcome response");
    await deliveryState(db, receipt, "accepted", now);
    await db.rows("alert_signups", "PATCH", { id: `eq.${row.id}`, status: "eq.confirmed" }, { last_sent_at: new Date(now).toISOString() });
  } catch {
    await db.rows("email_delivery_receipts", "PATCH", { campaign: `eq.${receipt.campaign}`, recipient_hash: `eq.${receipt.recipient_hash}`, state: "eq.reserved" }, { state: "unknown", updated_at: new Date(now).toISOString() });
  }
}

export type Stream = "corrections" | "monthly" | "weekly" | "lessons";
export type DeliveryReport = { recipients: number; eligible: number; accepted: number; skipped: number; reasons: Record<string, number> };
const contentHash = (alias: string, variables: Record<string, string | number>) => hash(JSON.stringify({ alias, variables: Object.fromEntries(Object.entries(variables).sort(([a], [b]) => a.localeCompare(b))) }));
async function candidates(db: Database, filters: Record<string, string>): Promise<Row[]> {
  const snapshot: Row[] = []; let after = "";
  while (true) {
    const rows = await db.rows("alert_signups", "GET", { select: ROW_FIELDS, status: "eq.confirmed", ...filters, order: "id.asc", limit: "500", ...(after ? { id: `gt.${after}` } : {}) });
    if (!rows.length) return snapshot;
    snapshot.push(...rows); after = rows[rows.length - 1].id;
  }
}
async function streamGate(db: Database, row: Row, campaign: string, content: string, stream: Stream, env: Env, dry: boolean) {
  const salt = env("IP_HASH_SALT") || env("INGEST_SALT");
  if (!salt) throw new Error("Email hash salt is not configured");
  const receipt = { campaign, recipient_hash: await hash(salt + "delivery:" + row.email), content_hash: content, state: "reserved", stream };
  const { decision } = await db.rpc<{ decision: string }>("email_delivery_gate", { p_campaign: campaign, p_recipient_hash: receipt.recipient_hash, p_content_hash: content, p_stream: stream, p_dry: dry });
  if (!["claimed", "eligible", "duplicate", "weekly_cap", "monthly_cap", "blocked", "changed"].includes(decision)) throw new Error("Invalid delivery gate response");
  return { receipt, decision };
}
export async function sendTemplates(alias: string, campaign: string, variables: Record<string, string | number>, filters: Record<string, string>, deps: SendDeps, stream: Stream, dry = false): Promise<DeliveryReport> {
  const key = deps.env("RESEND_API_KEY");
  if (!dry && !key) throw new Error("RESEND_API_KEY is not configured");
  const db = database(deps.env, deps.fetch), rows = await candidates(db, filters);
  const report: DeliveryReport = { recipients: rows.length, eligible: 0, accepted: 0, skipped: 0, reasons: {} };
  const skip = (reason: string) => { report.skipped++; report.reasons[reason] = (report.reasons[reason] ?? 0) + 1; };
  const content = await contentHash(alias, variables);
  for (let start = 0; start < rows.length; start += 100) {
    const messages: ReturnType<typeof templateMessage>[] = [], receipts: Receipt[] = [], ids: string[] = [];
    try {
      for (const snapshot of rows.slice(start, start + 100)) {
        const row = dry ? snapshot : (await db.rows("alert_signups", "GET", { id: `eq.${snapshot.id}`, status: "eq.confirmed", ...filters, select: ROW_FIELDS }))[0];
        if (!row) { skip("consent_changed"); continue; }
        const gate = await streamGate(db, row, campaign, content, stream, deps.env, dry);
        if (!["claimed", "eligible"].includes(gate.decision)) { skip(gate.decision); continue; }
        if (dry) { report.eligible++; continue; }
        receipts.push(gate.receipt);
        const ready = await freshLinks(db, row.id, { status: "eq.confirmed", ...filters });
        if (!ready) { await deliveryState(db, gate.receipt, "skipped", deps.now?.() ?? Date.now()); receipts.pop(); skip("consent_changed"); continue; }
        messages.push(templateMessage(ready.row, alias, variables, ready.links)); ids.push(row.id);
      }
      if (!messages.length) continue;
      const eligible = new Set((await db.rows<{ id: string }>("alert_signups", "GET", { select: "id", id: `in.(${ids.join(",")})`, status: "eq.confirmed", ...filters })).map(row => row.id));
      for (let i = ids.length - 1; i >= 0; i--) {
        if (eligible.has(ids[i])) continue;
        await deliveryState(db, receipts[i], "skipped", deps.now?.() ?? Date.now());
        messages.splice(i, 1); receipts.splice(i, 1); ids.splice(i, 1); skip("consent_changed");
      }
      if (!messages.length) continue;
      report.eligible += messages.length;
      const idempotency = await hash(campaign + ":" + receipts.map(r => r.recipient_hash).join(":"));
      const response = await deps.fetch("https://api.resend.com/emails/batch", { method: "POST", headers: { Authorization: `Bearer ${key}`, "content-type": "application/json", "Idempotency-Key": `batch-${idempotency}` }, body: JSON.stringify(messages) });
      const now = deps.now?.() ?? Date.now();
      if (!response.ok) {
        for (const receipt of receipts) await deliveryState(db, receipt, response.status >= 500 || [408,409].includes(response.status) ? "unknown" : "failed", now);
        throw new Error("Batch rejected; review delivery receipts");
      }
      const data = (await response.json()).data;
      if (!Array.isArray(data) || data.length !== messages.length || data.some(r => !r?.id)) throw new Error("Uncertain batch response; review delivery receipts");
      for (let i = 0; i < receipts.length; i++) {
        await deliveryState(db, receipts[i], "accepted", now);
        await db.rows("alert_signups", "PATCH", { id: `eq.${ids[i]}`, status: "eq.confirmed" }, { last_sent_at: new Date(now).toISOString() });
      }
      report.accepted += messages.length;
    } catch (error) {
      for (const receipt of receipts) await db.rows("email_delivery_receipts", "PATCH", { campaign: `eq.${receipt.campaign}`, recipient_hash: `eq.${receipt.recipient_hash}`, state: "eq.reserved" }, { state: "unknown", updated_at: new Date(deps.now?.() ?? Date.now()).toISOString() });
      throw error;
    }
  }
  return report;
}

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

export function createHandler(deps: { env: Env; fetch: typeof fetch; now?: () => number; bodyDeadlineMs?: number }) {
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
    const bodyCap = u.searchParams.has("prefs") ? 1024 : 8192;
    if (Number(req.headers.get("content-length")) > bodyCap) return json(413, { ok: false, error: "too_large" });
    try {
      const unsubscribe = u.searchParams.get("unsubscribe");
      if (unsubscribe !== null && (req.method === "GET" || req.method === "POST")) {
        if (tokenOk(unsubscribe)) await database(deps.env, deps.fetch).rows("alert_signups", "DELETE", { unsubscribe_hashes: `cs.{${await hash(unsubscribe)}}` });
        return req.method === "POST" ? success() : redirect("unsubscribed");
      }
      const prefs = u.searchParams.get("prefs");
      if (prefs !== null) {
        if (req.method !== "GET" && req.method !== "POST") return json(405, { ok: false, error: "method" });
        if (!tokenOk(prefs)) return json(404, { ok: false, error: "expired" });
        if (req.method === "POST" && origin !== SITE) return json(403, { ok: false, error: "origin" });
        let changes;
        if (req.method === "POST") {
          const raw = await readBody(req.body, 1024, deps.bodyDeadlineMs);
          try { changes = JSON.parse(raw); } catch { return json(400, { ok: false, error: "bad_json" }); }
          if (!changes || typeof changes !== "object" || Array.isArray(changes)) return json(400, { ok: false, error: "bad_input" });
          if (!(changes.unsubscribe === true && Object.keys(changes).length === 1) && (["corrections", "monthly", "weekly", "lessons"].some(k => typeof changes[k] !== "boolean") || Object.keys(changes).length !== 4)) return json(400, { ok: false, error: "bad_input" });
        }
        const db = database(deps.env, deps.fetch), auth = { unsubscribe_hashes: `cs.{${await hash(prefs)}}` };
        let row = (await db.rows("alert_signups", "GET", { ...auth, select: ROW_FIELDS }))[0];
        if (!row) return json(404, { ok: false, error: "expired" });
        if (req.method === "POST") {
          if (changes.unsubscribe === true && Object.keys(changes).length === 1) {
            await db.rows("alert_signups", "DELETE", auth);
            return success();
          }
          if (row.status !== "confirmed") return json(409, { ok: false, error: "pending" });
          row = (await db.rows("alert_signups", "PATCH", { ...auth, status: "eq.confirmed" }, { corrections: changes.corrections, monthly: changes.monthly, weekly: changes.weekly, lessons: changes.lessons }))[0];
          if (!row) return json(404, { ok: false, error: "expired" });
        } else if (u.searchParams.get("weekly") === "1") {
          if (row.status === "confirmed") await db.rows("alert_signups", "PATCH", { ...auth, status: "eq.confirmed" }, { weekly: true });
          return new Response(null, { status: 303, headers: { Location: `${SITE}/alerts/preferences/?prefs=${prefs}`, "Cache-Control": "no-store", "Referrer-Policy": "no-referrer" } });
        }
        return json(200, { ok: true, email: row.email, status: row.status, corrections: row.corrections, monthly: row.monthly, weekly: row.weekly, lessons: row.lessons });
      }
      const confirm = u.searchParams.get("confirm");
      if (confirm !== null && req.method === "GET") {
        if (!tokenOk(confirm)) return redirect("expired");
        const db = database(deps.env, deps.fetch);
        const now = deps.now?.() ?? Date.now(), confirmed_at = new Date(now).toISOString();
        // Keep expiry in the atomic update predicate for every token format.
        const pending = { status: "eq.pending", last_sent_at: `gte.${new Date(now - 7 * 86400000).toISOString()}` };
        const current = await db.rows("alert_signups", "PATCH", { confirm_hash: `eq.${await streamConfirmHash(confirm)}`, ...pending }, { status: "confirmed", confirm_hash: STREAM_CONSENT, confirmed_at });
        const platform = current.length ? current : await db.rows("alert_signups", "PATCH", { confirm_hash: `eq.${await platformConfirmHash(confirm)}`, ...pending }, { status: "confirmed", confirm_hash: PLATFORM_CONSENT, confirmed_at });
        const rows = platform.length ? platform : await db.rows("alert_signups", "PATCH", { confirm_hash: `eq.${await hash(confirm)}`, ...pending }, { status: "confirmed", confirm_hash: null, confirmed_at });
        if (!rows.length) return redirect("expired");
        // Confirmation is permanent even if the welcome provider is unavailable.
        try { await sendWelcome(rows[0], deps); } catch { /* The durable receipt retains the attempt. */ }
        return redirect("confirmed");
      }
      if (req.method !== "POST") return json(405, { ok: false, error: "method" });
      if (!ORIGINS.includes(origin)) return json(403, { ok: false, error: "origin" });
      const text = await readBody(req.body, 8192, deps.bodyDeadlineMs);
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
        const existing = (await db.rows("alert_signups", "GET", { email: `eq.${email}`, select: ROW_FIELDS }))[0];
        if (existing?.status === "confirmed") return success();
        if (existing?.last_sent_at && now - Date.parse(existing.last_sent_at) < 600000) return success();
        // Deleting a signup must not reset its email cooldown. This salted
        // receipt contains no address and remains outside the subscriber list.
        if (!addressReserved) {
          const addressHash = await hash(salt + "email:" + email);
          if (!await reserveRate(db, `email:${addressHash}`, 1, 10, now)) return success();
          if (!await reserveRate(db, `email-day:${addressHash}`, 3, 24 * 60, now)) return success();
          if (!await reserveRate(db, `email-week:${addressHash}`, 5, 7 * 24 * 60, now)) return success();
          addressReserved = true;
        }
        const confirmToken = token(), unsubscribeToken = token(), prefsToken = token();
        const platform = body.source === "hub" || body.source === "ai101";
        const confirm_hash = await streamConfirmHash(confirmToken);
        const unsubscribe_hashes = [...(existing?.unsubscribe_hashes ?? []), await hash(unsubscribeToken), await hash(prefsToken)].slice(-RECENT_HASHES);
        const last_sent_at = new Date(now).toISOString();
        const fields = { status: "pending", confirm_hash, unsubscribe_hashes, ip_hash, last_sent_at, source: body.source ?? null, ...streamDefaults(body.source) };
        const reserved = existing
          ? await db.rows("alert_signups", "PATCH", { id: `eq.${existing.id}`, status: "eq.pending", last_sent_at: existing.last_sent_at ? `eq.${existing.last_sent_at}` : "is.null" }, fields)
          : await db.rows("alert_signups", "POST", { on_conflict: "email" }, { email, ...fields }, "resolution=ignore-duplicates,return=representation");
        if (!reserved.length) continue;
        const confirmUrl = `${ENDPOINT}?confirm=${confirmToken}`;
        const unsubscribeUrl = `${ENDPOINT}?unsubscribe=${unsubscribeToken}`;
        const prefsUrl = `${SITE}/alerts/preferences/?prefs=${prefsToken}`;
        const scope = streamNames(fields);
        const { html, text } = renderEmail({
          preheader: platform ? "Confirm your address to get Warfare Command updates." : "Confirm your address to get Muster Out correction alerts.",
          eyebrow: platform ? "Warfare Command updates" : "Correction alerts",
          heading: "Confirm your email",
          paragraphs: [`Confirm your address to receive ${scope}. Weekly MARADMIN email is off until you add it.`],
          button: { label: "Confirm my email", url: confirmUrl },
          note: "If you did not request this, you can ignore it.",
          reason: platform ? "This address was entered at warfarecommand.com." : "This address was entered at musterout.warfarecommand.com.",
          unsubscribeUrl, prefsUrl,
        });
        const common = { from: "Warfare Command <updates@warfarecommand.com>", to: [email], reply_to: "feedback@warfarecommand.com", subject: "Confirm your Warfare Command email choices", headers: unsubscribeHeaders(unsubscribeUrl) };
        const headers = { Authorization: `Bearer ${resendKey}`, "content-type": "application/json", "Idempotency-Key": `alerts-confirm-${confirm_hash}` };
        const receipt = await claimDelivery(db, reserved[0], `confirm:${confirm_hash}`, confirm_hash, deps.env);
        if (!receipt) return success();
        try {
          let sent = await deps.fetch("https://api.resend.com/emails", { method: "POST", headers, body: JSON.stringify({ ...common, template: { id: "confirm-subscription", variables: { CONFIRM_URL: confirmUrl, ALERT_UNSUBSCRIBE_URL: unsubscribeUrl, PREFS_URL: prefsUrl, CONSENT_SCOPE: scope } } }) });
          if (!sent.ok && await templateRejected(sent)) sent = await deps.fetch("https://api.resend.com/emails", { method: "POST", headers: { ...headers, "Idempotency-Key": `alerts-confirm-fallback-${confirm_hash}` }, body: JSON.stringify({ ...common, html, text }) });
          if (!sent.ok) {
            await deliveryState(db, receipt, sent.status >= 500 || [408, 409, 429].includes(sent.status) ? "unknown" : "failed", now);
            return json(502, { ok: false, error: "send" });
          }
          if (!(await sent.json()).id) throw new Error("Uncertain confirmation response");
          await deliveryState(db, receipt, "accepted", now);
          return success();
        } catch {
          await db.rows("email_delivery_receipts", "PATCH", { campaign: `eq.${receipt.campaign}`, recipient_hash: `eq.${receipt.recipient_hash}`, state: "eq.reserved" }, { state: "unknown", updated_at: new Date(now).toISOString() });
          return json(503, { ok: false, error: "unavailable" });
        }
      }
      return json(503, { ok: false, error: "retry" });
    } catch (error) {
      if (error instanceof BodyReadError) return json(error.status, { ok: false, error: error.code });
      return json(503, { ok: false, error: "unavailable" });
    }
  };
}

if (import.meta.main) Deno.serve(createHandler({ env: (name) => Deno.env.get(name), fetch }));
