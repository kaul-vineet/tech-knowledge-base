# Lab 02 – Layered structure (presentation / service / repository)

The Library Loans service split into three layers. Swapping in-memory storage for SQLite
changes one line in `app.py`; the service rules and HTTP handler are untouched.

## Files
| File | Layer | Purpose |
|---|---|---|
| `handler.py` | presentation | HTTP ⇄ JSON, maps rule errors to 400/404/409 |
| `service.py` | service | Business rules: one active loan per book, max loans per member |
| `repository.py` | repository | `InMemoryLoanRepository` and `SqliteLoanRepository` (same 4 methods) |
| `app.py` | wiring | Picks the repository (`--storage memory|sqlite`), runs a short demo |
| `test_layers.py` | tests | Same rule tests against both repositories + HTTP test + dependency-direction check |
| `try_it.py` | – | Runs the lesson's two tryIt experiments and prints what happened (never edits the lab files) |

## Run
```bash
cd labs/L100/02-layered-structure
python app.py --storage memory
python app.py --storage sqlite
python -m unittest -v
```

## Expected output (observed 2026-10-28, Python 3.12.15)
```
storage=memory
borrow b1 by m1 -> 201 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'active'}
borrow b1 by m2 -> 409 {'error': 'book b1 is already on loan'}
return loan 1   -> 200 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'returned'}
get loan 99     -> 404 {'error': 'loan 99 not found'}
storage=sqlite
borrow b1 by m1 -> 201 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'active'}
borrow b1 by m2 -> 409 {'error': 'book b1 is already on loan'}
return loan 1   -> 200 {'id': 1, 'bookId': 'b1', 'memberId': 'm1', 'status': 'returned'}
get loan 99     -> 404 {'error': 'loan 99 not found'}
```
```
test_service_has_no_infrastructure_imports (test_layers.DependencyDirectionTest.test_service_has_no_infrastructure_imports) ... ok
test_borrow_conflict_get_and_errors (test_layers.HttpTest.test_borrow_conflict_get_and_errors) ... ok
test_borrow_returns_active_loan (test_layers.InMemoryRulesTest.test_borrow_returns_active_loan) ... ok
test_member_loan_limit (test_layers.InMemoryRulesTest.test_member_loan_limit) ... ok
test_return_frees_the_book (test_layers.InMemoryRulesTest.test_return_frees_the_book) ... ok
test_same_book_cannot_be_borrowed_twice (test_layers.InMemoryRulesTest.test_same_book_cannot_be_borrowed_twice) ... ok
test_unknown_loan (test_layers.InMemoryRulesTest.test_unknown_loan) ... ok
test_borrow_returns_active_loan (test_layers.SqliteRulesTest.test_borrow_returns_active_loan) ... ok
test_member_loan_limit (test_layers.SqliteRulesTest.test_member_loan_limit) ... ok
test_return_frees_the_book (test_layers.SqliteRulesTest.test_return_frees_the_book) ... ok
test_same_book_cannot_be_borrowed_twice (test_layers.SqliteRulesTest.test_same_book_cannot_be_borrowed_twice) ... ok
test_unknown_loan (test_layers.SqliteRulesTest.test_unknown_loan) ... ok

----------------------------------------------------------------------
Ran 12 tests in 1.165s

OK
```
Both storage modes print identical results: that is the point of the lab.

## Try it (observed 2026-10-28, Python 3.12.15)
Predict first, then run. `try_it.py` never edits the lab files (code changes go to a temporary `.tryit-work/` copy that is deleted afterwards); the tasks and predictions are in the lesson's `tryIt` field.
```bash
python try_it.py
```
```
[1] HTTP    borrow b2 by m1 -> 409 {'error': 'member m1 already has 1 loans'}
[1] service borrow b3 by m1 -> LoanLimitReached: member m1 already has 1 loans
[2] InMemoryLoanRepository   after returning loan 2, b4 gets loan id 4
[2] SqliteLoanRepository     after returning loan 2, b4 gets loan id 4
```

## Troubleshooting
| Symptom | Action |
|---|---|
| `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread` | Keep `check_same_thread=False` in `SqliteLoanRepository`; the server thread is not the thread that opened the connection. |
| A rule test passes for memory but fails for SQLite | The repositories have drifted; make both return the same `Loan` values (e.g. `returned` as `bool`). |
