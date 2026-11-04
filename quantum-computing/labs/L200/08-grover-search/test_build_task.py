"""Build-task check for lab 08. Run: python -m unittest test_build_task -v

Checks solution_search.py by default; to check your own file set BUILD_TASK_MODULE, e.g.
  macOS:   BUILD_TASK_MODULE=my_search python -m unittest test_build_task -v
  Windows: $env:BUILD_TASK_MODULE = "my_search"; python -m unittest test_build_task -v
"""
import importlib
import importlib.util
import os
import unittest

mod = importlib.import_module(os.environ.get("BUILD_TASK_MODULE", "solution_search"))
HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None


class SearchNumpy(unittest.TestCase):
    def test_single_value(self):
        self.assertEqual(mod.grover_search_numpy(lambda x: x == 5, 3), (["101"], 2, 0.9453))

    def test_three_marked(self):
        self.assertEqual(mod.grover_search_numpy(lambda x: x % 3 == 0, 3), (["000", "011", "110"], 1, 0.8437))

    def test_half_or_none_marked_is_refused(self):
        for predicate in (lambda x: x % 2 == 0, lambda x: False):
            with self.assertRaises(ValueError):
                mod.grover_search_numpy(predicate, 3)


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class SearchSdk(unittest.TestCase):
    def test_qiskit_search(self):
        marked, k, p, top = mod.grover_search(lambda x: x == 5, 3)
        self.assertEqual((marked, k, top), (["101"], 2, "101"))
        self.assertAlmostEqual(p, 0.9453, places=3)


if __name__ == "__main__":
    unittest.main()
