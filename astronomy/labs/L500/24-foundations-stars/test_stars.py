import math
import unittest

import stars as s


class TestFoundationsII(unittest.TestCase):
    def test_every_check_passes(self):
        for name, fn in s.CHECKS.items():
            with self.subTest(check=name):
                self.assertTrue(fn()[1])

    def test_luminosity_scales_as_r2_t4(self):
        self.assertAlmostEqual(s.luminosity(2 * s.R_SUN, s.T_SUN) / s.luminosity(s.R_SUN, s.T_SUN), 4.0)
        self.assertAlmostEqual(s.luminosity(s.R_SUN, 2 * s.T_SUN) / s.luminosity(s.R_SUN, s.T_SUN), 16.0)

    def test_distance_modulus_zero_at_10_pc(self):
        self.assertAlmostEqual(float(s.distance_modulus(10.0)), 0.0)
        self.assertAlmostEqual(float(s.distance_modulus(100.0)), 5.0)

    def test_sigma_from_exact_constants(self):
        self.assertAlmostEqual(s.sigma_from_constants() / s.SIGMA_CODATA, 1.0, places=9)


if __name__ == "__main__":
    unittest.main()
