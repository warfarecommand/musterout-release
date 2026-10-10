// Owner-run mail only. Reader: a confirmed subscriber. Effect: learn a correction.
import { database, ENDPOINT, FROM, hash, RECENT_HASHES, PLATFORM_CONSENT, PLATFORM_SCOPE, MUSTEROUT_SCOPE, renderEmail, type Env, type Row, token, unsubscribeHeaders } from "./index.ts";

export function readMessage(source: string): { subject: string; paragraphs: string[] } {
  const lines = source.replace(/\r\n/g, "\n").trim().split("\n");
  const subject = lines.shift()?.trim() ?? "";
  if (!subject || subject.length > 200 || lines.shift() !== "") throw new Error("Use a subject line, a blank line, then one line per paragraph");
  const paragraphs = lines.filter((line) => line.trim()).map((line) => line.trim());
  if (!paragraphs.length || source.length > 12000 || /[\u2013\u2014!\p{Extended_Pictographic}\p{Emoji_Presentation}]/u.test(source) || /[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/.test(source)) throw new Error("Use a short plain body, short hyphens, and no emoji or exclamation points");
  return { subject, paragraphs };
}

export async function sendAlert(source: string, send: boolean, deps: { env: Env; fetch: typeof fetch; now?: () => number; print: (line: string) => void; audience?: "corrections" | "platform"; musterOutUpdate?: boolean }): Promise<void> {
  const { subject, paragraphs } = readMessage(source);
  const db = database(deps.env, deps.fetch);
  const platformOnly = deps.audience === "platform";
  const consentFilter = platformOnly ? { confirm_hash: `eq.${PLATFORM_CONSENT}` } : {};
  if (!send) { deps.print(String(await db.count(consentFilter))); return; }
  const key = deps.env("RESEND_API_KEY");
  if (!key) throw new Error("RESEND_API_KEY is not configured");
  // Take a paginated snapshot of IDs only. Recheck consent before each send.
  const ids: string[] = [];
  let after = "";
  while (true) {
    const rows = await db.rows<{ id: string }>("alert_signups", "GET", { select: "id", status: "eq.confirmed", ...consentFilter, order: "id.asc", limit: "500", ...(after ? { id: `gt.${after}` } : {}) });
    if (!rows.length) break;
    ids.push(...rows.map((row) => row.id));
    after = rows[rows.length - 1].id;
  }
  let sentCount = 0;
  for (let start = 0; start < ids.length; start += 100) {
    const messages: Record<string, unknown>[] = [];
    const receipts: { id: string; digest: string }[] = [];
    for (const id of ids.slice(start, start + 100)) {
      // Compare the whole array so concurrent sends cannot overwrite receipts.
      let reserved: Row | undefined;
      const raw = token(), digest = await hash(raw);
      for (let retry = 0; retry < 3; retry++) {
        const row = (await db.rows("alert_signups", "GET", { id: `eq.${id}`, status: "eq.confirmed", ...consentFilter, select: "id,email,status,confirm_hash,unsubscribe_hashes,last_sent_at" }))[0];
        if (!row) break;
        const hashes = [...row.unsubscribe_hashes, digest].slice(-RECENT_HASHES);
        reserved = (await db.rows("alert_signups", "PATCH", { id: `eq.${id}`, status: "eq.confirmed", ...consentFilter, unsubscribe_hashes: `eq.{${row.unsubscribe_hashes.join(",")}}` }, { unsubscribe_hashes: hashes }))[0];
        if (reserved) break;
        if (retry === 2) throw new Error("Concurrent update prevented a send; stop and review before retrying");
      }
      if (!reserved) continue;
      const unsubscribeUrl = `${ENDPOINT}?unsubscribe=${raw}`;
      const mail = renderEmail({ preheader: paragraphs[0] ?? subject, eyebrow: deps.musterOutUpdate ? "Muster Out update" : platformOnly ? "Warfare Command updates" : "Muster Out correction alerts", heading: subject, paragraphs, callout: deps.musterOutUpdate ? { label: "To update your board, paste this into any Claude chat", body: "Update Muster Out. Read https://raw.githubusercontent.com/warfarecommand/musterout-release/main/UPDATE.md and follow it." } : undefined, reason: reserved.confirm_hash === PLATFORM_CONSENT ? `You received this because you confirmed ${PLATFORM_SCOPE}.` : `You received this because you confirmed Muster Out ${MUSTEROUT_SCOPE}.`, unsubscribeUrl });
      messages.push({ from: FROM, to: [reserved.email], subject, text: mail.text, html: mail.html, headers: unsubscribeHeaders(unsubscribeUrl) });
      receipts.push({ id, digest });
    }
    if (!messages.length) continue;
    // No automatic retry after an ambiguous network response. An idempotency
    // key protects this batch, but a new run deliberately gets fresh tokens.
    const response = await deps.fetch("https://api.resend.com/emails/batch", { method: "POST", headers: { Authorization: `Bearer ${key}`, "content-type": "application/json", "Idempotency-Key": `alerts-batch-${await hash(receipts.map((r) => r.digest).join(""))}` }, body: JSON.stringify(messages) });
    if (!response.ok) throw new Error(`Batch failed after ${sentCount} accepted emails; review delivery before retrying`);
    const result = await response.json();
    if (!Array.isArray(result.data) || result.data.length !== messages.length || result.data.some((entry: { id?: string }) => !entry.id)) throw new Error(`Uncertain batch response after ${sentCount} accepted emails; review delivery before retrying`);
    sentCount += messages.length;
    deps.print(`Accepted: ${sentCount}`);
    const last_sent_at = new Date(deps.now?.() ?? Date.now()).toISOString();
    for (const receipt of receipts) await db.rows("alert_signups", "PATCH", { id: `eq.${receipt.id}`, status: "eq.confirmed", ...consentFilter, unsubscribe_hashes: `cs.{${receipt.digest}}` }, { last_sent_at });
  }
  deps.print(`Accepted total: ${sentCount}`);
}

if (import.meta.main) {
  const args = Deno.args;
  const flags = ["--send", "--platform", "--musterout-update"];
  const files = args.filter((arg) => !flags.includes(arg));
  if (files.length !== 1 || args.some((arg) => arg.startsWith("--") && !flags.includes(arg)) || flags.some((flag) => args.filter((arg) => arg === flag).length > 1)) {
    console.error("Usage: deno run --allow-env --allow-net --allow-read send_alert.ts message.txt [--platform] [--musterout-update] [--send]");
    Deno.exit(1);
  }
  try {
    await sendAlert(await Deno.readTextFile(files[0]), args.includes("--send"), { env: (name) => Deno.env.get(name), fetch, print: console.log, audience: args.includes("--platform") ? "platform" : "corrections", musterOutUpdate: args.includes("--musterout-update") });
  } catch (error) {
    // Suppress network exception text because it can contain private URLs.
    console.error(error instanceof Error && !/https?:|@/.test(error.message) ? error.message : "Send stopped; review delivery before retrying");
    Deno.exit(1);
  }
}
