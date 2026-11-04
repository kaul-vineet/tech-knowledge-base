"""Seam S4 (astronomy <-> cryptography): Gaia's CC BY-NC 3.0 IGO terms and the credit lines must survive processing,
signing and replication - the licence gate runs before signing; licence + attribution are covered by the signature."""
import json
import unittest

from _world import world

import checks
import publisher as P
from _kb import INPUTS


class SeamLicence(unittest.TestCase):
    def test_seam(self):
        ok, d = checks.s4_licence(world())
        self.assertTrue(ok, d)
        self.assertEqual(d["licence"], "CC-BY-NC-4.0")

    def test_signed_manifest_binds_licence_and_attribution(self):
        w = world()
        m = json.loads(w.mirrors[0].objects["releases/v4/release.json"])["signed"]
        ack = w.mirrors[0].objects["releases/v4/ACKNOWLEDGEMENTS.md"]
        self.assertEqual(m["licence"], "CC-BY-NC-4.0")
        self.assertEqual(m["attribution_sha256"], P.sha(ack))
        for i in INPUTS.INPUTS:
            self.assertIn(i["credit"], ack.decode("utf-8"))  # verbatim, as astronomy L400 #21 requires

    def test_gate_refuses_a_licence_that_drops_nc(self):
        ok, d = checks.s4_licence(world("licence-drop"))
        self.assertFalse(ok)
        self.assertIn("drops the NC condition of input gaia_dr3_astrometry", d["gate"])


if __name__ == "__main__":
    unittest.main()
