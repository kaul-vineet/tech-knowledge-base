"""Build-task check for lab 18 (fair comparison harness). Run: python -m unittest test_build_task -v

Checks solution_fair.py by default. Your file: my_fair.py with compare(n, solvers, budget, seeds) -> (rows, winner)
  macOS:   BUILD_TARGET=mine python -m unittest test_build_task -v
  Windows: $env:BUILD_TARGET = "mine"; python -m unittest test_build_task -v
failureLab proof: BUILD_TASK_MODULE=bench_lab (naive compare) FAILS 3 of 3 tests.
"""
import unittest

import buildtarget

mod = buildtarget.load("solution_fair", "my_fair")


def spy(log, name, overspend=1):
    def solve(n, edges, budget, seed):
        log.append((name, budget, seed))
        return {"cut": 1, "used": budget * overspend, "first_best": 1}
    return solve


class FairHarness(unittest.TestCase):
    def test_same_budget_and_seeds_for_every_solver(self):
        log = []
        mod.compare(8, {k: spy(log, k) for k in ("greedy", "annealing", "qaoa")}, budget=100, seeds=(1, 2, 3))
        calls = {k: [(b, s) for name, b, s in log if name == k] for k in ("greedy", "annealing", "qaoa")}
        self.assertEqual(calls["greedy"], [(100, 1), (100, 2), (100, 3)])
        self.assertEqual(calls["qaoa"], calls["greedy"])
        self.assertEqual(calls["annealing"], calls["greedy"])

    def test_over_budget_solver_is_rejected(self):
        with self.assertRaises(RuntimeError):
            mod.compare(8, {"greedy": spy([], "greedy"), "qaoa": spy([], "qaoa", overspend=2)}, budget=100, seeds=(1,))

    def test_rows_summarise_every_run(self):
        rows, _ = mod.compare(8, {"greedy": spy([], "greedy"), "qaoa": spy([], "qaoa")}, budget=100, seeds=(1, 2, 3, 4))
        self.assertEqual([r["runs"] for r in rows], [4, 4])


if __name__ == "__main__":
    unittest.main()
