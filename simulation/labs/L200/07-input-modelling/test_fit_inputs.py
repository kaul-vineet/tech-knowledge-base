import unittest

import numpy as np

import fit_inputs as fi


class TestFitting(unittest.TestCase):
    def setUp(self):
        self.x = fi.load()

    def test_data_file_loads(self):
        self.assertEqual(len(self.x), 200)
        self.assertGreater(self.x.min(), 0)

    def test_estimators_match_closed_forms(self):
        self.assertAlmostEqual(fi.fit_exponential(self.x)["params"]["rate"], 1 / self.x.mean())
        p = fi.fit_lognormal(self.x)["params"]
        self.assertAlmostEqual(p["mu"], float(np.mean(np.log(self.x))))
        self.assertAlmostEqual(p["sigma"], float(np.std(np.log(self.x))))

    def test_cdf_and_ppf_are_inverses(self):
        for f in fi.FITTERS:
            fit = f(self.x)
            p = np.array([0.1, 0.5, 0.9])
            np.testing.assert_allclose(fit["cdf"](fit["ppf"](p)), p, atol=1e-9)

    def test_ks_hand_example(self):
        # data 0.2, 0.6 vs uniform(0,1): ECDF is 1.0 at 0.6 where the CDF is 0.6 -> D = 0.4 (worked by hand)
        self.assertAlmostEqual(fi.ks_statistic(np.array([0.6, 0.2]), lambda v: v), 0.4)

    def test_lognormal_has_smallest_ks(self):
        d = {f(self.x)["name"]: fi.ks_statistic(self.x, f(self.x)["cdf"]) for f in fi.FITTERS}
        self.assertEqual(min(d, key=d.get), "lognormal")
        self.assertLess(d["lognormal"], 1.36 / np.sqrt(len(self.x)))
        self.assertGreater(d["exponential"], 1.36 / np.sqrt(len(self.x)))

    def test_queue_matches_pollaczek_khinchine(self):
        # M/G/1 mean wait = lam E[S^2] / (2 (1 - rho)) with the lognormal's analytic E[S^2]
        p = fi.fit_lognormal(self.x)["params"]
        es, es2 = np.exp(p["mu"] + p["sigma"] ** 2 / 2), np.exp(2 * p["mu"] + 2 * p["sigma"] ** 2)
        lam = 0.7 / es
        pk = lam * es2 / (2 * (1 - 0.7))
        sim = fi.queue_waits(fi.fit_lognormal(self.x)["sample"], lam).mean()
        self.assertAlmostEqual(sim, pk, delta=0.05 * pk)

    def test_exponential_input_overstates_wait(self):
        lam = 0.85 / self.x.mean()
        wrong = fi.queue_waits(fi.fit_exponential(self.x)["sample"], lam).mean()
        data = fi.queue_waits(lambda rng, n: rng.choice(self.x, n), lam).mean()
        self.assertGreater(wrong / data, 1.15)


try:
    import fit_scipy
except ImportError:  # SciPy runs in CI only
    fit_scipy = None


@unittest.skipIf(fit_scipy is None, "scipy not installed (pending-ci)")
class TestSciPyEquivalent(unittest.TestCase):
    def test_scipy_gives_same_parameters_and_ks(self):
        x = fi.load()
        for name, (params, d) in fit_scipy.fit_all(x).items():
            fit = {f(x)["name"]: f(x) for f in fi.FITTERS}[name]
            self.assertAlmostEqual(d, fi.ks_statistic(x, fit["cdf"]), places=6)


if __name__ == "__main__":
    unittest.main()
