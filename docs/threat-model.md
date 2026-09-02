# Threat model and limits

## Controls

- Immutable sponsor repository policy; recipient cannot direct verification outside it.
- Fixed recipient caller for claim/submission; sponsor-only expired refund; payout goes only to recipient.
- Contract/chain/grant/milestone/recipient/nonce/revision bindings prevent evidence replay.
- Actual artifact bytes are fetched and hashed; manifest claims alone cannot approve.
- Same-nonce retry appends assessment history. Corrections use increasing nonces, maximum eight submissions.
- Approved funds cannot be expired or reclaimed. Outage does not approve or enable premature refund.
- Sequential claims and terminal paid/refunded states prevent skipped tranches and replay.
- Invalid payable plans revert before writes; sum uses checked range before custody bookkeeping.

## Limits

The sponsor must choose a suitable repository and criteria. This is a repository-constrained delivery agreement, not GitHub author authentication or an independent authoritative registry. A collaborator may publish artifacts; content evaluation does not prove wallet-to-author identity. Public immutable URLs can still become unavailable. Semantic judgment remains probabilistic and may disagree; no payout is allowed on uncertainty. Only bounded UTF-8 artifacts are supported, not binaries or full repository analysis. A failed earlier milestone blocks later claims until their individual refund deadlines. Assessment retries are not count-limited within the time window and incur transaction/storage costs.
