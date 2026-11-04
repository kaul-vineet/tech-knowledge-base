import unittest

import numpy as np

import sensitivity as sa

# Analytic variance decomposition of the energy model (inputs independent and uniform):
V_T, V_INT, V_OCC, V_LIGHT = 16 ** 2 * 12, 24 ** 2 * (1 / 12) * 12, 1.0 * 40 ** 2 / 12, 9 * 4 ** 2 / 12
V = V_T + V_INT + V_OCC + V_LIGHT
S1_TRUE = np.array([V_T, V_OCC, 0.0, V_LIGHT]) / V
ST_TRUE = np.array([V_T + V_INT, V_OCC, V_INT, V_LIGHT]) / V


class TestMethods(unittest.TestCase):
    def test_sobol_estimates_match_the_analytic_indices(self):
        s1, st = sa.sobol()
        np.testing.assert_allclose(s1, S1_TRUE, atol=0.02)
        np.testing.assert_allclose(st, ST_TRUE, atol=0.02)

    def test_sobol_on_an_additive_model_has_no_interaction(self):
        s1, st = sa.sobol(f=lambda x: 2 * x[:, 0] + x[:, 1])
        np.testing.assert_allclose(s1, st, atol=0.02)

    def test_morris_detects_the_window_and_flags_the_interaction(self):
        mu_star, sigma = sa.morris()
        self.assertGreater(mu_star[2], mu_star[1])  # window_open above occupants
        self.assertGreater(sigma[2], 50)  # large sigma = effect depends on other inputs
        self.assertAlmostEqual(sigma[1], 0.0, places=9)  # occupants: purely additive, same effect everywhere

    def test_oat_is_blind_to_the_window(self):
        self.assertEqual(sa.oat()[2], 0.0)


class TestFailureLab(unittest.TestCase):
    """Fault: screening by OAT freezes an input that matters. Your fix to screen() is checked by test_build_task.py."""

    def test_fault_oat_screening_loses_variance(self):
        keep = sa.ranking(sa.table(), "oat_swing")[:2]  # what the shipped screen() does
        self.assertNotIn("window_open", keep)
        self.assertLess(sa.variance_kept(keep), 0.88)

    def test_total_order_ranking_puts_the_window_second(self):
        self.assertEqual(sa.ranking(sa.table(), "ST")[:2], ["outdoor_C", "window_open"])


try:
    import SALib  # noqa: F401
except ImportError:  # SALib runs in CI only
    SALib = None


@unittest.skipIf(SALib is None, "SALib not installed (pending-ci)")
class TestSALibEquivalent(unittest.TestCase):
    def test_salib_total_order_matches_ours(self):
        import sensitivity_salib
        _, st = sa.sobol()
        np.testing.assert_allclose(sensitivity_salib.sobol_indices()["ST"], st, atol=0.03)

    def test_salib_morris_ranks_window_above_occupants(self):
        import sensitivity_salib
        mu_star = sensitivity_salib.morris_indices()["mu_star"]
        self.assertGreater(mu_star[2], mu_star[1])


if __name__ == "__main__":
    unittest.main()
