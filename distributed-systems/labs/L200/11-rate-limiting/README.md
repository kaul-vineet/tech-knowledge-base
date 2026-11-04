# 11 · Rate limiting: token bucket, per-client limits, 429 + Retry-After

`ratelimit.py` runs an HTTP API that gives **each client** (key: the `X-Client-Id` header) its own **token bucket**: 2 tokens/s, bucket size (burst) 5. A request takes a token; with none left the server answers **429 Too Many Requests** with **`Retry-After: <seconds>`** — the time until the next token, rounded up to whole seconds (`delay-seconds` must be an integer). Three clients run on a simulated clock: `alice` honors Retry-After, `bob` retries every 0.1 s, `carol` sends only 3 requests. Identical output on every run.

Files: `ratelimit.py` (the lesson code: bucket, API, Retry-After parsing, client event loop) · `helpers.py` (plumbing: JSON handler, `call()`, `serve()`, `SimClock`) · `try_it.py` · `test_ratelimit.py` · build task: `solution_ratelimit.py` + `test_build_task.py`.

## Run (Mac mini and Windows: same command inside the venv)
```bash
python ratelimit.py
```

## Expected output (real run, Python 3.12.15, Linux — identical on every run)
```
alice trace: 200 200 200 200 200 429(wait 1) 200 200 429(wait 1) 200 200 429(wait 1) 200 200 429(wait 1) 200
alice (honors Retry-After): 12 ok, 4 x 429, done at t=4s
bob   (retries every 0.1 s): 12 ok, 35 x 429, done at t=3.5s
carol (honors Retry-After): 3 ok, 0 x 429, done at t=0s
```
Read it: the burst of 5 passes at t=0; the 6th request finds 0 tokens, the next token is 0.5 s away, so `Retry-After: 1`. After 1 s alice has 2 tokens again (2 per second). Bob finishes 0.5 s earlier only because he polls every 0.1 s — at the cost of 35 rejected requests the server still had to handle. Carol shares the server with both and never sees a 429: limits are per client.

## Test
```bash
python -m unittest -v     # Ran 8 tests ... OK (4 lesson tests + 3 build-task tests against the solution + 1 real-clock k6-target test)
```

## Build task: a sliding-window-log limiter
Add `SlidingWindowLog(limit, window, clock)` to `ratelimit.py` with the same `allow() -> (ok, wait)` interface: keep the timestamps of accepted requests, drop those older than `window`, accept while fewer than `limit` remain, otherwise `wait` = when the oldest one leaves the window. Plug it in with `run(..., make_limiter=lambda clock: SlidingWindowLog(5, 2.5, clock))`.
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v                     # macOS (zsh)
$env:BUILD_TARGET="mine"; python -m unittest test_build_task -v             # Windows (PowerShell)
```
Before your change: `Ran 3 tests ... FAILED (errors=3)`. Reference: `solution_ratelimit.py`:
```
alice trace: 200 200 200 200 200 429(wait 3) 200 200 200 200 200 429(wait 3) 200 200
alice (honors Retry-After): 12 ok, 2 x 429, done at t=6s
bob   (retries every 0.1 s): 12 ok, 50 x 429, done at t=5s
carol (honors Retry-After): 3 ok, 0 x 429, done at t=0s
```
Tip: compare `oldest + window <= now`, not `oldest <= now - window` — with floats, `1.9 - 1.0` is `0.8999999999999999` (the first reference version failed its own boundary test this way).

## Try it (real run — `python try_it.py`)
```
tryIt 1: 10 requests within 10 ms across a second boundary -> fixed window allows 10, token bucket allows 5
tryIt 2: BURST 5 -> alice 12 ok, 4 x 429, done at t=4s
tryIt 2: BURST 1 -> alice 12 ok, 11 x 429, done at t=11s
```
tryIt 2 shows a real side effect of whole-second `Retry-After`: with no burst, every wait of 0.5 s is rounded up to 1 s, so a polite client gets 1 request/s instead of the 2/s the limit allows.

## Load it with k6 (optional learning tool — see `documentation/LEARNING-TOOLS.md`)
The demo runs on a simulated clock, so an external load tool needs a real-clock copy of the same server:
```bash
python serve_realtime.py          # http://127.0.0.1:8011/data, same Api, RATE 2/s, BURST 5 per X-Client-Id
k6 run load_test.js               # 2nd terminal: constant-arrival-rate 10 req/s for 10 s, one client id
python serve_realtime.py --check  # the same load from Python (no k6 needed)
```
`--check` output (real run, Python 3.12.15, Linux; ran twice, same result):
```
100 requests at 10/s for 10 s (limit 2/s, burst 5): 200=24 429=76 -> 429 share 76%; 429 without Retry-After: 0
```
k6 should agree: `http_req_failed` ≈ 76% (k6 counts 429 as failed) and both checks 100%. The k6 run itself is pending (k6 not installed here). `python -m unittest test_serve_realtime -v` checks the real-clock target (2 s, loose bounds).

## Platform notes
Same on the Mac mini and the Windows PC (`127.0.0.1`, OS-chosen port, simulated time). In production the limit key must be an authenticated identity — anyone can send `X-Client-Id: carol`.
