/* Shared, dependency-free TEL1 contract for browser, ingest, and offline tests. */
(function(root){
 'use strict';
 const BASES=['us_west','us_central','us_east','hawaii','japan','other_overseas','other_us','not_on_installation'];
 const BASE_LABELS=['US West','US Central','US East','Hawaii','Japan','Other overseas','Other US location','Not on an installation'];
 const STEPS=['consent','release_verified','published','intake_confirmed','plan_verified','record_requested'];
 const TABS=['today','plan','dates','claim','more'], CATEGORIES=['sep','sb','va','dap','leave','fam','cmd','other'];
 const ERRORS=['save','update','feed','storage','sample','permission','validation','other'];
 const OUTCOMES=['trs_done','skillbridge','va_claim_before_separation','separation_counseling_done'];
 const COMMON=['schema_version','kind','product','record_id','install_id','version'];
 const CONSENT='Muster Out counts installs, usage, and progress milestones. It cannot read your plan.';
 const LICENSE="I have read and agree to the Warfare Command Individual Use License 1.0. I am acting in my individual capacity and independently choose this setup for permitted Individual Use. I am not setting up the Work to fulfill an organization's software requirement, deployment, or client-service delivery. I understand that this agreement does not bind my employer or the government.";
 const object=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
 const keys=(v,k)=>object(v)&&Object.keys(v).sort().join('|')===[...k].sort().join('|');
 const integer=(v,lo=0,hi=10000)=>Number.isSafeInteger(v)&&v>=lo&&v<=hi;
 const member=(v,k)=>typeof v==='string'&&k.includes(v);
 const hex=(v,n)=>typeof v==='string'&&new RegExp('^[a-f0-9]{'+n+'}$').test(v);
 const id=v=>typeof v==='string'&&/^[a-f0-9]{16,32}$/.test(v);
 const version=v=>typeof v==='string'&&v.length<=32&&/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.test(v);
 const canonical=v=>JSON.stringify(v,(_,x)=>object(x)?Object.fromEntries(Object.keys(x).sort().map(k=>[k,x[k]])):x);
 const bytes=v=>new TextEncoder().encode(v);
 const byteLength=v=>bytes(v).length;
 const random=(n=16)=>Array.from(crypto.getRandomValues(new Uint8Array(n)),b=>b.toString(16).padStart(2,'0')).join('');
 const sha=async s=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes(s))),b=>b.toString(16).padStart(2,'0')).join('');
 const counts=(v,k)=>keys(v,k)&&k.every(key=>integer(v[key]));
 function bucket(v){return keys(v,['bucket_id','week_index','revision','opens','tab_opens','done_by_category','ask_questions','errors'])&&hex(v.bucket_id,32)&&integer(v.week_index,0,104)&&integer(v.revision,1)&&integer(v.opens)&&integer(v.ask_questions)&&counts(v.tab_opens,TABS)&&counts(v.done_by_category,CATEGORIES)&&counts(v.errors,ERRORS);}
 function record(r){
  if(!object(r)||r.schema_version!==2||r.product!=='musterout'||!hex(r.record_id,32)||!id(r.install_id)||!version(r.version))return false;
  const exact=k=>keys(r,COMMON.concat(k));
  if(r.kind==='install'){
   if(!exact(['channel','device','surface','status','path','grade','eas_month','base','steps_completed','failed_step','error_class','consent_schema']))return false;
   if(!member(r.channel,['chat','laptop'])||!member(r.device,['iphone','ipad','android','desktop','other','unknown'])||!member(r.surface,['web','ios_app','android_app','desktop_app','code','unknown'])||!member(r.status,['in_progress','failed','complete'])||!(r.path===null||member(r.path,['eas','resign','retire']))||!(r.grade===null||member(r.grade,['e15','e67','e89','o14','o5','wo13','cwo45']))||!(r.base===null||member(r.base,BASES))||!(r.eas_month===null||(typeof r.eas_month==='string'&&/^\d{4}-(0[1-9]|1[0-2])$/.test(r.eas_month)))||!(r.failed_step===null||member(r.failed_step,STEPS.slice(1)))||!member(r.error_class,['none','network','unavailable','permission','validation','save','verify','rate_limited','other'])||r.consent_schema!=='tel1-v2')return false;
   const s=r.steps_completed;if(!Array.isArray(s)||s.length<1||s.length>6||s[0]!=='consent'||s.some((x,i)=>!member(x,STEPS)||(i>0&&STEPS.indexOf(x)<=STEPS.indexOf(s[i-1]))))return false;
   return r.status==='complete'?s.length===6&&r.path!==null&&r.grade!==null&&r.base!==null&&r.failed_step===null&&r.error_class==='none':r.status==='failed'?r.failed_step!==null:r.failed_step===null;
  }
  if(r.kind==='usage')return exact(['trigger','weeks_active','late_count','buckets'])&&member(r.trigger,['update','weekly'])&&integer(r.weeks_active,0,105)&&integer(r.late_count)&&Array.isArray(r.buckets)&&r.buckets.length<=26&&r.buckets.every(bucket)&&new Set(r.buckets.map(b=>b.bucket_id)).size===r.buckets.length;
  if(r.kind==='outcome')return exact(['week_index',...OUTCOMES])&&integer(r.week_index,0,104)&&OUTCOMES.every(k=>r[k]===null||typeof r[k]==='boolean');
  if(r.kind==='hosted_demand')return exact(['week_index','would_use','pay_monthly'])&&integer(r.week_index,4,104)&&member(r.would_use,['yes','no','unsure'])&&member(r.pay_monthly,['zero','under_5','5_to_9','10_to_19','20_to_29','30_or_more','unsure']);
  // setup is the first impression; week4 remains the legacy pricing-survey score.
  if(r.kind==='recommend')return exact(['context','week_index','score'])&&integer(r.score,0,10)&&((r.context==='setup'&&r.week_index===0)||(r.context==='after_use'&&integer(r.week_index,0,104))||(r.context==='week4'&&integer(r.week_index,4,104)));
  return false;
 }
 function envelope(v){
  if(!keys(v,['schema_version','records','access'])||v.schema_version!==2||!Array.isArray(v.records)||v.records.length<1||v.records.length>32||!v.records.every(record)||new Set(v.records.map(r=>r.record_id)).size!==v.records.length||new Set(v.records.map(r=>r.install_id)).size!==1)return false;
  if(keys(v.access,['registration_nonce'])&&hex(v.access.registration_nonce,64))return v.records.some(r=>r.kind==='install')&&v.records.filter(r=>r.kind==='install'&&r.status==='complete').length<=1&&v.records.every(r=>r.kind==='install'||(r.kind==='recommend'&&r.context==='setup'));
  return keys(v.access,['capability'])&&hex(v.access.capability,64)&&v.records.every(r=>r.kind!=='install')&&v.records.reduce((n,r)=>n+(r.buckets?.length||0),0)<=32;
 }
 const enrollRequest=v=>keys(v,['schema_version','kind'])&&v.schema_version===2&&v.kind==='enroll';
 const enrollmentDraft=v=>keys(v,['schema_version','records','access'])&&keys(v.access,[])&&envelope({...v,access:{registration_nonce:'0'.repeat(64)}});
 const timestamp=v=>typeof v==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z$/.test(v)&&Number.isFinite(Date.parse(v))&&new Date(Date.parse(v)).toISOString().slice(0,19)===v.slice(0,19);
 const issued=v=>keys(v,['ok','registration_nonce','expires_at'])&&v.ok===true&&hex(v.registration_nonce,64)&&timestamp(v.expires_at);
 const registrationCode=v=>keys(v,['schema_version','kind','previous','request','expires_at'])&&v.schema_version===2&&v.kind==='enrollment'&&(enrollmentDraft(v.previous)||envelope(v.previous)&&hex(v.previous.access.registration_nonce,64))&&envelope(v.request)&&hex(v.request.access.registration_nonce,64)&&timestamp(v.expires_at)&&byteLength(canonical(v))<=40000;
 // Scan before JSON.parse, rejecting duplicate keys at every depth, and retain
 // each record's exact lexical bytes for the receipt digest. No eval/reviver.
 function parse(text,limit=20000){
  if(typeof text!=='string'||byteLength(text)>limit||!integer(limit,1,40000))throw Error('too_large');
  let i=0;const raws=[];const ws=()=>{while(/[\t\n\r ]/.test(text[i]||'x'))i++;};
  function string(){let start=i++;while(i<text.length){let c=text[i++];if(c==='"')return JSON.parse(text.slice(start,i));if(c==='\\')i++;}throw Error('bad_json');}
  function value(path,depth){if(depth>16)throw Error('bad_json');ws();const start=i,c=text[i];
   if(c==='{'){i++;ws();const seen=new Set();if(text[i]!=='}')while(true){ws();if(text[i]!=='"')throw Error('bad_json');const k=string();if(seen.has(k))throw Error('duplicate_key');seen.add(k);ws();if(text[i++]!==':')throw Error('bad_json');value(path.concat(k),depth+1);ws();if(text[i]!==',')break;i++;}if(text[i++]!=='}')throw Error('bad_json');}
   else if(c==='['){i++;ws();let n=0;if(text[i]!==']')while(true){value(path.concat(n++),depth+1);ws();if(text[i]!==',')break;i++;}if(text[i++]!==']')throw Error('bad_json');}
   else if(c==='"')string();else{const m=/^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/.exec(text.slice(i));if(!m)throw Error('bad_json');i+=m[0].length;}
   if(path.length===2&&path[0]==='records')raws[path[1]]=text.slice(start,i);
  }
  value([],0);ws();if(i!==text.length)throw Error('bad_json');return {body:JSON.parse(text),recordBytes:raws};
 }
 function decode64(s){if(typeof s!=='string'||s.length>30000||!/^[A-Za-z0-9_-]+$/.test(s))throw Error('bad_input');return new TextDecoder('utf-8',{fatal:true}).decode(Uint8Array.from(atob(s.replace(/-/g,'+').replace(/_/g,'/')),c=>c.charCodeAt(0)));}
 function encode64(s){return btoa(String.fromCharCode(...bytes(s))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');}
 function emptyBucket(week){return {bucket_id:random(),week_index:week,revision:1,opens:0,tab_opens:Object.fromEntries(TABS.map(k=>[k,0])),done_by_category:Object.fromEntries(CATEGORIES.map(k=>[k,0])),ask_questions:0,errors:Object.fromEntries(ERRORS.map(k=>[k,0]))};}
 async function verify(result,request,receiptKeys){
  if(byteLength(canonical(result))>8192||!envelope(request)||!keys(result,result.access?['ok','receipt','access']:['ok','receipt'])||result.ok!==true||!keys(result.receipt,['key_id','payload','signature']))throw Error('receipt');
  const {key_id,payload:p,signature}=result.receipt,complete=p?.install_status==='complete';
  if(!keys(p,complete?['schema_version','install_id','records','install_status','received_at','capability_sha256']:['schema_version','install_id','records','install_status','received_at'])||p.schema_version!==2||p.install_id!==request.records[0].install_id||!member(p.install_status,['in_progress','failed','complete','unchanged'])||typeof p.received_at!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z$/.test(p.received_at)||!Number.isFinite(Date.parse(p.received_at))||new Date(Date.parse(p.received_at)).toISOString().slice(0,19)!==p.received_at.slice(0,19)||!Array.isArray(p.records)||p.records.length!==request.records.length)throw Error('receipt');
  for(let n=0;n<p.records.length;n++){let a=p.records[n],r=request.records[n];if(!keys(a,['record_id','kind','payload_sha256','status'])||a.record_id!==r.record_id||a.kind!==r.kind||!member(a.status,['recorded','duplicate'])||a.payload_sha256!==await sha(canonical(r)))throw Error('receipt');}
  if(complete){if(!request.records.some(r=>r.kind==='install'&&r.status==='complete')||!keys(result.access,['capability'])||!hex(result.access.capability,64)||await sha(result.access.capability)!==p.capability_sha256)throw Error('receipt');}else if(result.access)throw Error('receipt');
  if(!Object.hasOwn(receiptKeys||{},key_id)||typeof signature!=='string')throw Error('receipt');
  const decode=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
  const key=await crypto.subtle.importKey('raw',decode(receiptKeys[key_id]),{name:'Ed25519'},false,['verify']);
  if(!await crypto.subtle.verify('Ed25519',key,decode(signature),bytes('musterout-telemetry-receipt-v2\n'+canonical(p))))throw Error('receipt');return p;
 }
 const DELETE_TABLES=['telemetry_usage_buckets','telemetry_chat_runs','telemetry_outcomes','telemetry_hosted_demand','telemetry_recommend','telemetry_install_events','telemetry_request_receipts','telemetry_rate','setup_pings','install_registrations','feedback_reports','usage_weeks','learn_install_cohorts','telemetry_admissions'];
 async function verifyDelete(result,request,receiptKeys){
  if(!keys(result,['ok','delete_receipt'])||result.ok!==true||!keys(result.delete_receipt,['key_id','payload','signature']))throw Error('deletion_receipt');
  const {key_id,payload:p,signature}=result.delete_receipt;
  if(!keys(p,['schema_version','kind','install_id','deleted','repeat','proof_sha256'])||p.schema_version!==2||p.kind!=='delete'||p.install_id!==request.install_id||typeof p.repeat!=='boolean'||!keys(p.deleted,DELETE_TABLES)||!Object.values(p.deleted).every(n=>integer(n,0,Number.MAX_SAFE_INTEGER))||p.proof_sha256!==await sha(request.access.capability||request.access.registration_nonce)||!Object.hasOwn(receiptKeys||{},key_id))throw Error('deletion_receipt');
  const decode=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0)),key=await crypto.subtle.importKey('raw',decode(receiptKeys[key_id]),{name:'Ed25519'},false,['verify']);
  if(!await crypto.subtle.verify('Ed25519',key,decode(signature),bytes('musterout-telemetry-delete-v2\n'+canonical(p))))throw Error('deletion_receipt');return p;
 }
 root.MusterOutTelemetry=Object.freeze({BASES,BASE_LABELS,STEPS,TABS,CATEGORIES,ERRORS,OUTCOMES,DELETE_TABLES,CONSENT,LICENSE,object,keys,integer,hex,id,version,canonical,bytes,byteLength,random,sha,bucket,record,envelope,enrollRequest,enrollmentDraft,timestamp,issued,registrationCode,parse,decode64,encode64,emptyBucket,verify,verifyDelete});
})(globalThis);
