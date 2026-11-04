import datetime as dt
import tempfile
import unittest
from pathlib import Path

from cryptography import x509
from cryptography.x509.verification import VerificationError

import local_ca as lab


class TestLocalCA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ca_key, cls.ca = lab.make_root()
        cls.key, cls.leaf = lab.issue_server(cls.ca_key, cls.ca)

    def test_chain_verifies_for_san_names(self):
        self.assertEqual(len(lab.verify(self.leaf, [self.ca], "localhost")), 2)

    def test_extensions(self):
        bc = self.leaf.extensions.get_extension_for_class(x509.BasicConstraints).value
        ku = self.ca.extensions.get_extension_for_class(x509.KeyUsage).value
        self.assertFalse(bc.ca)
        self.assertTrue(ku.key_cert_sign)
        self.assertEqual((self.leaf.not_valid_after_utc - self.leaf.not_valid_before_utc).days, 30)

    def test_failures(self):
        for args, kw in [((self.leaf, [self.ca], "example.com"), {}),
                         ((self.leaf, [self.ca], "localhost"), {"at": lab.NOW + dt.timedelta(days=31)}),
                         ((self.leaf, [lab.make_root("Other")[1]], "localhost"), {})]:
            with self.assertRaises(VerificationError):
                lab.verify(*args, **kw)

    def test_save_pem(self):
        with tempfile.TemporaryDirectory() as tmp:
            lab.save_pem(Path(tmp), self.ca, self.key, self.leaf)
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ["ca.pem", "server-key.pem", "server.pem"])
            self.assertEqual(x509.load_pem_x509_certificate((Path(tmp) / "server.pem").read_bytes()), self.leaf)


if __name__ == "__main__":
    unittest.main()
