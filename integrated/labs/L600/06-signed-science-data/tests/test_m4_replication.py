"""M4: anti-entropy between mirrors (Merkle buckets, push-pull gossip on the distributed L400 #17 event loop)."""
import unittest

from _world import world

import checks
import mirrors as MR


def fresh(w, n=4):
    ms = [MR.Mirror(f"m{i}") for i in range(n)]
    for k, raw in w.objects.items():
        ms[0].put(k, raw)
    ms[0].put_timestamp(w.ts)
    return ms


class M4Replication(unittest.TestCase):
    def test_milestone(self):
        ok, d = checks.m4_replicated(world())
        self.assertTrue(ok, d)

    def test_same_final_state_for_any_gossip_order(self):
        w = world()
        roots = set()
        for seed in (1, 2, 3, 99):
            ms = fresh(w)
            self.assertTrue(MR.gossip(ms, seed=seed)["converged"])
            roots.add(ms[0].root())
        self.assertEqual(len(roots), 1)  # merge is a join: order and path do not matter

    def test_only_differing_buckets_are_sent(self):
        w = world()
        ms = fresh(w, 2)
        st = MR.gossip(ms, seed=1)
        payload = sum(len(v) for v in w.objects.values()) + len(w.ts)
        self.assertLessEqual(st["bytes"], payload)  # each object crosses once, nothing twice
        again = MR.gossip(ms, seed=2)
        self.assertEqual(again["bytes"], 0)  # converged replicas exchange roots only

    def test_timestamp_register_keeps_highest_version(self):
        w = world()
        m = MR.Mirror("x")
        newer, older = w.ts, w.stale.timestamp
        m.put_timestamp(newer)
        m.put_timestamp(older)
        self.assertEqual(m.timestamp, newer)


if __name__ == "__main__":
    unittest.main()
