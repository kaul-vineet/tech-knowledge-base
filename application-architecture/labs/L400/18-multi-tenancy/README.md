# Lab 18 – Multi-tenancy: shared schema vs schema per tenant vs database per tenant

Library Loans hosts 50 libraries (tenants, 40 loans each). `tenancy.py` stores them in three layouts on **SQLite files** and measures each one: **isolation** (rows of other libraries returned when one query forgets the tenant filter), **noisy neighbour** (another library's writes blocked while one library runs a bulk import) and **migration effort** (DDL statements and files touched for one new column). Two guards keep every query **tenant-scoped**: a static **fitness test** (`fitness_tenant.py`: no SQL on a tenant table without `WHERE tenant_id = ?`) and a runtime **TenantGuard** (each statement must carry the current tenant's own id; it reads the expanded SQL from `sqlite3`'s trace callback).

## Files
| File | Purpose |
|---|---|
| `tenancy.py` | Three layouts, `TenantGuard`, seeding and the three measurements (lesson code) |
| `repository.py` | Loans SQL used by every layout; **seeded fault**: the new overdue report has no tenant filter |
| `fitness_tenant.py` | Fitness function: tenant-scoped SQL (static) |
| `app.py` | Measures all three layouts, writes `out/tenancy.jsonl` |
| `failure_lab.py` | The unscoped report in the shared schema, base vs solution |
| `adr/0002-shared-schema-with-tenant-guard.md` | Decision record |
| `test_tenancy.py` | Measurements (6 tenants), guards |
| `test_build_task.py` / `solution/repository.py` | Build task check / solution |
| `try_it.py` | The two tryIt experiments |

## Run
```bash
cd labs/L400/18-multi-tenancy
python app.py                  # shipped repository (overdue report forgets tenant_id)
python failure_lab.py
python app.py --solution
python fitness_tenant.py       # exit 1 until you fix repository.py
python -m unittest -v
```
The databases live in a scratch folder (`.work-*`) inside the lab and are deleted after each run.

## Expected output (observed 2026-10-28, Python 3.12.15, SQLite 3.44.0, Linux)
Rows, leaks, blocked writes and DDL counts are deterministic. The migration `ms` varies with the disk (here a network mount: 9–54 ms shared, 0.5–9.1 s per-tenant tables, 0.45–4.5 s per-tenant files over 3 runs).
```
$ python app.py
{"layout": "shared-schema", "isolation": {"rows": 700, "leaked": 686, "guard_violations": 1}, "noisy_neighbour": {"attempts": 20, "blocked": 20}, "migration": {"ddl_statements": 1, "files": 1, "ms": 53.5}}
{"layout": "schema-per-tenant", "isolation": {"rows": 14, "leaked": 0, "guard_violations": 1}, "noisy_neighbour": {"attempts": 20, "blocked": 20}, "migration": {"ddl_statements": 50, "files": 1, "ms": 1287.3}}
{"layout": "db-per-tenant", "isolation": {"rows": 14, "leaked": 0, "guard_violations": 1}, "noisy_neighbour": {"attempts": 20, "blocked": 0}, "migration": {"ddl_statements": 50, "files": 50, "ms": 787.5}}
$ python app.py --solution
{"layout": "shared-schema", "isolation": {"rows": 14, "leaked": 0, "guard_violations": 0}, "noisy_neighbour": {"attempts": 20, "blocked": 20}, "migration": {"ddl_statements": 1, "files": 1, "ms": 9.7}}
{"layout": "schema-per-tenant", "isolation": {"rows": 14, "leaked": 0, "guard_violations": 0}, "noisy_neighbour": {"attempts": 20, "blocked": 20}, "migration": {"ddl_statements": 50, "files": 1, "ms": 1112.3}}
{"layout": "db-per-tenant", "isolation": {"rows": 14, "leaked": 0, "guard_violations": 0}, "noisy_neighbour": {"attempts": 20, "blocked": 0}, "migration": {"ddl_statements": 50, "files": 50, "ms": 4518.8}}
$ python fitness_tenant.py
{"gate": "tenant-scoped-queries", "ok": false, "value": ["repository.py:8 SELECT id, member_id, book_id, due FROM {table} WHERE due < ? ORDER BY id"], "budget": 0}
```
SQLite allows one writer per file: lib01's open import transaction (`BEGIN IMMEDIATE`) makes all 20 of lib02's writes fail with `database is locked` (busy timeout 0) when they share a file; with one file per library none fail.

## failureLab: one new query without the tenant filter
```
$ python failure_lab.py
base    : lib00 overdue report returns 700 rows, 686 from other libraries; guard violations 1; static gate ok=False
    guard saw: SELECT id, member_id, book_id, due FROM loans WHERE due < '2026-10-28' ORDER BY id
solution: lib00 overdue report returns 14 rows, 0 from other libraries; guard violations 0; static gate ok=True
```
The guard flags the query in all three layouts, also where the layout happened to contain the damage, so the bug is found before the next layout change exposes it.

## Tests (observed 2026-10-28)
```
$ python -m unittest -v
test_every_repository_call_passes_the_guard (test_build_task.TenantScopeTest.test_every_repository_call_passes_the_guard) ... ok
test_overdue_report_sees_only_its_tenant (test_build_task.TenantScopeTest.test_overdue_report_sees_only_its_tenant) ... ok
test_static_gate (test_build_task.TenantScopeTest.test_static_gate) ... ok
test_static_gate_flags_the_new_report (test_tenancy.GuardTest.test_static_gate_flags_the_new_report) ... ok
test_static_gate_passes_on_scoped_sql (test_tenancy.GuardTest.test_static_gate_passes_on_scoped_sql) ... ok
test_migration_effort (test_tenancy.LayoutTest.test_migration_effort) ... ok
test_noisy_neighbour_only_separate_files_isolate_writes (test_tenancy.LayoutTest.test_noisy_neighbour_only_separate_files_isolate_writes) ... ok
test_separate_tables_or_files_contain_the_bug_but_the_guard_still_sees_it (test_tenancy.LayoutTest.test_separate_tables_or_files_contain_the_bug_but_the_guard_still_sees_it) ... ok
test_symptom_shared_schema_leaks_other_tenants (test_tenancy.LayoutTest.test_symptom_shared_schema_leaks_other_tenants) ... ok

----------------------------------------------------------------------
Ran 9 tests in 7.079s

OK
```
`test_tenancy.py` uses 6 tenants instead of 50 (same mechanics, faster): 84 rows, 70 leaked in the shared schema.

## Build task (the hardening change)
Scope the overdue report: `WHERE tenant_id = ? AND due < ?`, bind `session.tenant` first.
- Solution: `solution/repository.py`.
- Check (solution by default; YOUR file with `CHECK_MINE=1`):
```
CHECK_MINE=1 python -m unittest -v test_build_task          # Mac mini (zsh)
$env:CHECK_MINE = "1"; python -m unittest -v test_build_task   # Windows (PowerShell)
Remove-Item Env:\CHECK_MINE                                     # Windows: switch back
```
Fail before / pass after (observed 2026-10-28):
```
$ CHECK_MINE=1 python -m unittest test_build_task      # unchanged repository.py
FAIL: test_every_repository_call_passes_the_guard
FAIL: test_overdue_report_sees_only_its_tenant
FAIL: test_static_gate
FAILED (failures=3)
$ python -m unittest test_build_task                   # solution
OK
```

## Try it (observed 2026-10-28)
```
$ python try_it.py
[1] attached 10 tenant files, then: too many attached databases - max 10
[2] session lib00 queries tenant_id='lib01' -> 6 rows; guard violations ["SELECT id FROM loans WHERE tenant_id = 'lib01'"]
```

## Mac mini and Windows
Same commands inside the venv. SQLite locking is per file on every OS; on Windows an open connection keeps the file locked, so the lab closes every connection before deleting its scratch folder. Keep the lab on a local disk: SQLite's locking is unreliable on some network file systems, and the timings above are slow because this sandbox's disk is a network mount.

## Troubleshooting
| Symptom | Action |
|---|---|
| `database is locked` in your own runs | Another connection holds a write transaction: keep transactions short, or give the connection a busy timeout. |
| `PermissionError` deleting `.work-*` on Windows | A connection was left open; close it (the lab's functions all close theirs). |
| Guard reports a statement you think is fine | It needs the current tenant's id as a bound value; a hard-coded id for another tenant is exactly what it should catch. |
