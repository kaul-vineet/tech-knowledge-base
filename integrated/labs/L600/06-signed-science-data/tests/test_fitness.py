"""Fitness functions: they keep the design decisions true on every change.
F1 any single-byte tamper detected (100 %), F2 mirrors converge within 4 rounds, F3 rollback always refused."""
import unittest

from _world import world

import checks


class Fitness(unittest.TestCase):
    def test_f1_every_single_byte_tamper_is_detected(self):
        ok, d = checks.f1_tamper(world())
        self.assertTrue(ok, d)
        self.assertEqual(d["rate"], 1.0)
        self.assertGreater(d["total"], 15000)

    def test_f2_mirrors_converge_within_bound(self):
        ok, d = checks.f2_convergence(world())
        self.assertTrue(ok, d)

    def test_f3_older_release_rejected(self):
        ok, d = checks.f3_rollback(world())
        self.assertTrue(ok, d)


if __name__ == "__main__":
    unittest.main()
