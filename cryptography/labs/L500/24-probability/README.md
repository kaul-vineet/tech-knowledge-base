# Lesson 24 lab - birthday bounds, nonce budgets and entropy

Exact, upper and lower collision probabilities, the 96-bit nonce budget, Shannon and min-entropy, and a Monte-Carlo scale model. Simulations use a seeded `random.Random` for reproducibility - never use it for keys or nonces.

Platforms: Linux (validated locally), macOS and Windows expected (pure Python + pyca wheels; CI matrix pending). No OS-specific calls; run every command from this folder so the local imports resolve.

## Run
```
python prob_tools.py
python theorem_checks.py
python -m unittest -v
```
Requirements: Python 3.9+ and `cryptography==50.0.2` (`pip install -r ../../../requirements.txt`).

## Expected output - `python prob_tools.py` (observed, Linux, Python 3.12, cryptography 50.0.2)
```
96-bit random nonces, q = 2^28: P[collision] = 4.547e-13 (~2^-41.0)
96-bit random nonces, q = 2^32: P[collision] = 1.164e-10 (~2^-33.0)
96-bit random nonces, q = 2^40: P[collision] = 7.629e-06 (~2^-17.0)
96-bit random nonces, q = 2^48: P[collision] = 3.935e-01 (~2^-1.3)
messages per key for risk 2^-32: 6.074e+09 (~2^32.50)
at 1,000,000 messages/s one key reaches 2^32 messages in 71.6 minutes
4-digit PIN where '1234' has 10%: Shannon 12.43 bits, min-entropy 3.32 bits
```

## Expected output - `python theorem_checks.py` (observed; also stored verbatim in content/L500.json `checkOutput`)
```
[T24.1] Union bound P[collision] <= q(q-1)/(2N)
exact <= bound in 20/20 (N, q) cases; N = 365, q = 23: exact 0.507297, bound 0.693151
96-bit nonces, q = 2^32: bound = 2^-33.00
[T24.2] Lower bound P >= 1 - exp(-q(q-1)/(2N)) and the 50 % threshold q ~ 1.1774 sqrt(N)
lower <= exact in 20/20 cases
N = 365: first q with P >= 1/2 is 23 (formula 22.49)
N = 2^32: first q with P >= 1/2 is 77164 (formula 77163)
simulation N = 2^24, q = 4096, 2000 trials: observed 0.400, predicted 0.393
[T24.3] Nonce budget for 96-bit random nonces under one key
P[collision] after 2^32 messages = 1.1642e-10 = 2^-33.00
messages for risk 2^-32 = 6.0740e+09 = 2^32.50; risk 1/2 at 2^48.24
collisions among 2^20 os.urandom(12) nonces: 0 | pyca AES-GCM: 96-bit nonce, 16-byte tag
[T24.4] H_min <= H <= log2|X| (equality iff uniform); poly * negligible is negligible
random distributions satisfying both inequalities: 1000/1000
uniform 2^128: H = H_min = 128 bits | PIN with P('1234') = 0.1: H = 12.43, H_min = 3.32 bits
n^10 * 2^-n < n^-3 for every n >= 83 (checked to 5000); 1/n^3 is not negligible (n^4 * n^-3 = n grows)
2^40 queries, 2^-128 per query: union bound 2^-88
```

## Tests
`python -m unittest -v` -> `Ran 6 tests ... OK` (observed).

## What the checks do and do not prove
The theorems are proved in the lesson (content/L500.json, `theorems[].proof`). The checks confirm them on exhaustive small cases and random large cases and guard the implementation; they are not proofs for all inputs. `research/l500_checks.py` re-runs this script and fails if any line changes.
