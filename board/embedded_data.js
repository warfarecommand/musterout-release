/* Seed transport and saved-record recovery. Uses the existing IDB codec. */
(function(global){
'use strict';
var help='https://musterout.warfarecommand.com/support/#setup-help',api={recovery:null,value:null};
function link(){var a=document.createElement('a');a.href=help;a.target='_blank';a.rel='noopener';a.textContent='Open setup help';return a;}
function notice(){
 var view=document.getElementById('view');
 view.replaceChildren();
 var section=document.createElement('section'),h=document.createElement('h2'),p=document.createElement('p');
 section.className='panel';section.id='board-data-unavailable';h.textContent='Plan data is unavailable in this browser';
 p.textContent='Open this board in a current browser, or use setup help. Your saved records are kept.';
 section.append(h,p,link());view.append(section);
 ['tabs','hero','stats','loeStrip','talkToClaude','registrationBanner','releaseBanner'].forEach(function(id){var n=document.getElementById(id);if(n)n.hidden=true;});
}
api.savedNotice=function(){
 // The recovery notice owns this load's status; a disconnected save control
 // would crowd the phone header and cannot offer a save action.
 document.getElementById('saveHeader').hidden=true;
 var host=document.getElementById('board-data-recovery');
 if(!host){host=document.createElement('p');host.id='board-data-recovery';document.getElementById('view').before(host);}
 host.replaceChildren(document.createTextNode('This browser could not open the plan data in this version. Your saved plan is shown; updates wait until it can. '),link());
};
// Recovery owns this whole load. Keep preferences and drafts usable in memory,
// including handlers and libraries that access window.localStorage directly.
function memoryStorage(source){
 var values=new Map();
 if(source)for(var i=0;i<source.length;i++){var key=source.key(i);values.set(key,source.getItem(key));}
 return {get length(){return values.size;},key:function(i){return Array.from(values.keys())[i]??null;},
  getItem:function(k){k=String(k);return values.has(k)?values.get(k):null;},
  setItem:function(k,v){values.set(String(k),String(v));},removeItem:function(k){values.delete(String(k));},clear:function(){values.clear();}};
}
function isolateStorage(){
 ['localStorage','sessionStorage'].forEach(function(name){
  var source;try{source=global[name];}catch(_){}
  Object.defineProperty(global,name,{value:memoryStorage(source),configurable:true});
 });
}
api.savedIDES=function(state,tab,support,appointmentTime){
 function esc(value){return String(value??'').replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
 function date(value){var m=String(value||'').match(/^(\d{4})-(\d{2})-(\d{2})$/);return m&&Number(m[2])>=1&&Number(m[2])<=12?m[3]+' '+['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][Number(m[2])-1]+' '+m[1]:value;}
 var ides=state.ides||{},title={brief:'Today',lines:'Plan',timeline:'Timeline',va:'Claim'}[tab]||'Saved IDES plan';
 var h='<section class="panel" id="saved-ides-plan"><div class="v30-head"><h1 id="v30Title" tabindex="-1">'+title+'</h1></div>';
 if(ides.stageConfirmed)h+='<p>Confirmed stage: <strong>'+esc(String(ides.stage||'').replace(/_/g,' ').toUpperCase())+'</strong></p>';
 if(ides.outcomeConfirmed)h+='<p>Confirmed disposition: '+esc(String(ides.outcome||'').replace(/_/g,' '))+'</p>';
 var events=[];Object.values(ides.events||{}).forEach(function(rows){Object.values(rows||{}).forEach(function(e){if(e&&e.status==='confirmed')events.push(e);});});
 h+='<h2>Saved confirmed events</h2>';
 h+=events.length?'<div class="rows">'+events.map(function(e){return '<div class="row"><div><strong>'+esc(String(e.eventType||'Event').replace(/_/g,' '))+'</strong><p>'+esc(date(e.date))+(e.time?' · '+esc(appointmentTime(e)):'')+' · '+esc(e.classification||'Confirmed')+'</p><p>'+esc(e.verifierOffice||'')+'</p></div></div>';}).join('')+'</div>':'<p>No confirmed events saved.</p>';
 h+='<h2>Saved tasks</h2><div class="rows">';
 Object.values(state.items||{}).forEach(function(it){if(it.kind==='marker')return;h+='<div class="row"><div><strong>'+esc(it.label||it.title||it.id)+'</strong><p>'+esc(it.status||'open')+'</p>'+(it.brief?'<p>'+esc(it.brief)+'</p>':'')+'</div></div>';});
 return h+'</div>'+support+'</section>';
};
async function recover(){
 isolateStorage();
 if(!global.claude||!global.claude.use)throw Error('SAVED_PLAN_UNAVAILABLE');
 var db=await global.claude.use('db');if(!db)throw Error('SAVED_PLAN_UNAVAILABLE');
 var names=['profile','seeded','settings','ledger','install','ides','reset'];
 var docs=await Promise.all(names.map(function(k){return db.doc('meta/'+k).get();}));
 if(docs.some(function(d){return d.metadata?.fromCache||d.metadata?.hasPendingWrites;}))throw Error('SAVED_PLAN_UNAVAILABLE');
 var state={};docs.forEach(function(d,i){state[names[i]]=d.exists?d.data():null;});
 if(!state.seeded||!state.profile?.path||!state.profile.grade||state.reset)throw Error('SAVED_PLAN_UNAVAILABLE');
 names=['items','loes','contacts','blocks','conditions','claim','links','inbox'];
 var collections=await Promise.all(names.map(function(k){return db.collection(k).get();}));
 collections.forEach(function(s,i){
  if(s.metadata?.fromCache||s.metadata?.hasPendingWrites||s.docs.some(function(d){return d.metadata?.fromCache||d.metadata?.hasPendingWrites;}))throw Error('SAVED_PLAN_UNAVAILABLE');
  var rows=s.docs.map(function(d){return Object.assign({id:d.id},d.data());});
  state[names[i]]=['items','claim'].includes(names[i])?Object.fromEntries(rows.map(function(r){return[r.id,r];})):rows;
 });
 state.settings=state.settings||{eas:null,sbStart:null,sbEnd:null,planSet:null};
 state.ledger=state.ledger||{balance:null,asOf:null,accrualPerMonth:2.5};state.installLoaded=true;
 var seed={pack:state.seeded.pack||'usmc',settings:state.settings,ledger:state.ledger,items:Object.values(state.items),loes:state.loes,contacts:state.contacts,blocks:[],conditions:[],claim:Object.assign({benefits:{rows:[]}},state.claim)};
 api.recovery={state:state};return JSON.stringify(seed);
}
api.prepare=function(start){
 if(api.value)return false;
 var node=document.getElementById('seed'),task;
 try{
  var payload=JSON.parse(node.textContent);
  if(payload&&!payload.encoding&&Array.isArray(payload.items)&&Array.isArray(payload.loes)&&payload.claim){api.value=payload;return false;}
  task=global.MusterOutIDES.loadText(payload);
 }catch(_){task=Promise.reject(Error('SEED_DATA_UNAVAILABLE'));}
 task.then(function(text){
  var value=JSON.parse(text);if(!Array.isArray(value.items)||!Array.isArray(value.loes)||!value.claim)throw Error('SEED_DATA_UNAVAILABLE');
  api.value=value;return text;
 }).catch(recover).then(function(text){if(!api.value)api.value=JSON.parse(text);if(node)node.textContent=text;start();}).catch(notice);
 return true;
};
global.MusterOutBoardData=api;
})(window);
