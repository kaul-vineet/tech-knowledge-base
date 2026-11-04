"""Tests for lab 14. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import os
import unittest

import numpy as np

import qaoa_lab as lab

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None and importlib.util.find_spec("scipy") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit/scipy is not installed")


class Qaoa(unittest.TestCase):
    def test_brute_force_optimum(self):
        best, strings = lab.brute_force()
        self.assertEqual((best, strings), (5.0, ["01001", "01011", "10100", "10110"]))

    def test_zero_angles_give_random_guessing(self):
        self.assertAlmostEqual(-lab.cost([0.0, 0.0]), 3.0)          # each of 6 edges cut with probability 1/2

    def test_state_is_normalised(self):
        self.assertAlmostEqual(float(np.sum(np.abs(lab.qaoa_state([0.3, 1.1, 0.2, 0.7])) ** 2)), 1.0)

    def test_grid_finds_p1_region(self):
        g, b, grid = lab.landscape()
        self.assertEqual((round(g, 4), round(b, 4), lab.ratio([g, b])), (0.6283, 0.3927, 0.8188))

    def test_unlucky_start_is_a_local_minimum(self):
        x = lab.solve(2, seed=0)
        self.assertEqual(lab.ratio(x), 0.7002)
        self.assertEqual(lab.ratio(lab.optimize(x, steps=100)), 0.7002)   # more steps do not help


@unittest.skipUnless(HAVE_QISKIT, "qiskit/scipy not installed (runs in CI)")
class QiskitAgrees(unittest.TestCase):
    def test_estimator_matches_numpy(self):
        import qaoa_qiskit
        for x in ([0.6283, 0.3927], [0.585, 1.029, 0.517, 0.309], [2.0, 0.9, -0.5, 0.03]):
            self.assertAlmostEqual(qaoa_qiskit.expected_cut(x), -lab.cost(x), places=6)

    def test_cobyla_from_warm_start(self):
        import qaoa_qiskit
        _, r = qaoa_qiskit.cobyla(np.array([0.3245, 0.649, 0.354, 0.177]))
        self.assertGreaterEqual(r, 0.92)


if __name__ == "__main__":
    unittest.main()
