"""Failure lab (seam: nonce uniqueness vs leader failover). With the shipped leader-local counter every new leader
restarts at nonce 1 under the same epoch key: lesson 15's scan finds reuse and the keystream XOR recovers a
plaintext. Random 96-bit nonces (the default, ADR-01-1) give 0 reuse on the same seeded failovers."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # the lab folder
import scenarios as sc  # noqa: E402
from harness import nonce_reuse  # noqa: E402


class TestFailureLab(unittest.TestCase):
    def test_injected_counter_reuses_nonces_and_leaks(self):
        svc, acked = sc.traffic(600, seed=11, faults={"leader-counter"}, chaos=0.02)
        self.assertGreater(svc.failovers, 0)
        self.assertTrue(nonce_reuse(svc.wire))
        demo = sc.keystream_demo(svc, acked)
        self.assertEqual(demo["recovered"], demo["actual"])

    def test_random_nonces_survive_the_same_failovers(self):
        svc, _ = sc.traffic(600, seed=11, chaos=0.02)
        self.assertGreater(svc.failovers, 0)
        self.assertEqual(nonce_reuse(svc.wire), {})


if __name__ == "__main__":
    unittest.main()
