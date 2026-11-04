"""Seam cost/time budget: costs are computed by code and reserved BEFORE runs; the agent loop is call-capped."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _fixture  # noqa: E402
import unittest  # noqa: E402

import agent  # noqa: E402
import fake_sim_agent  # noqa: E402
import pipeline  # noqa: E402
import registry  # noqa: E402

A, B = _fixture.A, _fixture.B


class TestBudgetSeam(unittest.TestCase):
    def test_over_budget_screening_is_rejected_before_running(self):
        pl = pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(300_000))
        res = pl.submit("run_screening", {"method": "sobol", "size": 1024})
        self.assertEqual(res["status"], "rejected")
        self.assertIn("6,144,000", res["errors"][0])
        self.assertEqual((pl.budget.spent, pl.registry.records), (0, []))

    def test_extension_stops_at_the_budget_and_says_so(self):
        pl = pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(60_000), half_width=0.3)
        res = pl.submit("run_experiment", {"baseline": A, "candidate": B, "replications": 3, "seed": 13})
        self.assertTrue(res["budget_limited"])
        self.assertEqual(res["replications"], 10)
        self.assertLessEqual(pl.budget.spent, 60_000)

    def test_agent_loop_is_capped_by_model_calls(self):
        server, url = fake_sim_agent.start_in_thread()
        try:
            brief = "seed 1. " + " ".join(["Screen with sobol 4096."] * 12)  # a runaway plan: 12 tool calls
            out = agent.run_session(brief, pipeline.Pipeline(registry.Registry(), pipeline.SimBudget(1000)), url,
                                    "fake-model", max_calls=4)
        finally:
            server.shutdown()
            server.server_close()
        self.assertTrue(out["stopped"].startswith("agent budget"))
        self.assertEqual(out["calls"], 4)


if __name__ == "__main__":
    unittest.main()
