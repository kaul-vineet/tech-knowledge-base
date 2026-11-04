"""M4 (seam: key rotation vs log replay): epochs travel in the log, so a fresh device replays from index 1;
carol (removed) reads epoch 1 only; a late epoch-1 envelope committed after the removal is rejected."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # the lab folder
import scenarios as sc  # noqa: E402


class TestM4RotationReplay(unittest.TestCase):
    def test_rotation_and_replay(self):
        r = sc.m4_rotation()
        self.assertEqual(r["replay_from_index_1"], {"alice": "20/20", "bob": "20/20", "carol": "10/20"})
        self.assertEqual((r["stale_epoch_rejected"], r["carol_reads_after_removal"]), (1, 0))
        self.assertEqual(r["carol_send_after_removal"], 409)
        self.assertTrue(r["replicas_agree"])

    def test_accepting_stale_epochs_leaks_to_removed_member(self):
        self.assertEqual(sc.m4_rotation({"accept-stale-epoch"})["carol_reads_after_removal"], 1)


if __name__ == "__main__":
    unittest.main()
