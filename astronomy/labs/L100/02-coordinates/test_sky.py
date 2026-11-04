import importlib.util
import unittest
from datetime import datetime, timezone

import sky

WHEN = datetime(2026, 10, 29, 15, 30, tzinfo=timezone.utc)


class TestTime(unittest.TestCase):
    def test_unix_epoch_and_j2000(self):
        self.assertEqual(sky.julian_date(datetime(1970, 1, 1, tzinfo=timezone.utc)), 2440587.5)
        self.assertEqual(sky.julian_date(datetime(2000, 1, 1, 12, tzinfo=timezone.utc)), 2451545.0)

    def test_gmst_at_j2000_is_the_formula_constant(self):
        self.assertAlmostEqual(sky.gmst_hours(2451545.0), 18.697375, places=9)


class TestGeometry(unittest.TestCase):
    def test_polaris_altitude_is_close_to_latitude(self):
        for lat, lon in (sky.GURGAON, (51.4778, -0.0015), (-33.87, 151.21)):
            alt, _ = sky.altaz(*sky.STARS["Polaris"], lat, lon, WHEN)
            self.assertLess(abs(alt - lat), 0.75 + 1e-6)  # Polaris is 0.74 deg from the pole

    def test_star_on_the_meridian_has_maximum_altitude(self):
        jd = sky.julian_date(WHEN)
        lst_deg = (sky.gmst_hours(jd) * 15 + sky.GURGAON[1]) % 360
        alt, az = sky.altaz(lst_deg, 10.0, *sky.GURGAON, WHEN)  # RA = LST -> hour angle 0
        self.assertAlmostEqual(alt, 90 - (sky.GURGAON[0] - 10.0), places=6)
        self.assertAlmostEqual(az, 180.0, places=6)  # due south for a star south of the zenith

    def test_altitude_stays_in_range(self):
        for _, alt, az, up in sky.sky_table(*sky.GURGAON, WHEN):
            self.assertTrue(-90 <= alt <= 90 and 0 <= az < 360)
            self.assertEqual(up, alt > 0)

    def test_gurgaon_at_21_ist(self):
        rows = {r[0]: r for r in sky.sky_table(*sky.GURGAON, WHEN)}
        self.assertEqual(f"{rows['Deneb'][1]:.2f}", "56.27")
        self.assertFalse(rows["Sirius"][3])

    def test_never_rises_rule(self):
        # a star with dec < -(90 - lat) never rises: Canopus from London
        lat = 51.4778
        best = max(sky.altaz(*sky.STARS["Canopus"], lat, 0.0, WHEN.replace(hour=h))[0] for h in range(24))
        self.assertLess(best, 0)
        self.assertAlmostEqual(best, sky.STARS["Canopus"][1] + 90 - lat, delta=0.5)  # upper culmination


@unittest.skipUnless(importlib.util.find_spec("astropy"), "astropy not installed (runs in CI)")
class TestAstropyEquivalent(unittest.TestCase):
    def test_astropy_agrees_within_precession(self):
        import sky_astropy
        for name, alt, az in sky_astropy.compare(WHEN):
            with self.subTest(star=name):
                self.assertLess(abs(alt), 0.6)  # differences in degrees: J2000 vs date (precession ~0.4 deg)
                self.assertLess(abs(az), 1.5)


if __name__ == "__main__":
    unittest.main()
