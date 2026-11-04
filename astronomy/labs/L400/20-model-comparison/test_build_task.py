"""buildTask check (lesson 20): select() must penalise parameters (BIC), not just minimise chi^2.

By default this checks solution/compare.py. To check your edited compare.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v      (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file both build-task tests fail; after your fix they pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import galaxy as g

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("compare.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/compare.py")
spec = importlib.util.spec_from_file_location("compare_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestPenalisedSelection(unittest.TestCase):
    def test_published_curve(self):
        v, err = g.observed()
        self.assertEqual(target.select(g.R, v, err)[0], "disk + cored halo")

    def test_ten_more_galaxies(self):
        for seed in range(30, 40):
            v, err = g.observed(seed=seed)
            with self.subTest(seed=seed):
                self.assertNotEqual(target.select(g.R, v, err)[0], "disk + halo + wiggles")


if __name__ == "__main__":
    unittest.main()
