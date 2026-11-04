"""buildTask check (lesson 15): the default communication step must keep the coupled loop stable.

By default this checks solution/cosim.py. To check your edited cosim.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 2 of 2 tests fail; after your fix both pass.
"""
import importlib.util
import math
import os
import unittest
from pathlib import Path

import cosim as reference

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("cosim.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/cosim.py")
spec = importlib.util.spec_from_file_location("cosim_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestDefaultStep(unittest.TestCase):
    def test_default_step_is_below_the_stability_bound(self):
        self.assertLess(target.COMM_STEP_S, 3600 * math.log(12 / 11))  # tau ln(K/(K-1)) = 313 s

    def test_default_run_settles(self):
        m = reference.metrics(target.run())
        self.assertLess(m["last_hour_swing_C"], 0.2)
        self.assertLessEqual(m["heater_flips"], 2)


if __name__ == "__main__":
    unittest.main()
