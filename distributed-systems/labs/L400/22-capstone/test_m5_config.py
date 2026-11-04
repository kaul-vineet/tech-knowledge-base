"""Milestone 5: the gateway's queue bound is replicated config, committed through Raft (L300 #12, hardened)."""
import unittest

from checks import evaluate
from pipeline import Pipeline


class Config(unittest.TestCase):
    def test_config_change_survives_a_leader_crash(self):
        p = Pipeline(22, ("raft-leader-crash",)).run()
        ok, measure = evaluate(p)["config via Raft"]
        self.assertTrue(ok, measure)
        self.assertEqual(p.config, {"version": 2, "max_queue": 12})
        versions = [v for _, v in p.config_seen]
        self.assertEqual(versions, sorted(versions))  # monotonic: never applied an older config again

    def test_bound_follows_the_committed_config(self):
        p = Pipeline(22).run()
        self.assertEqual({bound for _, bound in p.queue_seen}, {1, 8, 12})  # 1 = safe default before any commit


if __name__ == "__main__":
    unittest.main()
