// Owner-reviewed campaigns only. Dry run unless --send is present.
import { escapeHtml, sendTemplates } from "./index.ts";
import type { SendDeps, Stream } from "./index.ts";
const REQUIRED: Record<string, string[]> = {
  "correction-alert": ["WHAT_CHANGED", "WHO_IS_AFFECTED", "WHAT_TO_DO", "VERSION"],
  "monthly": ["SHIPPED", "NEXT", "AI_MOVE", "QUESTION"],
  "lesson-launch": ["LESSON_TITLE", "LESSON_PROMISE", "LESSON_URL"],
};
const STREAMS: Record<string, Stream> = { "correction-alert": "corrections", monthly: "monthly", "lesson-launch": "lessons" };
export type Message = { template: string; campaign: string; variables: Record<string, string> };
export function readMessage(raw: string): Message {
  if (raw.length > 25000) throw new Error("Message file is too large");
  let m: Message;
  try { m = JSON.parse(raw); } catch { throw new Error("Message must be a JSON object"); }
  if (!m || typeof m.template !== "string" || typeof m.campaign !== "string" || !Object.hasOwn(REQUIRED, m.template) || !/^[a-zA-Z0-9_-]{1,100}$/.test(m.campaign) || !m.variables || typeof m.variables !== "object" || Array.isArray(m.variables) || Object.keys(m).some(k => !["template", "campaign", "variables"].includes(k))) throw new Error("Provide template, campaign, and variables");
  if (Object.keys(m.variables).some(k => !REQUIRED[m.template].includes(k)) || REQUIRED[m.template].some(k => typeof m.variables[k] !== "string" || !m.variables[k].trim())) throw new Error("Every campaign block must contain reviewed copy; empty Monthly sends are refused");
  for (const value of Object.values(m.variables)) {
    if (typeof value !== "string" || escapeHtml(value).length > 2000 || /[<>\u0000-\u001f\u007f\u2013\u2014!]|\p{Extended_Pictographic}/u.test(value) || /\{\{/.test(value)) throw new Error("Use plain reviewed copy within template limits");
  }
  if (m.template === "lesson-launch") {
    let url: URL; try { url = new URL(m.variables.LESSON_URL); } catch { throw new Error("Use the verified HTTPS lesson URL"); }
    if (url.protocol !== "https:" || url.origin !== "https://warfarecommand.com" || url.username || url.password) throw new Error("Use the verified Warfare Command lesson URL");
  }
  return m;
}
export async function sendAlert(raw: string, send: boolean, deps: SendDeps & { print: (line: string) => void }): Promise<void> {
  const message = readMessage(raw), stream = STREAMS[message.template];
  const variables = Object.fromEntries(Object.entries(message.variables).map(([k, v]) => [k, escapeHtml(v)]));
  const report = await sendTemplates(message.template, `${message.template}:${message.campaign}`, variables, { [stream]: "eq.true" }, deps, stream, !send);
  deps.print(JSON.stringify({ dry: !send, ...report }));
}
if (import.meta.main) {
  const args = Deno.args, files = args.filter(arg => arg !== "--send");
  if (files.length !== 1 || args.some(arg => arg.startsWith("--") && arg !== "--send") || args.filter(arg => arg === "--send").length > 1) {
    console.error("Usage: deno run --allow-env --allow-net --allow-read send_alert.ts message.json [--send]"); Deno.exit(1);
  }
  try { await sendAlert(await Deno.readTextFile(files[0]), args.includes("--send"), { env: name => Deno.env.get(name), fetch, print: console.log }); }
  catch (error) { console.error(error instanceof Error && !/https?:|@/.test(error.message) ? error.message : "Send stopped; review delivery receipts"); Deno.exit(1); }
}
