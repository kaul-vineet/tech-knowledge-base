# 19 – Keys in hardware-style storage: PKCS#11, non-exportable keys and key ceremonies

Read first: `content/concepts/L400/19-keys-in-hardware.md`. Full lesson (steps, walkthrough, options, failure lab, trade-offs, sources): `content/L400.json` (lesson 19).

## Design brief
The release-signing key (lesson 14) signs every artifact. It sits as a PEM file on the build host. A build-host compromise must not let the attacker sign releases after the incident is cleaned up.

Constraints:
- the application process can never read private key bytes
- after clean-up (key disabled / session closed) the attacker can no longer sign
- signing latency <= 1 ms on the build host
- every signing operation leaves an audit event
- recovery plan if the device is lost

**Question:** Where should the signing key live and how does the application use it?

**Decision:** `ADR-0019-signing-key-storage.md` (Nygard ADR in this folder).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python soft_token.py
python key_storage_options.py
python ceremony.py
python -m unittest -v
python try_it.py
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2 (OpenSSL 4.0.3 wheel), Linux sandbox)
`python soft_token.py`:
```
1) wrong PIN: CKR_PIN_INCORRECT
2) signed via handle 1 | sig bytes: 64 | public key DER bytes: 44
--- fault: a compromised app asks the token for the private key
attributes: {'CKA_SENSITIVE': False, 'CKA_VALUE': 48, 'CKA_EXTRACTABLE': True}
after logout the stolen key still signs offline: True | audit events: 6
```

`python key_storage_options.py`:
```
{"option": "file key", "app_can_read_key": true, "sign_us": 35.1, "attacker_signs_after_cleanup": true}
{"option": "KMS-style remote signing (HTTP, 127.0.0.1)", "app_can_read_key": false, "sign_us": 5001.5, "attacker_signs_after_cleanup": false}
{"option": "token handle (PKCS#11-shaped, non-exportable)", "app_can_read_key": false, "sign_us": 40.1, "attacker_signs_after_cleanup": false}
```

`python ceremony.py`:
```
{"step": 1, "do": "SO initialises token, sets USER PIN (out of band)", "by": "SO", "seen_by": ["witness-b", "witness-c"]}
{"step": 2, "do": "generate release-signing-2026 in token (CKM_EDDSA, non-exportable)", "by": "custodian-a", "seen_by": ["witness-b", "witness-c"]}
{"step": 3, "do": "export PUBLIC key and read fingerprint aloud", "sha256": "dfa076b7ef64b6852d14a0e82552f526e1c3f1bdaa6bdd832162f54a67d8e44c", "seen_by": ["witness-b", "witness-c"]}
transcript verifies: True
edited transcript verifies: False
custodian as own witness: need 2 distinct witnesses who are not the custodian
```

Timings (µs/ms) are medians on the sandbox machine and differ on yours; sizes, counts and seeded results are exact. Keys, signatures and fingerprints are random per run.

Tests (`python -m unittest -v`, all test files in this folder):
```
Ran 14 tests in 0.088s
OK (skipped=1)
```

## Options and evidence
| Option | Evidence (measured here) | Verdict |
|---|---|---|
| A: PEM file next to the app | app can read key: True; sign ≈35.1 µs; attacker signs after clean-up: True. | Rejected: a single read gives permanent signing power. |
| B: KMS-style remote signing | app can read key: False; sign ≈5001.5 µs over HTTP on 127.0.0.1 (new connection per call); after clean-up: False (key disabled). | Good for many services; misses the 1 ms constraint without connection reuse. |
| C: PKCS#11 token, non-exportable, sign via handle | app can read key: False; sign ≈40.1 µs; after clean-up: False. | Chosen for the build host (ADR-0019); front with a KMS when many services sign. |

## Failure lab: break it, then fix it
**Fault (seeded):** The application relies on the token's defaults (sensitive: no, extractable: yes); a compromised app asks for CKA_VALUE (attribute order from random.Random(19)).

**Symptom:** `attributes: {'CKA_SENSITIVE': False, 'CKA_VALUE': 48, 'CKA_EXTRACTABLE': True} / after logout the stolen key still signs offline: True | audit events: 6`

**Fix = build task:** Token-enforced non-exportable keys: private keys are always created CKA_SENSITIVE=True and CKA_EXTRACTABLE=False (so ALWAYS_SENSITIVE and NEVER_EXTRACTABLE are True); a template that asks otherwise raises CKR_TEMPLATE_INCONSISTENT.

Hints: Override generate_key_pair in a Session subclass and merge an ENFORCED dict last. · Return your session class from SoftToken.open_session().

Reference solution: `solution_nonexportable.py` → `python solution_nonexportable.py` prints:
```
attributes: {'CKA_SENSITIVE': True, 'CKA_EXTRACTABLE': False, 'CKA_ALWAYS_SENSITIVE': True, 'CKA_NEVER_EXTRACTABLE': True}
read CKA_VALUE: CKR_ATTRIBUTE_SENSITIVE
wrap (export) the key: CKR_KEY_UNEXTRACTABLE
flip CKA_EXTRACTABLE back on: CKR_ATTRIBUTE_READ_ONLY
template asking extractable: CKR_TEMPLATE_INCONSISTENT
signing via handle still works: 64 byte signature
```

**Proof** (`test_build_task.py`). Against the reference solution:
```
Ran 4 tests in 0.010s
OK
```

Against the shipped, unfixed lab file (observed — this is the "fails before"):
```
FAIL: test_attributes_prove_lifetime_protection (test_build_task.TestNonExportableByDefault.test_attributes_prove_lifetime_protection)
FAIL: test_key_cannot_be_wrapped_out (test_build_task.TestNonExportableByDefault.test_key_cannot_be_wrapped_out)
FAIL: test_private_value_cannot_be_read (test_build_task.TestNonExportableByDefault.test_private_value_cannot_be_read)
FAIL: test_template_cannot_opt_out (test_build_task.TestNonExportableByDefault.test_template_cannot_opt_out)
Ran 4 tests in 0.008s
FAILED (failures=4)
```

Test **your** `soft_token.py` (the shipped file is the unfixed one):

macOS (zsh): `BUILD_TARGET=mine python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_TARGET`  
(`BUILD_IMPL=<module>` still works, as in L200/L300.)

## Fitness function
Static: no module outside the token implementation reads private key bytes (private_bytes*, wrap_key). Inventory: every private key on the token is ALWAYS_SENSITIVE and NEVER_EXTRACTABLE. Also run over the capstone.  
Test: `test_fitness_no_key_export.py` · Threshold: 0 forbidden calls; 0 exportable private keys in the inventory

## Scaling limits
- Throughput: one token signs serially; signal = sign queue latency rising with release frequency - add tokens/HSM partitions or batch-sign manifests.
- Many consumers: per-host tokens multiply ceremonies and PINs; signal = number of hosts holding signing PINs - centralise behind a KMS (OpenBao transit with external-key) and audit there.
- Disaster recovery: non-exportable keys cannot be restored from software backups; signal = a single device holding a production key - provision a second device in the ceremony and rehearse rotation.

## Try it (predict first)
1. Try three wrong PINs and then the correct one against the hardened token. *Predict:* Locked out even with the right PIN.
2. Measure signing via a handle against signing with raw key bytes (500 runs, median). *Predict:* Handle costs a few microseconds more.

```bash
python try_it.py
```
Observed locally:
```
1) logins: ['CKR_PIN_INCORRECT', 'CKR_PIN_INCORRECT', 'CKR_PIN_INCORRECT', 'CKR_PIN_LOCKED']
2) sign via handle 39.9 us vs raw key 34.0 us (overhead 1.18x, plus one audit event per call: 502 events)
```

## Equivalents (pending CI)
`python pkcs11_softhsm.py` here (skip branch):
```
PKCS11_MODULE not set: skipped (CI ubuntu job installs softhsm2 and python-pkcs11==0.10.1)
```

Same design against a real PKCS#11 module: init a token, export PKCS11_MODULE, run pkcs11_softhsm.py (P-256 key, SENSITIVE/non-EXTRACTABLE, sign via handle, verify with cryptography).

macOS (zsh):
```zsh
brew install softhsm
softhsm2-util --init-token --free --label kb-l19 --so-pin 5678 --pin 1234   # demo PINs
python -m pip install python-pkcs11==0.10.1
export PKCS11_MODULE=$(brew --prefix softhsm)/lib/softhsm/libsofthsm2.so
python pkcs11_softhsm.py
```
Windows (PowerShell):
```powershell
Not verified natively: run the mac/Linux commands inside WSL2 (Ubuntu: sudo apt install softhsm2; module /usr/lib/softhsm/libsofthsm2.so)
```

## Learning tool: OpenBao (transit engine + web UI) (pending a manual run)
Start the dev server (lesson 12 README), enable transit, then: bao write transit/keys/release-signing type=ed25519 ; bao write transit/sign/release-signing input=$(echo -n 'release 1.4.0' | base64) ; bao read transit/export/signing-key/release-signing

Expected: Signing returns 'vault:v1:...'; the export is refused because transit keys are created with exportable=false (OpenBao transit API: 'exportable (bool: false)', and once set to true it cannot be disabled) - the service version of the lab's 'read CKA_VALUE: CKR_ATTRIBUTE_SENSITIVE'. The exact CLI error text was not checked. Dev mode only, 127.0.0.1. Pending a manual run: the tool was not run in the sandbox; the value comes from the lab's printed output.

Install — macOS: brew install openbao (official install page), or podman run -d --name bao -p 127.0.0.1:8200:8200 docker.io/openbao/openbao:2.7.2 server -dev -dev-root-token-id=root -dev-listen-address=0.0.0.0:8200 · Windows: Container only (Docker Desktop / Podman), same podman run command; a native Windows binary was not checked · Licence: MPL-2.0 (OSI) · https://github.com/openbao/openbao/releases

## If it fails
| Symptom | Action |
|---|---|
| CKR_PIN_LOCKED | Only the SO can reset the user PIN (C_InitPIN); in the lab, create a new SoftToken. |
| CKR_TEMPLATE_INCONSISTENT | Your template asked for an extractable or non-sensitive private key; the hardened token refuses by design. |
| pkcs11_softhsm.py: KeyError PKCS11_MODULE | Export PKCS11_MODULE to the libsofthsm2 path (see the step's mac/windows lines). |
