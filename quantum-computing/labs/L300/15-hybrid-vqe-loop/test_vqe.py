"""Tests for lab 15. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

import numpy as np

import vqe_lab as lab

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None and importlib.util.find_spec("scipy") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit/scipy is not installed")


class Vqe(unittest.TestCase):
    def test_ground_energy(self):
        self.assertAlmostEqual(lab.E0, -1.8405, places=4)

    def test_ansatz_reaches_ground_state_exactly(self):
        self.assertEqual(lab.vqe(None)[1], 0.0)

    def test_sampled_energy_is_unbiased(self):
        rng, t = np.random.default_rng(1), np.array([0.3, -0.2, 0.5, 1.0])
        mean = np.mean([lab.energy(t, 1000, rng) for _ in range(400)])
        self.assertAlmostEqual(mean, lab.energy(t), delta=0.005)

    def test_shot_noise_breaks_finite_differences(self):
        with tempfile.TemporaryDirectory(dir=lab.HERE) as d:      # per-run folder: parallel runs never share a log file
            log_path = Path(d) / "test_gd.jsonl"
            x, err = lab.vqe(1000, log_path=log_path)
            summary = lab.summarize(log_path)
        self.assertGreater(err, 0.5)
        self.assertGreater(summary["tail_grad_norm_median"], 5)       # the log shows it: huge, noisy gradients


@unittest.skipUnless(HAVE_QISKIT, "qiskit/scipy not installed (runs in CI)")
class QiskitAgrees(unittest.TestCase):
    def test_estimator_matches_numpy(self):
        import vqe_qiskit
        for t in ([0.1, 0.1, 0.1, 0.1], [0.3, -0.2, 0.5, 1.0]):
            self.assertAlmostEqual(vqe_qiskit.exact_energy(t), lab.energy(np.array(t)), places=6)

    def test_sampled_energy_close(self):
        import vqe_qiskit
        t = [0.3, -0.2, 0.5, 1.0]
        self.assertAlmostEqual(vqe_qiskit.sampled_energy(t, shots=20000), lab.energy(np.array(t)), delta=0.02)

    def test_cobyla_with_shots(self):
        import vqe_qiskit
        self.assertLess(vqe_qiskit.run("cobyla", shots=4000)[1], 0.05)


if __name__ == "__main__":
    unittest.main()
