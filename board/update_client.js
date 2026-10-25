/* Muster Out signed update engine. No board data enters the worker. */
(function (global) {
'use strict';
var MAX_BYTES = 2000000, enc = new TextEncoder();
function fail(code) { throw Object.assign(new Error(code), {code: code}); }
function canonical(value) {
if (value === null || typeof value === 'string' || typeof value === 'boolean') return JSON.stringify(value);
if (typeof value === 'number' && Number.isSafeInteger(value)) return JSON.stringify(value);
if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
if (value && Object.getPrototypeOf(value) === Object.prototype) {
return '{' + Object.keys(value).sort().map(function (key) {
if (!/^[\x20-\x7e]+$/.test(key)) fail('invalid_envelope');
return JSON.stringify(key) + ':' + canonical(value[key]);
}).join(',') + '}';
}
fail('invalid_envelope');
}
function exact(value, keys) {
if (!value || Array.isArray(value) || Object.keys(value).sort().join(',') !== keys.slice().sort().join(',')) fail('invalid_envelope');
}
function bytes64(value, size) {
if (typeof value !== 'string' || !/^[A-Za-z0-9+/]+={0,2}$/.test(value)) fail('bad_signature');
var result;
try { result = Uint8Array.from(atob(value), function (c) { return c.charCodeAt(0); }); } catch (_) { fail('bad_signature'); }
if (result.length !== size || btoa(String.fromCharCode.apply(null, result)) !== value) fail('bad_signature');
return result;
}
function semver(value) {
if (typeof value !== 'string' || value.length > 128) fail('invalid_version');
var m = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$/.exec(value);
if (!m) fail('invalid_version');
var pre = m[4] ? m[4].split('.') : [];
if (pre.some(function (s) { return /^\d+$/.test(s) && s.length > 1 && s[0] === '0'; })) fail('invalid_version');
return {core: m.slice(1, 4), pre: pre};
}
function digits(a, b) { return a.length !== b.length ? Math.sign(a.length - b.length) : a === b ? 0 : a > b ? 1 : -1; }
function compare(a, b) {
a = semver(a); b = semver(b);
for (var i = 0; i < 3; i++) { var d = digits(a.core[i], b.core[i]); if (d) return d; }
if (!a.pre.length || !b.pre.length) return a.pre.length === b.pre.length ? 0 : a.pre.length ? -1 : 1;
for (var j = 0; j < Math.max(a.pre.length, b.pre.length); j++) {
if (a.pre[j] === undefined || b.pre[j] === undefined) return a.pre[j] === undefined ? -1 : 1;
var x = a.pre[j], y = b.pre[j];
if (x === y) continue;
var xn = /^\d+$/.test(x), yn = /^\d+$/.test(y);
return xn && yn ? digits(x, y) : xn !== yn ? xn ? -1 : 1 : x > y ? 1 : -1;
}
return 0;
}
function stamp(value) {
if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/.test(value) || !Number.isFinite(Date.parse(value))) fail('invalid_envelope');
if (new Date(Date.parse(value)).toISOString() !== (value.length === 20 ? value.slice(0,-1) + '.000Z' : value) || value.startsWith('0000-')) fail('invalid_envelope');
return Date.parse(value);
}
async function signed(key, signature, message) {
try {
var imported = await crypto.subtle.importKey('raw', bytes64(key, 32), {name: 'Ed25519'}, false, ['verify']);
if (!await crypto.subtle.verify('Ed25519', imported, bytes64(signature, 64), enc.encode(canonical(message)))) fail('bad_signature');
} catch (_) { fail('bad_signature'); }
}
async function verifySignedEnvelope(e, signature, options) {
options = options || {};
var kind = options.kind;
if (kind !== 'release' && kind !== 'feed') fail('wrong_kind');
exact(e, kind === 'release' ? ['product','kind','version','pack','sha256','size','created','key_id','notes','correction','impact','keychain'] : ['product','kind','seq','pack','sha256','size','created','expires','key_id','keychain']);
if (e.product !== 'Muster Out') fail('wrong_product');
if (e.kind !== kind) fail('wrong_kind');
if (typeof e.pack !== 'string' || !e.pack || typeof e.key_id !== 'string' || !e.key_id || !/^[a-f0-9]{64}$/.test(e.sha256) || !Number.isSafeInteger(e.size) || e.size < 1 || e.size > MAX_BYTES) fail('invalid_envelope');
if (options.pack && e.pack !== options.pack) fail('wrong_pack');
stamp(e.created);
if (kind === 'release') {
semver(e.version);
if (!Array.isArray(e.notes) || e.notes.length > 3 || e.notes.some(function (n) { return typeof n !== 'string' || n.length > 500; }) || typeof e.correction !== 'boolean' || !(e.impact === null || typeof e.impact === 'string' && e.impact.length <= 1000) || e.correction && (!e.impact || !e.impact.trim())) fail('invalid_envelope');
} else {
if (!Number.isSafeInteger(e.seq) || e.seq < 1 || stamp(e.expires) <= stamp(e.created)) fail('invalid_envelope');
}
var roots = options[kind + '_keys'] || {}, trusted = new Map(Object.entries(roots));
if (!Array.isArray(e.keychain) || e.keychain.length > 16) fail('invalid_keychain');
for (var link of e.keychain) {
exact(link, ['key_id','public_key','signed_by','signature']);
if (typeof link.key_id !== 'string' || !link.key_id || typeof link.signed_by !== 'string' || trusted.has(link.key_id) || !trusted.has(link.signed_by)) fail('invalid_keychain');
bytes64(link.public_key, 32);
await signed(trusted.get(link.signed_by), link.signature, {product: e.product, kind: kind, key_id: link.key_id, public_key: link.public_key, signed_by: link.signed_by});
trusted.set(link.key_id, link.public_key);
}
if (!trusted.has(e.key_id)) fail('untrusted_key');
await signed(trusted.get(e.key_id), signature, e);
return e;
}
async function verifyEnvelope(e, signature, payload, options) {
options = options || {};
var kind = options.kind;
await verifySignedEnvelope(e, signature, options);
if (typeof payload !== 'string' || payload.length > MAX_BYTES) fail('too_large');
var bytes = enc.encode(payload);
if (bytes.length !== e.size) fail('size_mismatch');
var hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))).map(function (x) { return x.toString(16).padStart(2,'0'); }).join('');
if (hash !== e.sha256) fail('hash_mismatch');
if (kind === 'release') {
if (!payload.startsWith('<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>') || !payload.endsWith('</body></html>')) fail('invalid_document');
if (compare(e.version, options.currentVersion) <= 0) fail('not_newer');
} else {
if (e.seq <= (options.lastSeq || 0)) fail('replay');
if (stamp(e.expires) <= (options.now === undefined ? Date.now() : options.now)) fail('expired');
try { if (canonical(JSON.parse(payload)) !== payload) fail('invalid_payload'); } catch (_) { fail('invalid_payload'); }
}
return e;
}
// Bound plain JSON before serialization, canonicalization or signature work.
// Structured clone can carry cycles, transferables and non-JSON objects.
function boundedMessage(value, kind, ports) {
if (ports && ports.length) fail('invalid_message');
var bytes = 0, nodes = 0, seen = new Set();
function visit(item, depth) {
if (++nodes > 50000 || depth > 32) fail('too_large');
if (item === null || typeof item === 'boolean') { bytes += 5; }
else if (typeof item === 'number' && Number.isSafeInteger(item)) { bytes += 24; }
else if (typeof item === 'string') {
// Refuse large strings before allocating their UTF-8 encoding.
if (item.length > MAX_BYTES) fail('too_large');
bytes += enc.encode(item).length + 2;
} else if (item && typeof item === 'object') {
if (seen.has(item)) fail('invalid_message');
seen.add(item);
if (Array.isArray(item)) {
if (item.length > 50000) fail('too_large');
bytes += item.length + 2;
for (var child of item) visit(child, depth + 1);
} else {
if (Object.getPrototypeOf(item) !== Object.prototype) fail('invalid_message');
var keys = Object.keys(item);
if (keys.length > 256) fail('too_large');
bytes += keys.length * 2 + 2;
for (var key of keys) { visit(key, depth + 1); visit(item[key], depth + 1); }
}
} else fail('invalid_message');
if (bytes > MAX_BYTES) fail('too_large');
}
visit(value, 0);
exact(value, kind === 'release' ? ['envelope','signature','html'] : ['envelope','signature','data']);
if (typeof value.signature !== 'string' || value.signature.length > 100) fail('invalid_message');
var e = value.envelope;
exact(e, kind === 'release' ? ['product','kind','version','pack','sha256','size','created','key_id','notes','correction','impact','keychain'] : ['product','kind','seq','pack','sha256','size','created','expires','key_id','keychain']);
if (e.kind !== kind) fail('wrong_kind');
if (!Array.isArray(e.keychain) || e.keychain.length > 16) fail('invalid_message');
if (kind === 'release' ? typeof value.html !== 'string' : !value.data || Array.isArray(value.data) || typeof value.data !== 'object') fail('invalid_message');
// Retain the exact serialized byte ceiling as well as the traversal bounds.
if (enc.encode(JSON.stringify(value)).length > MAX_BYTES) fail('too_large');
return value;
}
// Defense in depth for mutable channel code. This is not a JavaScript sandbox.
// No state enters this worker. Remove origin storage, communication and nested
// worker APIs from their defining prototypes before the single captured import.
function channelWorker(source, kind) {
'use strict';
var root = globalThis, load = root.importScripts.bind(root), send = root.postMessage.bind(root), close = root.close.bind(root);
var define = Object.defineProperty, proto = Object.getPrototypeOf, own = Function.call.bind(Object.prototype.hasOwnProperty), sent = false;
function deny(object, name, value) {
for (var current = object; current; current = proto(current)) {
if (own(current, name)) define(current, name, {value:value, writable:false, configurable:false});
}
define(object, name, {value:value, writable:false, configurable:false});
}
function once(value, transfer) {
if (sent) return;
sent = true;
try { if (transfer !== undefined) fail('invalid_message'); boundedMessage(value, kind); send(value); }
catch (error) { var code = error && error.code; send({channel_error:code === 'too_large' ? 'too_large' : code === 'wrong_kind' ? 'wrong_kind' : 'invalid_message'}); }
finally { close(); }
}
// Also cover OPFS and locks exposed through WorkerNavigator, then remove its
// accessor so constructor/prototype walks cannot recover the original object.
if (root.navigator) ['storage','locks','serviceWorker','sendBeacon'].forEach(function (name) { deny(root.navigator, name, undefined); });
['indexedDB','caches','Worker','SharedWorker','fetch','XMLHttpRequest','WebSocket','WebSocketStream','WebTransport','EventSource','BroadcastChannel','navigator','importScripts'].forEach(function (name) { deny(root, name, undefined); });
deny(root, 'postMessage', once);
load(source);
}
function loadWorker(source, kind) {
return new Promise(function (resolve, reject) {
var worker, url, timer, settled = false;
function finish(error, value) {
if (settled) return;
settled = true;
clearTimeout(timer);
if (worker) worker.terminate();
if (url) URL.revokeObjectURL(url);
if (error) reject(Object.assign(new Error(error), {code:error})); else resolve(value);
}
try {
url = URL.createObjectURL(new Blob(['var MAX_BYTES=' + MAX_BYTES + ',enc=new TextEncoder();\n' + fail.toString() + '\n' + exact.toString() + '\n' + boundedMessage.toString() + '\n(' + channelWorker.toString() + ')(' + JSON.stringify(source) + ',' + JSON.stringify(kind) + ');'], {type:'text/javascript'}));
worker = new Worker(url);
timer = setTimeout(function () { finish('worker_timeout'); }, 20000);
worker.onerror = function (event) { event.preventDefault(); finish('worker_error'); };
worker.onmessageerror = function () { finish('worker_error'); };
worker.onmessage = function (event) {
// Kill on the first message, before verification or any asynchronous work.
var value = event.data;
worker.terminate();
try {
// A rejected child sends only this fixed failure schema, never the rejected data.
if (event.ports && event.ports.length) fail('invalid_message');
if (value && Object.prototype.hasOwnProperty.call(value, 'channel_error')) {
exact(value, ['channel_error']);
if (!['too_large','wrong_kind','invalid_message'].includes(value.channel_error)) fail('invalid_message');
return finish(value.channel_error);
}
boundedMessage(value, kind, event.ports);
finish(null, value);
} catch (error) { finish(['too_large','wrong_kind'].includes(error.code) ? error.code : 'invalid_message'); }
};
} catch (_) { finish('worker_unavailable'); }
});
}
async function loadVerified(options, validate) {
var kind = options.kind;
if (kind === 'feed' && options.feedProfile !== undefined && !['v2','v3'].includes(options.feedProfile)) fail('invalid_feed_profile');
if (options.exactVersion && !/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.test(options.exactVersion)) fail('invalid_version');
var path = kind === 'release' ? 'musterout@' + (options.exactVersion || 'latest') + '/release.js' : 'musterout-feed@latest/' + (options.feedProfile === 'v3' ? 'v3/feed.js' : 'feed.js');
// Schema 3 uses only release-gated package mirrors. importScripts returns an
// object, not raw wrapper bytes; canonical payload signatures remain mandatory.
// Each CDN has its own worker, first-message limit and 20 s deadline.
// No board state or identifiers are sent to either worker.
var results = await Promise.allSettled(['https://unpkg.com/', 'https://cdn.jsdelivr.net/npm/'].map(async function (host) {
var value = await loadWorker(host + path, kind);
await verifyEnvelope(value.envelope, value.signature, kind === 'release' ? value.html : canonical(value.data), options);
if (options.exactVersion && value.envelope.version !== options.exactVersion) fail('wrong_version');
if (validate) validate(value);
return value;
}));
var best = null;
for (var result of results) {
if (result.status !== 'fulfilled') continue;
var value = result.value, e = value.envelope;
if (best && (kind === 'release' ? e.version === best.envelope.version : e.seq === best.envelope.seq) && (kind === 'release' ? canonical(e) !== canonical(best.envelope) : e.sha256 !== best.envelope.sha256 || e.size !== best.envelope.size || e.pack !== best.envelope.pack || e.created !== best.envelope.created || e.expires !== best.envelope.expires)) fail('mirror_conflict');
if (!best || (kind === 'release' ? compare(e.version, best.envelope.version) > 0 : e.seq > best.envelope.seq || e.seq === best.envelope.seq && stamp(e.created) > stamp(best.envelope.created))) best = value;
}
// A CDN that verified a release no newer than this board means the board is current.
if (!best) throw results.map(function (r) { return r.reason; }).find(function (r) { return r && r.code === 'not_newer'; }) || results[0].reason;
return best;
}
// Explicit owner-requested device backup. This helper performs reads only.
var BACKUP_COLLECTIONS=['items','loes','contacts','blocks','conditions','claim','links','inbox','coach','coach_facts','coach_checkins'];
function freshSnapshot(s){return s&&!s.metadata?.fromCache&&!s.metadata?.hasPendingWrites;}
async function collectRecords(db){
if(!db||typeof db.collection!=='function')fail('backup_unavailable');
var records=[],collections=BACKUP_COLLECTIONS;
for(var collection of collections){
var query=db.collection(collection),seen=new Set();
for(;;){var snap=await query.get();if(!freshSnapshot(snap)||!Array.isArray(snap.docs))fail('backup_unverified');
for(var doc of snap.docs){if(typeof doc.id!=='string'||!/^[A-Za-z0-9_.~:@+-]+$/.test(doc.id)||doc.id==='.'||doc.id==='..'||seen.has(doc.id)||!freshSnapshot(doc))fail('backup_unverified');seen.add(doc.id);var path=collection+'/'+doc.id;var value=doc.data();if(!value||typeof value!=='object'||Array.isArray(value))fail('backup_unverified');records.push({path:path,value:JSON.parse(JSON.stringify(value))});}
if(!snap.hasMore&&!snap.nextPage)break;
if(typeof snap.nextPage==='function')query={get:snap.nextPage};else if(typeof query.startAfter==='function'&&snap.docs.length)query=query.startAfter(snap.docs.at(-1));else fail('backup_incomplete');
}
}
for(var path of ['meta/profile','meta/settings','meta/ledger']){var snap=await db.doc(path).get();if(!freshSnapshot(snap))fail('backup_unverified');if(snap.exists)records.push({path:path,value:JSON.parse(JSON.stringify(snap.data()))});}
records.sort(function(a,b){return a.path.localeCompare(b.path);});return records;
}
function create(options) {
options = options || {};
var config = options.config || global.MusterOutUpdateConfig || {}, state, candidate = null, checkTask = null, applyTask = null, readyTask = null, listeners = new Set();
var db = options.db, correctionPending = false, justUpdated = null, pendingVersion = null, visitDismissed=new Set(), offerTimer=null;
if (typeof options.onState === 'function') listeners.add(options.onState);
function report(status, values) {
state = Object.freeze(Object.assign({status:status, correctionPending:correctionPending, justUpdated:justUpdated}, values || {}));
listeners.forEach(function (fn) { try { fn(state); } catch (_) {} });
return state;
}
report('idle');
function info() {
var e = candidate.envelope;
var key='mo.update.first.'+config.version+'.'+e.version,first;try{first=Number(localStorage.getItem(key));if(!Number.isFinite(first)||first<=0||first>Date.now()){first=Date.now();localStorage.setItem(key,String(first));}}catch(_){first=Date.now();}var overdue=Date.now()-first>=7*86400000;clearTimeout(offerTimer);if(!overdue)offerTimer=setTimeout(function(){if(candidate?.envelope.version===e.version&&['available','snoozed'].includes(state.status))report(visitDismissed.has(e.version)?'snoozed':'available',info());},Math.max(1,7*86400000-(Date.now()-first)));return {version:e.version, notes:Object.freeze(e.notes.slice()), correction:e.correction, critical:e.correction, impact:e.impact,overdue:overdue,visitDismissed:!e.correction&&visitDismissed.has(e.version),sheetDismissed:e.correction&&visitDismissed.has(e.version)};
}
function snoozed(version) {
var offer=candidate&&candidate.envelope.version===version?info():null;if(offer&&(offer.critical||offer.overdue))return visitDismissed.has(version);
try { var until = Number(localStorage.getItem('mo.update.snooze.' + version)); return Number.isFinite(until) && until > Date.now() && until <= Date.now() + 86400000; } catch (_) { return false; }
}
async function pinnedJournal() {
if (!db) return null;
var snap = await db.doc('meta/update').get(), j = snap.exists ? snap.data() : null;
if (!j || Object.prototype.hasOwnProperty.call(j,'stage') || !j.state) return null;
if (!j.target) { if (j.trust_schema !== undefined) fail('journal_changed'); return null; }
if (j.trust_schema !== 1 || !j.target || j.target.package !== 'musterout' || j.target.version !== j.to || j.target.pack !== config.pack || canonical(j.target.mirrors) !== canonical(['https://cdn.jsdelivr.net/npm/musterout@','https://unpkg.com/musterout@'])) fail('journal_changed');
if (!['publishing','failed','complete'].includes(j.state) || compare(j.to,j.from) <= 0) fail('journal_changed');
stamp(j.at);
exact(j.target, ['package','version','pack','mirrors','release']);
exact(j.target.release, ['envelope','signature']);
var e = j.target.release.envelope;
if (e.version !== j.to || e.pack !== config.pack) fail('journal_changed');
await verifySignedEnvelope(e, j.target.release.signature, Object.assign({}, config, {kind:'release'}));
return j;
}
async function resumePinned() {
var raw = db ? await db.doc('meta/update').get() : null, legacy = raw && raw.exists ? raw.data() : null;
if (legacy && !Object.prototype.hasOwnProperty.call(legacy,'stage') && legacy.state && legacy.state !== 'complete') {pendingVersion=legacy.to; if (!legacy.target && legacy.to !== config.version) fail('legacy_pending');}
var j = await pinnedJournal();
if (!j || j.state === 'complete' || j.to === config.version) return false;
if (j.from !== config.version || compare(j.to, config.version) <= 0) fail('journal_changed');
var value = await loadVerified(Object.assign({}, config, {kind:'release', currentVersion:config.version, exactVersion:j.to}));
if (canonical(value.envelope) !== canonical(j.target.release.envelope) || value.signature !== j.target.release.signature) fail('journal_changed');
candidate = value;
report('available', info());
return true;
}
function checkForUpdate() {
if (applyTask || state.status === 'applying') return Promise.resolve(state);
if (checkTask) return checkTask;
report('checking');
checkTask = (async function () {
try {
if (await resumePinned()) return state;
var value = await loadVerified(Object.assign({}, config, {kind:'release', currentVersion:config.version}));
if (!candidate || compare(value.envelope.version, candidate.envelope.version) > 0) candidate = value;
correctionPending = candidate.envelope.correction;
return report(snoozed(candidate.envelope.version) ? 'snoozed' : 'available', info());
} catch (error) {
if (pendingVersion) return failed(error);
// A failed network check never hides an already verified correction.
if (candidate) return report(snoozed(candidate.envelope.version) ? 'snoozed' : 'available', info());
return error && error.code === 'not_newer' ? report('idle', {upToDate:true}) : report('idle', {quietCode:error.code || 'check_failed'});
} finally { checkTask = null; }
})();
return checkTask;
}
function snooze() {
if (!candidate || state.status === 'applying' || applyTask) return state;
var offer=info();if(offer.critical||offer.overdue)visitDismissed.add(candidate.envelope.version);else try { localStorage.setItem('mo.update.snooze.' + candidate.envelope.version, String(Date.now() + 86400000)); } catch (_) {}
return report('snoozed', info());
}
async function capability(name) {
if (Object.prototype.hasOwnProperty.call(options, name)) return options[name];
return global.claude && global.claude.use ? await global.claude.use(name) : null;
}
async function requireWriter() {
var user = await capability('user');
if (!user) fail('not_granted');
var allowed = await user.can('files.write');
if (allowed === null) allowed = await user.canEdit();
if (allowed !== true) fail('not_writer');
}
function hooks() {
if (!db || ['drainPendingWrites','persistDrafts','runMigration','verifyMigration'].some(function (key) { return typeof options[key] !== 'function'; })) fail('hooks_missing');
}
function failed(error) {
var code = error.code || 'update_failed';
var readOnly = ['not_writer','not_granted','not_declared','capability_disabled','capability_removed'].includes(code);
return report('failed', {code:code, message:pendingVersion ? 'I could not verify the release you already approved. Your update is still pending, and your saved plan is kept. I will not switch versions without your approval.' : readOnly ? 'This view is read-only. Open your board as an editor to update.' : code === 'conflict' ? 'Another page update won. Reopen your board before updating.' : code === 'too_large' ? 'This update is too large. Use the pasted update message.' : 'The update did not finish. Your saved plan is still available.'});
}
function applyUpdate() {
if (applyTask) return applyTask;
if (!candidate || state.status === 'applying') return Promise.resolve(state);
var target = candidate, journal = null;
report('applying', {phase:'preparing'});
applyTask = (async function () {
try {
await requireWriter(); hooks();
var artifact = await capability('artifact');
if (!artifact || typeof artifact.publish !== 'function') fail('not_granted');
var installedBefore = await db.doc('meta/install').get();
if (installedBefore.exists && installedBefore.data().version && compare(installedBefore.data().version, target.envelope.version) >= 0) fail('not_newer');
await options.drainPendingWrites();
await options.persistDrafts();
var existing = await db.doc('meta/update').get(), prior = existing.exists ? existing.data() : null;
if (prior && prior.state !== 'complete' && (prior.stage || !prior.target || prior.from !== config.version || prior.to !== target.envelope.version || canonical(prior.target.release.envelope) !== canonical(target.envelope))) fail('journal_changed');
journal = {from:config.version, to:target.envelope.version, at:prior && prior.to === target.envelope.version ? prior.at : new Date().toISOString(), state:'publishing', trust_schema:1,
target:{package:'musterout', version:target.envelope.version, pack:target.envelope.pack, mirrors:['https://cdn.jsdelivr.net/npm/musterout@','https://unpkg.com/musterout@'], release:{envelope:target.envelope,signature:target.signature}}};
await db.doc('meta/update').set(journal);
var saved = await db.doc('meta/update').get();
if (!saved.exists || canonical(saved.data()) !== canonical(journal)) fail('journal_changed');
var latestInstall = await db.doc('meta/install').get();
if (latestInstall.exists && latestInstall.data().version && compare(latestInstall.data().version,target.envelope.version) >= 0) fail('not_newer');
report('applying', {phase:'publishing'});
for (var attempt = 0; attempt < 2; attempt++) {
try { await artifact.publish(target.html); break; }
catch (error) {
if (attempt || error.code !== 'upstream_error') throw error;
await new Promise(function (resolve) { setTimeout(resolve, 1000 + Math.floor(Math.random() * 2001)); });
}
}
return state; // The runtime reloads. No install claim in the old page.
} catch (error) {
if (journal && error.code !== 'conflict') {
try { await db.doc('meta/update').set(Object.assign({}, journal, {state:'failed', code:error.code || 'update_failed'})); } catch (_) {}
}
return failed(error);
} finally { applyTask = null; }
})();
return applyTask;
}
async function finishInstall() {
if (!db) return false;
var snap = await db.doc('meta/update').get(), journal = snap.exists ? snap.data() : null;
// Chat owns stage journals. A page journal can lag behind the running release.
if (journal && Object.prototype.hasOwnProperty.call(journal,'stage')) return false;
var pending = journal && ['publishing','failed'].includes(journal.state);
if (journal && journal.state !== 'complete' && !pending) return false;
if (pending && (journal.state === 'failed' && !journal.target || compare(journal.to, config.version) > 0)) return false;
// MTN-133, TRS 21:10: only a pending page journal owns install bookkeeping.
// Browser writes have no version precondition; quiet repair cannot be fenced.
if (!pending) return false;
try {
if (pending && (journal.target || journal.trust_schema !== undefined)) { if (!await pinnedJournal()) fail('journal_changed'); }
hooks();
await requireWriter();
if (pending) {
report('applying', {phase:'migrating', version:config.version});
var backoff = 1000;
for (;;) {
try { await options.runMigration(); break; }
catch (error) {
if (!error || error.code !== 'busy') throw error;
// A surviving webview may renew its lease. Keep waiting, with a capped
// interval, rather than declaring a valid, pinned update failed.
report('applying', {phase:'finishing', version:config.version});
var delay = Math.min(45000, Math.max(backoff, Number(error.retryAfterMs) || 0));
await new Promise(function (resolve) { setTimeout(resolve, delay); });
backoff = Math.min(45000, backoff * 2);
await requireWriter();
var waiting = await db.doc('meta/update').get(), latest = waiting.exists ? waiting.data() : null;
if (canonical(latest) === canonical(Object.assign({}, journal, {state:'complete'}))) {
// Another finisher committed this exact approved update while we waited.
var doneInstall = await db.doc('meta/install').get();
if (!doneInstall.exists || doneInstall.data().version !== config.version || await options.verifyMigration() !== true) fail('install_unverified');
justUpdated = {from:journal.from, to:config.version}; correctionPending = false;
report('done'); return true;
}
if (canonical(latest) !== canonical(journal)) fail('journal_changed');
}
}
report('applying', {phase:'verifying'});
if (await options.verifyMigration() !== true) fail('migration_unverified');
}
var freshJournal = await db.doc('meta/update').get();
if (canonical(freshJournal.exists ? freshJournal.data() : null) !== canonical(journal)) fail('journal_changed');
var installRef = db.doc('meta/install'), installed = await installRef.get();
if (installed.exists && installed.data().version && compare(installed.data().version,config.version) > 0) fail('not_newer');
if (installed.exists) await installRef.update({version:config.version});
else await installRef.set({version:config.version});
installed = await installRef.get();
if (!installed.exists || installed.data().version !== config.version) fail('install_unverified');
if (!pending) return false;
var updateRef = db.doc('meta/update');
var current = await updateRef.get();
if (!current.exists || Object.prototype.hasOwnProperty.call(current.data(),'stage') || canonical(current.data().target || null) !== canonical(journal.target || null) || current.data().trust_schema !== journal.trust_schema || current.data().to !== journal.to || current.data().at !== journal.at || current.data().state !== journal.state) fail('journal_changed');
await updateRef.set(Object.assign({}, journal, {state:'complete'}));
var completed = await updateRef.get();
if (!completed.exists || completed.data().state !== 'complete' || canonical(completed.data()) !== canonical(Object.assign({}, journal, {state:'complete'}))) fail('install_unverified');
justUpdated = {from:journal.from, to:config.version}; correctionPending = false;
report('done'); return true;
} catch (error) { if (!pending) return false; failed(error); return true; }
}
function ready() {
if (!readyTask) readyTask = (async function () {
try { if (await finishInstall()) return state; if (await resumePinned()) return state; } catch (error) { return failed(error); }
return checkForUpdate();
})();
return readyTask;
}
return Object.freeze({get state() { return state; }, ready:ready, checkForUpdate:checkForUpdate, applyUpdate:applyUpdate, snooze:snooze,
subscribe:function (fn) { listeners.add(fn); try { fn(state); } catch (_) {} return function () { listeners.delete(fn); }; }});
}
global.MusterOutUpdate = Object.freeze({create:create, verifyEnvelope:verifyEnvelope, canonical:canonical, compareVersions:compare,
collectRecords:collectRecords,
loadFeed:function (options, validate) { return loadVerified(Object.assign({}, options, {kind:'feed'}), validate); }});
})(window);
