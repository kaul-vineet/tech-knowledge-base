## Why it matters
A cryptographically relevant quantum computer would break X25519, ECDSA, Ed25519 and RSA (Shor's algorithm); symmetric ciphers and hashes are hit much less. Nobody knows when such a machine will exist, but an attacker can **record traffic today and decrypt it later**. Anything that must stay secret for 10 years therefore needs post-quantum key exchange *now*. NIST finalised ML-KEM (FIPS 203) and ML-DSA (FIPS 204) in August 2024. RFC 10024 (August 2026) registers the TLS group `X25519MLKEM768` (0x11EC) as Recommended, and pyca/cryptography 50.0.2 ships ML-KEM, ML-DSA and HPKE `MLKEM768_X25519`. The question is no longer whether, but how.

## Mental model
A **hybrid lock with two keys**. The client sends two public halves, an ML-KEM encapsulation key and an X25519 share. The server returns an ML-KEM ciphertext and its own X25519 share. Both sides concatenate the two shared secrets and derive one key, so an attacker must break *both* to read the traffic.

```
client share (1216 B) = ML-KEM-768 pk (1184) || X25519 (32)
server share (1120 B) = ML-KEM ct (1088)     || X25519 (32)
secret (64 B) = ss_mlkem || ss_x25519 ─► HKDF(…, transcript) ─► session key
```

## Design space
- **X25519 only.** Tiny (64 bytes on the wire) and fast, but recorded traffic falls to a future quantum attacker.
- **ML-KEM-768 only.** Quantum-safe (2,272 bytes), but everything rests on one new lattice scheme and its new implementations.
- **Hybrid X25519MLKEM768.** 2,336 bytes. Secure if *either* component holds, and the current IETF and industry default.
- **Signatures.** ML-DSA-44/65/87 (2,420 / 3,309 / 4,627-byte signatures), dual-signed with Ed25519 during a transition (lesson 17). SLH-DSA is an option where very conservative hash-based assumptions are wanted.
- **Where.** In TLS, the stack does it: OpenSSL 3.5+ has the hybrid groups natively, and oqs-provider disables its own copies there. Stored data shared with recipients uses HPKE with `MLKEM768_X25519`. Prototyping and interop use liboqs (pending CI).

## How to decide
Criteria: data lifetime against the quantum threat horizon, bytes and CPU per handshake, the blast radius if one scheme breaks, and whether every peer can be upgraded.

Evidence from `pq_measure.py` (timings are medians on the lab machine) → see lab steps 1 and 3:

| Option | Bytes on the wire | Handshake time |
|---|---|---|
| X25519 | 64 | ≈141 µs |
| ML-KEM-768 | 2,272 | ≈180 µs |
| Hybrid X25519MLKEM768 | 2,336 | ≈391 µs |

Authentication costs more than key exchange: a root + leaf certificate chain plus a CertificateVerify signature is 478 B with Ed25519 and 14,106 B with ML-DSA-65 (30×, tryIt 2). That is one reason the key exchange migrates first: a signature forged later cannot harm a session that has already ended, but a recorded key exchange can be decrypted later.

Worked example from one lab run (→ see lab steps 2 and 4). The hybrid handshake agrees on a key from a 1,216 B client share and a 1,120 B server share. An attacker who later breaks X25519 recomputes the key: `False`.

Then the fault. An on-path attacker cuts the server share down to its 32-byte X25519 part. The naive client "is liberal in what it accepts" and falls back: `mode: X25519 (fallback)`, `quantum attacker recovers key: True`. The fix follows RFC 10024 §4.2: the client MUST check the share length and abort with `illegal_parameter`. Classical-only key exchange may exist only as an explicitly configured group, never as a reaction.

## Failure modes at scale
- **Silent downgrade.** A fallback path that only runs under attack or misconfiguration never shows up in happy-path tests. Count `handshake_abort` events, and alert on any classical-only session for protected data.
- **Large ClientHellos.** 1.2 KB more per hello can split it across packets, and some middleboxes mishandle that. You see it as connection failures that correlate with clients enabling PQ, so roll out gradually and watch error rates.
- **Signature bloat.** ML-DSA chains in certificates multiply handshake size (about 14 KB in tryIt 2). Plan for compression, intermediate suppression or future schemes before switching certificates.
- **Prototype libraries in production.** liboqs and oqs-provider are explicitly for prototyping. Ship the standardised implementations in OpenSSL 3.5+ or pyca/cryptography.

## Common mistakes
- Deploying ML-KEM alone because "it is the standard". Hybrid protects against an early break of the new scheme.
- Combining secrets with XOR or without binding the transcript. Concatenate, then run a KDF over a transcript that includes both shares.
- Migrating signatures first. Key exchange protects against recording today, so it comes first.
