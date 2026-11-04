"""Lesson tests for lab 21 (linearizability checking): python -m unittest -v"""
import importlib.util, unittest
from pathlib import Path

import lincheck as lc

spec = importlib.util.spec_from_file_location("l300_checker", Path(__file__).resolve().parents[2] / "L300" /
                                              "13-partitions-fault-injection" / "checker.py")
l300 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(l300)


def op(c, f, v, s, e):
    return {"process": c, "f": f, "value": v, "start": s, "end": e, "ok": True}


class LinCheck(unittest.TestCase):
    def test_porcupine_readme_histories(self):
        self.assertTrue(lc.check([op("C0", "write", 100, 0, 10), op("C1", "read", 100, 1, 8), op("C2", "read", 0, 2, 5)])[0])
        self.assertFalse(lc.check([op("C0", "write", 200, 0, 10), op("C1", "read", 200, 1, 3), op("C2", "read", 0, 4, 6)])[0])

    def test_agrees_with_the_exhaustive_l300_checker(self):
        quorum = lc.load_lab17("quorum")
        verdicts = [(lc.check(h)[0], l300.check_register(h)[0])
                    for r, w in ((1, 1), (2, 2), (1, 3)) for h in (quorum.run(r, w, s, run_ms=10) for s in range(1, 101))]
        self.assertTrue(all(a == b for a, b in verdicts))
        self.assertEqual(sum(not a for a, _ in verdicts), 89)

    def test_finds_the_quorum_inversion_in_a_long_history(self):
        ok, stats = lc.check(lc.load_lab17("quorum").run(2, 2))
        self.assertFalse(ok)
        b = stats["blocker"]
        self.assertEqual((b["process"], b["value"], round(b["start"], 1)), ("r6", 28, 1738.9))
        self.assertTrue(lc.check(lc.load_lab17("solution_quorum").run(2, 2, write_back=True))[0])


if __name__ == "__main__":
    unittest.main()
