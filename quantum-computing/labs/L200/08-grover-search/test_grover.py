"""Tests for lab 08. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import os
import unittest

import crosscheck_numpy as cc

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class CrossCheck(unittest.TestCase):
    def test_two_qubits_one_iteration_is_certain(self):
        self.assertEqual(cc.success(["11"], 1), 1.0)

    def test_three_qubits_curve(self):
        self.assertEqual([cc.success(["101"], k) for k in range(4)], [0.125, 0.7812, 0.9453, 0.3301])
        self.assertEqual(cc.optimal_iterations(1, 3), 2)

    def test_oracle_gates_flip_only_marked(self):
        self.assertEqual(cc.oracle_gates_diagonal(["011", "100"]), [1, 1, 1, -1, -1, 1, 1, 1])


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class SdkLab(unittest.TestCase):
    def test_success_matches_numpy(self):
        import grover_lab
        for marked in (["11"], ["101"], ["011", "100"]):
            for k in range(4):
                self.assertAlmostEqual(grover_lab.success_probability(marked, k), cc.success(marked, k), places=3)

    def test_oracle_is_the_numpy_diagonal(self):
        import numpy as np
        from qiskit.quantum_info import Operator

        import grover_lab
        diag = np.real_if_close(np.diag(Operator(grover_lab.grover_oracle(["011", "100"])).data))
        self.assertEqual(np.round(diag).astype(int).tolist(), cc.oracle_gates_diagonal(["011", "100"]))

    def test_marked_state_wins_the_counts(self):
        import grover_lab
        counts = grover_lab.counts(["101"], 2)
        self.assertEqual(max(counts, key=counts.get), "101")
        self.assertGreater(counts["101"], 900)


if __name__ == "__main__":
    unittest.main()
