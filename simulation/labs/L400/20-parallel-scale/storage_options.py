"""Evidence for the storage decision (ADR 0001): CSV append vs SQLite per-row commit vs SQLite batched commits.

Writes 5,000 result rows each way into a temporary folder, then simulates a crash in the middle of a write.
python storage_options.py      (timings are machine-dependent; the crash results are not)
"""
import csv
import sqlite3
import tempfile
import time
from pathlib import Path

ROWS = [(s, r, 2.0, 3, 0.4 + s / 1000, 0.66) for s in range(500) for r in range(10)]
INSERT = "INSERT OR IGNORE INTO results VALUES (?,?,?,?,?,?)"
SCHEMA = "CREATE TABLE results (scenario INT, rep INT, lam REAL, desks INT, wq REAL, util REAL, PRIMARY KEY (scenario, rep))"


def csv_append(path):
    with path.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for row in ROWS:
            w.writerow(row)
            f.flush()  # make each row visible as soon as it exists (what a checkpoint needs)


def sqlite_rows(path, batch):
    con = sqlite3.connect(path)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute(SCHEMA)
    for i in range(0, len(ROWS), batch):
        with con:  # one transaction per batch
            con.executemany(INSERT, ROWS[i:i + batch])
    con.close()


def timed(fn, *args):
    start = time.perf_counter()
    fn(*args)
    return time.perf_counter() - start


def torn_csv(path):
    """A crash mid-write leaves half a line; the resumed run then appends after it."""
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write("0,0,2.0,3,0.4,0.66\r\n0,1,2.0,3,0.4")  # killed here
    with path.open("a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow((0, 1, 2.0, 3, 0.401, 0.66))  # resume re-runs task (0, 1)
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    return sum(len(r) != 6 for r in rows), len(rows)


def interrupted_sqlite(path):
    con = sqlite3.connect(path)
    con.execute(SCHEMA)
    with con:
        con.executemany(INSERT, ROWS[:8])
    try:
        with con:
            con.executemany(INSERT, ROWS[8:12])
            raise RuntimeError("killed mid-batch")
    except RuntimeError:
        pass
    with con:
        con.executemany(INSERT, ROWS[:16])  # resume: re-run everything not committed; duplicates are ignored
    n, distinct = con.execute("SELECT count(*), count(DISTINCT scenario * 100 + rep) FROM results").fetchone()
    con.close()
    return n, distinct


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        print(f"write {len(ROWS):,} rows (machine-dependent):")
        print(f"  CSV append + flush per row   {timed(csv_append, d / 'a.csv'):6.3f} s")
        print(f"  SQLite, commit every row     {timed(sqlite_rows, d / 'b.db', 1):6.3f} s")
        print(f"  SQLite, commit every 8 rows  {timed(sqlite_rows, d / 'c.db', 8):6.3f} s")
        print(f"  SQLite, one commit           {timed(sqlite_rows, d / 'd.db', len(ROWS)):6.3f} s")
        bad, total = torn_csv(d / "torn.csv")
        print(f"crash mid-write, CSV: {bad} malformed of {total} lines - the torn row swallowed the resumed row")
        n, distinct = interrupted_sqlite(d / "e.db")
        print(f"crash mid-batch, SQLite: {n} rows, {distinct} distinct after resume (the torn batch rolled back)")
