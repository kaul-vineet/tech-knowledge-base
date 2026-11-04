"""buildTask check (lesson 7): the shifted-exponential candidate. Point SOLUTION at your own file to test your version."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "solution"))
import fit_inputs as fi  # noqa: E402
import shifted_exponential as SOLUTION  # noqa: E402


class TestShiftedExponential(unittest.TestCase):
    def setUp(self):
        self.x = fi.load()
        self.fit = SOLUTION.fit_shifted_exponential(self.x)

    def test_parameters_are_the_mles(self):
        self.assertAlmostEqual(self.fit["params"]["loc"], self.x.min())
        self.assertAlmostEqual(self.fit["params"]["rate"], 1 / (self.x.mean() - self.x.min()))

    def test_cdf_is_zero_below_the_shift_and_inverts_ppf(self):
        self.assertEqual(float(self.fit["cdf"](np.array(self.x.min() - 0.1))), 0.0)
        p = np.array([0.1, 0.5, 0.9])
        np.testing.assert_allclose(self.fit["cdf"](self.fit["ppf"](p)), p, atol=1e-12)

    def test_samples_never_below_shift(self):
        self.assertGreaterEqual(self.fit["sample"](np.random.default_rng(1), 10_000).min(), self.x.min())

    def test_ranks_between_exponential_and_lognormal(self):
        d = {f(self.x)["name"]: fi.ks_statistic(self.x, f(self.x)["cdf"]) for f in SOLUTION.FITTERS}
        self.assertLess(d["shifted exponential"], d["exponential"])
        self.assertGreater(d["shifted exponential"], d["lognormal"])


if __name__ == "__main__":
    unittest.main()
