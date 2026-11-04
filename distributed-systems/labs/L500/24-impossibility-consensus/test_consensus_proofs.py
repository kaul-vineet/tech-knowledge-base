"""python -m unittest -v   (smaller runs than the demo; same invariants)"""
import random
import unittest

import consensus_proofs as cp


class ConsensusTests(unittest.TestCase):
    def test_no_two_generals_protocol_in_family(self):
        out = "\n".join(cp.generals_family(max_msgs=4))
        self.assertIn("correct protocols: 0", out)

    def test_paxos_safe_and_broken_variant_unsafe(self):
        rng = random.Random(5)
        for _ in range(300):
            px = cp.random_run(rng, broken=False)
            self.assertLessEqual(len({v for _, v in px.chosen()}), 1)
            self.assertEqual(cp.p2b_violations(px), 0)
        rng = random.Random(5)
        bad = sum(len({v for _, v in cp.random_run(rng, broken=True).chosen()}) > 1 for _ in range(300))
        self.assertGreater(bad, 0)

    def test_quorum_intersection(self):
        out = "\n".join(cp.check_paxos(runs=10))
        self.assertIn("R + W > N with a disjoint pair: 0", out)
        self.assertIn("56 of 56", out)

    def test_duel_never_decides(self):
        px = cp.duel(200)
        self.assertEqual(px.chosen(), set())
        self.assertEqual(px.accept_log, [])

    def test_cap(self):
        out = "\n".join(cp.check_cap())
        self.assertIn("AP-local", out)
        for line in out.splitlines()[1:]:
            self.assertFalse("available=True linearizable=True" in line)


if __name__ == "__main__":
    unittest.main()
