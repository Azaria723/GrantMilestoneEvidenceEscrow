# GrantGate protocol architecture delivery

This document is a synthetic documentation deliverable for grant 0, milestone 0.
It describes the implemented architecture; it is not an independent audit,
authorship proof, or claim of production readiness.

## Accounting conservation

The contract maintains the equation:

total_deposited = total_paid + total_refunded + active_locked

The sponsor deposits the exact sum of milestone amounts at grant creation.
Settlement is deliberately two-phase. `pay_milestone(mid, attempt)` emits one
native EOA `SEND` through `@gl.evm.contract_interface`, then records
`settlement_state = PENDING`; it does not mark the milestone PAID, clear its
amount, reduce grant custody, or increase `total_paid`. The same rule protects
expired refunds.

`reconcile_settlement` independently retrieves the parent and linked child
receipts from the contract's fixed Studionet RPC under validator consensus. It
requires chain 61999, exact parent calldata and authorized caller, exactly one
linked child, child type `SEND` (0), the contract as sender, the stored EOA as
recipient, the exact milestone amount, FINALIZED status, and
`value_credited = true` without an ERROR receipt. Only after all checks pass is
the milestone marked PAID, its amount cleared, grant remaining reduced, and
`total_paid` increased. This preserves the accounting equation without treating
parent finality as proof that the recipient received funds.

An explicit failed and uncredited child changes only the settlement attempt to a
retryable failure. The milestone remains APPROVED with its amount intact. A new
attempt is monotonic and allowed only when contract balance still covers all
other locked liabilities, so a failed outgoing transfer cannot be replaced with
another grant's reserved GEN. Missing, malformed, unlinked, pending, or
contradictory receipts remain unresolved and cannot unlock payment or retry.

The frontend waits for parent finality, polls the linked child result, submits
reconciliation, waits for reconciliation finality, and automatically refreshes
all grants, milestones, settlement state, and accounting. It also refreshes
authoritative state after every other write, so users do not need a manual page
reload to observe finalized results.

## Sequential milestone claim dependency

Only the fixed recipient wallet can claim a milestone. For local milestone index
greater than zero, the immediately preceding milestone must already have status
PAID (4). Merely APPROVED (3) is insufficient. Otherwise claim_milestone returns
PREVIOUS_MILESTONE_NOT_PAID without changing state. Thus milestone 1 cannot be
claimed until milestone 0 has been paid; the same dependency applies to every
subsequent milestone in that grant. The first milestone has no predecessor.

## 24-hour review grace

Each delivery deadline is the creation timestamp plus deadline_seconds. New
submissions must be made by that delivery deadline. An already SUBMITTED or
UNAVAILABLE submission can be assessed through deadline_at + 86400 seconds,
which is a 24-hour review grace. Such a milestone cannot be expired until after
that extended cutoff. The grace does not permit a late new submission.

An APPROVED tranche does not expire and cannot be refunded, including after the
review window. It remains payable exactly once to the stored recipient. Other
nonterminal states expire only after their applicable deadlines. Refund requires
the EXPIRED state and the sponsor caller, and returns funds only to the sponsor.
