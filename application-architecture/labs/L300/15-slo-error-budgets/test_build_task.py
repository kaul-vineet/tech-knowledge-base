"""Build task check (lesson 15): a latency SLI ("99% of POST /loans < 300 ms") pages during the slow-tail incident.

By default this checks solution/slo.py. To check your edited slo.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import importlib.util
import os
import pathlib
import unittest

from failure_lab import check
from traffic import INCIDENT_START

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("slo.py" if os.environ.get("CHECK_MINE") else "solution/slo.py")
spec = importlib.util.spec_from_file_location("slo_under_test", TARGET)
slo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(slo)


class LatencySliTest(unittest.TestCase):
    def test_slow_tail_pages_on_the_latency_sli(self):
        fired = check(slo)[2]
        self.assertEqual([(a["sli"], a["severity"], a["windows"]) for a in fired], [("latency", "page", "1h/5m")])
        self.assertAlmostEqual(fired[0]["burn_long"], 19.7)

    def test_latency_slo_is_99_percent_of_post_loans_under_300_ms(self):
        self.assertEqual(slo.SLOS["latency"], 0.99)
        is_valid, is_good = slo.SLIS["latency"]
        self.assertTrue(is_good({"route": "POST /loans", "status": 200, "ms": 299.9}))
        self.assertFalse(is_good({"route": "POST /loans", "status": 200, "ms": 300.0}))
        self.assertFalse(is_valid({"route": "GET /books", "status": 200, "ms": 10.0}))

    def test_quiet_before_the_incident_and_on_healthy_traffic(self):
        self.assertEqual(check(slo, now=INCIDENT_START.timestamp())[2], [])
        self.assertEqual(check(slo, incident=False)[2], [])


if __name__ == "__main__":
    unittest.main()
