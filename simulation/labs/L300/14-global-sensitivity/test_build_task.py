"""buildTask check (lesson 14): screen() must keep the inputs that carry the variance, interactions included.

By default this checks solution/sensitivity.py. To check your edited sensitivity.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 2 of 2 tests fail; after your fix both pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import sensitivity as reference

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("sensitivity.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/sensitivity.py")
spec = importlib.util.spec_from_file_location("sensitivity_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestScreening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keep = target.screen(reference.table())

    def test_keeps_the_window(self):
        self.assertEqual(self.keep, ["outdoor_C", "window_open"])

    def test_reduced_model_keeps_over_95_percent_of_the_variance(self):
        self.assertGreater(reference.variance_kept(self.keep), 0.95)  # judged by the lab's own check, not the target's


if __name__ == "__main__":
    unittest.main()
