"""Build task check. Default: tests solution_multi.py.
Test YOUR version:  macOS  BUILD_IMPL=seal_box python -m unittest test_build_task
                    Windows  $env:BUILD_IMPL="seal_box"; python -m unittest test_build_task"""
import importlib
import os
import unittest

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

impl = importlib.import_module(os.environ.get("BUILD_IMPL", "solution_multi"))


class TestMultiRecipient(unittest.TestCase):
    def test_each_recipient_can_open(self):
        alice, bob, eve = (X25519PrivateKey.generate() for _ in range(3))
        blob = impl.seal_multi([alice.public_key(), bob.public_key()], b"backup.tar")
        self.assertEqual(impl.open_multi(alice, blob), b"backup.tar")
        self.assertEqual(impl.open_multi(bob, blob), b"backup.tar")
        with self.assertRaises(ValueError):
            impl.open_multi(eve, blob)

    def test_payload_encrypted_once(self):
        rs = [X25519PrivateKey.generate().public_key() for _ in range(3)]
        self.assertEqual(len(impl.seal_multi(rs, b"x" * 1000)), 1 + 3 * 80 + 1000 + 16)

    def test_header_tamper_detected(self):
        alice = X25519PrivateKey.generate()
        blob = bytearray(impl.seal_multi([alice.public_key(), X25519PrivateKey.generate().public_key()], b"data"))
        blob[1 + 80 + 5] ^= 1  # flip a bit inside the SECOND stanza (not alice's)
        with self.assertRaises(InvalidTag):
            impl.open_multi(alice, bytes(blob))


if __name__ == "__main__":
    unittest.main()
