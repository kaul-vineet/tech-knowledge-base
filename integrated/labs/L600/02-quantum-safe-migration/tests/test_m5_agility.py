import unittest

import _lab
import crypto_registry as registry


class TestM5Agility(unittest.TestCase):
    def test_hybrid_and_mldsa_when_all_servers_v2(self):
        stats = _lab.phase_stats("migrated", [2, 2, 2], required=True)
        self.assertEqual((stats["sessions"], stats["delivered"], stats["refused"]), ({"X25519MLKEM768": 6}, 6, 0))
        hello = next(f for f in stats["tap"].flights if f["t"] == "server_hello")
        self.assertEqual((hello["group"], hello["sig"], hello["blob_bytes"]), ("X25519MLKEM768", "ML-DSA-65", [1120, 3309]))

    def test_flag_off_means_classical_only(self):
        registry.reset()
        registry.FLAGS.set("pq_hybrid_kex.messaging", False)
        try:
            self.assertEqual(registry.expected_offers("messaging"), ["X25519"])
        finally:
            registry.reset()
        self.assertEqual(registry.expected_offers("messaging"), ["X25519MLKEM768", "X25519"])

    def test_tampered_transcript_signature_fails(self):
        sig = registry.SIG["ML-DSA-65"]
        sk, pk = sig.keygen()
        s = sig.sign(sk, b"transcript")
        self.assertTrue(sig.verify(pk, s, b"transcript"))
        self.assertFalse(sig.verify(pk, s, b"transcripT"))


if __name__ == "__main__":
    unittest.main()
