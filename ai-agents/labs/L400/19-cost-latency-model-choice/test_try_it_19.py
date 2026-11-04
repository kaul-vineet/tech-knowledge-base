"""Try it (lesson 19): a bigger context with parallel slots; drop "urgent" and "down" from the routing rule."""
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import cost_model as cm  # noqa: E402
import fake_server_l400  # noqa: E402
import route_cost as rc  # noqa: E402


class TryIt(unittest.TestCase):
    def test_1_ctx_32k_parallel_4(self):
        rows = {(m, model): (need, where) for m, model, need, _, where, _ in cm.sizing_rows(ctx=32768, parallel=4)}
        got = rows[("Mac mini M6 24GB", "qwen2.5:14b")], rows[("Mac mini M5 Pro 48GB", "qwen2.5:14b")]
        print(f"\nobserved: 14b at 32k x 4 needs {got[0][0]} GB -> M6 24GB: {got[0][1]}; M5 Pro 48GB: {got[1][1]}")
        self.assertEqual((got[0][1], got[1][1]), ("does not fit", "GPU (Metal)"))

    def test_2_rule_without_urgent(self):
        old = rc.HARD
        rc.HARD = re.compile(r"\b(asap|immediately)\b", re.I)
        server, url = fake_server_l400.start_in_thread()
        try:
            s = rc.summary(rc.run("rules+cascade", base_url=url))
            failed = [r["id"] for r in rc.run("rules+cascade", base_url=url) if not r["pass"]]
        finally:
            rc.HARD = old
            server.shutdown()
            server.server_close()
        print(f"\nobserved: {s['passed']}/20, cost {s['cost']}, failed {failed}")
        self.assertEqual((s["passed"], failed), (19, ["t03"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
