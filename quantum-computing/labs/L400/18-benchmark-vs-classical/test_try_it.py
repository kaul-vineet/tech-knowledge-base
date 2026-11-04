"""Tests for lab 18 try-it items and the Qiskit path (CI). Run: python -m unittest -v"""
import importlib.util
import os
import unittest

import try_it

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class TryIt(unittest.TestCase):
    def test_qaoa_win_does_not_generalise(self):
        self.assertEqual(try_it.other_instances(), {1: "annealing", 2: "greedy", 3: "qaoa", 4: "annealing", 5: "annealing"})

    def test_exact_budget(self):
        self.assertEqual(try_it.exact_in_budget(), ({"greedy": 1.0, "annealing": 1.0, "qaoa": 1.0, "exact": 1.0}, "greedy"))


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class QiskitPath(unittest.TestCase):
    def test_sampled_cut_distribution_matches_numpy(self):
        import bench_qiskit
        out = bench_qiskit.compare_distributions()
        self.assertLess(out["tvd"], 0.05)


if __name__ == "__main__":
    unittest.main()
