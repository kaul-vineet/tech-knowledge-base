"""Tests for lab 06 try-it items. Run: python -m unittest -v"""
import os
import unittest

import crosscheck_numpy
import try_it

if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not try_it.HAVE_SDKS:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit/cirq are not installed")


class TryItNumpy(unittest.TestCase):
    def test_model_matches_lab_crosscheck_for_2_qubits(self):
        k = try_it.keys_for_x(0, 2, (0, 1))
        self.assertEqual({k["qiskit"]: 1.0}, crosscheck_numpy.probabilities("x_on_q0", "qiskit"))
        self.assertEqual({k["cirq_raw"]: 1.0}, crosscheck_numpy.probabilities("x_on_q0", "cirq"))

    def test_three_qubits(self):
        self.assertEqual(try_it.try1_numpy(), {"qiskit": "001", "cirq_raw": "100", "cirq_in_qiskit_order": "001"})

    def test_reversed_measure_order_breaks_normalising(self):
        self.assertEqual(try_it.try2_numpy(), {"qiskit": "01", "cirq_raw": "01", "cirq_in_qiskit_order": "10"})


@unittest.skipUnless(try_it.HAVE_SDKS, "qiskit/cirq not installed (runs in CI)")
class TryItSdk(unittest.TestCase):
    def test_sdks_match_model(self):
        m = try_it.try1_numpy()
        self.assertEqual(try_it.sdk_try1(), {"qiskit": m["qiskit"], "cirq_raw": m["cirq_raw"]})
        self.assertEqual(try_it.sdk_try2(), {"cirq_raw": try_it.try2_numpy()["cirq_raw"]})


if __name__ == "__main__":
    unittest.main()
