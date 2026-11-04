"""Seam S2 (cryptography <-> distributed systems): mirrors keep old releases forever, so key rotation must keep
them verifiable without letting a retired key sign anything new."""
import unittest

from _world import world

import checks
import client as CL


class SeamRotation(unittest.TestCase):
    def test_seam(self):
        ok, d = checks.s2_rotation(world())
        self.assertTrue(ok, d)
        self.assertIn("no valid Ed25519 signature from a key trusted for v5", d["retired_key_signs_v5"])

    def test_naive_rotation_breaks_old_releases(self):
        w = world("drop-old-key")
        ok, d = checks.s2_rotation(w)
        self.assertFalse(ok)
        self.assertEqual(d["old_releases_verify"], [4])  # v1-v3 were signed by keys the new root forgot
        with self.assertRaises(CL.Rejected):
            CL.verify_release(w.mirrors[1].objects, 2, w.root)

    def test_window_is_inclusive_and_exact(self):
        w = world()
        retired = w.root["retired"]
        self.assertEqual({r["valid_through_version"] for r in retired.values()}, {3})
        self.assertEqual(len(retired), 2)  # the Ed25519 and the ML-DSA-65 key of generation 1


if __name__ == "__main__":
    unittest.main()
