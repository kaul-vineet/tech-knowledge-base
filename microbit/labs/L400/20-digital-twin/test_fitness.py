"""Fitness function (lab 20): keeps ADR-0020 true.

On nominal windows drawn from the twin's own model (2 links: 4 % and 10 % loss, 3 seeds each) the
CUSUM check raises at most 5 alarms per 1,000 windows, and on the recorded classroom telemetry it
finds both seeded drifts within 10 windows (5 minutes).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import drift_eval  # noqa: E402


class Fitness(unittest.TestCase):
    def test_false_alarm_rate(self):
        for loss in (0.04, 0.10):
            for seed in (1, 2, 3):
                with self.subTest(loss=loss, seed=seed):
                    self.assertLessEqual(drift_eval.synthetic_false_alarms("solution.py", seed=seed, loss=loss), 5)

    def test_detection_delay(self):
        m, _ = drift_eval.run("solution.py")
        self.assertEqual(len(m["detected"]), 2)
        self.assertLessEqual(max(m["detected"].values()), 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
