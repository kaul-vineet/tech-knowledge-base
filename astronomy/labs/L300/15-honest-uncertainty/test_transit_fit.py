"""Unit tests + fault reproduction for lesson 15 (numpy only; the emcee test is skipped locally)."""
import unittest

import numpy as np

import mcmc
import transit_fit as tf


class TestModelAndFit(unittest.TestCase):
    def test_trapezoid_shape(self):
        f = tf.model(tf.TRUE, np.array([0.12, 0.12 + 0.9, 3.0]))
        np.testing.assert_allclose(f, [0.99, 0.99, 1.0])
        self.assertAlmostEqual(float(tf.model(tf.TRUE, np.array([0.12 + 1.25 - 0.15]))[0]), 0.995)  # mid-ingress

    def test_lm_recovers_noiseless_truth(self):
        np.testing.assert_allclose(tf.fit_lm(tf.model(tf.TRUE)), tf.TRUE, atol=1e-6)

    def test_autocorrelation_time_of_ar1(self):
        rng, rho = np.random.default_rng(0), 0.9
        x = np.zeros(200_000)
        for i in range(1, x.size):
            x[i] = rho * x[i - 1] + rng.normal()
        self.assertAlmostEqual(mcmc.autocorr_time(x) / ((1 + rho) / (1 - rho)), 1.0, delta=0.15)


class TestFailureLab(unittest.TestCase):
    """Shipped uncertainty() trusts flux_err = 0.0010 while the scatter is 0.0020: error bars 2x too small."""

    def test_shipped_coverage_is_far_below_68_percent(self):
        np.testing.assert_allclose(tf.coverage(), [0.36, 0.335, 0.275, 0.22])

    def test_reduced_chi2_reveals_it(self):
        y = tf.make_data()
        p = tf.fit_lm(y)
        self.assertAlmostEqual(float(np.sum(((y - tf.model(p)) / tf.SIGMA_REPORTED) ** 2) / (y.size - 4)), 4.13, places=2)


class TestMcmc(unittest.TestCase):
    def test_noise_scale_and_acceptance(self):
        post, acc, tau = mcmc.run(tf.make_data())
        self.assertAlmostEqual(float(np.exp(np.median(post[:, 4]))), 2.0, delta=0.15)
        self.assertTrue(0.2 < acc < 0.5)
        self.assertGreater(len(post) / tau, 50)


class TestEmceeEquivalent(unittest.TestCase):
    def test_emcee_agrees_with_metropolis(self):
        try:
            import fit_emcee
        except ImportError:
            self.skipTest("emcee not installed (pending-ci)")
        flat, _ = fit_emcee.run(tf.make_data())
        self.assertAlmostEqual(float(np.median(flat[:, 0])), 0.1555, delta=0.004)
        self.assertAlmostEqual(float(np.exp(np.median(flat[:, 4]))), 2.0, delta=0.15)


if __name__ == "__main__":
    unittest.main()
