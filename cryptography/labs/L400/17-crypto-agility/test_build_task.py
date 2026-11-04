"""Build task check (failureLab proof). Default: tests solution_agile.py.
Test YOUR version (the shipped agile_envelope.py is the unfixed one):
  macOS    BUILD_TARGET=mine python -m unittest -v test_build_task
  Windows  $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task; Remove-Item Env:BUILD_TARGET
BUILD_IMPL=<module> picks any other module (same switch as L200/L300)."""
import importlib
import os
import random
import unittest

import agile_envelope as ae
import registry as reg

MODULE = "agile_envelope" if os.environ.get("BUILD_TARGET") == "mine" else os.environ.get("BUILD_IMPL", "solution_agile")
impl = importlib.import_module(MODULE)


class TestPolicyDecidesSignatures(unittest.TestCase):
    def setUp(self):
        self.saved = dict(reg.POLICY)
        self.ring = ae.Keyring()
        self.ring.add(reg.POLICY["aead_default"])
        self.signers = {a: reg.new_signer(a) for a in reg.PHASES["transition"]}
        self.pubs = {a: k.public_key() for a, k in self.signers.items()}

    def tearDown(self):
        reg.POLICY.clear()
        reg.POLICY.update(self.saved)

    def env(self, algs, text=b"invoice 1: amount=100"):
        return ae.seal(self.ring, self.ring.primary(), text, "doc-1", {a: self.signers[a] for a in algs}, sig_algs=algs)

    def test_stripped_envelope_rejected_in_transition(self):
        rng = random.Random(17)  # same seeded forgery as the lab
        forged = self.env(reg.PHASES["classic"], f"doc-1: amount={rng.randrange(1, 9)}".encode())
        self.assertFalse(impl.verify(forged, self.pubs))

    def test_dual_signed_envelope_accepted(self):
        self.assertTrue(impl.verify(self.env(reg.PHASES["transition"]), self.pubs))

    def test_pq_only_envelope_needs_pq_only_phase(self):
        pq_only = self.env(reg.PHASES["pq-only"])
        self.assertFalse(impl.verify(pq_only, self.pubs))  # transition: Ed25519 still required
        reg.POLICY["phase"] = "pq-only"
        self.assertTrue(impl.verify(pq_only, self.pubs))

    def test_tampered_signature_rejected(self):
        e = self.env(reg.PHASES["transition"])
        e["ct"] = ae.b64e(ae.b64d(e["ct"])[:-1] + b"\x00")
        self.assertFalse(impl.verify(e, self.pubs))


if __name__ == "__main__":
    unittest.main()
