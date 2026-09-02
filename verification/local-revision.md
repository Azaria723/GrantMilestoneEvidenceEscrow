# Local future-work revision verification — 2026-09-02

## Executed checks

- `python -m pytest tests -q --tb=short`: **29 passed**. Actual contract via GenLayer DirectMode; HTTP/LLM responses are mocks. Covers three-tranche payout state transitions, caller permissions, eight identity-binding mutations with valid hashes, append-only corrections, stale nonce, outage retry, grace boundary, approved protection, refund replay, hostile artifact URLs/content, bounded semantic results, payable mismatch, typed plan validation and sum overflow.
- `genvm-lint check contracts/GrantMilestoneEvidenceEscrow.py`: lint and validation passed, 13 methods (6 view / 7 write), pinned runner retained.
- `node --test src/forms.test.js` from frontend: **5 passed**. Exact GEN conversion, malformed amounts, creation schema without future evidence, increasing deadlines, nonce-bound manifest URL.
- `npm run build` from frontend: passed. Rollup dependency annotation and >500 KB bundle warnings remain; these are not security or consensus proof.
- Local browser: loaded revised form, entered title/repository/criteria, added milestone (second offset 172800), removed it, reloaded cleanly. Without a new configured contract the transaction button is disabled. This does not test signed wallet transactions or live submission history.

These results apply to local revised code, not the obsolete deployed contract. No live lifecycle or real transfer receipt is claimed here. Required post-deploy checks are documented separately in README.
