"""Build-task check for lab 14 (the hardening change). Run: python -m unittest test_build_task -v

Checks solution_restarts.py by default; to check your own file set BUILD_TASK_MODULE, e.g.
  macOS:   BUILD_TASK_MODULE=my_restarts python -m unittest test_build_task -v
  Windows: $env:BUILD_TASK_MODULE = "my_restarts"; python -m unittest test_build_task -v
failureLab proof: BUILD_TASK_MODULE=qaoa_lab (one random start) FAILS test_p2_reaches_best_known_ratio.
"""
import importlib
import os
import unittest

import qaoa_lab as lab

mod = importlib.import_module(os.environ.get("BUILD_TASK_MODULE", "solution_restarts"))


class Restarts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p1, cls.p2 = mod.solve(1, seed=0), mod.solve(2, seed=0)

    def test_p1_reaches_grid_quality(self):
        self.assertGreaterEqual(lab.ratio(self.p1), 0.82)

    def test_p2_reaches_best_known_ratio(self):
        self.assertGreaterEqual(lab.ratio(self.p2), 0.92)

    def test_deeper_circuit_is_not_worse(self):
        self.assertGreaterEqual(lab.ratio(self.p2), lab.ratio(self.p1))


if __name__ == "__main__":
    unittest.main()
