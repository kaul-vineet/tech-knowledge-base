import random
import unittest

import modularity as m


class GraphTheoryTest(unittest.TestCase):
    def test_cycle_detected_and_collapsed(self):
        nodes, edges = ["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")]
        self.assertFalse(m.is_acyclic(nodes, edges))
        self.assertEqual([frozenset(nodes)], m.tarjan_scc(nodes, edges))
        with self.assertRaises(ValueError):
            m.longest_path_layering(nodes, edges)

    def test_longest_path_layering_is_strict(self):
        nodes, edges = ["ui", "svc", "repo", "db"], [("ui", "svc"), ("svc", "repo"), ("repo", "db"), ("ui", "db")]
        level = m.longest_path_layering(nodes, edges)
        self.assertEqual({"ui": 3, "svc": 2, "repo": 1, "db": 0}, level)
        self.assertEqual([], m.strict_layering_violations(edges, level))

    def test_strict_random_graphs_are_acyclic(self):
        rng = random.Random(1)
        for _ in range(200):
            nodes, edges, level = m.random_graph(rng, 8, 0.4, strict=True)
            self.assertTrue(m.is_acyclic(nodes, edges))
            self.assertEqual([], m.strict_layering_violations(edges, level))


class LibraryLoansTest(unittest.TestCase):
    def test_hexagonal_metrics(self):
        rows = m.martin_metrics(*m.module_graph(m.HEXAGONAL))
        self.assertEqual((1, 0, 0.0, 1.0, 0.0), tuple(rows["ports"][k] for k in ("Ca", "Ce", "I", "A", "Dn")))
        self.assertEqual((5, 1), (rows["domain"]["Ca"], rows["domain"]["Ce"]))
        self.assertAlmostEqual(5 / 6, rows["domain"]["Dn"])

    def test_main_block_creates_the_only_cycle(self):
        nodes, edges, _ = m.module_graph(m.HEXAGONAL, include_main=True)
        self.assertEqual([["app", "driving_cli"]], [sorted(c) for c in m.tarjan_scc(nodes, edges) if len(c) > 1])
        self.assertTrue(m.is_acyclic(*m.module_graph(m.HEXAGONAL)[:2]))

    def test_kwic_information_hiding(self):
        self.assertEqual(14, sum(len(v) for v in m.change_impact(m.KWIC_CONVENTIONAL).values()))
        self.assertEqual(5, sum(len(v) for v in m.change_impact(m.KWIC_HIDING).values()))


if __name__ == "__main__":
    unittest.main()
