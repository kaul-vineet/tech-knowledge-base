"""Build-task check for lab 15 (the hardening change). Run: python -m unittest test_build_task -v

Checks solution_spsa.py by default; to check your own file set BUILD_TASK_MODULE, e.g.
  macOS:   BUILD_TASK_MODULE=my_spsa python -m unittest test_build_task -v
  Windows: $env:BUILD_TASK_MODULE = "my_spsa"; python -m unittest test_build_task -v
failureLab proof: BUILD_TASK_MODULE=vqe_lab (finite-difference descent) FAILS test_converges_under_shot_noise.
"""
import importlib
import os
import unittest

mod = importlib.import_module(os.environ.get("BUILD_TASK_MODULE", "solution_spsa"))


class RobustOptimizer(unittest.TestCase):
    def test_converges_under_shot_noise(self):
        for seed in range(4):
            self.assertLess(mod.vqe(1000, seed=seed)[1], 0.03, f"seed {seed}")

    def test_still_works_without_noise(self):
        self.assertLess(mod.vqe(None)[1], 0.03)


if __name__ == "__main__":
    unittest.main()
