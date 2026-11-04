import unittest

import numpy as np

import surrogate as sg

mmc_queue = sg.mmc_queue  # the L200 lesson 8 model, put on sys.path by surrogate.py


class TestDesignAndFits(unittest.TestCase):
    def test_latin_hypercube_has_one_point_per_stratum(self):
        X = sg.latin_hypercube(10, np.random.default_rng(0))
        for j in range(2):
            strata = np.floor(sg.scale(X)[:, j] * 10).astype(int)
            self.assertEqual(sorted(strata.tolist()), list(range(10)))

    def test_polynomial_is_exact_on_a_quadratic(self):
        X = sg.latin_hypercube(12, np.random.default_rng(1))
        f = lambda Z: 1 + 2 * Z[:, 0] - Z[:, 1] + 0.5 * Z[:, 0] * Z[:, 1]
        pred, _ = sg.fit_poly(X, f(X))(X[:3])
        np.testing.assert_allclose(pred, f(X[:3]), atol=1e-9)

    def test_gp_uncertainty_grows_away_from_data(self):
        X = sg.latin_hypercube(15, np.random.default_rng(2))
        gp = sg.fit_gp(X, np.sin(3 * sg.scale(X)[:, 0]))
        _, sd_in = gp(X[:1])
        _, sd_out = gp(np.array([[4.0, 1.5]]))
        self.assertGreater(sd_out[0], 3 * sd_in[0])


class TestFailureLab(unittest.TestCase):
    """Fault: the shipped what_if() extrapolates. Your fix is checked by test_build_task.py."""

    @classmethod
    def setUpClass(cls):
        X, y, _, _ = sg.design()
        cls.models = sg.fit_all(X, y)

    def test_fault_surrogates_extrapolate_far_too_low(self):
        exact = mmc_queue.erlang_c(3, 2.7, 0.95)["Wq"]  # 6.015 min
        for name, model in self.models.items():
            with self.subTest(surrogate=name):
                r = sg.what_if(model, 2.7, 0.95)
                self.assertEqual(r["source"], "surrogate")
                self.assertLess(r["Wq"], exact / 2)


if __name__ == "__main__":
    unittest.main()
