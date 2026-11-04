"""Tests for lab 13. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import os
import unittest

import numpy as np

import mitigation_lab as lab

HAVE_MITIQ = importlib.util.find_spec("mitiq") is not None
if os.environ.get("REQUIRE_L300_EXTRAS") == "1" and not HAVE_MITIQ:
    raise ImportError("REQUIRE_L300_EXTRAS=1 but mitiq is not installed")


class ReadoutMitigation(unittest.TestCase):
    def test_exact_calibration_recovers_truth(self):
        a = lab.dm.readout_matrix(lab.READOUT["p01"], lab.READOUT["p10"], 2)
        self.assertTrue(np.allclose(lab.mitigate(a @ lab.true_bell(), a), lab.true_bell()))

    def test_plain_inverse_goes_negative_with_few_shots(self):
        mins = []
        for seed in range(50):
            rng = np.random.default_rng(seed)
            mins.append(lab.mitigate(lab.measure(lab.true_bell(), 200, rng), lab.calibrate(100, rng)).min())
        self.assertGreater(np.mean(np.array(mins) < 0), 0.5)


class Zne(unittest.TestCase):
    def test_folding_keeps_ideal_circuit(self):
        from qsim import statevector as sv
        for s in (1, 3, 5):
            self.assertAlmostEqual(abs(sv.run(3, lab.folded(lab.mirror_ops(), s))[0]) ** 2, 1.0)

    def test_noise_grows_with_scale(self):
        v = [lab.noisy_value(s) for s in (1, 3, 5)]
        self.assertTrue(v[0] > v[1] > v[2])

    def test_extrapolation_beats_raw(self):
        scales, v = [1, 3, 5], [lab.noisy_value(s) for s in (1, 3, 5)]
        raw_err = 1 - v[0]
        self.assertLess(abs(1 - lab.linear(scales, v)), raw_err)
        self.assertLess(abs(1 - lab.richardson(scales, v)), abs(1 - lab.linear(scales, v)))

    def test_richardson_is_exact_for_a_quadratic(self):
        f = lambda s: 0.9 - 0.05 * s + 0.002 * s * s
        self.assertAlmostEqual(lab.richardson([1, 3, 5], [f(1), f(3), f(5)]), 0.9)


@unittest.skipUnless(HAVE_MITIQ, "mitiq not installed (runs in CI job l300-extras)")
class MitiqAgrees(unittest.TestCase):
    def test_raw_and_richardson_match_numpy(self):
        import mitiq_zne
        from mitiq import zne
        self.assertAlmostEqual(mitiq_zne.execute(mitiq_zne.mirror_circuit()), lab.noisy_value(1), places=3)
        v = [lab.noisy_value(s) for s in (1, 3, 5)]
        ours = lab.richardson([1, 3, 5], v)
        self.assertAlmostEqual(mitiq_zne.mitiq_zne(zne.inference.RichardsonFactory(scale_factors=[1, 3, 5])), ours, places=3)


if __name__ == "__main__":
    unittest.main()
