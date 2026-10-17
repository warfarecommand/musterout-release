// Configure only after proving the gateway overwrites the chosen header.
// Unconfigured, missing, or ambiguous addresses share SQL's unknown bucket.
function prefix(raw: string): string | null {
  if (/^\d{1,3}(\.\d{1,3}){3}$/.test(raw)) {
    const parts = raw.split('.');
    if (!parts.every(x => Number(x) <= 255 && String(Number(x)) === x)) return null;
    return 'v4:' + parts.slice(0, 3).join('.');
  }
  if (!raw.includes(':') || !/^[a-fA-F0-9:.]+$/.test(raw)) return null;
  try {
    const canonical = new URL('https://[' + raw + ']/').hostname.slice(1, -1);
    const halves = canonical.split('::');
    const left = halves[0] ? halves[0].split(':') : [];
    const right = halves[1] ? halves[1].split(':') : [];
    const words = (halves.length === 2
      ? [...left, ...Array(8 - left.length - right.length).fill('0'), ...right]
      : left).map(x => parseInt(x, 16));
    if (words.length !== 8 || words.some(x => !Number.isInteger(x))) return null;
    // IPv4-mapped IPv6 and ordinary IPv4 must share the same /24 allowance.
    if (words.slice(0, 5).every(x => x === 0) && words[5] === 0xffff) {
      return 'v4:' + [words[6] >> 8, words[6] & 255, words[7] >> 8].join('.');
    }
    return 'v6:' + words.slice(0, 3).map(x => x.toString(16).padStart(4, '0')).join(':')
      + ':' + (words[3] >> 8).toString(16).padStart(2, '0');
  } catch { return null; }
}

export async function rg3NetworkHash(req: Request, env: (name: string) => string | undefined, now: number): Promise<string | null> {
  const header = env('RG3_CLIENT_IP_HEADER');
  const secret = env('RG3_NETWORK_SECRET');
  if (!header || !['cf-connecting-ip', 'x-real-ip', 'x-forwarded-for'].includes(header)
    || !secret || new TextEncoder().encode(secret).length < 32) return null;
  const raw = req.headers.get(header)?.trim();
  const network = raw ? prefix(raw) : null;
  if (!network) return null;
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', encoder.encode(secret), {name: 'HMAC', hash: 'SHA-256'}, false, ['sign']);
  const bytes = await crypto.subtle.sign('HMAC', key, encoder.encode(
    'musterout-rg3-network-v1\n' + new Date(now).toISOString().slice(0, 10) + '\n' + network));
  return Array.from(new Uint8Array(bytes), x => x.toString(16).padStart(2, '0')).join('');
}
