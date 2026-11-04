"""L400 large-scale simulation: a checkpointed, parallel parameter sweep that survives a crash.

12 scenarios (arrival rate x desks) x 10 replications of the L200 lesson 8 clinic queue = 120 tasks.
Workers: a spawn-safe process pool. Storage: SQLite (stdlib), one transaction per batch, primary key
(scenario, rep) so a resumed run can never duplicate a row. Export: CSV (stdlib); Parquet in CI.
python sweep.py            (writes sweep.db and sweep.csv next to this file)
"""
import csv
import hashlib
import multiprocessing as mp
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parents[1] / "L200" / "08-multi-server-queue"))
import mmc_queue  # noqa: E402  (simulate(n_customers, c, lam, mu, seed))

ROOT, REPS, CUSTOMERS, BATCH = 20, 10, 5_000, 8
SCENARIOS = [(lam, c) for lam in (1.6, 2.0, 2.4, 2.8) for c in (3, 4, 5)]
SCHEMA = ("CREATE TABLE IF NOT EXISTS results (scenario INTEGER, rep INTEGER, lam REAL, desks INTEGER, "
          "wq REAL, util REAL, seed TEXT, PRIMARY KEY (scenario, rep))")


class Crash(Exception):
    """Stands in for a killed process, a reboot or a laptop lid closing."""


def all_tasks():
    return [(s, r) for s in range(len(SCENARIOS)) for r in range(REPS)]


def seeded(pending):
    """Attach a random stream to each pending task."""
    children = np.random.SeedSequence(ROOT).spawn(len(pending))  # one child per task still to run
    return [(s, r, child) for (s, r), child in zip(pending, children)]


def run_task(task):
    """Worker (top level, picklable for spawn): one replication of one scenario."""
    s, r, seed_seq = task
    lam, desks = SCENARIOS[s]
    seed = int(seed_seq.generate_state(1)[0])  # mmc_queue uses random.Random(int)
    out = mmc_queue.simulate(CUSTOMERS, desks, lam, 1.0, seed=seed)
    return s, r, lam, desks, out["Wq"], out["util"], f"{seed_seq.entropy}/{list(seed_seq.spawn_key)}"


def connect(db):
    con = sqlite3.connect(db)
    con.execute("PRAGMA journal_mode=WAL")  # readers do not block the writer; a commit is one appended record
    con.execute(SCHEMA)
    return con


def pending_tasks(con):
    done = set(con.execute("SELECT scenario, rep FROM results"))
    return [t for t in all_tasks() if t not in done]


def run_sweep(db, workers=2, crash_after=None, chunksize=4):
    """Run every task not yet in the database; commit every BATCH results. Returns the number of new rows."""
    con, new, batch = connect(db), 0, []
    tasks = seeded(pending_tasks(con))
    try:
        with mp.get_context("spawn").Pool(workers) as pool:
            for row in pool.imap_unordered(run_task, tasks, chunksize=chunksize):
                batch.append(row)
                if crash_after is not None and new + len(batch) > crash_after:
                    raise Crash(f"crashed after {new} committed results")
                if len(batch) == BATCH:
                    with con:  # one transaction: the whole batch is stored, or none of it
                        con.executemany("INSERT OR IGNORE INTO results VALUES (?,?,?,?,?,?,?)", batch)
                    new, batch = new + len(batch), []
            with con:
                con.executemany("INSERT OR IGNORE INTO results VALUES (?,?,?,?,?,?,?)", batch)
            new += len(batch)
    finally:
        con.close()
    return new


def checksum(db):
    """Order-independent fingerprint of the stored results (same rows, same values -> same hash)."""
    con = sqlite3.connect(db)
    rows = con.execute("SELECT scenario, rep, round(wq, 12), round(util, 12) FROM results ORDER BY scenario, rep")
    digest = hashlib.sha256(repr(rows.fetchall()).encode("utf-8")).hexdigest()[:16]
    con.close()
    return digest


def export_csv(db, path):
    con = sqlite3.connect(db)
    with Path(path).open("w", encoding="utf-8", newline="") as f:  # newline="": csv writes its own line ends
        w = csv.writer(f)
        w.writerow(["scenario", "rep", "lam", "desks", "wq", "util", "seed"])
        w.writerows(con.execute("SELECT * FROM results ORDER BY scenario, rep"))
    con.close()


def summary(db):
    con = sqlite3.connect(db)
    rows = con.execute("SELECT lam, desks, avg(wq), count(*) FROM results GROUP BY scenario ORDER BY scenario").fetchall()
    con.close()
    return rows


def fresh(db):
    for suffix in ("", "-wal", "-shm"):
        Path(str(db) + suffix).unlink(missing_ok=True)


def main(workers=2):
    clean, resumed = HERE / "sweep.db", HERE / "sweep_resumed.db"
    fresh(clean), fresh(resumed)
    start = time.perf_counter()
    run_sweep(clean, workers)
    print(f"clean run: {len(all_tasks())} tasks on {workers} spawn workers in {time.perf_counter() - start:.1f} s "
          f"(machine-dependent); checksum {checksum(clean)}")
    try:
        run_sweep(resumed, workers, crash_after=50)
    except Crash as exc:
        print(f"interrupted run: {exc}; resuming...")
    print(f"resumed run: +{run_sweep(resumed, workers)} rows; checksum {checksum(resumed)} -> "
          f"{'IDENTICAL' if checksum(resumed) == checksum(clean) else 'DIFFERENT'} to the clean run")
    export_csv(clean, HERE / "sweep.csv")
    print("lam desks  mean Wq (min)  reps")
    for lam, desks, wq, n in summary(clean):
        print(f"{lam:3.1f} {desks:5d} {wq:13.3f} {n:5d}")


if __name__ == "__main__":  # required with 'spawn': children re-import this file
    main()
