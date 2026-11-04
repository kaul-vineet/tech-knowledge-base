"""Build-task check: a bounded experiment (10% cohort, control group, abort after the first harmed order) still
refutes the hypothesis but hurts at most one customer. Default target = solution_chaos.py.
Test YOUR chaos.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, sys, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FILE = "chaos.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_chaos.py"
spec = importlib.util.spec_from_file_location("target_chaos", HERE / FILE)
ch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ch)


class BoundedExperiment(unittest.TestCase):
    def test_finding_kept_damage_bounded(self):
        for fault in ("shipping-outage", "crash-after-charge"):
            r = ch.run_saga_experiment("L300 lesson", fault, 14)
            with self.subTest(fault=fault):
                self.assertFalse(r["held"])  # the weakness is still found ...
                self.assertLessEqual(r["blast_radius_pct"], 10.0)
                self.assertLessEqual(r["customers_hurt"], 1)  # ... at the cost of one customer, not sixty
                self.assertTrue(r["aborted"])

    def test_control_group_is_untouched(self):
        r = ch.run_saga_experiment("L300 lesson", "shipping-outage", 14)
        self.assertEqual(r["control_harmed"], 0)


if __name__ == "__main__":
    unittest.main()
