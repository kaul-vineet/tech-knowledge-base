# 1. Store sweep results in SQLite in batched transactions, keyed on (scenario, rep), with streams keyed the same way

## Status
Accepted (2026-10-28)

## Context
A 12-scenario × 10-replication sweep of the clinic queue runs on a process pool and may be interrupted. Constraints: a resumed run must store exactly the rows of an uninterrupted run, for any crash point and worker count; no duplicates; stdlib only locally. Measured by `sweep.py` and `storage_options.py` (sandbox mount, 1 CPU):
- Streams by position in the pending list (as in the L300 fix): the resumed checksum 8a6983e0e764e5cb differs from the clean 5a2bd148609737c0.
- Streams by SeedSequence(ROOT, spawn_key=(s, r)): both give 38975a17ffb143cd.
- CSV append + flush: 0.176 s / 5,000 rows, but a torn line swallowed the resumed row.
- SQLite: 22.8 s committing every row, 3.98 s in batches of 8, 0.058 s in one commit. An interrupted batch rolled back, and the resume gave 16 rows, 16 distinct.
- Parquet (pyarrow 26.0.0): a columnar export, run in CI only.

## Decision
Use SQLite (WAL) as the checkpoint store, one transaction per batch of 8 results, PRIMARY KEY (scenario, rep) with INSERT OR IGNORE, and streams keyed on the task identity. CSV and Parquet are exports.

## Consequences
- Resume is exact and idempotent. At most 7 completed tasks are redone after a crash.
- One writer (the parent). For several machines, use one database per machine merged by key.
- Keep the database on a local disk (SQLite: WAL "does not work over a network filesystem").
- Fitness function: `test_fitness.py` (crashes at 0, 17 and 40 results on 1 and 2 workers; 48 rows and the clean checksum every time).
