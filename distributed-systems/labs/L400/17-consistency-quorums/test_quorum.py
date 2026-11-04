"""Lesson tests for lab 17: python -m unittest -v"""
import importlib.util, unittest
from pathlib import Path

import quorum as q
from helpers import anomalies

CHECKER = Path(__file__).resolve().parents[2] / "L300" / "13-partitions-fault-injection" / "checker.py"
spec = importlib.util.spec_from_file_location("l300_checker", CHECKER)
l300 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(l300)


class Quorums(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(q.run(2, 2), q.run(2, 2))

    def test_eventual_settings_read_stale(self):
        m = q.measure(1, 1)
        self.assertFalse(m["overlap"])
        self.assertGreater(m["stale_pct"], 10.0)
        self.assertGreater(m["ryw"], 0)

    def test_failure_lab_overlap_is_not_linearizable(self):
        m = q.measure(2, 2)  # R + W > N: no stale read of a FINISHED write ...
        self.assertEqual((m["stale_pct"], m["ryw"]), (0.0, 0))
        self.assertEqual(m["inversions"], 2)  # ... but new-then-old between reads: not linearizable
        self.assertFalse(m["linearizable"])

    def test_fast_check_agrees_with_exhaustive_l300_checker(self):
        verdicts = []
        for r, w in ((1, 1), (2, 2), (1, 3)):
            for seed in range(1, 101):
                hist = q.run(r, w, seed, run_ms=10)
                a = anomalies(hist)
                verdicts.append(((a["stale"] == 0 and a["inversions"] == 0), l300.check_register(hist)[0]))
        self.assertTrue(all(fast == exact for fast, exact in verdicts))
        self.assertEqual(sum(not exact for _, exact in verdicts), 89)  # both checkers reject the same 89 histories

    def test_pacelc_partition_costs_availability(self):
        avail = {(m["R"], m["W"]): m["avail_c_down_pct"] for m in (q.measure(r, w) for r, w in ((1, 1), (2, 2), (1, 3), (3, 1)))}
        self.assertEqual(avail, {(1, 1): 100.0, (2, 2): 100.0, (1, 3): 0.0, (3, 1): 0.0})

    def test_decisions_in_the_lesson_file(self):
        rows = [q.measure(r, w, wb) for r, w, wb in q.SETTINGS]
        picks = {name: (lambda b: b and (b["R"], b["W"], b["write_back"]))(q.decide(rows, need))
                 for name, need in q.USE_CASES.items()}
        self.assertEqual(list(picks.values()), [(1, 1, False), (2, 2, False), None])


if __name__ == "__main__":
    unittest.main()
