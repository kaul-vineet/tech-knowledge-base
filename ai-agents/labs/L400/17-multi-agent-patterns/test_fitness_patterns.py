"""Fitness function (lesson 17, ADR-0017): keeps 'one agent by default, escalate only on context' true.

Thresholds: hybrid passes 10/10; on every task the estimate keeps on one agent it spends EXACTLY the single agent's
tokens (no hidden extra hops); no task needs more than 8 model calls. Any new agent layer must keep this green.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import fake_server_l400  # noqa: E402
import patterns  # noqa: E402


class FitnessTopology(unittest.TestCase):
    def test_one_agent_default_holds(self):
        server, url = fake_server_l400.start_in_thread(context_limit=patterns.CONTEXT_LIMIT)
        try:
            hybrid = {r["task"]: r for r in patterns.evaluate("hybrid", url, "fake-model")}
            single = {r["task"]: r for r in patterns.evaluate("single", url, "fake-model")}
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(sum(r["pass"] for r in hybrid.values()), 10)
        for tid, task, _ in patterns.ow.TASKS:
            if patterns.estimate(task) <= 0.9 * patterns.CONTEXT_LIMIT:
                self.assertEqual(hybrid[tid]["tokens"], single[tid]["tokens"], tid)
            self.assertLessEqual(hybrid[tid]["model_calls"], 8, tid)


if __name__ == "__main__":
    unittest.main()
