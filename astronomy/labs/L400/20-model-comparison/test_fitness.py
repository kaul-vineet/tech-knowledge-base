"""Fitness function (lesson 20, ADR 0001): keeps "select by BIC, then check the residuals" true.

Over 50 seeded galaxies (truth: disk + cored halo) select() must pick a 3-parameter halo model at least 95% of the
time and never the 6-parameter wiggles model; the published fit must leave residuals without structure
(|runs Z| < 1.96) while the disk-only fit must fail that test.
Default target: solution/compare.py; BUILD_TARGET=mine checks your compare.py (the shipped file fails).
"""
import importlib.util
import os
import unittest
from pathlib import Path

import galaxy as g

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("compare.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/compare.py")
spec = importlib.util.spec_from_file_location("compare_fitness", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestSelectionFitness(unittest.TestCase):
    def test_selection_rate(self):
        picks = [target.select(g.R, *g.observed(seed=s))[0] for s in range(100, 150)]
        halo = sum(p in ("disk + cored halo", "disk + NFW halo") for p in picks)
        self.assertGreaterEqual(halo / len(picks), 0.95)
        self.assertNotIn("disk + halo + wiggles", picks)

    def test_residuals_of_published_and_rejected_models(self):
        v, err = g.observed()
        best, rows = target.select(g.R, v, err)
        by = {r["model"]: r for r in rows}
        self.assertLess(abs(by[best]["runs_z"]), 1.96)
        self.assertGreater(abs(by["disk only"]["runs_z"]), 1.96)


if __name__ == "__main__":
    unittest.main()
