"""Build task check. Default: tests solution_replay.py.
Test YOUR version:  macOS  BUILD_IMPL=tokens python -m unittest test_build_task
                    Windows  $env:BUILD_IMPL="tokens"; python -m unittest test_build_task"""
import importlib
import os
import unittest
import uuid

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import tokens

impl = importlib.import_module(os.environ.get("BUILD_IMPL", "solution_replay"))


class TestReplay(unittest.TestCase):
    def setUp(self):
        self.sk, self.now = Ed25519PrivateKey.generate(), 1_800_000_000
        self.keys, self.guard = {"EdDSA": self.sk.public_key()}, impl.ReplayGuard()

    def tok(self, **extra):
        return tokens.sign({"aud": "orders-api", "exp": self.now + 60, **extra}, "EdDSA", self.sk)

    def test_second_use_rejected(self):
        t = self.tok(jti=str(uuid.uuid4()))
        impl.verify_once(t, self.keys, "orders-api", self.guard, now=self.now)
        with self.assertRaisesRegex(tokens.TokenError, "replay"):
            impl.verify_once(t, self.keys, "orders-api", self.guard, now=self.now + 1)

    def test_missing_jti_and_distinct_ids(self):
        with self.assertRaises(tokens.TokenError):
            impl.verify_once(self.tok(), self.keys, "orders-api", self.guard, now=self.now)
        for _ in range(3):
            impl.verify_once(self.tok(jti=str(uuid.uuid4())), self.keys, "orders-api", self.guard, now=self.now)

    def test_memory_is_bounded_by_exp(self):
        impl.verify_once(self.tok(jti="a"), self.keys, "orders-api", self.guard, now=self.now)
        later = tokens.sign({"aud": "orders-api", "exp": self.now + 500, "jti": "b"}, "EdDSA", self.sk)
        impl.verify_once(later, self.keys, "orders-api", self.guard, now=self.now + 100)
        self.assertNotIn("a", self.guard.seen)


if __name__ == "__main__":
    unittest.main()
