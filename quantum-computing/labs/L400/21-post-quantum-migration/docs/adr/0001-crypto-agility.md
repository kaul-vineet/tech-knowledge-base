# 1. Inventory by AST, prioritise by Mosca, migrate key establishment first through one agile KEM interface

## Status
Accepted (2026-10-28). Guarded by `test_fitness.py`.

## Context
NIST IR 8547 (final, 2026-10-27) deprecates RSA, ECDH, ECDSA and EdDSA after 2030 and disallows them after 2035; it
names "harvest now, decrypt later" as the main reason to move key establishment first. Our toy app has 8 crypto uses.
A grep for "rsa" found 5 lines (1 docstring false positive, duplicates) and 0 P1 items; it missed X25519, ECDH P-384
and ECDSA P-256. The AST scanner found all 8 (recall and precision 1.0 against `EXPECTED_INVENTORY.json`).
With Mosca's X + Y > Z (Y = 3 migration years, Z = 9 years as a planning assumption), two items are P1:
`billing.py:7` RSA-3072 OAEP (10-year card tokens) and `sync.py:7` ECDH P-384 (7-year customer records).
For scale: Gidney & Ekerå (2019) estimated RSA-2048 at 20 million noisy qubits / 8 hours, Gidney (2025) at under a
million / under a week; lesson 19's data-only model gives 9,025,020 physical qubits and 16.1 h.

Options (measured with cryptography 50.0.2, `agility.measure`):

| Option | Change per future swap | Public key / ciphertext | Risk |
|---|---|---|---|
| A Replace X25519 with ML-KEM-768 at each call site | 4 key-establishment sites now, again next time | 1184 / 1088 B | no fallback if ML-KEM or its implementation breaks |
| B One KEM interface + registry, hybrid X25519+ML-KEM-768 | 1 config line | 1216 / 1120 B | larger messages; receivers must be upgraded first |
| C Wait until 2030 | none now | 32 / 32 B | P1 data recorded today is exposed for 10 years |

## Decision
B. All key establishment goes through `agility.establish/accept`; `CONFIG["kem"]` = `x25519+ml-kem-768` (HKDF over both
secrets, the composite form IR 8547 §3.2.1 allows). Envelopes carry the algorithm name. Signatures move to ML-DSA-65
in phase 2. Symmetric AES-256-GCM and SHA-256 stay. Upgrade receivers before senders (try 2).

## Consequences
- The inventory is a test, not a spreadsheet: new quantum-vulnerable code fails the ratchet against
  `migration_baseline.json`, which may only shrink.
- About 1.1 kB more per handshake; fine for APIs, check MTU-sensitive protocols.
- An agent may draft migration notes, but code rejects any note whose file, line, algorithm, replacement,
  priority or date disagrees with the inventory.
