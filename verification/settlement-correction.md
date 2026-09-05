# Settlement correction awaiting fresh deployment

The reviewed `0x37Eb…b420` deployment is retired. Its parent `pay_milestone` transaction could mark a milestone paid even when the linked contract-to-recipient operation ended in GenVM ERROR.

The current source:

- emits a native EOA `SEND` through `@gl.evm.contract_interface`;
- records `SETTLEMENT_PENDING` without clearing the milestone amount or increasing `total_paid`;
- derives parent and child receipts from a fixed Studionet RPC under validator consensus;
- requires exact chain, calldata, parties, linkage, type, amount, finality and `value_credited=true`;
- makes explicit failed transfers retryable without spending another milestone's reserves;
- finalizes `PAID` only after successful reconciliation;
- automatically refreshes frontend state after finalized writes and after reconciliation.

Local verification: contract lint passes, frontend production build passes, and 43 Python tests pass, including adversarial receipt mutations, failed-credit retry, reserve shortfall, duplicate prevention and emission rollback.

Required next evidence: deploy a fresh instance, prove deployed/local source parity, execute an approved milestone payout, record the linked child `SEND`, prove the recipient EOA balance increased by the exact milestone amount, reconcile, and confirm the milestone is `PAID` with cleared accounting only afterward.
