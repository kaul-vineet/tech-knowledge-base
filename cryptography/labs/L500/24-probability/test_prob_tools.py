import math
import random
import unittest
from fractions import Fraction

from prob_tools import (collision_exact, collision_lower, collision_upper, min_entropy, q_for_probability,
                        shannon_entropy)


class Birthday(unittest.TestCase):
    def test_classic_birthday(self):
        none = Fraction(1)
        for i in range(23):
            none *= Fraction(365 - i, 365)
        self.assertAlmostEqual(collision_exact(23, 365), float(1 - none), places=12)
        self.assertGreater(collision_exact(23, 365), 0.5)
        self.assertLess(collision_exact(22, 365), 0.5)

    def test_bounds_sandwich_exact(self):
        for n in (100, 365, 2**20):
            for q in (2, 5, 20, 90):
                self.assertLessEqual(collision_lower(q, n), collision_exact(q, n) + 1e-15)
                self.assertLessEqual(collision_exact(q, n), collision_upper(q, n) + 1e-15)

    def test_nonce_budget(self):
        self.assertAlmostEqual(math.log2(collision_exact(2**32, 2**96)), -33.0, places=2)
        self.assertAlmostEqual(math.log2(q_for_probability(2**-32, 2**96)), 32.5, places=2)

    def test_simulation_matches_formula(self):
        r = random.Random(7)
        n, q, trials = 2**16, 256, 3000
        hits = sum(len({r.randrange(n) for _ in range(q)}) < q for _ in range(trials))
        self.assertAlmostEqual(hits / trials, collision_lower(q, n), delta=0.04)


class Entropy(unittest.TestCase):
    def test_uniform_equal(self):
        p = [1 / 256] * 256
        self.assertAlmostEqual(shannon_entropy(p), 8.0)
        self.assertAlmostEqual(min_entropy(p), 8.0)

    def test_min_entropy_le_shannon(self):
        p = [0.5, 0.25, 0.125, 0.125]
        self.assertAlmostEqual(min_entropy(p), 1.0)
        self.assertAlmostEqual(shannon_entropy(p), 1.75)


if __name__ == "__main__":
    unittest.main()
