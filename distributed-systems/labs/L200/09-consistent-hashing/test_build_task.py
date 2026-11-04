"""Build-task check: HashRing.nodes_for(key, n) returns n DISTINCT physical nodes, walking clockwise.
Default target = solution_ring.py. Test YOUR ring.py:  BUILD_TARGET=mine python -m unittest test_build_task -v
(PowerShell: $env:BUILD_TARGET="mine"; python -m unittest test_build_task -v)"""
import importlib.util, os, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILE = "ring.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution_ring.py"
spec = importlib.util.spec_from_file_location("target_ring", HERE / FILE)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
KEYS = [f"user:{i}" for i in range(2_000)]


class TestReplicaPlacement(unittest.TestCase):
    def setUp(self):
        self.ring = r.HashRing(list("ABCDE"))

    def test_n_distinct_nodes_and_the_first_is_the_owner(self):
        for k in KEYS:
            nodes = self.ring.nodes_for(k, 3)
            self.assertEqual(len(set(nodes)), 3)
            self.assertEqual(nodes[0], self.ring.node_for(k))

    def test_deterministic_and_too_many_replicas_is_an_error(self):
        self.assertEqual(self.ring.nodes_for("user:1"), r.HashRing(list("ABCDE")).nodes_for("user:1"))
        with self.assertRaises(ValueError):
            self.ring.nodes_for("user:1", 6)

    def test_removing_a_node_only_touches_replica_sets_that_contained_it(self):
        smaller = r.HashRing(list("ABCDE"))
        smaller.remove("C")
        for k in KEYS:
            if "C" not in self.ring.nodes_for(k):
                self.assertEqual(self.ring.nodes_for(k), smaller.nodes_for(k))


if __name__ == "__main__":
    unittest.main()
