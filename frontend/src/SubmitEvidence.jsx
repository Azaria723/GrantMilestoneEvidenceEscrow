import React,{useState} from 'react';
import {evidenceUrl} from './forms.js';
export default function SubmitEvidence({grant,milestone,onSubmit,disabled}){
 const [e,setE]=useState(''),[d,setD]=useState(''),[hash,setHash]=useState('');
 const nonce=milestone.attempts+1;
 return <form className="create-form" onSubmit={event=>{event.preventDefault();onSubmit([BigInt(milestone.milestone_id),BigInt(nonce),e,d,hash])}}><h4>Submit delivery · nonce {nonce}</h4><p>Commit artifacts first (D), then the identity-bound manifest (E). SHA-256 must hash the exact manifest bytes.</p><label>Deliverable commit D<input required pattern="[a-fA-F0-9]{40}" value={d} onChange={event=>setD(event.target.value)}/></label><label>Evidence commit E<input required pattern="[a-fA-F0-9]{40}" value={e} onChange={event=>setE(event.target.value)}/></label><label>Manifest SHA-256<input required pattern="[a-fA-F0-9]{64}" value={hash} onChange={event=>setHash(event.target.value)}/></label><p className="break">{evidenceUrl(grant.repository,e||'<E>',grant.grant_id,milestone.local_index,nonce)}</p><button disabled={disabled||nonce>8}>Submit immutable evidence</button></form>
}
