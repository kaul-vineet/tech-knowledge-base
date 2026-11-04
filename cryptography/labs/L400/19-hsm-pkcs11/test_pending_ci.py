"""SoftHSM2 equivalence (pending CI): runs only when PKCS11_MODULE points at a PKCS#11 library with token kb-l19."""
import os
import unittest

import pkcs11_softhsm


@unittest.skipUnless(os.environ.get("PKCS11_MODULE"), "PKCS11_MODULE not set (CI ubuntu job: softhsm2 + python-pkcs11)")
class TestSoftHSM(unittest.TestCase):
    def test_non_exportable_key_signs_via_handle(self):
        r = pkcs11_softhsm.run()
        self.assertEqual(r, {"verified_with_cryptography": True, "private_value_readable": False,
                             "never_extractable": True, "always_sensitive": True})


if __name__ == "__main__":
    unittest.main()
