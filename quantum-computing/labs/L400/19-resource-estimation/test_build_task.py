"""Build-task check for lab 19 (code distance from the error budget). Run: python -m unittest test_build_task -v

Checks solution_distance.py by default. Your file: my_distance.py with choose_distance(p, logical_qubits, cycles, budget=0.01)
  macOS:   BUILD_TARGET=mine python -m unittest test_build_task -v
  Windows: $env:BUILD_TARGET = "mine"; python -m unittest test_build_task -v
failureLab proof: BUILD_TASK_MODULE=estimate_lab (fixed d = 3) FAILS 3 of 4 tests.
"""
import unittest

import buildtarget
import estimate_lab as lab

mod = buildtarget.load("solution_distance", "my_distance")


class Distance(unittest.TestCase):
    def test_rsa_2048_needs_distance_27(self):
        r = lab.rsa_logical(2048)
        self.assertEqual(mod.choose_distance(1e-3, r["logical_qubits"], r["logical_cycles"]), 27)

    def test_meets_the_budget_and_is_minimal(self):
        q, cycles = 100, 1253
        d = mod.choose_distance(1e-3, q, cycles)
        self.assertEqual(d % 2, 1)
        self.assertLessEqual(q * cycles * lab.logical_error(d), lab.BUDGET)
        self.assertGreater(q * cycles * lab.logical_error(d - 2), lab.BUDGET)

    def test_refuses_above_threshold(self):
        with self.assertRaises(ValueError):
            mod.choose_distance(0.011, 100, 1000)

    def test_longer_programs_never_get_a_smaller_code(self):
        ds = [mod.choose_distance(1e-3, 100, cycles) for cycles in (10, 10 ** 4, 10 ** 8)]
        self.assertEqual(ds, sorted(ds))


if __name__ == "__main__":
    unittest.main()
