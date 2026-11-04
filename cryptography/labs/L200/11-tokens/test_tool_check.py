import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization as ser

import tokens
import tool_check

EXPECTED_HS256 = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                  "eyJzdWIiOiJhbGljZSIsImF1ZCI6Im9yZGVycy1hcGkiLCJleHAiOjQxMDI0NDQ4MDAsInJvbGUiOiJ1c2VyIn0."
                  "HKTDiu55nB_ks2cnZx_ZySPZaxFaSDkNjgrdbFKN-aA")


class TestToolCheck(unittest.TestCase):
    def test_hs256_demo_token_is_fixed_and_verifies(self):
        tok = tool_check.demo_hs256()
        self.assertEqual(tok, tool_check.demo_hs256())
        self.assertEqual(tok, EXPECTED_HS256)
        self.assertEqual(tokens.verify(tok, {"HS256": tool_check.DEMO_KEY}, "orders-api"), tool_check.DEMO_CLAIMS)

    def test_written_files_verify_and_none_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            out = tool_check.write_eddsa_files(Path(d))
            pub = ser.load_pem_public_key((Path(d) / "issuer-pub.pem").read_bytes())
            good = (Path(d) / "eddsa.jwt").read_text(encoding="utf-8")
            self.assertEqual(tokens.verify(good, {"EdDSA": pub}, "orders-api")["sub"], "alice")
            self.assertEqual(out["good"], good)
            none_tok = (Path(d) / "none.jwt").read_text(encoding="utf-8")
            self.assertTrue(none_tok.endswith("."))
            with self.assertRaises(tokens.TokenError):
                tokens.verify(none_tok, {"EdDSA": pub}, "orders-api")
            self.assertNotIn(b"PRIVATE", b"".join(p.read_bytes() for p in Path(d).iterdir()))


if __name__ == "__main__":
    unittest.main()
