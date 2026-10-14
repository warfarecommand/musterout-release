// Feed verification ported from board/update_client.js. Keep the canonical
// representation, exact fields, key-kind separation, and rotation signatures.
export const MAX_FEED_BYTES = 2_000_000;
export const FEED_PACK = "usmc-2026.10";
// Independently pinned public roots from config.json, never from the transport.
export const FEED_KEYS: Readonly<Record<string, string>> = Object.freeze({
  "feed-2026-10-05bbe934": "Wu+hyhxyklR3J/HQsbRq6XkCcWjNmiunuCfCb3G8TLo=",
});
const enc = new TextEncoder();
function fail(code: string): never { throw new Error(code); }
export function canonical(value: unknown): string {
  if (value === null || typeof value === "string" || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number" && Number.isSafeInteger(value)) return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
  if (value && Object.getPrototypeOf(value) === Object.prototype) {
    const obj = value as Record<string, unknown>;
    return "{" + Object.keys(obj).sort().map(key => {
      if (!/^[\x20-\x7e]+$/.test(key)) fail("invalid_envelope");
      return JSON.stringify(key) + ":" + canonical(obj[key]);
    }).join(",") + "}";
  }
  return fail("invalid_envelope");
}
function exact(value: any, keys: string[]): void {
  if (!value || typeof value !== "object" || Array.isArray(value) || Object.keys(value).sort().join(",") !== keys.slice().sort().join(",")) fail("invalid_envelope");
}
function bytes64(value: unknown, size: number): Uint8Array {
  if (typeof value !== "string" || !/^[A-Za-z0-9+/]+={0,2}$/.test(value)) fail("bad_signature");
  let result: Uint8Array;
  try { result = Uint8Array.from(atob(value), c => c.charCodeAt(0)); } catch { return fail("bad_signature"); }
  if (result.length !== size || btoa(String.fromCharCode(...result)) !== value) fail("bad_signature");
  return result;
}
function stamp(value: unknown): number {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/.test(value) || !Number.isFinite(Date.parse(value))) fail("invalid_envelope");
  return Date.parse(value);
}
async function signed(key: string, signature: unknown, message: unknown): Promise<void> {
  try {
    const imported = await crypto.subtle.importKey("raw", bytes64(key, 32), "Ed25519", false, ["verify"]);
    if (!await crypto.subtle.verify("Ed25519", imported, bytes64(signature, 64), enc.encode(canonical(message)))) fail("bad_signature");
  } catch { fail("bad_signature"); }
}
export type VerifiedFeed = { data: any; envelope: { seq: number; sha256: string } };
export async function verifyFeedTransport(script: string, options: { now: number; lastSeq?: number; keys?: Readonly<Record<string, string>>; pack?: string }): Promise<VerifiedFeed> {
  if (enc.encode(script).length > MAX_FEED_BYTES) fail("too_large");
  if (!script.startsWith("self.postMessage(") || !script.endsWith(");\n")) fail("invalid_transport");
  const transport = JSON.parse(script.slice("self.postMessage(".length, -3));
  exact(transport, ["envelope", "signature", "data"]);
  const e = transport.envelope;
  exact(e, ["product", "kind", "seq", "pack", "sha256", "size", "created", "expires", "key_id", "keychain"]);
  if (e.product !== "Muster Out") fail("wrong_product");
  if (e.kind !== "feed") fail("wrong_kind");
  if (e.pack !== (options.pack ?? FEED_PACK)) fail("wrong_pack");
  if (typeof e.key_id !== "string" || !e.key_id || !/^[a-f0-9]{64}$/.test(e.sha256) || !Number.isSafeInteger(e.size) || e.size < 1 || e.size > MAX_FEED_BYTES) fail("invalid_envelope");
  if (!Number.isSafeInteger(e.seq) || e.seq < 1 || stamp(e.expires) <= stamp(e.created)) fail("invalid_envelope");
  const trusted = new Map(Object.entries(options.keys ?? FEED_KEYS));
  if (!Array.isArray(e.keychain) || e.keychain.length > 16) fail("invalid_keychain");
  for (const link of e.keychain) {
    exact(link, ["key_id", "public_key", "signed_by", "signature"]);
    if (typeof link.key_id !== "string" || !link.key_id || typeof link.signed_by !== "string" || trusted.has(link.key_id) || !trusted.has(link.signed_by)) fail("invalid_keychain");
    bytes64(link.public_key, 32);
    await signed(trusted.get(link.signed_by)!, link.signature, { product: e.product, kind: "feed", key_id: link.key_id, public_key: link.public_key, signed_by: link.signed_by });
    trusted.set(link.key_id, link.public_key);
  }
  if (!trusted.has(e.key_id)) fail("untrusted_key");
  await signed(trusted.get(e.key_id)!, transport.signature, e);
  const payload = canonical(transport.data), bytes = enc.encode(payload);
  if (bytes.length !== e.size) fail("size_mismatch");
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))).map(x => x.toString(16).padStart(2, "0")).join("");
  if (hash !== e.sha256) fail("hash_mismatch");
  if (e.seq <= (options.lastSeq ?? 0)) fail("replay");
  if (stamp(e.expires) <= options.now) fail("expired");
  if (stamp(e.created) > options.now) fail("future_feed");
  const data = transport.data;
  if (!data || data.schema_version !== 2 || data.seq !== e.seq || data.generated_at !== e.created || data.expires_at !== e.expires) fail("invalid_payload");
  return { data, envelope: e };
}
