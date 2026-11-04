"""Seam S3 (distributed systems <-> cryptography): a lagging mirror is honest but old; the client must still refuse
to go backwards (rollback) and must notice a mirror that never updates (freeze). Fake clock only - run 3x."""
import json
import unittest

from _world import world

import checks
import client as CL
import publisher as P


class SeamFreshness(unittest.TestCase):
    def test_seam(self):
        ok, d = checks.s3_freshness(world())
        self.assertTrue(ok, d)
        self.assertIn("rollback", d["lagging"])
        self.assertIn("freeze", d["frozen"])

    def test_expiry_boundary_on_fake_clock(self):
        w = world()
        expires = json.loads(w.stale.timestamp)["signed"]["expires"]
        self.assertEqual(expires, 2 * 1200 + P.TTL)
        for t, accepted in ((expires - 1, True), (expires, False), (expires + 1, False)):
            c = w.client()  # never saw v4, so only the clock can protect it
            try:
                c.fetch(w.stale, w.pub.log, t)
                got = True
            except CL.Rejected:
                got = False
            self.assertEqual(got, accepted, t)

    def test_failover_to_a_fresh_mirror(self):
        w = world()
        c = w.client()
        c.fetch(w.mirrors[0], w.pub.log, w.now + 100)
        name, m, reasons = c.fetch_any([w.stale, w.mirrors[1]], w.pub.log, w.now + 200)
        self.assertEqual((name, m["version"]), ("m1", 4))
        self.assertIn("rollback", reasons[0])

    def test_without_freshness_checks_the_attack_works(self):
        ok, d = checks.s3_freshness(world("no-freshness"))
        self.assertFalse(ok)
        self.assertEqual(d["lagging"], "ACCEPTED")


if __name__ == "__main__":
    unittest.main()
