"""Build-task check: read write-back makes the quorum linearizable (and is skipped when replicas agree).
Default target = solution_quorum.py. Test YOUR quorum.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILE = "quorum.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_quorum.py"
spec = importlib.util.spec_from_file_location("target_quorum", HERE / FILE)
qm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qm)


class WriteBack(unittest.TestCase):
    def test_write_back_removes_inversions(self):
        m = qm.measure(2, 2, True)
        self.assertEqual((m["inversions"], m["stale_pct"]), (0, 0.0))
        self.assertTrue(m["linearizable"])

    def test_config_use_case_is_now_decidable(self):
        rows = [qm.measure(r, w, wb) for r, w, wb in qm.SETTINGS]
        best = qm.decide(rows, qm.USE_CASES["lock owner / config (linearizable)"])
        self.assertIsNotNone(best)
        self.assertEqual((best["R"], best["W"], best["write_back"]), (2, 2, True))

    def test_write_back_only_when_replicas_disagree(self):
        plain, wb = qm.measure(2, 2, False), qm.measure(2, 2, True)
        self.assertLess(wb["read_p50"] - plain["read_p50"], 1.0)  # median read: no extra round trip


if __name__ == "__main__":
    unittest.main()
