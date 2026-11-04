"""Each seam line holds on the defended design AND its guard is proven (the matching seeded fault breaks it)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # the lab folder
import scenarios as sc  # noqa: E402


class TestSeams(unittest.TestCase):
    def test_nonce_failover(self):
        self.assertTrue(sc.seam_nonce_failover(n=600)["pass"])

    def test_rotation_replay(self):
        self.assertTrue(sc.seam_rotation()["pass"])

    def test_idempotency(self):
        self.assertTrue(sc.seam_idempotency()["pass"])

    def test_contract(self):
        self.assertTrue(sc.seam_contract()["pass"])


if __name__ == "__main__":
    unittest.main()
