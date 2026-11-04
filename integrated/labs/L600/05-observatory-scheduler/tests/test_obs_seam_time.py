"""SEAM astronomy <-> scheduler: time systems. Fails under SCHED_FAULT=local-as-utc (the failure lab)."""
import unittest
from datetime import datetime, timedelta, timezone

from tests import _lab

import _kb  # noqa: E402
import sky  # noqa: E402
import validator  # noqa: E402
from timeutil import UtcInstant, lst_hours  # noqa: E402

IST = timezone(timedelta(hours=5, minutes=30))


class TypedUtc(unittest.TestCase):
    def test_naive_and_non_utc_datetimes_are_refused(self):
        with self.assertRaises(TypeError):
            UtcInstant(datetime(2026, 11, 19, 18, 50))
        with self.assertRaises(TypeError):
            UtcInstant(datetime(2026, 11, 19, 18, 50, tzinfo=IST))
        with self.assertRaises(TypeError):
            UtcInstant.from_aware(datetime(2026, 11, 19, 18, 50))

    def test_local_time_is_converted_not_relabelled(self):
        t = UtcInstant.from_aware(datetime(2026, 11, 19, 18, 50, tzinfo=IST))
        self.assertEqual(t.iso(), "2026-11-19T13:20:00Z")

    def test_sky_maths_accepts_only_utc_instants(self):
        for bad in (datetime(2026, 11, 19, 13, 20, tzinfo=timezone.utc), 2461364.0):
            with self.assertRaises(TypeError):
                sky.alt_deg(sky.REQUESTS[0], bad)


class SiderealRoutes(unittest.TestCase):
    def test_gast_reproduces_wallace_capitaine_2006(self):
        ts = _kb.timescales
        self.assertLess(abs(ts.gast_hours(ts.WC06_JD_UT1, ts.WC06_JD_TT) - ts.WC06_GST_H) * 3600.0, 0.1)

    def test_two_altitude_routes_agree(self):
        r = _lab.night()
        diff = max(abs(sky.alt_deg(q, s.utc) - validator.alt_deg_lst(q, s.utc)) for q in r["reqs"] for s in r["slots"])
        self.assertLess(diff, 0.02)

    def test_lst_advances_one_sidereal_day_in_23h56m04s(self):
        t = UtcInstant.from_aware(datetime(2026, 11, 19, 13, 20, tzinfo=timezone.utc))
        later = UtcInstant(t.dt + timedelta(hours=23, minutes=56, seconds=4.0905))
        self.assertAlmostEqual((lst_hours(later, 77.03) - lst_hours(t, 77.03)) % 24.0, 0.0, delta=1e-4)


class ScheduledBlocksAtRealUtc(unittest.TestCase):
    def test_every_scheduled_block_passes_the_independent_validator(self):
        """The guard: the scheduler's sky time and the published UTC time must be the same instant."""
        import scheduler
        r = scheduler.build()  # honours SCHED_FAULT
        for key in ("greedy", "local"):
            with self.subTest(plan=key):
                self.assertEqual(validator.validate(validator.rows_from_blocks(r[key], r["reqs"], r["slots"])), [])


if __name__ == "__main__":
    unittest.main()
