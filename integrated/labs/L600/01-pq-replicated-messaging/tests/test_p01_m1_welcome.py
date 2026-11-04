"""M1: every member (and the sealer) derives the same epoch secret from a hybrid X25519MLKEM768 welcome; a
downgraded (32-byte, X25519-only) share is refused by lesson 18's strict client."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # the lab folder
import scenarios as sc  # noqa: E402


class TestM1Welcome(unittest.TestCase):
    def test_welcome(self):
        r = sc.m1_welcome()
        self.assertEqual(r["distinct_secrets"], 1)
        self.assertEqual((r["key_package_B"], r["welcome_B"]), (1216, 1180))
        self.assertTrue(r["downgraded_32B_share"].startswith("refused"))
        self.assertTrue(r["pass"])


if __name__ == "__main__":
    unittest.main()
