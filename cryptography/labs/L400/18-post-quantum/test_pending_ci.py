"""Equivalence checks that need software the sandbox lacks (pending CI): liboqs-python and a PQ-capable TLS stack."""
import ssl
import sys
import unittest

import oqs_crosscheck
import pq_tls_probe

try:
    import oqs  # noqa: F401
    HAVE_OQS = True
except ImportError:
    HAVE_OQS = False
PQ_TLS = hasattr(ssl.SSLSocket, "group") and ssl.OPENSSL_VERSION_INFO >= (3, 5)


class TestPendingCI(unittest.TestCase):
    @unittest.skipUnless(HAVE_OQS, "liboqs-python not installed (CI ubuntu job installs it)")
    def test_liboqs_interop(self):
        r = oqs_crosscheck.crosscheck()
        self.assertTrue(r["liboqs->cryptography"] and r["cryptography->liboqs"])
        self.assertEqual(r["sizes"], (1184, 1088, 32))

    @unittest.skipUnless(PQ_TLS, f"needs Python 3.15+ and OpenSSL 3.5+ (have {sys.version.split()[0]}, {ssl.OPENSSL_VERSION})")
    def test_tls_negotiates_hybrid_group(self):
        self.assertIn("X25519MLKEM768", pq_tls_probe.probe())

    def test_probe_reports_why_it_skips(self):
        self.assertTrue(pq_tls_probe.probe().startswith(("skipped", "negotiated")))


if __name__ == "__main__":
    unittest.main()
