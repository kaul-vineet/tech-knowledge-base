import importlib.util
import unittest

import numpy as np

import light


class TestBlackbody(unittest.TestCase):
    def test_numerical_peak_matches_wien(self):
        for T in (3000, 5772, 20000):
            self.assertAlmostEqual(light.peak_wavelength(T) / (light.B_WIEN / T), 1.0, places=4)

    def test_stefan_boltzmann(self):
        self.assertAlmostEqual(light.total_flux(5772) / (light.SIGMA * 5772**4), 1.0, places=5)

    def test_hotter_is_brighter_at_every_wavelength(self):
        lam = np.geomspace(100e-9, 10e-6, 50)
        self.assertTrue(np.all(light.planck(lam, 6000) > light.planck(lam, 5000)))

    def test_rayleigh_jeans_limit(self):
        lam, T = 1.0, 300  # long wavelength (hc / lambda k T = 5e-5): B -> 2 c k T / lambda^4
        self.assertAlmostEqual(light.planck(lam, T) / (2 * light.C * light.K * T / lam**4), 1.0, places=3)


class TestDoppler(unittest.TestCase):
    def test_h_alpha_velocity(self):
        self.assertEqual(f"{light.doppler_velocity(656.50e-9, light.H_ALPHA) / 1000:+.1f}", "+100.5")

    def test_blueshift_is_negative(self):
        self.assertLess(light.doppler_velocity(656.0e-9, light.H_ALPHA), 0)

    def test_relativistic_formula_limits(self):
        self.assertAlmostEqual(light.relativistic_velocity(1e-6) / (light.C * 1e-6), 1.0, places=5)
        self.assertLess(light.relativistic_velocity(100.0), light.C)


@unittest.skipUnless(importlib.util.find_spec("astropy"), "astropy not installed (runs in CI)")
class TestAstropyEquivalent(unittest.TestCase):
    def test_astropy_blackbody_and_constants(self):
        import light_astropy
        ratio, b = light_astropy.compare()
        self.assertAlmostEqual(ratio, 1.0, places=6)
        self.assertAlmostEqual(b / light.B_WIEN, 1.0, places=8)


if __name__ == "__main__":
    unittest.main()
