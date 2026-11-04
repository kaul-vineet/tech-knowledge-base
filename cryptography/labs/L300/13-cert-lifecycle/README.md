# 13 – Certificate lifecycle: short-lived certs, renewal and revocation

Read first: `content/concepts/L300/13-certificate-lifecycle.md`. Full lesson (steps, walkthrough, failure lab, trade-offs, sources): `content/L300.json` (lesson 13).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python cert_lifecycle.py
python -m unittest -v
python try_it.py
python tool_check.py          # writes tool_check/ca.pem, leaf.pem, crl.pem for step CLI / KeyStore Explorer
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2, Linux sandbox)
```
{"hour": 0, "metric": "cert_expires_in_hours", "value": 159.0, "handshake": "ok", "renewals": 0}
{"hour": 24, "metric": "cert_expires_in_hours", "value": 135.0, "handshake": "ok", "renewals": 0}
{"hour": 48, "metric": "cert_expires_in_hours", "value": 111.0, "handshake": "ok", "renewals": 0}
{"hour": 72, "metric": "cert_expires_in_hours", "value": 87.0, "handshake": "ok", "renewals": 0}
{"hour": 96, "metric": "cert_expires_in_hours", "value": 63.0, "handshake": "ok", "renewals": 0}
{"hour": 120, "metric": "cert_expires_in_hours", "value": 39.0, "handshake": "ok", "renewals": 0}
{"hour": 144, "metric": "cert_expires_in_hours", "value": 15.0, "handshake": "ok", "renewals": 0}
{"hour": 160, "metric": "cert_expires_in_hours", "value": -1.0, "handshake": "FAIL", "renewals": 0}
{"hour": 168, "metric": "cert_expires_in_hours", "value": -9.0, "handshake": "FAIL", "renewals": 0}
static server: first failed handshake at hour 160, 32 failed hours of 192
lifetime: 160.0 h, notBefore backdated 1 h
CRL check now:         revoked (key_compromise)
CRL check other cert:  good
CRL check 25 h later:  stale CRL
skew 5 min, notBefore = issue time: False
skew 5 min, notBefore backdated 1 h: True
```
Keys, key IDs, serial numbers and nanosecond timings are random or machine-dependent and change per run; everything else is seeded.

Tests (`python -m unittest -v`, all test files in this folder):
```
Ran 8 tests in 0.889s
OK
```

## Failure lab: break it, then harden it
**Fault (seeded):** `Server` loads one 160-hour certificate at start-up and `tick()` never renews it; `simulate()` advances a clock hour by hour (renewal jitter seeded with `random.Random(13)`), and in the build-task test the CA is also unreachable for hours 90-124.

**Symptom:** see the output above (the metric `cert_expires_in_hours` falls to `-1.0` and `handshake` turns `FAIL` at hour 160).

**Fix = build task:** write `next_renewal(cert, rng)` (uniform random time at 60-72 % of the lifetime) and a `Server.tick()` that renews when due, retries hourly while the CA is down, hot-swaps the certificate and logs an `cert_expiry_soon` alert line below 25 % lifetime.

Hints: Jitter = `rng.uniform(0.60, 0.72)` times the lifetime, added to notBefore. · On a failed issuance set the next attempt to now + 1 h; keep serving the old (still valid) certificate.

Reference solution: `solution_renewal.py` → `python solution_renewal.py` prints:
```
renewing server, 21 days: 0 failed handshakes, 4 renewals, 0 alerts
CA down hours 90-124: 0 failed handshakes, 4 renewals, 6 alert lines
first alert: {"alert": "cert_expiry_soon", "hours_left": 40.0}
```
**Proof** (`test_build_task.py`). Against the reference solution:
```
Ran 3 tests in 0.237s
OK
```
Against the unfixed lab file (observed — this is the "fails before"):
```
ERROR: test_jitter_spreads_a_fleet (test_build_task.TestRenewal.test_jitter_spreads_a_fleet)
FAIL: test_ca_outage_alerts_and_recovers (test_build_task.TestRenewal.test_ca_outage_alerts_and_recovers)
FAIL: test_no_expired_cert_is_ever_served (test_build_task.TestRenewal.test_no_expired_cert_is_ever_served)
Ran 3 tests in 0.163s
FAILED (failures=2, errors=1)
```
Test **your** `cert_lifecycle.py`:

macOS (zsh): `BUILD_IMPL=cert_lifecycle python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_IMPL="cert_lifecycle"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_IMPL`

## Try it (predict first)
1. 100 servers renew the same certificate: count distinct renewal hours without and with jitter. *Predict:* 1 vs many?
2. Client clock 5, 59 and 61 minutes slow against a certificate backdated by 1 h. *Predict:* Where does it break?

```bash
python try_it.py
```
Observed locally:
```
1) distinct renewal hours for 100 servers: no jitter 1, jitter 20
2) client clock  5 min slow: handshake ok
2) client clock 59 min slow: handshake ok
2) client clock 61 min slow: handshake FAIL (not yet valid)
```

## Observability: read the metric lines
`{"hour": h, "metric": "cert_expires_in_hours", ...}` is printed every 24 simulated hours and at the first failed handshake. A dashboard alert on this value (for example below 25 % of the lifetime) fires days before clients see TLS errors. The fixed server adds `{"alert": "cert_expiry_soon", ...}` lines while the CA is down.

## OCSP (concept only)
OCSP asks a responder about one certificate and gets `good`, `revoked` or `unknown` with thisUpdate/nextUpdate (RFC 6960); pyca/cryptography has `x509.ocsp` builders. Let's Encrypt announced (Dec 2024) that it would add CRL URLs, drop OCSP URLs from certificates on 2025-05-07 and turn its OCSP responders off on 2025-08-06, so the lab builds and checks a CRL.

## Learning tool check (step CLI / KeyStore Explorer)
`python tool_check.py` writes public files only (CA, leaf, CRL):
```
wrote tool_check/ca.pem, leaf.pem, crl.pem
leaf validity hours: 160.0
leaf serial (hex): 535e9465e6f109932b2f01fc703b3afccd001e75 | revoked in crl.pem: yes
```
The serial changes every run. `tool_check/` is not needed by the tests; delete it when done.

## If it fails
| Symptom | Action |
|---|---|
| `static server` never fails | You already changed `tick()`; run `python solution_renewal.py` to compare. |
| `not yet valid` right after issuing | Client clock behind the issuer: backdate notBefore (the lab uses 1 h) and fix NTP. |
| `stale CRL` | The CRL is past nextUpdate: fetch a new one; decide whether stale means fail-closed (safer) or alert. |
| Slow test run on Windows | Each simulated hour runs a full path validation; 21 days = 504 verifications, normally a few seconds. |
