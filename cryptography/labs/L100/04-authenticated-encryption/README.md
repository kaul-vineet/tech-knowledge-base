# 04 – Authenticated encryption (AES-256-GCM, ChaCha20-Poly1305)

## Run
```bash
python aead_demo.py
python -m unittest -v
```

## Expected output (observed locally)
```
RFC 8439 2.8.2 ChaCha20-Poly1305 vector: True
GCM spec TC14 AES-256-GCM vector:        True
--- AES-256-GCM (blob 42 bytes = 12 nonce + 14 ct + 16 tag)
  decrypt ok         card=4111-1111
  1 bit flipped      InvalidTag (rejected)
  AAD changed        InvalidTag (rejected)
--- ChaCha20-Poly1305 (blob 42 bytes = 12 nonce + 14 ct + 16 tag)
  decrypt ok         card=4111-1111
  1 bit flipped      InvalidTag (rejected)
  AAD changed        InvalidTag (rejected)
nonce reuse leaks p1^p2: True
attacker who knows p1 recovers p2: b'retreat at dusk!'
```

## Vectors
- RFC 8439 §2.8.2 (key 80..9f, nonce = `07000000` ‖ `4041424344454647`, AAD `50515253c0c1c2c3c4c5c6c7`, tag `1ae10b59…0691`).
- GCM spec (McGrew & Viega) test case 14: AES-256, all-zero key/IV/plaintext block.

## If it fails
| Symptom | Action |
|---|---|
| `InvalidTag` on a message you just encrypted | Decrypt must use the *same* key, nonce and AAD; check you split nonce (first 12 bytes) correctly |

## Try it (concept experiments)
1. Flip one bit of the stored nonce (blob byte 0) and decrypt. *Predict first*, then compare.
2. Seal 0, 14 and 1000-byte plaintexts and compare blob sizes. *Predict first*, then compare.

```bash
python try_it.py
```
Observed locally (cryptography 50.0.2):
```
1) nonce bit flipped -> InvalidTag (rejected)
2) plaintext    0 B -> blob   28 B (overhead 28 B)
2) plaintext   14 B -> blob   42 B (overhead 28 B)
2) plaintext 1000 B -> blob 1028 B (overhead 28 B)
```
