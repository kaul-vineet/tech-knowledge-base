## Why it matters
Every algorithm you deploy will need replacing: Ed25519 by ML-DSA (FIPS 204) before quantum attackers arrive, an AEAD after an incident, a hash because a regulator says so. If the cipher is implied by the code ("we always use AES-GCM"), each change becomes a flag day. Every record has to be rewritten and every reader upgraded at once. RFC 7696: algorithms age; protocols need a way to migrate. Agility is designing that path before you need it.

## Mental model
Think of **labels and a rulebook**. Every envelope carries a label naming its algorithms. A single registry translates labels into code, and a policy (the rulebook) says which labels may be written, which may only be read, and which are refused. Readers trust the rulebook, never the label alone.

```
envelope: { h: {v:2, aead:"A256GCM", kid, n, ctx}, ct, sigs:[{alg:"Ed25519"},{alg:"ML-DSA-65"}] }
                 │ label                                   │ labels
registry: id ─► implementation + status (active | deprecated | disallowed)
policy:   default AEAD, preference order, signature phase (classic → transition → pq-only)
```

## Design space
- **One algorithm, no identifier** (v1). Simplest; a change means a new format version and a rewrite, or readers that guess.
- **Per-algorithm identifiers plus a registry** (v2). A few header bytes, one dispatch point, old and new data side by side (as in JOSE and COSE).
- **Suite identifiers** (one id for a whole combination, as in TLS 1.2 cipher suites). Easy to keep combinations consistent, but the number of ids multiplies.
- **Negotiation** (for live connections). Pick the best algorithm both sides support. It must fail closed: no silent fallback, and the choice should be integrity-protected against downgrade (RFC 7696 §2.4).
- **Dual signing** during a transition. Two signatures, classical and PQ, so old and new verifiers both work.

## How to decide
Criteria: old data readable after the switch, bytes per envelope, identifiers and code paths to maintain, and whether a verifier can be tricked into accepting less than policy requires.

Evidence from `measure_options.py` (1,000 documents of 1 KiB) → see lab step 2:
- Option A forces 1,000 rewrites before a switch, or 2.0 trial decryptions per read.
- Option B costs 31 extra header bytes (74 instead of 43), needs 0 rewrites, and 1000/1000 old documents stay readable.
- Option C needs 6 suite ids for 2 AEADs × 3 signature phases, and 9 after adding one AEAD; option B needs 4, then 5.

Dual signing costs 3,373 bytes per envelope (Ed25519 64 + ML-DSA-65 3,309), and ML-DSA signing is about 40× slower than Ed25519 here (≈1,380 vs ≈34 µs).

Worked example from one lab run (→ see lab steps 1-5). Three invoices are sealed under `A256GCM`. The policy default then changes to `C20P1305`, and a fourth invoice uses it, with no code change: `opened: 4 of 4`, `{"A256GCM": 3, "C20P1305": 1}`. Negotiation picks `A256GCM` when the peer offers `A256GCM` and the unknown `A128CBC`, and fails outright when the peer offers only `A128CBC`. A v1 legacy record opens and migrates lazily to v2.

Then the fault. The Ed25519 key has leaked, and a co-tenant re-signs an edited `doc-4` with Ed25519 only. The naive verifier accepts it (`forged doc-4 verify: True`), because "any valid signature" let the *envelope* decide what counts. The fix makes the verifier's policy phase decide: in `transition` both signatures are required, and a missing one fails.

## Failure modes at scale
- **Downgrade through the label.** If a reader honours whatever the header names, an attacker picks the weakest algorithm you still support. Statuses in the registry, enforced on read, stop this. Watch the count of `deprecated` reads.
- **Never-ending deprecation.** Old algorithms stay "read-only" forever because nobody measures who still needs them. The `envelopes_by_aead` metric is your migration dashboard; disallow an algorithm only when its count is zero.
- **Registry sprawl.** Every algorithm is a code path that needs tests (RFC 7696 §3.2: too many choices hurt). Test each entry; prune unused ones.
- **Agility bypassed in code.** One module importing `AESGCM` directly pins the algorithm; `agility_lint.py` fails the build (the capstone runs it too).
- **Key reuse across algorithms** invites cross-protocol attacks. Bind each key to one algorithm id.

## Common mistakes
- Trusting the algorithm field in the message instead of the verifier's policy (the stripping fault).
- Falling back to "whatever works" when negotiation finds nothing in common.
- Treating "add ML-DSA" as the end of the job: the hard part is the phased policy and the metrics that let you retire the old algorithm.
