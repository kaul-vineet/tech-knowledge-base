"""M2: content-addressed release and the RFC 9162 Merkle tree (definitions + iterative verifiers)."""
import hashlib
import unittest

from _world import world

import checks
import merkle


def D(n):
    return [f"d{i}".encode() for i in range(n)]


class M2Release(unittest.TestCase):
    def test_milestone(self):
        ok, d = checks.m2_release(world())
        self.assertTrue(ok, d)
        self.assertEqual(d["licence"], "CC-BY-NC-4.0")

    def test_empty_tree_is_hash_of_empty_string(self):
        self.assertEqual(merkle.mth([]), hashlib.sha256(b"").digest())  # RFC 9162 2.1.1

    def test_rfc9162_example_proof_shapes(self):
        L = D(7)  # 2.1.5: d0 -> [b, h, l]; d6 -> [i, k]; PROOF(3) = [c, d, g, l]; PROOF(4) = [l]; PROOF(6) = [i, j, k]
        b, h, l_ = merkle.leaf_hash(L[1]), merkle.mth(L[2:4]), merkle.mth(L[4:7])
        self.assertEqual(merkle.inclusion_proof(0, L), [b, h, l_])
        self.assertEqual(merkle.inclusion_proof(6, L), [merkle.mth(L[4:6]), merkle.mth(L[0:4])])
        self.assertEqual(merkle.consistency_proof(3, L),
                         [merkle.leaf_hash(L[2]), merkle.leaf_hash(L[3]), merkle.mth(L[0:2]), l_])
        self.assertEqual(merkle.consistency_proof(4, L), [l_])
        self.assertEqual(merkle.consistency_proof(6, L), [merkle.mth(L[4:6]), merkle.leaf_hash(L[6]), merkle.mth(L[0:4])])

    def test_every_inclusion_and_consistency_proof_verifies(self):
        for n in range(1, 34):
            L, root = D(n), merkle.mth(D(n))
            for m in range(n):
                p = merkle.inclusion_proof(m, L)
                self.assertTrue(merkle.verify_inclusion(L[m], m, n, p, root))
                self.assertFalse(merkle.verify_inclusion(L[m] + b"!", m, n, p, root))
                if m:
                    c = merkle.consistency_proof(m, L)
                    self.assertTrue(merkle.verify_consistency(m, n, merkle.mth(L[:m]), root, c))
                    forked = L[:m - 1] + [b"rewritten"]
                    self.assertFalse(merkle.verify_consistency(m, n, merkle.mth(forked), root, c))

    def test_domain_separation(self):
        L = D(2)  # a node must never be confused with a leaf whose data is two concatenated hashes
        fake = merkle.leaf_hash(L[0]) + merkle.leaf_hash(L[1])
        self.assertNotEqual(merkle.mth(L), merkle.leaf_hash(fake))


if __name__ == "__main__":
    unittest.main()
