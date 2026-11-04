"""python -m unittest -v : lesson 13 proxy, checker and the reproducible split brain."""
import json
import unittest

import partition as pt
from checker import check_register, stale_reads
from helpers import jsonl


def op(p, f, v, s, e, ok=True):
    return {"process": p, "node": "n", "f": f, "value": v, "start": s, "end": e, "ok": ok}


class Checker(unittest.TestCase):
    def test_concurrent_write_may_be_seen_or_not(self):
        h = [op("a", "write", 1, 0, 10), op("b", "read", 1, 2, 3), op("c", "read", 0, 4, 5)]
        self.assertFalse(check_register(h)[0])  # once a read saw 1, a LATER read cannot see 0 again
        h[2] = op("c", "read", 0, 1, 1.5)  # overlaps the first read: 0 then 1 is fine
        self.assertTrue(check_register(h)[0])

    def test_porcupine_readme_histories(self):  # the two register examples from the Porcupine README
        ok = [op("c0", "write", 100, 0, 10), op("c1", "read", 100, 1, 8), op("c2", "read", 0, 2, 5)]
        bad = [op("c0", "write", 200, 0, 10), op("c1", "read", 200, 1, 2), op("c2", "read", 0, 3, 4)]
        self.assertTrue(check_register(ok)[0])
        self.assertFalse(check_register(bad)[0])

    def test_failed_ops_are_ignored_and_stale_read_explained(self):
        h = [op("a", "write", 1, 0, 1), op("b", "write", 2, 2, 3, ok=False), op("c", "read", 2, 4, 5)]
        self.assertFalse(check_register(h)[0])
        self.assertEqual(stale_reads(h)[0][1]["value"], 1)


class ProxyAndScenario(unittest.TestCase):
    def test_down_link_times_out_and_latency_is_reported(self):
        p = pt.Proxy()
        p.add("a", "b", latency=0.3)
        self.assertEqual(p.call("a", "b", lambda: "hi"), ("hi", 0.3))
        p.partition({"a"}, {"b"})
        with self.assertRaises(pt.Timeout):
            p.call("b", "a", lambda: "hi")

    def test_happy_path_one_leader_linearizable(self):
        _, history, leaders = pt.run(pt.OPS, {})
        self.assertTrue(all(l == ["n1"] for l in leaders))
        self.assertTrue(check_register(history)[0])

    def test_partition_gives_two_leaders_and_a_non_linearizable_history(self):
        events, history, leaders = pt.run(pt.OPS, pt.FAULTS)
        self.assertEqual([t for t, l in enumerate(leaders) if l == ["n1", "n2"]], [4, 5, 6, 7, 8])
        self.assertFalse(check_register(history)[0])
        self.assertTrue(all(op["ok"] for op in history))  # the stale writer was accepted
        self.assertEqual(json.loads(jsonl(history)[0])["type"], "invoke")


if __name__ == "__main__":
    unittest.main()
