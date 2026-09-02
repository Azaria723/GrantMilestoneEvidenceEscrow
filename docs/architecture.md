# Architecture and proof obligation

## Proof obligation

For milestone `M` of grant `G`, prove that bytes fetched from the sponsor-committed immutable location match the precommitted digest, identify `G/M`, the fixed recipient and revision exactly, contain bounded deliverable descriptors, and substantively satisfy the acceptance criteria.

The validator produces only consequential semantic facts. It does not authorize a transfer. The contract maps an `APPROVED` finding through lifecycle, sequencing, recipient, amount, remaining-custody and replay checks before transfer.

## Consensus binding matrix

| Field | Origin | Verification | Consequence |
|---|---|---|---|
| Manifest bytes | Contract-derived immutable raw GitHub URL | HTTP and size bounds | Acquisition gate |
| Manifest digest | Sponsor commitment at grant creation | SHA-256 exact equality | Approval gate |
| Grant/milestone | Manifest | Exact integers | Subject gate |
| Recipient | Manifest + stored grant | Exact address equality | Identity gate |
| Revision | Manifest + immutable URL policy | Exact 40-hex equality | Version gate |
| Deliverables | Manifest | Bounded list and 64-hex digests | Completeness gate |
| Criteria | Validator judgment | `PASS/FAIL/UNRESOLVED` | Semantic gate |
| Verdict/code/reason | Derived closed mapping | Strict consensus JSON | State transition |

## Recovery

`UNAVAILABLE` is non-terminal and can be assessed again. Any non-paid milestone may be permissionlessly marked expired only after its deadline. Only the stored sponsor can recover an expired tranche. A late verdict cannot reopen a terminal paid or refunded state.
