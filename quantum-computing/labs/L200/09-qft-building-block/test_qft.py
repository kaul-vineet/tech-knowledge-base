"""Tests for lab 09. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import os
import unittest

import numpy as np

import crosscheck_numpy as cc
from qsim import statevector as sv

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class CrossCheck(unittest.TestCase):
    def test_gates_equal_numpy_dft(self):
        for n in (1, 2, 3, 4):
            self.assertLess(cc.max_error(sv.unitary(n, cc.qft_ops(n)), cc.dft_matrix(n)), 1e-12, n)

    def test_inverse_undoes_qft(self):
        u = sv.unitary(3, cc.qft_ops(3) + cc.inverse_qft_ops(3))
        self.assertTrue(np.allclose(u, np.eye(8)))


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class SdkLab(unittest.TestCase):
    def test_qiskit_circuit_equals_numpy_dft(self):
        from qiskit.quantum_info import Operator

        import qft_lab
        for n in (2, 3, 4):
            self.assertTrue(np.allclose(Operator(qft_lab.qft_circuit(n)).data, qft_lab.dft_matrix(n)), n)

    def test_matches_library_qftgate(self):
        from qiskit.quantum_info import Operator

        import qft_lab
        self.assertTrue(np.allclose(Operator(qft_lab.library_qft(3)).data, qft_lab.dft_matrix(3)))

    def test_inverse_is_identity(self):
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Operator

        import qft_lab
        qc = qft_lab.qft_circuit(3).compose(qft_lab.inverse_qft_circuit(3))
        self.assertTrue(Operator(qc).equiv(Operator(QuantumCircuit(3))))

    def test_basis_state_matches_numpy(self):
        import qft_lab
        self.assertTrue(np.allclose(qft_lab.qft_of_basis_state(5, 3), sv.run(3, [sv.x(0), sv.x(2)] + cc.qft_ops(3))))


if __name__ == "__main__":
    unittest.main()
