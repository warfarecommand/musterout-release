// Byte limits apply while streaming, before decoding or parsing.
export const BODY_DEADLINE_MS = 5000;
export class BodyReadError extends Error {
  readonly status: number;
  readonly code: string;
  constructor(status: number, code: string) { super(code); this.status = status; this.code = code; }
}

export async function readBody(body: ReadableStream<Uint8Array> | null, cap: number, deadlineMs = BODY_DEADLINE_MS): Promise<string> {
  if (!Number.isSafeInteger(cap) || cap < 1 || !Number.isFinite(deadlineMs) || deadlineMs <= 0) throw new Error("Invalid body limit");
  if (!body) return "";
  const reader = body.getReader();
  const bytes = new Uint8Array(cap + 1);
  const endsAt = performance.now() + deadlineMs;
  let used = 0, timer: ReturnType<typeof setTimeout> | undefined;
  // Cancellation must not wait for a hostile stream's cancel promise.
  const cancel = () => { void reader.cancel().catch(() => {}); };
  const deadline = new Promise<never>((_, reject) => {
    timer = setTimeout(() => { reject(new BodyReadError(408, "body_timeout")); cancel(); }, deadlineMs);
  });
  try {
    const consume = async () => {
      while (true) {
        if (performance.now() >= endsAt) throw new BodyReadError(408, "body_timeout");
        const part = await reader.read();
        if (performance.now() >= endsAt) throw new BodyReadError(408, "body_timeout");
        if (part.done) break;
        const take = Math.min(part.value.byteLength, cap + 1 - used);
        bytes.set(part.value.subarray(0, take), used);
        used += take;
        if (used > cap) throw new BodyReadError(413, "too_large");
      }
      try { return new TextDecoder("utf-8", { fatal: true }).decode(bytes.subarray(0, used)); }
      catch { throw new BodyReadError(400, "invalid_utf8"); }
    };
    return await Promise.race([consume(), deadline]);
  } catch (error) {
    cancel();
    throw error;
  } finally {
    clearTimeout(timer);
    reader.releaseLock();
  }
}
