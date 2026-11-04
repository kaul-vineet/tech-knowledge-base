"""Unit tests + fault reproduction for lesson 12 (numpy only; the astroplan equivalence test is skipped locally)."""
import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import ephem
import plan

HERE = Path(__file__).resolve().parent


class TestEphemeris(unittest.TestCase):
    def test_gmst_at_j2000_matches_usno_formula(self):
        self.assertAlmostEqual(ephem.gmst_deg(2451545.0) / 15.0, 18.697375, places=5)

    def test_sun_declination_at_june_solstice_equals_obliquity(self):
        _, dec = ephem.sun_radec(ephem.julian_date(datetime(2026, 6, 21, 8, tzinfo=timezone.utc)))
        self.assertAlmostEqual(float(dec), 23.436, delta=0.01)

    def test_full_moon_on_the_planning_night(self):
        jd = ephem.julian_date(datetime(2026, 11, 24, 22, 0, tzinfo=plan.SITE["tz"]))
        mra, mdec, _ = ephem.moon_radec(jd)
        elong = ephem.separation(mra, mdec, *ephem.sun_radec(jd))
        self.assertGreater(float(elong), 170.0)
        self.assertLess(float(ephem.separation(*plan.TARGETS["Aldebaran"], mra, mdec)), plan.MIN_MOON_SEP)

    def test_separation_small_angle(self):
        self.assertAlmostEqual(float(ephem.separation(10.0, 0.0, 10.0, 1 / 3600)), 1 / 3600, places=9)

    def test_dark_window(self):
        self.assertEqual(plan.dark_window(), ("18:50", "05:20"))


class TestFailureLab(unittest.TestCase):
    """The shipped airmass() is sec z: negative below the horizon, so 'lowest airmass wins' picks buried stars."""

    def test_shipped_schedule_contains_stars_below_the_horizon(self):
        rows, _ = plan.schedule()
        below = [r["target"] for r in rows if r["alt_deg"] < 0]
        self.assertEqual(below, ["Sirius", "Vega", "Fomalhaut", "Altair"])
        self.assertEqual(rows[0], {"target": "Sirius", "start": "18:50", "alt_deg": -34.6, "airmass": -1.76,
                                   "moon_sep_deg": 59.5})

    def test_shipped_airmass_passes_the_limit_below_horizon(self):
        self.assertLess(float(plan.airmass(-10.0)), plan.MAX_AIRMASS)


class TestFixedGolden(unittest.TestCase):
    def test_solution_schedule(self):
        spec = importlib.util.spec_from_file_location("plan_fixed", HERE / "solution" / "plan.py")
        fixed = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixed)
        rows, left = fixed.schedule()
        self.assertEqual([(r["target"], r["start"]) for r in rows],
                         [("Deneb", "18:50"), ("Betelgeuse", "22:10"), ("Sirius", "00:10")])
        self.assertEqual(left, ["Aldebaran", "Altair", "Capella", "Fomalhaut", "Vega"])
        self.assertAlmostEqual(float(fixed.airmass(30.0)), 1.9943, places=4)
        self.assertTrue(np.isinf(fixed.airmass(0.0)))

    def test_solution_airmass_matches_kasten_young_1989_table(self):
        # Kasten & Young 1989 (Applied Optics 28, 4735), Table II relative optical air mass m(elevation);
        # the paper states its eq. 3 fit has a maximum relative error < 0.5 %
        spec = importlib.util.spec_from_file_location("plan_fixed2", HERE / "solution" / "plan.py")
        fixed = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixed)
        table = {0.1: 36.5581, 1.0: 26.2595, 5.0: 10.3164, 10.0: 5.5841, 20.0: 2.9016, 30.0: 1.9939,
                 45.0: 1.4128, 60.0: 1.1543, 90.0: 1.0000}
        for elev, m in table.items():
            with self.subTest(elevation=elev):
                self.assertLess(abs(float(fixed.airmass(elev)) - m) / m, 0.005)


class TestAstroplanEquivalent(unittest.TestCase):
    def test_low_precision_sun_and_moon_agree_with_astropy(self):
        try:
            import plan_astroplan
        except ImportError:
            self.skipTest("astropy/astroplan not installed (pending-ci)")
        d_sun, d_moon = plan_astroplan.max_differences()
        self.assertLess(d_sun, 0.1)
        self.assertLess(d_moon, 0.5)  # Moon: 1-2 arcmin theory + J2000-vs-date frame differences


if __name__ == "__main__":
    unittest.main()
