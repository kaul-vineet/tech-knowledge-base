# ADR-0018: Hybrid X25519MLKEM768 for key exchange, strict with no classical fallback; ML-DSA via dual signing

## Status
Accepted (2026-10-28, lesson 18 lab). Revisit when the pure ML-KEM groups are recommended for TLS, or when the policy reaches `pq-only` (ADR-0017).

## Context
The service stores and transmits data that must stay confidential for at least 10 years (`pq_policy.json`). An attacker
can record traffic today and decrypt it once a cryptographically relevant quantum computer exists ("harvest now, decrypt
later"). FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA) are final. RFC 10024 (August 2026) registers X25519MLKEM768 (0x11EC,
Recommended: Y). pyca/cryptography 50.0.2 provides ML-KEM, ML-DSA and HPKE `MLKEM768_X25519`. Measured in `pq_measure.py` on the lab machine:

| Option | On-wire key-share bytes | Handshake (median) | Safe if a CRQC exists | Safe if the lattice scheme breaks |
|---|---|---|---|---|
| X25519 only | 64 | ≈141 µs | no | yes |
| ML-KEM-768 only | 2,272 | ≈180 µs | yes | no |
| X25519MLKEM768 | 2,336 | ≈391 µs | yes | yes |

Authentication costs more than key exchange. A root + leaf certificate chain plus the CertificateVerify signature is
478 B with Ed25519 and 14,106 B with ML-DSA-65 (try_it 2). With a forged-today signature there is nothing to harvest, so
the signature migration is less urgent than the key-exchange migration.

## Decision
1. Use X25519MLKEM768 for key exchange, with the RFC 10024 layout: ML-KEM part first, a 64-byte combined secret, and the key derived over the transcript.
2. Make the client strict. A server share that is not exactly 1,120 bytes aborts the handshake (illegal_parameter) and emits a `handshake_abort` event. Classical-only key exchange is never a fallback; it would have to be a separately configured group, and the fitness test forbids it for this data.
3. For stored data shared with a recipient, use HPKE `MLKEM768_X25519`: a 1,120-byte encapsulation per recipient, 1,168 bytes for a wrapped 32-byte key.
4. Signatures: dual-sign with Ed25519 and ML-DSA-65 under ADR-0017's `transition` phase; do not yet put ML-DSA in certificates.
5. Fitness function: `test_fitness_pq_policy.py` requires a PQ-safe group, no fallback, and at most 2,400 bytes of key shares.

## Consequences
- Every handshake carries about 2.3 KB more. This can push a ClientHello over one network packet, and middleboxes that mishandle large hellos will show up as handshake failures; watch `handshake_abort` and connection-error rates during rollout.
- Handshake CPU about triples in this Python lab (≈141 → ≈391 µs). Native TLS stacks are faster; measure there.
- Both a quantum break of X25519 and a classical break of ML-KEM are survivable, at the cost of implementing both.
- Strictness can cause outages with old peers. Upgrade the peers or give them an explicit, monitored exception; do not loosen the parser.
- liboqs-python and oqs-provider are for prototyping and interop checks only. oqs-provider disables its own ML-KEM/ML-DSA and the three RFC 10024 hybrids on OpenSSL 3.5 and later, which implements them natively.
