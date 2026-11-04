"""Build task check (lab 17): six (and 24) boards share one relay without losing readings.

Runs solution.py. Check YOUR file: BUILD_TARGET=mine python -m unittest test_build_task
(= node.py, which FAILS as shipped; or BUILD_FILE=<file>). Windows PowerShell:
$env:BUILD_TARGET="mine"; py -m unittest test_build_task
"""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import edge_sim  # noqa: E402

TARGET = os.environ.get("BUILD_FILE") or ("node.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution.py")


class Classroom(unittest.TestCase):
    def test_frames_still_fit_after_a_school_day(self):
        from labtest import load_boards
        (b,) = load_boards(str(Path(__file__).resolve().parent), names=("n1",), filename=TARGET)
        text = b.lab.encode("D", "n12", 99999, "%d,-10,255,1" % (8 * 3600 * 1000))   # 8 h of samples
        self.assertLessEqual(len(text) + 3, b.radio._cfg["length"])                   # 3-byte string header

    def test_six_boards_deliver_everything_fast(self):
        res, _ = edge_sim.run(TARGET)
        self.assertGreaterEqual(res["delivery_pct"], 99.0)
        self.assertLessEqual(res["p95_ms"], 2000)
        self.assertEqual(res["gave_up"], 0)

    def test_24_boards_still_deliver(self):
        n = 24
        res, _ = edge_sim.run(TARGET, n=n, loss={"n%d" % (i + 1): 0.10 for i in range(n)}, readings=20)
        self.assertGreaterEqual(res["delivery_pct"], 99.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
