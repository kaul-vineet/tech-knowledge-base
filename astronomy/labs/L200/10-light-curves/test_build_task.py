"""buildTask check (lesson 10): bootstrap_fap() estimates the false-alarm probability by shuffling magnitudes.

By default this checks solution/periods.py. To check your edited periods.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfinished) file all 3 tests fail (NotImplementedError); after your change all 3 pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("periods.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/periods.py")
spec = importlib.util.spec_from_file_location("periods_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestBootstrapFap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = target.sample_times()
        cls.f = target.frequency_grid(cls.t, oversample=2)  # coarse grid keeps the test fast

    def test_real_signal_has_tiny_fap(self):
        self.assertLessEqual(target.bootstrap_fap(self.t, target.variable_star(self.t), self.f, n=30), 1 / 31 + 1e-12)

    def test_pure_noise_is_not_significant(self):
        noise = 12 + np.random.default_rng(5).normal(0, 0.02, self.t.size)
        self.assertGreater(target.bootstrap_fap(self.t, noise, self.f, n=30), 0.05)

    def test_reproducible_with_seed(self):
        y = 12 + np.random.default_rng(6).normal(0, 0.02, self.t.size)
        self.assertEqual(target.bootstrap_fap(self.t, y, self.f, n=20, seed=1),
                         target.bootstrap_fap(self.t, y, self.f, n=20, seed=1))


if __name__ == "__main__":
    unittest.main()
