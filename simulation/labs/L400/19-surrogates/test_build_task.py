"""buildTask check (lesson 19): what_if() must refuse to extrapolate and answer from the simulation instead.

By default this checks solution/surrogate.py. To check your edited surrogate.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 2 of 3 tests fail; after your fix all 3 pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("surrogate.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/surrogate.py")
spec = importlib.util.spec_from_file_location("surrogate_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestEnvelopeGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        X, y, _, _ = target.design()
        cls.gp = staticmethod(target.fit_gp(X, y))  # staticmethod: a stored function must not bind to self
        cls.poly = staticmethod(target.fit_poly(X, y))

    def test_inside_the_envelope_the_surrogate_answers(self):
        self.assertEqual(target.what_if(self.gp, 2.0, 1.0)["source"], "surrogate")

    def test_just_outside_the_box_is_not_answered_by_the_surrogate(self):
        for model in (self.gp, self.poly):  # arrivals +10% from 2.2 -> 2.42 > 2.4: outside, even if the GP is calm
            self.assertNotEqual(target.what_if(model, 2.42, 1.0)["source"], "surrogate")

    def test_far_outside_the_answer_is_within_20_percent_of_exact(self):
        r = target.what_if(self.poly, 2.7, 0.95)
        self.assertLess(abs(r["Wq"] - 6.015) / 6.015, 0.20)


if __name__ == "__main__":
    unittest.main()
