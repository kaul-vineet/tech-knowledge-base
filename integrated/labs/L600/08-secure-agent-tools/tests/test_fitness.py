"""Fitness functions F1-F3 (the scorecard's thresholds, as tests). F3 is time-based on a fake clock: run 3x."""
import unittest

import _lab
import scenarios as sc
from run_project import ttl_fitness


class TestFitness(unittest.TestCase):
    def test_f1_injection_corpus(self):
        rows = sc.run_corpus(_lab.url(), _lab.registry(), _lab.FAULTS)
        self.assertEqual(len(rows), 40)
        self.assertEqual(sum(r["requested"] for r in rows), 24)  # the fake obeyed 24 of 40 payloads
        self.assertEqual(sum(r["executed"] for r in rows), 0)
        self.assertEqual(sum(r["unscoped_side_effects"] for r in rows), 0)

    def test_f3_ttl_three_runs(self):
        for _ in range(3):
            self.assertEqual(ttl_fitness(_lab.FAULTS), (50, 50, True))


if __name__ == "__main__":
    unittest.main()
