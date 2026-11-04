# ADR-01-4: A versioned envelope contract, switched on by a replicated gate entry

## Status
Accepted (L600 project 01, 2026-10-30). Guarded by M5 and the seam test "envelope contract versioning across replicas".

## Context
The envelope format will change: a cipher swap (v3 = ChaCha20-Poly1305 via lesson 17's registry), a PQ signature
later. Writers (the sealer), readers (member devices) and the replicated state machine all read the header. The state
machine must apply identically on every replica. If one replica accepts v3 because its local config was upgraded
first, replicas diverge: different messages exist depending on which replica you read.

## Decision
- Envelope header `{v, aead, kem, epoch, sender, ikey, n}`. The whole header is AAD. Unknown versions raise
  `EnvelopeError`, with no fallback. v1 history (no algorithm id, implied A256GCM) stays readable.
- A consumer-driven reader contract (`READER_CONTRACT`, built with application-architecture L300 #14's `like()`
  matchers) is checked against the writer's header. Renaming or retyping a field fails the check.
- Which versions the log accepts is replicated state, changed only by a `{"type": "contract", "accept": [...]}` log
  entry. The API refuses to write a version the log does not accept yet (409). Rollout order: ship readers, then
  commit the gate entry, then switch writers (expand/contract).

## Consequences
- M5: v2 header has 0 contract problems; renamed `n` gives `missing n`; v3 before the gate gets 409, after it 201
  (aead C20P1305); every replica shows 4 readable messages. Under `local-contract-config` the replicas show {3, 5, 3}.
- Rolling back a gate is also a log entry. Envelopes already written in v3 stay readable only by v3-capable readers.
- Replicas hold no keys and never decrypt. They depend only on the header fields in the contract.
