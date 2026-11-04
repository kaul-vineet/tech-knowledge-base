import importlib.util
import unittest

import numpy as np

import crossmatch as cm
from kdtree import KDTree


class TestSeparation(unittest.TestCase):
    def test_known_angles(self):
        self.assertAlmostEqual(float(cm.angular_sep(0, 0, 90, 0)), 90.0, places=12)
        self.assertAlmostEqual(float(cm.angular_sep(10, 89.9, 190, 89.9)), 0.2, places=9)  # across the pole

    def test_wrap_at_zero_ra(self):
        self.assertAlmostEqual(float(cm.angular_sep(359.9999, 28, 0.0001, 28)) * 3600, 0.6357, places=4)


class TestKDTree(unittest.TestCase):
    def test_same_answer_as_brute_force(self):
        rng = np.random.default_rng(1)
        pts = cm.unit_vectors(rng.uniform(0, 360, 500), rng.uniform(-90, 90, 500))
        tree = KDTree(pts)
        for q in cm.unit_vectors(rng.uniform(0, 360, 50), rng.uniform(-90, 90, 50)):
            j, d = tree.nearest(q)
            brute = np.sqrt(((pts - q) ** 2).sum(axis=1))
            self.assertEqual(j, int(np.argmin(brute)))
            self.assertAlmostEqual(d, float(brute.min()), places=12)


class TestMatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a, cls.b, cls.truth = cm.make_catalogues()
        cls.idx, cls.sep, cls.evals = cm.match(cls.a, cls.b)

    def test_all_true_counterparts_found(self):
        self.assertEqual(int(np.sum(self.idx[:len(self.truth)] == self.truth)), 1812)

    def test_separations_inside_radius(self):
        self.assertLessEqual(np.nanmax(self.sep), 1.0)
        self.assertEqual(f"{np.nanmedian(self.sep):.3f}", "0.233")

    def test_tree_does_far_less_work(self):
        self.assertLess(self.evals, len(self.a[0]) * len(self.b[0]) / 50)


@unittest.skipUnless(importlib.util.find_spec("astropy") and importlib.util.find_spec("scipy"),
                     "astropy/scipy not installed (runs in CI)")
class TestLibraryEquivalent(unittest.TestCase):
    def test_astropy_and_scipy_find_the_same_pairs(self):
        import crossmatch_astropy
        ours, astro, kd = crossmatch_astropy.compare()
        self.assertTrue(np.array_equal(ours, astro))
        self.assertTrue(np.array_equal(ours, kd))


if __name__ == "__main__":
    unittest.main()
