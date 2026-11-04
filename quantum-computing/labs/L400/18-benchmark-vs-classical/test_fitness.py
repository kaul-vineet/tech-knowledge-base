"""Fitness function for lab 18: guards the COMPARISON METHOD (docs/adr/0001-fair-benchmark.md).
Run: python -m unittest test_fitness -v    (same BUILD_TARGET / BUILD_TASK_MODULE switch as test_build_task)

Thresholds: one budget for all solvers (equality) · >= 10 identical seeds · used <= budget on every run ·
a classical baseline and the exact optimum in every report · same inputs -> same report (reproducible).
"""
import unittest

import bench_lab as lab
import buildtarget

mod = buildtarget.load("solution_fair", "my_fair")


def strip(rows):
    return [{k: v for k, v in r.items() if k != "local_s"} for r in rows]


class ComparisonMethodFitness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.winner = mod.compare(12)
        cls.again = mod.compare(12)

    def test_reference_config(self):
        self.assertGreaterEqual(len(lab.SEEDS), 10)
        self.assertEqual({r["budget"] for r in self.rows}, {lab.BUDGET})
        self.assertEqual({r["runs"] for r in self.rows}, {len(lab.SEEDS)})

    def test_classical_baseline_present(self):
        self.assertTrue(set(lab.CLASSICAL) <= {r["solver"] for r in self.rows})
        self.assertEqual(lab.instance(12)[1], 15)

    def test_reproducible(self):
        self.assertEqual(strip(self.rows), strip(self.again[0]))
        self.assertEqual(self.winner, self.again[1])


if __name__ == "__main__":
    unittest.main()
