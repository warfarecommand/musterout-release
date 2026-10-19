import { createHandler, ENDPOINT, SITE } from './index.ts';
const assert = (v: unknown, m = 'Assertion failed') => { if (!v) throw Error(m); };
const eq = (a: unknown, b: unknown) => assert(JSON.stringify(a) === JSON.stringify(b), `${JSON.stringify(a)} != ${JSON.stringify(b)}`);
function fixture() {
 const calls: { url: string; body: unknown }[] = [];
 const totals = { copy_board: 0, copy_coach: 0 }, dropped = { copy_board: 0, copy_coach: 0 };
 let failure = false, status = '';
 const values: Record<string,string> = {SUPABASE_URL:'https://database.invalid',SUPABASE_SERVICE_ROLE_KEY:'fixture-key'};
 const handler = createHandler({env: k => values[k],bodyDeadlineMs:20,
  fetch: async (input, init) => {
   const url=String(input),body=JSON.parse(String((init as RequestInit | undefined)?.body));calls.push({url,body});
   eq(url,'https://database.invalid/rest/v1/rpc/setup_copy_hit');eq(Object.keys(body),['p_button']);
   if(failure) return new Response('private database error',{status:500});
   const key=body.p_button as keyof typeof totals;
   if(totals[key]>=200)dropped[key]++;else totals[key]++;
   return Response.json({status:status||(totals[key]===200&&dropped[key]>0?'dropped':'counted')});
  }});
 const post=(body: unknown={button:'copy_board'},headers: Record<string,string>={},suffix='')=>handler(new Request(ENDPOINT+'/setup-count'+suffix,{method:'POST',headers:{origin:SITE,'content-type':'application/json',...headers},body:JSON.stringify(body)}));
 return {handler,post,calls,totals,dropped,fail:()=>{failure=true;},reply:(s:string)=>{status=s;}};
}
Deno.test('setup count stores only an allowed button through one aggregate RPC; no email/salt dependency',async()=>{
 const f=fixture();eq((await f.post(undefined,{'x-forwarded-for':'192.0.2.9',cookie:'fixture=private',referer:SITE+'/?private=fixture','x-install-id':'private-fixture'})).status,200);
 eq((await f.post({button:'copy_coach'})).status,200);
 eq(f.calls.map(c=>c.body),[{p_button:'copy_board'},{p_button:'copy_coach'}]);
 assert(!/192\.0\.2|private|cookie|referrer|install/.test(JSON.stringify(f.calls)));
});
Deno.test('setup count global per-button 200 ceiling returns 429 and records overflow',async()=>{
 const f=fixture();for(let i=0;i<200;i++)eq((await f.post()).status,200);
 eq((await f.post()).status,429);eq((await f.post()).status,429);
 eq((await f.post({button:'copy_coach'})).status,200);eq(f.totals,{copy_board:200,copy_coach:1});eq(f.dropped,{copy_board:2,copy_coach:0});
});
Deno.test('setup count rejects malformed shape, all extra fields and arbitrary names before database access',async()=>{
 const f=fixture();for(const body of [null,[],0,'copy_board',{}, {button:0},{button:null},{button:'Copy board setup'},{button:'copy_board',day:'2026-10-18'},{button:'copy_board',kind:'intent'},{button:'copy_board',email:'synthetic@example.invalid'},{button:'copy_board',ip_hash:'fixture'},{button:'copy_board',__proto__:null,identifier:'fixture'}])eq((await f.post(body)).status,400);
 for(const raw of ['{', 'true','{"button":"copy_board","referrer":"fixture"}'])eq((await f.handler(new Request(ENDPOINT+'/setup-count',{method:'POST',headers:{origin:SITE,'content-type':'application/json'},body:raw}))).status,400);
 eq(f.calls.length,0);
});
Deno.test('setup count rejects foreign/missing origins, query, method and media type',async()=>{
 const f=fixture();for(const origin of ['', 'https://other.invalid'])eq((await f.post(undefined,{origin})).status,403);
 eq((await f.post(undefined,{},'?identifier=fixture')).status,400);
 eq((await f.post(undefined,{'content-type':'text/plain'})).status,415);
 eq((await f.handler(new Request(ENDPOINT+'/setup-count',{headers:{origin:SITE}}))).status,405);
 eq(f.calls.length,0);
 eq((await f.post(undefined,{origin:'https://warfarecommand.com'})).status,200);
 eq((await f.post(undefined,{origin:'https://www.warfarecommand.com'})).status,200);
 eq((await f.handler(new Request(ENDPOINT+'/setup-count',{method:'OPTIONS',headers:{origin:SITE}}))).status,204);
});
Deno.test('setup count enforces streamed byte cap, declared cap, UTF-8 and read deadline',async()=>{
 const f=fixture();eq((await f.post({button:'copy_board'}, {'content-length':'129'})).status,413);
 eq((await f.handler(new Request(ENDPOINT+'/setup-count',{method:'POST',headers:{origin:SITE,'content-type':'application/json'},body:' '.repeat(129)}))).status,413);
 const req=(stream:ReadableStream<Uint8Array>)=>new Request(ENDPOINT+'/setup-count',{method:'POST',headers:{origin:SITE,'content-type':'application/json'},body:stream,duplex:'half'} as RequestInit);
 eq((await f.handler(req(new ReadableStream({start(c){c.enqueue(new Uint8Array([255]));c.close();}})))).status,400);
 eq((await f.handler(req(new ReadableStream({start(){},cancel(){}})))).status,408);eq(f.calls.length,0);
});
Deno.test('setup count fails closed and never leaks database errors or confirms unknown RPC status',async()=>{
 const f=fixture();f.fail();const result=await f.post();eq(result.status,503);eq(await result.json(),{ok:false,error:'unavailable'});
 const g=fixture();g.reply('unexpected');eq((await g.post()).status,503);
});
