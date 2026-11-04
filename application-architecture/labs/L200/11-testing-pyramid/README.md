# Lab 11 – Testing pyramid: unit, integration, end-to-end, measured

The Library Loans service from lesson 7, tested at three layers: many unit tests of the domain with a fake store, a few integration tests of the SQLite adapter against a real file, and one end-to-end HTTP journey. `pyramid.py` runs each layer, measures it and checks the shape. A PostgreSQL integration test with Testcontainers runs in CI only.

## Files
| File | Purpose |
|---|---|
| `pyramid.py` | Runs the layers by file-name pattern, times each test, checks the shape (lesson code) |
| `loans.py` | Domain (same rules as lesson 7) |
| `sqlite_store.py` | SQLite adapter |
| `http_api.py` | HTTP adapter + small client |
| `test_unit_loans.py` | Unit layer: 8 tests, in-memory fake |
| `test_integration_sqlite.py` | Integration layer: store contract against a SQLite file |
| `test_integration_postgres.py` | Same contract against PostgreSQL via Testcontainers (skipped unless `LOANS_TESTCONTAINERS=1`) |
| `postgres_store.py` | PostgreSQL adapter (psycopg 3), used only by the test above |
| `requirements-ci.txt` | testcontainers[postgres]==4.15.0, psycopg[binary]==3.3.6 (CI only) |
| `test_e2e_http.py` | End-to-end layer: one HTTP journey |
| `test_build_task.py` | Build task check (speed budgets) |
| `solution/pyramid.py` | Build task solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L200/11-testing-pyramid
python pyramid.py
python -m unittest -v
```
## Expected output (observed 2026-10-28, Python 3.12.15, Linux)

Times vary from run to run and machine to machine (this host stores files on a shared network mount, which slows every SQLite write). Repeated runs here gave unit means of 0.03-3.8 ms, integration 82-201 ms and e2e 0.6-4.9 s; the order of the layers never changed.

```
$ python pyramid.py
layer        tests  skipped  failed  total ms  mean ms
unit             8        0       0       0.4     0.03
integration      4        3       0     350.6    87.60
e2e              1        0       0     610.7   610.62
one e2e test costs about as much as 17,876 unit tests (about 10^4)
pyramid OK
```

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_custom_budgets (test_build_task.BudgetTest.test_custom_budgets) ... ok
test_real_suite_meets_the_default_budget (test_build_task.BudgetTest.test_real_suite_meets_the_default_budget) ... ok
test_slow_unit_layer_is_reported (test_build_task.BudgetTest.test_slow_unit_layer_is_reported) ... ok
test_within_budget (test_build_task.BudgetTest.test_within_budget) ... ok
test_borrow_conflict_return_and_lookup (test_e2e_http.LoanJourneyE2ETest.test_borrow_conflict_return_and_lookup) ... ok
test_active_excludes_returned_in_id_order (test_integration_postgres.PostgresStoreIntegrationTest.test_active_excludes_returned_in_id_order) ... skipped 'set LOANS_TESTCONTAINERS=1 (needs requirements-ci.txt and Docker/Podman)'
test_get_round_trips_types (test_integration_postgres.PostgresStoreIntegrationTest.test_get_round_trips_types) ... skipped 'set LOANS_TESTCONTAINERS=1 (needs requirements-ci.txt and Docker/Podman)'
test_ids_start_at_one (test_integration_postgres.PostgresStoreIntegrationTest.test_ids_start_at_one) ... skipped 'set LOANS_TESTCONTAINERS=1 (needs requirements-ci.txt and Docker/Podman)'
test_active_excludes_returned_in_id_order (test_integration_sqlite.SqliteStoreIntegrationTest.test_active_excludes_returned_in_id_order) ... ok
test_data_survives_a_restart (test_integration_sqlite.SqliteStoreIntegrationTest.test_data_survives_a_restart) ... ok
test_get_round_trips_types (test_integration_sqlite.SqliteStoreIntegrationTest.test_get_round_trips_types) ... ok
test_ids_start_at_one (test_integration_sqlite.SqliteStoreIntegrationTest.test_ids_start_at_one) ... ok
test_book_cannot_be_on_loan_twice (test_unit_loans.LoanServiceUnitTest.test_book_cannot_be_on_loan_twice) ... ok
test_borrow_returns_an_active_loan (test_unit_loans.LoanServiceUnitTest.test_borrow_returns_an_active_loan) ... ok
test_limit_is_per_member (test_unit_loans.LoanServiceUnitTest.test_limit_is_per_member) ... ok
test_member_limit (test_unit_loans.LoanServiceUnitTest.test_member_limit) ... ok
test_missing_fields (test_unit_loans.LoanServiceUnitTest.test_missing_fields) ... ok
test_return_frees_a_slot (test_unit_loans.LoanServiceUnitTest.test_return_frees_a_slot) ... ok
test_return_frees_the_book (test_unit_loans.LoanServiceUnitTest.test_return_frees_the_book) ... ok
test_unknown_loan (test_unit_loans.LoanServiceUnitTest.test_unknown_loan) ... ok

----------------------------------------------------------------------
Ran 20 tests in 2.274s

OK (skipped=3)
```

## Build task
Add speed budgets to `pyramid.py`: `python pyramid.py --budget` also fails when a layer's mean test time is over `BUDGET_MS = {"unit": 10, "integration": 1000, "e2e": 10000}`. Put the check in `budget_problems(rows, budgets)`.

- Solution: `solution/pyramid.py` (read it only after trying).
- Check: `python -m unittest -v test_build_task` tests the solution by default. To test YOUR `pyramid.py`:
```
CHECK_MINE=1 python -m unittest -v test_build_task          # Mac mini (zsh)
$env:CHECK_MINE = "1"; python -m unittest -v test_build_task   # Windows (PowerShell)
Remove-Item Env:\CHECK_MINE                                     # Windows: switch back
```
```
$ python -m unittest test_build_task   # against the solution, observed 2026-10-28
OK
```

## Try it (observed 2026-10-28, Python 3.12.15)
Predict first (the tasks and predictions are in the lesson's `tryIt` field), then run. `try_it.py` never edits the lab files.
```
$ python try_it.py
[1] mean ms: unit 0.03, integration 82.83, e2e 613.02 -> one e2e test = 20,248 unit tests (10^4)
[2] sqlite_store.py: bool(row[3]) -> row[3]      failed tests -> unit 0, integration 1, e2e 0
[2] http_api.py: BookAlreadyOnLoan 409 -> 422    failed tests -> unit 0, integration 0, e2e 1
```

## Testcontainers, the real-database equivalent (pending-ci)
Not run in the sandbox (no pip access, no container engine). CI on `ubuntu-latest` runs:
```bash
pip install -r requirements-ci.txt
LOANS_TESTCONTAINERS=1 python -m unittest -v test_integration_postgres
```
On the Mac mini or Windows PC: start a Podman machine (lesson 1) and point Testcontainers at it (`DOCKER_HOST`, see the Testcontainers docs), or use Docker Desktop; then the same two commands (PowerShell: `$env:LOANS_TESTCONTAINERS = "1"`).

## Mac mini and Windows
Inside an activated venv the commands are identical on both machines (`python3`/`py -3.12` also work outside a venv). Use `\` in paths on Windows. Tests bind 127.0.0.1 on port 0 and create scratch folders inside the lab folder, never in a system temp path.

## Troubleshooting
| Symptom | Action |
|---|---|
| `not a pyramid: unit 8, integration 4, e2e 3` | Too many end-to-end tests: move rule checks down to unit tests, keep one journey per feature. |
| Means much higher than in this README | Normal on slower disks or busy machines; compare the layers' ratio, not the absolute numbers. |
| `test_integration_postgres` errors instead of skipping | `LOANS_TESTCONTAINERS=1` is set but no container engine is reachable; unset it or start Podman/Docker. |
