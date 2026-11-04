"""Seam S3 agility layer <-> wire format. Guards the failure lab:
    python -m unittest test_seam_wire_contract              -> OK (migrated channel)
    INJECT=bypass python -m unittest test_seam_wire_contract -> FAIL (fast path skips the registry)"""
import unittest

import _lab
import seams


class TestSeamWireContract(unittest.TestCase):
    def test_rollout_offers_and_sizes_match_registry(self):
        stats = _lab.phase_stats(_lab.INJECT or "migrated", [2, 2, 1], required=False)
        self.assertTrue(stats["s3"]["ok"], stats["s3"])

    def test_every_handshake_was_resolved_by_the_registry(self):
        stats = _lab.phase_stats(_lab.INJECT or "migrated", [2, 2, 1], required=False)
        self.assertGreaterEqual(stats["f3"]["client_kex_resolutions"], stats["f3"]["handshakes"], stats["f3"])

    def test_adapters_put_what_they_advertise_on_the_wire(self):
        sizes = seams.measured_sizes()
        self.assertEqual(sizes["X25519MLKEM768"], {"client_share": 1216, "server_share": 1120})
        self.assertEqual(sizes["ML-DSA-65"], {"public_key": 1952, "signature": 3309})


if __name__ == "__main__":
    unittest.main()
