"""Build task check. Default: tests solution_keyring.py.
Test YOUR version:  macOS  BUILD_IMPL=signatures python -m unittest test_build_task
                    Windows  $env:BUILD_IMPL="signatures"; python -m unittest test_build_task"""
import importlib
import os
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

impl = importlib.import_module(os.environ.get("BUILD_IMPL", "solution_keyring"))


class TestKeyring(unittest.TestCase):
    def test_rotation(self):
        old, new, stranger = (Ed25519PrivateKey.generate() for _ in range(3))
        keyring = [old.public_key(), new.public_key()]
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "rel.bin"
            f.write_bytes(b"v2")
            for signer, expected in ((old, impl.key_id(old.public_key())),
                                     (new, impl.key_id(new.public_key())), (stranger, None)):
                sig = f.with_name("rel.bin.sig")
                sig.write_bytes(signer.sign(f.read_bytes()))
                self.assertEqual(impl.verify_with_keyring(keyring, f, sig), expected)

    def test_key_id_is_stable_and_short(self):
        pub = Ed25519PrivateKey.generate().public_key()
        self.assertEqual(impl.key_id(pub), impl.key_id(pub))
        self.assertEqual(len(impl.key_id(pub)), 16)


if __name__ == "__main__":
    unittest.main()
