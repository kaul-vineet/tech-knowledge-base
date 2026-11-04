"""Fitness functions. F1/F2 use the full 10k-message run with ~1% leader crashes per post (slowest test, no
wall-clock assertions). F3 handshake byte budget, F4 rotation before the per-key message limit."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # the lab folder
import scenarios as sc  # noqa: E402


class TestFitness(unittest.TestCase):
    def test_f1_f2_traffic_10k(self):
        f1, f2 = sc.fitness_traffic()
        self.assertEqual(f1["reused_nonces"], 0)
        self.assertGreater(f1["failovers"], 100)
        self.assertTrue(f2["identical"] and f2["match_acked"])
        self.assertEqual(f2["shown"], 10000)

    def test_f3_handshake_budget(self):
        r = sc.fitness_handshake()
        self.assertLessEqual(r["welcome_B"], 1200)
        self.assertLessEqual(r["total_B"], 2400)

    def test_f4_key_limit(self):
        self.assertTrue(sc.fitness_key_limit()["pass"])


if __name__ == "__main__":
    unittest.main()
