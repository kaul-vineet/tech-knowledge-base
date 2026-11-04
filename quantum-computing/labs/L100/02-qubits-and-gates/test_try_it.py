"""Tests for lab 02 try-it items. Run: python -m unittest -v"""
import os
import unittest

import try_it

if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not try_it.HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class TryItNumpy(unittest.TestCase):
    def test_h_x_h_is_always_zero(self):
        self.assertEqual(try_it.numpy_probabilities("h_x_h"), {"0": 1.0})

    def test_x_on_qubit_1_reads_10(self):
        self.assertEqual(try_it.numpy_probabilities("x_on_q1_of_2"), {"10": 1.0})


@unittest.skipUnless(try_it.HAVE_QISKIT, "qiskit not installed (runs in CI)")
class TryItSdk(unittest.TestCase):
    def test_deterministic_counts(self):
        self.assertEqual(try_it.sdk_counts("h_x_h"), {"0": 1000})
        self.assertEqual(try_it.sdk_counts("x_on_q1_of_2"), {"10": 1000})


if __name__ == "__main__":
    unittest.main()
