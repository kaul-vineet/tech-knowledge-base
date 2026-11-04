"""Fitness function (lesson 18 ADR 0001): keeps "grid search + OCBA clean-up on fresh CRN streams" true.

Fails the build if: any optimiser spends more than the shared budget; the chosen method's mean optimality gap
over 5 macro-replications exceeds 0.06/day or its worst gap 0.10/day (the indifference zone); or the reported
cost is biased by more than 0.15/day over 12 macro-replications (the winner's curse is back).
Default target: solution/optimise.py; BUILD_TARGET=mine checks your optimise.py (the shipped file fails 2 of 3).
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("optimise.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/optimise.py")
spec = importlib.util.spec_from_file_location("optimise_fitness", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)
DELTA = 0.10  # indifference zone: cost differences below 0.10/day do not matter to the shop


class TestOptimisationFitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = [target.optimise(target.grid_search, m) for m in range(12)]

    def test_budget_fairness_across_methods(self):
        for method in (target.grid_search, target.surrogate_search, target.evolution):
            with self.subTest(method=method.__name__):
                self.assertLessEqual(target.optimise(method, 0)["runs"], target.BUDGET)

    def test_chosen_design_within_the_indifference_zone(self):
        gaps = [r["gap"] for r in self.grid[:5]]
        self.assertLessEqual(np.mean(gaps), 0.06)
        self.assertLessEqual(max(gaps), DELTA)

    def test_reported_cost_is_unbiased(self):
        self.assertLessEqual(abs(np.mean([r["reported"] - r["true"] for r in self.grid])), 0.15)


if __name__ == "__main__":
    unittest.main()
