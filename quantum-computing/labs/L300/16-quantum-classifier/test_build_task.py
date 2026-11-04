"""Build-task check for lab 16 (the hardening change). Run: python -m unittest test_build_task -v

Checks solution_init.py by default; to check your own file set BUILD_TASK_MODULE, e.g.
  macOS:   BUILD_TASK_MODULE=my_init python -m unittest test_build_task -v
  Windows: $env:BUILD_TASK_MODULE = "my_init"; python -m unittest test_build_task -v
failureLab proof: BUILD_TASK_MODULE=classifier_lab (uniform random init) FAILS test_wide_deep_model_has_usable_gradients.
"""
import importlib
import os
import unittest

import classifier_lab as lab

mod = importlib.import_module(os.environ.get("BUILD_TASK_MODULE", "solution_init"))


class NearIdentityInit(unittest.TestCase):
    def test_wide_deep_model_has_usable_gradients(self):
        scan = lab.gradient_scan(10, 20, init=mod.init_weights, samples=10)
        self.assertGreater(scan["median_abs_grad"], 10 * lab.SHOT_FLOOR)
        self.assertEqual(scan["below_shot_floor"], 0.0)

    def test_small_model_still_learns(self):
        train_acc, test_acc, _ = lab.train_quantum(*lab.make_dataset(), init=mod.init_weights)
        self.assertGreaterEqual(train_acc, 0.9)
        self.assertGreaterEqual(test_acc, 0.85)


if __name__ == "__main__":
    unittest.main()
