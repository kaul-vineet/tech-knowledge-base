# ADR-003: Audit = SHA-256 hash chain of headers + separately stored bodies + Ed25519-signed checkpoints

## Status
Accepted (2026-10-30). Fitness: F2 (`tests/test_m4_audit_chain.py`); seam `tests/test_seam_audit_privacy.py`.

## Context
Every tool call must be provable later, and nobody - including the host operator - may edit, delete or reorder
entries unnoticed. The log must also never hold secrets, and privacy rules require deleting content after a
retention period. Measured: verifying each entry alone (the 'per-entry-hash' fault) detects 20 of 31 seeded edits
- it misses deletions, swaps, truncation and a rewritten chain. A Merkle tree (Crosby & Wallach 2009; RFC 9162)
gives logarithmic proofs but is more code than one host with thousands of entries per day needs.

## Decision
Each header carries seq, ts, event, actor, prev hash and body_sha256; hash = SHA-256(prev || canonical(header)).
Bodies (redacted: x-sensitive fields as hash + length, secret patterns scrubbed, tokens as id + fingerprint) are
stored apart, so retention can erase a body while the chain still verifies. After each session the host signs a
checkpoint (seq, head) with an Ed25519 key that lives outside the log store.

## Consequences
- 31 of 31 seeded edits detected, including a fully recomputed chain (its head no longer matches the checkpoint).
- Edits after the last checkpoint are only detected at the next checkpoint: checkpoint per session, ship
  checkpoints to a second store (pendingCi: external witness).
- Verification is linear in log length; past ~10^6 entries per audit move to a Merkle tree.
