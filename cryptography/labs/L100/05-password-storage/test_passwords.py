import unittest

import passwords as lab

RFC9106_ARGON2ID_TAG = "0d640df58d78766c08c037a34a8b53c9d01ef0452d75b65eb52520e96b01e659"
RFC7914_SCRYPT_DK = ("fdbabe1c9d3472007856e7190d01e9fe7c6ad7cbc8237830e77376634b373162"
                     "2eaf30d92e22a3886ff109279d9830dac727afb94a83ee6d8360cbdfa2cc0640")


class TestPasswords(unittest.TestCase):
    def test_official_vectors(self):
        self.assertEqual(lab.rfc9106_argon2id_vector(), RFC9106_ARGON2ID_TAG)
        self.assertEqual(lab.rfc7914_scrypt_vector(), RFC7914_SCRYPT_DK)

    def test_argon2id_phc_roundtrip_with_owasp_params(self):
        h = lab.hash_password("pw")
        self.assertTrue(h.startswith("$argon2id$v=19$m=19456,t=2,p=1$"))
        self.assertTrue(lab.verify_password("pw", h))
        self.assertFalse(lab.verify_password("pW", h))
        self.assertNotEqual(h, lab.hash_password("pw"))  # unique salt

    def test_scrypt_fallback(self):
        s = lab.scrypt_hash("pw")
        self.assertTrue(s.startswith("scrypt$131072$8$1$"))
        self.assertTrue(lab.scrypt_verify("pw", s))
        self.assertFalse(lab.scrypt_verify("px", s))


if __name__ == "__main__":
    unittest.main()
