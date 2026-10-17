import {createHandler} from './index.ts';
const C=(globalThis as any).MusterOutRG3;
const assert=(x:unknown,label='assert')=>{if(!x)throw Error(label);};
const reg=()=>({schema_version:3,kind:'registration',board_key:'1'.repeat(32),version:'0.2.14',path:'eas',grade_band:'e67',campaign:null,setup_date:'2026-10-16'});
function fixture(enabled=true){const calls:any[]=[];let status='recorded';const h=createHandler({env:n=>n==='RG3_ENABLED'&&enabled?'true':undefined,db:{from(){throw Error('legacy table');},async rpc(name:string,args:any){calls.push({name,args});return {data:{status}};}},now:()=>Date.parse('2026-10-16T12:00:00Z')});return {calls,h,set:(s:string)=>{status=s;},send:(body:any,headers:any={},method='POST')=>h(new Request('https://example.invalid/ingest',{method,headers:{'content-type':'application/json',...headers},...(method==='POST'?{body:typeof body==='string'?body:C.canonical(body)}:{})}))};}
Deno.test('v3 off by default and invalid records never reach database',async()=>{
 const f=fixture(false);assert((await f.send(reg())).status===503);assert(f.calls.length===0);
 const yes=fixture();for(const text of [C.canonical(reg()).replace('"kind":','"kind":"registration","kind":'),C.canonical({...reg(),campaign:'arbitrary'}),C.canonical({...reg(),setup_date:'2026-02-30'}),C.canonical({...reg(),setup_date:'2026-10-18'}),C.canonical({...reg(),path:'<img onerror=alert(1)>'}),'[]','null',C.canonical({...reg(),extra:1})])assert((await yes.send(text)).status===400,text);assert(yes.calls.length===0);
});
Deno.test('v3 hash and payload privacy, verified headers cannot be spoofed',async()=>{
 const f=fixture();assert((await f.send(reg(),{'x-forwarded-for':'victim','x-real-ip':'forged','cf-connecting-ip':'forged'})).status===200);const call=f.calls[0];assert(call.name==='rg3_ingest');assert(Object.keys(call.args).sort().join()===['p_key_hash','p_record'].sort().join());assert(!JSON.stringify(call).includes(reg().board_key));assert(!JSON.stringify(call).includes('forged'));const sha=await crypto.subtle.digest('SHA-256',new TextEncoder().encode('musterout-rg3:'+reg().board_key));assert(call.args.p_key_hash===Array.from(new Uint8Array(sha),x=>x.toString(16).padStart(2,'0')).join(''));
});
Deno.test('transaction result statuses map honestly; usage separately inactive',async()=>{
 const f=fixture();for(const [status,code] of [['recorded',200],['duplicate',200],['conflict',409],['revoked',410],['budget',429],['busy',503],['inactive',503]]){f.set(status as string);const r=await f.send(reg());assert(r.status===code,status as string);assert((await r.json()).ok===(code===200));}
 const n=f.calls.length;assert((await f.send({schema_version:3,kind:'usage',board_key:reg().board_key,version:'0.2.14',buckets:[{bucket_id:'a'.repeat(32),week_index:0,revision:1,opens:1,done_actions:0}]})).status===503);assert(f.calls.length===n);
 f.set('deleted');assert((await f.send({schema_version:3,kind:'delete',board_key:reg().board_key})).status===200);
});
Deno.test('methods, origins, invalid UTF8 and streamed bounds before database',async()=>{
 const f=fixture();assert((await f.send('',{},'GET')).status!==200);assert(f.calls.length===0);assert((await f.send(reg(),{origin:'https://evil.invalid'})).status===403);assert((await f.send(reg(),{'content-type':'text/plain'})).status===400);
 const invalid=new Request('https://example.invalid/ingest',{method:'POST',headers:{'content-type':'application/json'},body:new Uint8Array([0xff])});assert((await f.h(invalid)).status===400);assert((await f.send('x'.repeat(20001))).status===413);assert(f.calls.length===0);
});
Deno.test('short fragment reconstructs the exact cohort and hashes the unchanged short key',async()=>{
 const fragment='v3.eas.e67.20261016.0123456789abcdef.0-2-14';
 const record=C.decode(fragment),f=fixture();
 assert(C.canonical(record)===C.canonical({...reg(),board_key:'0123456789abcdef'}));
 assert((await f.send(record)).status===200);
 f.set('duplicate');assert((await f.send(C.decode(fragment))).status===200);
 assert(JSON.stringify(f.calls[0])===JSON.stringify(f.calls[1]),'retry uses identical SQL arguments');
 const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode('musterout-rg3:0123456789abcdef'));
 assert(f.calls[0].args.p_key_hash===Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,'0')).join(''));
 f.set('conflict');assert((await f.send({...record,version:'0.2.15'})).status===409);
 assert(f.calls[2].args.p_record.version==='0.2.15','version remains a conflicting cohort field');
 f.set('deleted');assert((await f.send(C.decode('d3.0123456789abcdef'))).status===200);
 assert(f.calls[3].args.p_key_hash===f.calls[0].args.p_key_hash,'deletion shares exact identity');
 const n=f.calls.length;
 for(const board_key of ['A'.repeat(16),'a'.repeat(15),'a'.repeat(17)])assert((await f.send({...record,board_key})).status===400);
 assert(f.calls.length===n,'invalid key lengths fail before SQL');
});
