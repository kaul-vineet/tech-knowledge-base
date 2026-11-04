# Lab 21 — Quantum and post-quantum: crypto inventory and migration plan

Shor in context (lesson 19's estimator + published estimates), an inventory of `toy_app/` (RSA-OAEP, ECDH, X25519,
ECDSA, TLS config, AES-GCM), priorities from Mosca's X + Y > Z (Y = 3, Z = 9: planning assumptions), and crypto agility
with a hybrid X25519 + ML-KEM-768 that **runs locally** (cryptography 50.0.2). Decision: `docs/adr/0001-crypto-agility.md`.

## Run
```bash
python pqc_lab.py               # shipped: grep inventory
python solution_scanner.py      # AST inventory + plan
python try_it.py
python agent_assist.py --fake   # agent drafts migration notes; code checks them
python -m unittest -v
```

## Expected output
**`python pqc_lab.py`** — observed locally (Python 3.12.15, numpy 2.5.3, cryptography 50.0.2; Linux sandbox, no quantum SDKs); `ms_per_exchange` varies by machine:
```
{"shor_model": {"workload": "rsa-2048", "logical_qubits": 6190, "distance": 27, "physical_qubits": 9025020, "runtime_s": 57870.0}, "ecc": {"workload": "ecc-p256", "logical_qubits": 2330, "toffoli": 128748355584}}
{"source": "Gidney & Ekera 2019/2021", "target": "RSA-2048", "physical_qubits": 20000000, "runtime": "8 hours"}
{"source": "Gidney 2025", "target": "RSA-2048", "physical_qubits": 1000000, "runtime": "under a week", "note": "'less than a million'"}
{"scanner": "grep", "findings": 5}
{"file": "toy_app/auth.py", "line": 1, "algorithm": "RSA", "usage": "unknown", "secrecy_years": 0, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "review manually"}
{"file": "toy_app/billing.py", "line": 1, "algorithm": "RSA", "usage": "unknown", "secrecy_years": 10, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "review manually"}
{"file": "toy_app/billing.py", "line": 3, "algorithm": "RSA", "usage": "unknown", "secrecy_years": 10, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "review manually"}
{"file": "toy_app/billing.py", "line": 7, "algorithm": "RSA", "usage": "unknown", "secrecy_years": 10, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "review manually"}
{"file": "toy_app/config/tls.toml", "line": 3, "algorithm": "RSA-2048", "usage": "unknown", "secrecy_years": 5, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "review manually"}
{"kem": "x25519", "public_key_bytes": 32, "ciphertext_bytes": 32, "ms_per_exchange": 0.398}
{"kem": "ml-kem-768", "public_key_bytes": 1184, "ciphertext_bytes": 1088, "ms_per_exchange": 0.451}
{"kem": "x25519+ml-kem-768", "public_key_bytes": 1216, "ciphertext_bytes": 1120, "ms_per_exchange": 2.201}
```
**`python solution_scanner.py`**:
```
{"scanner": "ast", "findings": 8}
{"file": "toy_app/billing.py", "line": 7, "algorithm": "RSA-3072", "usage": "key-establishment", "secrecy_years": 10, "priority": "P1 now (harvest now, decrypt later)", "replacement": "ML-KEM-768 (FIPS 203); hybrid X25519+ML-KEM-768 during transition"}
{"file": "toy_app/sync.py", "line": 7, "algorithm": "ECDH P-384", "usage": "key-establishment", "secrecy_years": 7, "priority": "P1 now (harvest now, decrypt later)", "replacement": "ML-KEM-768 (FIPS 203); hybrid X25519+ML-KEM-768 during transition"}
{"file": "toy_app/api_client.py", "line": 11, "algorithm": "X25519", "usage": "key-establishment", "secrecy_years": 2, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "ML-KEM-768 (FIPS 203); hybrid X25519+ML-KEM-768 during transition"}
{"file": "toy_app/auth.py", "line": 11, "algorithm": "ECDSA P-256", "usage": "signature", "secrecy_years": 0, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "ML-DSA-65 (FIPS 204)"}
{"file": "toy_app/config/tls.toml", "line": 3, "algorithm": "RSA-2048", "usage": "signature", "secrecy_years": 5, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "ML-DSA-65 (FIPS 204)"}
{"file": "toy_app/config/tls.toml", "line": 4, "algorithm": "ECDHE X25519/P-256", "usage": "key-establishment", "secrecy_years": 5, "priority": "P2 before 2030 (deprecated after 2030, disallowed after 2035)", "replacement": "ML-KEM-768 (FIPS 203); hybrid X25519+ML-KEM-768 during transition"}
{"file": "toy_app/api_client.py", "line": 19, "algorithm": "AES-GCM", "usage": "symmetric", "secrecy_years": 2, "priority": "none", "replacement": "keep (AES-256 / SHA-256 not broken by Shor)"}
{"file": "toy_app/storage.py", "line": 10, "algorithm": "AES-GCM", "usage": "symmetric", "secrecy_years": 10, "priority": "none", "replacement": "keep (AES-256 / SHA-256 not broken by Shor)"}
```
**`python -m unittest`**: `Ran 19 tests ... OK` (everything, including ML-KEM-768, ran locally).

## Try it
```
longer_secrecy ['toy_app/api_client.py:11', 'toy_app/billing.py:7', 'toy_app/sync.py:7']
old_receiver   receiver rejects envelope: unknown kem 'x25519+ml-kem-768'
```

## Agent assist (fake model server)
```
draft     ACCEPT  
summarise REJECT  toy_app/storage.py:10 is symmetric (AES-GCM): keep it, do not replace; P1 item missing: toy_app/sync.py:7
creative  REJECT  toy_app/payments.py:12 is not in the inventory; toy_app/auth.py:11 replacement 'ML-KEM-768' != 'ML-DSA-65'; year 2029 is not a NIST IR 8547 date
```
Only file paths, line numbers and algorithm names are sent to the model. Real model: `LOCAL_MODEL_URL`, `LOCAL_MODEL`, `python agent_assist.py --show`.

## failureLab and build task — AST inventory
Fault: `scan()` greps for "rsa": a docstring is flagged, X25519 / ECDH P-384 / ECDSA are missed, no P1 item.
Fix: resolve imports and aliases with `ast`, classify calls by purpose, comment-aware config rules (`my_scanner.py`).
```bash
BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v        # your my_scanner.py
BUILD_TASK_MODULE=pqc_lab python -m unittest test_build_task test_fitness   # the shipped (unfixed) lab file: must fail
```
```powershell
$env:BUILD_TARGET = "mine"; python -m unittest test_build_task test_fitness -v; Remove-Item Env:BUILD_TARGET
```
Proof — observed locally on the shipped file:
```
FAIL: test_aliased_and_from_imports_resolve (test_build_task.Inventory.test_aliased_and_from_imports_resolve)
AssertionError: None != 'ECDSA P-256'
FAIL: test_docstrings_are_not_findings (test_build_task.Inventory.test_docstrings_are_not_findings)
AssertionError: ('toy_app/auth.py', 1) unexpectedly found in {('toy_app/auth.py', 1): {'file': 'toy_app/auth.py', 'line': 1, 'algorithm': 'RSA', 'usage': 'unknown'}, ('toy_app/billing.py', 1): {'file': 'toy_app/billing.py', 'line': 1, 'algorithm': 'RSA', 'usage': 'unknown'}, ('toy_app/billing.py', 3): {'file': 'toy_app/billing.py', 'line': 3, 'algorithm': 'RSA', 'usage': 'unknown'}, ('toy_app/billing.py', 7): {'file': 'toy_app/billing.py', 'line': 7, 'algorithm': 'RSA', 'usage': 'unknown'}, ('toy_app/config/tls.toml', 3): {'file': 'toy_app/config/tls.toml', 'line': 3, 'algorithm': 'RSA-2048', 'usage': 'unknown'}}
FAIL: test_matches_ground_truth (test_build_task.Inventory.test_matches_ground_truth)
AssertionError: Lists differ: [{'file': 'toy_app/auth.py', 'line': 1, 'algorithm': 'RSA', '[356 chars]wn'}] != [{'file': 'toy_app/api_client.py', 'line': 11, 'algorithm': '[711 chars]nt'}]
FAIL: test_purpose_is_classified (test_build_task.Inventory.test_purpose_is_classified)
AssertionError: 'unknown' != 'key-establishment'
FAIL: test_ratchet_blocks_new_quantum_vulnerable_code (test_fitness.MigrationFitness.test_ratchet_blocks_new_quantum_vulnerable_code)
AssertionError: Lists differ: [{'file': 'toy_app/auth.py', 'line': 1, 'a[282 chars]wn'}] != []
FAIL: test_recall_and_precision (test_fitness.MigrationFitness.test_recall_and_precision)
AssertionError: Tuples differ: (0.0, 0.0) != (1.0, 1.0)
Ran 7 tests in 0.185s
FAILED (failures=6)
```
Solution and `BUILD_TARGET=mine` with a correct file: `Ran 7 tests ... OK`.
`test_fitness.py` copies `toy_app` into a temporary folder inside this lab to prove the ratchet catches a new `ec.ECDH()`;
on network mounts where cleanup fails, delete the leftover `tmp*` folder (git-ignored).
