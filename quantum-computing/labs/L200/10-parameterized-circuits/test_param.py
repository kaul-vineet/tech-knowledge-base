"""Tests for lab 10. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import os
import unittest

import numpy as np

import crosscheck_numpy as cc

HAVE_QISKIT = importlib.util.find_spec("qiskit") is not None
if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class CrossCheck(unittest.TestCase):
    def test_exact_curves(self):
        z, x = cc.exact()
        self.assertTrue(np.allclose(z, np.cos(cc.THETAS)) and np.allclose(x, np.sin(cc.THETAS)))
        self.assertEqual(cc.fit_cos_sin(cc.THETAS, z), [1.0, 0.0, 0.0])

    def test_sampled_fit_within_shot_noise(self):
        a, b, c = cc.fit_cos_sin(cc.THETAS, cc.sampled_z(shots=400))
        self.assertLess(max(abs(a - 1), abs(b), abs(c)), 0.05)


@unittest.skipUnless(HAVE_QISKIT, "qiskit not installed (runs in CI)")
class SdkLab(unittest.TestCase):
    def test_binding_leaves_template_free(self):
        import param_lab
        qc, theta = param_lab.ansatz()
        self.assertEqual((qc.assign_parameters({theta: 0.5}).num_parameters, qc.num_parameters), (0, 1))

    def test_estimator_matches_numpy(self):
        import param_lab
        qc, _ = param_lab.ansatz()
        z, x = param_lab.exact_expectations(qc)
        nz, nx = cc.exact()
        self.assertTrue(np.allclose(z, nz) and np.allclose(x, nx))

    def test_sampled_fit_within_shot_noise(self):
        import param_lab
        qc, _ = param_lab.ansatz()
        a, b, c = param_lab.fit_cos_sin(param_lab.THETAS, param_lab.sampled_z(qc))
        self.assertLess(max(abs(a - 1), abs(b), abs(c)), 0.05)

    def test_same_seed_same_estimates(self):
        import param_lab
        qc, _ = param_lab.ansatz()
        self.assertTrue(np.array_equal(param_lab.sampled_z(qc), param_lab.sampled_z(qc)))


if __name__ == "__main__":
    unittest.main()
