"""buildTask check (lesson 12): antithetic_loop() must pair f(u) with f(1-u) of the SAME u.

By default this checks solution/variance_reduction.py. To check your edited variance_reduction.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 2 of 3 tests fail; after your fix all 3 pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import variance_reduction as reference

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("variance_reduction.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/variance_reduction.py")
spec = importlib.util.spec_from_file_location("variance_reduction_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)

N = 20_000


class TestOneStreamPerPair(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = target.antithetic_loop(N)

    def test_pairs_anti_correlate(self):
        self.assertLess(self.r["rho"], -0.25)

    def test_variance_ratio_like_the_vectorised_version(self):
        self.assertGreater(reference.plain(N)["var_per_eval"] / self.r["var_per_eval"], 1.3)

    def test_still_unbiased(self):
        self.assertLess(abs(self.r["mean"] - reference.exact_overtime()), 3 * self.r["se"])


if __name__ == "__main__":
    unittest.main()
