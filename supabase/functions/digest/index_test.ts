import { createHandler, FEED, roundupVariables, validateFeed, weeklyFeed, weekKey } from "./index.ts";
import { fixture } from "../alerts/index_test.ts";
import { ENDPOINT, hash } from "../alerts/index.ts";
import { sendAlert } from "../alerts/send_alert.ts";
const assert=(value:unknown)=>{if(!value)throw new Error("Assertion failed");};
const equal=(a:unknown,b:unknown)=>{if(JSON.stringify(a)!==JSON.stringify(b))throw new Error(`${JSON.stringify(a)} differs from ${JSON.stringify(b)}`);};
const digestEndpoint=ENDPOINT.replace(/alerts$/,"digest");
function feed(notices=true):any {
 return {schema_version:1,source:"MARADMIN",checked_from:"2026-10-05",checked_to:"2026-10-12",generated_at:"2026-10-12T13:30:00Z",checked_count:14,unclassified_count:0,truncated:false,capture_replay:false,notices:notices?[{number:"473/26",title:"ACTIVE RESERVE OFFICER PLAN",summary:"Possible separation connection.",url:"https://www.marines.mil/News/Messages/Messages-Display/Article/4618001/plan/",posted:"2026-10-05",body_available:false}]:[]};
}
function digestFixture(){
 const f=fixture();f.advance(Date.parse("2026-10-12T15:00:00Z")-f.deps.now());f.values.DIGEST_OPS_KEY="test-ops-key";let value=feed(),feedStatus=200;const feedCalls:string[]=[];
 const deps={...f.deps,fetch:(async(input,init)=>{if(String(input)===FEED){feedCalls.push(String(input));return new Response(JSON.stringify(value),{status:feedStatus});}return f.deps.fetch(input,init);}) as typeof fetch};
 const handler=createHandler(deps),request=(dry=false,key:string|null="test-ops-key")=>new Request(digestEndpoint+(dry?"?dry=1":""),{method:"POST",headers:dry&&key!==null?{"x-ops-key":key}:{}});
 const add=(id:string,weekly=true,status="confirmed")=>f.tables.alert_signups.push({id,email:`${id}@example.com`,status,weekly,monthly:true,corrections:true,lessons:true,confirm_hash:null,unsubscribe_hashes:[],last_sent_at:null});
 return {...f,deps,handler,request,add,feedCalls,setTime:(stamp:string)=>f.advance(Date.parse(stamp)-f.deps.now()),setFeed:(v:any)=>{value=v;},feedStatus:(s:number)=>{feedStatus=s;}};
}
Deno.test("authorized digest dry run reports counts without reservations",async()=>{
 const f=digestFixture();f.add("on");f.add("off",false);f.add("pending",true,"pending");
 const response=await f.handler(f.request(true));equal(response.status,200);equal(await response.json(),{ok:true,dry:true,notices:1,batches:1,recipients:1,eligible:1,accepted:0,skipped:0,reasons:{}});
 equal(f.mail().length,0);equal(f.tables.email_delivery_receipts.length,0);equal(f.tables.alert_signups[0].unsubscribe_hashes,[]);
 assert(!JSON.stringify(await(await f.handler(f.request(true))).json()).includes("@"));
});
Deno.test("dry details require the exact ops key and remain private when the secret is unset",async()=>{
 for(const secret of [undefined,"","test-ops-key"])for(const key of [null,"","test-ops-ke","test-ops-key-extra","Test-ops-key","test-ops-kex","test-ops-key"]){
  const f=digestFixture();f.add("on");if(secret===undefined)delete f.values.DIGEST_OPS_KEY;else f.values.DIGEST_OPS_KEY=secret;
  const result=await(await f.handler(f.request(true,key))).json();
  if(secret&&key===secret){equal(result.recipients,1);equal(result.eligible,1);}else{equal(result,{ok:true});equal(f.calls.length,0);equal(f.feedCalls.length,0);}
  equal(f.mail().length,0);equal(f.tables.email_delivery_receipts.length,0);
 }
 for(const mode of ["quiet","stale","unavailable"]){
  const f=digestFixture();f.add("on");if(mode==="quiet")f.setFeed(feed(false));if(mode==="stale")f.advance(80*3600000);if(mode==="unavailable")f.feedStatus(500);
  equal(await(await f.handler(f.request(true,null))).json(),{ok:true});equal(f.calls.length,0);equal(f.feedCalls.length,0);
 }
});
Deno.test("cron sends without an ops key or configured ops secret",async()=>{
 const f=digestFixture();delete f.values.DIGEST_OPS_KEY;f.add("on");
 equal((await f.handler(f.request())).status,200);equal(f.mail().length,1);
});
Deno.test("digest filters confirmed weekly choices and sends unique private links in batches",async()=>{
 const f=digestFixture();for(let n=0;n<101;n++)f.add(String(n).padStart(4,"0"));f.add("off",false);f.add("pending",true,"pending");
 equal((await f.handler(f.request())).status,200);equal(f.mail().map(c=>(c.body as any[]).length),[100,1]);const tokens=new Set<string>();
 for(const c of f.mail())for(const m of c.body as any[]){
  equal(m.template.id,"weekly-roundup");equal(m.to.length,1);assert(!m.html&&!m.text);const v=m.template.variables;assert(!Object.hasOwn(v,"NOTHING_NEW"));assert(v.ITEMS_HTML.includes("<table")&&v.ITEMS_HTML.includes("Title only"));assert(v.ITEMS_TEXT.includes("Source: https://www.marines.mil"));
  for(const [url,key] of [[v.ALERT_UNSUBSCRIBE_URL,"unsubscribe"],[v.PREFS_URL,"prefs"]]){const raw=new URL(url).searchParams.get(key) as string;tokens.add(raw);const row=f.tables.alert_signups.find(r=>r.email===m.to[0]);assert((row?.unsubscribe_hashes as string[]).includes(await hash(raw)));assert(!JSON.stringify(f.tables).includes(raw));}
 }
 equal(tokens.size,202);equal(f.tables.alert_signups.find(r=>r.id==="off")?.last_sent_at,null);
 const again=await(await f.handler(f.request())).json();equal(again.skipped,101);equal(again.noop,"no_eligible_recipients");equal(f.mail().length,2);
});
Deno.test("public concurrent triggers and changed feed content cannot duplicate an ISO week",async()=>{
 const f=digestFixture();f.add("on");await Promise.all([f.handler(f.request()),f.handler(f.request())]);equal(f.mail().length,1);
 f.setFeed({...feed(),notices:[{...feed().notices[0],summary:"Updated title qualification."}]});const result=await(await f.handler(f.request())).json();equal(result.accepted,0);equal(result.reasons.duplicate,1);equal(f.mail().length,1);
});
Deno.test("quiet weeks no-op with skipped counts and never reserve or send",async()=>{
 for(const dry of [false,true]){const f=digestFixture();f.add("on");f.setFeed(feed(false));const response=await f.handler(f.request(dry));equal(response.status,200);const result=await response.json();equal(result.noop,"no_matches");equal(result.skipped,1);equal(result.eligible,0);equal(f.mail().length,0);equal(f.tables.email_delivery_receipts.length,0);assert(f.calls.every(c=>c.method==="HEAD"));}
});
Deno.test("early calls leave the Monday slot for the refreshed feed",async()=>{
 const f=digestFixture();f.add("on");f.setTime("2026-10-12T00:00:00Z");f.setFeed({...feed(),generated_at:"2026-10-09T20:00:00Z"});
 equal(await(await f.handler(f.request())).json(),{ok:true,noop:"outside_window"});equal(f.calls.length,0);equal(f.feedCalls.length,0);equal(f.tables.email_delivery_receipts.length,0);
 f.setTime("2026-10-12T15:00:00Z");const newer={...feed(),notices:[{...feed().notices[0],number:"484/26",title:"NEW MONDAY RETIREMENT GUIDANCE"}]};f.setFeed(newer);
 equal((await(await f.handler(f.request())).json()).accepted,1);equal(f.mail().length,1);const variables=(f.mail()[0].body as any[])[0].template.variables;assert(variables.ITEMS_TEXT.includes("484/26"));assert(!variables.ITEMS_TEXT.includes("473/26"));
 equal((await(await f.handler(f.request())).json()).reasons.duplicate,1);equal(f.mail().length,1);
});
Deno.test("delivery window starts at Monday 15 UTC and ends at midnight",async()=>{
 for(const stamp of ["2026-10-11T23:59:59Z","2026-10-12T14:59:59Z","2026-10-13T00:00:00Z","2026-10-16T15:00:00Z","2026-10-19T14:59:59Z"]){
  for(const dry of [false,true]){const f=digestFixture();f.add("on");f.setTime(stamp);equal(await(await f.handler(f.request(dry))).json(),{ok:true,...(dry?{dry:true}:{}),noop:"outside_window"});equal(f.calls.length,0);equal(f.feedCalls.length,0);equal(f.tables.email_delivery_receipts.length,0);}
 }
 for(const stamp of ["2026-10-12T15:00:00Z","2026-10-12T23:59:59.999Z"]){const f=digestFixture();f.add("on");f.setTime(stamp);equal((await(await f.handler(f.request())).json()).accepted,1);equal(f.mail().length,1);}
});
Deno.test("current cycle requires a feed generated since daily Watch at 10 UTC",async()=>{
 for(const stamp of ["2026-10-09T20:00:00Z","2026-10-12T09:59:59.999Z"]){for(const dry of [false,true]){const f=digestFixture();f.add("on");f.setFeed({...feed(),generated_at:stamp});equal(await(await f.handler(f.request(dry))).json(),{ok:true,...(dry?{dry:true}:{}),noop:"stale_feed"});equal(f.calls.length,0);equal(f.mail().length,0);equal(f.tables.email_delivery_receipts.length,0);}}
 const f=digestFixture();f.add("on");f.setFeed({...feed(),generated_at:"2026-10-12T09:59:59Z"});equal((await(await f.handler(f.request())).json()).noop,"stale_feed");
 f.setFeed({...feed(),generated_at:"2026-10-12T10:00:00Z"});equal((await(await f.handler(f.request(true))).json()).eligible,1);equal(f.tables.email_delivery_receipts.length,0);equal((await(await f.handler(f.request())).json()).accepted,1);
 f.setTime("2026-10-19T15:00:00Z");equal((await(await f.handler(f.request())).json()).noop,"stale_feed");equal(f.mail().length,1);equal(f.tables.email_delivery_receipts.length,1);
});
Deno.test("digest rejects unsafe, incomplete or malformed feeds before writes",async()=>{
 for(const change of [{schema_version:2},{source:"OTHER"},{truncated:true},{capture_replay:true},{unclassified_count:1},{checked_count:0},{generated_at:"2026-10-09"},{generated_at:"2026-10-12T15:00:01Z"},{checked_to:"2026-09-01"},{checked_from:"2026-02-30"},{notices:[{...feed().notices[0],url:"https://evil.invalid/message"}]},{notices:[{...feed().notices[0],summary:"<script>bad</script>"}]},{notices:[feed().notices[0],feed().notices[0]]}]){const f=digestFixture();f.add("on");f.setFeed({...feed(),...change});equal((await f.handler(f.request())).status,503);equal(f.calls.length,0);equal(f.mail().length,0);}
 const f=digestFixture();f.feedStatus(500);equal((await f.handler(f.request())).status,503);equal(f.calls.length,0);
});
Deno.test("digest escapes notice copy and links large issues to the complete roundup",()=>{
 const small=feed();small.notices[0].title="RESERVE & OFFICER PLAN";const vars=roundupVariables(validateFeed(small,Date.parse("2026-10-12T15:00:00Z")));assert(vars.ITEMS_HTML.includes("&amp;"));assert(vars.ITEMS_TEXT.includes("&"));
 const large=feed();large.notices=Array.from({length:20},(_,n)=>({...small.notices[0],number:`${n+1}/26`}));large.checked_count=20;const v=roundupVariables(validateFeed(large,Date.parse("2026-10-12T15:00:00Z")));assert(v.ITEMS_HTML.includes("20 MARADMIN title matches"));assert(v.ITEMS_TEXT.includes("https://watch.warfarecommand.com/"));assert(Object.values(v).every(value=>value.length<=2000));assert(!Object.hasOwn(v,"NOTHING_NEW"));
 equal(weekKey(Date.parse("2026-12-31T23:59:59Z")),"2026-12-28");equal(weekKey(Date.parse("2027-01-03T23:59:59Z")),"2026-12-28");equal(weekKey(Date.parse("2027-01-04T00:00:00Z")),"2027-01-04");
});
Deno.test("uncertain digest delivery blocks duplicate public attempts with visible skip reasons",async()=>{
 const f=digestFixture();f.add("on");f.badMail();equal((await f.handler(f.request())).status,503);equal(f.tables.email_delivery_receipts[0].state,"unknown");const again=await(await f.handler(f.request())).json();equal(again.reasons.blocked,1);equal(f.mail().length,1);
});
Deno.test("digest and Monthly compete for the same atomic cap, reflected in dry runs",async()=>{
 const f=digestFixture();f.add("on");const message=JSON.stringify({template:"monthly",campaign:"october",variables:{SHIPPED:"A reviewed release shipped.",NEXT:"The next release is in review.",AI_MOVE:"Ask Claude to explain a term.",QUESTION:"Which term needs an explanation?"}});
 await Promise.all([f.handler(f.request()),sendAlert(message,true,{...f.deps,print:()=>{}})]);equal(f.mail().length,1);equal(f.tables.email_delivery_receipts.filter(r=>r.state==="accepted").length,1);
 const dry=await(await f.handler(f.request(true))).json();equal(dry.eligible,0);equal(dry.skipped,1);assert(dry.reasons.duplicate===1||dry.reasons.weekly_cap===1);
});

function v2feed(): any {
 const legacy = feed();
 const block = (source: string, number: string) => ({ source, coverage: `${source} official RSS; posted in the stated window`, status: "ok", reason: null, last_attempt: legacy.generated_at, last_success: legacy.generated_at, window: {from: "2026-09-13", to: "2026-10-12"}, checked_count: 14, unclassified_count: 0, truncated: false, body_available: false, notices: [{...legacy.notices[0],series: source,number,id: source + "-" + number.replace("/","-"),lines:["reserve"],paths:["all"]}] });
 return {schema_version:2,seq:4,generated_at:legacy.generated_at,expires_at:"2026-10-20T13:30:00Z",capture_replay:false,sources:[block("MARADMIN","473/26"),block("ALMAR","473/26")]};
}
Deno.test("v2 groups colliding series identities and retains ISO week idempotency", async () => {
 const f = digestFixture(); f.add("on"); f.setFeed(v2feed());
 equal((await(await f.handler(f.request())).json()).notices,2);
 const variables = (f.mail()[0].body as any[])[0].template.variables;
 assert(variables.ITEMS_TEXT.includes("MARADMIN")); assert(variables.ITEMS_TEXT.includes("ALMAR"));
 equal((await(await f.handler(f.request())).json()).reasons.duplicate,1); equal(f.mail().length,1);
});
Deno.test("v2 daily catch-up feed contributes only the digest week", async () => {
 const f = digestFixture(); f.add("on"); const v = v2feed();
 v.sources[0].notices.push({...v.sources[0].notices[0],number:"100/26",id:"MARADMIN-100-26",posted:"2026-09-30"});
 f.setFeed(v); equal((await(await f.handler(f.request())).json()).notices,2);
 const weekly = weeklyFeed(validateFeed(v,f.deps.now()),f.deps.now()) as any;
 equal(weekly.sources[0].notices.length,1); equal(weekly.sources[0].notices[0].number,"473/26");
});
Deno.test("v2 failed source remains visible and does not suppress a healthy source", async () => {
 const f=digestFixture();f.add("on");const v=v2feed();v.sources[1].status="failed";v.sources[1].reason="Official source unavailable";v.sources[1].last_success="2026-10-11T10:00:00Z";f.setFeed(v);
 equal((await(await f.handler(f.request())).json()).notices,1);
 const variables=(f.mail()[0].body as any[])[0].template.variables;
 assert(variables.ITEMS_TEXT.includes("ALMAR"));assert(variables.ITEMS_TEXT.includes("failed"));assert(!variables.ITEMS_TEXT.includes("ALMAR 473/26"));
 const all=digestFixture();all.add("on");v.sources[0].status="failed";v.sources[0].reason="Source unavailable";all.setFeed(v);
 equal((await(await all.handler(all.request())).json()).noop,"incomplete_sources");equal(all.mail().length,0);
});
Deno.test("v2 zero-match result carries coverage for every source", async () => {
 const f=digestFixture();f.add("on");const v=v2feed();for(const b of v.sources)b.notices=[];f.setFeed(v);
 const result=await(await f.handler(f.request())).json();equal(result.noop,"no_matches");equal(result.coverage.length,2);assert(result.coverage.every((b:any)=>b.coverage&&typeof b.body_available==="boolean"));equal(f.mail().length,0);
});
Deno.test("v2 rejects replay-shaped metadata, bad identities, dates, and source URLs", async () => {
 const changes=[(v:any)=>v.seq=true,(v:any)=>v.expires_at="2026-10-21T13:30:00Z",(v:any)=>v.sources.push(v.sources[0]),(v:any)=>v.sources[0].notices[0].id="ALMAR-473-26",(v:any)=>v.sources[0].notices[0].url="https://www.marines.mil/News/Messages/Messages-Display/../evil",(v:any)=>v.sources[0].notices[0].url+="?next=x",(v:any)=>v.sources[0].notices[0].posted="2026-02-30",(v:any)=>v.sources[0].checked_count=true,(v:any)=>v.sources[0].last_success=null,(v:any)=>v.sources[0].notices[0].lines=["unknown"],(v:any)=>v.sources[0].hidden={text:"bad\u0001"},(v:any)=>v.capture_replay=true];
 for(const change of changes){const f=digestFixture();f.add("on");const v=v2feed();change(v);f.setFeed(v);equal((await f.handler(f.request())).status,503);equal(f.mail().length,0);equal(f.calls.length,0);}
});
Deno.test("v2 ALNAV and ORDER use their own official URL rules",()=>{
 const v=v2feed();const alnav=v.sources[1];alnav.source="ALNAV";alnav.notices[0].series="ALNAV";alnav.notices[0].id="ALNAV-473-26";alnav.notices[0].url="https://www.mynavyhr.navy.mil/Portals/55/Messages/ALNAV/ALN2026/ALN26073.txt";
 validateFeed(v,Date.parse("2026-10-12T15:00:00Z"));
 const order=v.sources[0];order.source="ORDER";order.notices[0].series="ORDER";order.notices[0].number="MCO 1900.16";order.notices[0].id="ORDER-MCO-1900-16";order.notices[0].url="https://www.marines.mil/News/Publications/MCPEL/Electronic-Library-Display/Article/900/mco-190016/";
 validateFeed(v,Date.parse("2026-10-12T15:00:00Z"));
});
