# GrantGate protocol architecture delivery

This document is a synthetic documentation deliverable for grant 0, milestone 0.
It describes the implemented architecture; it is not an independent audit,
authorship proof, or claim of production readiness.

## Accounting conservation

The contract maintains the equation:

total_deposited = total_paid + total_refunded + active_locked

The sponsor deposits the exact sum of milestone amounts at grant creation.
Paying one approved milestone decreases its outstanding amount and the grant's
remaining custody, and increases total_paid by the same amount. Refunding an
expired milestone similarly increases total_refunded. These transitions preserve
the equation and do not release other tranches. The milestone enters its terminal
state and its amount is cleared before a transfer is emitted.

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
