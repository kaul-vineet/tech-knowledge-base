"""Lesson 14 tests: retry only 5xx/timeouts, budgets, fallback, cache, and the failureLab (naive vs hardened)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import compare  # noqa: E402
import resilient_agent as ra  # noqa: E402
from fake_server_l300 import start_in_thread  # noqa: E402


class Resilience(unittest.TestCase):
    def serve(self, **faults):
        server, url = start_in_thread(**faults)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server, url

    def test_retries_5xx_then_succeeds(self):
        server, url = self.serve(fail_rate=0.5, seed=1)  # seed 1: first draw fails, second passes
        client = ra.Client([(url, "fake-model")], seed=7)
        self.assertEqual(ra.answer("What is 12*7?", client), "Final answer: 12*7 = 84")
        self.assertIn("retry", [e["event"] for e in client.events])
        self.assertGreaterEqual(server.stats["503"], 1)

    def test_4xx_is_not_retried(self):
        server, url = self.serve()
        client = ra.Client([(url, "fake-model")])
        bad = [{"role": "tool", "tool_call_id": "nope", "content": "x"}]  # fake answers 400 (no user message)
        with self.assertRaises(ra.requests.HTTPError):
            client.chat(bad, ra.Budget())
        self.assertEqual(server.stats["requests"], 1)

    def test_timeout_falls_back_to_second_endpoint(self):
        _, slow = self.serve(slow_rate=1.0, slow_s=1.0)
        _, healthy = self.serve()
        client = ra.Client([(slow, "fake-model"), (healthy, "fake-small")], timeout=0.2, retries=1)
        self.assertEqual(ra.answer("What is 6*6?", client), "Final answer: 6*6 = 36")
        self.assertEqual([e["error"] for e in client.events if e["event"] in ("retry", "give_up")][:2], ["timeout", "timeout"])

    def test_budget_stops_runaway_loop_and_cache_hits(self):
        _, url = self.serve()
        client = ra.Client([(url, "fake-model")])
        many = "Add up 1+1, 2+2, 3+3, 4+4, 5+5, 6+6, 7+7 and 8+8."
        self.assertEqual(ra.answer(many, client, max_steps=20), ra.CANNED)  # needs 9 calls, budget is 8
        self.assertEqual(client.events[-1], {"event": "canned", "reason": "calls 8 >= 8"})
        budget = ra.Budget()
        ra.answer("What is 7*8?", client)
        self.assertEqual(ra.answer("What is 7*8?", client, budget=budget), "Final answer: 7*8 = 56")
        self.assertEqual((budget.calls, budget.tokens), (0, 0))  # served from the response cache

    def test_cost_budget(self):
        b = ra.Budget(max_cost=0.0001)
        with self.assertRaises(ra.BudgetExceeded):
            b.add("fake-model", {"total_tokens": 100})  # 100 tokens * $0.002/1k = $0.0002


class FailureLab(unittest.TestCase):
    def test_naive_hangs_and_overspends_hardened_stays_bounded(self):
        naive, hard = compare.run("naive"), compare.run("hardened")
        print(f"\nnaive: max {naive['max_s']} s, tokens {naive['tokens']} | hardened: max {hard['max_s']} s, "
              f"tokens {hard['tokens']}, canned {hard['canned']}")
        self.assertGreater(naive["max_s"], 4.0)  # one question waited through two 2 s stalls + retries
        self.assertGreater(naive["tokens"], 250)  # no budget: the 9-call question ran to the end
        self.assertLess(hard["max_s"], 3.0)
        self.assertLess(hard["tokens"], 150)
        self.assertEqual([r["q"] for r in hard["rows"] if r["canned"]], ["Add up 1+1, 2+2, 3+3, "])


if __name__ == "__main__":
    unittest.main()
