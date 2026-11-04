# 16 – Secrets handling in applications

Read first: `content/concepts/L300/16-secrets-in-applications.md`. Full lesson (steps, walkthrough, failure lab, trade-offs, sources): `content/L300.json` (lesson 16).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python secrets_app.py
python -m unittest -v
python try_it.py
python agent_assist.py        # fake model server; --real uses LOCAL_MODEL_URL / LOCAL_MODEL
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2, Linux sandbox)
```
loaded from file: Secret('***') | length 40
6 JSON log lines, e.g. {"headers": {"Accept": "application/json", "Authorization": "Bearer sk_demo_5993718a7211a334e3a12aea88313527"}, "level": "DEBUG", "msg": "upstream request", "order": 1}
scanner findings:
  line 1: BEARER (pattern)
  line 1: KNOWN_SECRET (value of a configured secret)
  line 1: SENSITIVE_KEY (Authorization)
```
Keys, key IDs, serial numbers and nanosecond timings are random or machine-dependent and change per run; everything else is seeded.

Tests (`python -m unittest -v`, all test files in this folder):
```
Ran 11 tests in 1.095s
OK
```

## Failure lab: break it, then harden it
**Fault (seeded):** `handle_request()` has a debug path that logs the outgoing headers; the request that takes it is chosen by `random.Random(16)`.

**Symptom:** see the output above (the first JSON line contains the Bearer token, and `scan_log` reports BEARER, KNOWN_SECRET and SENSITIVE_KEY on line 1).

**Fix = build task:** add a `logging.Filter` on the handler that masks sensitive key names, known secret values and token patterns in the message, its args and nested `extra` fields; `scan_log` over the emitted log must return `[]`.

Hints: Merge args first: `record.getMessage()`, then set `record.args = None`. · Deep-copy `record.ctx` before masking so the caller's dict is not changed.

Reference solution: `solution_redact.py` → `python solution_redact.py` prints:
```
{"headers": {"Accept": "application/json", "Authorization": "[REDACTED]"}, "level": "DEBUG", "msg": "upstream request", "order": 1}
scanner findings after the fix: []
```
**Proof** (`test_build_task.py`). Against the reference solution:
```
Ran 2 tests in 0.002s
OK
```
Against the unfixed lab file (observed — this is the "fails before"):
```
FAIL: test_message_args_and_nested_fields (test_build_task.TestNoSecretsInLogs.test_message_args_and_nested_fields)
FAIL: test_seeded_request_mix_leaves_clean_logs (test_build_task.TestNoSecretsInLogs.test_seeded_request_mix_leaves_clean_logs)
Ran 2 tests in 0.004s
FAILED (failures=2)
```
Test **your** `secrets_app.py`:

macOS (zsh): `BUILD_IMPL=secrets_app python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_IMPL="secrets_app"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_IMPL`

## Try it (predict first)
1. Print a config dict holding the key as a str and as a `Secret`. *Predict:* Which one shows the key?
2. Log the key base64-encoded (like a Kubernetes Secret manifest) and scan. *Predict:* Does the exact-value scanner catch it?

```bash
python try_it.py
```
Observed locally:
```
1) plain str : {'service': 'orders', 'api_key': 'sk_demo_c0ffeec0ffeec0ffeec0ffeec0ffee'}
1) Secret    : {'service': 'orders', 'api_key': Secret('***')}
2) scan with known=[key]:           []
2) scan with known=[key, b64(key)]: [(1, 'KNOWN_SECRET', 'value of a configured secret')]
```

## Loading a secret from a file (both machines)
macOS (zsh):
```
printf 'sk_demo_123' > orders_api_key && chmod 600 orders_api_key
export ORDERS_API_KEY_FILE="$PWD/orders_api_key"
```
Windows (PowerShell):
```
Set-Content -NoNewline -Encoding utf8 orders_api_key 'sk_demo_123'
$env:ORDERS_API_KEY_FILE = "$PWD\orders_api_key"
```
`load_secret("ORDERS_API_KEY")` reads the file first and falls back to `ORDERS_API_KEY`. In containers the file usually lives under `/run/secrets/<name>` (Docker secrets) or a mounted Kubernetes Secret volume. Kubernetes Secrets are stored unencrypted in etcd by default and only base64-encoded in manifests.

## Agent assist: review a log for leaked secrets
`agent_assist.py` scans `review_me.log` (fake values), redacts, passes the text through a gate (lesson 9's `SECRET` regex plus this lesson's scanner must find nothing), asks the model, and checks every claim against `scan_log`:
```
sent to the model (redacted):
  {"level": "INFO", "msg": "service start", "config": "/etc/orders/app.yaml"}
  {"headers": {"Authorization": "[REDACTED]"}, "level": "DEBUG", "msg": "upstream request"}
  db_password: "[REDACTED]"
  token_ttl_seconds: 3600
  {"level": "INFO", "msg": "order sent", "status": 200}
  smtp_url: smtp://[REDACTED]@mail.local:587
line 2: MISSED by agent (scanner found it)
line 3: CONFIRMED - agent explains: a credential appears to be logged here; remove it or log a
line 4: REJECTED (scanner: no leak)
line 6: MISSED by agent (scanner found it)
LEAKS = [2, 3, 6] (decided by scan_log); the agent only proposes and explains.
```
The fake model is naive on purpose (keyword match), so it misses two leaks and flags one false positive; the scanner decides. `--real` uses Ollama (`LOCAL_MODEL_URL`, `LOCAL_MODEL`); not run in the sandbox. Never paste unredacted logs or real keys into any model.

## Learning tool check (CyberChef)
```
base64 as stored in a manifest: c2tfZGVtb19jMGZmZWVjMGZmZWVjMGZmZWVjMGZmZWVjMGZmZWU=
CyberChef 'From Base64' should print the demo value, length 38
```
Paste the base64 into CyberChef **From Base64**: the demo value appears, which shows that base64 is not protection.

## Learning tool: Gitleaks (pending a manual run)
Gitleaks v8.30.1 (MIT). macOS: `brew install gitleaks`. Windows: `gitleaks_8.30.1_windows_x64.zip` (or `windows_arm64.zip`) from https://github.com/gitleaks/gitleaks/releases.
1. `gitleaks dir review_me.log -v` (same on both machines). The lab's scanner decides `LEAKS = [2, 3, 6]` for this file (see the agent assist above). Write down which lines Gitleaks reports.
2. Pipe the base64 value from `tool_check.py` into the stdin scanner with decoding on:
   - macOS (zsh): `echo '{"data": "c2tfZGVtb19jMGZmZWVjMGZmZWVjMGZmZWVjMGZmZWVjMGZmZWU="}' | gitleaks stdin --max-decode-depth=2 -v`
   - Windows (PowerShell): `'{"data": "c2tfZGVtb19jMGZmZWVjMGZmZWVjMGZmZWVjMGZmZWVjMGZmZWU="}' | gitleaks stdin --max-decode-depth=2 -v`
   Compare with tryIt 2. The lab's exact-value scanner gives `scan with known=[key]: []` until you add `b64(key)`; then it finds `KNOWN_SECRET`. Gitleaks decodes base64 (8.26.0 and later) and matches patterns plus entropy instead of known values.

It is not known whether Gitleaks' default rules flag these low-entropy demo values (`demo-only-s3cr3t`, `sk_demo_c0ffee…`). Record what it finds; a miss is a lesson in itself. Use demo values only: never put real secrets into a shared report.

## If it fails
| Symptom | Action |
|---|---|
| Scanner still finds the key after your fix | The filter is on the logger, not the handler, or it ignores `record.args` / nested dicts. |
| `KeyError: secret ORDERS_API_KEY not configured` | Set `ORDERS_API_KEY_FILE` (preferred) or `ORDERS_API_KEY`. |
| Old API key rejected too early | Clock or `grace_s` too small; watch the `previous` count before ending the window. |
| agent_assist refuses to send | Good: the gate found secret-like text after redaction. Extend `redact()`, never the gate. |
