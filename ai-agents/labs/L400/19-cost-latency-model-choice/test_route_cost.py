"""Lesson 19: routing, caching, batching and sizing numbers + the failure lab (python -m unittest -v test_route_cost)."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import cost_model as cm  # noqa: E402
import fake_server_l400  # noqa: E402
import route_cost as rc  # noqa: E402


def measure(strategy, prompt=rc.PROMPT):
    server, url = fake_server_l400.start_in_thread()
    try:
        return rc.run(strategy, base_url=url, prompt=prompt)
    finally:
        server.shutdown()
        server.server_close()


class RouteCost(unittest.TestCase):
    def test_strategies(self):
        got = {n: rc.summary(measure(n)) for n in rc.STRATEGIES}
        self.assertEqual({n: (s["passed"], s["cost"], s["escalated"]) for n, s in got.items()},
                         {"large-only": (20, 7000.0, 0), "small-only": (13, 1590.0, 0), "cascade": (19, 3807.6, 6),
                          "rules+cascade": (20, 3890.1, 4)})

    def test_failure_lab_small_only_and_the_silent_miss(self):
        failed = [r["id"] for r in measure("small-only") if not r["pass"]]
        self.assertEqual(failed, ["t03", "t04", "t05", "t10", "t14", "t18", "t19"])
        cascade = {r["id"]: r for r in measure("cascade")}
        self.assertEqual((cascade["t03"]["pass"], cascade["t03"]["models"]), (False, ["fake-small"]))  # valid JSON, wrong priority
        fixed = {r["id"]: r for r in measure("rules+cascade")}
        self.assertEqual((fixed["t03"]["pass"], fixed["t03"]["models"]), (True, ["fake-large"]))

    def test_prompt_order_and_cache(self):
        first = rc.summary(measure("large-only"))
        last = rc.summary(measure("large-only", prompt=rc.TICKET_FIRST))
        self.assertEqual((first["cache_ratio"], last["cache_ratio"]), (0.76, 0.03))
        self.assertLess(first["cost"], last["cost"])

    def test_batching_and_sizing(self):
        b = rc.batching(measure("large-only"))
        self.assertEqual([(x["parallel"], x["kv_gb"]) for x in b], [(1, 0.23), (4, 0.94)])
        self.assertAlmostEqual(cm.kv_gb("qwen2.5:7b", 1) * 1e6, 57.344)  # 2 x 28 x 4 x 128 x 2 bytes
        rows = {(m, model): where for m, model, _, _, where, _ in cm.sizing_rows()}
        self.assertEqual(rows[("Windows NVIDIA 8GB VRAM", "qwen2.5:14b")], "partial GPU + CPU")
        self.assertEqual(rows[("Mac mini M6 16GB", "qwen2.5:14b")], "GPU (Metal)")

    def test_cli(self):
        server, url = fake_server_l400.start_in_thread()
        try:
            out = subprocess.run([sys.executable, "route_cost.py"], cwd=HERE, capture_output=True, text=True, encoding="utf-8",
                                 env={**os.environ, "LOCAL_MODEL_URL": url}, timeout=120).stdout
        finally:
            server.shutdown()
            server.server_close()
        self.assertIn('"strategy": "rules+cascade", "passed": 20', out)
        self.assertIn("prompt order ticket first      : cached 3% of prompt tokens", out)


if __name__ == "__main__":
    unittest.main()
