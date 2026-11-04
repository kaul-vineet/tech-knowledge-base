"""failureLab symptom (modelled): main.py flattens 2 x AAA in under 2 days."""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import budget  # noqa: E402


class Symptom(unittest.TestCase):
    def test_battery_lasts_hours_not_a_month(self):
        d = json.loads(budget.report("main.py"))
        self.assertEqual((d["samples"], d["avg_ma"], d["life_h"]), (36000, 30.0, 41.7))
        self.assertFalse(d["meets_brief"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
