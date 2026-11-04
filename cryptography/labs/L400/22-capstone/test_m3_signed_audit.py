"""M3: signed, hash-chained audit log; deterministic anomaly rules."""
import json
import unittest

import audit
from capstone_testing import ServiceCase


class TestM3(ServiceCase):
    docs = 6

    def test_clean_chain_verifies(self):
        self.assertEqual(audit.verify_chain(self.ns.audit.entries, self.ns.audit_pub), [])

    def test_edit_and_delete_detected(self):
        copy = json.loads(json.dumps(self.ns.audit.entries))
        copy[2]["actor"] = "doc-service/bob"
        del copy[4]
        rules = [(a["rule"], a["seq"]) for a in audit.verify_chain(copy, self.ns.audit_pub)]
        self.assertIn(("bad_signature", 3), rules)
        self.assertIn(("chain_break", 4), rules)
        self.assertIn(("seq_gap", 6), rules)

    def test_burst_and_revoke_rules(self):
        svc, clock = self.ns.svc, self.ns.clock
        for i in range(1, 7):
            svc.get("mallory", f"doc-{i}")
            clock.advance(5)
        svc.revoke("admin", "mallory")
        clock.advance(10)
        svc.get("mallory", "doc-2")  # stale ACL cache lets this through ...
        found = {a["rule"] for a in audit.detect(self.ns.audit.entries, self.ns.audit_pub)}
        self.assertEqual(found, {"unwrap_burst", "access_after_revoke"})  # ... and the audit rules catch it
        clock.advance(400)
        with self.assertRaises(PermissionError):
            svc.get("mallory", "doc-3")


if __name__ == "__main__":
    unittest.main()
