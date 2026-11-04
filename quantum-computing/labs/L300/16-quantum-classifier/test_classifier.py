"""Tests for lab 16. Run: python -m unittest -v   (from this folder)"""
import importlib.util
import os
import unittest

import numpy as np

import circuit_model as cm
import classifier_lab as lab

HAVE_PENNYLANE = importlib.util.find_spec("pennylane") is not None
if os.environ.get("REQUIRE_L300_EXTRAS") == "1" and not HAVE_PENNYLANE:
    raise ImportError("REQUIRE_L300_EXTRAS=1 but pennylane is not installed")


class Classifier(unittest.TestCase):
    def test_split_is_disjoint_and_balanced(self):
        xtr, ytr, xte, yte = lab.make_dataset()
        self.assertEqual((len(xtr), len(xte)), (40, 20))
        self.assertFalse({tuple(r) for r in xtr} & {tuple(r) for r in xte})

    def test_parameter_shift_matches_finite_difference(self):
        w, x = np.array([[0.3, -0.7], [1.1, 0.2]]), np.array([[1.0, 2.0], [0.5, 0.1]])
        e = np.zeros_like(w)
        e[1, 0] = 1e-6
        fd = (cm.outputs(w + e, x) - cm.outputs(w - e, x)) / 2e-6
        self.assertTrue(np.allclose(cm.gradient(w, x)[1, 0], fd, atol=1e-6))

    def test_honest_comparison(self):
        q, c = lab.train_quantum(*lab.make_dataset())[1], lab.logistic_baseline(*lab.make_dataset())[1]
        self.assertEqual((q, c), (0.9, 0.85))                  # one test point apart out of 20: a tie in practice

    def test_random_init_goes_flat_at_scale(self):
        small, big = lab.gradient_scan(2, 2), lab.gradient_scan(10, 20)
        self.assertGreater(small["median_abs_grad"], 0.5)
        self.assertLess(big["median_abs_grad"], lab.SHOT_FLOOR)


@unittest.skipUnless(HAVE_PENNYLANE, "pennylane not installed (runs in CI job l300-extras)")
class PennyLaneAgrees(unittest.TestCase):
    def test_same_outputs_as_numpy(self):
        import classifier_pennylane as clp
        w, x = np.array([[0.3, -0.7], [1.1, 0.2]]), np.array([[1.0, 2.0], [0.5, 0.1]])
        self.assertTrue(np.allclose([clp.output(w, xi) for xi in x], cm.outputs(w, x), atol=1e-6))

    def test_same_gradient_as_numpy(self):
        import classifier_pennylane as clp
        w, x = np.array([[0.3, -0.7], [1.1, 0.2]]), np.array([1.0, 2.0])
        self.assertTrue(np.allclose(clp.gradient(w, x), cm.gradient(w, x[None, :])[..., 0], atol=1e-6))


if __name__ == "__main__":
    unittest.main()
