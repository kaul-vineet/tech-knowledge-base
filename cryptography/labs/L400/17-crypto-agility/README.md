# 17 – Crypto agility: versioned envelopes, negotiation and dual signing

Read first: `content/concepts/L400/17-crypto-agility.md`. Full lesson (steps, walkthrough, options, failure lab, trade-offs, sources): `content/L400.json` (lesson 17).

## Design brief
Encrypted, signed invoices are stored for 10 years and read by several services. Ed25519 must give way to ML-DSA (FIPS 204) before quantum attackers arrive, and the AEAD may need replacing after an incident. Today the cipher is implied by the code.

Constraints:
- 0 records rewritten before an algorithm switch (no flag day)
- old records stay readable until their algorithm is explicitly disallowed
- header overhead <= 64 bytes per envelope
- a verifier in the transition phase rejects any envelope missing a required signature
- 0 hard-coded algorithms outside registry.py (static check in CI)

**Question:** How should the envelope name its algorithms, and who decides which algorithms and signatures are acceptable?

**Decision:** `ADR-0017-versioned-envelope-registry.md` (Nygard ADR in this folder).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python agile_envelope.py
python measure_options.py
python -m unittest -v
python try_it.py
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2 (OpenSSL 4.0.3 wheel), Linux sandbox)
`python agile_envelope.py`:
```
1) sealed 3 docs | header: {'v': 2, 'aead': 'A256GCM', 'kid': 'dk-1'} | ct bytes: 37 | sigs: [('Ed25519', 64), ('ML-DSA-65', 3309)]
2) default -> C20P1305 | opened: 4 of 4
{"metric": "envelopes_by_aead", "A256GCM": 3, "C20P1305": 1}
3) negotiate: A256GCM | only A128CBC offered -> no common active algorithm in ['A128CBC']
4) legacy v1 opens: invoice 0: amount=0 | migrate -> {'v': 2, 'aead': 'C20P1305', 'kid': 'dk-2'}
--- fault: the Ed25519 key leaked; a co-tenant re-signs an edited document with Ed25519 only
legit verify: True | forged doc-4 verify: True | sigs on forged: ['Ed25519']
```

`python measure_options.py`:
```
{"option": "A one algorithm, no id", "header_bytes": 43, "swap_rewrites_before_switch": 1000, "trial_decryptions_per_read": 2.0, "rewrite_all_seconds_est": 0.006}
{"option": "B per-algorithm ids + registry", "header_bytes": 74, "extra_header_bytes_vs_A": 31, "swap_rewrites_before_switch": 0, "old_docs_readable_after_switch": "1000/1000", "dual_signature_bytes": 3373}
{"option": "C suite ids", "ids_needed_for_suites": 6, "ids_needed_per_algorithm": 4, "after_adding_one_aead": 9}
{"per_algorithm": {"A256GCM": {"seal_4KiB_us": 1.5}, "C20P1305": {"seal_4KiB_us": 2.2}, "Ed25519": {"sig_bytes": 64, "sign_us": 34.3, "verify_us": 111.0}, "ML-DSA-65": {"sig_bytes": 3309, "sign_us": 1380.1, "verify_us": 202.2}}}
```

Timings (µs/ms) are medians on the sandbox machine and differ on yours; sizes, counts and seeded results are exact. Keys, signatures and fingerprints are random per run.

Tests (`python -m unittest -v`, all test files in this folder):
```
Ran 15 tests in 2.373s
OK
```

## Options and evidence
| Option | Evidence (measured here) | Verdict |
|---|---|---|
| A: one algorithm, no identifier (v1) | 1000 rewrites before a switch, or 2.0 trial decryptions per read after it; header 43 B. | Rejected: every change is a flag day and readers must guess. |
| B: per-algorithm identifiers + registry + policy (v2) | +31 header bytes (74 B), 0 rewrites, 1000/1000 old documents readable after the switch; dual signature 3373 B. | Chosen (ADR-0017), with the verifier fix from the failure lab. |
| C: one suite identifier per combination | 6 suite ids today vs 4 per-algorithm ids; 9 after adding one AEAD. | Rejected for this format: combinatorial growth (RFC 7696 2.1); fine for protocols that negotiate whole suites. |

## Failure lab: break it, then fix it
**Fault (seeded):** The Ed25519 signing key leaked; a co-tenant that holds the shared data key edits a document (victim from random.Random(17)) and re-signs it with Ed25519 only, leaving out the ML-DSA-65 signature.

**Symptom:** `legit verify: True | forged doc-4 verify: True | sigs on forged: ['Ed25519']`

**Fix = build task:** Make verify() policy-driven: require a valid signature for every algorithm in registry.required_signatures() (ignore extra ones), so a stripped envelope fails in the transition phase and an ML-DSA-only envelope passes only in pq-only.

Hints: Build a dict alg -> signature entry from env['sigs'], then loop over the policy's list, not the envelope's. · Keep using reg.verify(): it already refuses unknown and disallowed algorithms.

Reference solution: `solution_agile.py` → `python solution_agile.py` prints:
```
phase: transition | required: ['Ed25519', 'ML-DSA-65']
legit verify: True | stripped (Ed25519 only) verify: False
phase: pq-only | legit verify: True | stripped verify: False
```

**Proof** (`test_build_task.py`). Against the reference solution:
```
Ran 4 tests in 0.267s
OK
```

Against the shipped, unfixed lab file (observed — this is the "fails before"):
```
FAIL: test_pq_only_envelope_needs_pq_only_phase (test_build_task.TestPolicyDecidesSignatures.test_pq_only_envelope_needs_pq_only_phase)
FAIL: test_stripped_envelope_rejected_in_transition (test_build_task.TestPolicyDecidesSignatures.test_stripped_envelope_rejected_in_transition)
Ran 4 tests in 0.110s
FAILED (failures=2)
```

Test **your** `agile_envelope.py` (the shipped file is the unfixed one):

macOS (zsh): `BUILD_TARGET=mine python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_TARGET`  
(`BUILD_IMPL=<module>` still works, as in L200/L300.)

## Fitness function
No module outside the registry imports a primitive, names an algorithm class or hard-codes an algorithm id (AST check, also run over the capstone).  
Test: `test_fitness_agility.py` · Threshold: 0 violations (agility_lint exit code 0)

## Scaling limits
- Many algorithms in the registry: every entry is a code path to test; signal = registry entries with zero reads in the envelopes_by_aead metric for months (prune them) or entries without a round-trip test.
- Very long-lived data: lazy migration on read never touches cold records; signal = deprecated-algorithm counts that stop falling - schedule a background re-seal job like lesson 12's rewrap.
- Signature size: dual signing adds 3,373 B per envelope; for millions of small records the signatures dominate storage - signal = signature bytes / payload bytes > 1; sign batches or manifests instead of each record.

## Try it (predict first)
1. Deprecate A256GCM (default ChaCha20-Poly1305), lazily migrate 5 of 10 documents, then disallow A256GCM. How many remain readable? *Predict:* 5 of 10 - only the migrated ones.
2. Paste a module that imports AESGCM and calls it directly into the static check. *Predict:* Two violations: the import and the class name.

```bash
python try_it.py
```
Observed locally:
```
1) migrated 5/10, then disallowed A256GCM: 5/10 readable; {'metric': 'envelopes_by_aead', 'A256GCM': 5, 'C20P1305': 5}
2) orders/storage.py:1: imports cryptography.hazmat.primitives.ciphers.aead
2) orders/storage.py:3: names algorithm AESGCM
```

## Learning tool: CyberChef (pending a manual run)
Run `python tool_check.py`. In CyberChef use AES Decrypt: Key = printed hex, IV = printed hex, Mode GCM, Input = printed ciphertext (hex), GCM Tag = printed tag, Additional Authenticated Data = the printed AAD JSON. Then change "A256GCM" to "C20P1305" inside the AAD.

Expected: Should match the lab's printed value: output 'invoice 1: amount=100' with the exact AAD; with aead=C20P1305 in the AAD decryption must fail (lab: 'AAD with aead=C20P1305 must fail: yes, InvalidTag'). The AAD must be byte-identical (no spaces, sorted keys). Demo key only. Pending a manual run: the tool was not run in the sandbox; the value comes from the lab's printed output.

Install — macOS: Open the CyberChef web app linked from github.com/gchq/CyberChef, or the offline release zip from https://github.com/gchq/CyberChef/releases (runs fully client-side); Docker ghcr.io/gchq/cyberchef · Windows: Same: web app or the offline release zip from https://github.com/gchq/CyberChef/releases (runs fully client-side) · Licence: Apache-2.0 (OSI) · https://github.com/gchq/CyberChef

`python tool_check.py` (fixed demo values for the tool check):
```
Key (hex):          000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
IV (hex):           111111111111111111111111
Ciphertext (hex):   e90ee2d0d1634a8e594505632c4a65d49722b19525
GCM tag (hex):      c8cadac773ec696c03616b89911c7889
AAD (UTF8):         {"aead":"A256GCM","ctx":"doc-1","kid":"dk-1","n":"ERERERERERERERER","v":2}
expected output:    invoice 1: amount=100
AAD with aead=C20P1305 must fail: yes, InvalidTag
```

## If it fails
| Symptom | Action |
|---|---|
| DisallowedAlgorithm on seal | The policy default points at a deprecated algorithm; pick an active one. |
| EnvelopeError: key dk-1 is bound to A256GCM, header says C20P1305 | Someone relabelled the header or reused a key across algorithms; keys are bound to one algorithm on purpose. |
| agility_lint reports a violation in a new module | Ask the registry (reg.aead(id, key), reg.sign(id, key, data)) instead of importing the primitive. |
