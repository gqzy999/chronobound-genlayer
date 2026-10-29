// Read-only: no accounts, signatures, deployments or writes.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createClient,abi} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import {TransactionHashVariant} from 'genlayer-js/types';
const root=path.resolve(import.meta.dirname,'..');
const e=JSON.parse(fs.readFileSync(path.join(root,'evidence/studionet.json')));
const client=createClient({chain:studionet});assert.equal(Number(await client.getChainId()),61999);
const source=fs.readFileSync(path.join(root,'contracts/chrono_bound.py'),'utf8');assert.equal(crypto.createHash('sha256').update(source).digest('hex'),e.sourceSha256);assert.equal(await client.getContractCode(e.address),source);
const r=JSON.parse(await client.readContract({address:e.address,functionName:'get_schedule',args:[e.owner,'archive-demo'],transactionHashVariant:TransactionHashVariant.LATEST_FINAL}));assert.deepEqual(r,e.record);assert.equal(r.status,'CERTIFIED');
for(const [name,t] of Object.entries(e.transactions)){
 const tx=await client.getTransaction({hash:t.hash});
 assert.equal(tx.statusName,'FINALIZED');assert.equal(tx.resultName||tx.result_name,'MAJORITY_AGREE');assert.equal(tx.txExecutionResultName||tx.consensus_data?.leader_receipt?.find(x=>x.mode==='leader')?.execution_result,'SUCCESS');assert.equal(tx.leader_only,false);
 assert.equal(tx.from_address.toLowerCase(),t.signer.toLowerCase());assert.equal(tx.to_address.toLowerCase(),e.address.toLowerCase());
 if(t.method==='deploy')assert.equal(Buffer.from(tx.data.contract_code,'base64').toString(),source);
 else{const call=abi.calldata.decode(Buffer.from(tx.data.calldata.base64,'base64'));assert.equal(call.get('method'),t.method);assert.deepEqual(JSON.parse(JSON.stringify(call.get('args'),(_,v)=>typeof v==='bigint'?Number(v):v)),t.args);}
 console.log(name,t.hash,'FINALIZED');
}

function sorted(v){if(Array.isArray(v))return v.map(sorted);if(v!==null&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,sorted(v[k])]));return v;}
function fingerprint(v){const text=JSON.stringify(sorted(v)).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));return crypto.createHash('sha256').update(text).digest('hex');}
const binding=Object.fromEntries(['protocol','owner','id','plan','bounds','proof'].map(k=>[k,r[k]]));assert.equal(fingerprint(binding),r.digest);
assert.deepEqual(r.proof.ranges,[[0,0],[30,60],[150,180]]);
const times=r.proof.times;assert.equal(times[0],0);assert.ok(times.every(t=>t>=0&&t<=r.plan.horizon));
for(const [i,b] of r.bounds.entries()){const rule=r.plan.rules[i],delta=times[rule.to]-times[rule.from];assert.equal(b.status,'KNOWN');assert.equal(b.source,rule.text);if(b.lower!==null)assert.ok(delta>=b.lower);if(b.upper!==null)assert.ok(delta<=b.upper);}
for(const edge of r.proof.edges)assert.ok(times[edge.to]-times[edge.from]<=edge.weight);
console.log('VERIFIED: source, exact transactions, full consensus, final state, digest and schedule witness.');
