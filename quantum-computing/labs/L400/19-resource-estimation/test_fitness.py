"""Fitness function for lab 19: keeps the feasibility decision (docs/adr/0001-feasibility-gate.md) true.
Run: python -m unittest test_fitness -v    (same BUILD_TARGET / BUILD_TASK_MODULE switch as test_build_task)

Thresholds: every estimate has p_fail <= 0.01 · nothing 'fault-tolerant-feasible' above 1,000,000 physical qubits
or 1 day · the reference decision table below does not change without a new ADR.
"""
import unittest

import buildtarget
import estimate_lab as lab

mod = buildtarget.load("solution_distance", "my_distance")
EXPECTED = ["simulate", "nisq-candidate", "fault-tolerant-feasible", "fault-tolerant-feasible",
            "infeasible (assumptions above)", "infeasible (assumptions above)"]


class FeasibilityFitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [lab.physical(w, choose=mod.choose_distance) for w in lab.WORKLOADS]

    def test_every_estimate_meets_the_error_budget(self):
        self.assertTrue(all(r["p_fail"] <= lab.BUDGET for r in self.rows), [r["p_fail"] for r in self.rows])

    def test_feasible_means_within_thresholds(self):
        for r in self.rows:
            if lab.classify(r) == "fault-tolerant-feasible":
                self.assertLessEqual(r["physical_qubits"], lab.THRESHOLDS["max_physical"])
                self.assertLessEqual(r["runtime_s"], lab.THRESHOLDS["max_runtime_s"])

    def test_decision_table(self):
        self.assertEqual([lab.classify(r) for r in self.rows], EXPECTED)


if __name__ == "__main__":
    unittest.main()
