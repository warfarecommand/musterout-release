import {createHandler} from './index.ts';
const T=(globalThis as any).MusterOutTelemetry;
const assert=(x:unknown,message='assertion failed')=>{if(!x)throw Error(message);};
const equal=(a:unknown,b:unknown)=>assert(JSON.stringify(a)===JSON.stringify(b));
const key=await crypto.subtle.generateKey('Ed25519',true,['sign','verify']) as CryptoKeyPair;
const jwk=JSON.stringify(await crypto.subtle.exportKey('jwk',key.privateKey));
const pub=btoa(String.fromCharCode(...new Uint8Array(await crypto.subtle.exportKey('raw',key.publicKey))));
function install(){return {schema_version:2,kind:'install',product:'musterout',record_id:'1'.repeat(32),install_id:'2'.repeat(32),version:'0.2.9',channel:'chat',device:'iphone',surface:'ios_app',status:'complete',path:'eas',grade:'e67',eas_month:null,base:'us_east',steps_completed:[...T.STEPS],failed_step:null,error_class:'none',consent_schema:'tel1-v2'};}
function request(records=[install()]){return {schema_version:2,records,access:{registration_nonce:'3'.repeat(64)}};}
function fixture(overrides:Record<string,string|undefined>={}){
 const calls:any[]=[];let reject='';
 const env:Record<string,string|undefined>={TELEMETRY_V2_ENABLED:'true',TELEMETRY_IP_SALT:'synthetic-address-salt',TELEMETRY_CLIENT_IP_HEADER:'x-real-ip',TELEMETRY_ADMISSION_SECRET:'synthetic-admission-key',TELEMETRY_RECEIPT_KEY_ID:'test',TELEMETRY_RECEIPT_PRIVATE_JWK:jwk,...overrides};
 const db={from(){throw Error('v2 touched a legacy table');},async rpc(name:string,args:any){calls.push({name,args});if(reject)return {data:{ok:false,error:reject}};
  if(name==='telemetry_delete_install')return {data:{ok:true,repeat:false,install_id:args.p_install_id,deleted:Object.fromEntries(T.DELETE_TABLES.map((k:string)=>[k,0]))}};
  if(name==='telemetry_enroll_issue')return {data:{ok:true,expires_at:'2026-10-16T00:00:00.123456Z'}};
  equal(name,'telemetry_admit');const complete=args.p_records.some((r:any)=>r.record.kind==='install'&&r.record.status==='complete');
  return {data:{ok:true,duplicate:false,install_id:args.p_install_id,install_status:complete?'complete':'unchanged',received_at:'2026-10-15T00:00:00.123456Z',records:args.p_records.map((r:any)=>({record_id:r.record.record_id,kind:r.record.kind,payload_sha256:r.payload_sha256,status:'recorded'})),...(complete?{capability_sha256:args.p_capability_hash}:{})}};
 }};
 const handler=createHandler({db,env:n=>env[n]});
 const send=(body:unknown,ip='192.0.2.1')=>handler(new Request('https://test.invalid/ingest',{method:'POST',headers:{origin:'https://musterout.warfarecommand.com','x-real-ip':ip},body:typeof body==='string'?body:T.canonical(body)}));
 return {calls,handler,send,reject:(s:string)=>{reject=s;}};
}
Deno.test('v2 nonce receipt verifies exact bytes and capability; never legacy budget',async()=>{
 const f=fixture(),r=request(),raw=T.canonical(r),response=await f.send(raw),out=await response.json();equal(response.status,200);
 await T.verify(out,r,{test:pub});equal(f.calls.length,1);equal(f.calls[0].name,'telemetry_admit');
 equal(f.calls[0].args.p_records[0].payload_sha256,await T.sha(T.canonical(r.records[0])));
 equal(f.calls[0].args.p_request_sha256,await T.sha(raw));assert(!JSON.stringify(f.calls).includes(r.access.registration_nonce));assert(!JSON.stringify(f.calls).includes('192.0.2.1'));
 const second=await (await f.send(raw)).json();equal(out.access,second.access);
 for(const mutate of [(x:any)=>x.receipt.payload.install_id='4'.repeat(32),(x:any)=>x.receipt.payload.records[0].payload_sha256='0'.repeat(64),(x:any)=>x.access.capability='0'.repeat(64),(x:any)=>x.receipt.signature='AAAA']){let bad=structuredClone(out);mutate(bad);let failed=false;try{await T.verify(bad,r,{test:pub});}catch{failed=true;}assert(failed,'forged receipt accepted');}
});
Deno.test('v2 disabled/missing signing or address config fails before admission',async()=>{
 for(const [k,v] of [['TELEMETRY_V2_ENABLED',undefined],['TELEMETRY_RECEIPT_PRIVATE_JWK','bad'],['TELEMETRY_ADMISSION_SECRET',undefined],['TELEMETRY_CLIENT_IP_HEADER',undefined]] as const){const f=fixture({[k]:v});equal((await f.send(request())).status,503);equal(f.calls.length,0);}
 for(const ip of ['192.0.2.1, 198.51.100.2','999.0.0.1','01.2.3.4','host.invalid','fe80::1%en0']){const f=fixture();equal((await f.send(request(),ip)).status,503);equal(f.calls.length,0);}
});
Deno.test('v2 established lane works without the anonymous address lane and honors RPC errors',async()=>{
 const r:any={schema_version:2,records:[{...install(),kind:'usage'}],access:{capability:'4'.repeat(64)}};r.records=[{schema_version:2,kind:'usage',product:'musterout',record_id:'5'.repeat(32),install_id:'2'.repeat(32),version:'0.2.9',trigger:'weekly',weeks_active:0,late_count:0,buckets:[]}];
 const f=fixture({TELEMETRY_CLIENT_IP_HEADER:undefined});equal((await f.send(r)).status,200);equal(f.calls[0].args.p_address_hash,null);equal(f.calls[0].args.p_nonce_hash,null);
 for(const [error,code] of [['capacity',503],['age',422],['conflict',409],['access_denied',403],['quota',429],['expired',410]]){f.reject(error as string);equal((await f.send(r)).status,code);}
});
Deno.test('v2 every extra field and invalid scalar rejects before database; no person data',async()=>{
 const base=request();
 for(const key of ['name','email','board_url','notes','question','answer','unit','date','__proto__']){
  for(const path of ['envelope','access','record']){const f=fixture(),v:any=structuredClone(base);const target=path==='envelope'?v:path==='access'?v.access:v.records[0];Object.defineProperty(target,key,{value:'Private Person 2026-10-14',enumerable:true});equal((await f.send(v)).status,400);equal(f.calls.length,0);}
 }
 for(const [key,values] of Object.entries({base:['My unit',null],eas_month:['2027-10-14','2027-13'],schema_version:[true,'2',1],grade:['e6'],version:['01.2.9'],steps_completed:[['consent','consent']],failed_step:['notes'],device:['iPhone serial 123']}))for(const value of values){const f=fixture(),r:any=request();r.records[0][key]=value;equal((await f.send(r)).status,400);equal(f.calls.length,0);}
 for(let n=0;n<100;n++){const f=fixture(),v:any=request();v.records[0]['private_'+n]=T.random();equal((await f.send(v)).status,400);equal(f.calls.length,0);}
 for(const raw of ['{"schema_version":2,"schema_version":2,"records":[],"access":{}}',T.canonical(base).replace('"base":"us_east"','"base":"us_east","base":"us_west"')]){const f=fixture();equal((await f.send(raw)).status,400);equal(f.calls.length,0);}
});
Deno.test('v2 bounded nested counters and optional answers contain only approved values',()=>{
 let b=T.emptyBucket(0);assert(T.bucket(b));
 for(const group of ['tab_opens','done_by_category','errors'])for(const key of Object.keys(b[group]))for(const bad of [true,-1,10001,1.2,'1',null]){let x=structuredClone(b);x[group][key]=bad;assert(!T.bucket(x));}
 for(let score=-1;score<=11;score++){let r={...install(),kind:'recommend'};for(const k of Object.keys(r))if(!['schema_version','kind','product','record_id','install_id','version'].includes(k))delete (r as any)[k];Object.assign(r,{context:'setup',week_index:0,score});equal(T.record(r),score>=0&&score<=10);}
});
Deno.test('v2 recommendation stages accept first impression, after use, and old clients separately',async()=>{
 const common={schema_version:2,kind:'recommend',product:'musterout',record_id:'5'.repeat(32),install_id:'2'.repeat(32),version:'0.2.15'};
 for(const [context,week] of [['setup',0],['after_use',0],['after_use',1],['after_use',104],['week4',4],['week4',104]] as const){
  const record={...common,context,week_index:week,score:0},request={schema_version:2,records:[record],access:{capability:'4'.repeat(64)}},f=fixture();
  equal((await f.send(request)).status,200);equal(T.canonical(f.calls[0].args.p_records[0].record),T.canonical(record));await T.verify(await (await f.send(request)).json(),request,{test:pub});
 }
 for(const patch of [{context:'first_impression'},{context:'unknown'},{context:'week4',week_index:0},{context:'setup',week_index:1},{week_index:-1},{week_index:105},{week_index:1.5},{week_index:'0'},{score:11},{score:-1},{score:0.5},{score:null},{score:true},{score:'9'},{stage:'after_use'},{opened_days:['2026-10-15']}]){
  const f=fixture(),record={...common,context:'after_use',week_index:0,score:10,...patch};equal((await f.send({schema_version:2,records:[record],access:{capability:'4'.repeat(64)}})).status,400);equal(f.calls.length,0);
 }
 const f=fixture();equal((await f.send({schema_version:2,records:[install(),{...common,context:'after_use',week_index:0,score:10}],access:{registration_nonce:'3'.repeat(64)}})).status,400);equal(f.calls.length,0);
});
Deno.test('v2 delete signed receipt authenticates the complete 14-class receipt',async()=>{
 const f=fixture(),r={schema_version:2,kind:'delete',install_id:'2'.repeat(32),access:{capability:'4'.repeat(64)}};
 const response=await f.send(r),data=await response.json();equal(response.status,200);equal(f.calls[0].name,'telemetry_delete_install');await T.verifyDelete(data,r,{test:pub});
 data.delete_receipt.payload.deleted.telemetry_admissions=1;let rejected=false;try{await T.verifyDelete(data,r,{test:pub});}catch{rejected=true;}assert(rejected);
});
Deno.test('v2 every allowed install enum and all optional answer shapes; reject text at every nested level',async()=>{
 for(const [field,values] of Object.entries({channel:['chat','laptop'],device:['iphone','ipad','android','desktop','other','unknown'],surface:['web','ios_app','android_app','desktop_app','code','unknown'],path:['eas','resign','retire'],grade:['e15','e67','e89','o14','o5','wo13','cwo45'],base:T.BASES}))for(const value of values){const r:any=install();r[field]=value;assert(T.record(r),field+' '+value);}
 const common={schema_version:2,product:'musterout',install_id:'2'.repeat(32),version:'0.2.9'};
 const examples:any[]=[{...common,record_id:T.random(),kind:'usage',trigger:'update',weeks_active:1,late_count:0,buckets:[T.emptyBucket(0)]},{...common,record_id:T.random(),kind:'outcome',week_index:0,trs_done:true,skillbridge:false,va_claim_before_separation:null,separation_counseling_done:null},{...common,record_id:T.random(),kind:'hosted_demand',week_index:4,would_use:'yes',pay_monthly:'zero'},{...common,record_id:T.random(),kind:'recommend',context:'week4',week_index:4,score:0}];
 for(const record of examples){assert(T.record(record));for(const key of ['email','name','notes','question','answer','board_url','medical','__proto__']){
  const r=structuredClone(record);Object.defineProperty(r,key,{value:'private@invalid.example',enumerable:true});const f=fixture();equal((await f.send({schema_version:2,records:[r],access:{capability:'4'.repeat(64)}})).status,400);equal(f.calls.length,0);
 }}
 for(const group of [null,'tab_opens','done_by_category','errors']){const r=structuredClone(examples[0]),target=group?r.buckets[0][group]:r.buckets[0];target.notes='Private text';const f=fixture();equal((await f.send({schema_version:2,records:[r],access:{capability:'4'.repeat(64)}})).status,400);equal(f.calls.length,0);}
 for(const value of [null,false,true])for(const field of T.OUTCOMES){const r=structuredClone(examples[1]);r[field]=value;assert(T.record(r));}
 for(const score of [-1,11,0.5,'0',true,null]){const r=structuredClone(examples[3]);r.score=score;assert(!T.record(r));}
 for(const field of T.OUTCOMES){const r=structuredClone(examples[1]);r[field]='yes';assert(!T.record(r));}
 for(let n=0;n<100;n++){const r=structuredClone(examples[n%examples.length]);r.record_id=T.random();assert(T.envelope({schema_version:2,records:[r],access:{capability:'4'.repeat(64)}}));equal(T.canonical(T.parse(T.canonical(r)).body),T.canonical(r));}
});

Deno.test('enroll: exact request, activation and configured verified address before any RPC',async()=>{
 const r={schema_version:2,kind:'enroll'};assert(T.enrollRequest(r));
 for(const body of [{...r,records:[]},{...r,email:'private@example.invalid'},{...r,kind:'enroll',access:{}},{kind:'enroll'},{...r,schema_version:'2'}]){const f=fixture();equal((await f.send(body)).status,400);equal(f.calls.length,0);}
 for(const settings of [{TELEMETRY_V2_ENABLED:undefined},{TELEMETRY_CLIENT_IP_HEADER:undefined},{TELEMETRY_IP_SALT:undefined}]){const f=fixture(settings);equal((await f.send(r)).status,503);equal(f.calls.length,0);}
 for(const ip of ['999.1.1.1','192.0.2.1, 198.51.100.1']){const f=fixture();equal((await f.send(r,ip)).status,503);equal(f.calls.length,0);}
 const f=fixture();equal((await f.send('{"schema_version":2,"kind":"enroll","kind":"enroll"}')).status,400);equal(f.calls.length,0);
});
Deno.test('enroll: random 32-byte server proof, no-store, only hashes in RPC and no logging',async()=>{
 const f=fixture({TELEMETRY_RECEIPT_PRIVATE_JWK:undefined,TELEMETRY_ADMISSION_SECRET:undefined}),logs:any[]=[],original=console.log;console.log=(...a:any[])=>{logs.push(a);};let response:Response,data:any;
 try{response=await f.send({schema_version:2,kind:'enroll'});data=await response.json();}finally{console.log=original;}
 equal(response!.status,200);equal(response!.headers.get('cache-control'),'no-store');assert(T.issued(data));equal(f.calls[0].name,'telemetry_enroll_issue');equal(Object.keys(f.calls[0].args).sort(),['p_address_hash','p_nonce_hash']);equal(f.calls[0].args.p_nonce_hash,await T.sha(data.registration_nonce));assert(!JSON.stringify(f.calls).includes(data.registration_nonce));assert(!JSON.stringify(logs).includes(data.registration_nonce));assert(!JSON.stringify(f.calls).includes('192.0.2.1'));
 const again=await (await f.send({schema_version:2,kind:'enroll'})).json();assert(data.registration_nonce!==again.registration_nonce);
});
Deno.test('enroll: issuance budget maps to 429, bad input 400, repeated conflict stops after one redraw',async()=>{
 for(const [error,code,count] of [['budget_exceeded',429,1],['bad_input',400,1],['conflict',503,2],['unknown',503,1]]){const f=fixture();f.reject(error as string);const response=await f.send({schema_version:2,kind:'enroll'});equal(response.status,code);equal(f.calls.length,count);if(count===2)assert(f.calls[0].args.p_nonce_hash!==f.calls[1].args.p_nonce_hash);}
 const calls:any[]=[],handler=createHandler({env:n=>({TELEMETRY_V2_ENABLED:'true',TELEMETRY_IP_SALT:'synthetic',TELEMETRY_CLIENT_IP_HEADER:'x-real-ip'})[n],db:{async rpc(name:any,args:any){calls.push({name,args});return {data:calls.length===1?{ok:false,error:'conflict'}:{ok:true,expires_at:'2026-10-16T00:00:00Z'}};}}});const response=await handler(new Request('https://test.invalid',{method:'POST',headers:{'x-real-ip':'192.0.2.1'},body:'{"schema_version":2,"kind":"enroll"}'}));equal(response.status,200);equal(calls.length,2);const data=await response.json();equal(calls[1].args.p_nonce_hash,await T.sha(data.registration_nonce));
});
Deno.test('enroll: malformed RPC success and retired admission budget code fail closed',async()=>{
 const f=fixture();f.reject('budget_exceeded');equal((await f.send(request())).status,503);
 for(const data of [null,{ok:true},{ok:true,expires_at:'private'},{ok:true,expires_at:'2026-02-31T00:00:00Z'},{ok:true,expires_at:'2026-10-16T00:00:00Z',registration_nonce:'extra'}]){const handler=createHandler({env:n=>({TELEMETRY_V2_ENABLED:'true',TELEMETRY_IP_SALT:'synthetic',TELEMETRY_CLIENT_IP_HEADER:'x-real-ip'})[n],db:{async rpc(){return {data};}}});equal((await handler(new Request('https://test.invalid',{method:'POST',headers:{'x-real-ip':'192.0.2.1'},body:'{"schema_version":2,"kind":"enroll"}'}))).status,503);}
});
