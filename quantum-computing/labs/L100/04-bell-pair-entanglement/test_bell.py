"""Tests for lab 04. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import math
import os
import unittest

import crosscheck_numpy

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class CrossCheck(unittest.TestCase):
    def test_bell_probabilities(self):
        self.assertEqual(crosscheck_numpy.bell_probabilities(), {"00": 0.5, "11": 0.5})


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class SdkLab(unittest.TestCase):
    def test_statevector_matches_numpy(self):
        import bell_lab
        self.assertEqual(bell_lab.ideal_probabilities(), crosscheck_numpy.bell_probabilities())

    def test_only_00_and_11(self):
        import bell_lab
        counts = bell_lab.run_bell(shots=2000, seed=3)
        self.assertTrue(bell_lab.only_correlated(counts), counts)
        self.assertEqual(sum(counts.values()), 2000)

    def test_roughly_half_half(self):
        import bell_lab
        shots = 2000
        counts = bell_lab.run_bell(shots=shots, seed=3)
        self.assertLess(abs(counts.get("00", 0) - shots / 2), 5 * math.sqrt(shots * 0.25))

    def test_only_correlated_rejects_mixed(self):
        import bell_lab
        self.assertFalse(bell_lab.only_correlated({"00": 5, "01": 1}))


if __name__ == "__main__":
    unittest.main()
