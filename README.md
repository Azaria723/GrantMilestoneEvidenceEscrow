# GrantMilestoneEvidenceEscrow (GrantGate)

A future-work grant dApp: sponsors deposit the exact sum of up to six sequential GEN tranches, fix a recipient and GitHub repository, and set immutable criteria and increasing deadlines. Recipients submit delivery evidence only after doing the work.

## Why GenLayer

Validators retrieve pinned public artifacts, verify their byte commitments and subject bindings, and judge whether their actual text meets the sponsor's written criteria. Deterministic contract code controls custody, permissions, deadlines and one-shot settlement. This does not prove authorship, external truth, code security or scientific impact.

## Workflow

1. Sponsor calls `create_grant(title, recipient, repository, milestone_plan_json)`, attaching the exact tranche sum. Each plan item has only `amount_wei` (decimal string), `deadline_seconds` (integer offset from creation), and `criteria`.
2. Recipient calls `claim_milestone(mid)`. The preceding tranche must already be PAID.
3. Complete and commit artifacts at D. Build an identity-bound manifest and commit it later at E. E is not embedded in itself.
4. Recipient calls `submit_milestone(mid, expected_nonce, E, D, manifest_sha256)`. Evidence URL is derived from the stored repository, E, grant ID, local milestone index and nonce.
5. Anyone calls `assess_milestone(mid, expected_nonce)`. Manifest and artifact hashes/bindings must pass before semantic assessment. UNAVAILABLE permits retry. Rejected/unavailable deliveries can be replaced by a new nonce before the delivery deadline, up to eight submissions.
6. Sponsor or recipient pays an APPROVED tranche. Otherwise, anyone can mark it expired after the applicable deadline and only the sponsor can refund it to the stored sponsor address.

SUBMITTED/UNAVAILABLE receive a 24-hour assessment grace after delivery deadline. APPROVED never expires. No new submission after delivery deadline. An expired earlier tranche blocks later claims; those tranches remain refundable after their own expiry.

## Verification

Run from the repository root:

```powershell
$env:PYTHONIOENCODING='utf-8'
genvm-lint check contracts/GrantMilestoneEvidenceEscrow.py
python -m pytest tests -q
cd frontend
node --test src/forms.test.js
npm run build
```

Direct tests execute the actual contract with mocked HTTP/LLM and transfer intents. They are not real validator consensus or live transfer receipts. See [local verification](verification/local-revision.md).

## Deployment verification

The historical deployments `0xfB34BB3338097b22ED036194BB796263920C331A` and `0x37Eb0776f03fa1C18ac9F0F327335dfE9388b420` must not be used. Their outgoing payout path could finalize the parent call while the linked transfer failed. The current source uses an EOA `SEND`, keeps settlement pending, and changes milestone/accounting state only after validator-retrieved Studionet receipts prove the linked recipient credit. Deploy this revision as a fresh instance, verify byte-for-byte source parity, then run the recipient-balance proof before configuring the frontend.

This is testnet evidence, not an audit or production-readiness claim. Production hosting remains a separate step.

Public frontend: https://grantmilestoneevidenceescrow.netlify.app/. It was checked without authentication and read back the final PAID lifecycle state; see [production verification](verification/netlify-production.md).

See [architecture](docs/architecture.md), [threat model](docs/threat-model.md), and [revision correction](docs/revision-fix.md).
