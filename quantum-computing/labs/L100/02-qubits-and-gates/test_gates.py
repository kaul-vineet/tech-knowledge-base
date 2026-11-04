"""Tests for lab 02. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import math
import os
import unittest

import crosscheck_numpy

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class CrossCheck(unittest.TestCase):
    def test_expected_probabilities(self):
        e = crosscheck_numpy.EXPECTED
        self.assertEqual(e["nothing"], {"0": 1.0})
        self.assertEqual(e["x"], {"1": 1.0})
        self.assertEqual(e["h"], {"0": 0.5, "1": 0.5})
        self.assertEqual(e["h_h"], {"0": 1.0})
        self.assertEqual(e["x_on_q0_of_2"], {"01": 1.0})


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class SdkLab(unittest.TestCase):
    SHOTS = 1000

    def test_counts_match_numpy(self):
        import gates_lab
        results = gates_lab.run_all(shots=self.SHOTS)
        for name, probs in crosscheck_numpy.EXPECTED.items():
            counts = results[name]
            self.assertEqual(sum(counts.values()), self.SHOTS, name)
            self.assertLessEqual(set(counts), set(probs), name)  # no impossible outcomes
            for bits, p in probs.items():
                sigma = math.sqrt(self.SHOTS * p * (1 - p))
                self.assertLessEqual(abs(counts.get(bits, 0) - self.SHOTS * p), 5 * sigma + 1e-9, name)

    def test_seed_makes_runs_repeatable(self):
        import gates_lab
        self.assertEqual(gates_lab.run_all(seed=11), gates_lab.run_all(seed=11))


if __name__ == "__main__":
    unittest.main()
