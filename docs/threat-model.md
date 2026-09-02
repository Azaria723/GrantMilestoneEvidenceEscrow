# Threat model

## Attacker goals

- Redirect validators to self-authored evidence.
- Reuse a valid manifest for another grant, milestone, recipient or revision.
- Obtain a later tranche without completing earlier work.
- Convert source outage into payout or early refund.
- Pay or refund a tranche twice.
- Attach GEN to an invalid plan and leave accounting inconsistent.

## Controls

- Source and revision fixed by sponsor; validator URL is contract-derived.
- SHA-256 byte commitment plus exact subject/version binding.
- Fixed recipient address and strict sequential claim gate.
- Closed verdict surface with `UNAVAILABLE` distinct from `REJECTED`.
- Checks-effects-interactions and terminal states before transfers.
- Payable validation raises `UserError` before record mutation.
- Permissionless expiry but sponsor-only fixed refund recipient.

## Epistemic boundary

The manifest and semantic verdict are evidence about delivered artifacts, not proof of their external truth, quality beyond stated criteria, authorship, legality or future availability.
