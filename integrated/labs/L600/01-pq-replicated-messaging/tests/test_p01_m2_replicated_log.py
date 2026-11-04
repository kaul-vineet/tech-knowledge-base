"""M2: sealed envelopes on lesson 12's Raft log survive a leader crash; committed logs are identical, contain no
plaintext, and every replica replays to the same 30 messages."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # the lab folder
import scenarios as sc  # noqa: E402


class TestM2ReplicatedLog(unittest.TestCase):
    def test_replicated_log(self):
        r = sc.m2_replicated()
        self.assertTrue(r["committed_logs_identical"])
        self.assertEqual(r["plaintext_in_any_log"], 0)
        self.assertEqual(r["safety_violations"], 0)
        self.assertEqual(set(r["alice_reads_per_replica"].values()), {30})
        self.assertTrue(r["pass"])


if __name__ == "__main__":
    unittest.main()
