"""M4: PQ-hybrid sharing with an external recipient through HPKE (ML-KEM-768 + X25519)."""
import base64
import unittest

import registry as reg
from capstone_testing import ServiceCase
from doc_service import open_shared


class TestM4(ServiceCase):
    docs = 1

    def test_recipient_opens_and_old_kem_refused(self):
        kem = reg.POLICY["share_kem"]
        self.assertTrue(reg.REGISTRY[kem].pq)
        recipient = reg.new_recipient(kem)
        package = self.ns.svc.share("alice", "doc-1", recipient.public_key())
        self.assertTrue(open_shared(package, recipient).startswith(b"contract 1"))
        old = [a.id for a in reg.REGISTRY.values() if a.kind == "kem" and a.status == "deprecated"]
        with self.assertRaises(reg.DisallowedAlgorithm):
            reg.share_seal(old[0], recipient.public_key(), b"k" * 32, b"doc-1")

    def test_share_size(self):
        kem = reg.POLICY["share_kem"]
        package = self.ns.svc.share("alice", "doc-1", reg.new_recipient(kem).public_key())
        self.assertEqual(len(base64.b64decode(package["blob"])), reg.share_overhead(kem) + 32)  # 1,120 + 16 + 32


if __name__ == "__main__":
    unittest.main()
