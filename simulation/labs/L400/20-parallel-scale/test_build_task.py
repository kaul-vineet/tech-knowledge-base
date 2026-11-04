"""buildTask check (lesson 20): a crashed and resumed sweep must store exactly the rows of a clean sweep.

By default this checks solution/sweep.py. To check your edited sweep.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file both tests fail; after your fix both pass.
"""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

import sweep as reference  # importable by name, so spawned workers can unpickle reference.run_task

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("sweep.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/sweep.py")
spec = importlib.util.spec_from_file_location("sweep_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)
target.run_task, target.REPS = reference.run_task, 3  # same worker code; 36 tasks keep the test fast


class TestResumeIsReproducible(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def resumed(self, name, workers, crash_after):
        db = self.dir / name
        with self.assertRaises(target.Crash):
            target.run_sweep(db, workers=workers, crash_after=crash_after)
        target.run_sweep(db, workers=workers)
        return target.checksum(db)

    def test_resume_on_one_worker_matches_clean_run(self):
        target.run_sweep(self.dir / "clean.db", workers=1)
        self.assertEqual(self.resumed("r1.db", 1, 10), target.checksum(self.dir / "clean.db"))

    def test_resume_on_two_workers_matches_clean_run(self):
        target.run_sweep(self.dir / "clean.db", workers=1)
        self.assertEqual(self.resumed("r2.db", 2, 20), target.checksum(self.dir / "clean.db"))


if __name__ == "__main__":
    unittest.main()
