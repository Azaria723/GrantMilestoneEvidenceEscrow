# Studionet lifecycle ledger

Contract: `0x37Eb0776f03fa1C18ac9F0F327335dfE9388b420` · Studionet 61999 · 2026-09-02.

Only executed cases appear below. Full RPC receipts are stored in `verification/receipts/`. Explorer base: `https://explorer-studio.genlayer.com/transactions/<hash>`.

| Case | Actor | Method / transaction | Observed result |
|---|---|---|---|
| Source parity | Read only | `getContractCode/schema/counts/accounting` | Deployed/local SHA-256 both `78dcfad5…5096c`; 13 ABI methods; zero initial state. |
| Fund grant #0 | Sponsor | `create_grant` · `0xaf3d12277e9b6452e1322d1f0721eec8f4e54e07861aa626e2a5b63248ac69b5` | FINALIZED, consensus success; exact 0.001 GEN custody and one milestone created. |
| Claim | Recipient | `claim_milestone(0)` · `0x2f6823431e969d52427fe782f47309eab719e3f321c70609c794ccb84b60a4e8` | FINALIZED; milestone CLAIMED. |
| Forged identity submit | Recipient | nonce 1 · `0x8e2419c26bb422b58f582672fefe28abbc4f91b1ebdf4552bfb575fa57fe128a` | Exact manifest digest submitted. |
| Forged identity assess | Sponsor | `0xec969295eab4b26ee9bb6e3ea6c401f4f325fb927927b77a4e52866d53939826` | FINALIZED; digest PASS, binding FAIL, REJECTED. |
| Rejected payout attempt | Sponsor | `0x0e1abedd1368b95b29670c06cbe4bc7c716e3fc0253b84ec2d0ce5263cbe6b75` | `MILESTONE_NOT_APPROVED`; custody unchanged. |
| Wrong-actor refund | Recipient | `0x42599e1452983378d6caca7ba6045b6fa8d2076a5a904753c05db4c9403abeae` | `SPONSOR_ONLY`; state unchanged. |
| Incomplete delivery | Recipient/sponsor | submit `0xf802655362c0ef8623eacb7d93a28f9ef84648f347280b5bce054dd783eb70ea`; assess `0xfe00d822c75fb378bb8cdad29d120cbf4e3007f4f633323d45fe8350577c1aeb` | Digest/binding/artifact PASS, criteria FAIL, REJECTED. |
| Corrected delivery | Recipient | nonce 3 submit `0x8a60a1ed8cca95ec4656f59609a86564b8cb5a4588091c4e8cbb5882ec64dbff` | FINALIZED; old nonce history retained. |
| Positive assessment | Sponsor | `0x0419e80ce0f4b99c1701a66324e39ed6bd6b2f719ca5d61b37aa5daef62fd9b2` | Consensus success; digest/binding/deliverables/criteria all PASS; APPROVED. |
| Approved expiry protection | Sponsor | expire `0x09edb6e9f39c66b3de423f9aa965317b1ea64e82c4ad8a798b733c8946b96c8e` | `MILESTONE_NOT_EXPIRABLE`; still APPROVED. |
| Approved refund protection | Sponsor | refund `0x3795c94b404cc6137001955da71c69ec625390bfa1451e26d79a52a881533596` | `MILESTONE_NOT_EXPIRED`; still APPROVED. |
| Payout | Recipient | `0x42d7d702fb135a44d2c7703ed04e9cdcb39fa9f48fee52ca442ddbf8ec41dabe` | FINALIZED; return `MILESTONE_PAID`; receipt contains 0.001 GEN transfer to stored recipient. Contract balance/active_locked 0; total_paid 0.001 GEN. |
| Payout replay | Recipient | `0x02d6e06a3fa6c3b5fcf5f3bbcb9255cbe690a7b8614a4c4673c75873b2dbc1b7` | `MILESTONE_NOT_APPROVED`; accounting unchanged. |

Final state: grant 0 / milestone 0 is PAID (4), attempt 3. Accounting: deposited 1000000000000000, paid 1000000000000000, refunded 0, active_locked 0. Contract balance is 0.

Frontend localhost readback after refresh showed: custody 0.0 GEN, deposited/released 0.001 GEN, 1 grant, 1 milestone, PAID. No browser console errors were observed. This is local browser integration evidence, not a hosted deployment claim.
