"""Build task check (lab 20): a drift check with memory (CUSUM) on the twin's z-scores.

Runs solution.py. Check YOUR file: BUILD_TARGET=mine python -m unittest test_build_task
(= twin.py, which FAILS as shipped; or BUILD_FILE=<file>). Windows PowerShell:
$env:BUILD_TARGET="mine"; py -m unittest test_build_task
"""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import drift_eval  # noqa: E402

TARGET = os.environ.get("BUILD_FILE") or ("twin.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution.py")


class DriftCheck(unittest.TestCase):
    def test_finds_both_drifts_within_ten_windows(self):
        m, _ = drift_eval.run(TARGET)
        self.assertEqual(set(m["detected"]), {"n3 DRIFT_TEMP", "n5 DRIFT_LAT"})
        self.assertLessEqual(max(m["detected"].values()), 10)

    def test_rarely_cries_wolf(self):
        self.assertLessEqual(drift_eval.run(TARGET)[0]["false_alarms"], 2)
        self.assertLessEqual(drift_eval.synthetic_false_alarms(TARGET), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
