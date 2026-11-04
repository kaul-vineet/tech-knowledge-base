# 20 · Large-scale and parallel simulation: reproducible streams, checkpoints, result storage, scaling

A parameter sweep of 12 scenarios × 10 replications of the clinic queue runs on a spawn-safe process pool. Results are stored in SQLite (stdlib) in batched transactions keyed on (scenario, rep), so the sweep can crash and resume. The failure lab shows that the L300 lesson 16 seeding fix, one spawned child per task *position*, is not enough once runs resume. You also measure storage options (CSV / SQLite / Parquet) and scaling (workers × chunk size, Amdahl's law).

Read the concept note first: `../../../content/concepts/L400/20-parallel-scale.md`. Needs Python 3.12 + numpy. Parquet needs pyarrow 26.0.0 (CI only).

## Run
```bash
python sweep.py             # clean sweep, crashed + resumed sweep, checksums, CSV export, summary
python storage_options.py   # CSV vs SQLite write cost and crash behaviour
python scaling.py           # tasks/s for 1, 2, 4 workers and chunk sizes 1, 8 (slow here: 1 CPU)
```
Windows/macOS: the same commands. Keep the `if __name__ == "__main__":` guard, because spawned workers re-import the file.

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux, 1 CPU) - shipped file
Timing varies by machine; everything else is seeded.
```
clean run: 120 tasks on 2 spawn workers in 37.5 s (machine-dependent); checksum 5a2bd148609737c0
interrupted run: crashed after 48 committed results; resuming...
resumed run: +72 rows; checksum 8a6983e0e764e5cb -> DIFFERENT to the clean run
lam desks  mean Wq (min)  reps
1.6     3         0.181    10
...
2.8     3         3.909    10
2.8     4         0.353    10
2.8     5         0.080    10
```
`storage_options.py` (timings from this sandbox's network-backed mount):
```
write 5,000 rows (machine-dependent):
  CSV append + flush per row    0.176 s
  SQLite, commit every row     22.841 s
  SQLite, commit every 8 rows   3.980 s
  SQLite, one commit            0.058 s
crash mid-write, CSV: 1 malformed of 2 lines - the torn row swallowed the resumed row
crash mid-batch, SQLite: 16 rows, 16 distinct after resume (the torn batch rolled back)
```
`scaling.py` (1 CPU, so the speed-ups are below 1; run it on your machine):
```
os.cpu_count() = 1
workers 1 chunksize 1:   14.0 tasks/s  (speed-up x1.00)
workers 1 chunksize 8:   15.7 tasks/s  (speed-up x1.12)
workers 2 chunksize 1:    7.0 tasks/s  (speed-up x0.50)
workers 2 chunksize 8:    9.4 tasks/s  (speed-up x0.67)
workers 4 chunksize 1:    3.5 tasks/s  (speed-up x0.25)
workers 4 chunksize 8:    6.1 tasks/s  (speed-up x0.43)
Amdahl serial fraction estimate (chunksize 8): f = 1.00
```

## Failure lab: break it, see it, fix it
- **Fault (seeded, shipped in `sweep.py`):** `seeded()` gives the pending tasks `SeedSequence(20).spawn(len(pending))`, so child i belongs to position i. A clean run is reproducible. After a crash, the 72 remaining tasks get children 0-71 of a *new* spawn, the same streams the first 72 tasks used. The resumed database differs (checksum 8a6983e0e764e5cb against 5a2bd148609737c0), and nothing warns you.
- **Fix (your build task):** key the stream on the task identity: `SeedSequence(ROOT, spawn_key=(s, r))`. Clean and resumed runs then both give `38975a17ffb143cd` (`solution/sweep.py`).
- **Proof:** `BUILD_TARGET=mine python -m unittest test_build_task` fails 2 of 2 on the shipped file and passes on the solution. `TestFailureLab` in `test_sweep.py` keeps the fault reproducible.

## Observability
`sweep.db` stores a `seed` column per row (`entropy/[spawn_key]`). In the shipped file, task (7, 2) of a resumed run reads `20/[14]`, meaning position 14 of the pending list. After the fix it reads `20/[7, 2]`, so the key *is* the task (tryIt 2). `sweep.csv` is the export for Orange, KNIME or a notebook.

## Design decision and fitness function
Decision: `decisions/0001-sqlite-checkpoints-identity-streams.md`. Fitness function `test_fitness.py`: crash at 0, 17 and 40 results on 1 and 2 workers, then resume. There must be 48 rows and the clean checksum every time. Observed: `Ran 1 test ... OK` on the solution, and `FAILED (failures=2)` on the shipped file (the crash-at-0 case passes either way: nothing was stored before the resume).

## Test
```bash
python -m unittest -v
```
Observed: `Ran 9 tests ... OK (skipped=1)` (test_sweep 5 + the Parquet round trip, skipped without pyarrow; test_build_task 2; test_fitness 1; about 6 minutes here, because every pool starts fresh interpreters on 1 CPU).

## Try it
```bash
python try_it.py
```
Observed (48 tasks):
```
fixed, crash after 9, resume on 1 worker: identical = True
fixed, crash after 33, resume on 1 worker: identical = True
shipped: task (7, 2) seed column = 20/[14]
fixed: task (7, 2) seed column = 20/[7, 2]
```
On this Linux sandbox, simulated crashes inside the pool sometimes print `UserWarning: ResourceTracker called reentrantly ...` after the shipped run. It is harmless: the exception terminates the pool, and the results are unaffected.

## Build it (design task)
Change `seeded(pending)` in `sweep.py` so that each task's stream depends only on (scenario, rep), not on its position in the pending list.

Hints:
- `np.random.SeedSequence(ROOT, spawn_key=(s, r))` builds the same child that a spawn tree would give at that address.
- Run `python sweep.py` again: the resumed checksum must say IDENTICAL.

Check: `BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v` (PowerShell: `$env:BUILD_TARGET = "mine"`).

## Library equivalent (pending-ci)
`to_parquet.py` exports `sweep.db` to Parquet with pyarrow 26.0.0 (Apache-2.0; wheels for macOS arm64 and Windows x64) and reads it back. Its test is skipped locally. Dask and Ray spread sweeps over machines and are listed as equivalents only.

## Files
- `sweep.py`: main lab (tasks, seeding, spawn pool, SQLite checkpoints, CSV export). Ships the unfixed `seeded()`.
- `storage_options.py`: CSV/SQLite evidence. `scaling.py`: throughput and Amdahl fit. `to_parquet.py`: Parquet export (pending-ci).
- `solution/sweep.py`: buildTask solution.
- `try_it.py`, `test_sweep.py`, `test_build_task.py`, `test_fitness.py`.
- `decisions/0001-sqlite-checkpoints-identity-streams.md`: the ADR.
