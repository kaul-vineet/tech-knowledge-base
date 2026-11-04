"""tryIt experiments for lesson 20 (run: python try_it.py). Spawn-safe: everything runs under the main guard."""
import importlib.util
import sqlite3
import tempfile
from pathlib import Path

import sweep as shipped

if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("sweep_fixed", Path(__file__).with_name("solution") / "sweep.py")
    fixed = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixed)
    fixed.run_task = shipped.run_task  # same worker; spawned children import it from sweep.py
    for m in (shipped, fixed):
        m.REPS = 4  # 48 tasks keep the experiment short
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        # 1. Predict: does the crash point matter once streams are keyed on (scenario, rep)?
        fixed.run_sweep(d / "clean.db", workers=2)
        for crash_after in (9, 33):
            db = d / f"fixed{crash_after}.db"
            try:
                fixed.run_sweep(db, workers=2, crash_after=crash_after)
            except fixed.Crash:
                fixed.run_sweep(db, workers=1)
            print(f"fixed, crash after {crash_after}, resume on 1 worker: identical = "
                  f"{fixed.checksum(db) == fixed.checksum(d / 'clean.db')}")
        # 2. Predict: which stream did task (7, 2) use after a resume, in each version?
        for name, m in (("shipped", shipped), ("fixed", fixed)):
            db = d / f"{name}_seed.db"
            try:
                m.run_sweep(db, workers=1, crash_after=20)
            except m.Crash:
                m.run_sweep(db, workers=1)
            con = sqlite3.connect(db)
            print(f"{name}: task (7, 2) seed column = {con.execute('SELECT seed FROM results WHERE scenario=7 AND rep=2').fetchone()[0]}")
            con.close()
