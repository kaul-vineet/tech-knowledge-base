"""Build-task check: persist votedFor AND add the VoteOnce invariant (a ghost log of votes). Default target =
solution_modelcheck.py. Test YOUR modelcheck.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILE = "modelcheck.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_modelcheck.py"
spec = importlib.util.spec_from_file_location("target_modelcheck", HERE / FILE)
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)


class PersistedVote(unittest.TestCase):
    def test_every_reachable_state_is_safe(self):
        self.assertTrue(mc.PERSIST_VOTE)
        self.assertEqual(mc.bfs()[:3], (None, [], 1853))

    def test_vote_once_catches_the_cause_earlier(self):
        self.assertIn("VoteOnce", mc.INVARIANTS)
        mc.PERSIST_VOTE = False  # re-introduce the bug: VoteOnce fails before any second leader exists
        try:
            violated, trace, _, _ = mc.bfs()
            self.assertEqual((violated, len(trace)), ("VoteOnce", 4))
        finally:
            mc.PERSIST_VOTE = True


if __name__ == "__main__":
    unittest.main()
