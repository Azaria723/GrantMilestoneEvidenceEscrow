# Proof obligation and lifecycle

Sponsor authority covers the fixed repository, recipient, tranche amounts, criteria and deadlines. Recipient authority covers post-delivery submission of pinned evidence within that repository, not arbitrary external evidence hosts.

Approval requires: fetched manifest SHA-256; exact chain ID, contract address, grant ID, global milestone ID, local index, recipient, nonce and D bindings; every artifact fetched from the same repository at D and hash checked; bounded semantic PASS against immutable criteria.

Manifests live at `evidence/grant-G/milestone-I/submission-N.json` within evidence commit E. E is stored on-chain, not embedded into its own manifest. Artifacts are limited to 20 UTF-8 files, 30 KB each, 100 KB combined; manifest limit 50 KB. Paths reject traversal, queries and external repositories.

## State transitions

PLANNED → CLAIMED → SUBMITTED → APPROVED → PAID.
Assessment can instead produce REJECTED or UNAVAILABLE. REJECTED/UNAVAILABLE allow new nonce submission until delivery deadline. UNAVAILABLE also allows same-nonce reassessment until review cutoff. Each assessment has an append-only 1-based ID. Previous submission records and assessment results remain readable.

Delivery deadlines are creation time plus strictly increasing offsets. Assessment of SUBMITTED/UNAVAILABLE is allowed through deadline + 86400 seconds; expiry only after that cutoff. Other nonterminal states expire after delivery deadline. APPROVED cannot expire or refund. Refund requires EXPIRED and stored sponsor caller, and always transfers to stored sponsor.

Accounting invariant: deposited = paid + refunded + active_locked. Tranche amount is cleared and terminal state committed before emitting transfer. On-chain settlement and transfer-finality still require network tests.
