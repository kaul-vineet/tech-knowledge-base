import unittest

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

import seal_box as lab


class TestSealBox(unittest.TestCase):
    def test_rfc7748_vector(self):
        v = lab.RFC7748
        a, b = X25519PrivateKey.from_private_bytes(v["a"]), X25519PrivateKey.from_private_bytes(v["b"])
        self.assertEqual(b.public_key().public_bytes_raw(), v["B"])
        self.assertEqual(a.exchange(b.public_key()), v["K"])
        self.assertEqual(b.exchange(a.public_key()), v["K"])

    def test_roundtrip_and_overhead(self):
        bob = X25519PrivateKey.generate()
        blob = lab.seal(bob.public_key(), b"hello", b"hdr")
        self.assertEqual(len(blob), 5 + 48)
        self.assertEqual(lab.open_(bob, blob, b"hdr"), b"hello")

    def test_wrong_key_tamper_aad(self):
        bob, eve = X25519PrivateKey.generate(), X25519PrivateKey.generate()
        blob = lab.seal(bob.public_key(), b"secret", b"hdr")
        bad = bytearray(blob)
        bad[-1] ^= 1
        for args in ((eve, blob, b"hdr"), (bob, bytes(bad), b"hdr"), (bob, blob, b"other")):
            with self.assertRaises(InvalidTag):
                lab.open_(*args)

    def test_small_order_point_rejected(self):
        with self.assertRaises(ValueError):  # pyca refuses; _key() would also refuse an all-zero secret
            lab.open_(X25519PrivateKey.generate(), bytes(32) + bytes(16))
        with self.assertRaises(ValueError):
            lab._key(bytes(32), bytes(32), bytes(32))

    def test_fresh_ephemeral_each_time(self):
        pub = X25519PrivateKey.generate().public_key()
        self.assertEqual(len({lab.seal(pub, b"x")[:32] for _ in range(50)}), 50)
        self.assertIsInstance(X25519PublicKey.from_public_bytes(lab.seal(pub, b"x")[:32]), X25519PublicKey)


if __name__ == "__main__":
    unittest.main()
