# 07 – Digital signatures with Ed25519

Read first: `content/concepts/L200/07-digital-signatures-ed25519.md`. Full lesson (steps, walkthrough, sources): `content/L200.json` (lesson 7).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python signatures.py
python -m unittest -v
python try_it.py
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2)
```
RFC 8032 TEST 1 public key: True
RFC 8032 TEST 1 signature:  True
sizes: raw private 32 B, raw public 32 B, PEM private 119 B, PEM public 113 B
signature file: app-1.0.tar.gz.sig 64 bytes
verify original:        True
verify with other key:  False
verify after 1 change:  False
```
Tests:
```
Ran 6 tests in 0.019s
OK
```

## Build task
Key rotation: add key_id(pub) (first 16 hex chars of SHA-256 of the raw key) and verify_with_keyring(keyring, path, sig_path) returning the signer's key_id or None.

Hints: Loop over the keyring and call pub.verify(); catch InvalidSignature and continue. · public_bytes_raw() gives the 32 raw bytes to hash.

Reference solution: `solution_keyring.py` (passes: `Ran 2 tests in 0.010s` → OK). Test **your** `signatures.py`:

macOS (zsh): `BUILD_IMPL=signatures python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_IMPL="signatures"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_IMPL`

Before you add the feature this fails on purpose (observed: `FAILED (errors=2)`).

## Try it (predict first)
1. Sign the same message twice with the same key and compare the signatures. *Predict:* Different, like ECDSA?
2. Serialize one public key as raw, PEM and OpenSSH; compare sizes and reload the PEM. *Predict:* Sizes differ; the 32 key bytes are the same.

```bash
python try_it.py
```
Observed locally:
```
1) same key + same message -> identical signatures: True | first 8 bytes: 8081583b8784835c
2) raw 32 B | PEM 113 B | OpenSSH 80 B | PEM loads back to same key: True
   OpenSSH form: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINdamAGCsQq31Uv+08lkBzoO4XLz2qYjJa8CGmj3B1Ea
```

## If it fails
| Symptom | Action |
|---|---|
| ValueError loading a key | PEM vs raw mix-up: use load_pem_public_key for .pub, from_public_bytes for 32 raw bytes. |
| Verification fails on Windows only | Read and write files in binary mode ('rb'/'wb'); text mode changes line endings. |
