import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import signatures as lab


class TestSignatures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.key = Ed25519PrivateKey.generate()
        self.file = self.d / "rel.bin"
        self.file.write_bytes(b"release bytes")

    def tearDown(self):
        self.tmp.cleanup()

    def test_rfc8032_test1(self):
        v = lab.RFC8032_T1
        k = Ed25519PrivateKey.from_private_bytes(v["secret"])
        self.assertEqual(k.public_key().public_bytes_raw(), v["public"])
        self.assertEqual(k.sign(b""), v["sig"])

    def test_roundtrip_through_pem(self):
        lab.save_keys(self.key, self.d)
        sig = lab.sign_file(self.key, self.file)
        self.assertEqual(len(sig.read_bytes()), 64)
        self.assertTrue(lab.verify_file(lab.load_public(self.d / "release.pub"), self.file, sig))

    def test_tamper_and_wrong_key(self):
        sig = lab.sign_file(self.key, self.file)
        self.assertFalse(lab.verify_file(Ed25519PrivateKey.generate().public_key(), self.file, sig))
        self.file.write_bytes(b"release bytez")
        self.assertFalse(lab.verify_file(self.key.public_key(), self.file, sig))

    def test_public_pem_has_no_private_material(self):
        lab.save_keys(self.key, self.d)
        self.assertNotIn(b"PRIVATE", (self.d / "release.pub").read_bytes())


if __name__ == "__main__":
    unittest.main()
