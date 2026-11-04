"""Build task check (lesson 21): size for the peak with headroom and one spare instance.

By default this checks solution/capacity.py. To check your edited capacity.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import importlib.util
import os
import pathlib
import unittest

import fitness_capacity
import l300_log

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("capacity.py" if os.environ.get("CHECK_MINE") else "solution/capacity.py")
spec = importlib.util.spec_from_file_location("capacity_under_test", TARGET)
cap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cap)
MODEL = cap.load_model(l300_log.records())


class SizingTest(unittest.TestCase):
    def test_three_instances_for_the_async_option(self):
        self.assertEqual(cap.instances_needed(MODEL, 75), 3)

    def test_six_instances_if_email_stays_synchronous(self):
        self.assertEqual(cap.instances_needed(cap.with_sync_email(MODEL), 35), 6)

    def test_slo_holds_with_one_instance_down(self):
        result = fitness_capacity.gate(cap)
        self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
