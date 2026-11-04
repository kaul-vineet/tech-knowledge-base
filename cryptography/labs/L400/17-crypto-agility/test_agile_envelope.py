"""Lab tests: envelope format, registry policy, negotiation, legacy v1 and lazy migration."""
import unittest

from cryptography.exceptions import InvalidTag

import agile_envelope as ae
import registry as reg


class TestAgileEnvelope(unittest.TestCase):
    def setUp(self):
        self.saved = {k: dict(v.__dict__) for k, v in reg.REGISTRY.items()}, dict(reg.POLICY)
        self.ring = ae.Keyring()
        self.ring.add(reg.POLICY["aead_default"])
        self.signers = {a: reg.new_signer(a) for a in reg.signing_algorithms()}

    def tearDown(self):
        for k, d in self.saved[0].items():
            reg.REGISTRY[k].__dict__.update(d)
        reg.POLICY.clear()
        reg.POLICY.update(self.saved[1])

    def test_roundtrip_and_sizes(self):
        e = ae.seal(self.ring, self.ring.primary(), b"hello", "d1", self.signers)
        self.assertEqual(ae.open_(self.ring, e), b"hello")
        self.assertEqual(len(ae.b64d(e["ct"])), 5 + 16)
        self.assertEqual({s["alg"]: len(ae.b64d(s["sig"])) for s in e["sigs"]}, {"Ed25519": 64, "ML-DSA-65": 3309})

    def test_swap_default_without_flag_day(self):
        old = ae.seal(self.ring, self.ring.primary(), b"old", "d1", self.signers)
        reg.POLICY["aead_default"] = "C20P1305"
        self.ring.add("C20P1305")
        new = ae.seal(self.ring, self.ring.primary(), b"new", "d2", self.signers)
        self.assertEqual((old["h"]["aead"], new["h"]["aead"]), ("A256GCM", "C20P1305"))
        self.assertEqual([ae.open_(self.ring, x) for x in (old, new)], [b"old", b"new"])

    def test_header_is_authenticated(self):
        e = ae.seal(self.ring, self.ring.primary(), b"x", "d1", self.signers)
        e["h"]["ctx"] = "d2"
        with self.assertRaises(InvalidTag):
            ae.open_(self.ring, e)

    def test_key_bound_to_algorithm(self):
        e = ae.seal(self.ring, self.ring.primary(), b"x", "d1", self.signers)
        e["h"]["aead"] = "C20P1305"
        with self.assertRaises(ae.EnvelopeError):
            ae.open_(self.ring, e)

    def test_deprecated_reads_disallowed_refuses(self):
        e = ae.seal(self.ring, self.ring.primary(), b"x", "d1", self.signers)
        reg.REGISTRY["A256GCM"].status = "deprecated"
        self.assertEqual(ae.open_(self.ring, e), b"x")  # read old data
        with self.assertRaises(reg.DisallowedAlgorithm):
            ae.seal(self.ring, "dk-1", b"y", "d2", self.signers)  # but no new data
        reg.REGISTRY["A256GCM"].status = "disallowed"
        with self.assertRaises(reg.DisallowedAlgorithm):
            ae.open_(self.ring, e)

    def test_negotiation_never_falls_back(self):
        self.assertEqual(ae.negotiate(["C20P1305", "A256GCM"], ["A256GCM"]), "A256GCM")
        with self.assertRaises(ae.NoCommonAlgorithm):
            ae.negotiate(["A256GCM"], ["A128CBC"])

    def test_legacy_v1_and_lazy_migration(self):
        old = ae.legacy_v1(self.ring, "dk-1", b"legacy")
        new = ae.migrate(self.ring, old, self.signers)
        self.assertEqual((new["h"]["v"], ae.open_(self.ring, new)), (2, b"legacy"))
        self.assertIs(ae.migrate(self.ring, new, self.signers), new)  # already current: untouched

    def test_unknown_version_rejected(self):
        with self.assertRaises(ae.EnvelopeError):
            ae.open_(self.ring, {"h": {"v": 3, "kid": "dk-1", "n": ""}, "ct": "", "sigs": []})


if __name__ == "__main__":
    unittest.main()
