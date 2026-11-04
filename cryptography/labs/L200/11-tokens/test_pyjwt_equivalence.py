"""Equivalent library: PyJWT accepts our tokens and we accept PyJWT's (same JWS compact format).
Skipped if PyJWT is not installed (pip install -r ../../../requirements-L200.txt)."""
import os
import time
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import tokens as lab

try:
    import jwt
except ImportError:
    jwt = None


@unittest.skipIf(jwt is None, "PyJWT not installed")
class TestPyJWT(unittest.TestCase):
    def setUp(self):
        self.claims = {"sub": "alice", "aud": "orders-api", "exp": int(time.time()) + 300}

    def test_pyjwt_reads_ours(self):
        sk = Ed25519PrivateKey.generate()
        ours = lab.sign(self.claims, "EdDSA", sk)
        self.assertEqual(jwt.decode(ours, sk.public_key(), algorithms=["EdDSA"], audience="orders-api")["sub"], "alice")

    def test_we_read_pyjwt(self):
        secret = os.urandom(32)
        theirs = jwt.encode(self.claims, secret, algorithm="HS256")
        self.assertEqual(lab.verify(theirs, {"HS256": secret}, "orders-api")["sub"], "alice")

    def test_pyjwt_enforces_allow_list_too(self):
        sk = Ed25519PrivateKey.generate()
        confused = lab.sign(self.claims, "HS256", sk.public_key().public_bytes_raw())
        with self.assertRaises(jwt.InvalidTokenError):
            jwt.decode(confused, sk.public_key(), algorithms=["EdDSA"], audience="orders-api")
        with self.assertRaises(jwt.InvalidAudienceError):
            jwt.decode(lab.sign(self.claims, "EdDSA", sk), sk.public_key(), algorithms=["EdDSA"], audience="billing")


if __name__ == "__main__":
    unittest.main()
