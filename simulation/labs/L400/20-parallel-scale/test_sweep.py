import sqlite3
import tempfile
import unittest
from pathlib import Path

import numpy as np

import scaling
import storage_options
import sweep


class SmallSweep(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()  # never a fixed path: parallel test runs must not collide
        self.dir = Path(self.tmp.name)
        self.saved, sweep.REPS = sweep.REPS, 3  # 36 tasks keep the tests fast

    def tearDown(self):
        sweep.REPS = self.saved
        self.tmp.cleanup()


class TestStorage(SmallSweep):
    def test_resume_adds_only_missing_rows(self):
        db = self.dir / "s.db"
        with self.assertRaises(sweep.Crash):
            sweep.run_sweep(db, workers=1, crash_after=10)
        self.assertEqual(len(sweep.pending_tasks(sqlite3.connect(db))), 36 - 8)  # one batch of 8 was committed
        self.assertEqual(sweep.run_sweep(db, workers=1), 28)
        self.assertEqual(sweep.run_sweep(db, workers=1), 0)  # nothing left: a re-run is a no-op

    def test_csv_export_round_trips(self):
        db = self.dir / "s.db"
        sweep.run_sweep(db, workers=1)
        sweep.export_csv(db, self.dir / "s.csv")
        lines = (self.dir / "s.csv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 37)

    def test_crash_evidence(self):
        self.assertEqual(storage_options.torn_csv(self.dir / "t.csv"), (1, 2))
        self.assertEqual(storage_options.interrupted_sqlite(self.dir / "t.db"), (16, 16))


class TestScalingMaths(unittest.TestCase):
    def test_amdahl_fit_recovers_the_serial_fraction(self):
        n = np.array([1, 2, 4, 8])
        self.assertAlmostEqual(scaling.amdahl_serial_fraction(n, 1 / (0.2 + 0.8 / n)), 0.2, places=9)


class TestFailureLab(SmallSweep):
    """Fault: seeded() numbers streams by position in the PENDING list. Your fix is checked by test_build_task.py."""

    def test_fault_resumed_sweep_differs_from_clean_sweep(self):
        clean, resumed = self.dir / "c.db", self.dir / "r.db"
        sweep.run_sweep(clean, workers=1)
        with self.assertRaises(sweep.Crash):
            sweep.run_sweep(resumed, workers=1, crash_after=10)
        sweep.run_sweep(resumed, workers=1)
        self.assertNotEqual(sweep.checksum(clean), sweep.checksum(resumed))


try:
    import pyarrow  # noqa: F401  (CI only: pyarrow 26.0.0)
except ImportError:
    pyarrow = None


@unittest.skipIf(pyarrow is None, "pyarrow not installed (pending-ci)")
class TestParquetExport(SmallSweep):
    def test_round_trip(self):
        import to_parquet
        db = self.dir / "s.db"
        sweep.run_sweep(db, workers=1)
        rows, same, size = to_parquet.export(db, self.dir / "s.parquet")
        self.assertEqual((rows, same), (36, True))
        self.assertGreater(size, 0)


if __name__ == "__main__":
    unittest.main()
