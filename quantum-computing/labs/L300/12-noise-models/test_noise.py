"""Tests for lab 12. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import os
import unittest

import noise_lab as lab

HAVE_AER = importlib.util.find_spec("qiskit_aer") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_AER:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit-aer is not installed")


class NumpyNoise(unittest.TestCase):
    def test_ideal_is_perfect(self):
        m = lab.metrics(2, lab.IDEAL)
        self.assertEqual((m["fidelity"], m["success"]), (1.0, 1.0))

    def test_fidelity_falls_with_noise_and_size(self):
        f = [lab.metrics(n, {**lab.NOISE, "p2": p})["fidelity"] for n in (2, 3, 4) for p in (0.0, 0.05, 0.1)]
        self.assertTrue(all(a > b for a, b in zip(f[0:3], f[1:3])))
        self.assertGreater(lab.metrics(2, lab.NOISE)["fidelity"], lab.metrics(4, lab.NOISE)["fidelity"])

    def test_damping_and_readout_favour_zeros(self):
        m = lab.metrics(3, lab.NOISE)
        self.assertGreater(m["p_all0"], m["p_all1"])

    def test_counts_are_seeded(self):
        self.assertEqual(lab.counts(2, lab.NOISE), lab.counts(2, lab.NOISE))

    def test_naive_check_breaks_under_noise(self):
        self.assertTrue(lab.bell_check(lab.counts(2, lab.IDEAL)))
        self.assertFalse(lab.bell_check(lab.counts(2, lab.NOISE)))


@unittest.skipUnless(HAVE_AER, "qiskit-aer not installed (runs in CI)")
class AerAgrees(unittest.TestCase):
    def test_aer_success_matches_numpy_model(self):
        import noise_aer
        for n in (2, 3):
            self.assertAlmostEqual(noise_aer.aer_success(n, lab.NOISE), lab.metrics(n, lab.NOISE)["success"], delta=0.02)

    def test_aer_ideal_has_no_impossible_outcomes(self):
        import noise_aer
        self.assertLessEqual(set(noise_aer.aer_counts(2, lab.IDEAL, shots=500)), {"00", "11"})


if __name__ == "__main__":
    unittest.main()
