"""Tests for lab 07. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import os
import unittest

import crosscheck_numpy

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class CrossCheck(unittest.TestCase):
    def test_secret_found_with_certainty(self):
        self.assertEqual(crosscheck_numpy.bv_probabilities("1011"), {"1011": 1.0})

    def test_every_4_bit_secret(self):
        self.assertTrue(crosscheck_numpy.all_secrets_found(4))


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class SdkLab(unittest.TestCase):
    def test_one_query_finds_secret(self):
        import bv_lab
        for secret in ("1011", "110101", "0000"):
            self.assertEqual(bv_lab.run(bv_lab.bv_circuit(bv_lab.bv_oracle(secret))), {secret: 100})

    def test_oracle_queries_once(self):
        import bv_lab
        self.assertEqual(sum(1 for i in bv_lab.bv_oracle("1011").data if i.operation.name == "cx"), 3)

    def test_classical_baseline_needs_n_queries(self):
        import bv_lab
        self.assertEqual(bv_lab.classical_queries("110101"), ("110101", 6))


if __name__ == "__main__":
    unittest.main()
