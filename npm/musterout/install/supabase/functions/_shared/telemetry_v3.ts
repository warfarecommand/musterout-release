import './registration_v3.js';
const contract = (globalThis as any).MusterOutRG3;
export async function telemetryV3(req: Request, raw: string, deps: {env:(name:string)=>string|undefined;db:any;now?:()=>number}, json:(status:number,body:unknown)=>Response):Promise<Response>{
 if(req.method!=='POST')return json(405,{ok:false,error:'method'});
 if(!/^application\/json(?:\s*;|$)/i.test(req.headers.get('content-type')||''))return json(400,{ok:false,error:'content_type'});
 let record:any;
 try{record=contract.parse(raw);}catch{return json(400,{ok:false,error:'bad_input'});}
 if(deps.env('RG3_ENABLED')!=='true'&&record.kind!=='delete')return json(503,{ok:false,error:'inactive'});
 if(new TextEncoder().encode(raw).length>(record.kind==='usage'?4096:1024))return json(413,{ok:false,error:'too_large'});
 if(record.kind==='usage'&&deps.env('RG3_USAGE_ENABLED')!=='true')return json(503,{ok:false,error:'usage_inactive'});
 const now=deps.now?.()??Date.now();
 if(record.kind==='registration'&&record.setup_date!==null&&Date.parse(record.setup_date)>Math.floor(now/86400000)*86400000+86400000)return json(400,{ok:false,error:'future_day'});
 const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode('musterout-rg3:'+record.board_key));
 const hash=Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,'0')).join('');
 const payload={...record};delete payload.board_key;
 // No proxy/IP header is trusted by this deployment. Unknown sources are
 // quarantined. Admission uses fixed global state and the bounded key registry.
 const result=await deps.db.rpc('rg3_ingest',{p_key_hash:hash,p_record:payload});
 if(result.error||!result.data||typeof result.data.status!=='string')return json(503,{ok:false,error:'unavailable'});
 const status=result.data.status;
 if(['recorded','duplicate','deleted'].includes(status))return json(200,{ok:true,status});
 return json(status==='conflict'?409:['revoked','expired'].includes(status)?410:status==='missing'?409:status==='budget'?429:503,{ok:false,error:status});
}
