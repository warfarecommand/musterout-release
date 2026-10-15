/* Lossless transport decoding. Full SHA-256 digests and item scope stay intact. */
(function(root){'use strict';
 function decode(value){
  if(!value||typeof value!=='object')throw Error('Invalid fingerprint map');
  if(value.format===undefined)return value;
  if(value.format!==2||!Array.isArray(value.digests)||!Array.isArray(value.shapes)||value.shapes.length!==value.digests.length||new Set(value.digests).size!==value.digests.length||value.digests.some(h=>typeof h!=='string'||!/^[a-f0-9]{64}$/.test(h)))throw Error('Invalid fingerprint dictionary');
  const hash=n=>{if(!Number.isSafeInteger(n)||n<0||n>=value.digests.length)throw Error('Invalid fingerprint index');return value.digests[n];};
  const map=v=>{if(!v||Array.isArray(v)||typeof v!=='object')throw Error('Invalid fingerprint map');return v;};
  const out={...value};delete out.format;delete out.digests;
  out.versions=Object.fromEntries(Object.entries(map(value.versions)).map(([v,items])=>[v,Object.fromEntries(Object.entries(map(items)).map(([id,n])=>[id,hash(n)]))]));
  out.shapes=Object.fromEntries(value.digests.map((h,n)=>{const s=value.shapes[n];if(!s||typeof s.setup!=='boolean'||!Array.isArray(s.when))throw Error('Invalid fingerprint shape');return [h,s];}));
  out.variants=Object.fromEntries(Object.entries(map(value.variants)).map(([id,indices])=>{if(!Array.isArray(indices))throw Error('Invalid fingerprint variants');return [id,indices.map(hash)];}));return out;
 }
 root.MusterOutFingerprints=Object.freeze({decode});
})(globalThis);
