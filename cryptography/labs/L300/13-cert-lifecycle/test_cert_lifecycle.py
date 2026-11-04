import datetime as dt
import unittest

import cert_lifecycle as cl

QUIET = lambda line: None  # noqa: E731


class TestLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ca_key, cls.ca = cl.local_ca.make_root()
        cls.cert = cl.issue(cls.ca_key, cls.ca, cl.T0)

    def test_short_lived_and_backdated(self):
        self.assertEqual((self.cert.not_valid_after_utc - self.cert.not_valid_before_utc) / cl.HOUR, 160)
        self.assertLessEqual(self.cert.not_valid_before_utc, cl.T0 - cl.HOUR)

    def test_fault_static_server_serves_expired_cert(self):
        failures, srv = cl.simulate(cl.Server, days=8, log=QUIET)
        self.assertEqual(failures[0], 160)
        self.assertEqual(len(failures), 32)
        self.assertEqual(srv.renewals, 0)

    def test_crl(self):
        crl = cl.make_crl(self.ca_key, self.ca, [self.cert.serial_number], cl.T0)
        self.assertEqual(cl.check_revocation(self.cert, crl, self.ca, cl.T0), "revoked (key_compromise)")
        other = cl.issue(self.ca_key, self.ca, cl.T0)
        self.assertEqual(cl.check_revocation(other, crl, self.ca, cl.T0), "good")
        self.assertEqual(cl.check_revocation(self.cert, crl, self.ca, cl.T0 + 25 * cl.HOUR), "stale CRL")

    def test_crl_from_another_ca_is_rejected(self):
        k2, ca2 = cl.local_ca.make_root("Some Other Root")
        forged = cl.make_crl(k2, ca2, [], cl.T0)
        self.assertEqual(cl.check_revocation(self.cert, forged, self.ca, cl.T0), "bad CRL")

    def test_clock_skew(self):
        slow = cl.T0 - dt.timedelta(minutes=5)
        exact = cl.issue(self.ca_key, self.ca, cl.T0, backdate=dt.timedelta(0))
        self.assertFalse(cl.handshake_ok(exact, self.ca, slow))
        self.assertTrue(cl.handshake_ok(self.cert, self.ca, slow))


if __name__ == "__main__":
    unittest.main()
