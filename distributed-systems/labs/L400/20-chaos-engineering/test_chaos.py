"""Lesson tests for lab 20: python -m unittest -v"""
import unittest

import chaos


class Chaos(unittest.TestCase):
    def test_loader_keeps_each_labs_helpers(self):
        self.assertTrue(hasattr(chaos.SAGA["L300 lesson"].lab_helpers, "SagaLog"))
        self.assertTrue(hasattr(chaos.RAFT["L300 lesson"].lab_helpers, "Cluster"))

    def test_failure_lab_unbounded_experiment_hurts_every_customer(self):
        r = chaos.run_saga_experiment("L300 lesson", "shipping-outage", 14)
        self.assertEqual((r["blast_radius_pct"], r["customers_hurt"], r["held"]), (100.0, 60, False))

    def test_hardened_saga_holds_both_hypotheses(self):
        for fault in ("shipping-outage", "crash-after-charge"):
            r = chaos.run_saga_experiment("L300 hardened", fault, 14)
            self.assertEqual((r["held"], r["customers_hurt"]), (True, 0), fault)

    def test_the_fault_you_pick_decides_what_you_find(self):
        s = chaos.summary([chaos.run_raft_experiment(t, f, seed) for t in chaos.RAFT
                           for f in ("random-crash", "rolling-restart") for seed in range(1, 21)])
        self.assertEqual(s[("raft/random-crash", "L300 lesson")][:2], (20, 20))  # random crashes find nothing
        self.assertEqual(s[("raft/rolling-restart", "L300 lesson")][:2], (19, 20))  # a fast rollout finds the bug
        self.assertEqual(s[("raft/rolling-restart", "L300 hardened")][:2], (20, 20))

    def test_deterministic(self):
        self.assertEqual(chaos.run_raft_experiment("L300 lesson", "random-crash", 3),
                         chaos.run_raft_experiment("L300 lesson", "random-crash", 3))


if __name__ == "__main__":
    unittest.main()
