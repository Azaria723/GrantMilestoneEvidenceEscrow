# Revision and artifact verification correction

The deployment at `0xfB34BB3338097b22ED036194BB796263920C331A` is superseded. Only counters and accounting were read; both were zero at that check. No funding transaction was sent by this workflow. Deployed-source parity was not established by those reads.

## Separate immutable identities

1. Commit the actual artifacts: deliverable commit **D**.
2. Build manifests referencing **D**, the recipient, grant ID and local milestone index. Hash the actual Git blob bytes from **D**.
3. Commit the manifests in a later commit **E**. The manifests do not contain **E**.
4. Create a grant with manifest base pinned to **E**, `evidence_revision=E`, `deliverable_revision=D`, and each manifest's SHA-256.

This avoids requiring a Git commit to contain its own hash. Both identities are returned by `get_grant` and are separate inputs to `create_grant`.

## Artifact verification

Validators fetch every listed artifact, restricted to the same repository at **D**. Each downloaded body must match its manifest SHA-256 before entering the semantic assessment. Duplicate URLs and policy violations fail closed. This version supports UTF-8 text artifacts, at most 20 descriptors, 30 KB per artifact and 100 KB combined. Unavailable, oversized or undecodable content cannot authorize payment. This is not a general PDF/binary or arbitrary external-domain verifier.

## Remaining boundaries

The sponsor chooses the recipient and evidence commitments; this is not GitHub authorship authentication. Immutable evidence cannot be corrected by resubmitting different bytes: retry re-evaluates the same commitment. It is suitable for pre-agreed evidence packages, not yet a full future-work grant workflow with authenticated evidence amendments. Do not claim independent authorship verification or mutable deliverable revisions.

## Deployment gate

Do not reuse the old address or old ABI. Local tests and lint are not on-chain proof. A new deployment and source-parity check, live custody tests, transfer receipts and wallet/browser integration tests remain required before submission.
