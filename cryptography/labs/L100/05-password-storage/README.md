# 05 – Password storage (Argon2id, scrypt fallback)

Argon2id is in `cryptography.hazmat.primitives.kdf.argon2` (added in 44.0.0, PHC helpers in 45.0.0; requires OpenSSL ≥ 3.2 – the official 50.0.2 wheels bundle OpenSSL 4.0.3). Verified locally with `cryptography==50.0.2`.

## Run
```bash
python passwords.py
python -m unittest -v
```

## Expected output (observed locally; salts/hashes and timings change every run)
```
RFC 9106 Argon2id tag: 0d640df58d78766c08c037a34a8b53c9d01ef0452d75b65eb52520e96b01e659
RFC 7914 scrypt  dk  : fdbabe1c9d3472007856e7190d01e9fe ...
argon2id hash (0.120s): $argon2id$v=19$m=19456,t=2,p=1$SiD6dAa4Z5mdBsQf/i7ZZQ$qBtbjVMUiSyxtzqjCzpIFqHjUkGbU9C7pYZ0DesRC/A
same password, new salt -> different hash: True
verify right password: True
verify wrong password: False
scrypt fallback (1.455s): scrypt$131072$8$1$z1X3SV9JN8PVXKtmVzyC6w==$wc2+EKZ3pTIGAg7AmWmXtH6nDNXesZfXkorhV/QOuNs=
scrypt verify right/wrong: True False
```

## Parameters (OWASP Password Storage Cheat Sheet, checked 2026-10-28)
- Argon2id minimum: m=19 MiB (19456 KiB), t=2, p=1 (equivalent alternatives listed in the cheat sheet, e.g. m=46 MiB, t=1).
- scrypt (only if Argon2id unavailable): N=2^17, r=8, p=1 (≈128 MiB).
- Salt: 16 random bytes per password (RFC 9106 recommendation); stored inside the PHC string.
- Benchmark on your server; OWASP says a hash should generally take < 1 s.

## If it fails
| Symptom | Action |
|---|---|
| `MemoryError` / very slow scrypt | The box has < 256 MiB free; on small CI runners use Argon2id or a documented OWASP alternative row |

## Try it (concept experiments)
1. Double `memory_cost` to 38912, hash, then verify an old m=19456 hash. *Predict first*, then compare.
2. Verify `'hunter2 '` (trailing space) and `'Hunter2'`. *Predict first*, then compare.

```bash
python try_it.py
```
Observed locally (cryptography 50.0.2):
```
1) new PHC prefix: $argon2id$v=19$m=38912,t=2,p=1$ | time 0.070s -> 0.128s (x1.8)
   old m=19456 hash still verifies: True
2) verify 'hunter2'   -> True
2) verify 'hunter2 '  -> False
2) verify 'Hunter2'   -> False
```

Timing varies per run (observed x1.4-x5.4 on a shared sandbox); the True/False lines do not.
