"""Stretch check (lesson 12): the pilot-based estimator choice.

By default this checks solution/pick_estimator.py. To check your own pick_estimator.py (in this folder) instead:
    BUILD_TARGET=mine python -m unittest test_stretch -v        (PowerShell: $env:BUILD_TARGET = "mine")
"""
import json
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"))
import pick_estimator as SOLUTION  # noqa: E402
import variance_reduction as vr  # noqa: E402

quiet = lambda line: None


class TestPickEstimator(unittest.TestCase):
    def test_overtime_gets_the_control_variate(self):
        d = SOLUTION.pick_estimator(vr.overtime, vr.N_TASKS, control_mean=vr.N_TASKS * vr.MEAN_H, log=quiet)
        self.assertEqual(d["method"], "control variate")
        self.assertLess(d["rho"], 0)

    def test_antithetic_refused_for_a_symmetric_model(self):
        d = SOLUTION.pick_estimator(SOLUTION.even, 4, log=quiet)
        self.assertNotIn("antithetic", d["ratios"])
        self.assertEqual(d["method"], "plain")

    def test_antithetic_chosen_for_a_monotone_model(self):
        self.assertEqual(SOLUTION.pick_estimator(SOLUTION.monotone, 4, log=quiet)["method"], "antithetic")

    def test_decision_is_logged_as_one_json_line(self):
        lines = []
        SOLUTION.pick_estimator(SOLUTION.even, 4, log=lines.append)
        self.assertEqual(json.loads(lines[0])["event"], "estimator_choice")


if __name__ == "__main__":
    unittest.main()
