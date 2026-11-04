"""Build-task check: the election restriction (Raft paper section 5.4.1) keeps every committed entry.
Default target = solution_raft.py. Test YOUR raft.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILE = "raft.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_raft.py"
spec = importlib.util.spec_from_file_location("target_raft", HERE / FILE)
rf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rf)


class ElectionRestriction(unittest.TestCase):
    def test_stale_follower_cannot_win_and_nothing_committed_is_lost(self):
        s = rf.stale_leader_scenario(rf.Node)
        self.assertEqual(s.checker.violations, [])
        leader = s.leader()
        self.assertEqual([e[1] for e in leader.log[:2]], ["x=1", "x=2"])  # Leader Completeness

    def test_safe_for_many_seeds(self):
        for seed in range(1, 21):
            self.assertEqual(rf.stale_leader_scenario(rf.Node, seed).checker.violations, [], f"seed {seed}")

    def test_vote_rule_compares_last_term_then_length(self):
        from helpers import Network
        node = rf.Node("n2", ["n1", "n3"], Network(), 7)
        node.log, node.term = [(1, "a"), (2, "b")], 2
        cases = {(3, 2, 1): False, (3, 1, 9): False, (3, 2, 2): True, (3, 3, 1): True}  # (term, last_term, last_index)
        for (term, last_term, last_index), expected in cases.items():
            node.voted_for = None
            node.receive("n3", {"type": "vote", "term": term, "last_term": last_term, "last_index": last_index})
            self.assertEqual(node.voted_for == "n3", expected, (last_term, last_index))


if __name__ == "__main__":
    unittest.main()
