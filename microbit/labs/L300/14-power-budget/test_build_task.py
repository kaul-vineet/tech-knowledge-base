"""Build task check (lab 14): adaptive sampling + Deep Sleep meets the brief in the model.

Runs solution.py. To check YOUR version: BUILD_FILE=main.py python -m unittest test_build_task
(Windows PowerShell: $env:BUILD_FILE="main.py"; py -m unittest test_build_task)
main.py as shipped FAILS this check: that is the failureLab "before".
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab  # noqa: E402
import budget  # noqa: E402

BUILD_FILE = os.environ.get("BUILD_FILE", "solution.py")


class Adaptive(unittest.TestCase):
    def test_meets_the_brief(self):
        d = json.loads(budget.report(BUILD_FILE))
        self.assertTrue(d["meets_brief"], d)
        self.assertGreaterEqual(d["life_h"], budget.REQUIRED_HOURS)
        self.assertLessEqual(d["max_delay_ms"], budget.MAX_DETECT_MS)

    def test_interval_backs_off_and_resets(self):
        lab = load_lab(HERE, BUILD_FILE)
        seq, iv = [], lab.MIN_MS
        for _ in range(9):
            iv = lab.next_interval(iv, False)
            seq.append(iv)
        self.assertEqual(seq, [200, 400, 800, 1600, 3200, 6400, 8000, 8000, 8000])
        self.assertEqual(lab.next_interval(8000, True), 100)

    def test_board_deep_sleeps_between_samples(self):
        run = budget.run_design(BUILD_FILE, run_ms=60000)
        self.assertEqual(run["wakeups"], len(run["samples"]))
        self.assertGreater(run["slept_ms"], 59000)

    def test_tradeoff_short_spike_can_be_missed(self):
        # documented trade-off: a 1.5 s spike between two samples 8 s apart is never seen
        spike = [(0, 20), (101000, 30), (102500, 20)]
        run = budget.run_design(BUILD_FILE, trace=spike, run_ms=120000)
        seen = [v for _, v in run["samples"]]
        self.assertFalse(30 in seen, "the spike was sampled")


if __name__ == "__main__":
    unittest.main(verbosity=2)
