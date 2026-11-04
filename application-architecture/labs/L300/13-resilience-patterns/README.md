# Lab 13 – Resilience patterns: timeouts, circuit breaker, bulkhead, fallback

Borrowing a book in Library Loans calls two dependencies: **members** (required, no fallback) and the **catalogue** (title only, fallback `(title unavailable)`). Every outbound call goes through a worker pool with a 0.1 s timeout, and the catalogue also through a **circuit breaker**. The breaker logs every state change as a JSON line. In the failure lab, each request logs `ok`, `error`, `ms` and the pools' busy gauge. The base wiring shares ONE pool of 8 threads between both dependencies; you isolate them with a **bulkhead**.

## Files
| File | Purpose |
|---|---|
| `resilience.py` | `Pool` (timeout + busy gauge), `Bulkhead`, `CircuitBreaker`, `with_fallback` (lesson code) |
| `loans_service.py` | `LoanService.borrow` + `build_service()` (base: one shared pool) |
| `deps.py` | `Members` (1 ms) and `Catalogue` with modes `up` / `down` / `slow` (hangs 1 s) |
| `app.py` | Breaker demo: catalogue up → down → still down → back |
| `failure_lab.py` | Hung catalogue, 3 waves of 8 concurrent borrows: base vs solution |
| `test_resilience.py` | Breaker states (fake clock), timeout vs thread, bulkhead, fallback, symptom |
| `test_build_task.py` | Build task check |
| `solution/loans_service.py` | Build task solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L300/13-resilience-patterns
python app.py
python failure_lab.py
python -m unittest -v
```

## Expected output (observed 2026-10-28, Python 3.12.15, Linux)
```
$ python app.py
# catalogue up: 3 borrows, 0 with fallback title, catalogue called 3x, breaker closed
{"calls": 6, "evt": "breaker", "failure_rate": 0.5, "from": "closed", "name": "catalogue", "to": "open"}
# catalogue down: 8 borrows, 8 with fallback title, catalogue called 3x, breaker open
{"evt": "breaker", "from": "open", "name": "catalogue", "to": "half_open"}
{"evt": "breaker", "from": "half_open", "name": "catalogue", "to": "open", "trial": "failed"}
# still down, after open_s: 1 borrows, 1 with fallback title, catalogue called 1x, breaker open
{"evt": "breaker", "from": "open", "name": "catalogue", "to": "half_open"}
{"evt": "breaker", "from": "half_open", "name": "catalogue", "to": "closed", "trial": "ok"}
# catalogue back, after open_s: 3 borrows, 0 with fallback title, catalogue called 3x, breaker closed
# transitions: closed -> open -> half_open -> open -> half_open -> closed
```
While open, 8 borrows made only 3 catalogue calls: after 3 failures (6 calls in the window, 50 %), the breaker failed fast.

## failureLab: one slow dependency exhausts all threads
The catalogue hangs for 1 s. Wave 1's 8 catalogue calls time out after 0.1 s (fallback titles), but their threads stay busy. Wave 2 and 3's **members** checks queue behind them and time out, although the members service is healthy. The request log shows the cause: `"pools": {"shared": "8/8"}`.
```
$ python failure_lab.py
base     (one shared pool of 8): 8/24 borrows ok, 8 with fallback title
    per wave: {1: {'ok': 8}, 2: {'TimeoutError': 8}, 3: {'TimeoutError': 8}}
    first failed request log: {"degraded": false, "error": "TimeoutError: shared: no answer within 0.1 s", "evt": "request", "ms": 102.2, "ok": false, "pools": {"shared": "8/8"}, "wave": 2}
solution (members 4 + catalogue bulkhead 4): 24/24 borrows ok, 24 with fallback title
    per wave: {1: {'ok': 8}, 2: {'ok': 8}, 3: {'ok': 8}}
```

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_every_borrow_succeeds_with_a_fallback_title (test_build_task.BulkheadTest...) ... ok
test_members_has_its_own_pool (test_build_task.BulkheadTest...) ... ok
test_no_request_waits_much_longer_than_the_timeout (test_build_task.BulkheadTest...) ... ok
test_half_open_trial_closes_or_reopens (test_resilience.CircuitBreakerTest...) ... ok
test_opens_at_the_failure_rate_after_min_calls (test_resilience.CircuitBreakerTest...) ... ok
test_successes_keep_it_closed (test_resilience.CircuitBreakerTest...) ... ok
test_bulkhead_rejects_the_call_over_its_limit (test_resilience.PoolAndBulkheadTest...) ... ok
test_fallback_only_for_expected_errors (test_resilience.PoolAndBulkheadTest...) ... ok
test_timeout_frees_the_caller_not_the_thread (test_resilience.PoolAndBulkheadTest...) ... ok
test_healthy_dependencies (test_resilience.ServiceTest...) ... ok
test_symptom_slow_catalogue_starves_the_shared_pool (test_resilience.ServiceTest...) ... ok
----------------------------------------------------------------------
Ran 11 tests in 2.155s

OK
```

## Build task (the hardening change)
Change `build_service()` in `loans_service.py`: members gets its own `Pool("members", 4)`, the catalogue a `Bulkhead("catalogue", 4)`. Call 5 to the catalogue is rejected at once (`BulkheadFull` → fallback title) instead of queueing.

- Solution: `solution/loans_service.py`.
- Check (solution by default; YOUR file with `CHECK_MINE=1`):
```
CHECK_MINE=1 python -m unittest -v test_build_task          # Mac mini (zsh)
$env:CHECK_MINE = "1"; python -m unittest -v test_build_task   # Windows (PowerShell)
Remove-Item Env:\CHECK_MINE                                     # Windows: switch back
```
Fail before / pass after (observed 2026-10-28):
```
$ CHECK_MINE=1 python -m unittest test_build_task      # unchanged loans_service.py
FAIL: test_every_borrow_succeeds_with_a_fallback_title
FAIL: test_members_has_its_own_pool
FAILED (failures=2)
$ python -m unittest test_build_task                   # solution
OK
```

## Try it (observed 2026-10-28, Python 3.12.15)
```
$ python try_it.py
[1] timeout 2.0 s: 24/24 ok, 8 degraded, fastest 1004 ms, slowest 2349 ms
[2] breaker went closed -> open; still {1: {'ok': 8}, 2: {'TimeoutError': 8}, 3: {'TimeoutError': 8}}
```
Other runs: fastest 1003–1008 ms, slowest 2298–2408 ms. A timeout longer than the hang removes the errors and replaces them with 1–2.4 s borrows: some catalogue calls queue behind the stuck ones and still exceed 2 s (8 degraded).

## Mac mini and Windows
The same commands work in zsh and PowerShell inside the venv. Everything is in-process (threads), so there are no ports. The timing margins are 0.1 s (timeout), 0.25 s (wave gap) and 1 s (hang). Windows' default timer resolution is coarser, so the per-request `ms` values will differ; the per-wave counts are expected to hold (pending CI).

## Troubleshooting
| Symptom | Action |
|---|---|
| Timeouts on a healthy dependency | Look at the `pools` gauge in the request log: `8/8` means starvation. Give each dependency its own bulkhead. |
| Breaker opens/closes constantly | Raise `min_calls` or the window; set `open_s` to about the dependency's recovery time. |
| `ZeroDivisionError` escapes `with_fallback` | Intended: only dependency errors get a fallback; bugs must surface. |
