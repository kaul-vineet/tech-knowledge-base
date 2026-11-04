# 18 – Post-quantum cryptography in practice: ML-KEM, ML-DSA and hybrids

Read first: `content/concepts/L400/18-post-quantum-in-practice.md`. Full lesson (steps, walkthrough, options, failure lab, trade-offs, sources): `content/L400.json` (lesson 18).

## Design brief
Two internal services exchange documents that must stay confidential for 10 years; traffic may be recorded. pyca/cryptography 50.0.2 (OpenSSL 4.0.3 wheels) is the only crypto dependency allowed.

Constraints:
- confidential against a future quantum attacker (data lifetime 10 years)
- still secure if the new lattice scheme turns out to be broken
- key-share bytes per handshake <= 2,400 B
- no silent classical fallback (0 classical-only sessions for this data)
- no prototype-only libraries in production

**Question:** Which key exchange should the services use, and how must the client behave when the peer's share is not what the group defines?

**Decision:** `ADR-0018-hybrid-key-exchange.md` (Nygard ADR in this folder).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python pq_hybrid.py
python pq_measure.py
python -m unittest -v
python try_it.py
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2 (OpenSSL 4.0.3 wheel), Linux sandbox)
`python pq_hybrid.py`:
```
{"kem": "X25519", "client_share": 32, "server_share": 32, "secret": 32, "on_wire": 64}
{"kem": "ML-KEM-768", "client_share": 1184, "server_share": 1088, "secret": 32, "on_wire": 2272}
{"kem": "ML-KEM-1024", "client_share": 1568, "server_share": 1568, "secret": 32, "on_wire": 3136}
{"kem": "X25519MLKEM768", "client_share": 1216, "server_share": 1120, "secret": 64, "on_wire": 2336}
1) hybrid handshake: client share 1216 B, server share 1120 B, keys match: True, mode: X25519MLKEM768
2) quantum attacker with X25519 broken recovers the key: False
--- fault: an on-path attacker rewrites the server share to its X25519 part only (downgrade)
client accepted a 32-byte server share | mode: X25519 (fallback) | quantum attacker recovers key: True
```

`python pq_measure.py`:
```
{"option": "X25519", "on_wire_bytes": 64, "handshake_us": 140.7, "safe_if_CRQC_exists": false, "safe_if_lattice_break": true}
{"option": "ML-KEM-768", "on_wire_bytes": 2272, "handshake_us": 180.3, "safe_if_CRQC_exists": true, "safe_if_lattice_break": false}
{"option": "X25519MLKEM768", "on_wire_bytes": 2336, "handshake_us": 390.5, "safe_if_CRQC_exists": true, "safe_if_lattice_break": true}
{"signature": "Ed25519", "public_key_bytes": 32, "signature_bytes": 64, "sign_us": 36.4, "verify_us": 108.0}
{"signature": "ML-DSA-44", "public_key_bytes": 1312, "signature_bytes": 2420, "sign_us": 659.7, "verify_us": 128.1}
{"signature": "ML-DSA-65", "public_key_bytes": 1952, "signature_bytes": 3309, "sign_us": 1721.3, "verify_us": 204.7}
{"signature": "ML-DSA-87", "public_key_bytes": 2592, "signature_bytes": 4627, "sign_us": 1522.7, "verify_us": 326.2}
{"hpke": "MLKEM768_X25519 (X-Wing)", "enc_bytes": 1120, "wrapped_32B_key_bytes": 1168, "classic_X25519_enc_bytes": 32, "seal_us": 142.8}
```

Timings (µs/ms) are medians on the sandbox machine and differ on yours; sizes, counts and seeded results are exact. Keys, signatures and fingerprints are random per run.

Tests (`python -m unittest -v`, all test files in this folder):
```
Ran 15 tests in 0.018s
OK (skipped=2)
```

## Options and evidence
| Option | Evidence (measured here) | Verdict |
|---|---|---|
| A: X25519 only | 64 B on the wire, handshake ≈140.7 µs; quantum attacker recovers recorded keys. | Rejected: fails the 10-year confidentiality constraint. |
| B: ML-KEM-768 only | 2272 B, ≈180.3 µs; insecure if ML-KEM or its implementation breaks. | Rejected for now: single point of failure in a young scheme. |
| C: hybrid X25519MLKEM768, strict | 2336 B, ≈390.5 µs; secure if either component holds (lab tests both directions). | Chosen (ADR-0018). |

## Failure lab: break it, then fix it
**Fault (seeded):** An on-path attacker rewrites the server share to its 32-byte X25519 part (or 33 bytes; choice from random.Random(18)).

**Symptom:** `client accepted a 32-byte server share | mode: X25519 (fallback) | quantum attacker recovers key: True`

**Fix = build task:** Strict client_finish: accept only a server share of exactly MLKEM_CT + X_LEN bytes for the negotiated group, otherwise emit a handshake_abort JSON event and raise HandshakeError('illegal_parameter ...'). No fallback branch.

Hints: RFC 10024 4.2: the client MUST check the ciphertext length and abort with illegal_parameter. · Classical-only is a separate, explicitly configured group, never a reaction to a malformed share.

Reference solution: `solution_strict.py` → `python solution_strict.py` prints:
```
normal: X25519MLKEM768 | keys match: True
{"event": "handshake_abort", "alert": "illegal_parameter", "share_bytes": 32}
downgraded 32-byte share: refused (illegal_parameter: X25519MLKEM768 server share must be 1120 bytes, got 32)
{"event": "handshake_abort", "alert": "illegal_parameter", "share_bytes": 33}
downgraded 33-byte share: refused (illegal_parameter: X25519MLKEM768 server share must be 1120 bytes, got 33)
```

**Proof** (`test_build_task.py`). Against the reference solution:
```
Ran 3 tests in 0.057s
OK
```

Against the shipped, unfixed lab file (observed — this is the "fails before"):
```
FAIL: test_downgraded_share_is_refused (test_build_task.TestNoSilentFallback.test_downgraded_share_is_refused)
FAIL: test_one_extra_byte_is_refused (test_build_task.TestNoSilentFallback.test_one_extra_byte_is_refused)
Ran 3 tests in 0.346s
FAILED (failures=2)
```

Test **your** `pq_hybrid.py` (the shipped file is the unfixed one):

macOS (zsh): `BUILD_TARGET=mine python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_TARGET`  
(`BUILD_IMPL=<module>` still works, as in L200/L300.)

## Fitness function
pq_policy.json names a PQ-safe group with no classical fallback, its key shares fit the byte budget, and the deployed client refuses a downgraded share.  
Test: `test_fitness_pq_policy.py` · Threshold: 0 classical-only groups; key shares <= 2,400 B; downgrade -> HandshakeError

## Scaling limits
- Packet size: a 1,216 B key share pushes ClientHellos past one packet; signal = handshake failures/timeouts rising for clients that enable PQ (middleboxes) - roll out gradually.
- CPU at high handshake rates: hybrid ≈2.8x the X25519 time in this Python lab; signal = handshake CPU share on TLS terminators - use session resumption and native stacks.
- Certificates: ML-DSA chains are ~30x larger (14,106 B vs 478 B in tryIt 2); signal = handshake bytes and latency on constrained links - keep classical certificates until signature migration is planned.

## Try it (predict first)
1. Compute the key-share sizes of the higher-security hybrid SecP384r1MLKEM1024 with real keys. *Predict:* About 1.4x the X25519MLKEM768 bytes.
2. Build a root + leaf certificate chain with Ed25519 and with ML-DSA-65 (cryptography signs X.509 with ML-DSA since 49.0) and add a CertificateVerify-sized signature. *Predict:* ML-DSA much larger - maybe 10x?

```bash
python try_it.py
```
Observed locally:
```
1) SecP384r1MLKEM1024: client share 1665 B, server share 1665 B, on wire 3330 B (X25519MLKEM768: 2336 B)
2) root+leaf certificates + CertificateVerify: Ed25519 478 B, ML-DSA-65 14106 B (30x)
```

## Equivalents (pending CI)
`python oqs_crosscheck.py` here (skip branch):
```
liboqs-python not installed: skipped (CI ubuntu job installs liboqs-python==0.16.0.1)
```

`python pq_tls_probe.py` here (skip branch):
```
skipped: needs Python 3.15+ with OpenSSL 3.5+ (have Python 3.12.15, OpenSSL 3.3.7 7 Apr 2026)
```

liboqs interop: pip install liboqs-python==0.16.0.1 (needs git, CMake and a C compiler; builds liboqs 0.16.0 on first import), then python oqs_crosscheck.py. TLS group: Python 3.15 linked to OpenSSL 3.5+, then python pq_tls_probe.py.

macOS (zsh):
```zsh
brew install cmake
python -m pip install liboqs-python==0.16.0.1
python oqs_crosscheck.py
```
Windows (PowerShell):
```powershell
winget install -e --id Kitware.CMake  # plus Build Tools for Visual Studio (C++ workload)
python -m pip install liboqs-python==0.16.0.1
python oqs_crosscheck.py
```

## Learning tool: Wireshark (pending a manual run)
With an OpenSSL 3.5+ build (catalog: brew openssl@3; Windows: not covered) run openssl s_server -accept 127.0.0.1:8443 -cert/-key from lab 9's PKI and openssl s_client -connect 127.0.0.1:8443 -groups X25519MLKEM768; capture loopback and open the ClientHello/ServerHello key_share.

Expected: Should match the lab's printed value: key_share group X25519MLKEM768 (0x11ec) with a 1216-byte client key_exchange and a 1120-byte server key_exchange (lab: 'client share 1216 B, server share 1120 B'); the classical X25519 share is 32 B. Pending a manual run: the tool was not run in the sandbox; the value comes from the lab's printed output.

Install — macOS: brew install --cask wireshark-app (or the official universal .dmg) · Windows: Official x64/Arm64 installer from wireshark.org (bundles Npcap) · Licence: GPL-2.0 (OSI) · https://www.wireshark.org/download.html

## If it fails
| Symptom | Action |
|---|---|
| UnsupportedAlgorithm: ML-KEM-768 is not supported by the backend | Use the official cryptography>=48 wheels (OpenSSL 3.5+); 50.0.2 is pinned in requirements.txt. |
| pq_tls_probe.py says skipped | Expected on Python < 3.15 or OpenSSL < 3.5 (the sandbox has 3.12 + OpenSSL 3.3.7); CI tries it. |
| liboqs-python import tries to download and build | That is documented behaviour (it builds liboqs on first import); install git, CMake and a compiler, or set OQS_INSTALL_PATH. |
