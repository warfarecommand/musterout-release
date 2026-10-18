/* Registration never sends from the board. Only native first-party anchors. */
var R3=window.MusterOutRG3;
var RG3={mode:false,eligible:false,busy:false,load:TEL_CONFIG.registrationV3Enabled===true?R3.random():null,firstFrame:0,visibleMs:0,lastTick:0,wasIdle:false,framePending:false,confirmation:null,opened:false,dismissed:false,card:null,tapped:false,message:'',halted:false,ready:false,stopping:false,pendingOffer:null,observing:false,observeEpoch:0,unsubscribe:null,retryTimer:null,retryDelay:1000,loadRetryTimer:null,loadRetryDelay:1000,bucket:null};
function rg3Mode(){return RG3.mode;}
function rg3Enabled(){return TEL_CONFIG.registrationV3Enabled===true;}
function rg3Agreement(s){return s?.schema===3&&s.agreement_version==='rg2-v3'&&Number.isFinite(Date.parse(s.agreement_accepted_at))&&telLicenseReady()&&(TEL_CONFIG.licenseAcknowledgmentRequired!==true||s.license?.agreed===true&&s.license.version===TEL_CONFIG.licenseAcknowledgmentVersion&&s.license.terms_sha256===TEL_CONFIG.licenseAcknowledgmentSha256);}
function rg3Writable(){return RG3.eligible&&telGuard();}
function rg3Active(s){return rg3Enabled()&&rg3Writable()&&rg3Agreement(s)&&s?.enabled===true&&s.withdrawn!==true&&!RG3.halted&&!RG3.stopping&&RG3.ready;}
async function rg3Load(setup,state){
 RG3.mode=!!state?.rg3||setup?.telemetry_schema==='rg2-v3'||S.install?.registration_schema==='rg2-v3';
 if(!RG3.mode)return false;
 TEL.state=state||{};TEL.pending=!!setup;TEL.localComplete=!setup&&!!S.install;TEL.enrolling=false;
 RG3.eligible=TEL.owner&&TEL.rules&&(state?.rg3?.personal_owner_verified===true||setup?.personal_owner_verified===true);
 RG3.loadRetryDelay=1000;if(RG3.loadRetryTimer){clearTimeout(RG3.loadRetryTimer);RG3.loadRetryTimer=null;}
 RG3.ready=!!state?.rg3;RG3.halted=state?.rg3?.withdrawn===true||state?.rg3?.enabled===false;TEL.loaded=true;rg3Observe();render();return true;
}
function rg3Idle(){return !S.seeding&&!UI.seedWaiting&&!c1BuildingPlan()&&!document.hidden&&!document.prerendering&&UI.tab==='brief'&&!UI.setup&&!UI.intake&&!UI.c1Dialog&&!document.querySelector('.mot-overlay,.c1-overlay')&&!UI.askBusy&&!typing()&&!UI.setupBusy&&!UI.intakeBusy&&!UI.dateBusy&&!UI.migrationBusy&&!UI.autoSeeding&&!UI.building&&!C1_UPDATE_FROZEN&&!C1_PENDING.size&&!Object.keys(queues).length&&!Object.keys(C1_FAILED).length&&!Object.keys(C1_DRAFTS).length;}
async function rg3Patch(work,withdrawal){return telMutate(async function(){var user=await window.claude.use('user');if(await user?.isOwner?.()!==true){RG3.eligible=false;throw Error('Registration needs its owner.');}if(!rg3Writable())throw Error('Private registration storage is unavailable.');var state=await telGet('meta/telemetry_state')||{};var current=state.rg3;if(!current||(!withdrawal&&!rg3Agreement(current)))throw Error('Registration agreement is unavailable.');var next=await work(clone(current));if(!next)return null;if(await user?.isOwner?.()!==true)throw Error('Registration owner changed.');await telSet('meta/telemetry_state',{...state,rg3:next});TEL.state={...state,rg3:next};if(UI.tab==='settings')rg3RefreshPrivacy();return next;});}
function rg3Freeze(s){s.board_key=R3.random(8);var completed=s.first_completed_at||S.install?.completed;var date=typeof completed==='string'&&Number.isFinite(Date.parse(completed))?new Date(completed).toISOString().slice(0,10):null;
    s.registration={schema_version:3,kind:'registration',board_key:s.board_key,version:VERSION,path:['eas','retire','resign'].includes(S.profile.path)?S.profile.path:null,grade_band:['e15','e67','e89','o14','o5','wo13','cwo45'].includes(S.profile.grade)?S.profile.grade:null,campaign:R3.campaigns.includes(s.campaign)?s.campaign:null,setup_date:date};}
function rg3PlanReady(){return !!S.install?.completed&&(boardReady()||c1Undated())&&!S.seeding&&!c1BuildingPlan();}
function rg3AfterRender(){
 if(!rg3Mode()||!rg3Active(TEL.state.rg3)||RG3.card||RG3.busy||!rg3PlanReady())return;
 if(UI.tab==='settings'&&!TEL.state.rg3.registration){rg3PrepareManual();return;}
 // Retry the painted Today check after pending setup and saves settle.
 if(!RG3.firstFrame&&!RG3.framePending&&rg3Idle()){
  RG3.framePending=true;
  requestAnimationFrame(function(){RG3.framePending=false;if(!rg3Idle()||!rg3PlanReady())return;RG3.firstFrame=performance.now()||0.01;RG3.lastTick=performance.now();RG3.wasIdle=true;rg3Tick();});
 }
}
async function rg3PrepareManual(){
 if(RG3.busy||!rg3PlanReady()||!rg3Active(TEL.state.rg3))return;
 RG3.busy=true;
 try{
  if(!await c1VerifyMigration())return;
  var saved=await rg3Patch(function(s){if(!rg3Active(s)||s.registration)return null;if(!s.board_key)rg3Freeze(s);return s;});
  if(saved&&UI.tab==='settings')render();
 }catch(e){rg3Unavailable();rg3Retry();}
 finally{RG3.busy=false;}
}
function rg3Deferred(){return UI.autoSeeding||UI.building||UI.migrationBusy||UI.setupBusy||UI.intakeBusy||UI.dateBusy||S.seeding||C1_UPDATE_FROZEN;}
async function rg3Tick(){
 if(!rg3Mode()||!rg3Enabled())return;
 var tick=performance.now(),idle=rg3Idle()&&rg3PlanReady()&&rg3Active(TEL.state.rg3);
 if(RG3.lastTick&&RG3.wasIdle&&idle)RG3.visibleMs+=Math.min(1000,Math.max(0,tick-RG3.lastTick));
 RG3.lastTick=tick;RG3.wasIdle=idle;
 if(!RG3.firstFrame||UI.tab==='settings'){rg3AfterRender();return;}
 if(RG3.busy||!idle)return;
 if(TEL.state.rg3.gate_offered||RG3.dismissed){if(RG3.pendingOffer&&!RG3.dismissed){var pending=RG3.pendingOffer;RG3.pendingOffer=null;if(R3.canonical(pending)===R3.canonical(TEL.state.rg3.registration))rg3Show(pending);}if(!RG3.opened){RG3.opened=true;rg3Count('opens');}return;}
 if(TEL.state.rg3.first_value_load===RG3.load&&RG3.visibleMs<60000)return;
 RG3.busy=true;
 try{
  if(!await c1VerifyMigration()||!rg3Idle()||!rg3PlanReady()||!rg3Active(TEL.state.rg3))return;
  var show=false;
  var state=await rg3Patch(function(s){
   if(!rg3Active(s)||s.gate_offered||RG3.dismissed)return null;
   if(!s.first_value_at){s.first_value_at=nowIso();s.first_value_load=RG3.load;if(!s.board_key)rg3Freeze(s);return s;}
   if(s.first_value_load===RG3.load&&RG3.visibleMs<60000)return null;
   // The next load still paints its plan first, with a short quiet interval.
   if(tick-RG3.firstFrame<1000)return null;
   if(!rg3Idle())return null;
   if(!s.board_key)rg3Freeze(s);
   if(!R3.valid(s.registration)||s.board_key!==s.registration.board_key||!rg3Fragment(s.registration))return null;
   s.gate_offered=true;show=true;return s;
  });
  // A verified offer may finish saving after Today stops being idle. Keep it
  // only in this load; a committed or uncertain offer never rearms on reload.
  if(show&&state){RG3.pendingOffer=state.registration;if(rg3Idle()&&rg3Active(state)){RG3.pendingOffer=null;rg3Show(state.registration);}}
  if(!RG3.opened){RG3.opened=true;rg3Count('opens');}
 }catch(e){if(!rg3Deferred()){rg3Unavailable();rg3Retry();}}
 finally{RG3.busy=false;}
}
function rg3Fragment(record){try{return R3.encode(record);}catch(_){return null;}}
function rg3Link(record,label,action){var fragment=rg3Fragment(record);if(!fragment)return '';return '<a class="btn '+(action==='rg3-tap'?'pri':'')+'" data-act="'+action+'" target="_blank" rel="noopener noreferrer" href="https://musterout.warfarecommand.com/r/#'+fragment+'">'+label+'</a>';}
function rg3Show(record){
 var section=document.createElement('section');section.id='rg3-card';section.setAttribute('aria-labelledby','rg3-title');
 section.innerHTML='<div class="rg3-content"><h1 id="rg3-title" tabindex="-1">Register your board.</h1><p>One tap. No name, no email.</p><p>This helps Warfare Command count boards. Your browser sends your version, plan path, grade group, campaign code, setup day and a random board key. Your plan and notes stay in Claude.</p>'+rg3Link(record,'Register my board','rg3-tap')+'<p>Opens your browser. Your board stays usable even if registration fails.</p><details><summary>Privacy</summary><p>'+RG3_AGREEMENT.join('</p><p>')+'</p></details></div>';
 RG3.card=section;var app=el('app');app.inert=true;app.hidden=true;document.body.append(section);el('rg3-title').focus();
}
function rg3Dismiss(){if(RG3.card){RG3.dismissed=true;RG3.card.remove();RG3.card=null;el('app').hidden=false;el('app').inert=false;var heading=el('who');heading.tabIndex=-1;heading.focus({preventScroll:true});}}
function rg3Settings(){if(!rg3Writable())return '';var s=TEL.state.rg3||{},stopped=RG3.halted||RG3.stopping||!RG3.ready||s.withdrawn||!s.enabled;return '<section class="panel rg3-settings"><h2>Board registration</h2><p>'+(stopped?(s.withdrawn?'Counts stopped. Your plan is ready.':'Counts paused in this view. Your plan is ready.'):(s.tap_observed||RG3.tapped)?'Registration page opened. Check the result there.':'Your plan is ready.')+'</p>'+(rg3Active(s)&&s.registration&&!rg3Fragment(s.registration)?'<p>Registration link unavailable. Your plan is ready.</p>':'')+(rg3Active(s)&&s.registration?rg3Link(s.registration,(s.tap_observed||RG3.tapped)?'Send registration again':'Register this board',(s.tap_observed||RG3.tapped)?'rg3-resend':'rg3-tap'):'')+rg3UsageSettings(s)+'<p role="status">'+esc(RG3.message)+'</p><details class="c1-disclosure"><summary>Privacy</summary>'+rg3Confirmation()+(!s.withdrawn?'<button class="btn" data-act="rg3-stop">Stop counts</button>':'')+(RG3.eligible&&s.board_key?'<button class="btn" data-act="rg3-delete">Delete received counts</button>':'')+'<p>'+RG3_AGREEMENT.join('</p><p>').replace(' Do you agree?','')+'</p></details></section>';}
function rg3Confirmation(){
 if(!RG3.confirmation)return '';
 var deletion=RG3.confirmation==='delete';
 return '<div role="group" aria-label="Confirm privacy change"><p>'+(deletion?'Stop future counts and request deletion of received counts for this board. Deletion completes only after your browser confirms it. A one-way key hash remains to prevent old links from restoring records.':'Stop future counts for this board on all devices after the change saves. This does not delete counts already received. Previously copied or in-flight links cannot be recalled.')+' This cannot be undone. Your saved plan stays usable.</p><button class="btn" data-act="rg3-confirm-'+RG3.confirmation+'">'+(deletion?'Stop counts and review deletion':'Confirm stop counts')+'</button><button class="btn" data-act="rg3-cancel">Cancel</button></div>';
}
function rg3RefreshPrivacy(){var panel=document.querySelector('.rg3-settings'),opened=panel?.querySelector('details')?.open;if(panel){panel.outerHTML=rg3Settings();var details=document.querySelector('.rg3-settings details');if(details)details.open=opened;}}
async function rg3Stop(){RG3.stopping=true;RG3.pendingOffer=null;rg3Dismiss();rg3ClearDecorated();document.querySelectorAll('a[data-act^="rg3-"]').forEach(function(a){a.removeAttribute('href');});try{await rg3Patch(function(s){s.enabled=false;s.usage_enabled=false;s.withdrawn=true;s.gate_offered=true;s.usage_buckets=[];return s;},true);RG3.message='Counts stopped. Previously copied or in-flight links cannot be recalled.';}catch(e){RG3.message='Counts paused in this view. Stopping on other devices is not confirmed. Try Stop counts again.';}render();return TEL.state.rg3?.withdrawn===true;}
async function rg3Count(kind){
 if(!rg3Mode()||TEL_CONFIG.registrationV3UsageEnabled!==true||!['opens','done'].includes(kind))return false;
 try{await rg3Patch(function(s){if(!rg3Active(s)||s.usage_enabled!==true||s.usage_agreement_version!=='rg3-usage-1'||!s.first_value_at)return null;var now=Date.now(),week=Math.floor((now-Date.parse(s.first_value_at))/604800000);if(week<0||week>104)return null;var rows=(s.usage_buckets||[]).filter(x=>x.created_at+180*86400000>now);var row=rows.find(x=>x.bucket.bucket_id===RG3.bucket&&x.bucket.week_index===week&&x.bucket.revision<10000);if(!row){RG3.bucket=R3.random();row={created_at:now,bucket:{bucket_id:RG3.bucket,week_index:week,revision:0,opens:0,done_actions:0}};rows.push(row);}row.bucket.revision++;var key=kind==='done'?'done_actions':'opens';row.bucket[key]=Math.min(10000,row.bucket[key]+1);if(rows.length>512){rows=rows.slice(-512);s.usage_overflow=true;}s.usage_buckets=rows;return s;});return true;}catch(e){return false;}
}
// Future Help/Report integration is deliberately dormant until the 8 KiB probe.
// Report content remains reviewed and never sent automatically by this module.
function rg3UsageEnvelope(s,report){if(TEL_CONFIG.registrationV3UsageEnabled!==true||!rg3Active(s)||s.usage_enabled!==true||s.usage_agreement_version!=='rg3-usage-1')return null;var b=R3.batch(s.usage_buckets||[],s.usage_cursor||0,Date.now());return {fragment:R3.envelope(s.registration,b.rows.length?{schema_version:3,kind:'usage',board_key:s.board_key,version:VERSION,buckets:b.rows.map(x=>x.bucket)}:null,report),next_cursor:b.cursor};}
var RG3_AGREEMENT=["Muster Out requires a one-tap board registration after you first see your plan. No name or email is needed. Your browser sends Warfare Command a random board key, version, plan path, grade group, campaign code if present, and setup day. Your plan, notes and service dates stay in Claude. The board stays usable if registration fails.","Registration records stay for up to 24 months. Published results use groups of at least 10 boards. You can stop future counts and request deletion in Settings. After deletion or expiry, a one-way key hash remains only to prevent old links from restoring records while this registration system accepts them. The website and hosting providers also process normal connection data such as your IP address. Later usage counts need a separate choice; reports and email are separate. Do you agree?"];
if(rg3Enabled()){
 setInterval(rg3Tick,1000);
 document.addEventListener('visibilitychange',function(){RG3.lastTick=performance.now();RG3.wasIdle=false;if(document.hidden)rg3Dismiss();});
 window.addEventListener('pageshow',function(e){if(e.persisted)rg3Dismiss();});
}
document.addEventListener('click',function(e){if(!rg3Mode())return;var a=e.target.closest('[data-act^="rg3-"]');if(!a)return;
  if(a.dataset.act==='rg3-tap'||a.dataset.act==='rg3-resend'){
   if(!rg3Active(TEL.state.rg3)){e.preventDefault();return;}
   // Keep the native anchor mounted until its default action has dispatched.
   RG3.tapped=true;RG3.dismissed=true;setTimeout(rg3Dismiss,0);
   rg3Patch(function(s){if(!rg3Active(s))return null;s.tap_observed=true;s.gate_offered=true;return s;}).catch(function(){});return;
  }
  if(a.dataset.act==='rg3-cancel'){RG3.confirmation=null;rg3RefreshPrivacy();return;}
  if(a.dataset.act==='rg3-stop'||a.dataset.act==='rg3-delete'){RG3.confirmation=a.dataset.act==='rg3-delete'?'delete':'stop';rg3RefreshPrivacy();document.querySelector('[data-act="rg3-confirm-'+RG3.confirmation+'"]')?.focus();return;}
  if(a.dataset.act==='rg3-confirm-stop'&&RG3.confirmation==='stop'){RG3.confirmation=null;rg3Stop();}
  if(a.dataset.act==='rg3-confirm-delete'&&RG3.confirmation==='delete'){
   RG3.confirmation=null;
   var key=TEL.state.rg3?.board_key;
   rg3Stop().then(function(saved){if(!key||!rg3Writable())return;RG3.message=saved?'Counts stopped; check deletion in your browser.':'Counts paused in this view; check deletion in your browser. Stopping on other devices is not confirmed.';render();var host=document.querySelector('.rg3-settings');if(host){var details=host.querySelector('details');if(details)details.open=true;(details||host).insertAdjacentHTML('beforeend',rg3Link({schema_version:3,kind:'delete',board_key:key},'Open deletion confirmation','rg3-delete-link'));}});
  }
 });

var RG3_USAGE_COPY="Send saved counts when I open Muster Out's help or report page. These count board opens and items I mark done, grouped by weeks since setup, and include my board key and running version. No task names, notes, questions or service dates are included. Counts stay for up to 180 days. I can turn this off without changing my plan.";
function rg3UsageSettings(s){return (s.usage_overflow?'<p>Some older saved counts expired to keep storage bounded. Your plan is ready.</p>':'')+'<p>Optional opens and done counts: '+(s.usage_enabled?'On':'Off')+'.</p>'+(TEL_CONFIG.registrationV3UsageEnabled===true&&rg3Active(s)?'<p>'+RG3_USAGE_COPY+'</p><p>After saved counts expire, only a one-way bucket hash remains until registration expiry or deletion to prevent replay. A 512-bucket lifetime limit can pause new optional counts; Help and reports stay available.</p><p>Example: week 0, opens 1, done actions 0. A random bucket id prevents duplicate counting.</p><button class="btn" data-act="rg3-usage">'+(s.usage_enabled?'Turn optional counts off':'Enable optional counts')+'</button>':'');}
function rg3ClearDecorated(){document.querySelectorAll('a[data-rg3-decorated]').forEach(function(a){a.href=a.dataset.rg3OriginalHref;delete a.dataset.rg3Decorated;delete a.dataset.rg3OriginalHref;delete a.dataset.rg3Cursor;a.querySelector('.rg3-count-label')?.remove();});}
async function rg3Decorate(){
 if(TEL_CONFIG.registrationV3UsageEnabled!==true||!rg3Mode())return;
 try{var state=await telGet('meta/telemetry_state'),s=state?.rg3;if(!rg3Active(s)||s.usage_enabled!==true){rg3ClearDecorated();return;}
 document.querySelectorAll('a[href]').forEach(function(a){if(a.dataset.rg3Decorated)return;var u;try{u=new URL(a.href);}catch(e){return;}if(u.origin!=='https://musterout.warfarecommand.com'||!['/support/','/report/'].includes(u.pathname)||u.search)return;
 var report=null;if(u.hash){if(u.pathname!=='/report/'||!/^#r=[A-Za-z0-9_-]+$/.test(u.hash))return;try{report=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(Uint8Array.from(atob(u.hash.slice(3).replace(/-/g,'+').replace(/_/g,'/')),c=>c.charCodeAt(0))));}catch(e){return;}}
 var batch=rg3UsageEnvelope(s,report);if(!batch?.fragment)return;a.dataset.rg3OriginalHref=a.href;a.dataset.rg3Decorated='true';a.dataset.rg3Cursor=String(batch.next_cursor);a.href=u.origin+u.pathname+'#'+batch.fragment;var label=document.createElement('span');label.className='rg3-count-label';label.textContent=' - Includes saved counts';a.append(label);
 });}catch(e){}
}
document.addEventListener('click',function(e){var a=e.target.closest('[data-rg3-decorated]');if(a)rg3Patch(function(s){if(!rg3Active(s))return null;s.usage_cursor=Number(a.dataset.rg3Cursor)||0;return s;}).catch(function(){});if(e.target.closest('[data-act="rg3-usage"]'))rg3Patch(function(s){if(!rg3Active(s)||TEL_CONFIG.registrationV3UsageEnabled!==true)return null;s.usage_enabled=!s.usage_enabled;s.usage_agreement_version='rg3-usage-1';s.usage_accepted_at=nowIso();if(!s.usage_enabled){s.usage_buckets=[];rg3ClearDecorated();}return s;}).then(render).catch(function(){RG3.message='The count choice was not confirmed.';render();});});

// Initial agreement reads can fail before v3 mode or its listener is attached.
function rg3RetryLoad(){
 if(RG3.loadRetryTimer||TEL.loaded)return;
 var delay=RG3.loadRetryDelay;RG3.loadRetryDelay=Math.min(30000,delay*2);
 RG3.loadRetryTimer=setTimeout(function(){RG3.loadRetryTimer=null;telLoad();},delay);
}
// Transient transport/storage failures suppress links without withdrawing consent.
function rg3Unavailable(){
 RG3.ready=false;RG3.wasIdle=false;RG3.message='Registration is unavailable. Your plan is ready.';
 rg3ClearDecorated();document.querySelectorAll('a[data-act="rg3-tap"],a[data-act="rg3-resend"]').forEach(a=>a.removeAttribute('href'));rg3Dismiss();rg3RefreshPrivacy();
}
function rg3Retry(){
 if(!rg3Mode()||!RG3.eligible||RG3.retryTimer)return;
 var delay=RG3.retryDelay;RG3.retryDelay=Math.min(30000,delay*2);
 RG3.retryTimer=setTimeout(async function(){
  RG3.retryTimer=null;rg3Observe();
  try{rg3ApplySnapshot(await DB.doc('meta/telemetry_state').get());}
  catch(e){rg3Unavailable();rg3Retry();}
 },delay);
}
function rg3ApplySnapshot(snap){
 if(!rg3Mode()||!RG3.eligible)return;
 if(!telDef(snap)||!snap.exists||!snap.data()?.rg3){rg3Unavailable();rg3Retry();return;}
 TEL.state=snap.data();var s=TEL.state.rg3;
 RG3.ready=true;if(s.withdrawn===true||s.enabled===false)RG3.halted=true;
 RG3.retryDelay=1000;if(RG3.retryTimer){clearTimeout(RG3.retryTimer);RG3.retryTimer=null;}
 if(RG3.message==='Registration is unavailable. Your plan is ready.'||RG3.message==='Registration link unavailable. Your plan is ready.')RG3.message='';
 if(s.usage_enabled!==true)rg3ClearDecorated();
 if(RG3.halted||RG3.stopping){RG3.pendingOffer=null;rg3ClearDecorated();document.querySelectorAll('a[data-act="rg3-tap"],a[data-act="rg3-resend"]').forEach(a=>a.removeAttribute('href'));rg3Dismiss();}
 rg3RefreshPrivacy();rg3AfterRender();
}
function rg3Observe(){
 if(!RG3.eligible||RG3.observing)return;
 var epoch=++RG3.observeEpoch;
 function failed(){
  if(epoch!==RG3.observeEpoch)return;
  RG3.observeEpoch++;RG3.observing=false;var unsubscribe=RG3.unsubscribe;RG3.unsubscribe=null;
  if(typeof unsubscribe==='function')try{unsubscribe();}catch(e){}
  rg3Unavailable();rg3Retry();
 }
 try{
  var ref=DB.doc('meta/telemetry_state');if(typeof ref.onSnapshot!=='function'){rg3Retry();return;}
  RG3.observing=true;
  var unsubscribe=ref.onSnapshot(function(snap){if(epoch===RG3.observeEpoch)rg3ApplySnapshot(snap);},failed);
  if(epoch===RG3.observeEpoch)RG3.unsubscribe=unsubscribe;else if(typeof unsubscribe==='function')unsubscribe();
 }catch(e){failed();}
}
window.addEventListener('pageshow',function(){if(!rg3Mode()||!RG3.eligible)return;rg3Observe();DB.doc('meta/telemetry_state').get().then(rg3ApplySnapshot).catch(function(){rg3Unavailable();rg3Retry();});});
