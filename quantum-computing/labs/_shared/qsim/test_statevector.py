"""Self-test of the numpy simulator against hand-known results. Run: python -m unittest -v"""
import unittest

import numpy as np

import statevector as sv


class Basics(unittest.TestCase):
    def test_bell_pair(self):
        self.assertEqual(sv.probabilities(sv.run(2, [sv.h(0), sv.cx(0, 1)])), {"00": 0.5, "11": 0.5})

    def test_qubit0_is_rightmost(self):
        self.assertEqual(sv.probabilities(sv.run(3, [sv.x(0)])), {"001": 1.0})

    def test_swap_is_three_cx(self):
        self.assertEqual(sv.probabilities(sv.run(2, [sv.x(0), sv.swap(0, 1)])), {"10": 1.0})

    def test_unitary_is_unitary(self):
        u = sv.unitary(2, [sv.h(0), sv.cp(0.3, 0, 1)])
        self.assertTrue(np.allclose(u.conj().T @ u, np.eye(4)))

    def test_global_phase(self):
        self.assertTrue(sv.equal_up_to_global_phase(1j * sv.H, sv.H))
        self.assertFalse(sv.equal_up_to_global_phase(sv.X, sv.H))


if __name__ == "__main__":
    unittest.main()
