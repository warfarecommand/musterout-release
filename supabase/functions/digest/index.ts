// Public weekly trigger. Fresh feed, durable ISO week receipts, and stream caps.
// Reader: a confirmed weekly subscriber. Effect: review the official notices.
import { database, escapeHtml, sendTemplates } from "../alerts/index.ts";
import type { SendDeps } from "../alerts/index.ts";
export const FEED = "https://watch.warfarecommand.com/feed/latest.json";
export const WATCH = "https://watch.warfarecommand.com/";
type Notice = { number: string; title: string; summary: string; url: string; posted: string; body_available: boolean };
export type Feed = { schema_version: number; source: string; checked_from: string; checked_to: string; generated_at: string; checked_count: number; unclassified_count: number; truncated: boolean; capture_replay: boolean; notices: Notice[] };
const dateOk = (v: unknown): v is string => typeof v === "string" && /^\d{4}-\d{2}-\d{2}$/.test(v) && new Date(v).toISOString().slice(0, 10) === v;
const copyOk = (v: unknown, n: number): v is string => typeof v === "string" && v.length > 0 && v.length <= n && !/[<>\u0000-\u001f\u007f]/.test(v);
function officialUrl(value: unknown): value is string {
  if (typeof value !== "string" || value.length > 500) return false;
  try {
    const u = new URL(value);
    return u.protocol === "https:" && ["www.marines.mil", "marines.mil"].includes(u.hostname) && !u.username && !u.password && !u.port && u.pathname.startsWith("/News/Messages/Messages-Display/");
  } catch { return false; }
}
export function validateFeed(input: unknown, now: number): Feed {
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new Error("Invalid feed");
  const f = input as Feed;
  if (f.schema_version !== 1 || f.source !== "MARADMIN" || typeof f.generated_at !== "string" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(f.generated_at) || !dateOk(f.checked_from) || !dateOk(f.checked_to) || !Array.isArray(f.notices) || f.notices.length > 100 || !Number.isInteger(f.checked_count) || f.checked_count < f.notices.length || f.unclassified_count !== 0 || f.truncated !== false || f.capture_replay !== false) throw new Error("Incomplete or invalid feed");
  const from = Date.parse(f.checked_from), to = Date.parse(f.checked_to), generated = Date.parse(f.generated_at);
  if (!Number.isFinite(generated) || generated > now ||  to < from || to - from > 7 * 86400000 || to > now) throw new Error("Stale or invalid feed window");
  const numbers = new Set<string>();
  for (const n of f.notices) {
    if (!n || !/^\d{1,3}\/\d{2}$/.test(n.number) || !copyOk(n.title, 600) || !copyOk(n.summary, 1000) || !officialUrl(n.url) || !dateOk(n.posted) || n.posted < f.checked_from || n.posted > f.checked_to || typeof n.body_available !== "boolean" || numbers.has(n.number)) throw new Error("Invalid notice");
    numbers.add(n.number);
  }
  return f;
}
// Fixed house item markup from RESEND_PLAN.md. No arbitrary HTML from the feed.
export function itemHtml(title: string, summary: string, url: string): string {
  const e = escapeHtml;
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;table-layout:fixed;border-collapse:collapse;"><tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:12px 0;border-top:1px solid #dcdad3;font-family:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;font-size:14px;line-height:1.5;color:#4a4a4f;font-weight:400;"><a href="${e(url)}" style="font-family:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;font-size:16px;line-height:1.4;color:#8f0b21;font-weight:600;text-decoration:underline;word-break:break-word;overflow-wrap:anywhere;">${e(title)}</a><br>${e(summary)}</td></tr></table>`;
}
export function roundupVariables(feed: Feed): Record<string, string> {
  const items = feed.notices.map(n => ({ title: `MARADMIN ${n.number}: ${n.title}`, summary: `${n.body_available ? "Applicability unverified." : "Title only; applicability unverified."} ${n.summary}`, url: n.url }));
  let html = items.map(n => itemHtml(n.title, n.summary, n.url)).join("");
  let text = items.map(n => `${n.title}. ${n.summary} Source: ${n.url}`).join("\n\n");
  // RESEND_PLAN allows one summary linking to the complete roundup when an
  // issue exceeds its editorial budget. Never silently drop real notices.
  const words = items.map(n => `${n.title} ${n.summary}`).join(" ").split(/\s+/).length + 23;
  if (html.length > 2000 || text.length > 2000 || (items.length && words > 60)) {
    const title = `${items.length} MARADMIN title matches`;
    const summary = "Read the complete roundup and official messages. Applicability is unverified.";
    html = itemHtml(title, summary, WATCH);
    text = `${title}. ${summary} Source: ${WATCH}`;
  }
  return { WEEK_OF: `${feed.checked_from} to ${feed.checked_to}`, ITEMS_HTML: html, ITEMS_TEXT: text };
}
export function weekKey(now: number): string {
  const day = new Date(now), weekday = (day.getUTCDay() + 6) % 7;
  day.setUTCDate(day.getUTCDate() - weekday);
  return day.toISOString().slice(0, 10);
}
export function createHandler(deps: SendDeps) {
  return async (req: Request): Promise<Response> => {
    const json = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "Cache-Control": "no-store" } });
    if (req.method !== "GET" && req.method !== "POST") return json(405, { ok: false, error: "method" });
    try {
      const dry = new URL(req.url).searchParams.get("dry") === "1";
      if (dry) {
        const secret = deps.env("DIGEST_OPS_KEY");
        if (!secret || !await opsKeyMatches(req.headers.get("x-ops-key") ?? "", secret)) return json(200, { ok: true });
      }
      const now = deps.now?.() ?? Date.now();
      // Watch runs Monday 13:00 UTC, release feed sync at 14:00, and this
      // digest's cron at 15:00. Allow retries through Monday, ending at 00:00.
      const monday = Date.parse(weekKey(now));
      const cycleStart = monday + 13 * 3600000;
      if (now < monday + 15 * 3600000 || now >= monday + 86400000) return json(200, { ok: true, ...(dry ? { dry: true } : {}), noop: "outside_window" });
      const response = await deps.fetch(FEED, { headers: { Accept: "application/json" }, redirect: "error", signal: AbortSignal.timeout(15000) });
      if (!response.ok) throw new Error("Feed unavailable");
      const raw = await response.text();
      if (raw.length > 250000) throw new Error("Feed too large");
      const feed = validateFeed(JSON.parse(raw), now);
      if (Date.parse(feed.generated_at) < cycleStart) return json(200, { ok: true, ...(dry ? { dry: true } : {}), noop: "stale_feed" });
      if (!feed.notices.length) {
        const recipients = await database(deps.env, deps.fetch).count({ weekly: "eq.true" });
        return json(200, { ok: true, dry, noop: "no_matches", recipients, eligible: 0, accepted: 0, skipped: recipients, reasons: { no_matches: recipients }, notices: 0 });
      }
      const result = await sendTemplates("weekly-roundup", `weekly-roundup:${weekKey(now)}`, roundupVariables(feed), { weekly: "eq.true" }, deps, "weekly", dry);
      return json(200, { ok: true, dry, ...(result.eligible ? {} : { noop: "no_eligible_recipients" }), notices: feed.notices.length, batches: Math.ceil(result.eligible / 100), ...result });
    } catch { return json(503, { ok: false, error: "unavailable", review_receipts: true }); }
  };
}
// Hash both inputs to fixed-size buffers, then compare every byte without an
// early exit. No secret-dependent string comparison or prefix timing.
async function opsKeyMatches(candidate: string, secret: string): Promise<boolean> {
  const encoder = new TextEncoder();
  const [a, b] = await Promise.all([candidate, secret].map(value => crypto.subtle.digest("SHA-256", encoder.encode(value))));
  const left = new Uint8Array(a), right = new Uint8Array(b);
  let difference = 0;
  for (let i = 0; i < left.length; i++) difference |= left[i] ^ right[i];
  return difference === 0;
}
if (import.meta.main) Deno.serve(createHandler({ env: name => Deno.env.get(name), fetch }));
