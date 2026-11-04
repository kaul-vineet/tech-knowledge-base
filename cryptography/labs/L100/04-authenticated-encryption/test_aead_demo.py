import os
import unittest

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

import aead_demo as lab


class TestAEAD(unittest.TestCase):
    def test_rfc8439_vector(self):
        v = lab.RFC8439
        aead = ChaCha20Poly1305(v["key"])
        self.assertEqual(aead.encrypt(v["nonce"], v["pt"], v["aad"]), v["ct"] + v["tag"])
        self.assertEqual(aead.decrypt(v["nonce"], v["ct"] + v["tag"], v["aad"]), v["pt"])

    def test_gcm_tc14_vector(self):
        g = lab.GCM_TC14
        self.assertEqual(AESGCM(g["key"]).encrypt(g["nonce"], g["pt"], None), g["ct"] + g["tag"])

    def test_tamper_and_aad(self):
        for aead in (AESGCM(AESGCM.generate_key(bit_length=256)),
                     ChaCha20Poly1305(ChaCha20Poly1305.generate_key())):
            blob = lab.seal(aead, b"secret", b"hdr")
            self.assertEqual(lab.open_(aead, blob, b"hdr"), b"secret")
            bad = bytearray(blob)
            bad[-1] ^= 1
            with self.assertRaises(InvalidTag):
                lab.open_(aead, bytes(bad), b"hdr")
            with self.assertRaises(InvalidTag):
                lab.open_(aead, blob, b"other")

    def test_nonces_are_fresh(self):
        aead = AESGCM(AESGCM.generate_key(bit_length=256))
        nonces = {lab.seal(aead, b"x", None)[:12] for _ in range(1000)}
        self.assertEqual(len(nonces), 1000)

    def test_nonce_reuse_leaks_xor(self):
        k, n = os.urandom(32), os.urandom(12)
        p1, p2 = b"A" * 16, b"B" * 16
        c1 = AESGCM(k).encrypt(n, p1, None)[:16]
        c2 = AESGCM(k).encrypt(n, p2, None)[:16]
        self.assertEqual(bytes(a ^ b for a, b in zip(c1, c2)), bytes(a ^ b for a, b in zip(p1, p2)))


if __name__ == "__main__":
    unittest.main()
