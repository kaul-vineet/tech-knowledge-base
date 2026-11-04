"""Lesson tests for lab 21 (model checking): python -m unittest -v"""
import unittest

import modelcheck as mc


def run(steps):
    """Apply labelled actions one by one (a hand-written example scenario)."""
    state = mc.init()
    for wanted in steps:
        state = dict(mc.actions(state))[wanted]
    return state


class ModelCheck(unittest.TestCase):
    def test_example_based_tests_pass_on_the_buggy_protocol(self):
        one = run(["n0 times out -> candidate, term 1", "n1 votes for n0 in term 1", "n0 becomes leader of term 1"])
        split = run(["n0 times out -> candidate, term 1", "n1 times out -> candidate, term 1"])
        restart = run(["n0 times out -> candidate, term 1", "n1 votes for n0 in term 1", "n1 restarts (votedFor forgotten)"])
        for state in (one, split, restart):
            self.assertTrue(mc.election_safety(state))  # three plausible tests, all green - and the bug ships

    def test_failure_lab_bfs_finds_the_shortest_counterexample(self):
        violated, trace, states, _ = mc.bfs()
        self.assertEqual((violated, len(trace), states), ("ElectionSafety", 7, 4519))
        self.assertEqual(trace[4], "n1 restarts (votedFor forgotten)")
        self.assertFalse(mc.election_safety(run(trace)))  # replaying the trace reproduces the violation

    def test_random_simulation_finds_it_less_reliably(self):
        self.assertEqual(mc.random_walks(), (16, 8))

    def test_persisted_vote_is_safe_in_every_reachable_state(self):
        mc.PERSIST_VOTE = True
        try:
            self.assertEqual(mc.bfs()[:3], (None, [], 1853))
        finally:
            mc.PERSIST_VOTE = False


if __name__ == "__main__":
    unittest.main()
