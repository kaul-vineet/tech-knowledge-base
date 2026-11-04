"""Stretch check (lesson 15): asymmetric posteriors are flagged; symmetric ones are not.

Checks solution/report.py; BUILD_TARGET=mine checks report.py in this folder (your copy).
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("report.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/report.py")
spec = importlib.util.spec_from_file_location("report_under_test", TARGET)
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


class TestReport(unittest.TestCase):
    def test_flags(self):
        rng = np.random.default_rng(0)
        post = np.column_stack([rng.normal(0, 1, 50_000), rng.lognormal(0, 0.6, 50_000)])
        rows = report.summarise(post, ["gauss", "skewed"])
        self.assertEqual([r["gaussian"] for r in rows], [True, False])


if __name__ == "__main__":
    unittest.main()
