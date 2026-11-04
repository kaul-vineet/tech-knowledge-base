# 03 – Secure randomness (`secrets` vs `random`)

## Run
```bash
python randomness.py
python -m unittest -v
```

## Expected output (observed locally; token values change every run, the True/False lines do not)
```
api_token_urlsafe  kCbfe1vHh8k_Pe0ECDLqKfk6ieS_QI0HaUzlfWYQCjo
session_id_hex     a3d7aee4aa415638337fba8ca564b2a6
aes256_key         eb4014beb28d57a1724192f0303ea43128c1c567f0a508eb15cc4f18dcef18a3
gcm_nonce          3dfdccf8f484ecb31514f846
pin_6_digits       270560
insecure token       ab411443d547b789ec845f36a966ee9a
attacker found seed  1793164812 == issued_at: True (0.078s)
attacker can mint    True
same seed same token True
secrets differs      True
```
The attacker tries every second in a ±1 h window (7,201 seeds) and recovers the clock-seeded token in well under a second.

## If it fails
| Symptom | Action |
|---|---|
| `attacker found seed None` | Your clock jumped during the run; re-run (window is ±3600 s) |

## Try it (concept experiments)
1. Issue the token 2 h ago with a ±1 h scan, then widen the scan to ±3 h. *Predict first*, then compare.
2. Use `secrets.token_hex(16)` as the token and run the same scan. *Predict first*, then compare.

```bash
python try_it.py
```
Observed locally (cryptography 50.0.2):
```
1) token issued 2 h ago, window +/-1 h -> attacker finds: None
   same token, window +/-3 h       -> attacker finds seed == issued_at: True
2) secrets.token_hex(16) scanned over 7,201 seeds -> attacker finds: None
```
