"""Build-task check: a deterministic LWW tie-break (Lamport time, then replica id) makes merge a join.
Default target = solution_crdts.py. Test YOUR crdts.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, sys, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from helpers import check_laws, converge  # noqa: E402

FILE = "crdts.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_crdts.py"
spec = importlib.util.spec_from_file_location("target_crdts", HERE / FILE)
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)


class LWWTieBreak(unittest.TestCase):
    def test_lww_obeys_the_laws_and_converges(self):
        self.assertEqual(set(check_laws(cm.LWWRegister)["counts"].values()), {"500/500"})
        self.assertEqual(converge(cm.LWWRegister)["converged"], "500/500")

    def test_tie_goes_to_the_higher_replica_id_both_ways(self):
        x, y = cm.LWWRegister("x", 1, "r0"), cm.LWWRegister("y", 1, "r1")
        self.assertEqual((x.merge(y).value(), y.merge(x).value()), ("y", "y"))

    def test_later_timestamp_still_wins(self):
        x, y = cm.LWWRegister("x", 2, "r0"), cm.LWWRegister("y", 1, "r9")
        self.assertEqual((x.merge(y).value(), y.merge(x).value()), ("x", "x"))


if __name__ == "__main__":
    unittest.main()
