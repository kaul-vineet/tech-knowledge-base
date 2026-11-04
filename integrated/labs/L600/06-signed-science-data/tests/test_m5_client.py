"""M5: the client verifies the release end to end, including the transparency log."""
import unittest

from _world import world

import checks
import client as CL
import tlog


class M5Client(unittest.TestCase):
    def test_milestone(self):
        ok, d = checks.m5_client(world())
        self.assertTrue(ok, d)

    def test_release_missing_from_log_is_rejected(self):
        w = world()
        c = w.client()
        empty = tlog.Log(w.pub.log_key)
        empty.entries = list(w.pub.log.entries[:3])  # a log that never heard of v4
        with self.assertRaises(CL.Rejected):
            c.fetch(w.mirrors[0], empty, w.now + 100)

    def test_rewritten_history_is_detected(self):
        w = world()
        c = w.client()
        early = tlog.Log(w.pub.log_key)
        early.entries = [b"something else"] + list(w.pub.log.entries[1:2])
        c.sth = early.sth(0)["signed"]  # the client once saw a different 2-entry history
        with self.assertRaises(CL.Rejected) as e:
            c.fetch(w.mirrors[0], w.pub.log, w.now + 100)
        self.assertIn("history rewritten", str(e.exception))


if __name__ == "__main__":
    unittest.main()
