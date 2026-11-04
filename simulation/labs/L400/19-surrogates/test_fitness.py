"""Fitness function (lesson 19 ADR 0001): keeps "GP-lite emulator behind an envelope guard" true.

Fails the build if: the GP's holdout RMSE exceeds 0.06 min (about 2x the simulation's own noise, 0.033);
its 95% intervals cover fewer than 80% of holdout runs; an in-envelope what-if is more than 10% off the exact
Erlang C value; or ANY out-of-envelope what-if is answered by the surrogate.
Default target: solution/surrogate.py; BUILD_TARGET=mine checks your surrogate.py (the shipped file fails 1 of 3).
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("surrogate.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/surrogate.py")
spec = importlib.util.spec_from_file_location("surrogate_fitness", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestSurrogateFitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        X, y, cls.Xh, cls.yh = target.design()
        cls.gp = staticmethod(target.fit_gp(X, y))  # staticmethod: a stored function must not bind to self

    def test_holdout_accuracy_and_calibrated_uncertainty(self):
        mean, sd = self.gp(self.Xh)
        self.assertLessEqual(np.sqrt(np.mean((mean - self.yh) ** 2)), 0.06)
        self.assertGreaterEqual(np.mean(np.abs(mean - self.yh) <= 1.96 * sd), 0.80)

    def test_in_envelope_what_ifs_are_close_to_exact(self):
        for lam, mu in ((1.6, 1.0), (2.0, 1.0), (2.3, 1.05)):
            exact = target.mmc_queue.erlang_c(3, lam, mu)["Wq"]
            r = target.what_if(self.gp, lam, mu)
            self.assertEqual(r["source"], "surrogate")
            self.assertLess(abs(r["Wq"] - exact) / exact, 0.10)

    def test_no_out_of_envelope_answer_comes_from_the_surrogate(self):
        for lam, mu in ((2.42, 1.0), (2.7, 0.95), (1.2, 1.0), (2.0, 0.9)):
            self.assertNotEqual(target.what_if(self.gp, lam, mu)["source"], "surrogate")


if __name__ == "__main__":
    unittest.main()
