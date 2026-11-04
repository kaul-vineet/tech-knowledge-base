"""Tests for lab 03. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import os
import unittest

import crosscheck_numpy

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class CrossCheck(unittest.TestCase):
    def test_exact_probabilities(self):
        self.assertEqual(crosscheck_numpy.exact_probabilities(), {"0": 0.5, "1": 0.5})

    def test_numpy_sampling_seeded_and_within_5_sigma(self):
        self.assertEqual(crosscheck_numpy.sample(100, seed=1), crosscheck_numpy.sample(100, seed=1))
        c = crosscheck_numpy.sample(10000, seed=3)
        self.assertLess(abs(c["1"] / 10000 - 0.5), 5 * crosscheck_numpy.standard_error(10000))


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class SdkLab(unittest.TestCase):
    def test_counts_sum_to_shots(self):
        import shots_lab
        for shots in (10, 100, 1000):
            self.assertEqual(sum(shots_lab.sample(shots, seed=5).values()), shots)

    def test_estimate_matches_numpy_probability(self):
        import shots_lab
        shots = 10000
        p = crosscheck_numpy.exact_probabilities()["1"]
        c = shots_lab.sample(shots, seed=42)
        self.assertLess(abs(c["1"] / shots - p), 5 * crosscheck_numpy.standard_error(shots, p))

    def test_same_seed_same_counts(self):
        import shots_lab
        self.assertEqual(shots_lab.sample(100, seed=2024), shots_lab.sample(100, seed=2024))

    def test_histogram_has_one_row_per_outcome(self):
        import shots_lab
        self.assertEqual(len(shots_lab.text_histogram({"0": 3, "1": 7}).splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
