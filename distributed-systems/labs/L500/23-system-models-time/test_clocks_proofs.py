"""python -m unittest -v   (smaller runs than the demo; same invariants)"""
import random
import unittest

import clocks_proofs as cp


class ClockTests(unittest.TestCase):
    def test_lamport_clock_condition_and_converse(self):
        rng = random.Random(1)
        converse_fails = 0
        for _ in range(60):
            ev = cp.random_execution(rng)
            hb, lam = cp.happened_before(ev), cp.lamport(ev, 3)
            for a in range(len(ev)):
                for b in range(len(ev)):
                    if b in hb[a]:
                        self.assertLess(lam[a], lam[b])
                    elif a != b and a not in hb[b] and lam[a] < lam[b]:
                        converse_fails += 1
        self.assertGreater(converse_fails, 0)  # L(a) < L(b) does not imply a -> b

    def test_vector_clocks_characterise_causality(self):
        rng = random.Random(2)
        for _ in range(60):
            ev = cp.random_execution(rng)
            hb, vc = cp.happened_before(ev), cp.vector(ev, 3)
            for a in range(len(ev)):
                for b in range(len(ev)):
                    if a != b:
                        self.assertEqual(b in hb[a], cp.vless(vc[a], vc[b]))

    def test_broken_rules_are_caught(self):
        out = "\n".join(cp.check_clock(runs=80) + cp.check_vector(runs=80))
        self.assertIn("violations of L(a) < L(b): 0", out)
        self.assertIn("mismatches between a->b and V(a) < V(b): 0", out)
        self.assertNotIn("(tick only, no max): 0 ", out)
        self.assertNotIn("(no element-wise max): 0 ", out)

    def test_safety_prefix_closed_and_liveness_extendable(self):
        out = "\n".join(cp.check_safety(max_len=6, ext_len=2))
        self.assertIn("good traces with a bad prefix = 0", out)
        self.assertIn("extension up to length 2: 0", out)
        self.assertIn("cannot be completed = 0", out)

    def test_detector(self):
        out = "\n".join(cp.check_detector(samples=20_000))
        self.assertIn("timeout 105 ms -> 0 false suspicions", out)


if __name__ == "__main__":
    unittest.main()
