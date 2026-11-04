"""Lab tests: STRIDE-per-element candidates, boundaries, test references, attack tree, Mermaid output."""
import unittest

import threat_model as tm


class TestThreatModel(unittest.TestCase):
    def setUp(self):
        self.m = tm.load()

    def test_candidates_follow_the_table(self):
        types = [e["type"] for e in self.m["elements"].values()]
        self.assertEqual(len(tm.candidates(self.m)), sum(len(tm.APPLIES[t]) for t in types))

    def test_boundary_crossing(self):
        els = self.m["elements"]
        self.assertTrue(tm.crosses_boundary(self.m, els["client->doc-api"]))
        self.assertFalse(tm.crosses_boundary(self.m, els["doc-api->app-log"]))

    def test_test_references_resolve(self):
        self.assertTrue(all(tm.test_exists(r) for c in self.m["controls"].values() for r in c["tests"]))
        self.assertFalse(tm.test_exists("labs/L300/12-envelope-rotation/test_build_task.py::TestRetireAfterRewrap::nope"))
        self.assertFalse(tm.test_exists("labs/nowhere/test_x.py::A::b"))

    def test_attack_tree_cheapest_path(self):
        self.assertEqual(tm.cheapest(self.m["attack_tree"], set(self.m["controls"])), (9, ["phish an authorised user"]))
        cost, path = tm.cheapest(self.m["attack_tree"], set())  # no controls at all
        self.assertEqual((cost, path), (3, ["stay in the project room after removal"]))

    def test_mermaid_lists_every_flow(self):
        text = tm.mermaid(self.m)
        self.assertEqual(text.count("-->|"), sum(e["type"] == "flow" for e in self.m["elements"].values()))


if __name__ == "__main__":
    unittest.main()
