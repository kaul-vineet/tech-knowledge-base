# 08 – Key exchange and hybrid encryption (X25519 + HKDF + AEAD)

Read first: `content/concepts/L200/08-key-exchange-hybrid-encryption.md`. Full lesson (steps, walkthrough, sources): `content/L200.json` (lesson 8).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python seal_box.py
python -m unittest -v
python try_it.py
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2)
```
RFC 7748 6.1 Alice public:   True
RFC 7748 6.1 shared secret:  True
sealed 29 B -> 77 B (overhead 48 = 32 eph_pub + 16 tag)
bob opens:    b'db password rotation at 02:00'
same msg sealed twice -> different blobs: True
eve opens:    InvalidTag (rejected)
aad changed:  InvalidTag (rejected)
eph swapped:  InvalidTag (rejected)
```
Tests:
```
Ran 9 tests in 0.047s
OK (skipped=1)
```

**Equivalent: age CLI (optional)**

macOS (zsh):
```zsh
brew install age
```
Windows (PowerShell):
```powershell
winget install --id FiloSottile.age
```

## Build task
Multi-recipient: add seal_multi(recipients, plaintext) / open_multi(identity, blob): one random file key, wrapped per recipient with seal(), payload sealed once with the stanzas as AAD.

Hints: Format: 1 byte count || n x 80-byte stanzas (32 eph + 32 key + 16 tag) || payload. · open_multi tries each stanza; InvalidTag means 'not mine', try the next.

Reference solution: `solution_multi.py` (passes: `Ran 3 tests in 0.072s` → OK). Test **your** `seal_box.py`:

macOS (zsh): `BUILD_IMPL=seal_box python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_IMPL="seal_box"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_IMPL`

Before you add the feature this fails on purpose (observed: `FAILED (errors=3)`).

## Try it (predict first)
1. Seal 0, 29 and 4096-byte messages and compare blob sizes. *Predict:* Always +48 B (32 eph_pub + 16 tag).
2. Open with a different HKDF info label (v2) than the sender used (v1). *Predict:* InvalidTag: a different label gives a different key.

```bash
python try_it.py
```
Observed locally:
```
1) plaintext    0 B -> blob   48 B
1) plaintext   29 B -> blob   77 B
1) plaintext 4096 B -> blob 4144 B
2) receiver uses info v2, sender used v1 -> InvalidTag (keys differ, domain separation works)
```

## If it fails
| Symptom | Action |
|---|---|
| InvalidTag for the right recipient | Same AAD and same INFO label on both sides; blob must start with the 32-byte ephemeral key. |
| ValueError: Error computing shared key | The peer public key is a small-order point (e.g. all zeros): reject the message. |
