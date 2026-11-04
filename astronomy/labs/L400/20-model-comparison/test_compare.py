"""Unit tests + fault reproduction for lesson 20 (numpy only; the SciPy cross-check is skipped locally)."""
import unittest

import numpy as np

import compare
import galaxy as g


class TestPhysics(unittest.TestCase):
    def test_bessel_values(self):
        x = np.array([1.0])
        # standard tabulated values at x = 1; bessel_scipy.py checks 200 points against SciPy in CI
        np.testing.assert_allclose([g.bessel_i(0, x)[0], g.bessel_i(1, x)[0], g.bessel_k(0, x)[0], g.bessel_k(1, x)[0]],
                                   [1.266065878, 0.565159104, 0.4210244382, 0.6019072302], rtol=1e-7)

    def test_cored_halo_matches_numerical_mass_integral(self):
        r, rho0, rc = 12.0, 2.8e7, 4.0
        s = np.linspace(0, r, 20001)
        mass = np.trapezoid(4 * np.pi * s ** 2 * rho0 / (1 + (s / rc) ** 2), s)
        self.assertAlmostEqual(float(np.sqrt(g.v_iso2(r, rho0, rc))), float(np.sqrt(g.G * mass / r)), places=3)

    def test_nfw_at_r200_equals_v200(self):
        v200 = 150.0
        self.assertAlmostEqual(float(np.sqrt(g.v_nfw2(np.array([v200 / (10 * g.H0)]), v200, 9.0))[0]), v200, places=6)

    def test_runs_test_flags_structure(self):
        self.assertLess(compare.runs_z(np.array([1.0] * 10 + [-1.0] * 10)), -1.96)


class TestFailureLab(unittest.TestCase):
    """Shipped select(): lowest chi^2 wins - the 6-parameter 'wiggles' model, every time."""

    def test_chi2_picks_the_most_flexible_model(self):
        v, err = g.observed()
        best, rows = compare.select(g.R, v, err)
        self.assertEqual(best, "disk + halo + wiggles")
        self.assertEqual([r["chi2"] for r in rows], [3267.95, 43.24, 67.83, 40.63])


class TestScipyEquivalent(unittest.TestCase):
    def test_bessel_against_scipy(self):
        try:
            import bessel_scipy
        except ImportError:
            self.skipTest("scipy not installed (pending-ci)")
        self.assertLess(bessel_scipy.max_relative_error(), 1e-6)


if __name__ == "__main__":
    unittest.main()
