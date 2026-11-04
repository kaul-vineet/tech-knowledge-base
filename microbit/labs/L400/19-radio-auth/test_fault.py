"""failureLab symptom (observed, seeded): the CRC-only gateway (verifier.py) under attack.

PASSES because it pins the failure: all 20 forged "45 C" frames and 18 of 20 replays get in
(2 were lost on the air) - a CRC detects noise, not an attacker.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import attacks  # noqa: E402


class Symptom(unittest.TestCase):
    def test_forgeries_and_replays_get_in(self):
        m, ver = attacks.run("verifier.py", "crc")
        self.assertEqual((m["forged_accepted"], m["replays_accepted"]), (20, 18))
        self.assertEqual(m["genuine_accepted"], m["genuine_intact"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
