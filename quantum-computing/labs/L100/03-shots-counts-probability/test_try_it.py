"""Tests for lab 03 try-it items. Run: python -m unittest -v"""
import os
import unittest

import try_it

if os.environ.get("REQUIRE_QUANTUM_SDKS") == "1" and not try_it.HAVE_QISKIT:
    raise ImportError("REQUIRE_QUANTUM_SDKS=1 but qiskit is not installed")


class TryItNumpy(unittest.TestCase):
    def test_2500_shots_standard_error(self):
        c, se = try_it.try1_numpy()
        self.assertAlmostEqual(se, 0.01)
        self.assertLessEqual(abs(c["1"] / 2500 - 0.5), 5 * se)

    def test_different_seed_gives_different_draws(self):
        a, b = try_it.try2_numpy()
        self.assertNotEqual(a, b)


@unittest.skipUnless(try_it.HAVE_QISKIT, "qiskit not installed (runs in CI)")
class TryItSdk(unittest.TestCase):
    def test_2500_shots_within_tolerance(self):
        import shots_lab
        c = shots_lab.sample(2500, seed=42)
        self.assertLessEqual(abs(c["1"] / 2500 - 0.5), 5 * 0.01)

    def test_seed_change_changes_counts(self):
        import shots_lab
        self.assertNotEqual(shots_lab.sample(100, seed=2024), shots_lab.sample(100, seed=2025))


if __name__ == "__main__":
    unittest.main()
