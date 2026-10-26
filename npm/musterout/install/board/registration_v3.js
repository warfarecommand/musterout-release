/* Registration never sends from the board. Native links or a consent-verified reserved browser. */
var R3=window.MusterOutRG3,RG3_HANDOFF=null;
var RG3={startedAt:Date.now(),mode:false,eligible:false,busy:false,load:TEL_CONFIG.registrationV3Enabled===true?R3.random():null,firstFrame:0,visibleMs:0,lastTick:0,wasIdle:false,framePending:false,confirmation:null,opened:false,dismissed:false,card:null,tapped:false,message:'',halted:false,ready:false,stopping:false,pendingOffer:null,observing:false,observeEpoch:0,unsubscribe:null,retryTimer:null,retryDelay:1000,loadRetryTimer:null,loadRetryDelay:1000,bucket:null,offerAtLoad:null};
function rg3Mode(){return RG3.mode;}
function rg3Enabled(){return TEL_CONFIG.registrationV3Enabled===true;}
function rg3Agreement(s){return s?.schema===3&&s.agreement_version==='rg2-v3'&&Number.isFinite(Date.parse(s.agreement_accepted_at))&&telLicenseReady()&&(TEL_CONFIG.licenseAcknowledgmentRequired!==true||s.license?.agreed===true&&s.license.version===TEL_CONFIG.licenseAcknowledgmentVersion&&s.license.terms_sha256===TEL_CONFIG.licenseAcknowledgmentSha256);}
function rg3Pending(s){return s?.schema===3&&s.agreement_pending===true&&s.personal_owner_verified===true&&s.usage_enabled===false&&s.agreement_version===undefined&&s.agreement_accepted_at===undefined&&s.link_transport===undefined&&telLicenseReady()&&(TEL_CONFIG.licenseAcknowledgmentRequired!==true||s.license?.agreed===true&&s.license.version===TEL_CONFIG.licenseAcknowledgmentVersion&&s.license.terms_sha256===TEL_CONFIG.licenseAcknowledgmentSha256);}
function rg3OfferActive(s){return rg3Enabled()&&rg3Writable()&&(rg3Agreement(s)||rg3Pending(s))&&s?.enabled===true&&s.withdrawn!==true&&!RG3.halted&&!RG3.stopping&&RG3.ready;}
function rg3OfferPatch(work){return rg3Patch(work,false,true);}
function rg3Writable(){return RG3.eligible&&telGuard();}
function rg3Active(s){return rg3Enabled()&&rg3Writable()&&rg3Agreement(s)&&s?.enabled===true&&s.withdrawn!==true&&!RG3.halted&&!RG3.stopping&&RG3.ready;}
async function rg3Load(setup,state){
 RG3.mode=!!state?.rg3||setup?.telemetry_schema==='rg2-v3'||S.install?.registration_schema==='rg2-v3';
 if(!RG3.mode)return false;
 RG3.offerAtLoad=state?.rg3?.offer_id||null;
 TEL.state=state||{};TEL.pending=!!setup;TEL.localComplete=!setup&&!!S.install;TEL.enrolling=false;
 RG3.eligible=TEL.owner&&TEL.rules&&(state?.rg3?.personal_owner_verified===true||setup?.personal_owner_verified===true);
 RG3.loadRetryDelay=1000;if(RG3.loadRetryTimer){clearTimeout(RG3.loadRetryTimer);RG3.loadRetryTimer=null;}
 RG3.ready=!!state?.rg3;RG3.halted=state?.rg3?.withdrawn===true||state?.rg3?.enabled===false;TEL.loaded=true;rg3Observe();render();return true;
}
function rg3Idle(){return !S.seeding&&!UI.seedWaiting&&!c1BuildingPlan()&&!document.hidden&&!document.prerendering&&UI.tab==='brief'&&!UI.setup&&!UI.intake&&!UI.c1Dialog&&!document.querySelector('.mot-overlay,.c1-overlay')&&!UI.askBusy&&!typing()&&!UI.setupBusy&&!UI.intakeBusy&&!UI.dateBusy&&!UI.migrationBusy&&!UI.autoSeeding&&!UI.building&&!C1_UPDATE_FROZEN&&!C1_PENDING.size&&!Object.keys(queues).length&&!Object.keys(C1_FAILED).length&&!Object.keys(C1_DRAFTS).length;}
async function rg3Patch(work,withdrawal,pending){return telMutate(async function(){var user=await window.claude.use('user');if(await user?.isOwner?.()!==true){RG3.eligible=false;throw Error('Registration needs its owner.');}if(!rg3Writable())throw Error('Private registration storage is unavailable.');var state=await telGet('meta/telemetry_state')||{};var current=state.rg3;if(!current||(!withdrawal&&!rg3Agreement(current)&&!(pending&&rg3Pending(current))))throw Error('Registration agreement is unavailable.');var next=await work(clone(current));if(!next)return null;if(await user?.isOwner?.()!==true)throw Error('Registration owner changed.');await telSet('meta/telemetry_state',{...state,rg3:next});TEL.state={...state,rg3:next};if(UI.tab==='settings')rg3RefreshPrivacy();return next;});}
function rg3OpenedKey(){return 'mo.rg3.opened.'+location.pathname;}
function rg3OpenedDay(){if(RG3.localOpenedDay)return RG3.localOpenedDay;try{var day=localStorage.getItem(rg3OpenedKey());return /^\d{4}-\d{2}-\d{2}$/.test(day||'')&&iso(parseD(day))===day?day:null;}catch(_){return null;}}
function rg3RememberOpened(){var day=iso(today());RG3.localOpenedDay=day;try{localStorage.setItem(rg3OpenedKey(),day);}catch(_){} }
function rg3ClearOpened(){RG3.localOpenedDay=null;try{localStorage.removeItem(rg3OpenedKey());}catch(_){} }
function rg3Freeze(s){rg3ClearOpened();s.board_key=R3.random(8);var completed=s.first_completed_at||S.install?.completed;var date=typeof completed==='string'&&Number.isFinite(Date.parse(completed))?new Date(completed).toISOString().slice(0,10):null;
    s.registration={schema_version:3,kind:'registration',board_key:s.board_key,version:VERSION,path:['eas','retire','resign'].includes(S.profile.path)?S.profile.path:null,grade_band:['e15','e67','e89','o14','o5','wo13','cwo45'].includes(S.profile.grade)?S.profile.grade:null,campaign:R3.campaigns.includes(s.campaign)?s.campaign:null,setup_date:date};}
function rg3PlanReady(){return !!S.install?.completed&&(boardReady()||c1Undated())&&!S.seeding&&!c1BuildingPlan();}
// REG30: an offer belongs to the views already open when its verified save arrives.
// A later load never revives a consumed or uncertain offer.
function rg3SharedOffer(s){return /^[a-f0-9]{16}$/.test(s?.offer_id||'')&&s.offer_id!==RG3.offerAtLoad&&s.gate_offered===true&&!s.offer_deferred&&!s.tap_observed&&!s.link_copied;}
function rg3OfferDue(s,tick){return RG3.firstFrame&&tick-RG3.firstFrame>=1000&&(!s.offer_deferred||RG3.visibleMs>=60000);}
function rg3HideOffer(){if(!RG3.card)return;RG3.card.remove();RG3.card=null;el('app').hidden=false;el('app').inert=false;var heading=el('v30Title')||el('who');heading.tabIndex=-1;heading.focus({preventScroll:true});}
function rg3Decision(s){return R3.canonical({deferred:s?.offer_deferred||null,tap:!!s?.tap_observed,copy:!!s?.link_copied});}
function rg3ConsumeOffer(){RG3.dismissed=true;RG3.pendingOffer=null;var s=TEL.state.rg3;if(s?.withdrawn||s?.enabled===false||RG3_HANDOFF&&RG3_HANDOFF.decision!==rg3Decision(s))rg3CancelHandoff();rg3HideOffer();}
function rg3SyncOffer(){
 var s=TEL.state.rg3;
 if(!s)return;
 if(s.withdrawn||s.enabled===false||s.tap_observed&&!RG3.tapped||s.link_copied&&!RG3.copied){rg3ConsumeOffer();return;}
 if(s.offer_deferred){if(!rg3DeferredOffer(s))rg3ConsumeOffer();return;}
 if(RG3.card||RG3.busy||RG3.dismissed||!rg3OfferActive(s)||!rg3PlanReady()||!rg3Idle()||!rg3OfferDue(s,performance.now()))return;
 if((rg3SharedOffer(s)||RG3.pendingOffer)&&R3.valid(s.registration)&&s.board_key===s.registration.board_key&&rg3Fragment(s.registration)){RG3.pendingOffer=null;rg3Show(s.registration);}
}
function rg3AfterRender(){
 rg3SyncOffer();
 if(!rg3Mode()||!rg3OfferActive(TEL.state.rg3)||RG3.card||RG3.busy||!rg3PlanReady())return;
 if(UI.tab==='settings'&&!TEL.state.rg3.registration){rg3PrepareManual();return;}
 // Retry the painted Today check after pending setup and saves settle.
 if(!RG3.firstFrame&&!RG3.framePending&&rg3Idle()){
  RG3.framePending=true;
  requestAnimationFrame(function(){RG3.framePending=false;if(!rg3Idle()||!rg3PlanReady())return;RG3.firstFrame=performance.now()||0.01;RG3.lastTick=performance.now();RG3.wasIdle=true;rg3Tick();});
 }
}
async function rg3PrepareManual(){
 if(RG3.busy||!rg3PlanReady()||!rg3OfferActive(TEL.state.rg3))return;
 RG3.busy=true;
 try{
  if(!await c1VerifyMigration())return;
  var saved=await rg3OfferPatch(function(s){if(!rg3OfferActive(s)||s.registration)return null;if(!s.board_key)rg3Freeze(s);return s;});
  if(saved&&UI.tab==='settings')render();
 }catch(e){rg3Unavailable();rg3Retry();}
 finally{RG3.busy=false;}
}
function rg3DeferredOffer(s){return !!s?.offer_deferred&&s.offer_deferred.load!==RG3.load&&Date.parse(s.offer_deferred.at)<RG3.startedAt&&!s.tap_observed&&!s.link_copied;}
function rg3Deferred(){return UI.autoSeeding||UI.building||UI.migrationBusy||UI.setupBusy||UI.intakeBusy||UI.dateBusy||S.seeding||C1_UPDATE_FROZEN;}
async function rg3Tick(){
 if(!rg3Mode()||!rg3Enabled())return;
 var tick=performance.now(),idle=rg3Idle()&&rg3PlanReady()&&rg3OfferActive(TEL.state.rg3);
 if(RG3.lastTick&&RG3.wasIdle&&idle)RG3.visibleMs+=Math.min(1000,Math.max(0,tick-RG3.lastTick));
 RG3.lastTick=tick;RG3.wasIdle=idle;
 if(!RG3.firstFrame||UI.tab==='settings'){rg3AfterRender();return;}
 if(RG3.busy||!idle)return;
 rg3SyncOffer();if(RG3.card)return;
 if((TEL.state.rg3.gate_offered&&!rg3DeferredOffer(TEL.state.rg3))||RG3.dismissed){if(!RG3.opened){RG3.opened=true;rg3Count('opens');}return;}
 if(TEL.state.rg3.first_value_at&&!rg3OfferDue(TEL.state.rg3,tick))return;
 RG3.busy=true;
 try{
  if(!await c1VerifyMigration()||!rg3Idle()||!rg3PlanReady()||!rg3OfferActive(TEL.state.rg3))return;
  var show=false;
  var state=await rg3OfferPatch(function(s){
   if(!rg3OfferActive(s)||(s.gate_offered&&!rg3DeferredOffer(s))||RG3.dismissed)return null;
   if(s.offer_deferred&&RG3.visibleMs<60000)return null;
   if(!s.first_value_at){s.first_value_at=nowIso();s.first_value_load=RG3.load;if(!s.board_key)rg3Freeze(s);return s;}
   if(!rg3OfferDue(s,tick))return null;
   // The next load still paints its plan first, with a short quiet interval.
   if(tick-RG3.firstFrame<1000)return null;
   if(!rg3Idle())return null;
   if(!s.board_key)rg3Freeze(s);
   if(!R3.valid(s.registration)||s.board_key!==s.registration.board_key||!rg3Fragment(s.registration))return null;
   delete s.offer_deferred;s.gate_offered=true;s.offer_id=R3.random(8);show=true;return s;
  });
  // A verified offer may finish saving after Today stops being idle. Keep it
  // only in this load; a committed or uncertain offer never rearms on reload.
  if(show&&state)RG3.pendingOffer=state.registration;
  if(!RG3.opened){RG3.opened=true;rg3Count('opens');}
 }catch(e){if(!rg3Deferred()){if(show){RG3.dismissed=true;RG3.pendingOffer=null;}rg3Unavailable();rg3Retry();}}
 finally{RG3.busy=false;rg3SyncOffer();}
}
function rg3Fragment(record){try{return R3.encode(record);}catch(_){return null;}}
function rg3TransportOk(s){return rg3Agreement(s)&&s?.link_transport==='query-v1'&&RG3.transportUnconfirmed!==true;}
function rg3Url(record){var token=rg3Fragment(record);if(!token)return null;return 'https://musterout.warfarecommand.com/r/'+(record.kind==='delete'?'#':'?registration=')+token;}
function rg3Link(record,label,action){var url=rg3Url(record);if(!url||record.kind==='registration'&&!rg3TransportOk(TEL.state.rg3))return '';return '<a class="btn '+(action==='rg3-tap'&&!rg3OpenedDay()?'pri':'')+'" data-act="'+action+'" target="_blank" rel="noopener noreferrer" href="'+url+'">'+label+'</a>';}
var RG3_TRANSPORT_NOTICE="Your registration link carries this board's count code in the web address. Our hosting provider can log it. It holds no name, email or plan details. Details are in Privacy.";
var RG3_TRANSPORT_DETAIL="Registration links now put count details and a key that can change or delete counts in the web address, where hosting providers can log them.";
function rg3Disclosure(){return '<div class="rg3-agreement"><p class="c1-prose">'+RG3_AGREEMENT.join('</p><p class="c1-prose">').replace(' Do you agree?','')+'</p></div>';}
function rg3CardDisclosure(){return '<p class="c1-prose">One tap registers your board. No name or email.</p><ul class="rg3-facts"><li>Sent: random board key, version, path, grade group, campaign code if present, and setup day.</li><li>The web address carries your board&#39;s count code. Our hosting provider can log it.</li><li>Registration records stay for up to 24 months.</li><li>Stop future counts or request deletion in Settings.</li></ul><details class="c1-disclosure"><summary>Details</summary>'+rg3Disclosure()+'<p class="c1-prose">The count code holds no name, email or plan details.</p></details>';}
function rg3Controls(record){
 if(!rg3TransportOk(TEL.state.rg3))return rg3CardDisclosure()+'<button class="btn pri" data-act="rg3-transport"'+(RG3.transportBusy?' disabled':'')+'>Agree and register</button>';
 return rg3Link(record,rg3OpenedDay()?'Open again':'Open browser',(TEL.state.rg3?.tap_observed||RG3.tapped)?'rg3-resend':'rg3-tap')+'<button class="btn" data-act="rg3-copy">Copy link</button><p class="c1-prose">If the browser cannot register, copy the link and paste it into your browser address bar. Keep the link private.</p>';
}
function rg3Purpose(){return '<p class="c1-prose">New setups require agreement to a one-time board count.</p><p class="c1-prose">Registration counts that a new board exists, with no name, no email, and nothing from your plan. <button class="linkbtn" data-act="rg3-settings">Settings</button></p>';}
function rg3Fields(){return '<p class="c1-prose">Your browser sends your board version, plan path, grade group, campaign code, setup day, and a random board key. Your plan and notes stay in Claude.</p>';}
function rg3RefreshCard(){if(!RG3.card)return;var record=TEL.state.rg3?.registration;RG3.card.remove();RG3.card=null;if(rg3OfferActive(TEL.state.rg3)&&record)rg3Show(record);else{el('app').hidden=false;el('app').inert=false;}}
// Reserve a key-free window during the gesture. No receiver request is made
// until the existing consent mutation has definitive matching readback.
function rg3ReserveBrowser(){
 var target=null;
 try{target=window.open('about:blank','_blank');if(target){target.opener=null;var meta=target.document.createElement('meta');meta.name='referrer';meta.content='no-referrer';target.document.head.append(meta);target.document.title='Muster Out';target.document.body.textContent='Saving your registration choice...';}}
 catch(e){try{target?.close();}catch(_){}return null;}
 return target;
}
function rg3CancelHandoff(){if(!RG3_HANDOFF)return;RG3_HANDOFF.cancelled=true;try{RG3_HANDOFF.target?.close();}catch(_){} }
function rg3OpenReserved(operation){
 var s=TEL.state.rg3,target=operation.target;
 if(operation.cancelled||operation.offerId!==s?.offer_id||operation.registration!==R3.canonical(s?.registration))return false;
 var url=rg3Active(s)&&rg3TransportOk(s)&&s.board_key===s.registration?.board_key?rg3Url(s.registration):null;
 if(!target||target.closed||!url)return false;
 try{var link=target.document.createElement('a');link.href=url;link.rel='noopener noreferrer';link.textContent='Open browser';target.document.body.replaceChildren(link);link.click();rg3RememberOpened();RG3.tapped=true;RG3.pendingOffer=null;rg3Dismiss();rg3Patch(function(s){if(!rg3Active(s))return null;s.tap_observed=true;s.gate_offered=true;return s;}).catch(function(){});return true;}
 catch(e){try{target.close();}catch(_){}return false;}
}
async function rg3AcceptTransport(){
 if(RG3.transportBusy||!rg3OfferActive(TEL.state.rg3)||!rg3PlanReady()||rg3TransportOk(TEL.state.rg3))return;
 var operation={pending:rg3Pending(TEL.state.rg3),target:rg3ReserveBrowser(),offerId:TEL.state.rg3.offer_id,registration:R3.canonical(TEL.state.rg3.registration),decision:rg3Decision(TEL.state.rg3),cancelled:false};RG3_HANDOFF=operation;
 RG3.transportBusy=true;RG3.transportUnconfirmed=true;RG3.message='';
 try{
  function current(s){return !operation.cancelled&&rg3OfferActive(s)&&s.personal_owner_verified===true&&(!operation.pending||s.usage_enabled===false)&&operation.offerId===s.offer_id&&operation.registration===R3.canonical(s.registration)&&operation.decision===rg3Decision(s)&&s.board_key===s.registration?.board_key&&R3.valid(s.registration);}
  if(rg3Pending(TEL.state.rg3)){
   await rg3OfferPatch(function(s){if(!current(s))throw Error('inactive');if(rg3Agreement(s))return null;if(!rg3Pending(s))throw Error('agreement unavailable');s.agreement_version='rg2-v3';s.agreement_accepted_at=nowIso();delete s.agreement_pending;return s;});
  }
  var saved=await rg3Patch(function(s){if(!current(s)||!rg3Active(s))throw Error('inactive');s.link_transport='query-v1';return s;});
  // The lease may have finished after a newer event. Recheck definitive state,
  // never promote a cached or pending snapshot merely because an older save won.
  var snap=await DB.doc('meta/telemetry_state').get();
  if(!telDef(snap)||!snap.exists||R3.canonical(snap.data()?.rg3)!==R3.canonical(saved))throw Error('incomplete');
  rg3ApplySnapshot(snap);RG3.transportUnconfirmed=false;
  if(!operation.cancelled&&!rg3OpenReserved(operation)){try{operation.target?.close();}catch(_){}RG3.message='Your choice was saved. Open registration in your browser.';}
 }
 catch(e){try{operation.target?.close();}catch(_){}if(!operation.cancelled)RG3.message='Your choice was not confirmed. Try again. Your plan is ready.';}
 finally{if(RG3_HANDOFF===operation)RG3_HANDOFF=null;RG3.transportBusy=false;rg3RefreshPrivacy();rg3RefreshCard();rg3SyncOffer();}
}
async function rg3Copy(){
 var s=TEL.state.rg3;if(!rg3Active(s)||!rg3TransportOk(s)||!s.registration)return;
 var url=rg3Url(s.registration);if(!url)return;
 var host=RG3.card?.querySelector('.rg3-content')||document.querySelector('.rg3-settings');if(!host)return;
 host.querySelector('[data-rg3-copy]')?.remove();
 // Keep a selectable fallback in this surface even when clipboard access is denied.
 var box=document.createElement('div');box.dataset.rg3Copy='true';
 var label=document.createElement('label');label.className='field';label.textContent='Copy this private link, then paste it into your browser address bar.';
 var field=document.createElement('textarea');field.readOnly=true;field.rows=3;field.value=url;field.setAttribute('aria-label','Registration link');label.append(field);box.append(label);host.append(box);RG3.copied=true;
 rg3Patch(function(s){if(!rg3Active(s)||!rg3TransportOk(s))return null;s.link_copied=true;s.gate_offered=true;return s;}).catch(function(){});
 try{await navigator.clipboard.writeText(url);if(box.isConnected&&rg3Active(TEL.state.rg3)&&rg3TransportOk(TEL.state.rg3)){RG3.message='Link copied. Paste it into your browser address bar.';toast(RG3.message);}}
 catch(e){if(box.isConnected){field.focus();field.select();}}
}
function rg3Show(record){
 var section=document.createElement('section');section.id='rg3-card';section.dataset.transport=String(rg3TransportOk(TEL.state.rg3));section.setAttribute('aria-labelledby','rg3-title');
 section.innerHTML='<div class="rg3-content"><h1 id="rg3-title" tabindex="-1">Register your board.</h1>'+(rg3TransportOk(TEL.state.rg3)?rg3Purpose()+rg3Fields():'')+rg3Controls(record)+'<button class="linkbtn" data-act="rg3-later">Not now</button><p class="c1-prose">Register later. Your plan stays open.</p><p role="status">'+esc(RG3.message)+'</p>'+(rg3TransportOk(TEL.state.rg3)?'<details><summary>Privacy</summary>'+rg3Disclosure()+'</details>':'')+'</div>';
 RG3.card=section;var app=el('app');app.inert=true;app.hidden=true;document.body.append(section);el('rg3-title').focus();
}
function rg3Dismiss(){if(RG3.card){RG3.dismissed=true;rg3HideOffer();}}
function rg3Later(){
 if(!RG3.card)return;
 rg3CancelHandoff();RG3.pendingOffer=null;rg3Dismiss();
 // Only an explicit deferral permits a later offer. Existing views stay quiet.
 rg3OfferPatch(function(s){if(!rg3OfferActive(s)||s.tap_observed||s.link_copied)return null;s.offer_deferred={at:nowIso(),load:RG3.load};return s;}).catch(function(){RG3.message='Registration stays in Settings. Your plan is ready.';});
}
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&RG3.card){e.preventDefault();rg3Later();}});
function rg3PossibleReceipt(s){return !!(s.tap_observed||s.link_copied||RG3.tapped||RG3.copied);}
function rg3Settings(){if(!rg3Writable())return '';var s=TEL.state.rg3||{},stopped=RG3.halted||RG3.stopping||!RG3.ready||s.withdrawn||!s.enabled;return '<section class="panel rg3-settings"><h2>Board registration</h2>'+(rg3TransportOk(s)||!rg3OfferActive(s)?rg3Purpose():'')+'<p>'+(stopped?(s.withdrawn?'Counts stopped. Your plan is ready.':'Counts paused in this view. Your plan is ready.'):(rg3OpenedDay()?'Registration opened on '+mil(parseD(rg3OpenedDay()))+'. If that page said You are registered, you are done.':'Not confirmed. Your plan is ready.'))+'</p>'+(rg3OfferActive(s)&&s.registration&&!rg3Fragment(s.registration)?'<p>Registration link unavailable. Your plan is ready.</p>':'')+(rg3OfferActive(s)&&s.registration&&rg3Fragment(s.registration)?rg3Controls(s.registration)+(rg3TransportOk(s)?rg3Fields():''):'')+rg3UsageSettings(s)+'<p role="status">'+esc(RG3.message)+'</p><details class="c1-disclosure"><summary>Privacy</summary>'+rg3Confirmation()+(rg3PossibleReceipt(s)?'<p>If your board was counted:</p>'+(!s.withdrawn?'<button class="btn" data-act="rg3-stop">Stop counts</button>':'')+(RG3.eligible&&s.board_key?'<button class="btn" data-act="rg3-delete">Delete counts</button>':''):'')+(rg3TransportOk(s)||!rg3OfferActive(s)?rg3Disclosure():'')+'</details></section>';}
function rg3Confirmation(){
 if(!RG3.confirmation)return '';
 var deletion=RG3.confirmation==='delete';
 return '<div role="group" aria-label="Confirm privacy change"><p class="c1-prose">'+(deletion?'Stop future counts and request deletion of received counts for this board. Deletion completes only after your browser confirms it. A one-way key hash remains to prevent old links from restoring records.':'Stop future counts for this board on all devices after the change saves. This does not delete counts already received. Previously copied or in-flight links cannot be recalled.')+' This cannot be undone. Your saved plan stays usable.</p><button class="btn pri" data-act="rg3-confirm-'+RG3.confirmation+'">'+(deletion?'Review deletion':'Stop counts')+'</button><button class="btn" data-act="rg3-cancel">Cancel</button></div>';
}
function rg3RefreshPrivacy(){
 var panel=document.querySelector('.rg3-settings'),opened=panel?.querySelector('details')?.open;
 if(panel){var copy=panel.querySelector('[data-rg3-copy]'),field=copy?.querySelector('textarea'),focused=field===document.activeElement;panel.outerHTML=rg3Settings();panel=document.querySelector('.rg3-settings');var details=panel?.querySelector('details');if(details)details.open=opened;
  if(copy&&panel&&rg3Active(TEL.state.rg3)&&rg3TransportOk(TEL.state.rg3)&&field.value===rg3Url(TEL.state.rg3.registration)){panel.append(copy);if(focused){field.focus();field.select();}}
 }
}
async function rg3Stop(){rg3CancelHandoff();document.querySelectorAll('[data-rg3-copy]').forEach(x=>x.remove());RG3.stopping=true;RG3.pendingOffer=null;rg3Dismiss();rg3ClearDecorated();document.querySelectorAll('a[data-act^="rg3-"]').forEach(function(a){a.removeAttribute('href');});try{await rg3Patch(function(s){s.enabled=false;s.usage_enabled=false;s.withdrawn=true;s.gate_offered=true;s.usage_buckets=[];return s;},true);RG3.message=rg3PossibleReceipt(TEL.state.rg3)?'Previously copied or in-flight links cannot be recalled.':'';}catch(e){RG3.message='Counts paused in this view. Stopping on other devices is not confirmed. Try Stop counts again.';}render();return TEL.state.rg3?.withdrawn===true;}
async function rg3Count(kind){
 if(!rg3Mode()||TEL_CONFIG.registrationV3UsageEnabled!==true||!['opens','done'].includes(kind))return false;
 try{await rg3Patch(function(s){if(!rg3Active(s)||s.usage_enabled!==true||s.usage_agreement_version!=='rg3-usage-1'||!s.first_value_at)return null;var now=Date.now(),week=Math.floor((now-Date.parse(s.first_value_at))/604800000);if(week<0||week>104)return null;var rows=(s.usage_buckets||[]).filter(x=>x.created_at+180*86400000>now);var row=rows.find(x=>x.bucket.bucket_id===RG3.bucket&&x.bucket.week_index===week&&x.bucket.revision<10000);if(!row){RG3.bucket=R3.random();row={created_at:now,bucket:{bucket_id:RG3.bucket,week_index:week,revision:0,opens:0,done_actions:0}};rows.push(row);}row.bucket.revision++;var key=kind==='done'?'done_actions':'opens';row.bucket[key]=Math.min(10000,row.bucket[key]+1);if(rows.length>512){rows=rows.slice(-512);s.usage_overflow=true;}s.usage_buckets=rows;return s;});return true;}catch(e){return false;}
}
// Future Help/Report integration is deliberately dormant until the 8 KiB probe.
// Report content remains reviewed and never sent automatically by this module.
function rg3UsageEnvelope(s,report){if(TEL_CONFIG.registrationV3UsageEnabled!==true||!rg3Active(s)||s.usage_enabled!==true||s.usage_agreement_version!=='rg3-usage-1')return null;var b=R3.batch(s.usage_buckets||[],s.usage_cursor||0,Date.now());return {fragment:R3.envelope(s.registration,b.rows.length?{schema_version:3,kind:'usage',board_key:s.board_key,version:VERSION,buckets:b.rows.map(x=>x.bucket)}:null,report),next_cursor:b.cursor};}
var RG3_AGREEMENT=["Muster Out requires a one-tap board registration after you first see your plan. No name or email is needed. Your browser sends Warfare Command a random board key, version, plan path, grade group, campaign code if present, and setup day. Your plan, notes and service dates stay in Claude. The board stays usable if registration fails.",RG3_TRANSPORT_DETAIL,"Registration records stay for up to 24 months. Published results use groups of at least 10 boards. You can stop future counts and request deletion in Settings. After deletion or expiry, a one-way key hash remains only to prevent old links from restoring records while this registration system accepts them. The website and hosting providers also process normal connection data such as your IP address. Later usage counts need a separate choice; reports and email are separate. Do you agree?"];
if(rg3Enabled()){
 setInterval(rg3Tick,1000);
 document.addEventListener('visibilitychange',function(){RG3.lastTick=performance.now();RG3.wasIdle=false;if(document.hidden)rg3Dismiss();});
 window.addEventListener('pageshow',function(e){if(e.persisted)rg3Dismiss();});
}
document.addEventListener('click',function(e){if(!rg3Mode())return;var a=e.target.closest('[data-act^="rg3-"]');if(!a)return;
  if(a.dataset.act==='rg3-settings'){rg3Dismiss();if(UI.tab!=='settings')c1Go('settings');var details=document.querySelector('.rg3-settings>.c1-disclosure');if(details){details.open=true;details.querySelector('summary')?.focus();}return;}
  if(a.dataset.act==='rg3-later'){rg3Later();return;}
  if(a.dataset.act==='rg3-transport'){rg3AcceptTransport();return;}
  if(a.dataset.act==='rg3-copy'){rg3Copy();return;}
  if(a.dataset.act==='rg3-tap'||a.dataset.act==='rg3-resend'){
   if(!rg3Active(TEL.state.rg3)||!rg3TransportOk(TEL.state.rg3)||a.href!==rg3Url(TEL.state.rg3.registration)){e.preventDefault();return;}
   // Keep the native anchor mounted until its default action has dispatched.
   rg3RememberOpened();RG3.tapped=true;RG3.dismissed=true;setTimeout(function(){rg3Dismiss();if(UI.tab==='settings')rg3RefreshPrivacy();},0);
   rg3Patch(function(s){if(!rg3Active(s))return null;s.tap_observed=true;s.gate_offered=true;return s;}).catch(function(){});return;
  }
  if(a.dataset.act==='rg3-cancel'){RG3.confirmation=null;rg3RefreshPrivacy();return;}
  if(a.dataset.act==='rg3-stop'||a.dataset.act==='rg3-delete'){RG3.confirmation=a.dataset.act==='rg3-delete'?'delete':'stop';rg3RefreshPrivacy();document.querySelector('[data-act="rg3-confirm-'+RG3.confirmation+'"]')?.focus();return;}
  if(a.dataset.act==='rg3-confirm-stop'&&RG3.confirmation==='stop'){RG3.confirmation=null;rg3Stop();}
  if(a.dataset.act==='rg3-confirm-delete'&&RG3.confirmation==='delete'){
   RG3.confirmation=null;
   var key=TEL.state.rg3?.board_key;
   rg3Stop().then(function(saved){if(!key||!rg3Writable())return;RG3.message=saved?'Check deletion in your browser.':'Counts paused in this view; check deletion in your browser. Stopping on other devices is not confirmed.';render();var host=document.querySelector('.rg3-settings');if(host){var details=host.querySelector('details');if(details)details.open=true;(details||host).insertAdjacentHTML('beforeend',rg3Link({schema_version:3,kind:'delete',board_key:key},'Open deletion confirmation','rg3-delete-link'));}});
  }
 });

var RG3_USAGE_COPY="Send saved counts when I open Muster Out's help or report page. These count board opens and items I mark done, grouped by weeks since setup, and include my board key and running version. No task names, notes, questions or service dates are included. Counts stay for up to 180 days. I can turn this off without changing my plan.";
function rg3UsageSettings(s){return (s.usage_overflow?'<p>Some older saved counts expired to keep storage bounded. Your plan is ready.</p>':'')+'<p>Optional opens and done counts: '+(s.usage_enabled?'On':'Off')+'.</p>'+(TEL_CONFIG.registrationV3UsageEnabled===true&&rg3Active(s)?'<p class="c1-prose">'+RG3_USAGE_COPY+'</p><p class="c1-prose">After saved counts expire, only a one-way bucket hash remains until registration expiry or deletion to prevent replay. A 512-bucket lifetime limit can pause new optional counts; Help and reports stay available.</p><p class="c1-prose">Example: week 0, opens 1, done actions 0. A random bucket id prevents duplicate counting.</p><button class="btn" data-act="rg3-usage">'+(s.usage_enabled?'Turn optional counts off':'Enable optional counts')+'</button>':'');}
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
function rg3Unavailable(transient){
 document.querySelectorAll('[data-rg3-copy]').forEach(x=>x.remove());
 RG3.ready=false;RG3.wasIdle=false;RG3.message='Registration is unavailable. Your plan is ready.';
 rg3ClearDecorated();document.querySelectorAll('a[data-act="rg3-tap"],a[data-act="rg3-resend"]').forEach(a=>a.removeAttribute('href'));if(transient){if(RG3.card){RG3.card.setAttribute('aria-busy','true');RG3.card.querySelector('[data-act="rg3-transport"]')?.setAttribute('disabled','');}}else{rg3CancelHandoff();rg3Dismiss();}rg3RefreshPrivacy();
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
 if(!telDef(snap)){rg3Unavailable(true);rg3Retry();return;}
 if(!snap.exists||!snap.data()?.rg3){rg3Unavailable();rg3Retry();return;}
 TEL.state=snap.data();var s=TEL.state.rg3;
 RG3.ready=true;if(s.withdrawn===true||s.enabled===false)RG3.halted=true;
 RG3.retryDelay=1000;if(RG3.retryTimer){clearTimeout(RG3.retryTimer);RG3.retryTimer=null;}
 if(RG3.message==='Registration is unavailable. Your plan is ready.'||RG3.message==='Registration link unavailable. Your plan is ready.')RG3.message='';
 if(s.usage_enabled!==true)rg3ClearDecorated();
 if(RG3.halted||RG3.stopping){RG3.pendingOffer=null;rg3ClearDecorated();document.querySelectorAll('a[data-act="rg3-tap"],a[data-act="rg3-resend"]').forEach(a=>a.removeAttribute('href'));rg3Dismiss();}
 if(!rg3Active(s)||!rg3TransportOk(s))document.querySelectorAll('[data-rg3-copy]').forEach(x=>x.remove());
 if(RG3.card&&(RG3.card.hasAttribute('aria-busy')||RG3.card.dataset.transport!==String(rg3TransportOk(s))))rg3RefreshCard();
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
