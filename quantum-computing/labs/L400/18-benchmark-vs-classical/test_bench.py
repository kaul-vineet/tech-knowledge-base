"""Tests for lab 18 solvers and metrics. Run: python -m unittest -v"""
import unittest

import bench_lab as lab
import solution_fair as fair
import solvers as S


class Solvers(unittest.TestCase):
    def test_reference_optima(self):
        self.assertEqual([lab.instance(n)[1] for n in lab.SIZES], [10, 15, 22])

    def test_budgeted_solvers_respect_budget_and_seed(self):
        edges, _ = lab.instance(12)
        for name, solve in S.BUDGETED.items():
            a, b = solve(12, edges, 200, 3), solve(12, edges, 200, 3)
            self.assertEqual(a, b, name)                     # seeded: same seed, same answer
            self.assertLessEqual(a["used"], 200, name)

    def test_tts99(self):
        self.assertEqual(lab.tts99(0.5, 200), 1329)
        self.assertEqual(lab.tts99(1.0, 200), 200)
        self.assertIsNone(lab.tts99(0.0, 200))

    def test_ties_go_to_the_classical_baseline(self):
        row = {"median_ratio": 1.0, "success": 1.0, "median_first_best": 50}
        self.assertEqual(lab.decide([{**row, "solver": "qaoa"}, {**row, "solver": "greedy"}]), "greedy")


class Observed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.naive = {n: lab.compare(n)[1] for n in (12, 16)}
        cls.fair = {n: fair.compare(n) for n in (12, 16)}

    def test_naive_method_claims_a_quantum_win(self):
        self.assertEqual(self.naive[12], "qaoa")

    def test_fair_results(self):
        rows, winner = self.fair[12]
        self.assertEqual({r["solver"]: (r["median_ratio"], r["success"]) for r in rows},
                         {"greedy": (0.9333, 0.4), "annealing": (0.9333, 0.3), "qaoa": (0.9667, 0.5)})
        self.assertEqual(winner, "qaoa")                     # one instance, sample budget, noiseless
        self.assertEqual(self.fair[16][1], "greedy")


if __name__ == "__main__":
    unittest.main()
