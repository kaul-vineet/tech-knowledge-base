"""Capstone fitness functions (keep ADRs 0001-0004 true). Run: python -m unittest test_fitness -v

Thresholds: modelled wall <= 60 s and exactly 1 transpile per request (ADR 0001) · winner == code's decide() and a
tie never goes to the quantum solver (ADR 0002) · mitigated error < raw error (ADR 0003) · a request larger than the
device never reaches the quantum path (ADR 0004) · every rubric line passes.
"""
import unittest

import run_capstone as rc
from reuse import l18_bench


class CapstoneFitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = rc.collect()
        cls.rep = cls.o["default"][1]

    def test_execution_budget(self):
        self.assertLessEqual(self.rep["execution"]["wall_s"], 60)
        self.assertEqual(self.rep["execution"]["transpiles"], 1)

    def test_code_decides_and_ties_go_classical(self):
        self.assertEqual(self.rep["winner"], l18_bench.decide(self.rep["benchmark"]))
        tied = [{**r, "median_ratio": 1.0, "success": 1.0, "median_first_best": 10} for r in self.rep["benchmark"]]
        self.assertIn(l18_bench.decide(tied), l18_bench.CLASSICAL)

    def test_mitigation_helps(self):
        m = self.rep["mitigation"]
        self.assertLess(abs(m["mitigated"] - m["gate_noise_only"]), abs(m["raw"] - m["gate_noise_only"]))

    def test_feasibility_gate(self):
        self.assertFalse(self.o["large"][1]["feasibility"]["quantum_path"])
        self.assertNotIn("qaoa-noisy", {r["solver"] for r in self.o["large"][1]["benchmark"]})

    def test_rubric(self):
        self.assertEqual([ok for _, _, ok in rc.rubric(self.o)], [True] * 6)


if __name__ == "__main__":
    unittest.main()
