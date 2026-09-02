import {createHash} from 'node:crypto';
const E='a9286a3f13c3274077ed2ec786a08e8a959ce9d0';
for(const n of [1,2]){
 const url=`https://raw.githubusercontent.com/Azaria723/GrantMilestoneEvidenceEscrow/${E}/evidence/grant-0/milestone-0/submission-${n}.json`;
 const response=await fetch(url);const bytes=Buffer.from(await response.arrayBuffer());
 if(response.status!==200)throw new Error(`HTTP ${response.status}`);
 const manifest=JSON.parse(bytes.toString());
 const artifact=await fetch(manifest.deliverables[0].url);const body=Buffer.from(await artifact.arrayBuffer());
 const hash=b=>createHash('sha256').update(b).digest('hex');
 console.log(JSON.stringify({nonce:n,url,sha256:hash(bytes),artifact_status:artifact.status,artifact_digest_matches:hash(body)===manifest.deliverables[0].sha256}));
}
