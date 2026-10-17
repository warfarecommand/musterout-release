/* RG3 is a separate protocol. Canonical POST bytes reject duplicate JSON keys. */
(function(root){
'use strict';
const campaigns=Object.freeze([]); // Release-controlled public campaign slugs only.
const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.keys(x).sort().map(k=>[k,x[k]])):x);
const object=v=>!!v&&typeof v==='object'&&!Array.isArray(v);
const keys=(v,list)=>object(v)&&Object.keys(v).length===list.length&&list.every(k=>Object.hasOwn(v,k));
const hex=v=>typeof v==='string'&&v.length===32&&/^[a-f0-9]{32}$/.test(v);
const boardKey=v=>typeof v==='string'&&[16,32].includes(v.length)&&/^(?:[a-f0-9]{16}|[a-f0-9]{32})$/.test(v);
const version=v=>typeof v==='string'&&v.length<=32&&!/\s/.test(v)&&/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.test(v);
const integer=(v,max)=>Number.isInteger(v)&&v>=0&&v<=max;
const day=v=>v===null||typeof v==='string'&&v.length===10&&/^\d{4}-\d{2}-\d{2}$/.test(v)&&Number.isFinite(Date.parse(v))&&new Date(v).toISOString().slice(0,10)===v;
const bucket=v=>keys(v,['bucket_id','week_index','revision','opens','done_actions'])&&hex(v.bucket_id)&&integer(v.week_index,104)&&integer(v.revision,10000)&&v.revision>0&&integer(v.opens,10000)&&integer(v.done_actions,10000);
function valid(v){
 if(!object(v)||v.schema_version!==3||!boardKey(v.board_key))return false;
 if(v.kind==='delete')return keys(v,['schema_version','kind','board_key']);
 if(!version(v.version))return false;
 if(v.kind==='registration')return keys(v,['schema_version','kind','board_key','version','path','grade_band','campaign','setup_date'])&&[null,'eas','retire','resign'].includes(v.path)&&[null,'e15','e67','e89','o14','o5','wo13','cwo45'].includes(v.grade_band)&&(v.campaign===null||typeof v.campaign==='string'&&/^[a-z0-9][a-z0-9_-]{0,31}$/.test(v.campaign)&&campaigns.includes(v.campaign))&&day(v.setup_date);
 return v.kind==='usage'&&keys(v,['schema_version','kind','board_key','version','buckets'])&&Array.isArray(v.buckets)&&v.buckets.length>0&&v.buckets.length<=8&&v.buckets.every(bucket)&&new Set(v.buckets.map(b=>b.bucket_id)).size===v.buckets.length;
}
function parse(text){const v=JSON.parse(text);if(!valid(v)||canonical(v)!==text||new TextEncoder().encode(text).length>(v.kind==='usage'?4096:768))throw Error('invalid');return v;}
// The version travels explicitly, so receiver upgrades cannot alter frozen cohorts.
// Nulls have a single readable spelling; an absent campaign stays absent.
function encode(v){
 if(!valid(v))throw Error('invalid');
 if(v.kind==='delete')return 'd3.'+v.board_key;
 if(v.kind!=='registration'||!/^[a-f0-9]{16}$/.test(v.board_key))throw Error('invalid');
 const fields=['v3',v.path||'none',v.grade_band||'none',v.setup_date?v.setup_date.replaceAll('-',''):'none',v.board_key,v.version.replaceAll('.','-')];
 if(v.campaign!==null)fields.push(v.campaign);
 const fragment=fields.join('.');
 if(fragment.length+1>=60)throw Error('too_long');
 return fragment;
}
function decode(fragment){
 if(typeof fragment!=='string'||/[^a-z0-9_.-]/.test(fragment))throw Error('invalid');
 if(/^d3\.(?:[a-f0-9]{16}|[a-f0-9]{32})$/.test(fragment))return {schema_version:3,kind:'delete',board_key:fragment.slice(3)};
 if(fragment.length+1>=60)throw Error('invalid');
 const fields=fragment.split('.');
 if(![6,7].includes(fields.length)||fields[0]!=='v3'||!/^[a-f0-9]{16}$/.test(fields[4]))throw Error('invalid');
 const date=fields[3]==='none'?null:/^\d{8}$/.test(fields[3])?fields[3].slice(0,4)+'-'+fields[3].slice(4,6)+'-'+fields[3].slice(6):'';
 const v={schema_version:3,kind:'registration',path:fields[1]==='none'?null:fields[1],grade_band:fields[2]==='none'?null:fields[2],setup_date:date,board_key:fields[4],version:fields[5].replaceAll('-','.'),campaign:fields.length===7?fields[6]:null};
 if(!valid(v)||encode(v)!==fragment)throw Error('invalid');
 return v;
}
function random(bytes=16){return Array.from(crypto.getRandomValues(new Uint8Array(bytes)),b=>b.toString(16).padStart(2,'0')).join('');}
// Retained batches rotate after a native handoff; no sent revision is inferred.
function batch(rows,cursor,now){const eligible=rows.filter(x=>x.created_at+180*86400000>now&&bucket(x.bucket)).sort((a,b)=>a.created_at-b.created_at||a.bucket.bucket_id.localeCompare(b.bucket.bucket_id));const start=eligible.length?cursor%eligible.length:0;return {rows:eligible.slice(start).concat(eligible.slice(0,start)).slice(0,8),cursor:eligible.length?(start+8)%eligible.length:0};}
const utf8base64=text=>btoa(Array.from(new TextEncoder().encode(text),b=>String.fromCharCode(b)).join('')).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
function envelope(registration,usage,report){if(!valid(registration)||registration.kind!=='registration'||usage&&(!valid(usage)||usage.kind!=='usage'||usage.board_key!==registration.board_key))throw Error('invalid');let value={schema_version:3,registration,usage:usage||null,report:report||null};const token=()=> 'h3.'+utf8base64(canonical(value));while(token().length>8192&&value.usage?.buckets.length){value.usage={...value.usage,buckets:value.usage.buckets.slice(0,-1)};if(!value.usage.buckets.length)value.usage=null;}if(token().length>8192)return null;return token();}
function decodeEnvelope(fragment){if(fragment.length>8192||!/^h3\.[A-Za-z0-9_-]+$/.test(fragment))throw Error('invalid');const bytes=Uint8Array.from(atob(fragment.slice(3).replace(/-/g,'+').replace(/_/g,'/')),c=>c.charCodeAt(0));const text=new TextDecoder('utf-8',{fatal:true}).decode(bytes),v=JSON.parse(text);if(!keys(v,['schema_version','registration','usage','report'])||v.schema_version!==3||canonical(v)!==text||!valid(v.registration)||v.registration.kind!=='registration'||v.usage!==null&&(!valid(v.usage)||v.usage.kind!=='usage'||v.usage.board_key!==v.registration.board_key)||v.report!==null&&!object(v.report)||envelope(v.registration,v.usage,v.report)!==fragment)throw Error('invalid');return v;}
root.MusterOutRG3=Object.freeze({campaigns,canonical,keys,hex,boardKey,version,day,bucket,valid,parse,encode,decode,random,batch,envelope,decodeEnvelope});
})(globalThis);
