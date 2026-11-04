# Lab 08 – Aggregates and invariants (DDD)

A `Member` aggregate owns its loans. Every change goes through the root, so two invariants hold after every call: at most `max_loans` active loans, and never the same book twice for one member. `SqliteMemberRepository` loads and saves the whole aggregate in one transaction, with an optimistic version check. The rule that spans two members (one book, one borrower) is a partial unique index.

## Files
| File | Purpose |
|---|---|
| `member.py` | Aggregate root `Member`, entity `Loan` (frozen), rule errors (lesson code) |
| `member_repository.py` | One repository per aggregate; version check; partial unique index |
| `app.py` | Application service (load -> one method -> save) + demo |
| `test_aggregate.py` | Unit tests (no database) + repository tests (SQLite) |
| `test_build_task.py` | Build task check (overdue rule) |
| `solution/member.py` | Build task solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L200/08-aggregates-invariants
python app.py
python -m unittest -v
```
## Expected output (observed 2026-10-28, Python 3.12.15, Linux)

```
$ python app.py
m1 borrows b1          -> ok, 1/3 active, version 1
m1 borrows b1 again    -> AlreadyBorrowed: member m1 already has b1
m1 borrows b2          -> ok, 2/3 active, version 2
m1 borrows b3          -> ok, 3/3 active, version 3
m1 borrows b4          -> LoanLimitReached: member m1 already has 3 loans
m2 borrows b1          -> BookAlreadyOnLoan: another member has that book on loan (UNIQUE constraint failed: loans.book_id)
m1 returns b1          -> ok, 2/3 active, version 4
m2 borrows b1          -> ok, 1/3 active, version 1
```

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_limit (test_aggregate.MemberAggregateTest.test_limit) ... ok
test_no_double_loan_of_the_same_book (test_aggregate.MemberAggregateTest.test_no_double_loan_of_the_same_book) ... ok
test_outside_code_cannot_bypass_the_root (test_aggregate.MemberAggregateTest.test_outside_code_cannot_bypass_the_root) ... ok
test_return_frees_a_slot_and_keeps_history (test_aggregate.MemberAggregateTest.test_return_frees_a_slot_and_keeps_history) ... ok
test_cross_member_rule_is_enforced_by_the_database (test_aggregate.MemberRepositoryTest.test_cross_member_rule_is_enforced_by_the_database) ... ok
test_persists_in_a_file (test_aggregate.MemberRepositoryTest.test_persists_in_a_file) ... ok
test_round_trip (test_aggregate.MemberRepositoryTest.test_round_trip) ... ok
test_stale_copy_is_rejected (test_aggregate.MemberRepositoryTest.test_stale_copy_is_rejected) ... ok
test_unknown_member (test_aggregate.MemberRepositoryTest.test_unknown_member) ... ok
test_day_14_is_still_fine (test_build_task.OverdueInvariantTest.test_day_14_is_still_fine) ... ok
test_day_15_blocks_new_loans (test_build_task.OverdueInvariantTest.test_day_15_blocks_new_loans) ... ok
test_old_invariants_still_hold (test_build_task.OverdueInvariantTest.test_old_invariants_still_hold) ... ok
test_returning_the_overdue_book_unblocks (test_build_task.OverdueInvariantTest.test_returning_the_overdue_book_unblocks) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.236s

OK
```

## Build task
Add invariant 3 to `member.py`: a member with a loan older than 14 days (`LOAN_DAYS = 14`, overdue from day 15) cannot borrow; raise `HasOverdueLoans` naming the books. Returning the overdue book lifts the block. Only the aggregate changes.

- Solution: `solution/member.py` (read it only after trying).
- Check: `python -m unittest -v test_build_task` tests the solution by default. To test YOUR `member.py`:
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
[1] with version check    -> ConcurrencyConflict: member m1 changed since version 1
[1] without version check -> saved; stored loans: ['b1', 'b2', 'b4'] (limit 3)
[2] no unique index: b1 is on loan to ['m1', 'm2'] at the same time
```

## Mac mini and Windows
Inside an activated venv the commands are identical on both machines (`python3`/`py -3.12` also work outside a venv). Use `\` in paths on Windows. Tests bind 127.0.0.1 on port 0 and create scratch folders inside the lab folder, never in a system temp path.

## Troubleshooting
| Symptom | Action |
|---|---|
| `ConcurrencyConflict` in your own code | Expected when two requests saved the same member; reload the member and retry the command once. |
| `BookAlreadyOnLoan ... UNIQUE constraint failed: loans.book_id` | Another member has that book; the partial unique index enforces the cross-aggregate rule. |
| `FrozenInstanceError` when editing a loan | By design: change loans only through `Member.borrow` / `give_back`. |
