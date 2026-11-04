import importlib.util
import unittest

import numpy as np

import periods as pr


class TestLombScargle(unittest.TestCase):
    def test_noise_free_sine_has_power_near_one_at_its_frequency(self):
        t = np.sort(np.random.default_rng(3).uniform(0, 20, 300))
        y = 0.3 * np.sin(2 * np.pi * t / 2.5 + 0.7)
        p = pr.lomb_scargle(t, y, np.array([1 / 2.5, 1 / 1.7]))
        self.assertGreater(p[0], 0.99)  # not exactly 1: the classical form subtracts the sample mean
        self.assertLess(p[1], 0.2)

    def test_power_is_between_zero_and_one(self):
        t = pr.sample_times()
        p = pr.lomb_scargle(t, pr.variable_star(t), pr.frequency_grid(t))
        self.assertTrue(((p >= 0) & (p <= 1 + 1e-12)).all())


class TestStars(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = pr.sample_times()
        cls.var = pr.analyse(cls.t, pr.variable_star(cls.t))
        cls.tra = pr.analyse(cls.t, pr.transit_star(cls.t))

    def test_sampling(self):
        self.assertEqual(self.t.size, 1104)

    def test_variable_period_recovered(self):
        self.assertLess(abs(self.var["best_period_days"] - pr.P_VAR) / pr.P_VAR, 0.001)
        self.assertAlmostEqual(self.var["second_period_days"], 1 / (1 / pr.P_VAR - 1), delta=0.01)  # 1-day alias

    def test_lomb_scargle_misses_the_transit(self):
        self.assertLess(self.tra["power"], 0.1)
        self.assertGreater(abs(self.tra["best_period_days"] - pr.P_TRANSIT), 0.5)
        self.assertGreater(self.tra["skew"], 0.5)  # but the dips show up as one-sided skew


@unittest.skipUnless(importlib.util.find_spec("astropy"), "astropy not installed (runs in CI)")
class TestAstropyEquivalent(unittest.TestCase):
    def test_astropy_lombscargle_matches(self):
        import periods_astropy
        self.assertLess(periods_astropy.compare(), 1e-8)


if __name__ == "__main__":
    unittest.main()
