import base64
import unittest

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import compare as lab


class TestCompare(unittest.TestCase):
    def test_rfc4648_vectors(self):
        for raw, b64 in [(b"", b""), (b"f", b"Zg=="), (b"fo", b"Zm8="), (b"foobar", b"Zm9vYmFy")]:
            self.assertEqual(base64.b64encode(raw), b64)
        self.assertEqual(base64.b16encode(b"foobar"), b"666F6F626172")

    def test_encoding_reversible_without_key(self):
        enc = lab.encode(lab.SECRET)
        self.assertEqual(base64.b64decode(enc["base64"]), lab.SECRET)
        self.assertEqual(bytes.fromhex(enc["hex"]), lab.SECRET)

    def test_hash_deterministic_fixed_length(self):
        self.assertEqual(lab.hash_(b"x"), lab.hash_(b"x"))
        self.assertEqual(len(lab.hash_(b"x" * 10_000)), 64)

    def test_encryption_needs_key(self):
        key = AESGCM.generate_key(bit_length=256)
        blob = lab.encrypt(lab.SECRET, key)
        self.assertEqual(lab.decrypt(blob, key), lab.SECRET)
        self.assertNotEqual(blob, lab.encrypt(lab.SECRET, key))
        with self.assertRaises(InvalidTag):
            lab.decrypt(blob, AESGCM.generate_key(bit_length=256))


if __name__ == "__main__":
    unittest.main()
