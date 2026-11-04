import unittest

import numpy as np

import cosmo_bayes as cb


class TestFoundationsIII(unittest.TestCase):
    def test_every_check_passes(self):
        for name, fn in cb.CHECKS.items():
            with self.subTest(check=name):
                self.assertTrue(fn()[1])

    def test_einstein_de_sitter_limit(self):
        # Om -> 1 makes the closed form tend to 2/(3 H0)
        self.assertAlmostEqual(cb.age_closed_form(67.4, 0.999999) / cb.hubble_time_gyr(67.4), 2 / 3, places=5)

    def test_detailed_balance_implies_stationarity(self):
        pi = np.array([0.2, 0.5, 0.3])
        q = np.full((3, 3), 0.5) - 0.5 * np.eye(3)
        k = cb.metropolis_matrix(pi, q)
        np.testing.assert_allclose(pi @ k, pi, atol=1e-15)

    def test_prior_pulls_posterior(self):
        d, v, s = cb.synthetic_hubble()
        flat, _ = cb.posterior_closed_form(d, v, s)
        tight, _ = cb.posterior_closed_form(d, v, s, prior=(60.0, 0.1))
        self.assertLess(abs(tight - 60.0), abs(flat - 60.0))


if __name__ == "__main__":
    unittest.main()
