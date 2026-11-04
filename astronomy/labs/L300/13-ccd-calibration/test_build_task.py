"""buildTask check (lesson 13): the master flat must describe the pixel response, not the bias pedestal.

By default this checks solution/calibrate.py. To check your edited calibrate.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 3 of 3 tests fail; after your fix all pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

import camera

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("calibrate.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/calibrate.py")
spec = importlib.util.spec_from_file_location("calibrate_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestFlatField(unittest.TestCase):
    def test_constant_star_is_not_variable(self):
        _, s, _ = target.run(log_path=None)
        self.assertFalse(s["variable"])
        self.assertLess(s["robust_rms_percent"], 0.45)

    def test_master_flat_matches_the_true_response(self):
        _, _, flat = target.run(log_path=None)
        truth = camera.response() / np.median(camera.response())
        self.assertLess(float(np.abs(flat / truth - 1).max()), 0.03)

    def test_other_nights_are_not_variable_either(self):
        for seed in range(20, 30):
            with self.subTest(seed=seed):
                self.assertFalse(target.run(seed=seed, log_path=None)[1]["variable"])


if __name__ == "__main__":
    unittest.main()
