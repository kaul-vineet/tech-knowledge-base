# Lab 16 – Performance and architecture fitness functions in CI

`fitness.py` turns four architecture qualities into CI gates. Each gate prints one JSON line, and the exit code fails the build:
**import boundaries** (`ast`: `domain.py` imports no adapters), **query count** (`sqlite3` trace callback: statements per overdue report on 10 and on 500 loans), a **micro-benchmark** (`timeit.repeat`, keep `min()`), and a **response-time budget** (stdlib load test against the HTTP adapter: p95 ≤ 200 ms, 0 errors). `k6/overdue.js` expresses the same budget as Grafana k6 thresholds. A "readability" refactor turned the overdue report into N+1 queries; the gates catch it, and you fix it.

## Files
| File | Purpose |
|---|---|
| `fitness.py` | The four gates + `QueryCounter` (lesson code) |
| `loans_repo.py` | Seeded SQLite library + `overdue_report()` after the refactor (N+1) |
| `domain.py` | Pure rules: days overdue, fine (capped at 10.00) |
| `http_api.py` | `GET /reports/overdue` (127.0.0.1; `request_queue_size = 64`) |
| `load_test.py` | Closed-model load test: threads, warm-up, p50/p95/max, errors |
| `k6/overdue.js` | Same load test for k6, thresholds `p(95)<200`, `rate<0.01` (pending-ci) |
| `failure_lab.py` | N+1 vs JOIN: rows, gates, statement trace, simulated network round trips |
| `test_fitness.py` | Domain, gates, symptom, exit code |
| `test_build_task.py` / `solution/loans_repo.py` | Build task check / solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L300/16-performance-fitness-ci
python fitness.py               # exit 1 until you fix loans_repo.py
python failure_lab.py
python fitness.py --solution    # exit 0
python -m unittest -v
```

## Expected output (observed 2026-10-28, Python 3.12.15, Linux)
Query counts repeat exactly. Timings vary with host load (9 runs here: micro-benchmark N+1 1.2–21 ms, JOIN 0.4–3.8 ms; p95 N+1 82–105 ms, JOIN 4.8–90 ms).
```
$ python fitness.py; echo "exit $?"
{"budget": "domain.py imports no adapters", "gate": "import-boundaries", "ok": true, "value": []}
{"budget": 2, "gate": "query-count", "ok": false, "value": {"10": 11, "500": 337}}
{"budget": 50, "gate": "micro-benchmark", "ok": true, "value": 2.4}
{"budget": 200, "gate": "response-time-p95", "ok": true, "value": {"errors": 0, "max_ms": 88.8, "p50_ms": 34.6, "p95_ms": 83.8, "requests": 40}}
fitness: FAILED query-count
exit 1
$ python fitness.py --solution; echo "exit $?"
{"budget": "domain.py imports no adapters", "gate": "import-boundaries", "ok": true, "value": []}
{"budget": 2, "gate": "query-count", "ok": true, "value": {"10": 1, "500": 1}}
{"budget": 50, "gate": "micro-benchmark", "ok": true, "value": 0.52}
{"budget": 200, "gate": "response-time-p95", "ok": true, "value": {"errors": 0, "max_ms": 4.9, "p50_ms": 4.5, "p95_ms": 4.8, "requests": 40}}
fitness: all gates passed
exit 0
```
Both versions pass the timing gates; only the query count separates them reliably.

## failureLab: an N+1 query added in a refactor
```
$ python failure_lab.py
same report rows (unit-test view): True, 168 overdue loans
base     (after refactor): query-count {10: 11, 500: 337} -> FAIL; p95 99.6 ms -> PASS; with 0.5 ms round trips: 342.9 ms per report
    trace (10 loans), first 3: ['SELECT id, member_id, book_id, due FROM loans WHERE returned = 0 ORDER BY id', 'SELECT name FROM members WHERE id = 15', 'SELECT title FROM books WHERE id = 229']
solution (one JOIN)     : query-count {10: 1, 500: 1} -> PASS; p95 65.4 ms -> PASS; with 0.5 ms round trips: 2.7 ms per report
    trace (10 loans), first 3: ["SELECT l.id, m.name, b.title, l.due FROM loans l JOIN members m ON m.id = l.member_id JOIN books b ON b.id = l.book_id WHERE l.returned = 0 AND l.due < '2026-10-28' ORDER BY l.id"]
```
Unit tests and the p95 budget cannot see the N+1 on small, in-process data. The statement count can: 1 + 2 × 168 = 337. To simulate a database on the network, the trace callback sleeps 0.5 ms per statement. `time.sleep` overshoots (here about 1 ms per call; more on Windows), so the N+1 report takes about 343 ms instead of the ideal 168 ms.

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_all_fitness_gates_pass (test_build_task.QueryBudgetTest...) ... ok
test_query_count_does_not_grow_with_the_data (test_build_task.QueryBudgetTest...) ... ok
test_same_rows_as_before_the_fix (test_build_task.QueryBudgetTest...) ... ok
test_days_and_fine (test_fitness.DomainTest...) ... ok
test_import_gate_passes_and_catches_a_planted_import (test_fitness.GateTest...) ... ok
test_main_exit_code_is_the_ci_contract (test_fitness.GateTest...) ... ok
test_query_counter_sees_every_statement (test_fitness.GateTest...) ... ok
test_response_time_gate_has_no_errors (test_fitness.GateTest...) ... ok
test_symptom_query_count_grows_with_the_data (test_fitness.GateTest...) ... ok
test_report_rows (test_fitness.ReportTest...) ... ok
----------------------------------------------------------------------
Ran 10 tests in 3.713s

OK
```

## Build task (the hardening change)
Rewrite `overdue_report()` as one JOIN that also filters overdue loans in SQL (`l.due < today.isoformat()`; ISO dates sort as text). Keep `ORDER BY l.id` so the rows stay identical.

- Solution: `solution/loans_repo.py`.
- Check (solution by default; YOUR file with `CHECK_MINE=1`):
```
CHECK_MINE=1 python -m unittest -v test_build_task          # Mac mini (zsh)
$env:CHECK_MINE = "1"; python -m unittest -v test_build_task   # Windows (PowerShell)
Remove-Item Env:\CHECK_MINE                                     # Windows: switch back
```
Fail before / pass after (observed 2026-10-28):
```
$ CHECK_MINE=1 python -m unittest test_build_task      # unchanged loans_repo.py
FAIL: test_all_fitness_gates_pass
FAIL: test_query_count_does_not_grow_with_the_data
FAILED (failures=2)
$ python -m unittest test_build_task                   # solution
OK
```

## Load test by hand, and with k6 (pending-ci)
```
python http_api.py 8016 &                                          # Mac mini (zsh); `kill %1` to stop
python load_test.py http://127.0.0.1:8016/reports/overdue
brew install k6 && k6 run k6/overdue.js

$api = Start-Process python -ArgumentList 'http_api.py','8016' -PassThru   # Windows (PowerShell)
python load_test.py http://127.0.0.1:8016/reports/overdue
winget install k6 --source winget; k6 run k6\overdue.js
Stop-Process -Id $api.Id
```
k6 was not run here (not installed). k6 exits non-zero when a threshold fails, which makes it a CI gate.

## Try it (observed 2026-10-28, Python 3.12.15)
```
$ python try_it.py
[1] in-process SQLite, 500 loans, best of 5 x 5 (ms per report): {'N+1': 6.64, 'JOIN': 1.05}
[2] domain.py imports sqlite3 -> {'gate': 'import-boundaries', 'ok': False, 'value': ['domain.py imports sqlite3'], 'budget': 'domain.py imports no adapters'}
```
Other runs of [1]: N+1 9.87 / 21.46 ms, JOIN 3.79 / 0.46 ms (busy shared host). The N+1 is always slower, yet always under the 50 ms budget.

## Mac mini and Windows
Commands are the same inside the venv, except running the API in the background (above). The server binds 127.0.0.1. Query counts are identical on every OS. Timing gates have generous budgets because CI runners and Windows' timer resolution add noise.

## Troubleshooting
| Symptom | Action |
|---|---|
| Timing gate fails only on CI | Compare `min()` of repeats; keep budgets generous; rely on counts for hard limits. |
| Load test shows about 1 s outliers | A full listen backlog makes clients retry the connection after 1 s; `http_api.py` sets `request_queue_size = 64`, and `load_test.py` warms up first. |
| `OSError: [Errno 48]` / `[WinError 10048]` | Port 8016 is busy: use another port and `k6 run -e BASE_URL=http://127.0.0.1:PORT k6/overdue.js`. |
