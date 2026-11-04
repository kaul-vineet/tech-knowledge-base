"""Fitness functions: keep the design decisions true (ADRs 0001-0003)."""
import unittest

import shared


class Fitness(unittest.TestCase):
    def test_exact_shots_for_every_job_under_injected_failures(self):          # ADR 0001
        m = shared.load()
        self.assertEqual(m["shots_exact"], m["jobs"])

    def test_cache_hit_never_crosses_calibration_versions(self):               # ADR 0003
        self.assertEqual(shared.load()["cache_crossings"], 0)

    def test_p95_queue_time_under_budget(self):                                # ADR 0002
        m = shared.load()
        self.assertLessEqual(m["p95_queue_s"], m["budget_p95_s"])


if __name__ == "__main__":
    unittest.main()
