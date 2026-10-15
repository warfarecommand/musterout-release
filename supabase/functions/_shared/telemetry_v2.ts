import './telemetry_contract.js';
const T = (globalThis as any).MusterOutTelemetry;
const status: Record<string,number>={bad_input:400,access_denied:403,access_conflict:409,capability_required:403,conflict:409,expired:410,age:422,rate_limited:429,quota:429,budget_exceeded:429,capacity:503};
function address(req:Request,env:(name:string)=>string|undefined):string|null {
 // Trust only the single header explicitly configured after gateway validation.
 const header=env('TELEMETRY_CLIENT_IP_HEADER');if(!header||!['cf-connecting-ip','x-real-ip','x-forwarded-for'].includes(header))return null;
 const raw=req.headers.get(header)?.trim();if(!raw||raw.includes(',')||raw.includes('%'))return null;
 if(/^\d{1,3}(\.\d{1,3}){3}$/.test(raw)){const p=raw.split('.');return p.every(x=>Number(x)<=255&&String(Number(x))===x)?p.join('.'):null;}
 try {if(!/^[a-fA-F0-9:]+$/.test(raw)||!raw.includes(':'))return null;return new URL('https://['+raw+']/').hostname.toLowerCase();}catch{return null;}
}
export async function telemetryV2(req:Request,text:string,deps:{env:(name:string)=>string|undefined;db:any},json:(status:number,body:unknown)=>Response):Promise<Response>{
 if(req.method!=='POST')return json(405,{ok:false,error:'method'});
 let parsed:any;try{parsed=T.parse(text);}catch{return json(400,{ok:false,error:'bad_json'});}
 const b=parsed.body,del=b?.kind==='delete',enroll=b?.kind==='enroll';
 if(enroll&&!T.enrollRequest(b))return json(400,{ok:false,error:'bad_input'});
 if(del){if(!T.keys(b,['schema_version','kind','install_id','access'])||b.schema_version!==2||!T.id(b.install_id)||!(T.keys(b.access,['capability'])&&T.hex(b.access.capability,64)||T.keys(b.access,['registration_nonce'])&&T.hex(b.access.registration_nonce,64)))return json(400,{ok:false,error:'bad_input'});}
 else if(!enroll&&!T.envelope(b))return json(400,{ok:false,error:'bad_input'});
 if(deps.env('TELEMETRY_V2_ENABLED')!=='true')return json(503,{ok:false,error:'disabled'});
 const salt=deps.env('TELEMETRY_IP_SALT'),ip=address(req,deps.env);
 const addr=salt&&ip?(await T.sha('musterout-telemetry-address-v2\n'+salt+'\n'+ip)).slice(0,24):null;
 if(enroll){
  if(!addr)return json(503,{ok:false,error:'not_configured'});
  for(let attempt=0;attempt<2;attempt++){
   const nonce=T.random(32);
   const {data,error}=await deps.db.rpc('telemetry_enroll_issue',{p_nonce_hash:await T.sha(nonce),p_address_hash:addr});
   if(error||!data||typeof data.ok!=='boolean')return json(503,{ok:false,error:'unavailable'});
   if(!data.ok){if(data.error==='conflict'&&attempt===0)continue;return json(data.error==='bad_input'?400:data.error==='budget_exceeded'?429:503,{ok:false,error:['bad_input','budget_exceeded'].includes(data.error)?data.error:'unavailable'});}
   if(!T.keys(data,['ok','expires_at'])||!T.timestamp(data.expires_at))return json(503,{ok:false,error:'unavailable'});
   return json(200,{ok:true,registration_nonce:nonce,expires_at:data.expires_at});
  }
  return json(503,{ok:false,error:'unavailable'});
 }
 const nonce=b.access.registration_nonce,access=nonce?'nonce':'capability';
 if(!addr&&(nonce||del))return json(503,{ok:false,error:'not_configured'});

 const secret=deps.env('TELEMETRY_ADMISSION_SECRET'),signing=deps.env('TELEMETRY_RECEIPT_PRIVATE_JWK'),keyId=deps.env('TELEMETRY_RECEIPT_KEY_ID');
 if((!secret&&!del)||!signing||!keyId||!/^[A-Za-z0-9_-]{1,64}$/.test(keyId))return json(503,{ok:false,error:'not_configured'});
 // Validate/import all signing configuration before the transaction can commit.
 let signingKey:CryptoKey;try{signingKey=await crypto.subtle.importKey('jwk',JSON.parse(signing),{name:'Ed25519'},false,['sign']);}catch{return json(503,{ok:false,error:'not_configured'});}
 if(del){
  const proof=await T.sha(nonce||b.access.capability);
  const {data,error}=await deps.db.rpc('telemetry_delete_install',{p_install_id:b.install_id,p_access:access,p_access_hash:proof,p_address_hash:addr});
  if(error||!data||typeof data.ok!=='boolean')return json(503,{ok:false,error:'unavailable'});
  if(!data.ok)return json(status[data.error]||503,{ok:false,error:status[data.error]?data.error:'unavailable'});
  if(data.install_id!==b.install_id||typeof data.repeat!=='boolean'||!T.keys(data.deleted,T.DELETE_TABLES)||!Object.values(data.deleted).every((n:any)=>T.integer(n,0,Number.MAX_SAFE_INTEGER)))return json(503,{ok:false,error:'unavailable'});
  const payload={schema_version:2,kind:'delete',install_id:data.install_id,deleted:data.deleted,repeat:data.repeat,proof_sha256:proof};
  const signature=btoa(String.fromCharCode(...new Uint8Array(await crypto.subtle.sign('Ed25519',signingKey,T.bytes('musterout-telemetry-delete-v2\n'+T.canonical(payload))))));
  return json(200,{ok:true,delete_receipt:{key_id:keyId,payload,signature}});
 }
 const installId=b.records[0].install_id;
 let capability=b.access.capability;
 if(nonce){const key=await crypto.subtle.importKey('raw',T.bytes(secret),{name:'HMAC',hash:'SHA-256'},false,['sign']);capability=Array.from(new Uint8Array(await crypto.subtle.sign('HMAC',key,T.bytes('musterout-telemetry-admission-v2\n'+T.canonical([installId,nonce])))),(x:any)=>x.toString(16).padStart(2,'0')).join('');}
 const entries=await Promise.all(b.records.map(async(r:any,n:number)=>({record:r,payload_sha256:await T.sha(parsed.recordBytes[n])})));
 const {data,error}=await deps.db.rpc('telemetry_admit',{p_access:access,p_install_id:installId,p_nonce_hash:nonce?await T.sha(nonce):null,p_capability_hash:await T.sha(capability),p_address_hash:addr,p_request_sha256:await T.sha(text),p_records:entries});
 if(error||!data||typeof data.ok!=='boolean')return json(503,{ok:false,error:'unavailable'});
 if(!data.ok)return json(data.error==='budget_exceeded'?503:status[data.error]||503,{ok:false,error:data.error!=='budget_exceeded'&&status[data.error]?data.error:'unavailable'});
 if(data.install_id!==installId||!Array.isArray(data.records)||data.records.length!==entries.length||typeof data.received_at!=='string')return json(503,{ok:false,error:'unavailable'});
 if(!['in_progress','failed','complete','unchanged'].includes(data.install_status)||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z$/.test(data.received_at)||!Number.isFinite(Date.parse(data.received_at)))return json(503,{ok:false,error:'unavailable'});
 for(let n=0;n<entries.length;n++){const r=data.records[n],expected=entries[n];if(!T.keys(r,['record_id','kind','payload_sha256','status'])||r.record_id!==expected.record.record_id||r.kind!==expected.record.kind||r.payload_sha256!==expected.payload_sha256||!['recorded','duplicate'].includes(r.status))return json(503,{ok:false,error:'unavailable'});}
 if((data.install_status==='complete')!==!!data.capability_sha256)return json(503,{ok:false,error:'unavailable'});
 const payload:any={schema_version:2,install_id:data.install_id,records:data.records,install_status:data.install_status,received_at:data.received_at};
 if(data.capability_sha256){if(data.capability_sha256!==await T.sha(capability))return json(503,{ok:false,error:'unavailable'});payload.capability_sha256=data.capability_sha256;}
 const signature=btoa(String.fromCharCode(...new Uint8Array(await crypto.subtle.sign('Ed25519',signingKey,T.bytes('musterout-telemetry-receipt-v2\n'+T.canonical(payload))))));
 return json(200,{ok:true,receipt:{key_id:keyId,payload,signature},...(data.capability_sha256?{access:{capability}}:{})});
}
