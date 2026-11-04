# 14 – Reliability: timeouts, retries, budgets and fallbacks

Decide in code how long to wait, what to retry, how much to spend and what to answer when the model server fails - before it fails in production.

Concept note: `../../../content/concepts/L300/14-reliability-budgets.md` · lesson object: `content/L300.json` #14

## Run (fake server – validated)
```bash
python compare.py          # starts its own seeded fake servers on 127.0.0.1
head -5 reliability.jsonl
python -m unittest -v
```
PowerShell (Windows 11):
```powershell
python compare.py          # starts its own seeded fake servers on 127.0.0.1
Get-Content reliability.jsonl -TotalCount 5
python -m unittest -v
```

### Expected output (observed 2026-10-28)
```
naive     wall 20.3 s | slowest question 6.1 s | HTTP calls 44 | tokens 269 | canned 0 | flaky server saw {'requests': 44, '503': 17, 'slow': 10}
hardened  wall  6.7 s | slowest question 1.79 s | HTTP calls 46 | tokens 132 | canned 1 | flaky server saw {'requests': 43, '503': 17, 'slow': 10}
hardened events: {'retry': 24, 'call': 19, 'give_up': 3, 'fallback': 3, 'cache_hit': 2, 'canned': 1}
```
`reliability.jsonl` (first lines, then the fallback / cache events):
```
{"event": "retry", "model": "fake-model", "attempt": 0, "error": "timeout", "ms": 503, "sleep_s": 0.033}
{"event": "retry", "model": "fake-model", "attempt": 1, "error": "http_503", "ms": 6, "sleep_s": 0.058}
{"event": "call", "model": "fake-model", "attempt": 2, "ms": 9, "tokens": 3}
{"event": "retry", "model": "fake-model", "attempt": 0, "error": "http_503", "ms": 2, "sleep_s": 0.041}
{"event": "call", "model": "fake-model", "attempt": 1, "ms": 38, "tokens": 9}
{"event": "fallback", "reason": "fake-model: http_503 after 3 attempts"}
{"event": "cache_hit", "key": "02affd35dcfe"}
```
Wall times vary by machine; tokens, canned answers, faults and event counts are deterministic (seed 7). Token counts are word counts (fake server).

Tests: `Ran 9 tests ... OK` (about 45 s – the failure-lab test runs both loops).

## Failure lab
| | |
|---|---|
| Fault (seeded) | Seeded flaky model server (rule F): 30% HTTP 503 and 20% responses delayed by 2 s, seed 7 - the same 17 errors and 10 stalls on every run. |
| Symptom | The naive loop (no timeout, retry anything at once, no budget) takes 20.3 s for 10 questions, one question hangs 6.1 s, and it spends 269 tokens - 161 on a single runaway question. |
| Fix | Per-call timeout 0.5 s, retries only on 5xx/timeouts with backoff + jitter, per-question budget (8 calls, 1,500 tokens, $0.01), fallback to a smaller model, response cache, canned answer. |
| Proof | FailureLab.test_naive_hangs_and_overspends_hardened_stays_bounded: naive max > 4 s and > 250 tokens; hardened max < 3 s, < 150 tokens, only the 9-call question canned. |

## Trade-offs
| Option | Gains | Costs | Choose when |
|---|---|---|---|
| Short timeout + retries | Bounded latency; stalls become quick retries | Long but healthy answers get cut; work is wasted on the server | Short outputs (classification, tool choice); set per call type |
| Fallback to a smaller model | Users get an answer during outages | Lower quality answers, a second model to evaluate (lesson 12) | The fallback passes the golden set for the task |
| Canned answer early | Predictable cost and latency; honest UX | No answer for some users | Budgets are hard limits (cost caps, SLAs) |

## Build task
Start from the shipped circuit_breaker.py (unfixed: BreakerClient stores trip_after/cool_down but never opens). Add a circuit breaker: after 2 consecutive give-ups on an endpoint, skip it for the next 5 chats (no HTTP call, no budget), then probe it again.

Hints:
- Subclass Client and wrap _call().
- Keep a failure counter and a skip counter per model.
- Raise Unavailable while open, so the existing fallback logic just works.

Your file: `circuit_breaker.py` (shipped unfixed) · solution: `solution/circuit_breaker.py` · the same test checks either one:
```bash
BUILD_TARGET=mine python -m unittest -v test_build_task   # YOUR file
python -m unittest -v test_build_task                     # the solution (default, what CI runs)
```
PowerShell: `$env:BUILD_TARGET="mine"; python -m unittest -v test_build_task` (`Remove-Item Env:BUILD_TARGET` to switch back).

Observed 2026-10-28 – shipped file (fail-before) vs solution (pass-after):
```
BUILD_TARGET=mine  -> AssertionError: Tuples differ: (24, 24) != (24, 9)
                      FAILED (failures=1)
solution           -> Ran 1 test ... OK
```

## Equivalents
- urllib3 Retry (requests' HTTPAdapter): total, backoff_factor, backoff_jitter, status_forcelist, allowed_methods, respect_retry_after_header
- tenacity / backoff libraries: decorators for retry with exponential backoff and jitter
- LLM gateways and proxies offer fallbacks and budgets as configuration; the rules (what to retry, how much to spend) stay the same

## Optional steps (not run in the sandbox)
**real local model with a smaller fallback** – Two models on the same Ollama; stop Ollama mid-run or load a big model in parallel to see retries and fallbacks.
```
ollama pull qwen2.5:0.5b
LOCAL_MODEL=qwen2.5:1.5b FALLBACK_MODEL=qwen2.5:0.5b python resilient_agent.py
```
PowerShell:
```powershell
ollama pull qwen2.5:0.5b
$env:LOCAL_MODEL="qwen2.5:1.5b"; $env:FALLBACK_MODEL="qwen2.5:0.5b"; python resilient_agent.py
```
Expected: An answer plus call events; the first call after a model load may time out and retry

**inject latency without code: Toxiproxy (learning tool, manual)** – put a proxy with a 2000 ms latency toxic in front of the fake server and send only the primary through it (keep the Toxiproxy API on localhost; it is unauthenticated by default).
```
python ../fake_server_l300.py --port 8765 &
toxiproxy-server &
toxiproxy-cli create -l localhost:26014 -u localhost:8765 model
toxiproxy-cli toxic add -t latency -a latency=2000 model
LOCAL_MODEL_URL=http://127.0.0.1:26014/v1 FALLBACK_MODEL_URL=http://127.0.0.1:8765/v1 LOCAL_MODEL=fake-model FALLBACK_MODEL=fake-small python resilient_agent.py
```
PowerShell: run `toxiproxy-server-windows-amd64.exe` and `toxiproxy-cli-windows-amd64.exe` with the same arguments, then `$env:LOCAL_MODEL_URL="http://127.0.0.1:26014/v1"; $env:FALLBACK_MODEL_URL="http://127.0.0.1:8765/v1"; $env:LOCAL_MODEL="fake-model"; $env:FALLBACK_MODEL="fake-small"; python resilient_agent.py`.
Expected (pending a manual run): every primary call ends at the 0.5 s timeout (`"error": "timeout"`, ~503 ms as in the log above), is retried, then a `fallback` event answers from the direct port – bounded, unlike the naive loop's 6.1 s question.


## Troubleshooting
| Symptom | Action |
|---|---|
| Everything times out against a real model | Cold model load takes seconds: warm the model at start-up and use longer timeouts for long generations. |
| Retries make the outage worse | Cap retries, add jitter, count them in the budget, and add a circuit breaker (build task). |
| Cached answer is wrong after data changed | Key the cache on everything that affects the answer (prompt version, tool data) and give entries a lifetime. |

## Try it (validated, observed 2026-10-28)
Predict first, then run `python -m unittest -v test_try_it_14` (each test makes the change and prints what it observed).

| Change | Observed |
|---|---|
| No retries: compare.run('hardened', retries=0). | canned 1, fallbacks 13, HTTP calls 33 - no more canned answers, but 13 model steps went to the smaller model: retries buy primary-model quality. |
| No fallback endpoint: compare.run('hardened', fallback=False). | canned 3, fallbacks 3, HTTP calls 40 - two extra users get the canned reply when the primary gives up. |
