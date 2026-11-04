# ADR-0022-4: External sharing wraps the document key with HPKE ML-KEM-768 + X25519; the classical KEM is read-only

## Status
Accepted (2026-10-28, capstone).

## Context
Shared documents leave our boundary and may be recorded for years ("harvest now, decrypt later"). pyca/cryptography
50.0.2 provides HPKE (RFC 9180) with `KEM.MLKEM768_X25519`. Measured in M4: a wrapped 32-byte DEK is 1,168 bytes
(a 1,120-byte encapsulation, the 32-byte DEK and a 16-byte tag), against 80 bytes with the X25519 KEM. The recipient opened the document,
and a new share with the deprecated X25519 KEM was refused.

## Decision
1. The capstone registry adds the KEMs `HPKE-XWING` (active, PQ) and `HPKE-X25519` (deprecated: open existing shares only). The policy names the sharing KEM.
2. A share = HPKE(recipient public key, DEK, info = document id) plus the unchanged envelope. Every share is audited (`doc.share`, with the KEM id).
3. Recipient public keys are verified out of band (threat T25, accepted). Adding a PQ signature to recipient keys follows ADR-0017's phases.

## Consequences
- Each share is about 1.1 KB larger, which is negligible next to documents.
- An old recipient that supports only X25519 cannot receive new shares until it upgrades. That is intentional; the refusal is visible in errors and in the audit.
- Hybrid security depends on both components being implemented correctly. Interop with liboqs-python and a TLS-level group check are pending CI (lesson 18).
