"""Stretch check (lesson 12): urgency-first scheduling observes more targets than 'lowest airmass now'.

Checks solution/urgent.py; BUILD_TARGET=mine checks urgent.py in this folder (your copy).
"""
import importlib.util
import os
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("urgent.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/urgent.py")
spec = importlib.util.spec_from_file_location("urgent_under_test", TARGET)
urgent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(urgent)


class TestUrgencyFirst(unittest.TestCase):
    def test_more_targets_than_greedy_and_altair_first(self):
        rows, left = urgent.schedule_urgent()
        self.assertGreaterEqual(len(rows), 4)
        self.assertEqual(rows[0]["target"], "Altair")
        self.assertTrue(all(r["alt_deg"] >= 30 for r in rows))


if __name__ == "__main__":
    unittest.main()
