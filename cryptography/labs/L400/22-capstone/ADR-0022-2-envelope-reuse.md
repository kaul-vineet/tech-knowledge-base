# ADR-0022-2: Documents use lesson 17's versioned envelope, with DEKs wrapped by the KMS and signed through token handles

## Status
Accepted (2026-10-28, capstone).

## Context
The service must survive algorithm changes (ADR-0017), KEK rotation (lesson 12) and key theft from the app host
(ADR-0019) without a flag day. Reusing earlier labs keeps one implementation of each rule: `agile_envelope.seal/open_`, `solution_agile.verify`,
the lesson 12 keyring, and the lesson 19 hardened token. Measured in M1: 6 documents, a rewrap crash after 3 records
(`{"docs-kek:v1": 3, "docs-kek:v2": 3}`), retire refused while records were in use, the job resumed (3 moved), v1 retired,
and 6/6 documents readable.

## Decision
1. Each document gets a fresh DEK for the policy's default AEAD, held in a one-entry keyring that never leaves memory. The record stores only `{env, kek, wdek}`.
2. The envelope header (version, AEAD id, kid, nonce, context) is the AEAD's AAD. A relabelled header fails (M1 test).
3. Document signatures are made through the token's `doc-signing` handle via a `TokenSigner` adapter: the registry calls `.sign()`, the token signs, and the key is never exposed. The policy phase is `classic` because the soft token signs Ed25519 only. Moving to `transition` (Ed25519 + ML-DSA-65) needs ML-DSA in the token; SoftHSM2 added ML-DSA support, but that is unverified here and pending CI.
4. Fitness: `agility_lint` scans the capstone folder (0 violations); only the capstone `registry.py` names algorithms.

## Consequences
- An AEAD swap, KEK rotation and a later signature-phase change are all configuration plus background jobs.
- Reading a document needs the KMS and the token to be up: availability now depends on three components.
- The capstone registry wraps lesson 17's registry by path import, so a change in lesson 17 changes the capstone. That coupling is intended, and its tests run in CI.
