# Lab 20 – Evolutionary architecture: expand/contract migrations, API versions, feature flags, fitness history

Library Loans splits `members.name` into `given_name` + `family_name` while **4 instances keep serving traffic** and are upgraded one at a time (a rolling deploy, simulated in `rollout.py`). `migrations.py` implements **expand/contract** (parallel change): expand (add columns), **backfill** in batches of 50, switch readers with a **release flag**, deploy code that no longer uses the old column, then **contract** (drop it), guarded by `can_contract()`. The API keeps **v1** (rebuilt from the new columns, with `Deprecation`, `Sunset` and `Link` headers) next to **v2**. Every step appends one JSON line of **fitness metrics**; `dashboard.py` reads that history and fails CI on any step with errors or expired flags. The shipped guard only checks the backfill, so the contract step runs while v2 instances still write the old column.

## Files
| File | Purpose |
|---|---|
| `migrations.py` | expand, backfill, `can_contract` (**seeded weakness**), contract (lesson code) |
| `app_versions.py` | v1 / v2 (dual write) / v3 data access |
| `rollout.py` | Rolling-deploy simulation, plans `big_bang` and `expand_contract`, fitness rows |
| `api.py` | `/v1` (deprecated) and `/v2` member representations |
| `flags.py` + `flags.json` | Release flag with owner and expiry; `no-expired-flags` gate |
| `dashboard.py` | Fitness history (JSON lines) → table + exit code |
| `app.py` | Runs both plans, writes `out/fitness.jsonl` |
| `failure_lab.py` | Premature contract, base vs solution, and the big bang |
| `adr/0004-expand-contract-migrations.md` | Decision record |
| `test_migrations.py` / `test_build_task.py` / `solution/migrations.py` | Tests / build task check / solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L400/20-evolutionary-migrations
python app.py && python dashboard.py                                    # shipped guard
python failure_lab.py
python app.py --solution && python dashboard.py --plan expand_contract  # exit 0
python -m unittest -v
```

## Expected output (observed 2026-10-28, Python 3.12.15, SQLite 3.44.0, Linux)
Seeded and in-memory: these lines repeat exactly. `ALTER TABLE … DROP COLUMN` works with the SQLite bundled here (3.44.0); print `sqlite3.sqlite_version` on your machine.
```
$ python app.py
big_bang        : 36 failed requests of 100; first error: v1: no such column: name
expand_contract : 62 failed requests of 700; first error: v2: table members has no column named name
history: out/fitness.jsonl (python dashboard.py)
$ python dashboard.py
plan / step                                                        fleet      errors unbackfilled  columns
big_bang / migrate all at once                                     v1v1v1v1        0            0  id,given_name,family_name
big_bang / deploy v3                                               v3v3v3v3       36            0  id,given_name,family_name  <-- errors=36 > 0
expand_contract / expand                                           v1v1v1v1        0          250  id,name,given_name,family_name
expand_contract / deploy v2 (dual write)                           v2v2v2v2        0          262  id,name,given_name,family_name
expand_contract / backfill                                         v2v2v2v2        0            0  id,name,given_name,family_name
expand_contract / flag read_split_name on                          v2v2v2v2        0            0  id,name,given_name,family_name
expand_contract / try contract: dropped name                       v2v2v2v2       50            0  id,given_name,family_name  <-- errors=50 > 0
expand_contract / deploy v3 (new columns only)                     v3v3v3v3       12            0  id,given_name,family_name  <-- errors=12 > 0
expand_contract / contract: dropped name                           v3v3v3v3        0            0  id,given_name,family_name
9 steps, 3 broke a fitness function
exit 1
$ python app.py --solution
big_bang        : 36 failed requests of 100; first error: v1: no such column: name
expand_contract : 0 failed requests of 700; first error: -
history: out/fitness.jsonl (python dashboard.py)
$ python dashboard.py --plan expand_contract
plan / step                                                        fleet      errors unbackfilled  columns
expand_contract / expand                                           v1v1v1v1        0          250  id,name,given_name,family_name
expand_contract / deploy v2 (dual write)                           v2v2v2v2        0          262  id,name,given_name,family_name
expand_contract / backfill                                         v2v2v2v2        0            0  id,name,given_name,family_name
expand_contract / flag read_split_name on                          v2v2v2v2        0            0  id,name,given_name,family_name
expand_contract / try contract: refused (instances on v2 still use members.name) v2v2v2v2        0            0  id,name,given_name,family_name
expand_contract / deploy v3 (new columns only)                     v3v3v3v3        0            0  id,name,given_name,family_name
expand_contract / contract: dropped name                           v3v3v3v3        0            0  id,given_name,family_name
7 steps, 0 broke a fitness function
exit 0
$ tail -1 out/fitness.jsonl
{"step": "contract: dropped name", "errors": 0, "columns": ["id", "given_name", "family_name"], "fleet": "v3v3v3v3", "unbackfilled": 0, "flags_on": 1, "flags_expired": 0, "plan": "expand_contract"}
```
`unbackfilled` is 250 after expand (200 seeded members + 50 created by v1 during the phase) and 262 after the v2 rollout (v1 instances still wrote 12 rows while being replaced). The backfill brings it to 0.

## failureLab: contract as soon as the backfill is done
```
$ python failure_lab.py
base    : try contract: dropped name with fleet v2v2v2v2 -> 62 failed requests of 700; first: v2: table members has no column named name
solution: try contract: refused (instances on v2 still use members.name) with fleet v2v2v2v2 -> 0 failed requests of 700
big bang: schema changed in one step -> 36 failed requests of 100; first: v1: no such column: name
```

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_allows_when_backfilled_and_all_on_v3 (test_build_task.ContractGuardTest.test_allows_when_backfilled_and_all_on_v3) ... ok
test_refuses_while_v2_instances_run (test_build_task.ContractGuardTest.test_refuses_while_v2_instances_run) ... ok
test_zero_failed_requests_and_old_column_gone (test_build_task.ContractGuardTest.test_zero_failed_requests_and_old_column_gone) ... ok
test_dashboard_flags_broken_steps (test_migrations.FitnessHistoryTest.test_dashboard_flags_broken_steps) ... ok
test_flags_gate (test_migrations.FitnessHistoryTest.test_flags_gate) ... ok
test_backfill_in_batches (test_migrations.MigrationStepTest.test_backfill_in_batches) ... ok
test_expand_is_idempotent_and_old_code_still_works (test_migrations.MigrationStepTest.test_expand_is_idempotent_and_old_code_still_works) ... ok
test_v1_api_survives_the_contract (test_migrations.MigrationStepTest.test_v1_api_survives_the_contract) ... ok
test_symptom_big_bang_breaks_old_instances (test_migrations.RolloutTest.test_symptom_big_bang_breaks_old_instances) ... ok
test_symptom_premature_contract (test_migrations.RolloutTest.test_symptom_premature_contract) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.534s

OK
```

## Build task (the hardening change)
Make `can_contract(db, fleet_versions)` also refuse while any running instance's version still uses `members.name` (`USES_OLD_COLUMN`).
- Solution: `solution/migrations.py`.
- Check (solution by default; YOUR file with `CHECK_MINE=1`):
```
CHECK_MINE=1 python -m unittest -v test_build_task          # Mac mini (zsh)
$env:CHECK_MINE = "1"; python -m unittest -v test_build_task   # Windows (PowerShell)
Remove-Item Env:\CHECK_MINE                                     # Windows: switch back
```
Fail before / pass after (observed 2026-10-28):
```
$ CHECK_MINE=1 python -m unittest test_build_task      # unchanged migrations.py
FAIL: test_refuses_while_v2_instances_run
FAIL: test_zero_failed_requests_and_old_column_gone
FAILED (failures=2)
$ python -m unittest test_build_task                   # solution
OK
```

## Try it (observed 2026-10-28)
```
$ python try_it.py
[1] name TEXT NOT NULL -> 38 failed requests {'deploy v3 (new columns only)': 38}; first: v3: NOT NULL constraint failed: members.name
[2] today 2026-12-01 -> {'gate': 'no-expired-flags', 'ok': False, 'value': ['read_split_name'], 'budget': 0}
```

## Mac mini and Windows
Same commands inside the venv; everything runs in memory. Read the history with `tail -3 out/fitness.jsonl` (zsh) or `Get-Content out\fitness.jsonl -Tail 3` (PowerShell).

## Troubleshooting
| Symptom | Action |
|---|---|
| `no such column` from old instances | A contract (or rename) ran before all code stopped using the column; run `can_contract` first. |
| `NOT NULL constraint failed` after the v3 deploy | The old column must be nullable or have a default before code stops writing it. SQLite 3.53+ has `ALTER TABLE … ALTER COLUMN … DROP NOT NULL`; older versions need SQLite's documented table-rebuild procedure. |
| `near "DROP": syntax error` | Your SQLite is too old for `DROP COLUMN`: print `sqlite3.sqlite_version`, update Python. |
