"""M4: hash-chained audit log with a signed checkpoint."""
import unittest

import _lab
import audit
import scenarios as sc
from run_project import audit_mutations


class TestAuditChain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env, _ = sc.s2_injection(_lab.url(), _lab.registry())

    def test_clean_log_verifies(self):
        key = audit.audit_key()
        log = self.env.audit
        self.assertEqual([e["event"] for e in log.entries], ["session_start", "decision", "executed", "decision", "answer"])
        self.assertEqual(audit.verify(log.entries, log.bodies, log.checkpoint(key), key.public_key()), [])

    def test_links_and_genesis(self):
        e = self.env.audit.entries
        self.assertEqual(e[0]["prev"], audit.GENESIS)
        self.assertTrue(all(e[i]["prev"] == e[i - 1]["hash"] for i in range(1, len(e))))

    def test_every_mutation_detected(self):
        detected, total, clean = audit_mutations(self.env.audit, set())
        self.assertEqual((detected, total, clean), (31, 31, []))

    def test_per_entry_hash_alone_misses_deletions(self):
        detected, total, _ = audit_mutations(self.env.audit, {"per-entry-hash"})
        self.assertEqual((detected, total), (20, 31))


if __name__ == "__main__":
    unittest.main()
