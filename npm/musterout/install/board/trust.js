/* Audience: mil-public. Reader: Marines using Muster Out. Effect: inspect saves, coverage, and approved report bytes. */
(function () {
'use strict';
const COUNTERS = Object.freeze(['opens','tab_today','tab_plan','tab_dates','tab_claim','items_done','drawers_opened','update_taps','errors_save','errors_update','errors_feed','errors_storage','errors_sample','errors_other']);
const COUNTER_MEANINGS = Object.freeze({opens:'Board opens',tab_today:'Today tab opens',tab_plan:'Plan tab opens',tab_dates:'Dates tab opens',tab_claim:'Claim tab opens',items_done:'Items marked done',drawers_opened:'Item drawers opened',update_taps:'Update now taps',errors_save:'Save errors',errors_update:'Update errors',errors_feed:'Watch feed errors',errors_storage:'Draft storage errors',errors_sample:'Claude errors',errors_other:'Other errors'});
const SCHEMA = 1;
const SCHEMA_KEY = 'v1:' + JSON.stringify(COUNTER_MEANINGS);
const SCREENS = ['today','plan','dates','claim','more','setup'];
const PATHS = ['resign','retire','eas','unsure'];
const GRADES = ['o5','o14','cwo45','wo13','e89','e67','e15','unsure'];
const PATH_LABELS = {resign:'Resigning',retire:'Retiring',eas:'Separating',unsure:'Not sure'};
const GRADE_LABELS = {o5:'O-5 and above',o14:'O-1 to O-4',cwo45:'CWO4 to CWO5',wo13:'WO to CWO3',e89:'E-8 to E-9',e67:'E-6/E-7',e15:'E-1 to E-5',unsure:'Not sure'};
const ERROR_CLASSES = ['none','save','update','feed','storage','sample','unavailable','other'];
const MESSAGES = Object.freeze({
'db.unavailable':'Save failed. Your changes are kept on this device.',
'db.resource_exhausted':'Saving paused. Try again later when fewer changes are pending.',
'db.quota_exceeded':'Board storage is full. Your changes have not saved.',
'db.invalid_argument':'This change could not be saved.',
'db.transform_error':'This change could not be saved.',
'TypeError':'This change could not be saved.',
'read-only':'This view is read-only. You can view saved work.',
'db.absent':'Saving is unavailable in this view.',
'db.refresh':'Saved data could not refresh.',
'PLAN_PRO_REQUIRED':'This account cannot save this board. Check that you are signed in to the account that owns it.',
'artifact.not_writer':'This view cannot publish updates.',
'artifact.not_granted':'This view cannot publish updates.',
'artifact.consent_required':'This view cannot publish updates.',
'artifact.absent':'Updates are unavailable in this view.',
'artifact.conflict':'Another version is opening. Your draft is kept.',
'artifact.upstream_error':'The update did not finish. Your draft is kept.',
'artifact.rate_limited':'Updates are paused. Try again later when this board has finished publishing.',
'artifact.too_large':'This update is too large to publish.',
'artifact.invalid_content':'This update cannot be published here.',
'artifact.transform_error':'This update cannot be published here.',
'artifact.read_only_path':'This update cannot be published here.',
'UPDATE_UNTRUSTED':'This update could not be verified. Keep using your current board.',
'UPDATE_VERIFY_FAILED':'The update opened, but verification is incomplete.',
'SNOOZE_SAVE_FAILED':'This reminder could not be saved. It may appear again.',
'DRAFT_STORAGE_FAILED':'Your draft could not be kept on this device. Copy changes before continuing.',
'WATCH_FAILED':'Last attempt failed. Showing the last good check.',
'FEED_UNTRUSTED':'The new watch feed could not be verified. Showing the last good check.',
'FEED_STALE':'Watch results are over 8 days old.',
'FEED_GAP':"Some notices fall outside this feed's 30-day window.",
'sample.absent':'Claude is unavailable in this view. Continue with the fields.',
'sample.tools_unavailable':'Claude cannot use page tools here. Continue with the fields.',
'sample.rate_limited':'Claude usage is limited right now. Continue with the fields.',
'sample.session_expired':'Sign in to Claude again to ask. Copy your draft first.',
'sample.refused':'Claude could not rewrite these details. Edit the details in the field above.',
'sample.invalid_json':'Claude did not return usable wording.',
'sample.invalid_request':'Claude could not process this request. Continue with the fields.',
'sample.upstream_error':"Claude's response was interrupted. Continue with the fields.",
'permissions.denied':'Claude is off for this board. Open permissions.',
'permissions.absent':"Permissions are unavailable here. Use the artifact's Permissions menu.",
'permissions.manage.unavailable':"Open the artifact's Permissions menu to change access.",
'REPORT_QUEUE_FAILED':'Report not saved. Try Continue to report page again.',
'REPORT_TRANSPORT_UNAVAILABLE':'Report not sent.',
'REPORT_VALIDATION_FAILED':'Review the highlighted fields before continuing.',
'CONSENT_SCHEMA_CHANGED':'Counts paused. Review the new schema to allow sending.',
'CONSENT_OFF_FAILED':'Counts paused on this device. Off could not be saved for other devices.',
'REPORT_DELETE_FAILED':'Deletion is not confirmed. Keep this receipt and try again.',
'CLIPBOARD_UNAVAILABLE':'Copy did not finish. On your phone, press and hold the text below to copy it.'
});
const ABSENT = ['revoked','not_granted','not_declared','sampling_disabled','capability_disabled','capability_removed'];
function message(code, component) {
code = String(code || 'unavailable');
const full = code.includes('.') || /^[A-Z]/.test(code) ? code : component + '.' + code;
if (MESSAGES[full]) return MESSAGES[full];
if (['UPDATE_TIMEOUT','UPDATE_OVERSIZE','UPDATE_FLOOD'].includes(full)) return MESSAGES.UPDATE_UNTRUSTED;
if (full === 'REPORT_SEND_FAILED') return MESSAGES.REPORT_TRANSPORT_UNAVAILABLE;
if (full === 'permissions.manage.upstream_error') return MESSAGES['permissions.manage.unavailable'];
if (ABSENT.some(c => full === component + '.' + c)) return MESSAGES[component + '.absent'] || MESSAGES['db.absent'];
if (['empty_completion'].some(c => full === 'sample.' + c)) return MESSAGES['sample.invalid_json'];
if (['prompt_too_large','transform_error','queue_overflow'].some(c => full === 'sample.' + c)) return MESSAGES['sample.invalid_request'];
return MESSAGES[component + '.upstream_error'] || MESSAGES['db.unavailable'];
}
const KNOWN_CODES = new Set(Object.keys(MESSAGES).flatMap(k => [k,k.split('.').pop()]).concat(ABSENT,['UPDATE_TIMEOUT','UPDATE_OVERSIZE','UPDATE_FLOOD','REPORT_SEND_FAILED','permissions.manage.upstream_error','empty_completion','prompt_too_large','queue_overflow','cancelled','NotAllowedError']));
function node(tag, text, cls) { const e = document.createElement(tag); if (text !== undefined) e.textContent = String(text); if (cls) e.className = cls; return e; }
function button(text, fn, primary) { const e = node('button', text, 'mot-button' + (primary ? ' mot-primary' : '') + (['View diagnostic','Report a problem'].includes(text) ? ' mot-tertiary' : '')); e.type = 'button'; e.addEventListener('click', fn); return e; }
function icon(kind) {
const disc = node('span',undefined,'c6-icon-disc'), ns = 'http://www.w3.org/2000/svg', svg = document.createElementNS(ns,'svg');
svg.setAttribute('viewBox','0 0 24 24'); svg.setAttribute('aria-hidden','true');
const shapes = kind === 'help' ? [['circle',{cx:'12',cy:'12',r:'9'}],['path',{d:'M9.1 9a3 3 0 0 1 5.8 1c0 2-3 2-3 4m.1 3h.01'}]] : [['path',{d:'m6 6 12 12M6 18 18 6'}]];
shapes.forEach(([tag,attrs]) => { const shape = document.createElementNS(ns,tag); Object.entries(attrs).forEach(([key,value]) => shape.setAttribute(key,value)); svg.append(shape); }); disc.append(svg); return disc;
}
function paragraph(parent, text, cls) { const e = node('p', text, cls); parent.append(e); return e; }
function jsonBox(parent, bytes) { const e = node('pre', bytes, 'mot-json'); e.tabIndex = 0; e.setAttribute('aria-label','Exact payload'); parent.append(e); return e; }
function cleanText(v) { return String(v || '').replace(/[\u0000-\u001f\u007f-\u009f]/g,' ').trim(); }
function hex() { const b = new Uint8Array(16); crypto.getRandomValues(b); return Array.from(b,n => n.toString(16).padStart(2,'0')).join(''); }
function weekAt(now) { const d = new Date(now); d.setUTCHours(0,0,0,0); d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7)); const y = d.getUTCFullYear(); return y + '-W' + String(Math.ceil((((d - Date.UTC(y,0,1))/86400000)+1)/7)).padStart(2,'0'); }
function utc(value) {
const d = new Date(value); if (!value || !Number.isFinite(d.getTime())) return 'Not recorded';
return String(d.getUTCDate()).padStart(2,'0') + ' ' + ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][d.getUTCMonth()] + ' ' + d.getUTCFullYear() + ' ' + String(d.getUTCHours()).padStart(2,'0') + String(d.getUTCMinutes()).padStart(2,'0') + ' UTC';
}
function milDate(value) { if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return 'Not recorded'; const date = new Date(value+'T00:00:00Z'); if (!Number.isFinite(date.getTime()) || date.toISOString().slice(0,10) !== value) return 'Not recorded'; return utc(value+'T00:00:00Z').replace(' 0000 UTC',''); }
function validVersion(value) { return typeof value === 'string' && value.length <= 64 && /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$/.test(value); }
function canonical(value) { if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']'; if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(key => JSON.stringify(key)+':'+canonical(value[key])).join(',') + '}'; return JSON.stringify(value); }
function definite(snap) { return !!snap && !!snap.metadata && snap.metadata.fromCache === false && snap.metadata.hasPendingWrites === false; }
function validDraftId(id) { return typeof id === 'string' && id.length <= 128 && /^[A-Za-z0-9][A-Za-z0-9._-]*(?::[A-Za-z0-9][A-Za-z0-9._-]*)*$/.test(id); }
function createDraftOwner(owner,options) {
if (!['report','ask'].includes(owner)) throw new TypeError('Invalid draft owner');
const opts = options || {}, storageKey = 'mo.drafts.' + owner + '.' + (opts.scope === undefined ? location.pathname : String(opts.scope));
let fields = Object.create(null); const bindings = new Set();
function failure(operation) { opts.onError?.({component:'draft',operation,code:'DRAFT_STORAGE_FAILED'}); return false; }
function check(id) { if (!validDraftId(id)) throw new TypeError('Invalid draft id'); }
function valueOK(value) { return typeof value === 'string' || typeof value === 'boolean'; }
try {
const saved = JSON.parse(localStorage.getItem(storageKey) || 'null');
if (saved?.schema_version === 1 && saved.owner === owner && saved.fields && typeof saved.fields === 'object') {
for (const [id,value] of Object.entries(saved.fields)) if (validDraftId(id) && valueOK(value)) fields[id] = value;
}
} catch (_) { failure('get'); }
function persist() { try { localStorage.setItem(storageKey,JSON.stringify({schema_version:1,owner,fields})); return true; } catch (_) { return failure('set'); } }
function read(id) { check(id); return fields[id]; }
function write(id,value) { check(id); if (!valueOK(value)) throw new TypeError('Invalid draft value'); fields[id] = value; return persist(); }
function remove(id) { check(id); delete fields[id]; return persist(); }
function clear() { fields = Object.create(null); try { localStorage.removeItem(storageKey); return true; } catch (_) { return failure('delete'); } }
function bind(element,id,options) {
check(id); if (!element?.matches('input,textarea,select')) throw new TypeError('Invalid draft editor');
const binding = options || {}, checkbox = element.type === 'checkbox';
element.dataset.draftOwner = owner; element.dataset.draftId = id;
if (binding.restore !== false && fields[id] !== undefined) { if (checkbox) element.checked = fields[id] === true; else element.value = String(fields[id]); }
function capture(event) {
event.stopPropagation(); const value = checkbox ? element.checked : element.value;
write(id,value); binding.onChange?.(value);
}
element.addEventListener('input',capture); element.addEventListener('change',capture);
const release = () => { element.removeEventListener('input',capture); element.removeEventListener('change',capture); bindings.delete(release); };
bindings.add(release); return release;
}
function destroy() { [...bindings].forEach(release => release()); }
return Object.freeze({owner,storageKey,read,write,remove,clear,bind,destroy});
}
function create(options) {
const o = Object.assign({version:'unknown',pack:'unknown',screen:'today',db:null,sample:null,updates:null,learningEnabled:false,canWrite:null,now:Date.now},options || {});
let watchCode = null, dead = false, update = {status:'idle'}, feed = null, save = {status:o.db ? (o.canWrite === false ? 'read-only' : 'unsaved') : 'unavailable'}, saveAttempt = 0, saveRevision = 0, timer = null;
let snoozePrefs = {}, snoozesReady = !o.db, pendingUpdate = null;
let lastConfirmed = null, releaseInfo = {}, updateSheet = null, forced = new Set(), ring = [], sheets = [], writer = hex(), counters = Object.fromEntries(COUNTERS.map(k => [k,0])), counterWeek = weekAt(o.now());
let consent = null, offRequested = false, localPaused = true, consentReady = false, usageChain = Promise.resolve(), unsubscribe = null, consentUnsubscribe = null;
let receipts = [], outbox = [], controls = [], settingsError = '';
const reportDrafts = createDraftOwner('report',{scope:o.draftScope,onError:e => recordError(e.component,e.operation,e.code)});
const slots = {header:[],save:[],today:[],settings:[]};
const emit = type => document.dispatchEvent(new CustomEvent('musterout:trust',{detail:{type}}));
function recordError(component,operation,code) {
const c = ['db','artifact','sample','permissions','update','feed','report','usage','clipboard','draft','ui'].includes(component) ? component : 'ui';
const op = ['set','get','delete','onSnapshot','publish','verify','snooze','rewrite','queue','consent','count','copy','render','refresh','apply','unknown'].includes(operation) ? operation : 'unknown';
ring.push(Object.freeze({component:c,operation:op,code:KNOWN_CODES.has(code) ? code : 'other'})); if (ring.length > 50) ring.shift();
if(typeof o.onErrorCount==='function')o.onErrorCount(c);
}
function diagnostic() {
return {version:/^[0-9A-Za-z.+-]{1,64}$/.test(o.version) ? o.version : 'unknown',pack:/^usmc-20\d{2}\.\d{2}$/.test(o.pack) ? o.pack : 'unknown',screen:SCREENS.includes(o.screen) ? o.screen : 'more',capabilities:{db:o.db ? 'available':'unavailable',sample:typeof o.sample === 'function' ? 'available':'unavailable',updates:o.updates ? 'available':'unavailable',data_write:o.canWrite === false ? 'denied':o.canWrite === true ? 'granted':'unknown'},errors:ring.map(e => ({...e}))};
}
function notice(parent,text) { const e = node('p',text,'mot-notice'); e.setAttribute('role','status'); e.setAttribute('aria-live','polite'); parent.append(e); return e; }
function actionRow(parent) { const e = node('div',undefined,'mot-actions'); parent.append(e); return e; }
function help() { openText('Get help','Open SUPPORT in Claude. Copy the diagnostic before continuing.'); }
function lockBackground(sheet) {
const changed = [];
for (const el of document.body.children) { if (el !== sheet.overlay && !el.inert) { changed.push({el,ariaHidden:el.getAttribute('aria-hidden')}); el.inert = true; el.setAttribute('aria-hidden','true'); } }
sheet.locked = changed;
}
function closeSheet(sheet, force) {
if (!sheet || !sheets.includes(sheet) || (!force && !sheet.cancel)) return;
if (sheets[sheets.length-1] !== sheet) return;
sheet.navObserver?.disconnect(); sheet.abort?.abort(); sheet.draftBindings?.forEach(release => release()); sheet.overlay.remove(); sheets.pop(); sheet.locked.forEach(({el,ariaHidden}) => { el.inert = false; if (ariaHidden === null) el.removeAttribute('aria-hidden'); else el.setAttribute('aria-hidden',ariaHidden); });
if (sheet === updateSheet) updateSheet = null;
document.body.style.overflow = sheets.length ? 'hidden' : sheet.oldOverflow;
if (sheet.opener?.isConnected && !sheet.opener.closest('[inert]')) sheet.opener.focus({preventScroll:true});
else if (sheets.length) sheets[sheets.length-1].heading.focus({preventScroll:true});
else { const replacement = sheet.returnContainer?.isConnected && Array.from(sheet.returnContainer.querySelectorAll('button,[tabindex="0"]')).find(el => !el.disabled && !el.closest('[inert]')); if (replacement) replacement.focus({preventScroll:true}); }
}
function sheet(title,cancel) {
const s = {opener:document.activeElement,cancel,oldOverflow:document.body.style.overflow};
s.returnContainer = [...slots.header,...slots.save,...slots.today,...slots.settings].find(el => el.contains(s.opener)) || s.opener?.parentElement;
s.overlay = node('div',undefined,'mot-overlay'); s.overlay.style.zIndex = String(100 + sheets.length * 2);
s.dialog = node('section',undefined,'mot-sheet'); s.dialog.setAttribute('role','dialog'); s.dialog.setAttribute('aria-modal','true');
s.heading = node('h2',title); s.heading.id = 'mot-heading-' + hex(); s.heading.tabIndex = -1; s.dialog.setAttribute('aria-labelledby',s.heading.id);
const header = node('header',undefined,'mot-sheet-header'); header.append(s.heading);
const dismiss = () => { if (s === updateSheet && ['available','snoozed'].includes(update.status)) { void snooze(true); closeSheet(s,true); return; } const result = s.cancel?.(); if (result?.then) return result.finally(() => closeSheet(s,true)); closeSheet(s,true); };
s.close = button('Close',dismiss); s.close.classList.add('mot-close'); s.close.setAttribute('aria-label','Close sheet'); s.close.replaceChildren(icon('close')); s.close.hidden = false; header.append(s.close);
s.notice = notice(header,'');
s.body = node('div',undefined,'mot-sheet-body'); s.actions = node('div',undefined,'mot-sheet-actions');
let moved = false;
const grabber = button('',e => { if (e.detail === 0 || !moved) dismiss(); }); grabber.className = 'mot-drag-handle'; grabber.setAttribute('aria-label','Dismiss sheet');
const pill = node('span',undefined,'c6-grabber'); pill.setAttribute('aria-hidden','true'); grabber.append(pill);
let drag = null;
grabber.addEventListener('pointerdown',e => { if (!e.isPrimary || e.button !== 0) return; moved = false; drag = {id:e.pointerId,x:e.clientX,y:e.clientY}; grabber.setPointerCapture(e.pointerId); });
grabber.addEventListener('pointermove',e => { if (drag && drag.id === e.pointerId && Math.hypot(e.clientX-drag.x,e.clientY-drag.y)>8) moved = true; });
grabber.addEventListener('pointerup',e => { if (!drag || drag.id !== e.pointerId) return; const start = drag; drag = null; if (e.clientY-start.y >= 48 && e.clientY-start.y > Math.abs(e.clientX-start.x)) dismiss(); });
grabber.addEventListener('pointercancel',() => { drag = null; });
const scroll = node('div',undefined,'mot-sheet-scroll'); scroll.append(s.body,s.actions);
if (title !== 'Report a problem' && title !== 'Review report') { const report = button('Report a problem',openReport); report.classList.add('mot-sheet-report','mot-tertiary'); scroll.append(report); }
const footer = node('footer',undefined,'mot-sheet-footer');if (title === 'Report a problem' || title === 'Review report') footer.append(s.actions);else footer.append(button('Done',dismiss));
s.dialog.append(grabber,header,scroll,footer); s.overlay.append(s.dialog); document.body.append(s.overlay);
const nav = document.querySelector('#tabs');
if (nav) { const measure = () => s.overlay.style.setProperty('--mot-nav-space',Math.ceil(Math.max(72,nav.getBoundingClientRect().height))+'px'); measure(); s.navObserver = new ResizeObserver(measure); s.navObserver.observe(nav); }
sheets.push(s); lockBackground(s); document.body.style.overflow = 'hidden';
s.overlay.addEventListener('click', e => { if (e.target === s.overlay) dismiss(); });
s.overlay.addEventListener('keydown', e => {
if (sheets[sheets.length-1] !== s) return;
if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); dismiss(); }
if (e.key !== 'Tab') return;
const focusables = Array.from(s.dialog.querySelectorAll('button:not([disabled]),input:not([disabled]),textarea:not([disabled]),select:not([disabled]),summary,a[href],[tabindex="0"]')).filter(el => !el.hidden && !el.closest('[hidden]') && el.getClientRects().length);
const first = focusables[0], last = focusables[focusables.length-1];
if (!first) { e.preventDefault(); s.heading.focus({preventScroll:true}); }
else if (e.shiftKey && (document.activeElement === first || document.activeElement === s.heading)) { e.preventDefault(); last.focus(); }
else if (!e.shiftKey && (document.activeElement === last || !s.dialog.contains(document.activeElement))) { e.preventDefault(); first.focus(); }
});
s.heading.focus({preventScroll:true}); return s;
}
function openText(title,text) { let s; s = sheet(title,() => closeSheet(s)); paragraph(s.body,text);  }
async function clipboard(bytes,status,preview) {
try { if (!navigator.clipboard?.writeText) throw {code:'CLIPBOARD_UNAVAILABLE'}; await navigator.clipboard.writeText(bytes); status.textContent = 'Copied.'; return true; }
catch (e) { recordError('clipboard','copy',e.code || e.name || 'CLIPBOARD_UNAVAILABLE'); status.textContent = MESSAGES.CLIPBOARD_UNAVAILABLE; preview?.focus(); if (preview) { const r = document.createRange(); r.selectNodeContents(preview); const sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r); } return false; }
}
function openCopy(title,bytes,success) {
let s; s = sheet(title,() => closeSheet(s)); paragraph(s.body,title === 'View diagnostic' ? 'Exact diagnostic':'Exact payload'); const preview = jsonBox(s.body,bytes); const status = s.notice; status.textContent = '';
if (title === 'View diagnostic' && !ring.length) paragraph(s.body,'No errors recorded in this view.');
s.actions.append(button('Copy',async () => { if (await clipboard(bytes,status,preview)) { status.textContent = success || 'Copied.'; if (title === 'View diagnostic') emit('diagnostic-copied'); } }));
}
function openDiagnostic() { openCopy('View diagnostic',JSON.stringify(diagnostic(),null,2),'Diagnostic copied.'); }
function copyMessage(kind) { const value = o[kind + 'Message']; if (typeof value === 'string' && value) openCopy('Copy ' + kind + ' message',value); else openText('Copy ' + kind + ' message','Open ' + kind.toUpperCase() + ' in Claude for the current message.'); }
function copyChanges() { if (typeof o.copyChanges === 'function') { try { const data = o.copyChanges(); if (typeof data === 'string') openCopy('Copy changes',data); } catch (e) { recordError('draft','copy',e.code || e.name); openDiagnostic(); } } else openText('Copy changes','Select your changes in the editor and copy them before continuing.'); }
function mountHeader(el) { if (!el) return; slots.header.push(el); const report = button('Report a problem',openReport); if (el.id === 'trustHeader') { report.setAttribute('aria-label','Report a problem'); report.replaceChildren(icon('help')); } el.append(report); }
function redraw(list,fn) { list.filter(el => el.isConnected).forEach(fn); }
function renderSave(el) {
let live = el.querySelector('.mot-save-live'); if (!live) { el.classList.add('mot-root'); live = node('div',undefined,'mot-save-live'); live.setAttribute('role','status'); live.setAttribute('aria-live','polite'); live.setAttribute('aria-atomic','true'); el.append(live); }
const codes = save.code || 'unavailable';
let text = {unsaved:'Unsaved changes.',saving:'Saving...',saved:'Saved.','read-only':MESSAGES['read-only'],unavailable:MESSAGES['db.absent']}[save.status];
if (save.status === 'failed') text = save.operation === 'onSnapshot' ? MESSAGES['db.refresh'] : message(codes,'db');
if (save.status === 'failed' && codes === 'DRAFT_STORAGE_FAILED') text = MESSAGES.DRAFT_STORAGE_FAILED;
if (live.textContent !== text) live.textContent = text;
let actions = el.querySelector('.mot-save-actions'); if (actions?.contains(document.activeElement)) { actions.addEventListener('focusout',() => { if (!actions.contains(document.activeElement)) renderSave(el); },{once:true}); return; } if (actions) actions.remove();
if (!['failed','unavailable'].includes(save.status)) return;
actions = node('div',undefined,'mot-actions mot-save-actions'); el.append(actions);
if (save.status === 'unavailable' || ABSENT.includes(codes.replace(/^db\./,''))) { paragraph(el.querySelector('.mot-save-live'),'Last loaded copy.'); actions.append(button('Open your board in Claude',() => openText('Open your board in Claude','Open your saved board from your Claude conversation.'))); }
const c = codes.replace(/^db\./,'');
if (codes === 'PLAN_PRO_REQUIRED') { actions.append(button('View demo',() => { if (typeof o.viewDemo === 'function') o.viewDemo(); else openText('View demo','Open the demo from setup.'); }),button('Copy setup message',() => copyMessage('setup'))); return; }
if (codes === 'db.refresh' || save.operation === 'onSnapshot') { actions.append(button('Reload once',() => { if (typeof o.reload === 'function') o.reload(); else openText('Reload once','Reload your board in Claude once to restore saved data. Copy changes first.'); }),button('View diagnostic',openDiagnostic)); return; }
if ((c === 'unavailable' || !KNOWN_CODES.has(codes)) && save.status === 'failed' && typeof save.retry === 'function' && saveAttempt < 1) actions.append(button('Retry',retrySave));
if (save.status === 'failed' && !['invalid_argument','transform_error','TypeError',...ABSENT].includes(c)) actions.append(button('Copy changes',copyChanges));
if (c === 'quota_exceeded') actions.append(button('Get help',help));
actions.append(button('View diagnostic',openDiagnostic));
}
async function retrySave() {
if (dead || saveAttempt >= 1 || typeof save.retry !== 'function') return;
clearTimeout(timer); const retry = save.retry, revision = saveRevision; saveAttempt++; save = {...save,status:'saving'}; redraw(slots.save,renderSave);
try { await retry(); if (!dead && revision === saveRevision) { save = {status:'saved'}; redraw(slots.save,renderSave); emit('save'); } }
catch (e) { if (!dead && revision === saveRevision) { save = {status:'failed',code:e.code || e.name || 'unavailable',retry}; recordError('db','set',save.code); redraw(slots.save,renderSave); emit('save'); } }
}
function setSave(value) {
clearTimeout(timer); saveRevision++; save = {...value}; if (['unsaved','saved'].includes(save.status)) saveAttempt = 0;
if (save.code) recordError('db','set',save.code);
redraw(slots.save,renderSave); emit('save');
if (saveAttempt < 1 && save.status === 'failed' && !save.operation && (save.code === 'unavailable' || save.code === 'db.unavailable' || !KNOWN_CODES.has(save.code)) && typeof save.retry === 'function') timer = setTimeout(retrySave,300 + Math.random()*400);
}
function mountSave(el) { if (el) { slots.save.push(el); renderSave(el); } }
function sourceBlocks() { const blocks = feed?.sources; return Array.isArray(blocks) ? blocks : blocks && typeof blocks === 'object' ? Object.entries(blocks).map(([source,b]) => ({...b,source:b.source || source})) : []; }
function sourceLabel(source) { return source === 'ORDER' ? 'Cited orders' : source; }
function watchSummary(b) {
if (!b.last_success) return sourceLabel(b.source) + ': No successful check yet.';
const count = Number.isInteger(b.checked_count) && b.checked_count >= 0 ? b.checked_count + ' ' + (b.source === 'ORDER' ? 'orders' : b.source + 's') : 'Count not stated';
const coverage = typeof b.body_available === 'boolean' ? (b.body_available ? 'full text':'titles only') : 'text availability not recorded';
const matches = Number.isInteger(b.possible_matches) && b.possible_matches >= 0 ? (b.possible_matches === 0 ? 'No possible matches.' : b.possible_matches + ' possible matches. Review before changing your plan.') : 'Possible matches are unknown for this check.';
return 'Checked ' + utc(b.last_success) + ': ' + count + ', ' + coverage + '. ' + (b.status === 'failed' ? MESSAGES.WATCH_FAILED : matches);
}
function stale() { return !!feed && (o.now() - Date.parse(feed.generated_at) > 8*86400000 || Date.parse(feed.expires_at) <= o.now()); }
function gap() { return !!feed && (feed.gap === true || o.now() - Date.parse(feed.generated_at) > 30*86400000); }
const todayKeys = new WeakMap();
function renderToday(el) {
const key = JSON.stringify({correction:update.correctionPending && update.status !== 'done',version:update.version,impact:update.impact,feed,watchCode,stale:stale(),gap:gap()}); if (todayKeys.get(el) === key) return; todayKeys.set(el,key);
el.replaceChildren(); el.classList.add('mot-root');
if (update.correctionPending && update.status !== 'done') { const banner = node('section',undefined,'mot-warning'); paragraph(banner,'Correction ready: ' + (update.version || 'Review update'),'mot-strong'); paragraph(banner,update.impact || MESSAGES.UPDATE_UNTRUSTED); banner.append(button('Review correction',openUpdates)); el.append(banner); }
const blocks = sourceBlocks().filter(b => ['MARADMIN','ALMAR'].includes(b.source));
const row = node('section',undefined,'mot-watch-line');
const checked = blocks.some(b => b.last_success), quiet = !checked || watchCode === 'WATCH_NOT_CHECKED';
const summary = watchCode && watchCode !== 'WATCH_NOT_CHECKED' ? 'review failed check' : quiet ? 'not checked yet' : stale() ? 'last check is old' : gap() ? 'coverage incomplete' : 'latest check ready';
const action = button('Policy checks: '+summary,openCoverage); action.classList.add('mot-policy-row'); const chevron=node('span','›'); chevron.setAttribute('aria-hidden','true'); action.append(chevron); row.append(action); el.append(row);
}
function mountToday(el) { if (el) { slots.today.push(el); renderToday(el); } }
function setWatch(value) {
if (value?.code && ['FEED_UNTRUSTED','WATCH_FAILED','WATCH_NOT_CHECKED'].includes(value.code)) { watchCode = value.code; recordError('feed','verify',value.code); }
else { watchCode = null; feed = value; } redraw(slots.today,renderToday); emit('watch'); }
function openCoverage() {
let s; s = sheet('Policy update checks',() => closeSheet(s));
const blocks = sourceBlocks().filter(b => ['MARADMIN','ALMAR'].includes(b.source));
const checked = blocks.filter(b => b.last_success), failed = watchCode || blocks.some(b => b.status === 'failed' || b.truncated || b.unclassified_count > 0 || b.body_available !== true || !Number.isInteger(b.checked_count) || !Number.isInteger(b.unclassified_count)) || stale() || gap();
const counts = typeof o.noticeSummary === 'function' ? o.noticeSummary() : null;
const matches = counts?.matches ?? blocks.reduce((sum,b) => sum + (Number.isInteger(b.possible_matches) ? b.possible_matches : (b.notices?.length || 0)),0);
const review = counts?.review || 0, at = checked.map(b => b.last_success).sort()[0];
paragraph(s.body,!checked.length ? 'Policy messages have not been checked yet.' : failed ? ((matches || review) ? (matches + review) + ' possible ' + (matches + review === 1 ? 'notice in' : 'notices in') + ' the last saved check. The latest check is incomplete.' : 'The latest check is incomplete. Review the last saved results.') : matches ? matches + ' possible ' + (matches === 1 ? 'notice matches' : 'notices match') + ' your profile.' : review ? review + ' ' + (review === 1 ? 'notice needs' : 'notices need') + ' an applicability review.' : 'No matching notices in the checked messages, checked ' + milDate(at.slice(0,10)) + '.','mot-strong');
const copy = button('Copy check request',async () => { const bytes = o.weeklyMessage; if (typeof bytes !== 'string' || !bytes) { paragraph(s.body,'The check request is unavailable. Open Talk to Claude.'); return; } if (await clipboard(bytes,s.notice)) s.notice.textContent = 'Copied. Paste into Claude.'; else openCopy('Copy check request',bytes); });
s.body.append(copy); paragraph(s.body,'Paste into Claude. A check does not change your plan.');
if (matches || review) paragraph(s.body,'Review possible notices in Sources and documents.');
const details = node('details'), summary = node('summary','Check details'); details.append(summary); s.body.append(details);
paragraph(details,'These checks compare published Marine Corps policy messages with your plan. Sources without a successful check still need review with the confirming office.');
if (!blocks.length) paragraph(details,'No successful check is recorded.');
blocks.forEach(b => {
const section = node('section',undefined,'mot-coverage'); section.append(node('h3',sourceLabel(b.source)));
paragraph(section,feed?.cadence === 'daily' && feed?.daily_shipped === true ? 'Daily checks.' : 'Weekly checks.');
paragraph(section,b.coverage || sourceLabel(b.source) + ' coverage has not been recorded.');
paragraph(section,'Last successful check','mot-meta'); paragraph(section,utc(b.last_success),'mot-mono');
paragraph(section,'Last attempt','mot-meta'); paragraph(section,utc(b.last_attempt),'mot-mono');
paragraph(section,'Checked window','mot-meta'); paragraph(section,b.window?.from && b.window?.to ? milDate(b.window.from) + ' to ' + milDate(b.window.to) : 'Not recorded');
paragraph(section,watchSummary(b));
if (b.truncated) paragraph(section,'This check is incomplete. Some notices were not included.');
if (Number.isInteger(b.unclassified_count) && b.unclassified_count > 0) paragraph(section,b.unclassified_count + ' notices await classification.');
if (b.status === 'failed') paragraph(section,b.reason || 'Last attempt failed.'); details.append(section);
});
if (watchCode && watchCode !== 'WATCH_NOT_CHECKED') paragraph(details,checked.length ? message(watchCode,'feed') : watchCode === 'FEED_UNTRUSTED' ? 'The latest feed could not be verified.' : 'The latest check did not finish.');
if (!blocks.some(b => b.source === 'ALMAR')) paragraph(details,'ALMAR: Not watched.');
if (stale()) paragraph(details,MESSAGES.FEED_STALE); if (gap()) paragraph(details,MESSAGES.FEED_GAP);
for (const name of ['ALNAV','Cited orders']) paragraph(details,name + ': Not yet covered.');
}

async function snooze(dismissed = false) {
const version = update.version, until = o.now() + 86400000;
try {
const state = o.updates?.snooze ? await o.updates.snooze() : {...update,status:'snoozed'}; if (state) setUpdate(state);
let kept = false;
try { localStorage.setItem('mo.update.snooze.' + version,String(until)); kept = Number(localStorage.getItem('mo.update.snooze.' + version)) === until; } catch (_) {}
if (o.db && o.canWrite !== false) {
try { const current = await o.db.doc('meta/trust_snoozes').get(); if (!definite(current)) throw {code:'unavailable'}; const versions = {...(current.data()?.versions || {}),[version]:until}; await verifiedSet('meta/trust_snoozes',{versions}); snoozePrefs = versions; kept = true; } catch (e) { recordError('db','snooze',e.code || e.name); }
}
if (!kept) throw {code:'SNOOZE_SAVE_FAILED'};
snoozePrefs[version] = until; if (update.status !== 'failed') closeSheet(updateSheet,true);
}
catch (e) { recordError('update','snooze',e.code || 'SNOOZE_SAVE_FAILED'); update = {...update,status:'failed',code:'SNOOZE_SAVE_FAILED'}; if (!dismissed) { openUpdates(); renderUpdate(); } }
}
async function apply() {
if (!o.updates?.applyUpdate || (update.correction && !update.impact)) return;
void count('update_taps');
try { const result = await o.updates.applyUpdate(); if (result) setUpdate(result); }
catch (e) { setUpdate({...update,status:'failed',code:e.code || 'artifact.upstream_error'}); }
}
function renderUpdate() {
if (!updateSheet) return;
const s = updateSheet, status = update.status;
s.body.replaceChildren(); s.actions.replaceChildren();
const cancel = () => snooze();
if (status === 'available' || status === 'snoozed') {
s.heading.textContent = (update.correction ? 'Correction ready: ':'Muster Out ') + update.version + (update.correction ? '' : ' is ready');
paragraph(s.body,'What changed','mot-strong');
const notes = Array.isArray(update.notes) ? update.notes : [];
notes.slice(0,2).forEach(text => paragraph(s.body,text));
if (update.correction) paragraph(s.body,update.impact || MESSAGES.UPDATE_UNTRUSTED);
const valid = notes.length === 2 && notes.every(n => typeof n === 'string' && n.trim()) && (!update.correction || (typeof update.impact === 'string' && update.impact.trim()));
if (!valid && !update.correction) paragraph(s.body,MESSAGES.UPDATE_UNTRUSTED);
const now = button('Update now',apply,true); now.disabled = !valid || !o.updates?.applyUpdate;
s.actions.append(now,button('Not now',cancel)); if (!valid) s.actions.append(button('View diagnostic',openDiagnostic)); if (!o.updates?.applyUpdate) { paragraph(s.body,MESSAGES['artifact.absent']); s.actions.append(button('Copy update message',() => copyMessage('update'))); } s.cancel = cancel;
} else if (status === 'applying') {
s.heading.textContent = 'Updating Muster Out'; s.cancel = null;
const progress = node('div'); window.MusterOutUpdateStatus?.render(progress,update,{version:o.version}); s.body.append(progress);
const labels = ['Saving your changes...','Publishing update...','Checking your board...'];
const current = {preparing:0,publishing:1,migrating:2,verifying:2}[update.phase] ?? 0;
const list = node('ol',undefined,'mot-progress'); labels.forEach((label,index) => { const li = node('li',label,index === current ? 'mot-current':''); if (index === current) li.setAttribute('aria-current','step'); list.append(li); });
list.setAttribute('role','status'); list.setAttribute('aria-live','polite'); s.body.append(list);
} else if (status === 'done') {
const progress = node('div'); window.MusterOutUpdateStatus?.render(progress,update,{version:o.version}); s.body.append(progress);
s.heading.textContent = 'Updated to ' + (update.justUpdated?.to || update.version || o.version) + '.'; s.cancel = () => closeSheet(s,true); s.actions.append(button('Continue',s.cancel,true));
} else if (status === 'failed') {
const progress = node('div'); window.MusterOutUpdateStatus?.render(progress,update,{version:o.version,retry:() => window.location.reload()}); s.body.append(progress);
s.heading.textContent = 'Update status'; const code = update.code || 'artifact.upstream_error'; notice(s.body,message(code,'artifact')); s.cancel = () => closeSheet(s,true);
if (['artifact.not_writer','artifact.not_granted','artifact.consent_required','artifact.not_declared','artifact.capability_disabled','artifact.capability_removed','artifact.absent'].includes(code)) s.actions.append(button('Copy update message',() => copyMessage('update')));
else if (code === 'DRAFT_STORAGE_FAILED') s.actions.append(button('Copy changes',copyChanges));
else s.actions.append(button('View diagnostic',openDiagnostic));
if (code === 'UPDATE_VERIFY_FAILED') s.actions.append(button('Get help',help));
s.actions.append(button(code === 'SNOOZE_SAVE_FAILED' ? 'Continue':'Close',s.cancel));
} else if (status === 'idle' && lastConfirmed) { s.heading.textContent = 'Updated to ' + lastConfirmed.to + '.'; s.cancel = () => closeSheet(s,true); s.actions.append(button('Continue',s.cancel,true));
} else { s.heading.textContent = 'Updates'; paragraph(s.body,status === 'checking' ? 'Checking for an update...' : o.updates ? (update.upToDate ? 'No newer verified release was found.' : 'The release check did not finish. Your saved plan is kept.') : MESSAGES['artifact.absent']); s.cancel = () => closeSheet(s,true); s.actions.append(button('Copy update message',() => copyMessage('update')),button('Close',s.cancel)); }
s.close.hidden = false;
}
function openUpdates() { if (updateSheet) { updateSheet.heading.focus({preventScroll:true}); return; } updateSheet = sheet('Updates',null); renderUpdate(); }
function normalizeUpdateCode(code) {
if (['migration_unverified','install_unverified','journal_changed','legacy_pending'].includes(code)) return 'UPDATE_VERIFY_FAILED';
if (['hooks_missing','worker_unavailable'].includes(code)) return 'artifact.absent';
if (['invalid_message','signature','hash','expired','replay','product','kind','key','check_failed','wrong_pack','mirror_conflict'].includes(code)) return 'UPDATE_UNTRUSTED';
return code && (code.includes('.') || /^[A-Z]/.test(code)) ? code : 'artifact.' + (code || 'upstream_error');
}
function setUpdate(state) {
if (dead || !state) return;
if (state.status === 'available' && !snoozesReady) { pendingUpdate = state; return; }
if (state.status === 'available') { let until = snoozePrefs[state.version]; try { until = Math.max(until || 0,Number(localStorage.getItem('mo.update.snooze.' + state.version)) || 0); } catch (_) {} if (until > o.now() && until <= o.now()+86400000) state = {...state,status:'snoozed'}; }
if (state.version) releaseInfo = {version:state.version,notes:state.notes,correction:state.correction,impact:state.impact}; update = {...releaseInfo,...state}; if (update.code) update.code = normalizeUpdateCode(update.code);
if (update.status === 'available' && (!Array.isArray(update.notes) || update.notes.length !== 2 || update.notes.some(n => typeof n !== 'string' || !n.trim()) || (update.correction && (typeof update.impact !== 'string' || !update.impact.trim())))) update.code = 'UPDATE_UNTRUSTED';
if (update.code) recordError('update','apply',update.code); if (update.quietCode) recordError('update','verify',update.quietCode);
if (update.status === 'done') { lastConfirmed = {from:update.justUpdated?.from || null,to:update.justUpdated?.to || update.version || o.version}; if (o.db && o.canWrite !== false) void verifiedSet('meta/trust_update_receipt',lastConfirmed).catch(e => recordError('db','set',e.code || e.name)); }
redraw(slots.today,renderToday);
if (update.status === 'available' && !forced.has(update.version)) { forced.add(update.version); openUpdates(); }
if (update.status === 'snoozed' && updateSheet) closeSheet(updateSheet,true);
if (update.status === 'done' && !updateSheet && update.justUpdated) openUpdates();
renderUpdate(); emit('update');
}
function field(parent,label,tag,value) { const wrap = node('label',undefined,'mot-field'); wrap.append(node('span',label)); const input = node(tag || 'input'); if (tag === 'textarea') input.rows = 3; input.value = value || ''; wrap.append(input); parent.append(wrap); return input; }
function reportPayload(r) {
const payload = {kind:'feedback',id:r.id,install_id:o.installId || null,version:o.version,pack:o.pack,path:PATHS.includes(o.path) ? o.path : null,grade:GRADES.includes(o.grade) ? o.grade : null,category:r.category,error_class:r.error_class,created:r.created};
if (r.include_text) {
const prose = [];
if (r.expected.trim()) prose.push('Expected: ' + r.expected);
if (r.details.trim()) prose.push('Details: ' + r.details);
if (prose.length) payload.text = prose.join('\n');
}
return payload;
}
function reportValid(payload) { return /^[a-f0-9]{16,32}$/.test(payload.install_id || '') && PATHS.includes(payload.path) && GRADES.includes(payload.grade) && validVersion(payload.version) && /^usmc-20\d{2}\.(0[1-9]|1[0-2])$/.test(payload.pack) && (payload.text === undefined || Array.from(payload.text).length <= 1000); }
function keepReport(s,r) {
if (!reportDrafts.write('current',JSON.stringify(r))) s.notice.textContent = MESSAGES.DRAFT_STORAGE_FAILED;
}
function openReport() {
let r = {id:hex(),created:new Date(o.now()).toISOString(),category:'content',problem:'Something looks wrong',where:SCREENS.includes(o.screen) ? o.screen : 'more',expected:'',details:'',error_class:'other',include_text:false};
try {
const saved = JSON.parse(reportDrafts.read('current') || 'null');
if (saved && /^[a-f0-9]{32}$/.test(saved.id) && Number.isFinite(Date.parse(saved.created)) && SCREENS.includes(saved.where) && ['bug','content','other'].includes(saved.category) && ERROR_CLASSES.includes(saved.error_class) && typeof saved.problem === 'string' && typeof saved.expected === 'string' && saved.expected.length <= 300 && typeof saved.details === 'string' && saved.details.length <= 600 && typeof saved.include_text === 'boolean') r = saved;
} catch (_) { recordError('draft','get','DRAFT_STORAGE_FAILED'); }
let s; s = sheet('Report a problem',() => closeSheet(s)); renderReportForm(s,r);
}
function renderReportForm(s,r) {
s.abort?.abort(); s.draftBindings?.forEach(release => release()); s.draftBindings = []; s.heading.textContent = 'Report a problem'; s.body.replaceChildren(); s.actions.replaceChildren(); s.cancel = () => closeSheet(s);
paragraph(s.body,'What happened','mot-strong'); const chips = node('div',undefined,'mot-chips'); s.body.append(chips);
[['Save failed','bug','save'],['Update failed','bug','update'],['Policy check failed','bug','feed'],['Something looks wrong','content','other'],['Other','other','other']].forEach(([label,category,error]) => {
const b = button(label,() => { r.problem = label; r.category = category; r.error_class = error; keepReport(s,r); chips.querySelectorAll('button').forEach(e => e.setAttribute('aria-pressed',String(e === b))); }); b.setAttribute('aria-pressed',String(r.problem === label)); chips.append(b);
});
const where = field(s.body,'Where','select'); SCREENS.forEach(v => { const option = node('option',({dates:'Timeline',claim:'VA Claim'})[v]||v[0].toUpperCase()+v.slice(1)); option.value = v; where.append(option); }); where.setAttribute('aria-label','Where'); where.value = r.where; s.draftBindings.push(reportDrafts.bind(where,'where',{restore:false,onChange:value => { r.where = value; keepReport(s,r); }}));
const expected = field(s.body,'What you expected (optional)','textarea',r.expected); expected.maxLength = 300;
s.draftBindings.push(reportDrafts.bind(expected,'expected',{restore:false,onChange:value => { r.expected = value; expected.removeAttribute('aria-invalid'); keepReport(s,r); }}));
paragraph(s.body,'Path: ' + (PATH_LABELS[o.path] || 'Unknown') + '; grade group: ' + (GRADE_LABELS[o.grade] || 'Unknown') + '.','mot-meta');
const details = field(s.body,'Details (optional)','textarea',r.details); details.maxLength = 600; s.draftBindings.push(reportDrafts.bind(details,'details',{restore:false,onChange:value => { r.details = value; s.body.querySelectorAll('.mot-rewrite').forEach(el => el.remove()); keepReport(s,r); }}));
const inclusion = node('label',undefined,'mot-include'), includeText = node('input'); includeText.type = 'checkbox'; includeText.checked = r.include_text; inclusion.append(includeText,node('span','Include optional text in this report')); s.body.append(inclusion);
s.draftBindings.push(reportDrafts.bind(includeText,'include_text',{restore:false,onChange:value => { r.include_text = value; keepReport(s,r); }}));
paragraph(s.body,'Remove names, dates, board links, and record details.');
const status = s.notice; status.textContent = '';
if (typeof o.sample === 'function') {
const rewrite = button('Rewrite details with Claude',async () => {
if (!details.value.trim()) return;
s.body.querySelectorAll('.mot-rewrite').forEach(el => el.remove());
const original = details.value; s.abort?.abort(); s.abort = new AbortController(); stop.hidden = false; rewrite.disabled = true; status.textContent = 'Thinking...';
let candidate;
try {
const result = await o.sample('Rewrite only these entered problem details in plain American English. Remove names, dates, board links, and record details. Do not add facts or instructions. Reply with wording only, at most 600 characters. Details:\n' + original,{signal:s.abort.signal,modelTier:'quick',effort:'low'});
if (!s.overlay.isConnected || s.abort.signal.aborted) return;
candidate = result.text;
if (typeof candidate !== 'string' || !candidate.trim() || result.truncated || Array.from(candidate).length > 600 || /[\u0000-\u001f\u007f-\u009f]/.test(candidate)) throw {code:'invalid_json'};
status.textContent = ''; const proposal = node('section',undefined,'mot-warning mot-rewrite'); paragraph(proposal,candidate);
proposal.append(button('Use this wording',() => { r.details = candidate; details.value = candidate; reportDrafts.write('details',candidate); keepReport(s,r); proposal.remove(); }),button('Keep my wording',() => proposal.remove())); s.body.append(proposal);
} catch (e) {
if (!s.overlay.isConnected) return; candidate = null;
if (e.code === 'cancelled') status.textContent = '';
else { recordError('sample','rewrite',e.code); status.textContent = message(e.code,'sample'); if (ABSENT.includes(e.code)) { o.sample = null; rewrite.hidden = true; } }
} finally { rewrite.disabled = false; stop.hidden = true; }
}); s.body.append(rewrite); paragraph(s.body,'Uses your Claude usage.','mot-meta'); const stop = button('Stop',() => s.abort?.abort()); stop.hidden = true; s.body.append(stop);
} else { paragraph(s.body,MESSAGES['sample.absent'],'mot-meta'); s.body.append(button('View diagnostic',openDiagnostic)); }
s.actions.append(button('Review report',() => {
r.expected = expected.value; r.details = details.value;
keepReport(s,r);
if (Array.from(reportPayload(r).text || '').length > 1000) { expected.setAttribute('aria-invalid','true'); status.textContent = MESSAGES.REPORT_VALIDATION_FAILED; expected.focus(); return; }
renderReportReview(s,r);
},true),button('Cancel',s.cancel));
}
function renderReportReview(s,r) {
s.abort?.abort(); s.draftBindings?.forEach(release => release()); s.draftBindings = []; s.heading.textContent = 'Review report'; s.heading.focus({preventScroll:true}); s.body.replaceChildren(); s.actions.replaceChildren();
paragraph(s.body,'Board fields: no name, no dates, no board link; an install id ties your reports together so a fix can be traced. Review your optional text.');
paragraph(s.body,'Category: ' + r.category + '; screen: ' + (({dates:'Timeline',claim:'VA Claim'})[r.where]||r.where) + '; error class: ' + r.error_class + '.','mot-meta');
paragraph(s.body,'Path: ' + (PATH_LABELS[o.path] || 'Unknown') + '; grade group: ' + (GRADE_LABELS[o.grade] || 'Unknown') + '.','mot-meta');
paragraph(s.body,reportPayload(r).text === undefined ? 'No optional text included.' : 'The payload below includes the optional text you chose to share.');
const exact = node('details'); exact.append(node('summary','See exactly what is sent')); s.body.append(exact);
const payload = reportPayload(r), context = Object.freeze({screen:r.where}), bytes = JSON.stringify(payload,null,2), preview = jsonBox(exact,bytes), status = s.notice; status.textContent = '';
const copy = button('Copy details',() => { exact.open = true; return clipboard(bytes,status,preview); }); copy.classList.add('mot-tertiary');
s.actions.append(button('Edit',() => renderReportForm(s,r)),copy);
{
paragraph(s.body,'Review here, then send from the report page.');
const queue = button('Continue to report page',async () => {
const hadFocus = document.activeElement === queue; queue.disabled = true;
if (hadFocus) s.heading.focus({preventScroll:true});
try {
if (!o.db || o.canWrite === false || !reportValid(payload)) throw {code:'REPORT_VALIDATION_FAILED'};
const ref = o.db.doc('outbox/' + payload.id), existing = await ref.get();
if (!definite(existing)) throw {code:'unavailable'};
const document = {schema_version:SCHEMA,kind:'feedback',id:payload.id,payload,bytes,context,approved_at:new Date(o.now()).toISOString(),status:'queued'};
if (existing.exists) { if (existing.data()?.bytes !== bytes || existing.data()?.context?.screen !== context.screen) throw {code:'REPORT_VALIDATION_FAILED'}; }
else { await ref.set(document); }
const read = await ref.get(); if (!definite(read) || !read.exists || read.data()?.bytes !== bytes || read.data()?.context?.screen !== context.screen) throw {code:'unavailable'};
const encoded = btoa(String.fromCharCode(...new TextEncoder().encode(bytes))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
const url = 'https://musterout.warfarecommand.com/report/#r=' + encoded;
reportDrafts.clear(); emit('report-queued');
status.textContent = 'Send it from the report page';
const link = node('a','Open report page','mot-button'); link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer';
s.actions.querySelector('.mot-report-link')?.remove(); link.classList.add('mot-report-link','mot-primary'); queue.remove(); s.actions.prepend(link,copy);
o.onReportLink?.(link);
await refreshSettings();
} catch (e) { recordError('report','queue',e.code || e.name); status.textContent = e.code === 'REPORT_VALIDATION_FAILED' ? MESSAGES.REPORT_VALIDATION_FAILED : MESSAGES.REPORT_QUEUE_FAILED; queue.disabled = false; }
},true);
queue.disabled = !o.db || o.canWrite === false || !reportValid(payload); s.actions.append(queue);
if (!reportValid(payload)) paragraph(s.body,'Report needs an install id, path, and grade group before sending. Copy details or check Troubleshooting.');
}
const troubleshooting = node('details'); troubleshooting.append(node('summary','Troubleshooting'),button('View diagnostic',openDiagnostic)); s.body.append(troubleshooting); s.body.parentElement.scrollTop = 0;
}
function usagePayload() { return {kind:'usage',install_id:o.installId || null,week:counterWeek,writer,version:o.version,counters:{...counters}}; }
function approved(c) { const counts = c?.sample?.counters; return c?.enabled === true && c.schema_version === SCHEMA && c.schema_key === SCHEMA_KEY && canonical(c.counter_meanings) === canonical(COUNTER_MEANINGS) && Number.isFinite(Date.parse(c.approved_at)) && c.sample?.kind === 'usage' && counts && Object.keys(counts).length === COUNTERS.length && COUNTERS.every(key => Number.isInteger(counts[key]) && counts[key] >= 0 && counts[key] <= 10000); }
async function verifiedSet(path,data) { const ref = o.db.doc(path); await ref.set(data); const snap = await ref.get(); if (!definite(snap) || !snap.exists || canonical(snap.data()) !== canonical(data)) throw {code:'unavailable'}; }
async function persistCounts() {
if (!o.learningEnabled || !o.db || o.canWrite === false || localPaused || !consentReady || !approved(consent) || dead) return false;
const live = await o.db.doc('meta/usage_consent').get();
if (!definite(live) || !approved(live.data())) { localPaused = true; consent = live.data(); redraw(slots.settings,renderSettings); return false; }
await verifiedSet('usage/' + counterWeek + '-' + writer,{schema_version:SCHEMA,status:'queued',...usagePayload()}); return true;
}
function count(key) {
if (!COUNTERS.includes(key) || dead) return Promise.resolve(false);
usageChain = usageChain.catch(() => false).then(async () => {
const week = weekAt(o.now()); if (week !== counterWeek) { try { await persistCounts(); } catch (e) { recordError('usage','count',e.code); } counterWeek = week; counters = Object.fromEntries(COUNTERS.map(k => [k,0])); }
counters[key] = Math.min(10000,counters[key]+1);
try { const ok = await persistCounts(); emit('usage'); return ok; } catch (e) { recordError('usage','count',e.code || e.name); return false; }
}); return usageChain;
}
function openConsent() {
let s; s = sheet('Usage counts',() => closeSheet(s)); paragraph(s.body,'Share weekly usage counts','mot-strong'); paragraph(s.body,'Counts help find broken steps. Allow weekly sending under this schema until you turn it off.');
paragraph(s.body,'Sample payload, schema 1'); const payload = usagePayload(), bytes = JSON.stringify(payload,null,2); jsonBox(s.body,bytes);
const meanings = node('details'); meanings.append(node('summary','What each count means')); const definitions = node('dl'); for (const [key,meaning] of Object.entries(COUNTER_MEANINGS)) { definitions.append(node('dt',key,'mot-mono'),node('dd',meaning)); } meanings.append(definitions); s.body.append(meanings);
paragraph(s.body,'No board text or profile fields. A new schema asks you again. Kept for 180 days.'); const status = s.notice; status.textContent = '';
const on = button('Allow weekly counts',async () => {
on.disabled = true;
try {
const c = {enabled:true,schema_version:SCHEMA,schema_key:SCHEMA_KEY,counter_meanings:COUNTER_MEANINGS,sample:payload,approved_at:new Date(o.now()).toISOString()};
await usageChain; await verifiedSet('meta/usage_consent',c); consent = c; consentReady = true; offRequested = false; localPaused = false; await persistCounts(); emit('consent'); await refreshSettings(); status.textContent = 'Weekly counts On.'; closeSheet(s);
} catch (e) { localPaused = true; recordError('usage','consent',e.code || e.name); status.textContent = 'Counts not enabled. Copy diagnostic.'; on.disabled = false; }
},true); on.disabled = !o.learningEnabled || !o.db || o.canWrite === false || !/^[a-f0-9]{16,32}$/.test(o.installId || '') || !validVersion(o.version);
s.actions.append(on,button('Not now',() => closeSheet(s)),button('View diagnostic',openDiagnostic));
}
async function setUsageEnabled(enabled) {
if (enabled) { openConsent(); return false; }
offRequested = true; localPaused = true; redraw(slots.settings,renderSettings);
if (!o.learningEnabled || !o.db || o.canWrite === false) { settingsError = MESSAGES.CONSENT_OFF_FAILED; redraw(slots.settings,renderSettings); return false; }
try {
await usageChain; const c = {enabled:false,schema_version:SCHEMA,schema_key:SCHEMA_KEY,changed_at:new Date(o.now()).toISOString()};
await verifiedSet('meta/usage_consent',c); consent = c; consentReady = true;
const [buckets,queued,sent] = await Promise.all([o.db.collection('usage').get(),o.db.collection('outbox').get(),o.db.collection('receipts').get()]);
if (![buckets,queued,sent].every(definite)) throw {code:'unavailable'};
const acknowledged = new Set(sent.docs.filter(d => definite(d) && ['sent','acknowledged'].includes(d.data()?.status) && d.data()?.acknowledged_at).map(d => d.data()?.payload_id || d.id));
for (const doc of queued.docs) { if (doc.data()?.kind === 'usage' && !acknowledged.has(doc.id)) await verifiedSet('outbox_control/' + doc.id,{cancelled:true,at:c.changed_at}); }
for (const doc of buckets.docs) { if (!acknowledged.has(doc.id) && !['sent','acknowledged'].includes(doc.data()?.status)) { await o.db.doc('usage/' + doc.id).delete(); const gone = await o.db.doc('usage/' + doc.id).get(); if (!definite(gone) || gone.exists) throw {code:'unavailable'}; } }
settingsError = ''; emit('consent'); await refreshSettings(); return true;
} catch (e) { settingsError = MESSAGES.CONSENT_OFF_FAILED; recordError('usage','consent',e.code || e.name); redraw(slots.settings,renderSettings); return false; }
}
function renderSettings(el) {
el.replaceChildren(); el.classList.add('mot-root'); el.hidden = !o.learningEnabled; if (el.hidden) return; el.append(node('h3','Reports and usage'));
paragraph(el,'Weekly counts: ' + (!localPaused && approved(consent) ? 'On':'Off'));
if (settingsError) { notice(el,settingsError); el.append(button('Get help',help)); }
if (consent?.enabled && !approved(consent)) notice(el,MESSAGES.CONSENT_SCHEMA_CHANGED);
const actions = actionRow(el); actions.append(button('On',openConsent),button('Off',() => setUsageEnabled(false)));
if (consent?.approved_at) paragraph(el,'Schema ' + consent.schema_version + ' approved ' + utc(consent.approved_at),'mot-meta');
if (consent?.sample) el.append(button('View approved schema',() => openCopy('Approved schema',JSON.stringify({schema_version:consent.schema_version,schema_key:consent.schema_key,counter_meanings:consent.counter_meanings,sample:consent.sample},null,2))));
if (!o.learningEnabled) paragraph(el,'Weekly sending and report queues are not available yet. Copy a report payload or diagnostic.');
const cancelled = new Set(controls.filter(d => d.cancelled).map(d => d.id));
const waiting = outbox.filter(d => !cancelled.has(d.id) && !receipts.some(r => r.payload_id === d.id && r.acknowledged_at));
paragraph(el,'Reports awaiting send: ' + waiting.filter(d => d.kind === 'feedback').length);
waiting.forEach(item => {
const row = node('section',undefined,'mot-receipt'); paragraph(row,(item.kind === 'usage' ? 'Usage ':'Report ') + item.id + ': Queued');
row.append(button('View payload',() => openCopy('Queued payload',item.bytes || JSON.stringify(item.payload,null,2))),button('Cancel report',async () => {
try { await verifiedSet('outbox_control/' + item.id,{cancelled:true,at:new Date(o.now()).toISOString()}); await refreshSettings(); }
catch (e) { recordError('report','set',e.code); notice(row,'Cancellation is not confirmed. Copy payload.'); }
})); el.append(row);
});
paragraph(el,'Receipts','mot-strong'); if (!receipts.length) paragraph(el,'No receipts yet.');
receipts.forEach(item => { const row = node('section',undefined,'mot-receipt'); const sent = item.acknowledged_at && ['sent','acknowledged'].includes(item.status); paragraph(row,item.id + ': ' + (sent ? 'Sent':'Queued')); row.append(button('View receipt',() => openCopy('Receipt',JSON.stringify(item,null,2)))); el.append(row); });
el.append(button('Delete sent reports and counts',openDeletion),button('View diagnostic',openDiagnostic));
}
function openDeletion() {
let s; s = sheet('Delete sent reports and counts',() => closeSheet(s));
paragraph(s.body,'This request deletes setup pings, install registrations, feedback reports, and usage counts tied to this install id. Your board and local receipts are kept.');
paragraph(s.body,'Exact payload','mot-strong'); const bytes = JSON.stringify({kind:'delete',install_id:o.installId || null},null,2); const preview = jsonBox(s.body,bytes);
const status = notice(s.body,'Deletion is not confirmed. Keep this receipt and try again.');
paragraph(s.body,'Copy this payload into Claude and ask to send the deletion request. Keep the server receipt with its deletion counts.');
s.actions.append(button('Copy payload',() => clipboard(bytes,status,preview),!o.learningEnabled),button('Cancel',() => closeSheet(s)));
}
function mountSettings(el) { if (el) { slots.settings.push(el); renderSettings(el); void refreshSettings(); } }
async function refreshSettings() {
if (dead) return;
if (!o.db || !o.learningEnabled) { redraw(slots.settings,renderSettings); return; }
try {
const [c,r,b,t] = await Promise.all([o.db.doc('meta/usage_consent').get(),o.db.collection('receipts').get(),o.db.collection('outbox').get(),o.db.collection('outbox_control').get()]);
if (![c,r,b,t].every(definite)) throw {code:'unavailable'};
consent = c.exists ? c.data() : null; consentReady = true; if (!approved(consent)) localPaused = true;
receipts = r.docs.map(d => ({...d.data(),id:d.id})); outbox = b.docs.map(d => ({...d.data(),id:d.id})); controls = t.docs.map(d => ({...d.data(),id:d.id}));
} catch (e) { recordError('usage','refresh',e.code || e.name); settingsError = 'Reports and usage could not refresh. Copy diagnostic.'; }
redraw(slots.settings,renderSettings);
}
function destroy() { reportDrafts.destroy(); dead = true; clearTimeout(timer); unsubscribe?.(); consentUnsubscribe?.(); while (sheets.length) closeSheet(sheets[sheets.length-1],true); }
if (o.db) {
void (async () => { try { const [snap,receipt] = await Promise.all([o.db.doc('meta/trust_snoozes').get(),o.db.doc('meta/trust_update_receipt').get()]); if (definite(snap) && snap.exists) snoozePrefs = snap.data()?.versions || {}; if (definite(receipt) && receipt.exists && receipt.data()?.to === o.version && validVersion(receipt.data().to)) lastConfirmed = receipt.data(); } catch (e) { recordError('db','snooze',e.code || e.name); } finally { snoozesReady = true; if (pendingUpdate && !dead) { const pending = pendingUpdate; pendingUpdate = null; setUpdate(pending); } } })();
}
if (o.updates?.subscribe) unsubscribe = o.updates.subscribe(setUpdate);
if (o.updates?.state) setUpdate(o.updates.state);
if (o.db && o.learningEnabled) {
void refreshSettings();
if (o.db.doc('meta/usage_consent').onSnapshot) consentUnsubscribe = o.db.doc('meta/usage_consent').onSnapshot(s => {
if (!definite(s)) return; consent = s.exists ? s.data() : null; consentReady = true; localPaused = offRequested || !approved(consent); redraw(slots.settings,renderSettings);
},e => { localPaused = true; recordError('db','onSnapshot',e.code); settingsError = 'Reports and usage could not refresh. Copy diagnostic.'; redraw(slots.settings,renderSettings); });
}
return Object.freeze({mountHeader,mountSave,mountToday,mountSettings,setContext(v) { for (const key of ['screen','path','grade']) if (key in v) o[key] = v[key]; },setSave,setWatch,setUpdate,openUpdates,openCoverage,openReport,openConsent,openDiagnostic,count,recordError,diagnostic,setUsageEnabled,refreshSettings,destroy});
}
window.MusterOutTrust = Object.freeze({create,createDraftOwner,validDraftId,COUNTER_KEYS:COUNTERS,SCHEMA_VERSION:SCHEMA,message});
})();
