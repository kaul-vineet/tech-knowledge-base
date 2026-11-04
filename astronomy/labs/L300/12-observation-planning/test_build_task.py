"""buildTask check (lesson 12): airmass() must never let a star below the horizon pass 'airmass <= 2.0'.

By default this checks solution/plan.py. To check your edited plan.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 2 of 3 tests fail (15 subtest failures); after your fix all 3 pass.
"""
import importlib.util
import os
import unittest
from datetime import timedelta
from pathlib import Path

import numpy as np

import ephem

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("plan.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/plan.py")
spec = importlib.util.spec_from_file_location("plan_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestHorizonSafeAirmass(unittest.TestCase):
    def test_below_horizon_never_passes_the_limit(self):
        for alt in (-60.0, -10.0, -0.5, 0.0):
            with self.subTest(alt=alt):
                self.assertFalse(float(target.airmass(alt)) <= target.MAX_AIRMASS)

    def test_airmass_is_at_least_one_above_horizon(self):
        x = np.array([float(target.airmass(a)) for a in (1.0, 10.0, 30.0, 60.0, 90.0)])
        self.assertTrue(np.all(x >= 1.0 - 1e-9) and np.all(np.diff(x) < 0))

    def test_every_scheduled_block_is_really_above_30_degrees(self):
        """Re-check start, middle and end with ephem.py directly, independent of the file under test."""
        rows, _ = target.schedule()
        self.assertGreaterEqual(len(rows), 3)
        for r in rows:
            h, m = map(int, r["start"].split(":"))
            start = target.NIGHT.replace(hour=h, minute=m) + timedelta(days=1 if h < 12 else 0)  # after midnight
            for minutes in (0, 30, 60):
                t = start + timedelta(minutes=minutes)
                jd = ephem.julian_date(t)
                alt, _ = ephem.altaz(*target.TARGETS[r["target"]], target.SITE["lat"], target.SITE["lon"], jd)
                with self.subTest(target=r["target"], minutes=minutes):
                    self.assertGreaterEqual(float(alt), 29.9)


if __name__ == "__main__":
    unittest.main()
