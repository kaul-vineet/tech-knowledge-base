"""Lab tests: tree relations, epochs in sync, O(log n) commits, messages bound to an epoch."""
import unittest

import group_keys as gk
import tree_math as tm

NAMES = ["alice", "bob", "carol", "dave", "erin", "frank", "grace", "heidi"]


class TestTreeMath(unittest.TestCase):
    def test_paths_in_a_tree_of_eight(self):
        self.assertEqual(tm.direct_path(tm.leaf(8, 3)), [5, 2, 1])
        self.assertEqual(tm.copath(tm.leaf(8, 3)), [10, 4, 3])

    def test_resolution_skips_blanks(self):
        nodes = {x: object() for x in range(1, 16)}
        nodes[5] = nodes[11] = None  # blank parent of leaves 2,3 and blank leaf 3
        self.assertEqual(tm.resolution(nodes, 5, 8), [10])
        self.assertEqual(tm.resolution(nodes, 2, 8), [2])


class TestGroupKeys(unittest.TestCase):
    def test_update_keeps_everyone_in_sync(self):
        g = gk.Group(NAMES)
        sent = g.commit("carol")
        self.assertEqual(sent, 3)  # log2(8) HPKE encryptions for a full tree
        self.assertEqual(len({(m.epoch, m.epoch_secret) for m in g.members.values()}), 1)

    def test_message_needs_current_epoch(self):
        g = gk.Group(NAMES)
        old = g.send("alice", "epoch 0 message")
        self.assertEqual(g.read("heidi", old), "epoch 0 message")
        g.commit("bob")
        self.assertIsNone(g.read("heidi", old))  # keys of past epochs are gone (forward secrecy within the toy)

    def test_tampered_message_rejected(self):
        g = gk.Group(NAMES)
        msg = g.send("alice", "pay 10")
        msg["ct"] = msg["ct"][:-1] + bytes([msg["ct"][-1] ^ 1])  # the delivery service flips one bit
        self.assertIsNone(g.read("bob", msg))

    def test_commit_cost_grows_with_log_n(self):
        costs = [gk.Group([f"m{i}" for i in range(n)]).commit("m0") for n in (4, 16, 64)]
        self.assertEqual(costs, [2, 4, 6])


if __name__ == "__main__":
    unittest.main()
