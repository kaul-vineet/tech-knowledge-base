"""Build-task check: a bounded queue that sheds with 503 + Retry-After keeps p99 bounded under overload.
Default target = solution_backpressure.py. Test YOUR file:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, unittest
from pathlib import Path

from helpers import simulate

HERE = Path(__file__).resolve().parent
FILE = "backpressure.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_backpressure.py"
spec = importlib.util.spec_from_file_location("target_backpressure", HERE / FILE)
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)


class LoadShedding(unittest.TestCase):
    def setUp(self):
        self.records = simulate(bp.Server(), bp.BURST, bp.SERVICE_MS)
        self.s = bp.summary(self.records)

    def test_p99_stays_bounded_during_the_burst(self):
        self.assertLess(self.s["p99_ms"], 250)  # queue bound (~100 ms) + service time tail

    def test_sheds_with_retry_after_of_at_least_one_second(self):
        shed = [r for r in self.records if r["status"] == 503]
        self.assertGreater(len(shed), 0)
        self.assertTrue(all(isinstance(r["retry_after"], int) and r["retry_after"] >= 1 for r in shed))

    def test_goodput_beats_the_unbounded_queue(self):
        self.assertEqual(self.s["goodput"], self.s["ok"])  # every 200 arrives before the 1 s client timeout
        self.assertGreater(self.s["goodput"], 8000)  # unbounded: 3781

    def test_no_shedding_under_normal_load(self):
        s = bp.summary(simulate(bp.Server(), [(20, 0.6 * bp.CAPACITY)], bp.SERVICE_MS))
        self.assertEqual(s["shed"], 0)


if __name__ == "__main__":
    unittest.main()
