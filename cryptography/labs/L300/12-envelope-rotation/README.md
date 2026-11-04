# 12 – Envelope encryption and key rotation

Read first: `content/concepts/L300/12-envelope-encryption-key-rotation.md`. Full lesson (steps, walkthrough, failure lab, trade-offs, sources): `content/L300.json` (lesson 12).

## Run (same commands on macOS and Windows inside the activated venv)
```bash
python envelope.py
python -m unittest -v
python try_it.py
python openbao_transit.py      # equivalent; skips unless BAO_ADDR/BAO_TOKEN are set
```

## Expected output (observed locally: Python 3.12.15, cryptography 50.0.2, Linux sandbox)
```
sealed 6 records with orders-kek:v1 | header: {'kid': 'orders-kek:v1', 'ctx': 'order-1'}
rotate -> orders-kek:v2 | old records still: 6/6 decrypt
{"event": "rewrap", "id": "order-1", "from": "orders-kek:v1", "to": "orders-kek:v2"}
{"event": "rewrap", "id": "order-2", "from": "orders-kek:v1", "to": "orders-kek:v2"}
{"event": "rewrap", "id": "order-3", "from": "orders-kek:v1", "to": "orders-kek:v2"}
{"event": "rewrap", "id": "order-4", "from": "orders-kek:v1", "to": "orders-kek:v2"}
{"event": "rewrap", "id": "order-5", "from": "orders-kek:v1", "to": "orders-kek:v2"}
{"event": "rewrap", "id": "order-6", "from": "orders-kek:v1", "to": "orders-kek:v2"}
{"metric": "records_by_kid", "orders-kek:v2": 6}
data ciphertext unchanged by rewrap: True
retire v1 after a full rewrap: 6/6 decrypt
--- fault: rotate again, the rewrap job crashes, the operator deletes v2 anyway
rotate -> orders-kek:v3
{"event": "rewrap", "id": "order-1", "from": "orders-kek:v2", "to": "orders-kek:v3"}
job: rewrap job crashed after 1 records | counts: {'orders-kek:v2': 5, 'orders-kek:v3': 1}
after retire v2: 1/6 decrypt; LOST ['order-2', 'order-3', 'order-4', 'order-5', 'order-6'] ({'no KEK for orders-kek:v2'})
```
Keys, key IDs, serial numbers and nanosecond timings are random or machine-dependent and change per run; everything else is seeded.

Tests (`python -m unittest -v`, all test files in this folder):
```
Ran 11 tests in 0.007s
OK (skipped=1)
```

## Failure lab: break it, then harden it
**Fault (seeded):** the rewrap job crashes part-way (`crash_after` chosen by `random.Random(12)`), then the operator retires the old KEK version anyway with the naive `retire()`.

**Symptom:** see the output above (`job: rewrap job crashed after 1 records` then `after retire v2: 1/6 decrypt; LOST [...]`).

**Fix = build task:** make `retire(ring, store, version)` refuse (raise `KeyInUse`) while any record header still names that version, and refuse to retire the primary; resume the idempotent rewrap job first (`rewrap_then_retire`).

Hints: `count_by_kid(store)` already tells you who still needs each version. · The rewrap job skips records already on the primary, so rerunning it after a crash is safe.

Reference solution: `solution_retire.py` → `python solution_retire.py` prints:
```
injected: rewrap job crashed after 2 records
retire refused: orders-kek:v1 still wraps 2 record(s): finish the rewrap job first
resumed job moved 2 record(s); 4/4 decrypt
```
**Proof** (`test_build_task.py`). Against the reference solution:
```
Ran 3 tests in 0.003s
OK
```
Against the unfixed lab file (observed — this is the "fails before"):
```
FAIL: test_primary_cannot_be_retired (test_build_task.TestRetireAfterRewrap.test_primary_cannot_be_retired)
FAIL: test_retire_refused_while_records_use_the_version (test_build_task.TestRetireAfterRewrap.test_retire_refused_while_records_use_the_version)
Ran 3 tests in 0.005s
FAILED (failures=2)
```
Test **your** `envelope.py`:

macOS (zsh): `BUILD_IMPL=envelope python -m unittest -v test_build_task`  
Windows (PowerShell): `$env:BUILD_IMPL="envelope"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_IMPL`

## Try it (predict first)
1. Change a record's header from `orders-kek:v1` to `orders-kek:v2` and decrypt. *Predict:* Decrypts with v2? Fails?
2. Compare the bytes a rewrap re-encrypts with re-encrypting 1,000 records of 4 KiB. *Predict:* How much smaller?

```bash
python try_it.py
```
Observed locally:
```
1) relabelled header: InvalidTag - the kid is bound to the wrapped DEK as AAD
2) wrapped DEK = 60 B (12 nonce + 32 key + 16 tag); rewrapping 1000 x 4096 B records re-encrypts 32,000 key bytes instead of 4,096,000 data bytes
```

## Observability: read the JSON lines
Each `{"event": "rewrap", ...}` line records one move; the final `{"metric": "records_by_kid", ...}` line is the number to check before retiring a version. A version may leave the keyring only when its count is 0.

## Equivalent: OpenBao transit engine (pending CI)
`openbao_transit.py` runs the same story against OpenBao (MPL-2.0; 2.7.2 checked 2026-10-28): create key → encrypt (`vault:v1:...`) → rotate → rewrap (`vault:v2:...`, no plaintext returned) → `min_decryption_version=2` → old ciphertext refused. Paths from https://openbao.org/docs/api/secret/transit/. Not run in the sandbox (no container runtime); CI starts a dev server on ubuntu.

Start a dev server (Podman, same on both machines; `docker` works the same way):
```
podman run -d --name bao -p 127.0.0.1:8200:8200 docker.io/openbao/openbao:2.7.2 server -dev -dev-root-token-id=root -dev-listen-address=0.0.0.0:8200
podman exec -e BAO_ADDR=http://127.0.0.1:8200 -e BAO_TOKEN=root bao bao secrets enable transit
```
macOS (zsh): `export BAO_ADDR=http://127.0.0.1:8200 BAO_TOKEN=root && python openbao_transit.py`  
Windows (PowerShell): `$env:BAO_ADDR="http://127.0.0.1:8200"; $env:BAO_TOKEN="root"; python openbao_transit.py`  
Dev mode is in-memory and unsealed: never use it for real data. Without the variables the script prints:
```
OpenBao not configured (set BAO_ADDR and BAO_TOKEN): skipped. Offline check: key_version('vault:v2:abc') = 2
```

## Learning tool: OpenBao (transit engine + web UI) (pending a manual run)
OpenBao 2.7.2 (MPL-2.0) is the service version of this lab. Install it on macOS with `brew install openbao` (official install page) or use the container above. On Windows use the container (Docker Desktop / Podman); a native Windows binary was not checked. Start the dev server and run `openbao_transit.py` as above. Then look at key `orders-kl12`:
1. `podman exec -e BAO_ADDR=http://127.0.0.1:8200 -e BAO_TOKEN=root bao bao read transit/keys/orders-kl12` (same on zsh and PowerShell). It should show `latest_version` 2 and `min_decryption_version` 2, the service version of `retire v1 after a full rewrap: 6/6 decrypt`.
2. Open the web UI on the dev listener and find the same key, its versions and its min decryption version. The UI path was not checked in the official docs; the catalog lists it as a gap.
3. Ask the service to decrypt the old `vault:v1:` ciphertext. It refuses, as `openbao_transit.py` printed (`decrypt old v1: refused, HTTP 4xx`). The lab's naive `retire()` instead loses data silently (`after retire v2: 1/6 decrypt; LOST [...]`): OpenBao archives old versions rather than deleting them. As the transit docs say for an emergency, set `min_decryption_version` back to 1, rewrap the old ciphertext, and set it to 2 again.

Dev mode is in-memory, unsealed and TLS-off: use it for learning only, and keep it on 127.0.0.1.

## Learning tool check (CyberChef)
`python tool_check.py` prints fixed DEMO values to unwrap a DEK by hand with CyberChef's AES Decrypt (mode GCM, key/IV hex, GCM tag, AAD):
```
Key (hex):          000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f
IV (hex):           0c0c0c0c0c0c0c0c0c0c0c0c
Ciphertext (hex):   5413bb59feb9cacf635790eb7622249e0e07234f00c5a199934fa0a2a3679e4f
GCM tag (hex):      9217297105acba4f2afbbd4eb6cceaaa
AAD (UTF8):         orders-kek:v1
expected output:    a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0
AAD 'orders-kek:v2' must fail: yes, InvalidTag
```

## If it fails
| Symptom | Action |
|---|---|
| `UnknownKey: no KEK for orders-kek:vN` | That version was deleted. Restore it from backup if you can; otherwise the records are lost. Next time check `records_by_kid` first. |
| `InvalidTag` on open | The header (kid) or the record id (ctx) was changed, or the wrong KEK bytes were loaded. |
| OpenBao test skipped | Expected without `BAO_ADDR`/`BAO_TOKEN`; start the dev server above. |
| OpenBao HTTP 400/403 | Transit not enabled (`bao secrets enable transit`) or wrong token. |
