import importlib.util
import math
import unittest

import kepler


class TestKeplerEquation(unittest.TestCase):
    def test_residual_is_tiny(self):
        for e in (0.0, 0.0167, 0.0934, 0.5, 0.9):
            for M in (-3.0, -1.0, 0.0, 0.3, 2.5):
                E = kepler.solve_kepler(M, e)
                self.assertLess(abs(E - e * math.sin(E) - M), 1e-12)

    def test_circular_orbit_E_equals_M(self):
        self.assertEqual(kepler.solve_kepler(1.234, 0.0), 1.234)


class TestPositions(unittest.TestCase):
    JD = 2461342.5

    def test_earth_distance_between_perihelion_and_aphelion(self):
        r = math.dist((0, 0, 0), kepler.heliocentric("EM Bary", self.JD))
        self.assertTrue(0.983 < r < 1.017)

    def test_earth_heliocentric_longitude_late_october(self):
        x, y, _ = kepler.heliocentric("EM Bary", self.JD)
        self.assertAlmostEqual(math.degrees(math.atan2(y, x)), 35.2, delta=0.5)  # Sun appears at ~215 deg

    def test_third_law(self):
        self.assertAlmostEqual(kepler.period_years(1.52371034), 1.8808, places=4)

    def test_printed_mars_position(self):
        ra, dec, d = kepler.geocentric_radec("Mars", self.JD)
        self.assertEqual((f"{ra:.4f}", f"{dec:+.4f}", f"{d:.4f}"), ("139.6593", "+17.2889", "1.4567"))


@unittest.skipUnless(importlib.util.find_spec("skyfield"), "skyfield not installed (runs in CI)")
class TestSkyfieldEquivalent(unittest.TestCase):
    def test_within_jpl_error_budget(self):
        import kepler_skyfield
        sep_deg, dist_au = kepler_skyfield.compare(2461342.5)
        self.assertLess(sep_deg, 0.05)  # JPL: ~40 arcsec for Mars; geometric vs astrometric adds a little
        self.assertLess(abs(dist_au), 0.001)


if __name__ == "__main__":
    unittest.main()
