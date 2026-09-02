import test from 'node:test';
import assert from 'node:assert/strict';
import {genToWei,buildPlan,evidenceUrl} from './forms.js';
test('exact wei without floating point',()=>{assert.equal(genToWei('0.000000000000000001'),1n);assert.equal(genToWei('123.001'),123001000000000000000n)});
test('reject invalid amounts',()=>{for(const v of ['0','-1','1e3','1.0000000000000000001','NaN'])assert.throws(()=>genToWei(v))});
test('creation plan contains no future evidence',()=>{const {plan,value}=buildPlan([{gen:'0.001',seconds:'86400',criteria:'Build tool'}]);assert.equal(value,10n**15n);assert.deepEqual(Object.keys(plan[0]),['amount_wei','deadline_seconds','criteria'])});
test('deadlines strictly increase',()=>assert.throws(()=>buildPlan([{gen:'1',seconds:'300',criteria:'A'},{gen:'1',seconds:'300',criteria:'B'}])));
test('manifest path binds submission nonce',()=>assert.equal(evidenceUrl('a/b','C'.repeat(40),2,1,3),`https://raw.githubusercontent.com/a/b/${'c'.repeat(40)}/evidence/grant-2/milestone-1/submission-3.json`));
