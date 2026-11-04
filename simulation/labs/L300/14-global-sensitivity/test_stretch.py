"""Stretch check (lesson 14): bootstrap CIs and an honest ranking.

By default this checks solution/robust_ranking.py. To check your own robust_ranking.py (in this folder) instead:
    BUILD_TARGET=mine python -m unittest test_stretch -v        (PowerShell: $env:BUILD_TARGET = "mine")
"""
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"))
import robust_ranking as SOLUTION  # noqa: E402
from test_sensitivity import ST_TRUE  # noqa: E402


class TestRobustRanking(unittest.TestCase):
    def test_intervals_cover_the_analytic_values(self):
        _, lo, hi = SOLUTION.st_with_ci(8192)
        for i in range(len(ST_TRUE)):
            self.assertLessEqual(lo[i], ST_TRUE[i] + 0.005)
            self.assertGreaterEqual(hi[i], ST_TRUE[i] - 0.005)

    def test_enough_runs_give_a_strict_order(self):
        self.assertEqual(SOLUTION.robust_ranking(*SOLUTION.st_with_ci(8192)),
                         "outdoor_C > window_open > occupants > lights_h")

    def test_too_few_runs_report_a_tie_instead_of_an_order(self):
        self.assertIn("~", SOLUTION.robust_ranking(*SOLUTION.st_with_ci(32)))


if __name__ == "__main__":
    unittest.main()
