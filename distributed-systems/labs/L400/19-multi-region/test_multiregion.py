"""Lesson tests for lab 19: python -m unittest -v"""
import unittest

import multiregion as mr


class MultiRegion(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(mr.simulate(mr.DESIGN, fail=True), mr.simulate(mr.DESIGN, fail=True))

    def test_failure_lab_async_loses_acknowledged_writes(self):
        self.assertEqual(mr.evaluate({"replication": "async", "leader": "ap"})["rpo_writes"], 16)
        self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN)), ["RPO: 16 acknowledged writes lost"])

    def test_majority_sync_never_loses_a_committed_write(self):
        for leader in ("us", "eu", "ap"):
            m = mr.evaluate({"replication": "sync-majority", "leader": leader})
            self.assertEqual(m["rpo_writes"], 0, leader)
            self.assertTrue(1000 <= m["rto_ms"] <= 2500, m["rto_ms"])  # election timeout + vote round trip

    def test_multi_leader_and_leaderless_trade_conflicts_for_latency(self):
        ml, ll = mr.evaluate({"replication": "multi-leader"}), mr.evaluate({"replication": "leaderless"})
        self.assertEqual((ml["conflicts"], ml["rpo_writes"]), (434, 2))
        self.assertEqual((ll["conflicts"], ll["rpo_writes"]), (409, 0))
        self.assertLess(ml["p99"]["us"], 150.0)

    def test_leader_placement_changes_who_pays(self):
        us, ap = (mr.simulate({"replication": "sync-majority", "leader": r})["p99"] for r in ("us", "ap"))
        self.assertLess(us["us"], ap["us"])
        self.assertLess(ap["ap"], us["ap"])


if __name__ == "__main__":
    unittest.main()
