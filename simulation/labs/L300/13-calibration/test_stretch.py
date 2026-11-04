"""Stretch check (lesson 13): identifiability report.

By default this checks solution/param_report.py. To check your own param_report.py (in this folder) instead:
    BUILD_TARGET=mine python -m unittest test_stretch -v        (PowerShell: $env:BUILD_TARGET = "mine")
"""
import os
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"))
import param_report as SOLUTION  # noqa: E402
import calibrate as cal  # noqa: E402

Y = cal.observed()
T, YC = cal.T_HOURS[cal.CAL], Y[cal.CAL]
NAMES5 = ["T_inf", "A", "tau_air", "B", "tau_wall"]


class TestParamReport(unittest.TestCase):
    def test_simple_model_is_identifiable(self):
        rep = SOLUTION.param_report(cal.one_exp, T, YC, [YC[-1], YC[0] - YC[-1], 2.0], ["T_inf", "A", "tau"])
        self.assertTrue(rep["identifiable"])

    def test_two_exp_is_flagged_and_the_culprit_pair_named(self):
        rep = SOLUTION.param_report(cal.two_exp, T, YC, [YC[-1], 5, 1, 5, 6], NAMES5)
        self.assertFalse(rep["identifiable"])
        self.assertEqual(set(rep["worst_pair"][:2]), {"T_inf", "tau_wall"})
        self.assertLess(rep["worst_pair"][2], -0.98)

    def test_measuring_t_inf_makes_it_identifiable(self):
        fixed = lambda t, q: cal.two_exp(t, np.r_[12.0, q])
        rep = SOLUTION.param_report(fixed, T, YC, [5, 1, 5, 6], NAMES5[1:])
        self.assertTrue(rep["identifiable"])


if __name__ == "__main__":
    unittest.main()
