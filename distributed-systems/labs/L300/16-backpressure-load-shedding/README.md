# 16 · Backpressure and load shedding

A server with **4 workers** (10 ms per request on average, exponential, seeded) and a **queue** in front: capacity = 4 / 10 ms = **400 requests/s**. Clients follow an **open model** (Poisson arrivals, seeded): they keep sending at their rate however slow the server gets — like real users and like k6's constant-arrival-rate executor. A discrete-event engine (`helpers.simulate`) runs it on simulated milliseconds, so every run prints the same numbers.

Part 1 measures **queueing delay vs throughput**: as load approaches capacity, throughput grows linearly but waiting grows much faster. Part 2 is the fault: a 10-second **burst at 150 %** of capacity, reported as **per-second metrics (JSON lines)** — the lines a dashboard would chart. The lesson server's queue is unbounded: everything is accepted, so the line only grows.

Files: `backpressure.py` (lesson: `Server.admit`, metrics, the two experiments) · `helpers.py` (plumbing: the discrete-event engine) · `aimd.py` (an AIMD concurrency limit for callers, used in tryIt 2) · `try_it.py` · `test_backpressure.py` · build task: `solution_backpressure.py` + `test_build_task.py` · tool target: `serve_realtime.py` (+ `http_helpers.py`), `load_test.js` (k6), `test_serve_realtime.py`.

## Run (Mac mini: `python3` inside the venv is `python`; Windows: same commands in PowerShell)
```bash
python backpressure.py
```

## Expected output (real run, Python 3.12.15, Linux — identical on every run; simulated, seeded)
```
capacity 400 requests/s (4 workers x 10 ms)
1) load sweep, 20 s each:  load  throughput/s  mean wait  p99
                         50%        193       0.8 ms   46.1 ms
                         80%        312       5.9 ms   59.3 ms
                         90%        352      14.1 ms   78.1 ms
                         95%        371      30.4 ms  204.6 ms
2) burst: 5 s at 60%, 10 s at 150%, 15 s at 60% - per-second metrics (JSON lines):
{"t": 3, "offered": 221, "ok": 221, "shed": 0, "p99_ms": 43}
{"t": 6, "offered": 589, "ok": 589, "shed": 0, "p99_ms": 812}
{"t": 9, "offered": 552, "ok": 552, "shed": 0, "p99_ms": 2317}
{"t": 12, "offered": 603, "ok": 603, "shed": 0, "p99_ms": 3733}
{"t": 15, "offered": 256, "ok": 256, "shed": 0, "p99_ms": 4689}
{"t": 18, "offered": 247, "ok": 247, "shed": 0, "p99_ms": 3507}
{"t": 21, "offered": 250, "ok": 250, "shed": 0, "p99_ms": 2307}
{"t": 24, "offered": 224, "ok": 224, "shed": 0, "p99_ms": 1279}
{"t": 27, "offered": 229, "ok": 229, "shed": 0, "p99_ms": 46}
summary: {"offered": 10686, "ok": 10686, "shed": 0, "throughput_per_s": 356, "mean_wait_ms": 1928.5, "p50_ms": 1840.8, "p99_ms": 4619.1, "goodput": 3781}
```
(per-second lines for every third second.) Read the metrics: during the burst 600 requests/s arrive and only 400 can be served, so ~200 per second join the queue; p99 climbs past 3.7 s and keeps climbing **after** the burst ends (t=15: 4.7 s) because the backlog drains at only 400 − 240 = 160 requests/s. Every request was eventually "served", but only **3,781 of 10,686** within the clients' 1 s timeout (`goodput`) — the rest was work for callers who had already given up.

## Test
```bash
python -m unittest -v     # Ran 11 tests ... OK  (6 lesson + 4 build-task tests against the solution + 1 real-clock target test, ~5 s)
```

## Build task: bounded queue + shedding with 503 and Retry-After
In `Server.admit`, refuse a request when the queue already holds `MAX_QUEUE = 40` (40 / 400 per s = at most ~100 ms of waiting): return a Retry-After in whole seconds, at least 1 (`max(1, ceil(queue_length / CAPACITY))`), which the engine turns into a 503.
```bash
BUILD_TARGET=mine python -m unittest test_build_task -v                     # macOS (zsh)
$env:BUILD_TARGET="mine"; python -m unittest test_build_task -v             # Windows (PowerShell)
```
Before your change (real run): `Ran 4 tests ... FAILED (failures=3)` (`AssertionError: 4619.1 not less than 250`; `3781 != 10686`). The reference `solution_backpressure.py` prints for the burst:
```
2) burst: 5 s at 60%, 10 s at 150%, 15 s at 60% - per-second metrics (JSON lines):
{"t": 3, "offered": 221, "ok": 221, "shed": 0, "p99_ms": 43}
{"t": 6, "offered": 589, "ok": 418, "shed": 171, "p99_ms": 138}
{"t": 9, "offered": 552, "ok": 377, "shed": 175, "p99_ms": 159}
{"t": 12, "offered": 603, "ok": 400, "shed": 203, "p99_ms": 167}
{"t": 15, "offered": 256, "ok": 256, "shed": 0, "p99_ms": 88}
{"t": 18, "offered": 247, "ok": 247, "shed": 0, "p99_ms": 54}
{"t": 21, "offered": 250, "ok": 250, "shed": 0, "p99_ms": 46}
{"t": 24, "offered": 224, "ok": 224, "shed": 0, "p99_ms": 46}
{"t": 27, "offered": 229, "ok": 229, "shed": 0, "p99_ms": 60}
summary: {"offered": 10686, "ok": 8779, "shed": 1907, "throughput_per_s": 293, "mean_wait_ms": 44.2, "p50_ms": 27.1, "p99_ms": 154.5, "goodput": 8779}
```
p99 stays near 160 ms through the burst and is back to normal the second the burst ends; 1,907 requests got a fast 503 + `Retry-After: 1` instead of a 4-second wait, and goodput rises from 3,781 to 8,779.

## Try it (real run — `python try_it.py`)
```
tryIt 1: max_queue  10: p99   65.1 ms, shed 1939, ok 8747, goodput 8747
tryIt 1: max_queue  40: p99  154.5 ms, shed 1907, ok 8779, goodput 8779
tryIt 1: max_queue 400: p99 1115.2 ms, shed 1547, ok 9139, goodput 6710
tryIt 2: no client limit: 503s the server had to send 1907, rejected locally 0, ok 8779, p99 154.5 ms
tryIt 2: AIMD client limit: 503s the server had to send 23, rejected locally 1885, ok 8778, p99 151.6 ms, final limit 95.5
```
tryIt 1: the bound is the latency budget — 10 keeps p99 at 65 ms, 400 lets it reach 1.1 s and throws away 2,400 late answers. tryIt 2: callers with an AIMD concurrency limit (+1/limit per success, ×0.9 per 503) stop sending what would be shed: the server sends 23 503s instead of 1,907; the rejected work fails locally, without network or server cost.

## Real clock + k6 (k6 itself pending a manual run)
`serve_realtime.py` runs the same admission control on real threads: 4 workers × 50 ms = 80 requests/s, queue bound 8. `--check` sends the same open-model load as `load_test.js` (120 requests/s for 10 s) from Python. Real runs here:
```
$ python serve_realtime.py --check
1200 requests at 120/s for 10 s (capacity 80/s, queue bound 8): {'200': 780, '503': 420, 'p99_ms': 193, '503_without_retry_after': 0}
$ python serve_realtime.py --check --unbounded
1200 requests at 120/s for 10 s (capacity 80/s, unbounded queue): {'200': 1200, '503': 0, 'p99_ms': 3787, '503_without_retry_after': 0}
```
Then, with k6 installed (`brew install k6` / `winget install k6 --source winget`): `python serve_realtime.py` in one terminal, `k6 run load_test.js` in another — expect `http_req_failed` ≈ 35% (k6 counts 503 as failed) and both checks at 100%.

## Platform notes
The simulation is pure computation (same numbers everywhere). The real-clock target uses threads and `time.sleep(0.05)`; on Windows sleep granularity can stretch service time slightly, which lowers capacity a little — expect a few more 503s.
