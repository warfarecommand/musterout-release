#!/usr/bin/env node
/* Muster Out protocol 1. Built-in modules only. Public data, no remote execution. */
'use strict';
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const https = require('node:https');
const http = require('node:http');
const tls = require('node:tls');
const zlib = require('node:zlib');
const MAX_BYTES=2000000, MAX_TOTAL=16000000, MAX_FILES=256, V0='0.2.13', PACK='usmc-2026.10';
const ROOTS={release:{'release-2026-10-6da55817':'lJHnis3XITfBHO3iy0tBM60/QydDw4fe4R3Znh6wuwY='},feed:{'feed-2026-10-05bbe934':'Wu+hyhxyklR3J/HQsbRq6XkCcWjNmiunuCfCb3G8TLo='}};
const MIRRORS=['https://cdn.jsdelivr.net/npm/musterout@','https://unpkg.com/musterout@'];
const FEEDS=['https://watch.warfarecommand.com/feed/v2/feed.js','https://raw.githubusercontent.com/warfarecommand/musterout-release/main/feed/v2/feed.js'];
// Only release-gated package mirrors may provide schema 3.
const FEEDS_V3=["https://cdn.jsdelivr.net/npm/musterout-feed@latest/v3/feed.js","https://raw.githubusercontent.com/warfarecommand/musterout-release/main/feed/v3/feed.js"];
const PREFIX='<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,sans-serif;background:#fafaf9}img{max-width:100%}[hidden]{display:none!important}</style></head><body>', SUFFIX='</body></html>';
const REQUIRED=['SETUP.md','WEEKLY.md','UPDATE.md','CLAUDE.md','SUPPORT.md','config.json','CHANGELOG.md','board/board.html','board/board.publish.html','.claude/skills/intake/SKILL.md','.claude/skills/board/SKILL.md','.claude/skills/update/SKILL.md','.claude/skills/watch/SKILL.md'];
const OPTIONAL=["PROJECT.md","COACH.md","board/coach.js","workflows/appointment-collisions.md","workflows/call-brief.md","workflows/household-coverage.md","workflows/income-runway.md","workflows/move-decision.md","workflows/resume-skills-gap.md","workflows/school-comparison.md","workflows/spouse-brief.md","workflows/tap-evidence.md","workflows/va-status.md"];
const VECTOR_KEY='d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a';
const VECTOR_SIG='e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b';
function need(ok,code){if(!ok)throw new Error(code);}
function scalar(s){need(!/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(s),'invalid_unicode');return s;}
function canonical(v){
  if(v===null||typeof v==='boolean')return JSON.stringify(v);
  if(typeof v==='string')return JSON.stringify(scalar(v));
  if(typeof v==='number'){need(Number.isSafeInteger(v),'unsafe_number');return JSON.stringify(v);}
  if(Array.isArray(v))return '['+v.map(canonical).join(',')+']';
  need(v&&typeof v==='object'&&[Object.prototype,null].includes(Object.getPrototypeOf(v)),'invalid_json_value');
  return '{'+Object.keys(v).sort().map(k=>{need(/^[\x20-\x7e]+$/.test(k),'invalid_key');return JSON.stringify(k)+':'+canonical(v[k]);}).join(',')+'}';
}
function parse(raw){
  need(Buffer.isBuffer(raw)&&raw.length>0&&raw.length<=MAX_BYTES,'transport_size');
  const s=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(raw);let i=0;
  function ws(){while(/[\x20\t\r\n]/.test(s[i]||'!'))i++;}
  function string(){const start=i++;while(i<s.length){if(s[i]==='\\'){i+=2;continue;}if(s[i++]==='"')return scalar(JSON.parse(s.slice(start,i)));}throw new Error('invalid_json');}
  function value(depth=0){need(depth<=100,'json_depth');ws();const c=s[i];
    if(c==='"')return string();
    if(c==='{'){i++;ws();const o=Object.create(null),seen=new Set();if(s[i]==='}'){i++;return o;}while(true){ws();need(s[i]==='"','invalid_json');const k=string();need(!seen.has(k),'duplicate_key');seen.add(k);ws();need(s[i++]===':','invalid_json');o[k]=value(depth+1);ws();if(s[i]==='}'){i++;return o;}need(s[i++]===',','invalid_json');}}
    if(c==='['){i++;ws();const a=[];if(s[i]===']'){i++;return a;}while(true){a.push(value(depth+1));ws();if(s[i]===']'){i++;return a;}need(s[i++]===',','invalid_json');}}
    const m=/^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/.exec(s.slice(i));need(m,'invalid_json');i+=m[0].length;const v=JSON.parse(m[0]);if(typeof v==='number'){need(Number.isSafeInteger(v),'unsafe_number');const n=/^(-?)(\d+)(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/.exec(m[0]),dec=n[3]||'',exp=Number(n[4]||0)-dec.length,digits=n[2]+dec;need(Math.abs(exp)<=10000,'unsafe_number');const whole=exp>=0?BigInt(digits)*10n**BigInt(exp):BigInt(digits)/(10n**BigInt(-exp));need(exp>=0||BigInt(digits)%(10n**BigInt(-exp))===0n,'unsafe_number');need(whole<=(9007199254740991n),'unsafe_number');}return v;
  }
  const v=value();ws();need(i===s.length,'invalid_json');canonical(v);return v;
}
function exact(v,keys){need(v&&typeof v==='object'&&!Array.isArray(v)&&Object.keys(v).sort().join(',')===keys.slice().sort().join(','),'invalid_fields');}
function wrapper(raw,kind){need(Buffer.isBuffer(raw)&&raw.length<=MAX_BYTES&&raw.subarray(0,17).toString()==='self.postMessage('&&raw.subarray(-3).toString()===');\n','invalid_wrapper');const t=parse(raw.subarray(17,-3));exact(t,['envelope','signature',kind==='release'?'html':'data']);return t;}
function b64(s,n){need(typeof s==='string'&&/^[A-Za-z0-9+/]*={0,2}$/.test(s),'invalid_base64');const b=Buffer.from(s,'base64');need(b.length===n&&b.toString('base64')===s,'invalid_base64');return b;}
const PRIME=(1n<<255n)-19n, ORDER=(1n<<252n)+27742317777372353535851937790883648493n;
const mod=x=>(x%PRIME+PRIME)%PRIME;
function pow(a,n){let r=1n;for(a=mod(a);n;n>>=1n,a=mod(a*a))if(n&1n)r=mod(r*a);return r;}
const CURVE_D=mod(-121665n*pow(121666n,PRIME-2n)), SQRT_I=pow(2n,(PRIME-1n)/4n), ID=[0n,1n,1n,0n];
function add(a,b){const [x,y,z,t]=a,[X,Y,Z,T]=b,A=mod((y-x)*(Y-X)),B=mod((y+x)*(Y+X)),C=mod(2n*CURVE_D*t*T),E=mod(2n*z*Z);return [mod((B-A)*(E-C)),mod((E+C)*(B+A)),mod((E-C)*(E+C)),mod((B-A)*(B+A))];}
function mul(a,n){let r=ID;while(n){if(n&1n)r=add(r,a);a=add(a,a);n>>=1n;}return r;}
function eq(a,b){return mod(a[0]*b[2]-b[0]*a[2])===0n&&mod(a[1]*b[2]-b[1]*a[2])===0n;}
function little(b){return BigInt('0x'+Buffer.from(b).reverse().toString('hex'));}
function point(b){const n=little(b),y=n&((1n<<255n)-1n),sign=n>>255n;need(y<PRIME,'bad_signature');const xx=mod((y*y-1n)*pow(CURVE_D*y*y+1n,PRIME-2n));let x=pow(xx,(PRIME+3n)/8n);if(mod(x*x-xx)!==0n)x=mod(x*SQRT_I);need(mod(x*x-xx)===0n&&!(x===0n&&sign===1n),'bad_signature');if((x&1n)!==sign)x=PRIME-x;return [x,y,1n,mod(x*y)];}
function strictSignature(key,sig){const a=point(key),r=point(sig.subarray(0,32));return little(sig.subarray(32))<ORDER&&!eq(a,ID)&&!eq(r,ID)&&eq(mul(a,ORDER),ID)&&eq(mul(r,ORDER),ID);}
function edverify(key,sig,msg){try{need(key.length===32&&sig.length===64&&strictSignature(key,sig),'bad_signature');const publicKey=crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),key]),format:'der',type:'spki'});return crypto.verify(null,msg,publicKey,sig);}catch(_){return false;}}
function preflight(){const k=Buffer.from(VECTOR_KEY,'hex'),s=Buffer.from(VECTOR_SIG,'hex');need(edverify(k,s,Buffer.alloc(0))&&!edverify(k,s,Buffer.from('x'))&&digest(Buffer.from('abc'))==='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad','runtime_unavailable');return {protocol:1,positive:true,modified_rejected:true};}
function signed(k,s,m){need(edverify(b64(k,32),b64(s,64),Buffer.from(canonical(m))),'bad_signature');}
function stamp(s){need(typeof s==='string'&&!s.startsWith('0000-')&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{3})?Z$/.test(s),'invalid_time');const n=Date.parse(s);need(Number.isFinite(n)&&new Date(n).toISOString()===(s.length===20?s.slice(0,-1)+'.000Z':s),'invalid_time');return n/1000;}
function day(s){need(typeof s==='string'&&!s.startsWith('0000-')&&/^\d{4}-\d\d-\d\d$/.test(s),'invalid_day');const n=Date.parse(s+'T00:00:00Z');need(Number.isFinite(n)&&new Date(n).toISOString().slice(0,10)===s,'invalid_day');return n/86400000;}
function version(s){need(typeof s==='string'&&s.length<=128&&!/[^0-9.]/.test(s)&&/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.test(s),'invalid_version');return s.split('.').map(BigInt);}
function compare(a,b){a=version(a);b=version(b);for(let i=0;i<3;i++)if(a[i]!==b[i])return a[i]>b[i]?1:-1;return 0;}
function digest(b){return crypto.createHash('sha256').update(b).digest('hex');}
function hashcheck(raw,sha,size){need(Buffer.isBuffer(raw)&&raw.length<=MAX_BYTES,'transport_size');need(typeof sha==='string'&&/^[a-f0-9]{64}$/.test(sha),'invalid_hash');need(digest(raw)===sha,'hash_mismatch');if(size!==undefined)need(Number.isSafeInteger(size)&&size>0&&size<=MAX_BYTES&&raw.length===size,'size_mismatch');}
function envelope(e,sig,payload,kind,pack=PACK,roots=ROOTS){
  need(['release','install','feed'].includes(kind),'wrong_kind');let fields=['product','kind','pack','sha256','size','created','key_id','keychain',...(kind==='feed'?['seq','expires']:['version'])];if(kind==='release')fields.push('notes','correction','impact');exact(e,fields);
  need(e.product==='Muster Out'&&e.kind===kind&&e.pack===pack,'wrong_identity');stamp(e.created);need(typeof e.key_id==='string'&&e.key_id.length>0&&e.key_id.length<=128,'invalid_key_id');if(kind!=='feed')version(e.version);else need(Number.isSafeInteger(e.seq)&&e.seq>0&&stamp(e.expires)>stamp(e.created),'invalid_sequence');
  const scope=kind==='feed'?'feed':'release',trusted=new Map(Object.entries(roots[scope]));need(Array.isArray(e.keychain)&&e.keychain.length<=16,'invalid_keychain');
  for(const l of e.keychain){exact(l,['key_id','public_key','signed_by','signature']);need(typeof l.key_id==='string'&&l.key_id.length>0&&l.key_id.length<=128&&!trusted.has(l.key_id)&&trusted.has(l.signed_by),'invalid_keychain');b64(l.public_key,32);signed(trusted.get(l.signed_by),l.signature,{product:e.product,kind:scope,key_id:l.key_id,public_key:l.public_key,signed_by:l.signed_by});trusted.set(l.key_id,l.public_key);}
  need(trusted.has(e.key_id),'untrusted_key');signed(trusted.get(e.key_id),sig,e);hashcheck(payload,e.sha256,e.size);return e;
}
function notes(v){need(Array.isArray(v)&&v.length===2&&v.every(s=>typeof s==='string'&&s.trim()&&s.length<=500),'invalid_notes');}
function release(raw,selected,pack=PACK,roots=ROOTS){const t=wrapper(raw,'release');need(typeof t.html==='string','invalid_document');const e=envelope(t.envelope,t.signature,Buffer.from(t.html),'release',pack,roots);need(e.version===selected,'wrong_version');notes(e.notes);need(typeof e.correction==='boolean'&&(e.impact===null||typeof e.impact==='string'&&e.impact.length<=1000)&&(!e.correction||e.impact&&e.impact.trim()),'invalid_impact');need(t.html.startsWith(PREFIX)&&t.html.endsWith(SUFFIX),'invalid_document');need(t.html.includes('var VERSION = '+JSON.stringify(selected)+';'),'document_version');return t;}
function safe_path(p){need(typeof p==='string'&&p.length>0&&p.length<=240&&/^[A-Za-z0-9_./-]+$/.test(p),'unsafe_path');const a=p.split('/'),low=a.map(x=>x.toLowerCase());need(a.every(x=>!['','.','..'].includes(x))&&!low.some(x=>x==='.git'||x.startsWith('.env'))&&!['my','npm','feed'].includes(low[0])&&low.slice(0,2).join('/')!=='supabase/migrations'&&!['install.json','release.json','release.js','verify.py','verify.cjs'].includes(p.toLowerCase()),'unsafe_path');return p;}
function install(raw,selected,pack=PACK,roots=ROOTS){
 const t=parse(raw);exact(t,['envelope','signature','manifest']);const m=t.manifest,e=envelope(t.envelope,t.signature,Buffer.from(canonical(m)),'install',pack,roots);exact(m,['schema_version','product','version','released','pack','notes','files','release']);need(m.schema_version===1&&m.product===e.product&&m.version===e.version&&m.version===selected&&m.pack===pack,'manifest_identity');day(m.released);notes(m.notes);need(m.files&&typeof m.files==='object'&&!Array.isArray(m.files)&&Object.keys(m.files).length>0&&Object.keys(m.files).length<=MAX_FILES,'file_count');const seen=new Set();for(const [p,sha] of Object.entries(m.files)){safe_path(p);need(!seen.has(p.toLowerCase()),'case_collision');seen.add(p.toLowerCase());need(typeof sha==='string'&&/^[a-f0-9]{64}$/.test(sha),'invalid_hash');}need(REQUIRED.every(p=>Object.hasOwn(m.files,p)),'missing_required_file');const offered=OPTIONAL.map(p=>Object.hasOwn(m.files,p));need(offered.every(Boolean)||offered.every(x=>!x),'partial_optional_set');const r=m.release;exact(r,['path','sha256','size','html_sha256','html_size']);need(r.path==='release.js','release_path');for(const k of ['sha256','html_sha256'])need(typeof r[k]==='string'&&/^[a-f0-9]{64}$/.test(r[k]),'invalid_hash');for(const k of ['size','html_size'])need(Number.isSafeInteger(r[k])&&r[k]>0&&r[k]<=MAX_BYTES,'transport_size');return t;
}
function package_check(i,rraw,selected,files,pack=PACK,roots=ROOTS){const t=install(i,selected,pack,roots),m=t.manifest,r=release(rraw,selected,pack,roots);hashcheck(rraw,m.release.sha256,m.release.size);need(m.release.html_sha256===r.envelope.sha256&&m.release.html_size===r.envelope.size&&canonical(m.notes)===canonical(r.envelope.notes),'release_binding');need(canonical(Object.keys(files).sort())===canonical(Object.keys(m.files).sort()),'file_set');need(i.length+rraw.length+Object.values(files).reduce((a,b)=>a+b.length,0)<=MAX_TOTAL,'aggregate_limit');for(const [p,sha] of Object.entries(m.files))hashcheck(files[p],sha);need(files['board/board.publish.html'].equals(Buffer.from(r.html))&&files['board/board.html'].equals(Buffer.from(r.html.slice(PREFIX.length,-SUFFIX.length))),'fragment_binding');const c=parse(files['config.json']);need(c.product==='Muster Out'&&c.version===selected&&c.pack===pack&&canonical(c.update_keys)===canonical({release_keys:roots.release,feed_keys:roots.feed}),'config_binding');const embedded=/window\.MusterOutUpdateConfig=(\{[^\n]+?\});/.exec(r.html);need(embedded,'embedded_config_missing');need(canonical(parse(Buffer.from(embedded[1])))===canonical({product:'Muster Out',version:selected,pack,release_keys:roots.release,feed_keys:roots.feed}),'embedded_config_binding');const escaped=selected.replace(/\./g,'\\.'),entry=new RegExp('^## '+escaped+' \\((\\d{4}-\\d\\d-\\d\\d)\\)\\n([\\s\\S]*?)(?=^## |$(?![\\s\\S]))','m').exec(files['CHANGELOG.md'].toString());need(entry&&entry[1]===m.released&&canonical(entry[2].split('\n').filter(s=>s.startsWith('- ')).map(s=>s.slice(2).trim()))===canonical(m.notes),'changelog_binding');return {install:t,release:r};}
function plain(s,n){need(typeof s==='string'&&s.trim()&&s.length<=n&&!/[<>\x00-\x1f\x7f-\x9f]/.test(s),'invalid_text');}
// WATCH_V3_BEGIN
/* Schema-3 public notice validation. No board facts or network access. */
function createWatchV3Contract() {
'use strict';
const ACTIVE=['MARADMIN','ALMAR','ALNAV','ORDER','ECFR','FEDERAL_REGISTER','VA_GOV'],MILITARY=ACTIVE.slice(0,4),DAY=86400000;
const LINES=['separation','retirement','va','skillbridge','reserve','leave','family'],PATHS=['resign','retire','eas','all'];
const VA_FIELDS=['series','number','id','title','url','posted','relevant','lines','paths','action','summary','confidence','deadline','body_available','identifiers','change','source_evidence','rule_type','comments_close_on','cfr_parts','diagnostic_code_evidence','applicability','applicability_evidence','applicability_version'];
const SOURCE_BLOCK_FIELDS_BY_VERSION={3:['source','coverage','status','reason','last_attempt','last_success','window','checked_count','unclassified_count','truncated','body_available','notices']},ORDER_BLOCK_FIELDS=['unresolved_count','unresolved_items'];
const DIMENSIONS={grades:['o5','o14','cwo45','wo13','e89','e67','e15'],service_types:['officer','enlisted'],reserve:[true,false],skillbridge:[true,false]};
const own=(v,k)=>Object.prototype.hasOwnProperty.call(v,k),object=v=>v!==null&&typeof v==='object'&&!Array.isArray(v),integer=v=>Number.isSafeInteger(v)&&v>=0;
function need(ok){if(!ok)throw new Error('invalid_payload');}
function scalar(s){need(!/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(s));return s;}
function clean(value){let nodes=0;function visit(v,depth){need(++nodes<=50000&&depth<=32);if(typeof v==='string'){scalar(v);need(!/[\x00-\x1f\x7f-\x9f]/.test(v));return;}if(v===null||typeof v==='boolean'||Number.isSafeInteger(v))return;if(Array.isArray(v)){need(v.length<=50000);v.forEach(x=>visit(x,depth+1));return;}need(object(v)&&Object.keys(v).length<=256);for(const k of Object.keys(v)){need(/^[\x20-\x7e]+$/.test(k));visit(k,depth+1);visit(v[k],depth+1);}}visit(value,0);}
function canonical(v){if(v===null||typeof v==='boolean'||Number.isSafeInteger(v))return JSON.stringify(v);if(typeof v==='string')return JSON.stringify(scalar(v));if(Array.isArray(v))return '['+v.map(canonical).join(',')+']';need(object(v));return '{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';}
function text(v,max){need(typeof v==='string'&&v.trim()&&v.length<=max&&!/[<>\x00-\x1f\x7f-\x9f]/.test(v));}
function day(v){need(typeof v==='string'&&/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(v)&&v.slice(0,4)!=='0000');const n=Date.parse(v+'T00:00:00Z');need(Number.isFinite(n)&&new Date(n).toISOString().slice(0,10)===v);return n;}
function stamp(v){need(typeof v==='string'&&/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{3})?Z$/.test(v));day(v.slice(0,10));const n=Date.parse(v);need(Number.isFinite(n)&&new Date(n).toISOString()===(v.length===20?v.slice(0,-1)+'.000Z':v));return n;}
function hash(v){return typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);}
function official(source,value){try{if(typeof value!=='string'||value.length>500||!value.startsWith('https://')||/[\s<>\\?#]|%2f|%5c/i.test(value))return false;const u=new URL(value);if(!value.startsWith('https://'+u.hostname+'/')||u.username||u.password||u.port||u.search||u.hash)return false;const raw=value.slice(value.indexOf('/',8));if(decodeURIComponent(raw).split('/').some(p=>p==='.'||p==='..'))return false;const p=raw;
 if(source==='MARADMIN'||source==='ALMAR')return u.hostname==='www.marines.mil'&&/^\/News\/Messages\/Messages-Display\/Article\/[0-9]+\/[A-Za-z0-9-]+\/$/.test(p);
 if(source==='ALNAV')return u.hostname==='www.mynavyhr.navy.mil'&&(p.startsWith('/References/Messages/')||p.startsWith('/Portals/55/Messages/'));
 if(source==='ORDER')return u.hostname==='www.marines.mil'&&(p.startsWith('/News/Publications/MCPEL/')||p.startsWith('/Portals/1/Publications/'));
 if(source==='ECFR')return u.hostname==='www.ecfr.gov'&&/^\/current\/title-38\/chapter-I\/part-[34]\/section-[34]\.[0-9]+[a-z]?(?:-(?:[34]\.)?[0-9]+[a-z]?)?$/.test(p);
 if(source==='FEDERAL_REGISTER')return u.hostname==='www.federalregister.gov'&&/^\/documents\/[0-9]{4}\/[0-9]{2}\/[0-9]{2}\/[0-9]{4}-[0-9]{4,6}\/[A-Za-z0-9-]+\/?$/.test(p);
 if(source==='VA_GOV')return u.hostname==='www.va.gov'&&['/resources/','/disability/','/health-care/'].some(x=>p.startsWith(x))||u.hostname==='news.va.gov'&&/^\/(?:press-room\/[A-Za-z0-9-]+|[0-9]+\/[A-Za-z0-9-]+)\/$/.test(p);
 return false;}catch(_){return false;}}
function sameKeys(v,keys){return object(v)&&Object.keys(v).sort().join(',')===keys.slice().sort().join(',');}
function nativeId(v){need(object(v));const keys=Object.keys(v).sort().join(',');
 if(keys==='part,section,title'){need(Number.isSafeInteger(v.title)&&v.title>=1&&v.title<=50&&Number.isSafeInteger(v.part)&&v.part>0&&typeof v.section==='string'&&new RegExp('^'+v.part+'\\.[0-9]+[a-z]?(?:-(?:'+v.part+'\\.)?[0-9]+[a-z]?)?$').test(v.section));}
 else if(keys==='dc')need(typeof v.dc==='string'&&/^[0-9]{4}$/.test(v.dc));
 else if(keys==='m21_1')need(typeof v.m21_1==='string'&&/^[IVX]+(?:\.[A-Za-z0-9]+){1,7}$/.test(v.m21_1));
 else if(keys==='document_number')need(typeof v.document_number==='string'&&/^[0-9]{4}-[0-9]{4,6}$/.test(v.document_number));
 else if(keys==='form_number')need(typeof v.form_number==='string'&&/^(?:VA|DD|NAVMC) [A-Za-z0-9][A-Za-z0-9 ()-]{0,60}$/.test(v.form_number));
 else if(keys==='issuance,paragraph'||keys==='issuance,paragraph,volume')need(typeof v.issuance==='string'&&/^(?:DoDI|DoDM|DoDD|MCO|SECNAVINST) [0-9]+[A-Za-z0-9. -]{0,40}$/.test(v.issuance)&&typeof v.paragraph==='string'&&/^[A-Za-z0-9.()]{1,40}$/.test(v.paragraph)&&(!own(v,'volume')||v.issuance.startsWith('DoDM ')&&Number.isSafeInteger(v.volume)&&v.volume>0));
 else if(keys==='url'){need(typeof v.url==='string'&&v.url.length<=500&&!/[\s<>\\]/.test(v.url)&&official('VA_GOV',v.url.replace(/[?#].*$/,'')));}
 else need(false);return v;}
function contactFree(v){need(!v.includes('@')&&!/https?:\/\//.test(v)&&!/(?:^|[^\p{L}\p{N}_])\p{Nd}{3}[-. ]\p{Nd}{3}[-. ]\p{Nd}{4}(?=$|[^\p{L}\p{N}_])/u.test(v));}
function applicability(n){if(!own(n,'applicability')){need(!own(n,'applicability_evidence')&&!own(n,'applicability_version'));return;}const a=n.applicability;need(object(a)&&Object.keys(a).every(k=>own(DIMENSIONS,k)));for(const k of Object.keys(a)){need(Array.isArray(a[k])&&a[k].length&&new Set(a[k]).size===a[k].length&&a[k].every(x=>DIMENSIONS[k].includes(x)));}if(own(n,'applicability_version'))need(n.applicability_version===1);if(own(n,'applicability_evidence')){const e=n.applicability_evidence;need(sameKeys(e,Object.keys(a)));for(const rows of Object.values(e)){need(Array.isArray(rows)&&rows.length>=1&&rows.length<=4);rows.forEach(v=>{text(v,500);contactFree(v);});}}}
function summary(n){const ids=n.identifiers;need(Array.isArray(ids));ids.forEach(nativeId);const sorted=rows=>[...new Set(rows)].sort(),cfr=sorted(ids.filter(i=>own(i,'section')).map(i=>i.title+' CFR '+i.section)),codes=sorted(ids.filter(i=>own(i,'dc')).map(i=>i.dc)),manuals=sorted(ids.filter(i=>own(i,'m21_1')).map(i=>i.m21_1)),documents=sorted(ids.filter(i=>own(i,'document_number')).map(i=>i.document_number));
 const bounded=rows=>rows.slice(0,3).join(', ')+(rows.length>3?' and '+(rows.length-3)+' more':''),label=v=>{const d=new Date(day(v));return String(d.getUTCDate()).padStart(2,'0')+' '+['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][d.getUTCMonth()]+' '+String(d.getUTCFullYear()).padStart(4,'0');};const change=n.change;need(object(change)&&['published','amended','removed','added','updated','version_changed'].includes(change.kind));let result;
 if(n.series==='FEDERAL_REGISTER'){need(['final','proposed'].includes(n.rule_type));result='VA published a '+(n.rule_type==='final'?'final rule':'proposed rule')+' about '+(cfr.length?bounded(cfr):'Federal Register document '+bounded(documents));}
 else if(n.series==='ECFR')result='eCFR records '+({amended:'an amendment to',added:'the addition of',removed:'the removal of',published:'a publication of',updated:'an update to',version_changed:'a version change to'}[change.kind])+' '+bounded(cfr);
 else if(n.series==='VA_GOV'){result=change.kind==='updated'?'VA.gov records a benefit-page content update':'VA.gov published a benefit or program update';if(cfr.length)result+=' concerning '+bounded(cfr);}
 else need(false);
 if(codes.length)result+='; diagnostic codes '+bounded(codes);if(change.published_at)result+=', published '+label(change.published_at);if(change.effective_from)result+=', effective '+label(change.effective_from);if(n.comments_close_on)result+='; comments close '+label(n.comments_close_on);return result+'. Read the official text.';}
function vaNotice(n,attempt){need(Object.keys(n).every(k=>VA_FIELDS.includes(k)));need(Array.isArray(n.identifiers)&&n.identifiers.length>=1&&n.identifiers.length<=200);const seen=new Set();n.identifiers.forEach(i=>{nativeId(i);const k=canonical(i);need(!seen.has(k));seen.add(k);});const has=v=>n.identifiers.some(i=>canonical(i)===canonical(v));
 if(n.series==='FEDERAL_REGISTER')need(has({document_number:n.number})&&n.url.includes('/'+n.number+'/')&&['final','proposed'].includes(n.rule_type)&&(n.comments_close_on??null)===(n.deadline??null));
 if(n.series==='ECFR'){const p=n.number.split(':');need(p.length===5&&p[0]==='38'&&['3','4'].includes(p[1])&&has({title:38,part:Number(p[1]),section:p[2]})&&n.url.endsWith('/section-'+p[2]));}
 if(n.series==='VA_GOV')need(has({url:n.url}));const c=n.change;need(object(c)&&['published','amended','removed','added','updated','version_changed'].includes(c.kind));need((c.before_hash==null||hash(c.before_hash))&&hash(c.after_hash)&&['identified','section','document'].includes(c.scope));need(typeof c.effective_unknown==='boolean'&&c.effective_unknown===(c.effective_from==null));for(const k of ['published_at','effective_from','effective_to'])if(c[k]!=null)day(c[k]);need(stamp(c.observed_at)<=attempt);if(c.effective_from&&c.effective_to)need(c.effective_to>=c.effective_from);
 const e=n.source_evidence;need(object(e)&&['official_metadata','official_body','snapshot_diff'].includes(e.basis)&&e.source_sha256===c.after_hash);text(e.quote,500);contactFree(e.quote);
 if(own(n,'diagnostic_code_evidence')){const rows=n.diagnostic_code_evidence,codes=[...new Set(n.identifiers.filter(i=>own(i,'dc')).map(i=>i.dc))].sort();need(n.series==='ECFR'&&Array.isArray(rows)&&rows.length===codes.length&&canonical([...new Set(rows.map(r=>r?.dc))].sort())===canonical(codes));rows.forEach(r=>{need(object(r)&&['before','after'].includes(r.snapshot)&&r.source_sha256===c[r.snapshot+'_hash']);text(r.quote,500);});}
 if(own(n,'cfr_parts'))need(Array.isArray(n.cfr_parts)&&n.cfr_parts.length<=100&&n.cfr_parts.every(r=>object(r)&&sameKeys(r,['title','part'])&&Number.isSafeInteger(r.title)&&r.title>=1&&r.title<=50&&Number.isSafeInteger(r.part)&&r.part>=1));need(!n.applicability||Object.keys(n.applicability).length===0);need(n.summary===summary(n));text(n.summary,1000);}
function validate(data,now=Date.now(),historical=false){clean(data);const top=['schema_version','seq','generated_at','expires_at','capture_replay','sources','off_sources','legacy_seq','legacy_sha256'];need(object(data)&&top.every(k=>own(data,k))&&Object.keys(data).every(k=>top.includes(k)||k==='classification_mode'));need(data.schema_version===3&&data.capture_replay===false&&integer(data.seq)&&integer(data.legacy_seq)&&data.legacy_seq>=1&&data.seq===data.legacy_seq+1&&hash(data.legacy_sha256));if(own(data,'classification_mode'))text(data.classification_mode,100);const generated=stamp(data.generated_at),expires=stamp(data.expires_at);need(Number.isFinite(now)&&generated<=now&&expires-generated===8*DAY&&(historical||now<expires));need(Array.isArray(data.sources)&&data.sources.length===7);need(canonical(data.off_sources)===canonical([{source:'M21_1',reason:'VA blocks automated reads'}]));const sources=new Set();
 for(const b of data.sources){const required=SOURCE_BLOCK_FIELDS_BY_VERSION[data.schema_version],allowed=required.concat(b?.source==='ORDER'?ORDER_BLOCK_FIELDS:[]);need(object(b)&&required.every(k=>own(b,k))&&Object.keys(b).every(k=>allowed.includes(k))&&ACTIVE.includes(b.source)&&!sources.has(b.source));sources.add(b.source);text(b.coverage,500);need(['ok','failed'].includes(b.status));if(b.status==='ok')need(b.reason===null);else text(b.reason,500);const attempt=stamp(b.last_attempt),success=b.last_success===null?null:stamp(b.last_success);need(attempt<=generated&&(success===null||success<=attempt)&&(b.status!=='ok'||success!==null));need(object(b.window)&&own(b.window,'from')&&own(b.window,'to'));const from=day(b.window.from),to=day(b.window.to);need(to>=from&&to-from<=30*DAY&&b.window.to<=data.generated_at.slice(0,10));need(Array.isArray(b.notices)&&b.notices.length<=500&&integer(b.checked_count)&&b.checked_count>=b.notices.length&&integer(b.unclassified_count)&&b.unclassified_count<=b.checked_count&&typeof b.truncated==='boolean'&&typeof b.body_available==='boolean');need(success!==null||b.checked_count===0&&b.notices.length===0);const ids=new Set();
 for(const n of b.notices){need(object(n)&&n.series===b.source);const military=MILITARY.includes(b.source);text(n.number,military?100:200);text(n.id,military?120:b.source.length+201);let id;if(!military){need(/^[A-Za-z0-9.:-]{1,200}$/.test(n.number));id=b.source+'-'+n.number;}else if(b.source==='ORDER')id='ORDER-'+n.number.toUpperCase().replace(/[^A-Z0-9]+/g,'-').replace(/^-|-$/g,'');else{need(/^[0-9]{1,3}\/[0-9]{2}$/.test(n.number));id=b.source+'-'+n.number.replace('/','-');}need(n.id===id&&!ids.has(id));ids.add(id);text(n.title,300);if(own(n,'summary'))text(n.summary,1000);need(official(b.source,n.url));const posted=day(n.posted);need(posted>=from&&posted<=to&&typeof n.body_available==='boolean'&&(!b.body_available||n.body_available));for(const [key,allowed] of [['lines',LINES],['paths',PATHS]])need(Array.isArray(n[key])&&n[key].length&&new Set(n[key]).size===n[key].length&&n[key].every(x=>allowed.includes(x)));need(['required','informational'].includes(own(n,'action')?n.action:'informational')&&['high','medium','low'].includes(own(n,'confidence')?n.confidence:'low'));if(n.deadline!=null)day(n.deadline);applicability(n);if(!military)vaNotice(n,attempt);
 }}need(sources.size===7);return data;}
return Object.freeze({ACTIVE:Object.freeze(ACTIVE),MILITARY:Object.freeze(MILITARY),validate,summary,canonical,official,clean});
}
const WATCH_V3=createWatchV3Contract();
// WATCH_V3_END

function feed_shape(data){
 function clean(v){if(typeof v==='string')need(!/[\x00-\x1f\x7f-\x9f]/.test(v),'feed_controls');else if(Array.isArray(v))v.forEach(clean);else if(v&&typeof v==='object')Object.entries(v).forEach(([k,x])=>{clean(k);clean(x);});}clean(data);
 need(data&&typeof data==='object'&&['schema_version','seq','generated_at','expires_at','capture_replay','sources'].every(k=>Object.hasOwn(data,k)),'feed_fields');need(data&&data.schema_version===2&&data.capture_replay===false,'feed_schema');need(Array.isArray(data.sources)&&data.sources.length>0&&data.sources.length<=4,'feed_sources');const seen=new Set();
 for(const s of data.sources){need(s&&typeof s==='object'&&['source','coverage','status','reason','last_attempt','last_success','window','checked_count','unclassified_count','truncated','body_available','notices'].every(k=>Object.hasOwn(s,k)),'source_fields');const name=s.source;need(['MARADMIN','ALMAR','ALNAV','ORDER'].includes(name)&&!seen.has(name),'feed_source');seen.add(name);plain(s.coverage,500);need(['ok','failed'].includes(s.status),'source_status');const attempt=stamp(s.last_attempt),success=s.last_success===null?null:stamp(s.last_success);need(attempt<=stamp(data.generated_at)&&(success===null||success<=attempt),'source_time');need(s.status==='ok'&&success!==null&&s.reason===null||s.status==='failed'&&typeof s.reason==='string','source_status');if(s.status==='failed')plain(s.reason,500);exact(s.window,['from','to']);const start=day(s.window.from),end=day(s.window.to);need(end>=start&&end-start<=30&&end<=day(data.generated_at.slice(0,10)),'source_window');const ns=s.notices;need(Array.isArray(ns)&&ns.length<=500,'notice_count');need(Number.isSafeInteger(s.checked_count)&&s.checked_count>=ns.length&&Number.isSafeInteger(s.unclassified_count)&&s.unclassified_count>=0&&s.unclassified_count<=s.checked_count,'source_count');need(success!==null||ns.length===0&&s.checked_count===0,'source_history');need(typeof s.truncated==='boolean'&&typeof s.body_available==='boolean','source_flags');const ids=new Set();
  for(const n of ns){need(n&&typeof n==='object'&&['series','number','id','title','url','posted','body_available','lines','paths'].every(k=>Object.hasOwn(n,k)),'notice_fields');need(n.series===name,'notice_series');need(typeof n.number==='string'&&n.number.trim(),'notice_number');let identity;if(name!=='ORDER'){need(/^[0-9]{1,3}\/[0-9]{2}$/.test(n.number),'notice_number');identity=name+'-'+n.number.replace('/','-');}else{need(n.number.length<=120,'notice_number');identity='ORDER-'+n.number.toUpperCase().replace(/[^A-Z0-9]+/g,'-').replace(/^-|-$/g,'');}need(n.id===identity&&!ids.has(identity),'notice_identity');ids.add(identity);plain(n.title,300);if(Object.hasOwn(n,'summary'))plain(n.summary,1000);if(n.deadline!=null)day(n.deadline);const posted=day(n.posted);need(posted>=start&&posted<=end,'notice_window');need(typeof n.body_available==='boolean'&&(!s.body_available||n.body_available),'notice_body');for(const [k,allowed] of [['lines',['separation','retirement','va','skillbridge','reserve','leave','family']],['paths',['resign','retire','eas','all']]]){const a=n[k];need(Array.isArray(a)&&a.length>0&&a.every(x=>allowed.includes(x))&&new Set(a).size===a.length,'classification');}for(const [k,a] of [['action',['required','informational']],['confidence',['high','medium','low']]])need(!Object.hasOwn(n,k)||a.includes(n[k]),'classification');const u=n.url;need(typeof u==='string'&&u.length<=500&&!/%2e/i.test(u)&&!/[\s<>\\?#@:]|%2f|%5c/i.test(u.slice(8))&&!u.slice(8).split('/').some(x=>['.','..'].includes(x)),'notice_url');const pattern=['MARADMIN','ALMAR'].includes(name)?/^https:\/\/www\.marines\.mil\/News\/Messages\/Messages-Display\/Article\/[0-9]+\/[a-zA-Z0-9-]+\/$/:name==='ALNAV'?/^https:\/\/www\.mynavyhr\.navy\.mil\/(?:References\/Messages\/|Portals\/55\/Messages\/)[A-Za-z0-9_./%()-]+$/:/^https:\/\/www\.marines\.mil\/(?:News\/Publications\/MCPEL\/|Portals\/1\/Publications\/)[A-Za-z0-9_./%()-]+$/;need(pattern.test(u),'notice_url');}
 }
}
function feed(raw,now,pack=PACK,roots=ROOTS){const t=wrapper(raw,'feed'),d=t.data,e=envelope(t.envelope,t.signature,Buffer.from(canonical(d)),'feed',pack,roots);need(typeof now==='number'&&Number.isFinite(now)&&now>0&&now<253402300800,'clock_unavailable');need(d.seq===e.seq&&(!Object.hasOwn(d,'pack')||d.pack===pack)&&d.generated_at===e.created&&d.expires_at===e.expires,'feed_binding');const start=stamp(e.created),end=stamp(e.expires);need(end-start===8*86400&&start<=now&&now<end,'expired_or_future');feed_shape(d);return t;}
function record(r){return Buffer.from('self.postMessage('+canonical({envelope:r.envelope,signature:r.signature,data:r.data}).replaceAll('\u2028','\\u2028').replaceAll('\u2029','\\u2029')+');\n');}
function feed_identity(e){return canonical(Object.fromEntries(['seq','created','expires','pack','sha256','size'].map(k=>[k,e[k]])));}
function highwater(records,now,pack=PACK,roots=ROOTS){need(Array.isArray(records),'invalid_records');let best=null;const identities=new Map();for(const r of records){try{const at=stamp(r.accepted_at);need(at<=now&&r.highest_seq===r.envelope.seq,'invalid_record');const t=feed(record(r),at,pack,roots),seq=t.envelope.seq,identity=feed_identity(t.envelope);need(!identities.has(seq)||identities.get(seq)===identity,'equivocation');identities.set(seq,identity);if(!best||seq>best.envelope.seq)best=t;}catch(e){if(e.message==='equivocation')throw e;}}return best;}
function replay(t,records,now,pack=PACK,roots=ROOTS){const b=highwater(records,now,pack,roots);if(b){need(t.envelope.seq>=b.envelope.seq,'replay');need(t.envelope.seq!==b.envelope.seq||feed_identity(t.envelope)===feed_identity(b.envelope),'equivocation');}return t;}
function feed_v3(raw,now,pack=PACK,roots=ROOTS){const t=wrapper(raw,'feed');need(raw.equals(Buffer.from('self.postMessage('+canonical(t).replaceAll('\u2028','\\u2028').replaceAll('\u2029','\\u2029')+');\n')),'noncanonical_transport');const d=t.data,e=envelope(t.envelope,t.signature,Buffer.from(canonical(d)),'feed',pack,roots);need(typeof now==='number'&&Number.isFinite(now)&&now>0&&now<253402300800,'clock_unavailable');need(d.seq===e.seq&&(!Object.hasOwn(d,'pack')||d.pack===pack)&&d.generated_at===e.created&&d.expires_at===e.expires,'feed_binding');const start=stamp(e.created),end=stamp(e.expires);need(end-start===8*86400&&start<=now&&now<end,'expired_or_future');WATCH_V3.validate(d,now*1000);return t;}
function highwater_v3(records,legacyRecords,now,pack=PACK,roots=ROOTS){need(Array.isArray(records)&&Array.isArray(legacyRecords),'invalid_records');let best=null;const identities=new Map();for(const [rows,validate] of [[legacyRecords,feed],[records,feed_v3]])for(const r of rows){try{const at=stamp(r.accepted_at);need(at<=now&&r.highest_seq===r.envelope.seq,'invalid_record');const t=validate(record(r),at,pack,roots),seq=t.envelope.seq,identity=feed_identity(t.envelope);need(!identities.has(seq)||identities.get(seq)===identity,'equivocation');identities.set(seq,identity);if(!best||seq>best.envelope.seq)best=t;}catch(e){if(e.message==='equivocation')throw e;}}return best;}
function replay_v3(t,records,legacyRecords,now,pack=PACK,roots=ROOTS){const best=highwater_v3(records,legacyRecords,now,pack,roots);if(best){need(t.envelope.seq>=best.envelope.seq,'replay');need(t.envelope.seq!==best.envelope.seq||feed_identity(t.envelope)===feed_identity(best.envelope),'equivocation');}return t;}
function feed_file_v3(file,now,records=[],legacyRecords=[],pack=PACK,roots=ROOTS){return replay_v3(feed_v3(read_local(file,MAX_BYTES),now,pack,roots),records,legacyRecords,now,pack,roots);}
async function fetch_feed_v3(now,records=[],legacyRecords=[],pack=PACK,fetch=get,roots=ROOTS){const good=[];for(const url of FEEDS_V3){try{good.push(feed_v3(await fetch(url),now,pack,roots));}catch(_){}}need(good.length,'unavailable_or_invalid');const identities=new Map();for(const t of good){const e=t.envelope;need(!identities.has(e.seq)||identities.get(e.seq)===feed_identity(e),'equivocation');identities.set(e.seq,feed_identity(e));}good.sort((a,b)=>b.envelope.seq-a.envelope.seq);return replay_v3(good[0],records,legacyRecords,now,pack,roots);}

function target_check(t,to,pack=PACK,roots=ROOTS){exact(t,['package','version','pack','mirrors','install','release','release_sha256','html_sha256','html_size','verifier']);need(t.package==='musterout'&&t.version===to&&t.pack===pack&&canonical(t.mirrors)===canonical(MIRRORS),'target_identity');const i=install(Buffer.from(canonical(t.install)),to,pack,roots);exact(t.release,['envelope','signature']);const e=t.release.envelope;exact(e,['product','kind','version','pack','sha256','size','created','key_id','notes','correction','impact','keychain']);need(e.version===to&&e.pack===pack&&e.product==='Muster Out'&&e.kind==='release','target_identity');const trusted=new Map(Object.entries(roots.release));need(Array.isArray(e.keychain)&&e.keychain.length<=16,'invalid_keychain');for(const l of e.keychain){exact(l,['key_id','public_key','signed_by','signature']);need(!trusted.has(l.key_id)&&trusted.has(l.signed_by),'invalid_keychain');signed(trusted.get(l.signed_by),l.signature,{product:'Muster Out',kind:'release',key_id:l.key_id,public_key:l.public_key,signed_by:l.signed_by});trusted.set(l.key_id,l.public_key);}need(trusted.has(e.key_id),'untrusted_key');signed(trusted.get(e.key_id),t.release.signature,e);const r=i.manifest.release;need(r.sha256===t.release_sha256&&r.html_sha256===e.sha256&&e.sha256===t.html_sha256&&r.html_size===e.size&&e.size===t.html_size&&canonical(i.manifest.notes)===canonical(e.notes),'target_binding');exact(t.verifier,['version','cjs_sha256','py_sha256']);version(t.verifier.version);need(['cjs_sha256','py_sha256'].every(k=>typeof t.verifier[k]==='string'&&/^[a-f0-9]{64}$/.test(t.verifier[k])),'verifier_audit');return t;}
// Registry integrity detects transport corruption only. Publisher signatures remain authority.
const REGISTRY='https://registry.npmjs.org/musterout/';
const MAX_ENTRIES=MAX_FILES+8, MAX_TAR=MAX_TOTAL+MAX_ENTRIES*1024+1024;
function registry_urls(selected){version(selected);return {metadata:REGISTRY+selected,tarball:REGISTRY+'-/musterout-'+selected+'.tgz'};}
function url_limit(url){
 need(typeof url==='string'&&url.length>0&&!/[^\x21-\x7e]/.test(url),'unsafe_url');
 if(FEEDS.includes(url)||FEEDS_V3.includes(url))return MAX_BYTES;
 const v='(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)';
 if(new RegExp('^https://registry\\.npmjs\\.org/musterout/'+v+'$').test(url))return MAX_BYTES;
 if(new RegExp('^https://registry\\.npmjs\\.org/musterout/-/musterout-'+v+'\\.tgz$').test(url))return MAX_TOTAL;
 for(const m of MIRRORS)if(url.startsWith(m)){
  const rest=url.slice(m.length),slash=rest.indexOf('/'),p=rest.slice(slash+1);
  if(slash<0)continue;
  try{version(rest.slice(0,slash));if(p!=='install.json'&&p!=='release.js'){need(p.startsWith('install/'),'unsafe_url');safe_path(p.slice(8));}return MAX_BYTES;}catch(_){}
 }
 throw new Error('unsafe_url');
}
function tar_read(raw){
 need(Buffer.isBuffer(raw)&&raw.length>0&&raw.length<=MAX_TOTAL,'transport_size');
 // Exactly one gzip member. Locate its deflate end before gunzip can process
 // concatenated members; both bounded inflations remain linear in archive size.
 let tar;try{need(raw.length>=18&&raw[0]===31&&raw[1]===139&&raw[2]===8&&!(raw[3]&224),'invalid_gzip');let at=10;const flags=raw[3];
 if(flags&4){need(at+2<=raw.length,'invalid_gzip');at+=2+raw.readUInt16LE(at);}
 for(const flag of [8,16])if(flags&flag){at=raw.indexOf(0,at);need(at>=0,'invalid_gzip');at++;}
 if(flags&2)at+=2;need(at<raw.length-8,'invalid_gzip');
 const first=zlib.inflateRawSync(raw.subarray(at),{maxOutputLength:MAX_TAR,info:true});need(at+first.engine.bytesWritten+8===raw.length,'invalid_gzip');
 const result=zlib.gunzipSync(raw,{maxOutputLength:MAX_TAR,info:true});need(result.engine.bytesWritten===raw.length,'invalid_gzip');tar=result.buffer;}catch(_){throw new Error('invalid_gzip');}
 need(tar.length%512===0,'invalid_tar');
 const files=Object.create(null),seen=new Set();let at=0,total=0,ended=false;
 const text=b=>{const i=b.indexOf(0),end=i<0?b.length:i;need(i<0||b.subarray(i).every(x=>x===0),'invalid_tar');need(b.subarray(0,end).every(x=>x>=32&&x<=126),'invalid_tar');return b.subarray(0,end).toString('ascii');};
 const octal=b=>{need(b.every(x=>x===0||x===32||x>=48&&x<=55),'invalid_tar');const n=b.toString('ascii').replace(/^[\x00 ]+|[\x00 ]+$/g,'');need(/^[0-7]+$/.test(n),'invalid_tar');return parseInt(n,8);};
 while(at+512<=tar.length){
  const h=tar.subarray(at,at+512);
  if(h.every(x=>x===0)){need(at+1024<=tar.length&&tar.subarray(at).every(x=>x===0),'invalid_tar');ended=true;break;}
  const checksum=octal(h.subarray(148,156));let sum=0;for(let i=0;i<512;i++)sum+=i>=148&&i<156?32:h[i];need(sum===checksum,'invalid_tar');
  need(h[156]===0||h[156]===48,'tar_type');need(h.subarray(157,257).every(x=>x===0),'tar_type');
  const prefix=text(h.subarray(345,500)),name=(prefix?prefix+'/':'')+text(h.subarray(0,100));
  need(name.startsWith('package/')&&name.length<=300&&/^[A-Za-z0-9_./-]+$/.test(name)&&name.split('/').every(x=>!['','.','..'].includes(x)),'unsafe_tar_path');
  need(!seen.has(name.toLowerCase()),'duplicate_entry');seen.add(name.toLowerCase());need(seen.size<=MAX_ENTRIES,'file_count');
  const size=octal(h.subarray(124,136));need(size<=MAX_BYTES,'transport_size');total+=size;need(total<=MAX_TOTAL,'aggregate_limit');
  const end=at+512+size,next=at+512+Math.ceil(size/512)*512;need(next<=tar.length&&tar.subarray(end,next).every(x=>x===0),'invalid_tar');
  files[name.slice(8)]=tar.subarray(at+512,end);at=next;
 }
 need(ended&&seen.size>0,'invalid_tar');return files;
}
async function registry_package(selected,fetch=get){
 const u=registry_urls(selected),m=parse(await fetch(u.metadata));
 need(m&&typeof m==='object'&&!Array.isArray(m),'registry_identity');
 need(m.name==='musterout'&&m.version===selected&&m.dist&&m.dist.tarball===u.tarball,'registry_identity');
 need(typeof m.dist.integrity==='string'&&m.dist.integrity.startsWith('sha512-'),'registry_integrity');
 const expected=b64(m.dist.integrity.slice(7),64),raw=await fetch(u.tarball);
 need(Buffer.isBuffer(raw)&&raw.length>0&&raw.length<=MAX_TOTAL,'transport_size');
 need(crypto.createHash('sha512').update(raw).digest().equals(expected),'registry_integrity');return tar_read(raw);
}
function proxy_config(){
 const raw=process.env.HTTPS_PROXY||process.env.https_proxy;if(!raw)return null;
 let p;try{p=new URL(raw);}catch(_){throw Error('unsafe_proxy');}
 need(['http:','https:'].includes(p.protocol)&&p.hostname&&!p.search&&!p.hash&&['','/'].includes(p.pathname),'unsafe_proxy');return p;
}
function proxy_agent(proxy){
 const agent=new https.Agent({keepAlive:false});let connectRequest,tunnel,secure;
 agent.abort=()=>{connectRequest?.destroy();secure?.destroy();tunnel?.destroy();};
 agent.createConnection=(options,callback)=>{
  const host=options.servername||options.host,authority=host+':'+(options.port||443),headers={Host:authority};let completed=false;
  const done=(error,socket)=>{if(completed)return;completed=true;callback(error,socket);};
  if(proxy.username||proxy.password)headers['Proxy-Authorization']='Basic '+Buffer.from(decodeURIComponent(proxy.username)+':'+decodeURIComponent(proxy.password)).toString('base64');
  connectRequest=(proxy.protocol==='https:'?https:http).request({hostname:proxy.hostname.replace(/^\[|\]$/g,''),port:proxy.port||(proxy.protocol==='https:'?443:80),method:'CONNECT',path:authority,headers,agent:false,rejectUnauthorized:true});
  connectRequest.on('connect',(response,socket,head)=>{
   tunnel=socket;if(response.statusCode!==200||head.length){socket.destroy();return done(Error([401,403,407,451].includes(response.statusCode)?'network_policy_refusal':'http_refused'));}
   secure=tls.connect({socket,servername:host,rejectUnauthorized:true});
   secure.once('secureConnect',()=>done(null,secure));secure.once('error',e=>done(e));
  });
  connectRequest.once('error',e=>done(e));connectRequest.setTimeout(20000,()=>{connectRequest.destroy();done(Error('http_timeout'));});connectRequest.end();
 };
 return agent;
}
function get(url){
 const limit=url_limit(url),proxy=proxy_config(),agent=proxy?proxy_agent(proxy):false;
 return new Promise((resolve,reject)=>{
  let done=false,req;const finish=(error,value)=>{if(done)return;done=true;clearTimeout(timer);if(agent){agent.abort();agent.destroy();}error?reject(error):resolve(value);};
  const timer=setTimeout(()=>{req?.destroy();finish(Error('http_timeout'));},20000);
  req=https.get(url,{headers:{'Accept-Encoding':'identity'},agent,rejectUnauthorized:true},res=>{
   if([401,403,407,451].includes(res.statusCode)){res.destroy();return finish(Error('network_policy_refusal'));}
   if(res.statusCode!==200||(res.headers['content-encoding']||'identity')!=='identity'){res.destroy();return finish(Error('http_refused'));}
   let size=0,parts=[];res.on('data',b=>{size+=b.length;if(size>limit){res.destroy();finish(Error('transport_size'));}else parts.push(b);});res.on('end',()=>{if(!size)return finish(Error('transport_size'));finish(null,Buffer.concat(parts));});res.on('error',()=>finish(Error('http_unavailable')));
  });
  req.on('error',e=>finish(Error(['network_policy_refusal','http_refused','http_timeout'].includes(e.message)?e.message:['EACCES','EPERM'].includes(e.code)?'network_policy_refusal':'http_unavailable')));
 });
}
async function retrieve(urls,validate,fetch=get){const good=[];for(const u of urls){try{const raw=await fetch(u);validate(raw);good.push(raw);}catch(_){}}need(good.length,'unavailable_or_invalid');need(good.every(x=>x.equals(good[0])),'mirror_conflict');return good[0];}
function select_update(selected,current){need(compare(selected,V0)>=0&&compare(selected,current)>0,'not_newer');return selected;}
async function fetch_feed(now,records=[],pack=PACK,fetch=get,roots=ROOTS){const good=[];for(const url of FEEDS){try{good.push(feed(await fetch(url),now,pack,roots));}catch(_){}}need(good.length,'unavailable_or_invalid');const identities=new Map();for(const t of good){const e=t.envelope;need(!identities.has(e.seq)||identities.get(e.seq)===feed_identity(e),'equivocation');identities.set(e.seq,feed_identity(e));}good.sort((a,b)=>b.envelope.seq-a.envelope.seq);return replay(good[0],records,now,pack,roots);}
async function stage(selected,parent,pack=PACK,target=null,fetch=get,roots=ROOTS,local=null){version(selected);if(target!==null)target_check(target,selected,pack,roots);else need(compare(selected,V0)>=0,'below_bootstrap_floor');// Cache both success and failure: one registry download per stage, no disk extraction.
let archive=null,registryTried=false;const totals=new Map();
const bounded=async u=>{const key=u.startsWith(REGISTRY)?REGISTRY:MIRRORS.find(m=>u.startsWith(m));need(key&&(totals.get(key)||0)<=MAX_TOTAL,'aggregate_limit');const raw=await fetch(u);need(Buffer.isBuffer(raw)&&raw.length>0&&raw.length<=url_limit(u),'transport_size');totals.set(key,(totals.get(key)||0)+raw.length);need(totals.get(key)<=MAX_TOTAL,'aggregate_limit');return raw;};
const registry=registry_urls(selected).tarball;
const retrieve_path=async(p,validate)=>{
 if(local!==null){need(Object.hasOwn(local,p),'unavailable_or_invalid');validate(local[p]);return local[p];}
 const source=async u=>{
  if(u!==registry)return bounded(u);
  if(!registryTried){registryTried=true;try{archive=await registry_package(selected,bounded);}catch(_){archive=null;}}
  need(archive&&Object.hasOwn(archive,p),'unavailable_or_invalid');return archive[p];
 };
 return retrieve([registry,...MIRRORS.map(m=>m+selected+'/'+p)],validate,source);
};
const iraw=await retrieve_path('install.json',x=>install(x,selected,pack,roots)),i=install(iraw,selected,pack,roots);if(target!==null)need(canonical(i)===canonical(target.install),'target_changed');const rraw=await retrieve_path('release.js',x=>release(x,selected,pack,roots)),files=Object.create(null);for(const [p,sha] of Object.entries(i.manifest.files))files[p]=await retrieve_path('install/'+p,x=>hashcheck(x,sha));const checked=package_check(iraw,rraw,selected,files,pack,roots);need(fs.statSync(parent).isDirectory()&&!fs.lstatSync(parent).isSymbolicLink()&&fs.realpathSync(parent)===path.resolve(parent),'unsafe_stage_parent');const dest=fs.mkdtempSync(path.join(parent,'musterout-public-'));fs.chmodSync(dest,0o700);for(const [p,raw] of Object.entries(files)){safe_path(p);const targetPath=path.join(dest,p);fs.mkdirSync(path.dirname(targetPath),{recursive:true});let q=path.dirname(targetPath);while(q!==path.dirname(q)){need(!fs.lstatSync(q).isSymbolicLink(),'symlink_stage');q=path.dirname(q);}const fd=fs.openSync(targetPath,fs.constants.O_WRONLY|fs.constants.O_CREAT|fs.constants.O_EXCL|fs.constants.O_NOFOLLOW,0o600);try{fs.writeFileSync(fd,raw);}finally{fs.closeSync(fd);}hashcheck(fs.readFileSync(targetPath),i.manifest.files[p]);}return {stage:dest,version:selected,install:checked.install,release:{envelope:checked.release.envelope,signature:checked.release.signature},release_sha256:digest(rraw)};}
function read_local(file,limit){
 const fd=fs.openSync(file,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW|fs.constants.O_NONBLOCK);
 try{const st=fs.fstatSync(fd);need(st.isFile()&&st.size>0&&st.size<=limit,'transport_size');const raw=Buffer.alloc(limit+1);let size=0,n;while(size<=limit&&(n=fs.readSync(fd,raw,size,limit+1-size,null))>0)size+=n;need(size>0&&size<=limit,'transport_size');return raw.subarray(0,size);}finally{fs.closeSync(fd);}
}
function transport_integrity(raw,integrity){if(integrity!==null){need(typeof integrity==='string'&&integrity.startsWith('sha512-'),'registry_integrity');need(crypto.createHash('sha512').update(raw).digest().equals(b64(integrity.slice(7),64)),'registry_integrity');}}
async function stage_tarball(selected,file,parent,pack=PACK,target=null,roots=ROOTS,integrity=null){const raw=read_local(file,MAX_TOTAL);transport_integrity(raw,integrity);return stage(selected,parent,pack,target,()=>{throw Error('offline_network_refused');},roots,tar_read(raw));}
function feed_file(file,now,records=[],pack=PACK,roots=ROOTS){return replay(feed(read_local(file,MAX_BYTES),now,pack,roots),records,now,pack,roots);}
async function main(){preflight();const cmd=process.argv[2];if(cmd==='preflight')return preflight();if(['stage-tarball','stage-resume-tarball','stage-update-tarball'].includes(cmd)){const update=cmd==='stage-update-tarball',resume=cmd==='stage-resume-tarball',n=update?7:6;need(process.argv.length===n||process.argv.length===n+1,'tarball_arguments');const selected=process.argv[3];if(update)select_update(selected,process.argv[4]);const target=resume?parse(fs.readFileSync(0)):null;if(resume)target_check(target,selected);const offset=update?5:4;return stage_tarball(selected,process.argv[offset],process.argv[offset+1],PACK,target,ROOTS,process.argv[offset+2]??null);}if(cmd==='feed-file-v3'){need(process.argv.length===4,'feed_file_arguments');const value=parse(fs.readFileSync(0));return feed_file_v3(process.argv[3],stamp(value.now),value.records||[],value.legacy_records||[],value.pack||PACK);}if(cmd==='feed-file'){need(process.argv.length===4,'feed_file_arguments');const value=parse(fs.readFileSync(0));return feed_file(process.argv[3],stamp(value.now),value.records||[],value.pack||PACK);}if(cmd==='stage-update'){need(process.argv.length===6,'update_requires_target_current_private_parent');select_update(process.argv[3],process.argv[4]);return stage(process.argv[3],process.argv[5]);}if(['stage','stage-resume'].includes(cmd)){need(process.argv.length===5,'stage_requires_version_and_private_parent');const target=cmd==='stage-resume'?parse(fs.readFileSync(0)):null;if(cmd==='stage-resume')target_check(target,process.argv[3]);return stage(process.argv[3],process.argv[4],PACK,target);}const v=parse(fs.readFileSync(0)),raw=v.transport===undefined?null:b64(v.transport,Buffer.from(v.transport,'base64').length);switch(cmd){case'release':return release(raw,v.version,v.pack);case'install':return install(raw,v.version,v.pack);case'feed':{const now=stamp(v.now);return replay(feed(raw,now,v.pack),v.records||[],now,v.pack);}case'feed-v3':{const now=stamp(v.now);return replay_v3(feed_v3(raw,now,v.pack),v.records||[],v.legacy_records||[],now,v.pack);}case'feed-fetch-v3':return fetch_feed_v3(stamp(v.now),v.records||[],v.legacy_records||[],v.pack);case'feed-fetch':return fetch_feed(stamp(v.now),v.records||[],v.pack);case'target':return target_check(v.target,v.version,v.pack);default:throw new Error('unknown_command');}}
module.exports={PACK,ROOTS,MIRRORS,FEEDS,FEEDS_V3,WATCH_V3,feed_v3,highwater_v3,replay_v3,feed_file_v3,fetch_feed_v3,PREFIX,SUFFIX,REQUIRED,OPTIONAL,V0,MAX_BYTES,MAX_TOTAL,MAX_TAR,REGISTRY,registry_urls,url_limit,proxy_config,tar_read,registry_package,read_local,transport_integrity,stage_tarball,feed_file,canonical,parse,wrapper,b64,preflight,envelope,release,install,package_check,feed,feed_shape,highwater,replay,target_check,stage,select_update,fetch_feed,get,retrieve,hashcheck,safe_path,stamp,day,version,digest,record,feed_identity};
if(require.main===module)main().then(v=>process.stdout.write(canonical(v)+'\n')).catch(e=>{process.stderr.write(JSON.stringify({error:/^[a-z_]{1,80}$/.test(e.message)?e.message:'verification_failed'})+'\n');process.exitCode=1;});
