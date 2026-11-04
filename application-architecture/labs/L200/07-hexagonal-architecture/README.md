# Lab 07 – Hexagonal architecture (ports and adapters)

The Library Loans rules from lesson 2, refactored so the domain depends only on **ports** it owns. Two driving adapters (HTTP, CLI) call the same hexagon; two driven adapters (in-memory, SQLite) plug into its storage port. Swapping one changes one line in `app.py` and nothing in `domain.py`.

## Files
| File | Purpose |
|---|---|
| `ports.py` | Ports: `ForStoringLoans` (driven), `ForManagingLoans` (driving), as `typing.Protocol` |
| `domain.py` | The hexagon: `Loan`, rule errors, `LoanService` (lesson code) |
| `driven_memory.py` | Driven adapter: dict |
| `driven_sqlite.py` | Driven adapter: SQLite (the only `sqlite3` import) |
| `driving_http.py` | Driving adapter: HTTP/JSON, errors -> 400/404/409 |
| `driving_cli.py` | Driving adapter: command line, errors -> exit codes 1/2/3 |
| `app.py` | Composition root: picks adapters; demo drives one hexagon via CLI and HTTP |
| `test_hexagon.py` | Port contract tests (both stores), domain rules, adapters, dependency-rule fitness test |
| `test_build_task.py` | Build task check (JSON-file adapter) |
| `solution/driven_jsonfile.py` | Build task solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L200/07-hexagonal-architecture
python app.py --storage memory
python app.py --storage sqlite
python -m unittest -v
```
## Expected output (observed 2026-10-28, Python 3.12.15, Linux)

Both storage modes print the same lines: the domain did not change.

```
$ python app.py --storage memory
storage=memory
cli  borrow b1 m1      -> 0 {"id": 1, "bookId": "b1", "memberId": "m1", "status": "active"}
http POST b1 by m2     -> 409 {'error': 'book b1 is already on loan'}
cli  return 1          -> 0 {"id": 1, "bookId": "b1", "memberId": "m1", "status": "returned"}
http GET /loans/1      -> 200 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'returned'}
cli  show 99           -> 3 error: loan 99 not found
```

```
$ python app.py --storage sqlite
storage=sqlite
cli  borrow b1 m1      -> 0 {"id": 1, "bookId": "b1", "memberId": "m1", "status": "active"}
http POST b1 by m2     -> 409 {'error': 'book b1 is already on loan'}
cli  return 1          -> 0 {"id": 1, "bookId": "b1", "memberId": "m1", "status": "returned"}
http GET /loans/1      -> 200 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'returned'}
cli  show 99           -> 3 error: loan 99 not found
```

The CLI on its own keeps loans in a SQLite file (`demo.db`, deleted afterwards):
```
$ python driving_cli.py --db demo.db borrow b1 m1
{"id": 1, "bookId": "b1", "memberId": "m1", "status": "active"}
(exit code 0)
$ python driving_cli.py --db demo.db borrow b1 m2
error: book b1 is already on loan
(exit code 2)
$ python driving_cli.py --db demo.db return 1
{"id": 1, "bookId": "b1", "memberId": "m1", "status": "returned"}
(exit code 0)
```

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_adapter_depends_only_on_the_hexagon (test_build_task.JsonFileStoreContractTest.test_adapter_depends_only_on_the_hexagon) ... ok
test_add_numbers_from_one (test_build_task.JsonFileStoreContractTest.test_add_numbers_from_one) ... ok
test_domain_rules_run_on_the_new_adapter (test_build_task.JsonFileStoreContractTest.test_domain_rules_run_on_the_new_adapter) ... ok
test_get_unknown_is_none (test_build_task.JsonFileStoreContractTest.test_get_unknown_is_none) ... ok
test_is_a_storing_port (test_build_task.JsonFileStoreContractTest.test_is_a_storing_port) ... ok
test_returned_loans_are_not_active (test_build_task.JsonFileStoreContractTest.test_returned_loans_are_not_active) ... ok
test_adapters_do_not_import_each_other (test_hexagon.DependencyRuleTest.test_adapters_do_not_import_each_other) ... ok
test_hexagon_imports_no_technology_and_no_adapter (test_hexagon.DependencyRuleTest.test_hexagon_imports_no_technology_and_no_adapter) ... ok
test_rules (test_hexagon.DomainRulesTest.test_rules) ... ok
test_cli_and_http_drive_the_same_hexagon (test_hexagon.DrivingAdaptersTest.test_cli_and_http_drive_the_same_hexagon) ... ok
test_add_numbers_from_one (test_hexagon.InMemoryStoreTest.test_add_numbers_from_one) ... ok
test_get_unknown_is_none (test_hexagon.InMemoryStoreTest.test_get_unknown_is_none) ... ok
test_is_a_storing_port (test_hexagon.InMemoryStoreTest.test_is_a_storing_port) ... ok
test_returned_loans_are_not_active (test_hexagon.InMemoryStoreTest.test_returned_loans_are_not_active) ... ok
test_add_numbers_from_one (test_hexagon.SqliteStoreTest.test_add_numbers_from_one) ... ok
test_get_unknown_is_none (test_hexagon.SqliteStoreTest.test_get_unknown_is_none) ... ok
test_is_a_storing_port (test_hexagon.SqliteStoreTest.test_is_a_storing_port) ... ok
test_returned_loans_are_not_active (test_hexagon.SqliteStoreTest.test_returned_loans_are_not_active) ... ok
test_survives_reopen (test_hexagon.SqliteStoreTest.test_survives_reopen) ... ok

----------------------------------------------------------------------
Ran 19 tests in 2.194s

OK
```

## Build task
Add a third driven adapter, `driven_jsonfile.py` with class `JsonFileLoanStore(path)`, that keeps loans in a JSON file. It must pass the same `StoreContract` tests and import nothing from the other adapters. Then add one line to `DRIVEN` in `app.py`. `domain.py` stays untouched.

- Solution: `solution/driven_jsonfile.py` (read it only after trying).
- Check: `python -m unittest -v test_build_task` tests the solution by default. To test YOUR `driven_jsonfile.py`:
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
[1] domain.py imports sqlite3 -> FAILED (failures=1): domain.py must depend on ports only, but imports ['sqlite3']
[2] isinstance(HalfStore(), ForStoringLoans) -> False
[2] borrow b1 -> loan 1 (still works)
[2] give_back(1) -> AttributeError: 'HalfStore' object has no attribute 'mark_returned'
```

## Mac mini and Windows
Inside an activated venv the commands are identical on both machines (`python3`/`py -3.12` also work outside a venv). Use `\` in paths on Windows. Tests bind 127.0.0.1 on port 0 and create scratch folders inside the lab folder, never in a system temp path.

## Troubleshooting
| Symptom | Action |
|---|---|
| `ModuleNotFoundError: No module named 'ports'` | Run commands from the lab folder (`cd labs/L200/07-hexagonal-architecture`). |
| `test_hexagon_imports_no_technology_and_no_adapter` fails | The message names the import that broke the rule; move that code into an adapter. |
| `OSError: [Errno 98] Address already in use` (macOS `[Errno 48]`, Windows `[WinError 10048]`) | Only if you hard-coded a port; the lab uses port 0. |
