import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {generateKeyPairSync,sign,createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {verifyFeed,verifyBundle,preparePackage} from './verify_publish.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const canonical=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canonical).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';
const {privateKey,publicKey}=generateKeyPairSync('ed25519'),pub=publicKey.export({format:'der',type:'spki'}).subarray(-32).toString('base64');
const roots={feed_keys:{test:pub}},env={MO_FEED_PUBLIC_KEY:pub,MO_FEED_KEY_ID:'test'};
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'v32-publish-'));
function write(name,value){const dest=path.join(tmp,name);fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,value);}
function transport(data){const raw=canonical(data),e={product:'Muster Out',kind:'feed',seq:data.seq,pack:'usmc-2026.10',sha256:createHash('sha256').update(raw).digest('hex'),size:Buffer.byteLength(raw),created:data.generated_at,expires:data.expires_at,key_id:'test',keychain:[]};return 'self.postMessage('+canonical({envelope:e,signature:sign(null,Buffer.from(canonical(e)),privateKey).toString('base64'),data}).replaceAll('\u2028','\\u2028').replaceAll('\u2029','\\u2029')+');\n';}
try{
 for(const name of ['validate_v1.py','validate_v2.py','validate_v3.py','watch_contract.py'])write('feed/'+name,fs.readFileSync(path.join(here,name)));
 const legacy=JSON.parse(fs.readFileSync(path.join(here,'fixtures/legacy.json'))),modern=JSON.parse(fs.readFileSync(path.join(here,'fixtures/page.json')));
 Object.assign(modern,{schema_version:3,seq:legacy.seq+1,legacy_seq:legacy.seq,legacy_sha256:createHash('sha256').update(canonical(legacy)).digest('hex')});
 write('config.json',JSON.stringify({product:'Muster Out',pack:'usmc-2026.10',update_keys:{feed_keys:roots.feed_keys,release_keys:{release:'different'}}}));
 write('npm/musterout-feed/public_keys.json',JSON.stringify(roots));
 write('npm/musterout-feed/package.json',JSON.stringify({name:'musterout-feed',version:'1.0.0',license:'SEE LICENSE IN LICENSE',files:['feed.js','LICENSE','NOTICE.md'],repository:{type:'git',url:'https://github.com/warfarecommand/musterout-release.git'}}));
 for(const [profile,data] of [['v2',legacy],['v3',modern]]){write('feed/'+profile+'/latest.json',canonical(data));write('feed/'+profile+'/feed.js',transport(data));}
 assert.equal(verifyFeed(tmp,env).seq,legacy.seq);
 const bundle=verifyBundle(tmp,env);assert.equal(bundle.seq,modern.seq);assert.equal(bundle.legacySeq,legacy.seq);
 assert.throws(()=>preparePackage(tmp,bundle,'1.0.'+legacy.seq),/must advance/);
 assert(preparePackage(tmp,bundle,'1.0.'+(legacy.seq-1)));
 assert.equal(fs.readFileSync(path.join(tmp,'npm/musterout-feed/feed.js'),'utf8'),transport(legacy));
 assert.equal(fs.readFileSync(path.join(tmp,'npm/musterout-feed/v3/feed.js'),'utf8'),transport(modern));
 assert.deepEqual(JSON.parse(fs.readFileSync(path.join(tmp,'npm/musterout-feed/package.json'))).files,['feed.js','v3/feed.js','LICENSE','NOTICE.md']);
 for(const name of ['LICENSE','NOTICE.md'])write('npm/musterout-feed/'+name,fs.readFileSync(path.join(here,'../npm/musterout-feed',name)));
 const packed=JSON.parse(execFileSync('npm',['pack','--ignore-scripts','--json'],{cwd:path.join(tmp,'npm/musterout-feed'),encoding:'utf8'}))[0];
 assert.deepEqual(packed.files.map(f=>f.path).sort(),['LICENSE','NOTICE.md','feed.js','package.json','v3/feed.js'].sort());
 for(const [name,expected] of [['feed.js',transport(legacy)],['v3/feed.js',transport(modern)]])assert.equal(execFileSync('tar',['-xOf',path.join(tmp,'npm/musterout-feed',packed.filename),'package/'+name],{encoding:'utf8'}),expected);
 assert.equal(preparePackage(tmp,verifyBundle(tmp,env),'1.0.'+modern.seq),false);
 assert.throws(()=>verifyFeed(tmp,env),/Unexpected package files/);
 // REFV32 duplicate_projection_key: preserve intentionally pretty JSON, reject ambiguity.
 write('feed/v3/latest.json',' \n'+JSON.stringify(modern,null,2)+'\n');verifyBundle(tmp,env);
 for(const duplicate of ['{"seq":0,'+canonical(modern).slice(1),canonical(modern).replace('"source":"VA_GOV"','"source":"FAKE","source":"VA_GOV"')]){
  write('feed/v3/latest.json',duplicate);
  assert.throws(()=>verifyBundle(tmp,env),/duplicate/i,'REFV32 F02 duplicate projection accepted');
 }
 write('feed/v3/latest.json',canonical(modern));
 // REFV32-F05: translated from evidence-r2/harness/large_publish_probe.py.
 // The same 500-notice ALMAR/ALNAV construction must pass sync and both publisher entry points.
 const largeLegacy=structuredClone(legacy),largeModern=structuredClone(modern),template=structuredClone(legacy.sources[0].notices[0]);
 for(const feed of [largeLegacy,largeModern])for(const source of ['ALMAR','ALNAV']){
  const block=feed.sources.find(b=>b.source===source);block.notices=[];
  for(let i=1;i<=500;i++)block.notices.push({...structuredClone(template),
   number:i+'/26',id:source+'-'+i+'-26',series:source,title:'A'.repeat(300),summary:'B'.repeat(1000),description:'D',
   url:source==='ALMAR'?'https://www.marines.mil/News/Messages/Messages-Display/Article/1234567/example/':'https://www.mynavyhr.navy.mil/References/Messages/example/',
   posted:block.window.to,body_available:false,applicability:{},applicability_evidence:{}});
  block.checked_count=500;
 }
 largeModern.legacy_sha256=createHash('sha256').update(canonical(largeLegacy)).digest('hex');
 const largeRoot=path.join(tmp,'large'),downloads=path.join(tmp,'large-download');
 for(const name of ['validate_v1.py','validate_v2.py','validate_v3.py','watch_contract.py'])write('large/feed/'+name,fs.readFileSync(path.join(here,name)));
 write('large/config.json',fs.readFileSync(path.join(tmp,'config.json')));
 write('large/npm/musterout-feed/public_keys.json',JSON.stringify(roots));
 const largePkg=JSON.parse(fs.readFileSync(path.join(tmp,'npm/musterout-feed/package.json')));largePkg.files=['feed.js','LICENSE','NOTICE.md'];
 write('large/npm/musterout-feed/package.json',JSON.stringify(largePkg));
 write('large-download/latest.json',fs.readFileSync(path.join(here,'fixtures/v1.json')));
 for(const [profile,data] of [['v2',largeLegacy],['v3',largeModern]]){
  write('large-download/'+profile+'/latest.json',canonical(data));write('large-download/'+profile+'/feed.js',transport(data));
 }
 const projectionBytes=fs.statSync(path.join(downloads,'v3/latest.json')).size,wrapperBytes=fs.statSync(path.join(downloads,'v3/feed.js')).size;
 assert(projectionBytes>1024*1024&&projectionBytes<2000000,'F05 control must lie between 1 MiB and the projection wire cap');
 assert(wrapperBytes>1024*1024&&wrapperBytes<2000000,'F05 wrapper must also remain under the wire cap');
 execFileSync('python3',['-B',path.join(here,'sync.py'),'--downloads',downloads,'--target',path.join(largeRoot,'feed'),'--profile','v3'],
  {env:{...process.env,...env},stdio:['ignore','ignore','pipe'],maxBuffer:65536});
 assert.equal(verifyFeed(largeRoot,env,'v3').seq,largeModern.seq);
 assert.equal(verifyBundle(largeRoot,env).seq,largeModern.seq);
 // Duplicate rejection must precede parsing even for a large, otherwise valid projection.
 write('large/feed/v3/latest.json','{"seq":0,'+canonical(largeModern).slice(1));
 assert.throws(()=>verifyBundle(largeRoot,env),/duplicate/i,'F05 large duplicate projection accepted');
 write('large/feed/v3/latest.json',canonical(largeModern));
 console.log('PASS F05: '+projectionBytes+'-byte v3 projection, '+wrapperBytes+'-byte wrapper; sync, verifyFeed and verifyBundle accept; large duplicate rejects');
 const bad=structuredClone(modern);bad.legacy_sha256='0'.repeat(64);write('feed/v3/latest.json',canonical(bad));write('feed/v3/feed.js',transport(bad));assert.throws(()=>verifyBundle(tmp,env));
 console.log('PASS: legacy-only, dual bundle, exact packaged bytes, monotonic roots, retry and signed pair rejection');
}finally{fs.rmSync(tmp,{recursive:true,force:true});}
