"""Seam S4 rollout flags (application-architecture) <-> crypto policy. Reproduce the rollout fault:
    INJECT=downgrade python -m unittest test_seam_rollout_downgrade -> FAIL (classical sessions while PQ required)"""
import unittest

import _lab
import seams


class TestSeamRolloutDowngrade(unittest.TestCase):
    def test_v1_server_left_behind_is_refused_not_downgraded(self):
        stats = _lab.phase_stats(_lab.INJECT or "migrated", [2, 2, 1], required=True)
        result = seams.s4_rollout_to_policy(stats, stats["servers"])
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["refused"], 2)

    def test_gate_only_allows_pq_required_on_an_all_v2_fleet(self):
        import fleet
        self.assertFalse(seams.can_require_pq(fleet.make_fleet([2, 2, 1])))
        self.assertTrue(seams.can_require_pq(fleet.make_fleet([2, 2, 2])))


if __name__ == "__main__":
    unittest.main()
