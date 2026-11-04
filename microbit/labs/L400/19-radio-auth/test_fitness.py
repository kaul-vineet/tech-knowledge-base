"""Fitness function (lab 19): keeps ADR-0019 true.

Five seeds of the attack scenario with the shipped gateway (solution.py, SipHash mode):
0 forged frames accepted, 0 replays accepted, and every genuine frame that reached the gateway
intact is accepted despite 10 % reordering and 5 % duplication.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import attacks  # noqa: E402


class Fitness(unittest.TestCase):
    def test_no_forgery_no_replay_no_genuine_loss(self):
        for seed in range(1, 6):
            m, _ = attacks.run("solution.py", "siphash", seed=seed)
            with self.subTest(seed=seed):
                self.assertEqual(m["forged_accepted"], 0)
                self.assertEqual(m["replays_accepted"], 0)
                self.assertEqual(m["genuine_accepted"], m["genuine_intact"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
