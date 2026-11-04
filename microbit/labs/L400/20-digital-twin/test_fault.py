"""failureLab symptom (observed, seeded): the memoryless 2-sigma twin (twin.py).

PASSES because it pins the failure: it finds both drifts, but it also raises 13 false alarms on the
20-minute classroom run and 80 per 1,000 nominal windows - an alarm nobody will keep reading.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import drift_eval  # noqa: E402


class Symptom(unittest.TestCase):
    def test_cries_wolf(self):
        s = drift_eval.summary("twin.py")
        self.assertEqual(s["false_alarms_fixture"], 13)
        self.assertEqual(s["false_alarms_per_1000_synthetic"], 80)
        self.assertEqual(s["detected_after_windows"], {"n3 DRIFT_TEMP": 7, "n5 DRIFT_LAT": 7})


if __name__ == "__main__":
    unittest.main(verbosity=2)
