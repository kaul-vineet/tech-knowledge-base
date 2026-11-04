import ssl
import tempfile
import unittest
from pathlib import Path

import tls_localhost as lab


class TestTLS(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pki = lab.make_pki(Path(self.tmp.name) / "pki")
        self.other = lab.make_pki(Path(self.tmp.name) / "other")
        self.port = lab.start_server(lab.server_context(self.pki), connections=1)

    def tearDown(self):
        self.tmp.cleanup()

    def test_handshake_ok(self):
        version, cipher, data = lab.connect(self.port, self.pki / "ca.pem", "localhost")
        self.assertIn(version, ("TLSv1.3", "TLSv1.2"))
        self.assertEqual(data, b"hello over TLS\n")
        self.assertGreaterEqual(cipher[2], 128)

    def test_hostname_mismatch(self):
        with self.assertRaises(ssl.SSLCertVerificationError) as cm:
            lab.connect(self.port, self.pki / "ca.pem", "example.com")
        self.assertEqual(cm.exception.verify_code, 62)  # X509_V_ERR_HOSTNAME_MISMATCH

    def test_untrusted_ca(self):
        with self.assertRaises(ssl.SSLCertVerificationError) as cm:
            lab.connect(self.port, self.other / "ca.pem", "localhost")
        self.assertEqual(cm.exception.verify_code, 20)  # unable to get local issuer certificate

    def test_server_refuses_old_tls(self):
        self.assertEqual(lab.server_context(self.pki).minimum_version, ssl.TLSVersion.TLSv1_2)


if __name__ == "__main__":
    unittest.main()
