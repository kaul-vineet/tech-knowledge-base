"""Fitness function (lesson 17 ADR 0001): keeps the decision "Kalman filter + CUSUM + recalibration" true.

Replays the committed feed and fails the build if the twin stops meeting the brief:
  no false alarm before the drift; drift detected within 60 min; recalibrated a within 15% of the plant's 0.035;
  last-day 1-h forecast RMSE <= 0.15 C AND better than the filter-only option (B).
Default target: solution/twin.py; BUILD_TARGET=mine checks your twin.py (the shipped file fails).
"""
import importlib.util
import os
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("twin.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/twin.py")
spec = importlib.util.spec_from_file_location("twin_fitness", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)
DRIFT_T = 2500


class TestTwinFitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.twin, cls.errors = target.run()
        _, cls.filter_only = target.run(target.Twin(recalibrate=False))

    def alarms(self):
        return [e["t_min"] for e in self.twin.events if e["event"] == "drift_alarm"]

    def test_no_false_alarms(self):
        self.assertEqual([t for t in self.alarms() if t < DRIFT_T], [])

    def test_detection_delay_within_one_hour(self):
        self.assertLessEqual(min(t for t in self.alarms() if t >= DRIFT_T) - DRIFT_T, 60)

    def test_recalibrated_physics_matches_the_plant(self):
        self.assertLess(abs(self.twin.a - 0.035) / 0.035, 0.15)

    def test_forecast_beats_threshold_and_filter_only(self):
        mine, other = target.rmse(self.errors, 2880), target.rmse(self.filter_only, 2880)
        self.assertLessEqual(mine, 0.15)
        self.assertLess(mine, other)


if __name__ == "__main__":
    unittest.main()
