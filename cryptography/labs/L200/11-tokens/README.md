# 11 – Tokens done right: signed JWT-style tokens

Read first: `content/concepts/L200/11-tokens-done-right.md`. Full lesson (steps, walkthrough, sources): `content/L200.json` (lesson 11).
**Learning code – not for production.** Use a maintained library (e.g. PyJWT) configured the same way.
## Run (same commands on macOS and Windows inside the activated venv)
```bash
python tokens.py
python -m unittest -v
python try_it.py
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2)
```
valid token: alice (211 chars)
alg none        naive ACCEPTS role=admin | safe rejects (algorithm 'none' not allowed)
key confusion   naive ACCEPTS role=admin | safe rejects (algorithm 'HS256' not allowed)
expired         naive ACCEPTS role=?     | safe rejects (expired or no exp)
wrong audience  naive ACCEPTS role=?     | safe rejects (wrong audience)
payload edited  naive rejects            | safe rejects (bad signature)
```
Tests:
```
Ran 13 tests in 0.082s
OK
```

## Build task
Replay protection: add ReplayGuard.check(claims, now) and verify_once(token, keys, audience, guard, now): require jti, reject a reused jti, forget ids after exp.

Hints: Store jti -> exp in a dict; purge entries with exp < now on each check. · Call tokens.verify() first; only then record the jti.

Reference solution: `solution_replay.py` (passes: `Ran 3 tests in 0.060s` → OK). Test **your** `tokens.py`:

macOS (zsh): `BUILD_IMPL=tokens python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_IMPL="tokens"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_IMPL`

Before you add the feature this fails on purpose (observed: `FAILED (errors=3)`).

## Try it (predict first)
1. Verify a token that expired 20 s ago with leeway 30 and with leeway 0. *Predict:* Accepted, then rejected.
2. Decode the payload of a signed token without any key. *Predict:* Readable: signing is not encryption.

```bash
python try_it.py
```
Observed locally:
```
1) expired 20 s ago, leeway=30: accepted
1) expired 20 s ago, leeway= 0: rejected (expired or no exp)
2) payload read with NO key: {'sub': 'alice', 'email': 'alice@example.com', 'aud': 'orders-api', 'exp': 1800000060}
```

## If it fails
| Symptom | Action |
|---|---|
| PyJWT: 'The specified alg value is not allowed' | Pass algorithms=[...] containing the alg the issuer uses - never the alg read from the token. |
| Tokens rejected right after issue | Clock skew between issuer and API: sync NTP; keep leeway small (seconds, not hours). |

## Check with independent tools (learningTools)
`tool_check.py` prints a fixed HS256 demo token for CyberChef "JWT Verify" and writes `eddsa.jwt`, `none.jwt` and
`issuer-pub.pem` (public key only) for `step crypto jwt verify`. The demo key is public on purpose.
```bash
python tool_check.py
```
Observed locally (the EdDSA files change every run):
```
HS256 demo token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSIsImF1ZCI6Im9yZGVycy1hcGkiLCJleHAiOjQxMDI0NDQ4MDAsInJvbGUiOiJ1c2VyIn0.HKTDiu55nB_ks2cnZx_ZySPZaxFaSDkNjgrdbFKN-aA
HS256 demo key  : lab11-demo-key-not-a-secret
lab verify      : {'sub': 'alice', 'aud': 'orders-api', 'exp': 4102444800, 'role': 'user'}
EdDSA lab verify: alice | files: eddsa.jwt, none.jwt, issuer-pub.pem
```
Then (pending a manual run; step is not installed in the sandbox):
```zsh
step crypto jwt verify --key tool_check/issuer-pub.pem --alg EdDSA --aud orders-api --subtle < tool_check/eddsa.jwt
```
```powershell
Get-Content tool_check\eddsa.jwt | step crypto jwt verify --key tool_check\issuer-pub.pem --alg EdDSA --aud orders-api --subtle
```
`--subtle` only drops step's required `--iss` check (the lab tokens have no `iss`). `none.jwt` must fail. Details: `../../../documentation/LEARNING-TOOLS.md`.
