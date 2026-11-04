"""buildTask check (lesson 15): error bars must be honest - +/-1 sigma should contain the truth ~68% of the time.

By default this checks solution/transit_fit.py. To check your edited transit_fit.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 2 of 2 tests fail; after your fix both pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("transit_fit.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/transit_fit.py")
spec = importlib.util.spec_from_file_location("transit_fit_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestHonestErrors(unittest.TestCase):
    def test_coverage_near_68_percent(self):
        cov = target.coverage()
        self.assertTrue(0.60 <= cov[0] <= 0.78, cov)  # t0
        self.assertTrue(0.60 <= cov[1] <= 0.78, cov)  # depth
        self.assertTrue((cov >= 0.5).all(), cov)  # T14, T12: nonlinear, linearised errors still under-cover a bit

    def test_formal_error_agrees_with_bootstrap(self):
        y = target.make_data()
        p = target.fit_lm(y)
        ratio = target.uncertainty(y, p)[:2] / target.bootstrap(y, p, n=100)[:2]
        self.assertTrue(((ratio > 0.75) & (ratio < 1.33)).all(), ratio)


if __name__ == "__main__":
    unittest.main()
