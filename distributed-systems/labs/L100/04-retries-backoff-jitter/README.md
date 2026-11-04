# 04 · Retries with exponential backoff, full jitter and a retry budget

B returns 503 about 30% of the time (seeded). A retries only retryable errors (429/502/503/504, connection errors, timeouts), at most 4 attempts, sleeping `uniform(0, min(cap, base·2^attempt))` (full jitter) between tries. A token-bucket retry budget pauses retries when B looks sick (phase 2: 90% 503s).

Files: `retries.py` (the lesson code: backoff, budget, retry loop, demo), `helpers.py` (plumbing + the simulated `FlakyB` service), `try_it.py` (tryIt experiments), `test_retries.py`; optional `agent_assist.py` + `test_agent_assist.py` (local-agent log summary, checked by code).

## Run
```bash
python retries.py
```

## Expected output (real run, Python 3.12.15, Linux — identical on every run; seeded)
```
full-jitter ceilings (s): [0.02, 0.04, 0.08, 0.16, 0.32, 0.5]
GET /missing -> ('gave up (404)', 1) (404: not retried)
--- B flaky (30% 503) ---
req 01: 200                          attempts=1 sleeps=[] tokens=10.0
req 02: 200                          attempts=4 sleeps=[0.006, 0.006, 0.052] tokens=7.5
req 03: 200                          attempts=1 sleeps=[] tokens=8.0
req 04: 200                          attempts=1 sleeps=[] tokens=8.5
req 05: 200                          attempts=2 sleeps=[0.001] tokens=8.0
req 06: 200                          attempts=3 sleeps=[0.011, 0.015] tokens=6.5
req 07: gave up (retry budget empty) attempts=2 sleeps=[0.001] tokens=4.5
req 08: 200                          attempts=1 sleeps=[] tokens=5.0
req 09: 200                          attempts=1 sleeps=[] tokens=5.5
req 10: gave up (retry budget empty) attempts=1 sleeps=[] tokens=4.5
8/10 succeeded, 17 attempts (load x1.7, worst case x4.0)
--- B sick (90% 503) ---
req 01: gave up (retry budget empty) attempts=1 sleeps=[] tokens=3.5
req 02: gave up (retry budget empty) attempts=1 sleeps=[] tokens=2.5
req 03: gave up (retry budget empty) attempts=1 sleeps=[] tokens=1.5
req 04: gave up (retry budget empty) attempts=1 sleeps=[] tokens=0.5
req 05: gave up (retry budget empty) attempts=1 sleeps=[] tokens=0.0
req 06: gave up (retry budget empty) attempts=1 sleeps=[] tokens=0.0
req 07: gave up (retry budget empty) attempts=1 sleeps=[] tokens=0.0
req 08: 200                          attempts=1 sleeps=[] tokens=0.5
req 09: gave up (retry budget empty) attempts=1 sleeps=[] tokens=0.0
req 10: gave up (retry budget empty) attempts=1 sleeps=[] tokens=0.0
1/10 succeeded, 10 attempts (load x1.0, worst case x4.0)
```

## Test
```bash
python -m unittest -v          # Ran 8 tests ... OK (4 retry tests + 4 agent-assist tests, fake model server)
```

## Note
The budget uses `ratio=0.5` (each success refunds half a token) so a 30%-flaky B can still be retried; gRPC's documented example uses `maxTokens: 10, tokenRatio: 0.1`, which is stricter. Tune the ratio to the failure rate you are willing to mask.

## Try it (real run, Python 3.12.15, Linux — seeded, identical on every run)
```bash
python try_it.py
```
```
tryIt 1: max_attempts=1: 5/10 succeeded, 10 attempts
tryIt 1: max_attempts=4: 8/10 succeeded, 17 attempts
tryIt 2: no jitter  : busiest 10 ms slot has 100 of 100 retries
tryIt 2: full jitter: busiest 10 ms slot has 17 of 100 retries
```

## Agent assist (optional): a local model summarizes a retry log — code checks every number
`agent_assist.py` builds a seeded retry/latency log (80 requests, 126 attempt lines), asks a model for `attempts`, `errors`, `p50_ms`, `p99_ms` and a one-line summary, then computes the true values itself (nearest-rank percentiles) and flags every number the agent got wrong. Code decides; the agent only proposes prose.
```bash
python agent_assist.py --fake     # deterministic fake model server from labs/_shared/local_agent (used by the tests)
python agent_assist.py            # a real local model: Ollama on the Mac mini or Windows PC
```
Real run with `--fake` (Python 3.12.15, Linux — identical on every run):
```
log: 126 attempts from 80 requests (seeded, seed 7)
field        agent     code  verdict
attempts       126      126  ok
errors          46       46  ok
p50_ms        32.7     24.1  WRONG
p99_ms       210.6    141.0  WRONG
agent prose (unverified): most requests succeed; about 37% of attempts fail with 503 and are retried, and a few slow calls stretch the latency tail.
flagged: p50_ms, p99_ms -> report the code's numbers, not the agent's
```
The fake model makes two classic mistakes on purpose (p50 = mean, p99 = max). With a real model (`ollama pull qwen2.5:1.5b`, then `LOCAL_MODEL=qwen2.5:1.5b python agent_assist.py`; other host: set `LOCAL_MODEL_URL`), any field may be wrong — the checker output is what you trust. Not run against a real model here. Never paste logs containing tokens, keys or customer data into a prompt; redact first.
