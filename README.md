# GrantMilestoneEvidenceEscrow (GrantGate)

GrantGate is a GenLayer dApp for multi-tranche grants. A sponsor locks the exact sum of every milestone in native GEN and commits an immutable evidence policy before work begins. Each tranche is released only after validators retrieve the sponsor-fixed manifest, verify its content commitment and subject bindings, and agree that concrete deliverables satisfy bounded acceptance criteria.

## Why GenLayer

A conventional contract can enforce amounts and deadlines but cannot independently retrieve public deliverable manifests or judge whether reports, releases and artifacts substantively meet written criteria. GenLayer provides the semantic consensus layer; deterministic contract logic retains execution authority over sequencing, custody, payout, expiry and replay prevention.

## Scope and non-claims

GrantGate proves only that a sponsor-committed manifest is retrievable, byte-for-byte committed, bound to the exact grant/milestone/recipient/revision, structurally contains deliverables, and is judged consistent with the stated criteria. It does not prove scientific truth, code security, legal compliance, real-world impact or ownership of arbitrary linked artifacts.

## Mechanism

```text
Sponsor creates grant and deposits exact tranche sum
  → immutable manifest base + revision + per-milestone digest committed
  → fixed recipient claims milestones sequentially
  → recipient triggers assessment (cannot redirect evidence)
  → validators fetch and hash the sponsor-fixed manifest
  → deterministic subject bindings must pass
  → bounded semantic criteria assessment reaches strict consensus
  → APPROVED tranche pays exactly once
  → outage remains retryable; expiry returns only that tranche to sponsor
```

Statuses: `PLANNED(0)`, `CLAIMED(1)`, `SUBMITTED(2)`, `APPROVED(3)`, `PAID(4)`, `REJECTED(5)`, `REFUNDED(6)`, `UNAVAILABLE(7)`, `EXPIRED(9)`.

## Security invariants

- `total_paid + total_refunded + active_locked = total_deposited`.
- Deposit must equal the sum of all tranche amounts; invalid payable creation reverts atomically.
- Recipient identity, manifest origin and immutable revision are fixed at grant creation.
- A recipient never supplies the evidence URL used by validators.
- Manifest SHA-256 and exact grant/milestone/recipient/revision bindings are on the approval critical path.
- Later milestones cannot be claimed before the previous milestone is paid.
- `UNAVAILABLE` keeps custody frozen and permits retry.
- Only an expired tranche can be refunded, and only to its stored sponsor.
- `PAID` and `REFUNDED` are terminal; transfers cannot replay.

## Local verification

```powershell
$env:PYTHONIOENCODING='utf-8'
genvm-lint check contracts/GrantMilestoneEvidenceEscrow.py
python -m pytest tests -q -p no:cacheprovider

cd frontend
npm install
npm run build
```

Latest revision separates the evidence-source commit from the deliverable commit and fetches/hashes actual UTF-8 artifact bytes before semantic judgment. See [revision correction and limitations](docs/revision-fix.md).

Expected contract result: GenVM lint and validation pass; `11 passed` direct security tests.

## Deployment status

The contract is locally verified but not yet deployed. After deployment, the required order is source-parity verification, live positive/negative custody lifecycles, transaction/state ledger, frontend address update, production deployment and production readback.

See [architecture](docs/architecture.md), [threat model](docs/threat-model.md), [originality analysis](docs/originality.md), and the empty [Studionet ledger](verification/studionet-e2e.md).
