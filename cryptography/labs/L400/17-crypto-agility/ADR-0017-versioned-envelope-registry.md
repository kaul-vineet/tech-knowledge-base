# ADR-0017: Versioned envelope with per-algorithm identifiers, a registry and policy-driven dual signing

## Status
Accepted (2026-10-28, lesson 17 lab). Revisit when the policy phase moves to `pq-only` or a new AEAD is added.

## Context
Encrypted, signed documents live for years. AES-256-GCM and Ed25519 are fine today, but ML-DSA (FIPS 204) has to be
introduced before a quantum attacker can forge Ed25519, and an AEAD may need replacing on short notice. The format must
let old and new algorithms coexist without a flag day, and a swap must not need code changes in every service.
Measured in `measure_options.py` (1,000 documents of 1 KiB):
- A, one algorithm and no identifier (v1): a swap forces 1,000 rewrites before the switch, or 2.0 trial decryptions per read.
- B, per-algorithm identifiers plus a registry (v2): 31 extra header bytes, 0 rewrites before the switch, 1000/1000 old documents still readable.
- C, suite identifiers: 6 identifiers for 2 AEADs × 3 signature phases, growing to 9 when one AEAD is added (B needs 4, then 5).
Dual signing costs 3,373 bytes per document (Ed25519 64 + ML-DSA-65 3,309).

## Decision
1. Use envelope format v2: the header carries `v`, `aead` (algorithm identifier), `kid`, the nonce and the context. The whole header is the AEAD's AAD.
2. Only `registry.py` names concrete algorithms. It maps identifiers to code and gives each one a status: active (any use), deprecated (read and verify only) or disallowed (refuse).
3. Bind every data key to exactly one algorithm (`Keyring.entries[kid] = (alg, key)`).
4. The verifier's policy phase (`classic` → `transition` → `pq-only`) decides which signatures are required. A signature the envelope lists but the policy does not require is ignored; a required signature that is missing fails verification.
5. Negotiation picks the first locally preferred active algorithm the peer offers. If there is none, it fails; it never falls back.
6. Keep reading v1 envelopes through the registry's `LEGACY_V1_AEAD`, and migrate them lazily on read.
7. Fitness function: `agility_lint.py` (via `test_fitness_agility.py`) fails the build when any module outside the allow-list imports a primitive, names an algorithm class or hard-codes an algorithm id.

## Consequences
- Swapping the default AEAD is a one-line policy change (lab step 2). Old data stays readable until its algorithm is disallowed. Migration is lazy, and the `envelopes_by_aead` metric shows what is left.
- Every envelope is 31 bytes larger, plus 3,373 bytes of signatures during the transition phase. ML-DSA-65 signing is about 40× slower than Ed25519 on the lab machine (≈1,380 µs vs ≈34 µs in the README run; ML-DSA signing time varies between runs).
- The registry becomes a security-critical file: changes to statuses and phases need review like code.
- Having more algorithms means more code paths to test, so each registry entry needs its own round-trip test (RFC 7696 §3.2, "too many choices can be harmful").
- Signature stripping is blocked only because the policy, not the envelope, decides what is required. Any verifier that skips `registry.required_signatures()` reintroduces the fault.
