"""Self-test of the shared MaxCut/QAOA helper. Run: python -m unittest -v"""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qopt import maxcut as mc  # noqa: E402
from qsim import statevector as sv  # noqa: E402

EDGES5 = [(0, 1), (0, 2), (0, 4), (1, 2), (2, 3), (3, 4)]   # lesson 14's graph


class MaxCut(unittest.TestCase):
    def test_regular_graph_is_regular_and_seeded(self):
        g = mc.regular_graph(8, 3, seed=1)
        self.assertEqual(len(g), 12)
        self.assertEqual(sorted(np.bincount(np.array(g).ravel())), [3] * 8)
        self.assertEqual(g, mc.regular_graph(8, 3, seed=1))

    def test_brute_force_matches_lesson_14(self):
        best, strings = mc.brute_force(5, EDGES5)
        self.assertEqual(best, 5)
        self.assertEqual(sorted(format(s, "05b") for s in strings), ["01001", "01011", "10100", "10110"])

    def test_vectorised_mixer_equals_qsim_rx(self):
        rng = np.random.default_rng(0)
        psi = rng.normal(size=8) + 1j * rng.normal(size=8)
        ref = psi.copy()
        for q in range(3):
            ref = sv.apply(ref, (sv.rx(0.8), q, ()))
        self.assertTrue(np.allclose(mc.mix(psi.copy(), 3, 0.4), ref))

    def test_lesson14_p1_value(self):
        cuts = mc.cut_values(5, EDGES5)
        self.assertAlmostEqual(mc.expectation(5, cuts, [0.6283, 0.3927]) / 5, 0.8188, places=4)


if __name__ == "__main__":
    unittest.main()
