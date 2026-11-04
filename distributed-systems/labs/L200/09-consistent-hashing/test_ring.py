import unittest

import ring as r

KEYS = [f"user:{i}" for i in range(10_000)]


class TestRing(unittest.TestCase):
    def test_hash_is_stable_across_processes(self):
        self.assertEqual(r.h("user:42"), int.from_bytes(__import__("hashlib").md5(b"user:42").digest()[:8], "big"))

    def test_adding_a_node_moves_about_one_fifth_with_the_ring_but_most_keys_with_modulo(self):
        four, five = r.HashRing(list("ABCD")), r.HashRing(list("ABCDE"))
        ring_moved = r.moved(four.node_for, five.node_for, KEYS)
        mod_moved = r.moved(lambda k: r.modulo_node(k, list("ABCD")), lambda k: r.modulo_node(k, list("ABCDE")), KEYS)
        self.assertLess(ring_moved, 0.25)
        self.assertGreater(mod_moved, 0.75)
        self.assertTrue(all(five.node_for(k) == "E" for k in KEYS if four.node_for(k) != five.node_for(k)))

    def test_removing_a_node_moves_only_its_keys(self):
        full, smaller = r.HashRing(list("ABCD")), r.HashRing(list("ABCD"))
        smaller.remove("D")
        self.assertTrue(all(full.node_for(k) == "D" for k in KEYS if full.node_for(k) != smaller.node_for(k)))
        self.assertNotIn("D", {smaller.node_for(k) for k in KEYS})

    def test_more_vnodes_means_more_even_load(self):
        from collections import Counter
        spread = [r.imbalance(Counter(ring.node_for(k) for k in KEYS))
                  for ring in (r.HashRing(list("ABCD"), 1), r.HashRing(list("ABCD"), 100))]
        self.assertGreater(spread[0], 1.5)
        self.assertLess(spread[1], 1.1)


if __name__ == "__main__":
    unittest.main()
