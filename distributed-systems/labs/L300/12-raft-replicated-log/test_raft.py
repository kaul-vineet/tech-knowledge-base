"""python -m unittest -v : lesson 12 behaviour (happy path, re-election, majority rule) and the reproducible fault."""
import unittest

import raft
from helpers import Cluster


def committed_logs(c):
    return {n.name: n.log[:n.commit] for n in c.nodes.values()}


class HappyPath(unittest.TestCase):
    def test_one_leader_replicates_and_commits_on_every_node(self):
        c = Cluster(raft.Node, seed=7)
        leader = c.run_until_leader()
        for cmd in ("x=1", "x=2", "x=3"):
            leader.propose(cmd)
        c.run(6)
        self.assertEqual([n.role for n in c.nodes.values()].count("leader"), 1)
        self.assertEqual(set(map(tuple, committed_logs(c).values())), {((1, "x=1"), (1, "x=2"), (1, "x=3"))})

    def test_leader_crash_reelection_and_catch_up(self):
        c = Cluster(raft.Node, seed=7)
        old = c.run_until_leader()
        old.propose("x=1")
        c.run(6)
        c.crash(old.name)
        new = c.run_until_leader()
        self.assertNotEqual(new.name, old.name)
        self.assertGreater(new.term, old.term)
        new.propose("x=2")
        c.run(6)
        c.restart(old.name)
        c.run(6)
        self.assertEqual(old.role, "follower")  # a newer term demoted it
        self.assertEqual([e[1] for e in old.log], ["x=1", "x=2"])
        self.assertEqual(old.commit, 2)
        self.assertEqual(c.checker.violations, [])

    def test_no_commit_without_a_majority(self):
        c = Cluster(raft.Node, seed=7)
        leader = c.run_until_leader()
        for n in c.nodes:
            if n != leader.name:
                c.crash(n)
        leader.propose("x=1")
        c.run(30)
        self.assertEqual((len(leader.log), leader.commit), (1, 0))

    def test_same_seed_same_history(self):
        a, b = raft.stale_leader_scenario(), raft.stale_leader_scenario()
        self.assertEqual(a.net.events, b.net.events)


class FailureLabSymptom(unittest.TestCase):
    def test_lesson_code_loses_a_committed_entry(self):
        s = raft.stale_leader_scenario()
        self.assertTrue(any("LOST committed entry 1 (1:x=1)" in v for v in s.checker.violations))


if __name__ == "__main__":
    unittest.main()
