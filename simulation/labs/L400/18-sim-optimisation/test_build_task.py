"""buildTask check (lesson 18): pick() must re-run the finalists on FRESH streams from a reserve inside the budget.

By default this checks solution/optimise.py. To check your edited optimise.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file both tests fail; after your fix both pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("optimise.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/optimise.py")
spec = importlib.util.spec_from_file_location("optimise_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestSelection(unittest.TestCase):
    def test_reserve_is_spent_inside_the_same_budget(self):
        self.assertGreater(target.RESERVE, 0)
        self.assertEqual(target.optimise(target.grid_search, 0)["runs"], target.BUDGET)

    def test_report_comes_from_fresh_runs_not_from_the_search(self):
        # A search that got lucky: (25, 70) looked free. The report must be re-measured (~8.5/day), not 0.0.
        data = {(25, 70): [0.0] * 4, (30, 60): [8.0] * 4, (20, 80): [8.2] * 4, (35, 70): [8.4] * 4, (50, 20): [9.0] * 4}
        budget = target.Budget(target.RESERVE, crn_offset=0)
        best, reported = target.pick(budget, data)
        self.assertGreater(reported, 7.0)
        self.assertLess(abs(reported - target.TRUTH[best]["mean"]), 1.0)


if __name__ == "__main__":
    unittest.main()
