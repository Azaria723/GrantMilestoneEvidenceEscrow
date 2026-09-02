export function genToWei(value){
 if(!/^(0|[1-9]\d*)(\.\d{1,18})?$/.test(value))throw new Error('GEN must be a decimal with at most 18 fractional digits.');
 const [whole,fraction='']=value.split('.');const result=BigInt(whole)*10n**18n+BigInt(fraction.padEnd(18,'0'));
 if(result<=0n||result>=2n**256n)throw new Error('Amount is outside the allowed range.');return result;
}
export function buildPlan(rows){
 if(rows.length<1||rows.length>6)throw new Error('Use 1–6 milestones.');let previous=0;
 const plan=rows.map(r=>{const deadline=Number(r.seconds);if(!Number.isInteger(deadline)||deadline<300||deadline>31536000||deadline<=previous)throw new Error('Deadlines must increase and be between 300 and 31536000 seconds.');previous=deadline;if(!r.criteria.trim()||r.criteria.length>1200)throw new Error('Enter bounded acceptance criteria.');return {amount_wei:genToWei(r.gen).toString(),deadline_seconds:deadline,criteria:r.criteria.trim()}});
 const value=plan.reduce((s,r)=>s+BigInt(r.amount_wei),0n);if(value>=2n**256n)throw new Error('Total amount is too large.');return {plan,value};
}
export function evidenceUrl(repository,revision,grant,index,nonce){return `https://raw.githubusercontent.com/${repository}/${revision.toLowerCase()}/evidence/grant-${grant}/milestone-${index}/submission-${nonce}.json`}
