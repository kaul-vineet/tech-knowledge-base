import unittest

import numpy as np

import schelling as s


class TestSchelling(unittest.TestCase):
    def test_reproducible(self):
        g1, h1 = s.run(seed=5)
        g2, h2 = s.run(seed=5)
        self.assertTrue(np.array_equal(g1, g2))
        self.assertEqual(h1, h2)

    def test_agents_conserved(self):
        rng = np.random.default_rng(1)
        grid = s.make_grid(rng)
        before = [(grid == k).sum() for k in (0, 1, 2)]
        for _ in range(5):
            s.step(grid, rng)
        self.assertEqual(before, [(grid == k).sum() for k in (0, 1, 2)])

    def test_neighbour_rule_on_tiny_grid(self):
        grid = np.array([[1, 1, 0], [2, 1, 0], [0, 0, 0]])
        # centre agent (1) sees neighbours 1,1,2 (no wrap duplicates on 3x3 with torus: all 8 cells once)
        frac = s.similarity(grid)
        self.assertAlmostEqual(frac[1, 1], 2 / 3)
        self.assertTrue(np.isnan(frac[2, 2]))

    def test_emergent_segregation(self):
        _, history = s.run(seed=42)
        self.assertLess(abs(history[0][0] - 50), 5)       # starts mixed (~50%)
        self.assertGreater(history[-1][0], 2 * 100 * s.WANT)  # ends far above the 30% each agent wanted
        self.assertEqual(history[-1][1], 0)


try:
    import schelling_mesa
except ImportError:  # Mesa runs in CI only
    schelling_mesa = None


@unittest.skipIf(schelling_mesa is None, "mesa not installed (pending-ci)")
class TestMesaEquivalent(unittest.TestCase):
    def test_mesa_shows_same_emergence(self):
        m = schelling_mesa.Schelling(seed=42)
        for _ in range(50):
            m.step()
        self.assertGreater(m.pct_similar(), 60)


if __name__ == "__main__":
    unittest.main()
