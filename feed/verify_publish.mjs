// Authenticate signed feed data before staging the npm package. No private keys.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createPublicKey, verify, createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';

function canonical(v) {
  if (v === null || typeof v === 'string' || typeof v === 'boolean' || Number.isSafeInteger(v)) return JSON.stringify(v);
  if (Array.isArray(v)) return '[' + v.map(canonical).join(',') + ']';
  assert(v && typeof v === 'object', 'Noncanonical JSON value');
  return '{' + Object.keys(v).sort().map(k => {
    assert(/^[\x20-\x7e]+$/.test(k), 'Non-ASCII object key');
    return JSON.stringify(k) + ':' + canonical(v[k]);
  }).join(',') + '}';
}
function exact(v, fields) {
  assert(v && typeof v === 'object' && !Array.isArray(v));
  assert.deepEqual(Object.keys(v).sort(), [...fields].sort());
}
function raw64(s, size) {
  assert.equal(typeof s, 'string');
  const bytes = Buffer.from(s, 'base64');
  assert.equal(bytes.length, size); assert.equal(bytes.toString('base64'), s);
  return bytes;
}
function signature(key, sig, message) {
  const publicKey = createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),raw64(key,32)]),format:'der',type:'spki'});
  assert(verify(null, Buffer.from(canonical(message)), publicKey, raw64(sig,64)), 'Invalid Ed25519 feed signature');
}
export function verifyFeed(root = '.', env = process.env) {
  const read = name => fs.readFileSync(path.join(root,name));
  const source = read('feed/v2/feed.js');
  assert(source.length <= 2000030, 'Oversized feed transport');
  const script = source.toString('utf8');
  assert(source.equals(Buffer.from(script)), 'Invalid UTF-8');
  assert(script.startsWith('self.postMessage(') && script.endsWith(');\n'), 'Invalid feed wrapper');
  const payload = JSON.parse(script.slice(17,-3));
  exact(payload,['envelope','signature','data']);
  assert.equal(script.slice(17,-3),canonical(payload).replaceAll('\u2028','\\u2028').replaceAll('\u2029','\\u2029'), 'Noncanonical or duplicate transport fields');
  assert(Buffer.byteLength(canonical(payload)) <= 2000000);
  const e = payload.envelope;
  exact(e,['product','kind','seq','pack','sha256','size','created','expires','key_id','keychain']);
  assert.equal(e.product,'Muster Out'); assert.equal(e.kind,'feed');
  assert(Number.isSafeInteger(e.seq) && e.seq > 0);
  assert(Number.isSafeInteger(e.size) && e.size > 0 && e.size <= 2000000);
  assert(/^[a-f0-9]{64}$/.test(e.sha256));
  assert(typeof e.key_id === 'string' && /^[A-Za-z0-9._-]{1,100}$/.test(e.key_id));
  const config = JSON.parse(read('config.json'));
  assert.equal(config.product,e.product); assert.equal(config.pack,e.pack);
  const roots = JSON.parse(read('npm/musterout-feed/public_keys.json'));
  exact(roots,['feed_keys']);
  assert(roots.feed_keys && !Array.isArray(roots.feed_keys) && Object.keys(roots.feed_keys).length > 0, 'Empty committed feed roots');
  for (const key of Object.values(roots.feed_keys)) {
    raw64(key,32);
    assert(!Object.values(config.update_keys.release_keys || {}).includes(key), 'Release and feed roots must differ');
  }
  raw64(env.MO_FEED_PUBLIC_KEY,32);
  assert(Object.values(roots.feed_keys).includes(env.MO_FEED_PUBLIC_KEY), 'Actions variable differs from committed public root');
  if (env.MO_FEED_KEY_ID) assert.equal(roots.feed_keys[env.MO_FEED_KEY_ID],env.MO_FEED_PUBLIC_KEY);
  assert.deepEqual(roots.feed_keys,config.update_keys.feed_keys, 'Feed package roots differ from board roots');
  const trusted = new Map(Object.entries(roots.feed_keys));
  assert(Array.isArray(e.keychain) && e.keychain.length <= 16);
  for (const link of e.keychain) {
    exact(link,['key_id','public_key','signed_by','signature']);
    assert(typeof link.key_id === 'string' && /^[A-Za-z0-9._-]{1,100}$/.test(link.key_id) && !trusted.has(link.key_id) && trusted.has(link.signed_by));
    raw64(link.public_key,32);
    signature(trusted.get(link.signed_by),link.signature,{product:e.product,kind:'feed',key_id:link.key_id,public_key:link.public_key,signed_by:link.signed_by});
    trusted.set(link.key_id,link.public_key);
  }
  assert(trusted.has(e.key_id), 'Untrusted feed signing key');
  signature(trusted.get(e.key_id),payload.signature,e);
  const data = Buffer.from(canonical(payload.data));
  assert.equal(data.length,e.size);
  assert.equal(createHash('sha256').update(data).digest('hex'),e.sha256);
  assert.equal(canonical(JSON.parse(read('feed/v2/latest.json'))),data.toString(), 'Feed projection differs from signed data');
  // Strict source schemas run only after the signature and canonical hash pass.
  execFileSync('python3',['-B','-c','import json,sys; from validate_v2 import validate_feed; validate_feed(json.load(sys.stdin))'],{cwd:path.join(root,'feed'),input:data,stdio:['pipe','pipe','pipe']});
  assert.equal(payload.data.seq,e.seq); assert.equal(payload.data.generated_at,e.created); assert.equal(payload.data.expires_at,e.expires);
  assert.equal(payload.data.capture_replay,false,'Captured fixtures cannot publish');
  for (const stamp of [e.created,e.expires]) {
    assert(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/.test(stamp));
    const ms = Date.parse(stamp); assert(Number.isFinite(ms));
    assert.equal(new Date(ms).toISOString(),stamp.length === 20 ? stamp.slice(0,-1)+'.000Z' : stamp);
  }
  assert(Date.parse(e.created) <= Date.now() && Date.parse(e.expires) > Date.now(), 'Future or expired feed');
  const pkg = JSON.parse(read('npm/musterout-feed/package.json'));
  assert.equal(pkg.name,'musterout-feed'); assert.equal(pkg.license,'MIT'); assert.deepEqual(pkg.files,['feed.js']);
  assert.equal(pkg.repository.url,'https://github.com/warfarecommand/musterout-release.git');
  for (const field of ['scripts','dependencies','devDependencies','optionalDependencies','peerDependencies','bundledDependencies']) assert(!pkg[field],field);
  return {seq:e.seq, source, pkg};
}
export function preparePackage(root, verified, publishedVersion) {
  if (publishedVersion !== null) {
    assert(/^1\.0\.(0|[1-9][0-9]*)$/.test(publishedVersion), 'Unexpected published feed version');
    const previous = Number(publishedVersion.slice(4));
    assert(Number.isSafeInteger(previous));
    if (verified.seq <= previous) {
      console.log('Feed seq '+verified.seq+' is already published or older; no publish');
      return false;
    }
  }
  verified.pkg.version = '1.0.' + verified.seq;
  fs.writeFileSync(path.join(root,'npm/musterout-feed/package.json'),JSON.stringify(verified.pkg,null,2)+'\n');
  fs.writeFileSync(path.join(root,'npm/musterout-feed/feed.js'),verified.source);
  return true;
}
async function main() {
  const root = process.cwd();
  const verified = verifyFeed(root);
  const response = await fetch('https://registry.npmjs.org/musterout-feed/latest',{redirect:'error',signal:AbortSignal.timeout(20000)});
  let publishedVersion = null;
  if (response.status !== 404) {
    assert(response.ok,'npm registry check failed: '+response.status);
    const body = await response.text(); assert(Buffer.byteLength(body) <= 1000000);
    const published = JSON.parse(body); assert.equal(published.name,'musterout-feed');
    publishedVersion = published.version;
  }
  const publish = preparePackage(root,verified,publishedVersion);
  if (process.env.GITHUB_OUTPUT) fs.appendFileSync(process.env.GITHUB_OUTPUT,'publish='+publish+'\nversion=1.0.'+verified.seq+'\n');
  console.log('Verified feed seq '+verified.seq+'; publish='+publish);
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
