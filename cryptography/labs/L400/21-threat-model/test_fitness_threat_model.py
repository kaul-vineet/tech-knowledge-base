"""Fitness function: the threat model stays true. Thresholds: 0 checker problems (every threat has a control or a
recorded acceptance, every control names tests that exist, every boundary-crossing flow has T and I threats) and
every referenced control test PASSES when run. Takes ~10-30 s: it runs 12 tests across L200-L400."""
import unittest

import solution_verified as sv


class TestThreatModelFitness(unittest.TestCase):
    def test_model_has_no_problems(self):
        self.assertEqual(sv.check(sv.load()), [])

    def test_every_control_test_passes(self):
        results = sv.run_control_tests(sv.load())
        self.assertEqual({cid for cid, ok in results.items() if not ok}, set())
        self.assertEqual(len(results), len(sv.load()["controls"]))


if __name__ == "__main__":
    unittest.main()
