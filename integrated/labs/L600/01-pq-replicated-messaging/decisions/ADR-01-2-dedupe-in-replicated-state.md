# ADR-01-2: Idempotency lives in the replicated state machine; the outbox stores ciphertext only

## Status
Accepted (L600 project 01, 2026-10-30). Guarded by M3 and the seam test "idempotent retries vs duplicate ciphertexts".

## Context
Clients retry a POST on any unknown outcome (503) with the same Idempotency-Key (distributed-systems L100 #5, IETF
draft-ietf-httpapi-idempotency-key-header). The API seals, writes the sealed envelope to the node's transactional
outbox (application-architecture L200 #9), and a relay proposes it to Raft until it commits (at least once).
Two things break naive dedupe:
1. Leader failover. A dedupe table in the leader's memory dies with the leader. The retry reaches a new leader that
   has never seen the key.
2. Re-sealing. Every retry that is sealed again gets a fresh random nonce, so the "same" message becomes a different
   ciphertext. Byte equality cannot detect the duplicate. A stuck outbox row relayed after restart adds another copy.

## Decision
The Idempotency-Key and a keyed fingerprint `HMAC(kdf(epoch_secret, "fp"), sender || text)` travel in every log
entry. The deterministic state machine (`replicated_state.State.apply`) keeps `seen[ikey] = (epoch, fp, index)`:
- first entry for a key: accepted;
- same key and fingerprint: `duplicate`, a no-op;
- same key, same epoch, different fingerprint: `conflict`, so the API returns 422.
The API checks `seen` before sealing and replays the stored result (200). The outbox holds sealed envelopes only:
no plaintext on any node's disk. This is the session-table pattern of the Raft paper, section 8.

## Consequences
- M3: crash after the outbox write gives 503. The client retry gives 201. The log holds 2 ciphertexts for the key and
  readers see 1 message. Under the seeded fault `no-apply-dedupe`, 32 duplicates are shown out of 300 messages.
- The fingerprint is keyed, so the log does not reveal equal plaintexts to someone without the epoch key. It does
  reveal equality to members, which is acceptable.
- `seen` grows forever in this lab. Production needs an expiry policy (the draft lets a resource expire keys) and
  snapshots (Raft section 7, not implemented here).
