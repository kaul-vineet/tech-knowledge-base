"""Build-task check: measured leader placement + majority-sync replication meet the design brief.
Default target = solution_multiregion.py. Test YOUR file:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, sys, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FILE = "multiregion.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_multiregion.py"
spec = importlib.util.spec_from_file_location("target_multiregion", HERE / FILE)
mr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mr)


class Placement(unittest.TestCase):
    def test_place_leader_by_weighted_p99(self):
        self.assertEqual(mr.place_leader("sync-majority"), "eu")

    def test_design_uses_the_measured_leader(self):
        self.assertEqual(mr.DESIGN, {"replication": "sync-majority", "leader": mr.place_leader("sync-majority")})

    def test_design_meets_the_brief(self):
        self.assertEqual(mr.violations(mr.evaluate(mr.DESIGN)), [])


if __name__ == "__main__":
    unittest.main()
