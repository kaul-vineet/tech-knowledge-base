**Concept: large-scale simulation - parallel sweeps that can crash, resume and still give the same answer**

## Why it matters
A sweep of 12 scenarios × 10 replications is small. Real studies run thousands of tasks for hours, on a Mac mini overnight or a Windows PC over a weekend. Something will interrupt them: a reboot, a full disk, a laptop lid. If a restart redoes everything, you lose hours. If it resumes but the results change, you have lost something worse, because nobody can reproduce your numbers. L'Ecuyer et al. (2017) put the requirement plainly: stream assignments and results "should not depend on the hardware in any way, neither on how the tasks are assigned to threads".

## Mental model
Identity, not order. A task is *what* is computed, (scenario, rep). Its random stream, its database key and its result are all functions of that identity, never of when or where it ran.

```
tasks (s, r) --pending = all - done--> Pool(spawn).imap_unordered --> batch of 8 --one transaction--> SQLite
     |                                                                         PRIMARY KEY (scenario, rep)
     +-- stream = SeedSequence(ROOT, spawn_key=(s, r))                         INSERT OR IGNORE
```

## Design space
**Execution.** You can run serially (simple and debuggable) or use a spawn-safe process pool with chunked tasks (it uses the cores, but each worker pays start-up and pickling costs). For many machines there are Dask and Ray, listed as equivalents. The pool is the default only when tasks are large compared with start-up.

**Result storage.**
- **CSV append** is human-readable and fast: 0.176 s for 5,000 rows with a flush per row. It has no transactions, so a crash leaves a torn line.
- **SQLite with batched transactions** is stdlib and atomic. "Either all database changes within a single transaction occur or none of them occur", even after a power failure (sqlite.org). A primary key makes duplicates impossible.
- **Parquet** is columnar, typed and compressed, and best for analysis. It is written in one go, so it is an export format, not a checkpoint (pyarrow 26.0.0, run in CI).

**Streams.** The L300 lesson 16 fix, `SeedSequence(root).spawn(len(tasks))`, ties child i to *position* i. That is safe for one uninterrupted run. To survive a resume, key each stream on the task identity.

## How to decide
Criteria: same results for any crash point and any worker count, no duplicates or gaps, write cost, and measured scaling.

**Worked example (lab run).** The shipped sweep crashed after 48 committed results and resumed. Its checksum 8a6983e0e764e5cb differed from the clean run's 5a2bd148609737c0, because the resumed tasks got children 0-71 of a new spawn. With streams keyed on (s, r), both runs give 38975a17ffb143cd. Storage on this sandbox mount: committing each SQLite row took 22.8 s for 5,000 rows, batches of 8 took 3.98 s and one commit took 0.058 s. A torn CSV line swallowed the resumed row (1 malformed of 2 lines). An interrupted SQLite batch rolled back and the resume ended with 16 rows, 16 distinct. Scaling on this 1-CPU sandbox: 1 worker ran 15.7 tasks/s and 4 workers 6.1, so the Amdahl fit says f = 1.00. Run `scaling.py` on the Mac mini or Windows PC to see real gains. **Decision (ADR 0001):** SQLite, batches of 8, WAL, streams keyed on identity, CSV and Parquet as exports. `test_fitness.py` crashes the sweep at 0, 17 and 40 results on 1 and 2 workers and requires the clean checksum and 48 rows every time.

## Failure modes at scale
- **Commit cost dominates:** per-row commits were 390× slower than one commit here, and slower still on network drives. The sign is CPU idle while the disk is busy. Batch, and size the batch to how much work you can afford to redo.
- **WAL on a network file system:** SQLite says WAL "does not work over a network filesystem". Keep the database on a local disk and copy it afterwards.
- **One writer:** SQLite serialises writers, so only the parent writes. With many machines, give each one its own file and merge by primary key.
- **Amdahl's ceiling:** with serial fraction f, the speed-up is capped at 1/f however many cores you add. Measure f; do not assume it.

## Common mistakes
- Numbering streams by list position, worker id or completion order.
- Appending results without a key, then "fixing" duplicates by hand.
- Reporting a speed-up without the machine, the core count and the chunk size.
