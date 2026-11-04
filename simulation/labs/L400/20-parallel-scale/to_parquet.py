"""Parquet export (pending-ci: needs pyarrow 26.0.0, Apache-2.0; not installed in the sandbox).

Reads sweep.db, writes sweep.parquet (columnar, typed, compressed), reads it back and compares.
python -m pip install pyarrow==26.0.0 && python to_parquet.py
"""
import sqlite3
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent


def export(db=HERE / "sweep.db", out=HERE / "sweep.parquet"):
    con = sqlite3.connect(db)
    cur = con.execute("SELECT scenario, rep, lam, desks, wq, util, seed FROM results ORDER BY scenario, rep")
    names = [d[0] for d in cur.description]
    rows = cur.fetchall()
    con.close()
    table = pa.table({name: [r[i] for r in rows] for i, name in enumerate(names)})
    pq.write_table(table, out)
    back = pq.read_table(out)
    return table.num_rows, back.equals(table), out.stat().st_size


if __name__ == "__main__":
    rows, same, size = export()
    print(f"parquet: {rows} rows, read back identical: {same}, {size:,} bytes")
