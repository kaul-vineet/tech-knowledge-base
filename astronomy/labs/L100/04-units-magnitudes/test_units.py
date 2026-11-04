import importlib.util
import unittest

import units


class TestDefinitions(unittest.TestCase):
    def test_light_year_exact_value(self):
        self.assertEqual(units.LY, 9_460_730_472_580_800.0)  # IAU value in metres

    def test_parsec_matches_iau_2015_b2(self):
        self.assertAlmostEqual(units.PC / 3.0856775814913673e16, 1.0, places=15)

    def test_parsec_in_light_years(self):
        self.assertAlmostEqual(units.PC / units.LY, 3.2616, places=4)


class TestMagnitudes(unittest.TestCase):
    def test_pogson_five_magnitudes_is_100(self):
        self.assertAlmostEqual(units.flux_ratio(0, 5), 100.0, places=12)

    def test_round_trip(self):
        self.assertAlmostEqual(units.flux_ratio(units.mag_difference(3.7, 1.0), 0), 3.7, places=12)

    def test_distance_modulus_round_trip(self):
        for d in (1.3, 10, 8000):
            self.assertAlmostEqual(units.distance_from_modulus(units.distance_modulus(d)), d, places=9)

    def test_sun_apparent_magnitude(self):
        self.assertEqual(f"{4.83 + units.distance_modulus(units.AU / units.PC):.2f}", "-26.74")


@unittest.skipUnless(importlib.util.find_spec("astropy"), "astropy not installed (runs in CI)")
class TestAstropyEquivalent(unittest.TestCase):
    def test_astropy_constants_agree(self):
        import units_astropy
        for name, ours, theirs in units_astropy.compare():
            with self.subTest(name=name):
                self.assertAlmostEqual(ours / theirs, 1.0, places=12)


if __name__ == "__main__":
    unittest.main()
