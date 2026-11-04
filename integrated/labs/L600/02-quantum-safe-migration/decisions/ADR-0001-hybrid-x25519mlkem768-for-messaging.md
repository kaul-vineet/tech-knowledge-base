# ADR-0001: Messaging moves to hybrid X25519MLKEM768 key exchange with ML-DSA-65 transcript signatures

## Status
Accepted (2026-10-30)

## Context
Patient messages must stay confidential for 12 years (x = 12) and the team needs about 2 years to migrate (y = 2).
With our planning assumption z = 10 years (ADR-0003), x + y = 14 > z: traffic recorded today is exposed to
harvest-now-decrypt-later. NIST IR 8547 (final, October 2026) deprecates quantum-vulnerable key establishment after 2030
and disallows it after 2035, and names hybrid key establishment as an accommodated option. RFC 10024 (August 2026)
defines X25519MLKEM768 for TLS 1.3: 1216-byte client share, 1120-byte server share. Our budget is a 1,400-byte client
first flight and 6,144 bytes per handshake.

## Decision
Messaging negotiates X25519MLKEM768 (ML-KEM first, then X25519, as RFC 10024 lays it out; cryptography L400 #18's
strict client: no silent fallback) and signs the handshake transcript with ML-DSA-65 using a pinned server key.
Payloads stay AES-256-GCM. Measured: client flight 1,352 B, handshake 5,871 B (F2 passes); ML-DSA-87 would be
7,145 B and is rejected by the budget.

## Consequences
- Confidentiality holds if either X25519 or ML-KEM-768 holds; one more KEM to patch and monitor.
- Handshakes are about 45x larger than X25519 + Ed25519; the budget fitness function guards growth.
- During the rollout a client still offers X25519 for v1 servers; that window is a flag with an owner and expiry (ADR-0002).
- Certificates/chains with ML-DSA keys are out of scope here (pinned key); revisit before a public PKI use.
