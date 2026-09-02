import {createClient} from '../frontend/node_modules/genlayer-js/dist/index.js';
import {studionet} from '../frontend/node_modules/genlayer-js/dist/chains/index.js';
import {TransactionStatus} from '../frontend/node_modules/genlayer-js/dist/types/index.js';
import {privateKeyToAccount} from '../frontend/node_modules/viem/_esm/accounts/index.js';
import {writeFile,mkdir} from 'node:fs/promises';
const encode=v=>JSON.stringify(v,(_,x)=>typeof x==='bigint'?x.toString():x,null,2);
async function record(receipt){await mkdir(new URL('../verification/receipts/',import.meta.url),{recursive:true});await writeFile(new URL(`../verification/receipts/${receipt.hash}.json`,import.meta.url),encode(receipt));console.log(encode({hash:receipt.hash,status:receipt.status,status_name:receipt.status_name,result:receipt.result_name,execution:receipt.consensus_data?.leader_receipt?.[0]?.execution_result}));}
const address='0x37Eb0776f03fa1C18ac9F0F327335dfE9388b420';
const reader=createClient({chain:studionet});
const [mode,method,raw='[]',value='0']=process.argv.slice(2);
const args=JSON.parse(raw).map(v=>typeof v==='number'?BigInt(v):v);
if(mode==='read')console.log(await reader.readContract({address,functionName:method,args}));
else if(mode==='wallet')console.log(privateKeyToAccount(`0x${process.env.TEST_KEY.replace(/^0x/,'')}`).address);
else if(mode==='receipt')await record(await reader.getTransaction({hash:method}));
else if(mode==='balances'){
 for(const a of [address,'0x67A1A08Fc4cf7D05c859d0d3D8398a3A30B1677e','0x7C87B10a3d43F3b3551414401F8b26B9F662bAB5'])console.log(encode({address:a,balance:(await reader.getBalance({address:a})).toString()}));
}
else if(mode==='write'){
 const account=privateKeyToAccount(`0x${process.env.TEST_KEY.replace(/^0x/,'')}`);
 const client=createClient({chain:studionet,account});
 const hash=await client.writeContract({address,functionName:method,args,value:BigInt(value)});
 console.log(JSON.stringify({hash,method,sender:account.address}));
 const receipt=await reader.waitForTransactionReceipt({hash,status:TransactionStatus.FINALIZED});
 await record(receipt);
}else throw new Error('Use read, wallet, receipt or write');
