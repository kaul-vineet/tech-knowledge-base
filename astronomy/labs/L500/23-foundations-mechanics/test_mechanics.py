import math
import unittest

import mechanics as m


class TestFoundationsI(unittest.TestCase):
    def test_every_check_passes(self):
        for name, fn in m.CHECKS.items():
            with self.subTest(check=name):
                self.assertTrue(fn()[1])

    def test_kepler_period_scales_as_a_to_three_halves(self):
        self.assertAlmostEqual(m.kepler_period(4.0, m.GM4) / m.kepler_period(1.0, m.GM4), 8.0, places=12)

    def test_vis_viva_circular_and_escape_limits(self):
        self.assertAlmostEqual(m.vis_viva(1.0, 1.0, m.GM4), m.GM4)       # r = a: v^2 = GM/a
        self.assertAlmostEqual(m.vis_viva(1.0, 1e300, m.GM4), 2 * m.GM4)  # a -> infinity: escape speed

    def test_rotation_route_at_the_pole(self):
        alt, _ = m.altaz_rotation(123.0, 45.0, 90.0)  # at the north pole, altitude = declination
        self.assertAlmostEqual(float(alt), 45.0, places=10)

    def test_geostationary_radius(self):
        r = (m.GM_EARTH * (m.SIDEREAL_DAY / (2 * math.pi)) ** 2) ** (1 / 3) / 1000
        self.assertAlmostEqual(r, 42164.2, delta=0.1)


if __name__ == "__main__":
    unittest.main()
