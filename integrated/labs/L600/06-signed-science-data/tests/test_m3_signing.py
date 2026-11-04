"""M3: dual signatures (crypto L400 #17 registry), the RFC 8032 vector (L200 #7) and the root chain (TUF 5.3)."""
import json
import unittest

from _world import world

import canonical as C
import checks
import client as CL
import trust


class M3Signing(unittest.TestCase):
    def test_milestone(self):
        ok, d = checks.m3_signed(world())
        self.assertTrue(ok, d)
        self.assertEqual(d["sig_bytes"], [64, 3309])

    def test_stripped_pq_signature_is_rejected(self):
        w = world()
        env = json.loads(w.mirrors[0].objects["releases/v4/release.json"])
        env["signatures"] = [s for s in env["signatures"] if s["alg"] == "Ed25519"]  # signature stripping
        objs = dict(w.mirrors[0].objects, **{"releases/v4/release.json": C.dumps(env)})
        with self.assertRaises(CL.Rejected):
            CL.verify_release(objs, 4, w.root)

    def test_root_chain_rejects_skip_and_wrong_signer(self):
        w = world()
        r1 = w.pub.roots[0]["signed"]
        self.assertEqual(trust.next_root(r1, w.pub.roots[1])["version"], 2)
        skip = trust.sign(dict(w.pub.roots[1]["signed"], version=3), [w.pub.root_key])
        with self.assertRaises(trust.Rejected):
            trust.next_root(r1, skip)
        rogue = trust.sign(w.pub.roots[1]["signed"], [trust.Signer("Ed25519", "attacker")])
        with self.assertRaises(trust.Rejected):
            trust.next_root(r1, rogue)


if __name__ == "__main__":
    unittest.main()
