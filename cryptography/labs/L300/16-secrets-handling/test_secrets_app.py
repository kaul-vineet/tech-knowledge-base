import io
import tempfile
import unittest
from pathlib import Path

import secrets_app as app


class TestSecrets(unittest.TestCase):
    def test_file_wins_over_env_and_missing_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "k"
            f.write_text("from-file\n", encoding="utf-8")
            env = {"K_FILE": str(f), "K": "from-env"}
            self.assertEqual(app.load_secret("K", env).reveal(), "from-file")
        self.assertEqual(app.load_secret("K", {"K": "from-env"}).reveal(), "from-env")
        with self.assertRaises(KeyError):
            app.load_secret("K", {})

    def test_secret_hidden_in_repr_and_wipe(self):
        s = app.Secret("sk_live_x")
        self.assertNotIn("sk_live", repr({"key": s}) + f"{s}")
        s.wipe()
        self.assertEqual(s.reveal(), "\x00" * 9)

    def test_fault_debug_line_leaks_and_scanner_sees_it(self):
        buf, key = io.StringIO(), app.Secret("sk_demo_" + "a1" * 16)
        app.handle_request(app.json_logger(buf, "t1"), key, 7, debug=True)
        kinds = {k for _, k, _ in app.scan_log(buf.getvalue(), known=[key.reveal()])}
        self.assertEqual(kinds, {"BEARER", "KNOWN_SECRET", "SENSITIVE_KEY"})

    def test_scanner_no_false_positives(self):
        clean = 'token_ttl_seconds: 3600\ndb_password: "[REDACTED]"\n{"msg": "order sent", "status": 200}'
        self.assertEqual(app.scan_log(clean), [])
        self.assertEqual(app.scan_log("smtp://u:pw@host")[0][1], "URL_CREDENTIALS")

    def test_dual_validity_rotation(self):
        keys = app.ApiKeys("old-key")
        keys.rotate("new-key", now=1000, grace_s=3600)
        self.assertEqual(keys.check("new-key", 1001), "current")
        self.assertEqual(keys.check("old-key", 4600), "previous")  # inside the window
        self.assertIsNone(keys.check("old-key", 4601))  # window closed
        self.assertIsNone(keys.check("guess", 1001))


if __name__ == "__main__":
    unittest.main()
