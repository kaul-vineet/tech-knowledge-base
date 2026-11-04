"""Build task check (lesson 13): with a hung catalogue, every borrow still succeeds (fallback title) and fast.

By default this checks solution/loans_service.py. To check your edited loans_service.py instead:
    CHECK_MINE=1 python -m unittest test_build_task -v        (PowerShell: $env:CHECK_MINE = "1")
"""
import importlib.util
import os
import pathlib
import unittest

from deps import Catalogue
from failure_lab import run_waves, summary

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / ("loans_service.py" if os.environ.get("CHECK_MINE") else "solution/loans_service.py")
spec = importlib.util.spec_from_file_location("loans_service_under_test", TARGET)
ls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls)


class BulkheadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = run_waves(ls, Catalogue(mode="slow"))

    def test_every_borrow_succeeds_with_a_fallback_title(self):
        self.assertEqual(summary(self.records), {1: {"ok": 8}, 2: {"ok": 8}, 3: {"ok": 8}})
        self.assertTrue(all(r["degraded"] for r in self.records))

    def test_no_request_waits_much_longer_than_the_timeout(self):
        self.assertLess(max(r["ms"] for r in self.records), 300)

    def test_members_has_its_own_pool(self):
        pools = self.records[0]["pools"]
        self.assertEqual(len(pools), 2, f"expected one pool per dependency, got {pools}")


if __name__ == "__main__":
    unittest.main()
