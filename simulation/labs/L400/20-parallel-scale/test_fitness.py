"""Fitness function (lesson 20 ADR 0001): keeps "SQLite checkpoints + streams keyed on (scenario, rep)" true.

Fails the build if a sweep interrupted at ANY of three points and resumed on 1 or 2 workers does not store
exactly the same 48 rows (same checksum, no duplicates, no gaps) as an uninterrupted sweep.
Default target: solution/sweep.py; BUILD_TARGET=mine checks your sweep.py (the shipped file fails).
"""
import importlib.util
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import sweep as reference

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("sweep.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/sweep.py")
spec = importlib.util.spec_from_file_location("sweep_fitness", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)
target.run_task, target.REPS = reference.run_task, 4  # 48 tasks


class TestSweepFitness(unittest.TestCase):
    def test_any_crash_point_any_worker_count_same_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            clean = Path(tmp) / "clean.db"
            target.run_sweep(clean, workers=2)
            for crash_after, workers in ((0, 1), (17, 2), (40, 1)):
                with self.subTest(crash_after=crash_after, workers=workers):
                    db = Path(tmp) / f"r{crash_after}.db"
                    with self.assertRaises(target.Crash):
                        target.run_sweep(db, workers=workers, crash_after=crash_after)
                    target.run_sweep(db, workers=workers)
                    con = sqlite3.connect(db)
                    self.assertEqual(con.execute("SELECT count(*) FROM results").fetchone()[0], 48)
                    con.close()
                    self.assertEqual(target.checksum(db), target.checksum(clean))


if __name__ == "__main__":
    unittest.main()
