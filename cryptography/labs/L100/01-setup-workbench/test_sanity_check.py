import unittest

import sanity_check


class TestWorkbench(unittest.TestCase):
    def setUp(self):
        self.r = sanity_check.run_checks()

    def test_pinned_version(self):
        self.assertTrue(self.r["cryptography_pinned"], self.r["cryptography"])

    def test_known_answer_and_roundtrip(self):
        self.assertTrue(self.r["sha256_known_answer"])
        self.assertTrue(self.r["aesgcm_roundtrip"])
        self.assertEqual(self.r["secrets_token_len"], 32)

    def test_argon2id(self):
        self.assertTrue(self.r["argon2id_available"])


if __name__ == "__main__":
    unittest.main()
