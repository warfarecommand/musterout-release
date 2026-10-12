// Public weekly trigger. Fresh feed, durable ISO week receipts, and stream caps.
// Reader: a confirmed weekly subscriber. Effect: review the official notices.
import { database, escapeHtml, sendTemplates } from "../alerts/index.ts";
import type { SendDeps } from "../alerts/index.ts";
export const FEED = "https://watch.warfarecommand.com/feed/v2/latest.json";
export const WATCH = "https://watch.warfarecommand.com/";
type Notice = { series?: string; id?: string; lines?: string[]; paths?: string[]; number: string; title: string; summary?: string; url: string; posted: string; body_available: boolean };
export type LegacyFeed = { schema_version: number; source: string; checked_from: string; checked_to: string; generated_at: string; checked_count: number; unclassified_count: number; truncated: boolean; capture_replay: boolean; notices: Notice[] };
export type SourceBlock = { source: string; coverage: string; status: "ok" | "failed"; reason: string | null; last_attempt: string; last_success: string | null; window: { from: string; to: string }; checked_count: number; unclassified_count: number; truncated: boolean; body_available: boolean; notices: Notice[] };
export type V2Feed = { schema_version: 2; generated_at: string; expires_at: string; seq: number; capture_replay?: boolean; sources: SourceBlock[] };
export type Feed = LegacyFeed | V2Feed;
const DAY = 86400000;
const SOURCES = ["MARADMIN", "ALMAR", "ALNAV", "ORDER"];
const LINES = ["separation", "retirement", "va", "skillbridge", "reserve", "leave", "family"];
const PATHS = ["resign", "retire", "eas", "all"];
const dateOk = (v: unknown): v is string => typeof v === "string" && /^\d{4}-\d{2}-\d{2}$/.test(v) && Number.isFinite(Date.parse(v)) && new Date(v).toISOString().slice(0, 10) === v;
const copyOk = (v: unknown, n: number): v is string => typeof v === "string" && v.trim().length > 0 && v.length <= n && !/[<>\u0000-\u001f\u007f-\u009f]/.test(v);
const stampOk = (v: unknown): v is string => typeof v === "string" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(v) && Number.isFinite(Date.parse(v)) && dateOk(v.slice(0, 10));
function clean(value: unknown): void {
  if (typeof value === "string" && /[\u0000-\u001f\u007f-\u009f]/.test(value)) throw new Error("Control character in feed");
  if (Array.isArray(value)) value.forEach(clean);
  else if (value && typeof value === "object") Object.entries(value).forEach(([k, v]) => { clean(k); clean(v); });
}
function officialUrl(value: unknown, source = "MARADMIN"): value is string {
  if (typeof value !== "string" || value.length > 500 || /[\s<>\\]/.test(value)) return false;
  try {
    const u = new URL(value);
    if (!value.startsWith("https://" + u.hostname + "/") || /[?#]/.test(value) || u.protocol !== "https:" || u.username || u.password || u.port || u.search || u.hash || /%2f|%5c/i.test(value) || decodeURIComponent(value).split("/").some(p => p === "." || p === "..")) return false;
    if (source === "MARADMIN" || source === "ALMAR") return u.hostname === "www.marines.mil" && /^\/News\/Messages\/Messages-Display\/Article\/\d+\/[A-Za-z0-9-]+\/$/.test(u.pathname);
    if (source === "ALNAV") return u.hostname === "www.mynavyhr.navy.mil" && (/^\/References\/Messages\//.test(u.pathname) || /^\/Portals\/55\/Messages\//.test(u.pathname));
    return source === "ORDER" && u.hostname === "www.marines.mil" && (/^\/News\/Publications\/MCPEL\//.test(u.pathname) || /^\/Portals\/1\/Publications\//.test(u.pathname));
  } catch { return false; }
}
function noticeOk(n: Notice, source: string, from: string, to: string, ids: Set<string>, v2: boolean): void {
  if (!n || typeof n.number !== "string" || (source !== "ORDER" && !/^\d{1,3}\/\d{2}$/.test(n.number)) || !copyOk(n.title, 300) || (n.summary !== undefined && !copyOk(n.summary, 1000)) || (!v2 && !copyOk(n.summary, 1000)) || !officialUrl(n.url, source) || !dateOk(n.posted) || n.posted < from || n.posted > to || typeof n.body_available !== "boolean") throw new Error("Invalid notice");
  const id = source === "ORDER" ? "ORDER-" + n.number.toUpperCase().replace(/[^A-Z0-9]+/g, "-").replace(/^-|-$/g, "") : source + "-" + n.number.replace("/", "-");
  if (ids.has(id) || (v2 && (n.series !== source || n.id !== id))) throw new Error("Duplicate or invalid notice identity");
  ids.add(id);
  if (v2) for (const [key, allowed] of [["lines", LINES], ["paths", PATHS]] as const) {
    const values = n[key];
    if (!Array.isArray(values) || !values.length || values.some(v => !allowed.includes(v)) || new Set(values).size !== values.length) throw new Error("Invalid notice classification");
  }
  const extra = n as Notice & { action?: string; confidence?: string; deadline?: string | null };
  if ((extra.action !== undefined && !["required", "informational"].includes(extra.action)) || (extra.confidence !== undefined && !["high", "medium", "low"].includes(extra.confidence)) || (extra.deadline != null && !dateOk(extra.deadline))) throw new Error("Invalid notice detail");
}
export function validateFeed(input: unknown, now: number): Feed {
  clean(input);
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new Error("Invalid feed");
  const f = input as Feed;
  if (!stampOk(f.generated_at) || Date.parse(f.generated_at) > now) throw new Error("Invalid generation time");
  if (f.schema_version === 2) {
    const v = f as V2Feed;
    if (!Number.isSafeInteger(v.seq) || v.seq < 1 || !stampOk(v.expires_at) || Date.parse(v.expires_at) !== Date.parse(v.generated_at) + 8 * DAY || now >= Date.parse(v.expires_at) || (v.capture_replay !== undefined && v.capture_replay !== false) || !Array.isArray(v.sources) || !v.sources.length || v.sources.length > 4) throw new Error("Invalid v2 feed");
    const sources = new Set<string>();
    for (const b of v.sources) {
      if (!b || !SOURCES.includes(b.source) || sources.has(b.source) || !copyOk(b.coverage, 2000) || !["ok", "failed"].includes(b.status) || (b.status === "ok" ? b.reason !== null : !copyOk(b.reason, 2000)) || !stampOk(b.last_attempt) || Date.parse(b.last_attempt) > Date.parse(v.generated_at) || (b.last_success !== null && (!stampOk(b.last_success) || Date.parse(b.last_success) > Date.parse(b.last_attempt))) || (b.status === "ok" && b.last_success === null) || !b.window || !dateOk(b.window.from) || !dateOk(b.window.to) || b.window.to < b.window.from || Date.parse(b.window.to) - Date.parse(b.window.from) > 30 * DAY || Date.parse(b.window.to) > now || !Array.isArray(b.notices) || b.notices.length > 500 || !Number.isInteger(b.checked_count) || b.checked_count < b.notices.length || !Number.isInteger(b.unclassified_count) || b.unclassified_count < 0 || b.unclassified_count > b.checked_count || typeof b.truncated !== "boolean" || typeof b.body_available !== "boolean" || (b.last_success === null && (b.checked_count || b.notices.length))) throw new Error("Invalid source block");
      sources.add(b.source);
      const ids = new Set<string>();
      for (const n of b.notices) { noticeOk(n, b.source, b.window.from, b.window.to, ids, true); if (b.body_available && !n.body_available) throw new Error("Body coverage mismatch"); }
    }
    return v;
  }
  const v = f as LegacyFeed;
  if (v.schema_version !== 1 || v.source !== "MARADMIN" || !dateOk(v.checked_from) || !dateOk(v.checked_to) || !Array.isArray(v.notices) || v.notices.length > 100 || !Number.isInteger(v.checked_count) || v.checked_count < v.notices.length || v.unclassified_count !== 0 || v.truncated !== false || v.capture_replay !== false) throw new Error("Incomplete or invalid feed");
  const from = Date.parse(v.checked_from), to = Date.parse(v.checked_to);
  if (to < from || to - from > 7 * DAY || to > now || now - Date.parse(v.generated_at) >= 8 * DAY) throw new Error("Stale or invalid feed window");
  const ids = new Set<string>();
  for (const n of v.notices) noticeOk(n, "MARADMIN", v.checked_from, v.checked_to, ids, false);
  return v;
}
export function weeklyFeed(feed: Feed, now: number): Feed {
  if (feed.schema_version !== 2) return feed;
  const start = new Date(Date.parse(weekKey(now)) - 7 * DAY).toISOString().slice(0, 10);
  const end = new Date(now).toISOString().slice(0, 10);
  const cycleStart = Date.parse(weekKey(now)) + 10 * 3600000;
  return { ...feed, sources: (feed as V2Feed).sources.map(b => {
    if (b.status === "ok" && (b.window.from > start || b.window.to < end || b.last_success === null || Date.parse(b.last_success) < cycleStart)) return { ...b, status: "failed", reason: "Source did not cover the digest week in the current cycle" };
    return { ...b, notices: b.notices.filter(n => n.posted >= start && n.posted <= end) };
  }) };
}
function usable(b: SourceBlock): boolean { return b.status === "ok" && !b.truncated && b.unclassified_count === 0; }
function noticeCount(feed: Feed): number { return feed.schema_version === 2 ? (feed as V2Feed).sources.filter(usable).reduce((sum, b) => sum + b.notices.length, 0) : (feed as LegacyFeed).notices.length; }
// Fixed house item markup from RESEND_PLAN.md. No arbitrary HTML from the feed.
export function itemHtml(title: string, summary: string, url: string): string {
  const e = escapeHtml;
  return `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;table-layout:fixed;border-collapse:collapse;"><tr><td bgcolor="#ffffff" style="background-color:#ffffff;padding:12px 0;border-top:1px solid #dcdad3;font-family:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;font-size:14px;line-height:1.5;color:#4a4a4f;font-weight:400;"><a href="${e(url)}" style="font-family:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;font-size:16px;line-height:1.4;color:#8f0b21;font-weight:600;text-decoration:underline;word-break:break-word;overflow-wrap:anywhere;">${e(title)}</a><br>${e(summary)}</td></tr></table>`;
}
export function roundupVariables(feed: Feed): Record<string, string> {
  const v2 = feed.schema_version === 2;
  const blocks: SourceBlock[] = v2 ? (feed as V2Feed).sources : [{ source: "MARADMIN", coverage: "MARADMINs only", status: "ok", reason: null, last_attempt: feed.generated_at, last_success: feed.generated_at, window: { from: (feed as LegacyFeed).checked_from, to: (feed as LegacyFeed).checked_to }, checked_count: (feed as LegacyFeed).checked_count, unclassified_count: 0, truncated: false, body_available: false, notices: (feed as LegacyFeed).notices }];
  const items = blocks.filter(usable).flatMap(b => b.notices.map(n => ({ title: `${b.source} ${n.number}: ${n.title}`, summary: `${n.body_available ? "Applicability unverified." : "Title only; applicability unverified."} ${n.summary ?? "Summary not provided."}`, url: n.url })));
  const statuses = blocks.map(b => `${b.source}: ${!usable(b) ? (b.status === "failed" ? `check failed; ${b.reason}. Last good ${b.last_success ?? "not recorded"}` : "coverage incomplete") : `${b.notices.length} possible matches, ${b.body_available ? "full text" : "titles only"}`}. Coverage: ${b.coverage}.`);
  let html = v2 ? blocks.map((b, i) => `<p>${escapeHtml(statuses[i])}</p>` + (usable(b) ? items.filter(n => n.title.startsWith(b.source + " ")).map(n => itemHtml(n.title, n.summary, n.url)).join("") : "")).join("") : items.map(n => itemHtml(n.title, n.summary, n.url)).join("");
  let text = (v2 ? statuses.join("\n\n") + "\n\n" : "") + items.map(n => `${n.title}. ${n.summary} Source: ${n.url}`).join("\n\n");
  const words = items.map(n => `${n.title} ${n.summary}`).join(" ").split(/\s+/).length + 23;
  if (html.length > 2000 || text.length > 2000 || (items.length && words > 60)) {
    const title = v2 ? `${items.length} possible notice matches` : `${items.length} MARADMIN title matches`;
    const summary = (v2 ? blocks.map(b => `${b.source}: ${usable(b) ? `${b.notices.length} possible matches, ${b.body_available ? "full text" : "titles only"}, ${b.checked_count} checked in the catch-up window` : `check ${b.status === "failed" ? "failed, last good result retained" : "incomplete"}`}.`).join(" ") + " " : "") + "Read the complete roundup and official messages. Applicability is unverified.";
    html = itemHtml(title, summary, WATCH);
    text = `${title}. ${summary} Source: ${WATCH}`;
  }
  const windows = blocks.filter(usable).map(b => b.window);
  const weekEnd = windows.map(w => w.to).sort().at(-1);
  const weekStart = weekEnd ? new Date(Date.parse(weekKey(Date.parse(weekEnd))) - 7 * DAY).toISOString().slice(0, 10) : "unknown";
  const weekOf = v2 ? `${weekStart} to ${weekEnd ?? "unknown"}` : `${(feed as LegacyFeed).checked_from} to ${(feed as LegacyFeed).checked_to}`;
  return { WEEK_OF: weekOf, ITEMS_HTML: html, ITEMS_TEXT: text };
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
      // Watch runs daily at 10:00 UTC and sync at 11:00. The existing
      // Monday digest remains at 15:00 UTC. Allow retries through Monday, ending at 00:00.
      const monday = Date.parse(weekKey(now));
      const cycleStart = monday + 10 * 3600000;
      if (now < monday + 15 * 3600000 || now >= monday + 86400000) return json(200, { ok: true, ...(dry ? { dry: true } : {}), noop: "outside_window" });
      const response = await deps.fetch(FEED, { headers: { Accept: "application/json" }, redirect: "error", signal: AbortSignal.timeout(15000) });
      if (!response.ok) throw new Error("Feed unavailable");
      const raw = await response.text();
      if (new TextEncoder().encode(raw).length > 2_000_000) throw new Error("Feed too large");
      const feed = weeklyFeed(validateFeed(JSON.parse(raw), now), now);
      if (Date.parse(feed.generated_at) < cycleStart) return json(200, { ok: true, ...(dry ? { dry: true } : {}), noop: "stale_feed" });
      const count = noticeCount(feed);
      const coverage = feed.schema_version === 2 ? (feed as V2Feed).sources.map(b => ({ source: b.source, status: b.status, coverage: b.coverage, body_available: b.body_available, truncated: b.truncated, unclassified_count: b.unclassified_count })) : undefined;
      if (feed.schema_version === 2 && !(feed as V2Feed).sources.some(usable)) return json(200, { ok: true, dry, noop: "incomplete_sources", coverage });
      if (!count) {
        const recipients = await database(deps.env, deps.fetch).count({ weekly: "eq.true" });
        return json(200, { ok: true, dry, noop: "no_matches", recipients, eligible: 0, accepted: 0, skipped: recipients, reasons: { no_matches: recipients }, notices: 0, ...(coverage ? { coverage } : {}) });
      }
      const result = await sendTemplates("weekly-roundup", `weekly-roundup:${weekKey(now)}`, roundupVariables(feed), { weekly: "eq.true" }, deps, "weekly", dry);
      return json(200, { ok: true, dry, ...(result.eligible ? {} : { noop: "no_eligible_recipients" }), notices: count, batches: Math.ceil(result.eligible / 100), ...result });
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
