# EF27 deployment and settlement proof — 2026-09-05

Contract: `0xEF27Ee5207071E1e8795bbCD00459c64d2Be85C3`  
Network: Studionet, chain ID 61999.

## Source parity

- Deployed source SHA-256: `cbde39e984f3e82f315740bb570d9412c50f4effb5d2dd8d9a4fb1c55bb14302`
- Local source SHA-256: `cbde39e984f3e82f315740bb570d9412c50f4effb5d2dd8d9a4fb1c55bb14302`
- Exact source parity: true
- ABI: 6 view and 9 write methods, including two-argument `pay_milestone` and `reconcile_settlement`.

## Live lifecycle

| Step | Transaction | Result |
|---|---|---|
| Create grant with 0.001 GEN | `0xd0173fdde640a84965795ca31374a85ae13832945013ff9a711cc91dde3f7728` | FINALIZED / SUCCESS; exact custody locked |
| Recipient claim | `0xfadb5a079a332daf4e28e77973c0d087689ed97739e2ddda8f9a414820177a9e` | FINALIZED |
| Bad manifest submit / assess | `0xc5a6c59b60f7bac5e4b608383c72897fe4380cd8148381f22da2340b17139c5f` / `0x603744fb4dadf5b7369316d9cff1be6cd585bc0e1a52c0a4871d4dbfb6f6152b` | Digest mismatch rejected; custody unchanged |
| Correct binding but stale document | `0xae96ee9d3e933f00eb381bf71d3a2c8f2725c2b0e5291890943ce301dfd284c0` / `0x35a6eb1f79b46085c21a877ee23d43d2f977340fbacfd141748eb2b4c1b98960` | Digest, binding, artifacts PASS; semantic criteria FAIL; custody unchanged |
| Correct delivery submit / assess | `0xdf2861904611f6a3cae8c7a773f7b8e3290aed519764c2f06b743d34f1837cb2` / `0xcb3390c8bace37aad1c0b9696909b7192ded0ad45baba5eee9640f95d0cf957f` | Digest, binding, deliverables and criteria PASS; APPROVED |
| Payout request | `0x3d7457a95303f5cbbfc64aa165b4de912922c0b855bb747e716bcd949e392135` | FINALIZED / SUCCESS; state stayed APPROVED with settlement PENDING |
| Linked recipient SEND | `0x5a1d6d6b74b13a66ebf2853af3a98eb9357b4d838f41948567ebcfdc3c02ccfb` | FINALIZED, type 0, exact 0.001 GEN, `value_credited=true` |
| Reconciliation | `0x5bffc3f434a29f07e205f48816d2e8c4f3ed6c8f8bd81c1d15490e6390fe9a96` | FINALIZED / SUCCESS; returned MILESTONE_PAID |

## Recipient-side proof

- Recipient EOA: `0xc67532aeF9D2879cBA9375a02E6217A3524657B8`
- Balance before: `199907001999999999998` wei
- Balance after: `199908001999999999998` wei
- Exact delta: `1000000000000000` wei (0.001 GEN)
- Child sender: corrected contract
- Child `triggered_by`: payout request hash
- Child type: `0` (`SEND`)
- Child `value_credited`: `true`

The proof runner measured the before/after balance and refused to submit reconciliation unless the delta exactly equaled the milestone amount. The final milestone has status PAID (4), amount 0, settlement state CONFIRMED (2), and the payout parent hash stored as its proof. Final accounting: deposited 0.001 GEN, paid 0.001 GEN, refunded 0, active locked 0, pending settlement 0.
