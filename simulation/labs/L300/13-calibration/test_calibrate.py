import unittest

import numpy as np

import calibrate as cal


class TestCalibration(unittest.TestCase):
    def test_gauss_newton_recovers_known_parameters_without_noise(self):
        t = cal.T_HOURS
        y = cal.one_exp(t, [12.0, 8.0, 2.5])
        p, _ = cal.gauss_newton(cal.one_exp, t, y, [10.0, 5.0, 1.0])
        np.testing.assert_allclose(p, [12.0, 8.0, 2.5], rtol=1e-6)

    def test_data_is_seeded(self):
        np.testing.assert_array_equal(cal.observed(), cal.observed())
        self.assertEqual(cal.CAL.sum(), 49)

    def test_more_parameters_always_fit_the_calibration_data_better(self):
        _, same, _ = cal.select(cal.observed())
        self.assertLess(same["poly-6 (7 p)"], same["two-exp (5 p)"])
        self.assertLess(same["two-exp (5 p)"], same["one-exp (3 p)"])

    def test_true_model_scores_near_the_noise_level_on_holdout(self):
        y = cal.observed()
        hold = cal.scores(cal.candidates(cal.T_HOURS[cal.CAL], y[cal.CAL]), y, ~cal.CAL)
        self.assertLess(hold["two-exp (5 p)"], 1.3 * cal.NOISE)


class TestFailureLab(unittest.TestCase):
    """Fault: validating on the calibration data picks the wrong model. The fix is checked by test_build_task.py."""

    def test_fault_same_data_picks_the_overfitted_model(self):
        y = cal.observed()
        models = cal.candidates(cal.T_HOURS[cal.CAL], y[cal.CAL])
        same, hold = cal.scores(models, y, cal.CAL), cal.scores(models, y, ~cal.CAL)
        best = min(same, key=same.get)
        self.assertEqual(best, "poly-6 (7 p)")
        self.assertGreater(hold[best], 5.0)  # degrees C: useless for the 12 h forecast


try:
    import scipy  # noqa: F401
except ImportError:  # SciPy runs in CI only
    scipy = None


@unittest.skipIf(scipy is None, "scipy not installed (pending-ci)")
class TestSciPyEquivalent(unittest.TestCase):
    def test_least_squares_finds_the_same_one_exp_parameters(self):
        import calibrate_scipy
        yc = cal.observed()[cal.CAL]
        p0 = [yc[-1], yc[0] - yc[-1], 2.0]
        ours, _ = cal.gauss_newton(cal.one_exp, cal.T_HOURS[cal.CAL], yc, p0)
        np.testing.assert_allclose(calibrate_scipy.fit(cal.one_exp, p0), ours, rtol=1e-4)


if __name__ == "__main__":
    unittest.main()
