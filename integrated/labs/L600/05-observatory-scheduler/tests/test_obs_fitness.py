"""Fitness functions that keep the design decisions true (ADRs 0001-0003)."""
import unittest

from tests import _lab

import scheduler  # noqa: E402
import sky  # noqa: E402
import validator  # noqa: E402
import weather  # noqa: E402

RUNS, SEED, MARGIN = 1000, 7, 0.15


class Fitness(unittest.TestCase):
    def test_ff1_no_scheduled_observation_above_airmass_limit(self):
        r = _lab.night()
        for key in ("greedy", "local"):
            self.assertEqual(validator.validate(validator.rows_from_blocks(r[key], r["reqs"], r["slots"])), [])
            self.assertTrue(all(x["max_airmass"] <= sky.MAX_AIRMASS for x in r[key + "_rows"]))

    def test_ff2_expected_value_beats_greedy_by_margin(self):
        r = _lab.night()
        clear = weather.clear_matrix(RUNS, len(r["slots"]), SEED)
        g = weather.realised([(s, n, r["reqs"][i].priority) for s, n, i in r["greedy"]], clear)
        lo = weather.realised([(s, n, r["reqs"][i].priority) for s, n, i in r["local"]], clear)
        self.assertGreaterEqual(lo.mean(), (1 + MARGIN) * g.mean())
        d, h = weather.summary(lo - g)
        self.assertGreater(d - h, 0.0)  # paired (common random numbers) 95 % CI excludes zero

    def test_ff3_schedule_deterministic_for_a_seed(self):
        a, b = scheduler.build(seed=2026), scheduler.build(seed=2026)
        self.assertEqual(scheduler.plan_hash(a["local_rows"]), scheduler.plan_hash(b["local_rows"]))
        self.assertEqual(scheduler.plan_hash(a["local_rows"]), "4928d62de8143130")
        self.assertTrue((weather.clear_matrix(50, 64, SEED) == weather.clear_matrix(50, 64, SEED)).all())


if __name__ == "__main__":
    unittest.main()
