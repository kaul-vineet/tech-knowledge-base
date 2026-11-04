# 09 – A local certificate authority

Read first: `content/concepts/L200/09-local-certificate-authority.md`. Full lesson (steps, walkthrough, sources): `content/L200.json` (lesson 9).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python local_ca.py
python -m unittest -v
python try_it.py
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2)
```
root: CN=KB Local Root CA | CA: True
leaf SAN: ['localhost', '127.0.0.1']
leaf valid: 2026-10-28 -> 2026-11-27
localhost              OK, chain length 2
wrong host             FAIL: validation failed: leaf certificate has no matching subjectAltName
31 days later          FAIL: validation failed: cert is not valid at validation time
untrusted root         FAIL: validation failed: candidates exhausted: all candidates exhausted with no interior errors
```
Tests:
```
Ran 13 tests in 1.885s
OK
```

## Agent assist (code is the judge)
```bash
python agent_assist.py          # fake model server (default)
python agent_assist.py --real   # Ollama at LOCAL_MODEL_URL
```
Observed (fake server):
```
wrong host    verifier=FAIL  code says HOSTNAME_MISMATCH agent says HOSTNAME_MISMATCH CONFIRMED
              agent explains: the name the client asked for is not in the certificate's SAN list.
expired       verifier=FAIL  code says EXPIRED           agent says EXPIRED           CONFIRMED
              agent explains: the certificate's validity period has ended.
clock skew    verifier=FAIL  code says NOT_YET_VALID     agent says EXPIRED           REJECTED
untrusted CA  verifier=FAIL  code says UNTRUSTED_ISSUER  agent says UNTRUSTED_ISSUER  CONFIRMED
              agent explains: no trusted root signed this chain.
VERDICTS come from the verifier; categories from diagnose(); the agent only explains.
```

## Build task
Intermediate CA: add make_hierarchy() -> (root, intermediate, leaf, leaf_key): root (path_length=1) signs an intermediate (path_length=0) that issues the localhost leaf.

Hints: Reuse issue_server(int_key, inter) for the leaf. · The intermediate needs KeyUsage keyCertSign and an AuthorityKeyIdentifier from the root key.

Reference solution: `solution_intermediate.py` (passes: `Ran 3 tests in 0.073s` → OK). Test **your** `local_ca.py`:

macOS (zsh): `BUILD_IMPL=local_ca python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_IMPL="local_ca"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_IMPL`

Before you add the feature this fails on purpose (observed: `FAILED (errors=3)`).

## Try it (predict first)
1. Issue a cert for DNS name ip-only.test (+127.0.0.1), then verify it for 'localhost' and for 'ip-only.test'. *Predict:* localhost fails (not in SAN); ip-only.test passes.
2. Compare the DER and PEM size of the same certificate and load both. *Predict:* PEM ~4/3 of DER; both load to the same certificate.

```bash
python try_it.py
```
Observed locally:
```
1) ask localhost       FAIL: validation failed: leaf certificate has no matching subjectAltName
1) ask ip-only.test    OK, chain length 2
2) DER 424 B, PEM 631 B, ratio 1.49; DER->cert == PEM->cert: True
```

## If it fails
| Symptom | Action |
|---|---|
| 'Certificate is missing required extension' | Add KeyUsage (critical) to the CA; the verifier's profile requires it. |
| 'cert is not valid at validation time' on a new cert | Clock skew: the machine clock is behind not_valid_before; fix NTP or backdate not_before a few minutes. |
