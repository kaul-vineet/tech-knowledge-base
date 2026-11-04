"""Self-test of the density-matrix extension. Run: python -m unittest -v   (from this folder)"""
import unittest

import numpy as np

import density as dm
import statevector as sv

BELL = [sv.h(0), sv.cx(0, 1)]


class Density(unittest.TestCase):
    def test_noiseless_matches_statevector(self):
        rho = dm.run(2, BELL)
        self.assertTrue(np.allclose(rho, dm.pure(sv.run(2, BELL))))

    def test_full_depolarizing_gives_maximally_mixed(self):
        rho = dm.run(2, BELL + [("depol", 1.0, (0, 1))])
        self.assertTrue(np.allclose(rho, np.eye(4) / 4))

    def test_channels_keep_trace_one(self):
        rho = dm.run(2, BELL + [("depol", 0.3, (0, 1)), ("damp", 0.4, 1), ("depol", 0.1, (0,))])
        self.assertAlmostEqual(float(np.real(np.trace(rho))), 1.0)
        self.assertTrue(np.allclose(rho, rho.conj().T))

    def test_damping_moves_one_to_zero(self):
        self.assertTrue(np.allclose(dm.probabilities(dm.run(1, [sv.x(0), ("damp", 0.25, 0)])), [0.25, 0.75]))

    def test_bell_fidelity_under_two_qubit_depolarizing(self):
        rho = dm.run(2, BELL + [("depol", 0.2, (0, 1))])
        self.assertAlmostEqual(dm.fidelity(rho, sv.run(2, BELL)), 1 - 0.2 + 0.2 / 4)

    def test_readout_matrix_columns_sum_to_one(self):
        a = dm.readout_matrix(0.02, 0.05, 3)
        self.assertTrue(np.allclose(a.sum(axis=0), 1))
        self.assertAlmostEqual(a[0b000, 0b111], 0.05 ** 3)


if __name__ == "__main__":
    unittest.main()
