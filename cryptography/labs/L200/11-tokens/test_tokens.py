import json
import os
import time
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import tokens as lab
from naive import naive_verify


class TestTokens(unittest.TestCase):
    def setUp(self):
        self.sk = Ed25519PrivateKey.generate()
        self.keys = {"EdDSA": self.sk.public_key()}
        self.now = 1_800_000_000
        self.claims = {"sub": "alice", "aud": "orders-api", "exp": self.now + 300}

    def test_roundtrip_eddsa_and_hs256(self):
        tok = lab.sign(self.claims, "EdDSA", self.sk)
        self.assertEqual(lab.verify(tok, self.keys, "orders-api", now=self.now)["sub"], "alice")
        secret = os.urandom(32)
        tok = lab.sign(self.claims, "HS256", secret)
        self.assertEqual(lab.verify(tok, {"HS256": secret}, "orders-api", now=self.now)["sub"], "alice")

    def test_alg_none_and_key_confusion_rejected(self):
        none_tok = lab.b64u(b'{"alg":"none"}') + "." + lab.b64u(json.dumps(self.claims).encode()) + "."
        confused = lab.sign(self.claims, "HS256", self.sk.public_key().public_bytes_raw())
        for tok in (none_tok, confused):
            self.assertEqual(naive_verify(tok, self.sk.public_key().public_bytes_raw())["sub"], "alice")  # the bug
            with self.assertRaisesRegex(lab.TokenError, "not allowed"):
                lab.verify(tok, self.keys, "orders-api", now=self.now)

    def test_time_and_audience(self):
        cases = {"expired": dict(self.claims, exp=self.now - 31), "nbf": dict(self.claims, nbf=self.now + 60),
                 "no exp": {"aud": "orders-api"}, "audience": dict(self.claims, aud=["billing-api"])}
        for msg, claims in cases.items():
            with self.assertRaises(lab.TokenError, msg=msg):
                lab.verify(lab.sign(claims, "EdDSA", self.sk), self.keys, "orders-api", now=self.now)
        ok = dict(self.claims, exp=self.now - 29, aud=["x", "orders-api"])  # inside 30 s leeway, list audience
        self.assertTrue(lab.verify(lab.sign(ok, "EdDSA", self.sk), self.keys, "orders-api", now=self.now))

    def test_tamper_and_malformed(self):
        h, p, s = lab.sign(self.claims, "EdDSA", self.sk).split(".")
        bad_p = lab.b64u(json.dumps(dict(self.claims, sub="mallory")).encode())
        with self.assertRaisesRegex(lab.TokenError, "bad signature"):
            lab.verify(f"{h}.{bad_p}.{s}", self.keys, "orders-api", now=self.now)
        with self.assertRaisesRegex(lab.TokenError, "malformed"):
            lab.verify("not-a-token", self.keys, "orders-api", now=self.now)

    def test_default_clock(self):
        tok = lab.sign(dict(self.claims, exp=time.time() + 60), "EdDSA", self.sk)
        self.assertEqual(lab.verify(tok, self.keys, "orders-api")["sub"], "alice")


if __name__ == "__main__":
    unittest.main()
