# Future-work redesign

The old deployment `0xfB34BB3338097b22ED036194BB796263920C331A` is superseded. Previous read-only checks found zero counts and accounting; they did not establish deployed source parity. No funding was sent by this workflow.

Earlier code fixed evidence before work existed. This revision instead fixes terms and repository at creation and lets the stored recipient submit immutable evidence afterward. D identifies artifacts; a later E contains the manifest. Each manifest binds the deployed contract and chain plus grant, milestone, recipient and submission nonce. New evidence never overwrites prior records.

A 24-hour review grace protects pending/unavailable submissions from immediate expiry at delivery deadline. Approved tranches cannot be expired or refunded. The frontend uses separate creation/submission forms and displays read-back state without treating transaction finality as proof of business success.

This is an ABI/storage-breaking redesign: deploy a new instance, not an upgrade over populated old storage. Live custody and wallet tests remain a separate deployment gate.
