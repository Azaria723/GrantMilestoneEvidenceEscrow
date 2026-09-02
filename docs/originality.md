# Originality and anti-clone review

Nearest internal comparison: `OpenSourceMicroBounty`.

| Dimension | OpenSourceMicroBounty | GrantGate | Material difference |
|---|---|---|---|
| Object | Independent bounty | Grant containing ordered tranches | Hierarchical persistent object |
| Acquisition | Contract derives GitHub PR APIs | Sponsor fixes repository; recipient submits pinned artifacts after work | Post-delivery, nonce-bound evidence |
| Proof | Merge, commit, issue and PR scope | Manifest bytes, subject/version bindings, deliverable set and criteria | Different proof obligation |
| Identity | Claiming wallet + PR evidence | One fixed recipient embedded in every committed manifest | Grant-level recipient continuity |
| Lifecycle | One task, one payout | Sequential milestone dependency and partial grant balance | Multi-stage economic evolution |
| Recovery | Whole bounty refund | Independent tranche expiry/refund | Partial recovery topology |
| Consequence | Single reward | Multiple bounded payouts from one deposit | Conservation across tranches |

Its distinguishing mechanism is an immutable repository policy coupled to an ordered financial schedule and append-only delivery submissions. Completing one milestone unlocks the next while changing one tranche of a shared grant balance. Verification evaluates actual pinned artifact text rather than PR merge facts, and recovery operates per tranche.
