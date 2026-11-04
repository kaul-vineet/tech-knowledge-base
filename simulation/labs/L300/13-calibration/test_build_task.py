"""buildTask check (lesson 13): select() must choose the model that forecasts data it was not fitted to.

By default this checks solution/calibrate.py. To check your edited calibrate.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 2 of 2 tests fail; after your fix both pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import calibrate as reference

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("calibrate.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/calibrate.py")
spec = importlib.util.spec_from_file_location("calibrate_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


def holdout_rmse(y, name):
    """Judge the pick independently of the file under test: RMSE on the unseen 8-12 h."""
    models = reference.candidates(reference.T_HOURS[reference.CAL], y[reference.CAL])
    return reference.scores(models, y, ~reference.CAL)[name]


class TestHoldoutSelection(unittest.TestCase):
    def test_picks_a_model_that_forecasts(self):
        y = reference.observed()
        best = target.select(y)[0]
        self.assertEqual(best, "two-exp (5 p)")
        self.assertLess(holdout_rmse(y, best), 0.2)

    def test_never_picks_the_polynomial_for_other_noise_seeds(self):
        for seed in range(20, 30):
            with self.subTest(seed=seed):
                self.assertNotEqual(target.select(reference.observed(seed))[0], "poly-6 (7 p)")


if __name__ == "__main__":
    unittest.main()
