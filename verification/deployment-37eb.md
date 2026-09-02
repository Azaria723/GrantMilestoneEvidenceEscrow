# Deployment verification — 2026-09-02

Contract: `0x37Eb0776f03fa1C18ac9F0F327335dfE9388b420`

Network: Studionet, chain ID 61999.

Read via `scripts/inspect_deployment.mjs`, using SDK `getContractCode`, `getContractSchema`, `get_counts` and `get_accounting`.

- Deployed source exactly equals local source (not just matching a contract name).
- SHA-256 for both: `78dcfad53d5ae66d2d5e6cb90a52141350ef0fa1f5c86a8b416b7d5917b5096c`.
- ABI has 6 view and 7 write methods. `create_grant` is payable with 4 arguments; `submit_milestone` has 5 arguments including expected nonce and E/D/digest; `assess_milestone` has milestone ID and expected nonce.
- Counts observed: 0 grants, 0 milestones.
- Accounting observed: deposited, paid, refunded and active locked all 0.

These are read-only deployment checks, not lifecycle or transfer proof. No GEN has been sent by this verification workflow. A public evidence repository is needed to publish contract-bound manifests before a positive lifecycle can be completed.

Frontend `.env` now points to this address. A Netlify environment override or `.env.local` can override it and must be checked before any production deployment.
