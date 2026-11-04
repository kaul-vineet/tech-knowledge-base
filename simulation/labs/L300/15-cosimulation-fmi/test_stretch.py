"""Stretch check (lesson 15): the self-guarding master.

By default this checks solution/guarded_master.py. To check your own guarded_master.py (in this folder) instead:
    BUILD_TARGET=mine python -m unittest test_stretch -v        (PowerShell: $env:BUILD_TARGET = "mine")
"""
import json
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"))
import guarded_master as SOLUTION  # noqa: E402


class TestGuardedMaster(unittest.TestCase):
    def test_halves_until_the_loop_settles(self):
        events = []
        h, m = SOLUTION.run_guarded(900, log=events.append)
        self.assertEqual(h, 225.0)
        self.assertLess(m["last_hour_swing_C"], 0.2)
        self.assertEqual([json.loads(e)["event"] for e in events], ["step_halved", "step_halved", "accepted"])

    def test_a_good_step_is_kept(self):
        self.assertEqual(SOLUTION.run_guarded(60, log=lambda e: None)[0], 60)

    def test_gives_up_instead_of_looping_forever(self):
        events = []
        SOLUTION.run_guarded(900, min_h=600, log=events.append)
        self.assertEqual(json.loads(events[-1])["event"], "gave_up")


if __name__ == "__main__":
    unittest.main()
