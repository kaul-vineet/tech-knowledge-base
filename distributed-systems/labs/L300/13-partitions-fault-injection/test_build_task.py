"""Build-task check: fencing tokens at the storage reject the stale leader's write.
Default target = solution_partition.py. Test YOUR partition.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, unittest
from pathlib import Path

from checker import check_register

HERE = Path(__file__).resolve().parent
FILE = "partition.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_partition.py"
spec = importlib.util.spec_from_file_location("target_partition", HERE / FILE)
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)


class Fencing(unittest.TestCase):
    def test_stale_write_is_rejected_and_history_is_linearizable(self):
        events, history, _ = pt.run(pt.OPS, pt.FAULTS)
        stale = [op for op in history if op["process"] == "c1" and op["value"] == 3][0]
        self.assertFalse(stale["ok"])
        self.assertIn("token 1 < 2", stale.get("error", ""))
        self.assertTrue(check_register(history)[0])

    def test_fenced_out_node_steps_down(self):
        _, _, leaders = pt.run(pt.OPS, pt.FAULTS)
        self.assertEqual(leaders[8], ["n2"])  # n1 gave up at t=7, before the heal at t=9

    def test_storage_keeps_the_newest_value(self):
        s = pt.Storage()
        s.write(2, "new")
        s.write(1, "old")
        self.assertEqual(s.value, "new")


if __name__ == "__main__":
    unittest.main()
