# Lesson 23 lab - number theory, textbook RSA and Diffie-Hellman (INSECURE learning toys)

Extended Euclid, modular inverse, CRT, Miller-Rabin, **textbook RSA** and **textbook Diffie-Hellman** written from scratch, then checked against key material from pyca/cryptography 50.0.2.

> **Insecure by design.** Textbook RSA is deterministic and malleable; textbook DH is unauthenticated; none of this is constant-time. Use RSA-OAEP/PSS, X25519 + HKDF or ML-KEM from pyca/cryptography in real code.

Platforms: Linux (validated locally), macOS and Windows expected (pure Python + pyca wheels; CI matrix pending). No OS-specific calls; run every command from this folder so the local imports resolve.

## Run
```
python nt_toys.py
python theorem_checks.py
python -m unittest -v
```
Requirements: Python 3.9+ and `cryptography==50.0.2` (`pip install -r ../../../requirements.txt`).

## Expected output - `python nt_toys.py` (observed, Linux, Python 3.12, cryptography 50.0.2)
```
1) egcd(240, 46) = (2, -9, 47) | modinv(17, 3120) = 2753
2) crt([2, 3, 2], [3, 5, 7]) = 23
3) textbook RSA round trip: True | CRT decrypt agrees: True
   deterministic (same m -> same c): True
4) malleability: Dec(c * 2^e) == 2*m: True
5) toy DH (p=23, g=5) both sides agree: True
INSECURE LEARNING TOYS - use RSA-OAEP/PSS, X25519+HKDF or ML-KEM from pyca/cryptography in real code
```

## Expected output - `python theorem_checks.py` (observed; also stored verbatim in content/L500.json `checkOutput`)
```
[T23.1] Bezout / extended Euclid
a*x + b*y = gcd(a, b) = math.gcd(a, b): 5000/5000 random 256-bit pairs
inverse exists exactly when gcd = 1 (and a*inv = 1 mod b): 5000/5000
egcd(240, 46) = (2, -9, 47) | modinv(17, 3120) = 2753
[T23.2] Euler's theorem a^phi(n) = 1 (mod n) when gcd(a, n) = 1
exhaustive n = 2..400: 48677/48677 coprime pairs satisfy it
Fermat a^(p-1) = 1 (mod p), 303 primes < 2000, bases 2,3,5,7: 1208/1208
phi(3233) = 3120 = (61-1)*(53-1) = 3120; 2^560 mod 561 = 1 (561 is composite)
[T23.3] Chinese remainder theorem
x -> (x mod 3, x mod 5, x mod 7) on 0..104: 105 distinct images (bijection onto 3*5*7 = 105)
crt() reconstructs x: 105/105 | crt([2, 3, 2], [3, 5, 7]) = 23
pyca 2048-bit key: CRT decryption = plain decryption = m for 20/20 random m
pyca CRT parameters match ours: dmp1 = True | dmq1 = True | iqmp = True
[T23.4] RSA correctness m^(e*d) = m (mod n) for every m in Z_n
n = 3233 (61*53), e = 17, d = 2753: 3233/3233 messages round-trip, incl. 113 with gcd(m, n) > 1
pyca 2048-bit key (e = 65537): 45/45 round-trip (40 random + p, 5q, 0, 1, n-1)
pyca d satisfies e*d = 1 mod lcm(p-1, q-1): True
[D23] textbook RSA malleability and textbook DH (insecure toys)
Enc(65) = 2790; attacker sends c * 2^e mod n = 3017; Dec = 130 (= 2 * 65)
Enc(6) * Enc(7) mod n decrypts to 42 (= 6 * 7)
DH p=23 g=5 a=6 b=15: A = 8, B = 19, B^a = 2, A^b = 2
pyca FFDH exchange == our pow(Y, x, p): True | pyca 50.0.2 warns FFDH deprecated: True
```

## Tests
`python -m unittest -v` -> `Ran 8 tests ... OK` (observed).

## What the checks do and do not prove
The theorems are proved in the lesson (content/L500.json, `theorems[].proof`). The checks confirm them on exhaustive small cases and random large cases and guard the implementation; they are not proofs for all inputs. `research/l500_checks.py` re-runs this script and fails if any line changes.
