"""Build task check (failureLab proof). Default: tests solution_nonexportable.py.
Test YOUR version (the shipped soft_token.py has exportable defaults):
  macOS    BUILD_TARGET=mine python -m unittest -v test_build_task
  Windows  $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_TARGET
BUILD_IMPL=<module> picks any other module."""
import importlib
import os
import unittest

import soft_token as st

MODULE = "soft_token" if os.environ.get("BUILD_TARGET") == "mine" else os.environ.get("BUILD_IMPL", "solution_nonexportable")
impl = importlib.import_module(MODULE)


class TestNonExportableByDefault(unittest.TestCase):
    def setUp(self):
        self.s = impl.SoftToken("t", so_pin="so", user_pin="pin").open_session()
        self.s.login("USER", "pin")
        self.pub, self.priv = self.s.generate_key_pair(st.CKM_EDDSA, "release-signing")  # app relies on defaults

    def test_private_value_cannot_be_read(self):
        with self.assertRaisesRegex(st.PKCS11Error, "CKR_ATTRIBUTE_SENSITIVE"):
            self.s.get_attribute_value(self.priv, st.CKA_VALUE)

    def test_key_cannot_be_wrapped_out(self):
        with self.assertRaisesRegex(st.PKCS11Error, "CKR_KEY_UNEXTRACTABLE"):
            self.s.wrap_key(self.pub, self.priv)

    def test_template_cannot_opt_out(self):
        with self.assertRaises(st.PKCS11Error):
            self.s.generate_key_pair(st.CKM_EDDSA, "x", {st.CKA_EXTRACTABLE: True})

    def test_attributes_prove_lifetime_protection(self):
        self.assertTrue(self.s.get_attribute_value(self.priv, st.CKA_ALWAYS_SENSITIVE))
        self.assertTrue(self.s.get_attribute_value(self.priv, st.CKA_NEVER_EXTRACTABLE))
        self.assertEqual(len(self.s.sign(self.priv, st.CKM_EDDSA, b"release")), 64)


if __name__ == "__main__":
    unittest.main()
