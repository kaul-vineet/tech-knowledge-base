import importlib.util
import unittest
from datetime import date, datetime, timedelta, timezone

import timescales as ts

UTC = timezone.utc


class TestScales(unittest.TestCase):
    def test_tai_minus_utc_now_is_37(self):
        self.assertEqual(ts.scales(datetime(2026, 10, 29, 15, 30, tzinfo=UTC))["TAI-UTC s"], 37)

    def test_leap_second_step_on_2017_01_01(self):
        self.assertEqual(ts.tai_minus_utc(57753.99), 36)
        self.assertEqual(ts.tai_minus_utc(57754.0), 37)

    def test_tt_minus_utc(self):
        self.assertAlmostEqual(ts.scales(datetime(2026, 1, 1, tzinfo=UTC))["TT-UTC s"], 69.184)

    def test_before_1972_is_refused(self):
        with self.assertRaises(ValueError):
            ts.tai_minus_utc(40000)


class TestSidereal(unittest.TestCase):
    def test_worked_example_wallace_capitaine_2006(self):
        # A&A 459, 981 (2006), appendix: ERA 5h05m03.7035s, GST 5h05m22.2133s for UTC 2006-01-15 21:24:37.5
        self.assertLess(abs(ts.era_hours(ts.WC06_JD_UT1) - ts.WC06_ERA_H) * 3600.0, 0.001)
        # USNO quotes ~0.1 s accuracy for its approximate apparent sidereal time
        self.assertLess(abs(ts.gast_hours(ts.WC06_JD_UT1, ts.WC06_JD_TT) - ts.WC06_GST_H) * 3600.0, 0.1)

    def test_short_formula_matches_usno_full_formula(self):
        # USNO (aa.usno.navy.mil/faq/GAST): the short 0h-UT form loses about 0.1 s per century
        for d in (datetime(1987, 1, 1, tzinfo=UTC), datetime(2000, 1, 1, 12, tzinfo=UTC),
                  datetime(2026, 10, 29, tzinfo=UTC), datetime(2026, 10, 29, 15, 30, tzinfo=UTC)):
            with self.subTest(when=d.isoformat()):
                diff_s = (ts.gmst_hours(ts.jd_utc(d)) - ts.gmst_usno_full_hours(d)) * 3600.0
                self.assertLess(abs(diff_s), 0.05)

    def test_j2000_value_matches_iers_earth_rotation_angle(self):
        # IERS Conventions (2010) eq. 5.14: ERA(J2000.0) = 0.7790572732640 turn = 18h41m50.548s
        self.assertLess(abs(ts.gmst_hours(2451545.0) - ts.era_hours(2451545.0)) * 3600.0, 0.005)

    def test_sidereal_day_is_23h56m04s(self):
        t0 = datetime(2026, 10, 29, tzinfo=UTC)
        g0 = ts.gmst_hours(ts.jd_utc(t0))
        g1 = ts.gmst_hours(ts.jd_utc(t0 + timedelta(hours=23, minutes=56, seconds=4.0905)))
        self.assertLess(abs(((g1 - g0 + 12) % 24 - 12) * 3600), 0.01)

    def test_hms_format(self):
        self.assertEqual(ts.hms(18.0318167), "18h01m54.54s")


class TestDataFreshness(unittest.TestCase):
    """Time-sensitive: fails once the vendored IERS table has expired (update LEAPS from Leap_Second.dat)."""

    def test_leap_table_not_expired(self):
        self.assertLessEqual(date.today(), ts.LEAP_TABLE_EXPIRES)


@unittest.skipUnless(importlib.util.find_spec("astropy"), "astropy not installed (runs in CI)")
class TestAstropyEquivalent(unittest.TestCase):
    def test_astropy_scales_and_gmst(self):
        import time_astropy
        r = time_astropy.compare(datetime(2026, 10, 29, 15, 30, tzinfo=UTC))
        self.assertAlmostEqual(r["tt_minus_utc_s"], 69.184, places=3)
        self.assertLess(abs(r["gmst_diff_s"]), 1.0)


if __name__ == "__main__":
    unittest.main()
