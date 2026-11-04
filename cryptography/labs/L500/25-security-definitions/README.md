# Lesson 25 lab - security games, a reduction, discrete log and toy LWE

Perfect secrecy of the OTP, IND-CPA / IND-CCA / EUF-CMA games played against real (pyca) and deliberately broken schemes, the Encrypt-then-MAC reduction run as code, baby-step giant-step and a toy Regev (LWE) scheme next to pyca's ML-KEM-768.

> The broken schemes (ECB, unauthenticated CTR, Encrypt-and-MAC, textbook RSA signatures, tiny LWE) exist to lose the games. Do not reuse them.

Platforms: Linux (validated locally), macOS and Windows expected (pure Python + pyca wheels; CI matrix pending). No OS-specific calls; run every command from this folder so the local imports resolve.

## Run
```
python games.py
python theorem_checks.py
python -m unittest -v
```
Requirements: Python 3.9+ and `cryptography==50.0.2` (`pip install -r ../../../requirements.txt`).

## Expected output - `python games.py` (observed, Linux, Python 3.12, cryptography 50.0.2)
```
IND-CPA advantage (equality adversary, 400 games):
  AES-ECB (deterministic)    1.000
  AES-GCM random nonce       0.000
  AES-GCM fixed nonce        1.000
  Encrypt-and-MAC            1.000
  Encrypt-then-MAC           0.000
IND-CCA advantage (bit-flip + decryption oracle, 400 games):
  AES-CTR (no MAC)           1.000
  AES-GCM                    0.005
  Encrypt-then-MAC           0.005
EUF-CMA textbook RSA (n = 3233): no-message forgeries accepted 100/100, multiplicative 99/100; Ed25519 random signatures accepted 0/100
```

## Expected output - `python theorem_checks.py` (observed; also stored verbatim in content/L500.json `checkOutput`)
```
[T25.1] One-time pad: Pr[M = m | C = c] = Pr[M = m]; perfect secrecy needs |K| >= |M|
3-bit OTP, non-uniform prior: posterior = prior for 64/64 (m, c) pairs
2-bit key on 3-bit messages: 32 of 32 possible (m, c) pairs have posterior != prior; e.g. Pr[M=7 | C=7] = 4/13 vs prior 2/9
pad reused: c1 XOR c2 == m1 XOR m2: True
[T25.2] Deterministic (or nonce-reusing) encryption has IND-CPA advantage 1
  AES-ECB (deterministic)      advantage 1.000 (1000 games)
  AES-GCM fixed nonce          advantage 1.000 (1000 games)
  Encrypt-and-MAC (tag on m)   advantage 1.000 (1000 games)
  AES-GCM random nonce         advantage 0.000 (1000 games)
  Encrypt-then-MAC             advantage 0.000 (1000 games)
[T25.3] Encrypt-then-MAC: Adv_INT-CTXT(A) <= Adv_EUF-CMA(B), and IND-CPA + INT-CTXT => IND-CCA
1-byte tags, 2560 trials: A forges EtM 12 times, B (running A) forges the MAC 12 times; equal: True; expected about 2560/256 = 10
  IND-CCA bit-flip adversary vs AES-CTR (no MAC)   advantage 1.000
  IND-CCA bit-flip adversary vs AES-GCM            advantage 0.002
  IND-CCA bit-flip adversary vs Encrypt-then-MAC   advantage 0.015
[T25.4] Hardness: BSGS solves discrete log in O(sqrt(q)); LWE without error is linear algebra
  q ~ 2^16: recovered x: True, group ops 368 <= 2*ceil(sqrt(q)) = 446: True
  q ~ 2^20: recovered x: True, group ops 1560 <= 2*ceil(sqrt(q)) = 1786: True
  q ~ 2^24: recovered x: True, group ops 4461 <= 2*ceil(sqrt(q)) = 6688: True
  q ~ 2^28: recovered x: True, group ops 17007 <= 2*ceil(sqrt(q)) = 30720: True
  q = 3329, n = 16: error 0 -> elimination recovers s: True; error in [-2, 2] -> recovers s: False
  toy Regev, m = 32 samples: decryption errors 0/1000 bits with |e| <= 2, 122/1000 with |e| <= 300 (threshold q/4 = 832)
  pyca ML-KEM-768: encapsulation key 1184 B, ciphertext 1088 B, shared secret 32 B, decapsulates: True
[D25] EUF-CMA: textbook RSA signatures vs RSA-PSS
textbook RSA n = 3233: no-message forgeries accepted 100/100, multiplicative (2 oracle queries) 100/100
pyca RSA-PSS 2048: product of two signatures accepted: False
```

## Tests
`python -m unittest -v` -> `Ran 7 tests ... OK` (observed).

## What the checks do and do not prove
The theorems are proved in the lesson (content/L500.json, `theorems[].proof`). The checks confirm them on exhaustive small cases and random large cases and guard the implementation; they are not proofs for all inputs. `research/l500_checks.py` re-runs this script and fails if any line changes.
