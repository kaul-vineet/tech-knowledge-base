"""M1: envelope encryption with versioned KEKs, crash-safe rotation, authenticated headers, ACL."""
import base64
import copy
import json
import unittest

from cryptography.exceptions import InvalidTag

from capstone_testing import ServiceCase


class TestM1(ServiceCase):
    def test_retire_refused_until_rewrap_done(self):
        svc = self.ns.svc
        svc.rotate_kek()
        with self.assertRaises(RuntimeError):
            svc.rewrap(crash_after=1)
        with self.assertRaises(PermissionError):
            svc.retire(1)  # records still wrapped by v1
        svc.rewrap()
        self.assertEqual(svc.retire(1), {"retired": "docs-kek:v1"})
        self.assertTrue(all(svc.get("alice", d).startswith(b"contract") for d in svc.docs))

    def test_header_relabel_rejected(self):
        rec = self.ns.svc.docs["doc-2"]
        saved = copy.deepcopy(rec["env"])
        rec["env"]["h"]["ctx"] = "doc-3"  # move the ciphertext to another row
        try:
            with self.assertRaises((ValueError, InvalidTag)):
                self.ns.svc.get("alice", "doc-2")
        finally:
            rec["env"] = saved

    def test_store_holds_no_plaintext_keys(self):
        dump = json.dumps(self.ns.svc.docs)
        self.assertNotIn("contract", dump)
        for rec in self.ns.svc.docs.values():
            self.assertEqual(set(rec), {"env", "kek", "wdek"})
            self.assertEqual(len(base64.b64decode(rec["wdek"])), 60)  # 12 nonce + 32 DEK + 16 tag

    def test_unlisted_user_denied(self):
        with self.assertRaises(PermissionError):
            self.ns.svc.get("eve", "doc-1")
        self.assertEqual(self.ns.audit.entries[-1]["result"], "denied")


if __name__ == "__main__":
    unittest.main()
