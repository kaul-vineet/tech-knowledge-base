"""Lesson 25 (L500): every theorem check must pass (each raises AssertionError if its prediction fails).

Run:  python -m unittest -v
"""
import unittest

import theorems


class TheoremChecks(unittest.TestCase):
    def test_every_check_passes_and_reports(self):
        self.assertGreaterEqual(len(theorems.CHECKS), 2)
        self.assertLessEqual(len(theorems.CHECKS), 4)
        for tid, (name, fn) in theorems.CHECKS.items():
            with self.subTest(theorem=tid):
                lines = fn()
                self.assertTrue(lines and all(isinstance(x, str) and x for x in lines), name)

    def test_output_is_deterministic(self):
        self.assertEqual(theorems.run(), theorems.run())


if __name__ == "__main__":
    unittest.main()
