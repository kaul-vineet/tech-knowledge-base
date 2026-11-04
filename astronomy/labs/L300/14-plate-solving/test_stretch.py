"""Stretch check (lesson 14): a 0.8 deg pointing error still solves with a ring search.

Checks solution/search.py; BUILD_TARGET=mine checks search.py in this folder (your copy).
"""
import importlib.util
import os
import unittest
from pathlib import Path

import fields

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("search.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/search.py")
spec = importlib.util.spec_from_file_location("search_under_test", TARGET)
search = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search)


class TestSearch(unittest.TestCase):
    def test_bad_hint_solves_after_search(self):
        ra0, dec0 = fields.FIELDS["orion"]["center"]
        result, tried = search.solve_with_search("orion", (ra0 + 0.8, dec0))
        self.assertTrue(result["solved"])
        self.assertLess(result["pointing_error_arcsec"], 1.0)
        self.assertLessEqual(tried, 19)


if __name__ == "__main__":
    unittest.main()
