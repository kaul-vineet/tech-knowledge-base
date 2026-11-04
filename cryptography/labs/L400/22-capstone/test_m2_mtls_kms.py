"""M2: the KMS sits behind mutual TLS; the caller's identity comes from its certificate."""
import unittest

import kms
import solution_mtls
from capstone_testing import ServiceCase


class TestM2(ServiceCase):
    docs = 1

    def test_client_without_cert_refused(self):
        with self.assertRaises(OSError):
            kms.KMSClient(self.ns.port, self.ns.pki, with_cert=False).call("rotate")

    def test_foreign_ca_client_refused(self):
        rogue = solution_mtls.make_pki_with_client(self.ns.work / "rogue", "rogue")
        with self.assertRaises(OSError):
            kms.KMSClient(self.ns.port, rogue, ca_file=self.ns.pki / "ca.pem").call("rotate")

    def test_caller_identity_logged(self):
        wraps = [e for e in self.ns.audit.entries if e["op"] == "kms.wrap"]
        self.assertEqual(wraps[0]["actor"], "doc-service/alice")  # CN from the client cert / user on whose behalf


if __name__ == "__main__":
    unittest.main()
