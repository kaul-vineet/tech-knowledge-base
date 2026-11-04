"""Tests for lab 06. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import math
import os
import unittest

import crosscheck_numpy

HAVE_SDKS = all(importlib.util.find_spec(m) for m in ("qiskit", "cirq"))
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_SDKS:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit/cirq are not installed")


def within_5_sigma(counts, probs, shots):
    if set(counts) - set(probs):
        return False
    return all(abs(counts.get(k, 0) - shots * p) <= 5 * math.sqrt(shots * p * (1 - p)) + 1e-9
               for k, p in probs.items())


class CrossCheck(unittest.TestCase):
    def test_bell_same_in_both_orders(self):
        self.assertEqual(crosscheck_numpy.probabilities("bell", "qiskit"), {"00": 0.5, "11": 0.5})
        self.assertEqual(crosscheck_numpy.probabilities("bell", "cirq"), {"00": 0.5, "11": 0.5})

    def test_x_on_q0_differs_by_convention(self):
        self.assertEqual(crosscheck_numpy.probabilities("x_on_q0", "qiskit"), {"01": 1.0})
        self.assertEqual(crosscheck_numpy.probabilities("x_on_q0", "cirq"), {"10": 1.0})


@unittest.skipUnless(HAVE_SDKS, "qiskit/cirq not installed (runs in CI)")
class SdkLab(unittest.TestCase):
    SHOTS = 2000

    def test_each_framework_matches_numpy(self):
        import two_frameworks_lab as lab
        for kind in lab.CIRCUITS:
            q = lab.qiskit_counts(kind, self.SHOTS, seed=1)
            c = lab.cirq_counts_raw(kind, self.SHOTS, seed=1)
            self.assertTrue(within_5_sigma(q, crosscheck_numpy.probabilities(kind, "qiskit"), self.SHOTS), q)
            self.assertTrue(within_5_sigma(c, crosscheck_numpy.probabilities(kind, "cirq"), self.SHOTS), c)

    def test_frameworks_agree_after_normalising_bit_order(self):
        import two_frameworks_lab as lab
        for kind in lab.CIRCUITS:
            r = lab.compare(kind, self.SHOTS, seed=2)
            self.assertEqual(set(r["qiskit"]), set(r["cirq_in_qiskit_order"]), kind)

    def test_cirq_seed_repeatable(self):
        import two_frameworks_lab as lab
        self.assertEqual(lab.cirq_counts_raw("bell", 100, seed=5), lab.cirq_counts_raw("bell", 100, seed=5))


if __name__ == "__main__":
    unittest.main()
