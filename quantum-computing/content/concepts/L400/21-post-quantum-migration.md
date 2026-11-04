# Concept: Quantum and post-quantum — what changes for software

## Why it matters
Shor's algorithm breaks RSA, finite-field Diffie-Hellman and elliptic-curve cryptography once a large enough
fault-tolerant machine exists. That machine does not exist yet, but data encrypted today can be recorded and decrypted
later: "harvest now, decrypt later". NIST IR 8547 (final, 27 October 2026) therefore deprecates quantum-vulnerable
public-key algorithms after 2030 and disallows them after 2035. It also prioritises key establishment for
long-lived data, because signatures are not exposed to harvesting. For a software team, the work is inventory,
prioritisation and crypto agility. It is not quantum physics.

## Mental model
Mosca's inequality, as quoted in IR 8547: if X years of required secrecy plus Y years of migration exceed Z years
until a cryptanalytically relevant quantum computer, the data is already at risk.

```
today ───── Y: migrate ─────┤
today ───── X: data must stay secret ───────────┤
today ───── Z: CRQC (unknown) ───────┤          ← if X + Y > Z, recorded traffic is exposed
```

Resource estimates put Z in context. Gidney & Ekerå (2019) estimated 20 million noisy qubits and 8 hours for
RSA-2048. Gidney (2025) estimated under a million qubits and under a week, at the same 0.1 % gate error. Lesson 19's
data-only model gives 9,025,020 physical qubits and 16.1 h. Roetteler et al. bound P-256 at 2330 logical qubits,
fewer than RSA-2048's 6190, so ECC is the easier target.

## Design space
- **Inventory method.** Grepping for algorithm names finds words, not uses. An AST scanner resolves imports and
  aliases and classifies each call by purpose (key establishment, signature, symmetric). Config files need their own
  rules.
- **Migration shape.** (A) Replace algorithms at each call site. (B) Route all key establishment through one
  interface whose algorithm is configuration, with a hybrid X25519 + ML-KEM-768 combined by HKDF (the composite form
  IR 8547 allows). (C) Wait for the deadlines.
- **Order.** Key establishment protecting long-lived data first (P1). Then signatures and the remaining key exchange
  before 2030 (P2). Keep AES-256 and SHA-256, which IR 8547 does not expect to transition.

## How to decide
Measure the inventory against ground truth. Compute priorities in code from data lifetimes. Compare options on change
cost, size and risk.

Worked example (toy app, Y = 3, Z = 9 as planning assumptions): grep found 5 lines, including 1 docstring false
positive, and 0 P1 items. The AST scanner found all 8 uses (recall and precision 1.0). P1 = `billing.py:7` RSA-3072
OAEP (10-year card tokens) and `sync.py:7` ECDH P-384 (7-year records). Sizes measured with cryptography 50.0.2:

- X25519: public key and ciphertext 32 / 32 bytes.
- ML-KEM-768: 1184 / 1088 bytes.
- Hybrid: 1216 / 1120 bytes.

Option B makes the next swap a one-line config change, and ADR 0001 adopts it. When legal extends API-traffic secrecy
to 8 years, `api_client.py:11` becomes P1 automatically (try it 1).

## Failure modes at scale
- **Invisible crypto.** Vendored libraries, configs and other languages escape a Python scanner. Measure recall
  against a hand-checked sample. A ratchet test that fails on any new vulnerable use outside the baseline stops the
  inventory from rotting.
- **Flag-day upgrades.** A sender that switches first breaks old receivers. Try it 2 shows the envelope being rejected
  with "unknown kem". Upgrade receivers first and keep algorithm names in envelopes.
- **Size limits.** About 1.1 kB more per handshake can break UDP, MTU-bound or constrained-device protocols.

## Common mistakes
- Migrating signatures first because they are visible, while recorded key exchanges stay harvestable.
- Treating "quantum-safe" as one algorithm swap instead of an agility capability.
- Letting an assistant's migration notes go unchecked. In the lab, code rejected an invented file, a signature mapped
  to ML-KEM and a made-up 2029 deadline.
