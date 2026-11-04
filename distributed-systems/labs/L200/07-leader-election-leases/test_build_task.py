"""Build-task check: Node.resign() hands the lease over without waiting for the TTL.
Default target = solution_election.py. Test YOUR election.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILE = "election.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_election.py"
spec = importlib.util.spec_from_file_location("target_election", HERE / FILE)
el = importlib.util.module_from_spec(spec)
spec.loader.exec_module(el)


class TestResign(unittest.TestCase):
    def test_resign_hands_over_in_the_same_tick(self):
        out = el.simulate(events={3: ("n1", "resign")}, quiet=True)
        self.assertEqual(out["holders"][3][1], "n2")  # no waiting for the TTL (pause case: t=5)
        self.assertGreater(out["holders"][3][2], out["holders"][2][2])  # new holder, higher token

    def test_resigned_node_never_writes_again(self):
        out = el.simulate(events={3: ("n1", "resign")}, quiet=True)
        self.assertFalse([l for l in out["log"] if l.startswith(("t=4 n1", "t=5 n1", "t=8 n1"))])

    def test_resign_of_a_follower_deletes_nothing(self):
        out = el.simulate(events={3: ("n3", "resign")}, quiet=True)
        self.assertEqual([h for _, h, _ in out["holders"]], ["n1"] * 9)  # n1 keeps its lease


if __name__ == "__main__":
    unittest.main()
