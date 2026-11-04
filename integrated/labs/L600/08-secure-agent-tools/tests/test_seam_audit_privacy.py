"""Seam cryptography <-> application-architecture: the audit log proves what happened without storing secrets."""
import unittest

import _lab
import audit
import scenarios as sc
from adapters import T0, ScriptedModel

SECRET = "sk-demo-000000000000000000000000"


class TestAuditPrivacySeam(unittest.TestCase):
    def setUp(self):
        self.env = sc.Env(ScriptedModel([("send_email", {"to": "alice@corp.example", "subject": f"key {SECRET}",
                                                         "body": f"the key is {SECRET}"})], answer=f"Sent {SECRET}."),
                          _lab.registry(), _lab.FAULTS)
        _, self.token = self.env.run("Email the key to alice@corp.example.", ["send_email"])

    def test_no_secret_token_or_body_in_log(self):
        text = self.env.audit.text()
        for leak in (SECRET, self.token, "the key is"):
            self.assertNotIn(leak, text)
        self.assertIn("[REDACTED]", text)

    def test_retention_purge_keeps_chain_verifiable(self):
        key = audit.audit_key()
        gone = self.env.audit.purge_bodies(T0 + 1)
        self.assertEqual(len(gone), len(self.env.audit.entries))
        cp = self.env.audit.checkpoint(key)
        self.assertEqual(audit.verify(self.env.audit.entries, self.env.audit.bodies, cp, key.public_key()), [])


if __name__ == "__main__":
    unittest.main()
