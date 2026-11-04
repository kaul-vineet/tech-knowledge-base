"""Lab tests: PIN handling, roles, handles, one-way attributes, audit events, ceremony transcript."""
import unittest

import ceremony
import soft_token as st


class TestSoftToken(unittest.TestCase):
    def setUp(self):
        self.t = st.SoftToken("t", so_pin="so", user_pin="pin")
        self.s = self.t.open_session()

    def test_pin_lockout_after_three_failures(self):
        for _ in range(3):
            with self.assertRaises(st.PKCS11Error):
                self.s.login("USER", "bad")
        with self.assertRaisesRegex(st.PKCS11Error, "CKR_PIN_LOCKED"):
            self.s.login("USER", "pin")  # even the right PIN

    def test_so_cannot_use_keys(self):
        self.s.login("SO", "so")
        with self.assertRaisesRegex(st.PKCS11Error, "CKR_USER_NOT_LOGGED_IN"):
            self.s.generate_key_pair(st.CKM_EDDSA, "k")

    def test_sign_via_handle_and_verify_with_public_key(self):
        self.s.login("USER", "pin")
        pub, priv = self.s.generate_key_pair(st.CKM_ECDSA_SHA256, "k", {st.CKA_SENSITIVE: True, st.CKA_EXTRACTABLE: False})
        sig = self.s.sign(priv, st.CKM_ECDSA_SHA256, b"data")
        key = st.ser.load_der_public_key(self.s.get_attribute_value(pub, st.CKA_VALUE))
        key.verify(sig, b"data", st.ec.ECDSA(st.hashes.SHA256()))
        self.assertEqual(self.s.find_objects("k"), [priv])

    def test_sensitive_is_one_way(self):
        self.s.login("USER", "pin")
        _, priv = self.s.generate_key_pair(st.CKM_EDDSA, "k", {st.CKA_SENSITIVE: True, st.CKA_EXTRACTABLE: False})
        with self.assertRaisesRegex(st.PKCS11Error, "CKR_ATTRIBUTE_READ_ONLY"):
            self.s.set_attribute_value(priv, st.CKA_SENSITIVE, False)
        with self.assertRaisesRegex(st.PKCS11Error, "CKR_ATTRIBUTE_SENSITIVE"):
            self.s.get_attribute_value(priv, st.CKA_VALUE)

    def test_audit_records_each_operation(self):
        self.s.login("USER", "pin")
        _, priv = self.s.generate_key_pair(st.CKM_EDDSA, "k")
        self.s.sign(priv, st.CKM_EDDSA, b"x")
        self.assertEqual([st.json.loads(e)["op"] for e in self.t.audit], ["C_Login", "C_GenerateKeyPair", "C_Sign"])

    def test_ceremony_transcript_detects_edits(self):
        rec = ceremony.run_ceremony("cust", ["w1", "w2"])
        self.assertTrue(ceremony.verify_ceremony(rec))
        rec["steps"][0]["by"] = "someone-else"
        self.assertFalse(ceremony.verify_ceremony(rec))
        with self.assertRaises(ValueError):
            ceremony.run_ceremony("cust", ["w1"])


if __name__ == "__main__":
    unittest.main()
