"""buildTask check (lesson 16): tasks_for() must give every replication its own stream, whatever the worker count.

By default this checks solution/perf.py. To check your edited perf.py instead:
    BUILD_TARGET=mine python -m unittest test_build_task -v        (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 2 of 3 tests fail; after your fix all 3 pass.
"""
import importlib.util
import os
import unittest
from pathlib import Path

import numpy as np

import perf as reference  # importable by name, so spawned workers can unpickle reference.one_replication

HERE = Path(__file__).resolve().parent
TARGET = HERE / ("perf.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/perf.py")
spec = importlib.util.spec_from_file_location("perf_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


class TestStreamPerReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.one = reference.run_parallel(target.tasks_for(6), 1)
        cls.two = reference.run_parallel(target.tasks_for(6), 2)

    def test_every_replication_is_distinct(self):
        self.assertEqual(len(set(self.two.tolist())), 6)

    def test_confidence_interval_has_real_width(self):
        self.assertGreater(reference.ci(self.two)[1], 0.01)

    def test_same_results_on_one_or_two_workers(self):
        np.testing.assert_array_equal(self.one, self.two)


if __name__ == "__main__":
    unittest.main()
