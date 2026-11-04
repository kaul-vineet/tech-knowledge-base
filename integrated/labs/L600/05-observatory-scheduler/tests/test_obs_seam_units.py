"""SEAM units: RA/Dec in degrees, sidereal time in hours, trig in radians, exposures in minutes."""
import unittest

from tests import _lab

import sky  # noqa: E402
import validator  # noqa: E402


class Units(unittest.TestCase):
    def test_transit_altitude_identity(self):
        for q in sky.REQUESTS:
            with self.subTest(target=q.name):
                self.assertAlmostEqual(validator.alt_from_hour_angle(0.0, q.dec_deg, sky.SITE["lat_deg"]),
                                       90.0 - abs(sky.SITE["lat_deg"] - q.dec_deg), places=9)

    def test_hour_angle_in_hours_would_be_caught(self):
        """Forgetting x15 (hours used as degrees) moves the star; the two routes then disagree by degrees."""
        r = _lab.night()
        q, t = r["reqs"][2], r["slots"][20].utc
        from timeutil import lst_hours
        wrong = validator.alt_from_hour_angle(lst_hours(t, sky.SITE["lon_deg"]) - q.ra_deg, q.dec_deg, sky.SITE["lat_deg"])
        self.assertGreater(abs(wrong - sky.alt_deg(q, t)), 1.0)
        self.assertLess(abs(validator.alt_deg_lst(q, t) - sky.alt_deg(q, t)), 0.02)

    def test_exposures_fill_whole_slots(self):
        for q in sky.REQUESTS:
            self.assertEqual(q.exp_min % sky.STEP_MIN, 0, q.name)

    def test_coordinates_are_degrees_in_range(self):
        for q in sky.REQUESTS:
            self.assertTrue(0.0 <= q.ra_deg < 360.0 and -90.0 <= q.dec_deg <= 90.0, q.name)


if __name__ == "__main__":
    unittest.main()
