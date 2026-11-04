# ADR-01-3: Epoch keys travel in the log as hybrid X25519MLKEM768 welcomes; stale epochs are rejected at apply

## Status
Accepted (L600 project 01, 2026-10-30). Guarded by M1, M4 and the seam test "key rotation vs log replay".

## Context
Membership changes rotate the group key (cryptography L400 #20: a removed member must lose access to new messages).
The log is replayed from index 1 by restarted replicas, by new devices and by the sealer on every new leader.
If epoch keys lived outside the log (a KMS or a side channel), replay would depend on a second system being
available and in sync. If the newest key were used for everything, old ciphertexts would fail to open (InvalidTag)
after rotation. Recorded traffic must also survive a future quantum attacker (harvest now, decrypt later).

## Decision
- Rotation is a log entry: `{"type": "epoch", "epoch": n, "members": [...], "welcomes": {...}}`. Each welcome is
  a hybrid encapsulation to the member's key package (lesson 18's `server_respond`; 1,120 B KEM part) plus the
  AES-GCM-wrapped epoch secret (12 B nonce + 48 B). That is 1,180 B per member. The member side uses lesson 18's
  strict `client_finish`.
- Every envelope names its `epoch` (in the AAD). Readers keep a key per epoch they were welcomed to.
- The state machine rejects an envelope whose epoch is not the current one at its log position (`stale_epoch`).
  A message sealed before a removal but committed after it is refused, not shown to the removed member.

## Consequences
- M4: a fresh device replays 20/20 messages (alice, bob). Carol, removed in epoch 2, reads 10/20 and 0 after her
  removal. The one late epoch-1 envelope is rejected. Under the fault `accept-stale-epoch`, carol reads it.
- A rejected late message must be resent by its client (409). The outbox cannot re-seal without plaintext, by design.
- Welcomes are O(members) per rotation: 4,720 B raw for 3 members + sealer, 119,180 B for 100 (tryIt 2). Large
  groups need a ratchet tree (MLS, RFC 9420; lesson 20).
- RFC 10024 warns that its hybrid analysis relies on the TLS transcript. This welcome binds both shares into the KDF
  like lesson 18 does, but it is a teaching construction. Production would use HPKE with a PQ/T KEM or MLS.
