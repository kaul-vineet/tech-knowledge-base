import time
import unittest

import randomness as lab


class TestRandomness(unittest.TestCase):
    def test_secure_material_sizes(self):
        m = lab.secure_material()
        self.assertEqual(len(m["aes256_key"]), 32)
        self.assertEqual(len(m["gcm_nonce"]), 12)
        self.assertEqual(len(m["session_id_hex"]), 32)
        self.assertEqual(len(m["pin_6_digits"]), 6)
        self.assertGreaterEqual(len(m["api_token_urlsafe"]), 43)

    def test_secrets_not_repeating(self):
        self.assertEqual(len({lab.secure_material()["aes256_key"] for _ in range(100)}), 100)

    def test_predictable_token_is_recovered(self):
        issued = int(time.time()) - 500
        token = lab.insecure_reset_token(issued)
        self.assertEqual(lab.attacker_recovers(token, around=int(time.time()), window=600), issued)


if __name__ == "__main__":
    unittest.main()
