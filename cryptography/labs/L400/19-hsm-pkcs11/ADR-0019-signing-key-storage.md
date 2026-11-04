# ADR-0019: Release-signing keys live in a PKCS#11 token as non-exportable objects; the application holds only handles

## Status
Accepted (2026-10-28, lesson 19 lab). The software token stands in for SoftHSM2 / an HSM; production needs a real
module behind the same PKCS#11 interface (pending CI against SoftHSM2 2.7.0).

## Context
The release-signing key (Ed25519, lesson 14) signs every artifact. If it leaks, every release can be forged until
every verifier distrusts the key, and the leak may not be noticed. Three storage options were measured in `key_storage_options.py` (one host compromise, then clean-up):

| Option | App can read key | Sign latency (median, lab machine) | Attacker can still sign after clean-up |
|---|---|---|---|
| PEM file on disk | yes | ≈35 µs | **yes**: the copied bytes work forever |
| KMS-style remote signing (HTTP on 127.0.0.1) | no | ≈5,002 µs (new TCP connection per call) | no: key disabled in the service |
| Token handle (PKCS#11-shaped, non-exportable) | no | ≈40 µs | no: the session is gone, and a handle is not a key |

In every option the attacker can sign *while* they control the host. Only the file key also lets them sign *afterwards*.

## Decision
1. Generate signing keys inside the token. The token, not the application, sets `CKA_SENSITIVE=True` and `CKA_EXTRACTABLE=False`; a template that asks otherwise fails with `CKR_TEMPLATE_INCONSISTENT`.
2. Applications find keys by label and sign through `C_Sign` with a handle. The SO role administers the token but cannot use keys; the USER PIN comes from a secret file (lesson 16), and three wrong PINs lock the token.
3. Every key operation emits an audit event, and the capstone feeds these into the signed audit log.
4. Generate new long-term keys in a key ceremony (`ceremony.py`): a custodian plus at least 2 witnesses, the public-key fingerprint read aloud, and a proof-of-possession signature over the transcript.
5. Fitness function: `test_fitness_no_key_export.py`. No module outside the token reads private key bytes, and every private key in the token inventory has `ALWAYS_SENSITIVE` and `NEVER_EXTRACTABLE` set.
6. When many services sign, front the token with a KMS-style service (OpenBao transit with `exportable=false`, or `external-key` for HSM-backed keys); that adds network latency.

## Consequences
- Key theft becomes key *misuse*: limited to the compromise window and visible in the audit log. That still needs monitoring (capstone anomaly rules).
- Non-exportable means no software backup. Recovery needs a second token provisioned in the same ceremony, or an HSM-native backup scheme, and losing every token means rotating to a new key and re-establishing trust.
- Per-call overhead is small for an in-process token (≈1.2×). Remote KMS adds about a millisecond per call in production (more in this Python lab), so batch or cache signatures where the protocol allows.
- A software token is only as strong as the host; this lab teaches the interface, and real protection comes from the hardware boundary.
