import math
import unittest

import numpy as np

import variance_reduction as vr

N = 20_000


class TestEstimators(unittest.TestCase):
    def test_exact_formula_matches_a_large_plain_run(self):
        r = vr.plain(400_000, seed=7)
        self.assertLess(abs(r["mean"] - vr.exact_overtime()), 3 * r["se"])

    def test_every_estimator_is_unbiased(self):
        for est in (vr.plain, vr.antithetic, vr.control_variate, vr.antithetic_loop):
            r = est(N)
            with self.subTest(est=est.__name__):
                self.assertLess(abs(r["mean"] - vr.exact_overtime()), 3 * r["se"])

    def test_variance_ratios(self):
        base = vr.plain(N)["var_per_eval"]
        self.assertGreater(base / vr.antithetic(N)["var_per_eval"], 1.3)
        self.assertGreater(base / vr.control_variate(N)["var_per_eval"], 4.0)

    def test_standard_error_from_repeats_agrees_with_formula(self):
        means = [vr.antithetic(2_000, seed=s)["mean"] for s in range(200)]
        self.assertAlmostEqual(np.std(means, ddof=1), vr.antithetic(2_000)["se"], delta=0.25 * vr.antithetic(2_000)["se"])

    def test_crn_shrinks_the_difference_interval(self):
        self.assertLess(vr.crn_difference(N)["se"] * 4, vr.crn_difference(N, crn=False)["se"])


def reseeded_pairs(n, seed=vr.SEED):
    """The fault, kept here so this proof does not change when you fix antithetic_loop() in your file."""
    a, b = np.empty(n // 2), np.empty(n // 2)
    for i in range(n // 2):
        a[i] = vr.overtime(np.random.default_rng([2 * i, seed]).random((1, vr.N_TASKS)))[0][0]
        b[i] = vr.overtime(1.0 - np.random.default_rng([2 * i + 1, seed]).random((1, vr.N_TASKS)))[0][0]
    return vr.summary((a + b) / 2, n) | {"rho": float(np.corrcoef(a, b)[0, 1])}


class TestFailureLab(unittest.TestCase):
    """Fault: reseeding per evaluation loses the gain. The fix is checked by test_build_task.py (BUILD_TARGET=mine)."""

    def test_fault_reseeding_breaks_the_pairs(self):
        r = reseeded_pairs(N)
        self.assertAlmostEqual(r["rho"], 0.0, delta=0.03)  # partners are independent
        self.assertLess(vr.plain(N)["var_per_eval"] / r["var_per_eval"], 1.15)  # no gain


try:
    from scipy import stats
except ImportError:  # SciPy runs in CI only
    stats = None


@unittest.skipIf(stats is None, "scipy not installed (pending-ci)")
class TestSciPyEquivalent(unittest.TestCase):
    def test_exact_overtime_by_numerical_integration(self):
        from scipy import integrate
        T = stats.gamma(a=vr.N_TASKS, scale=vr.MEAN_H)
        val, _ = integrate.quad(lambda t: (t - vr.SHIFT_H) * T.pdf(t), vr.SHIFT_H, math.inf)
        self.assertAlmostEqual(val, vr.exact_overtime(), places=8)


if __name__ == "__main__":
    unittest.main()
