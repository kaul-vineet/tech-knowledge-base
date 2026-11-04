import contextlib
import io
import unittest

import agent_assist
import capacity
import fitness_capacity
import l300_log
from agent_assist import check_memo, draft, facts

import sys
from app import HERE
sys.path.insert(0, str(HERE.parents[1] / "_shared"))
from local_agent import fake_model_server  # noqa: E402

MODEL = capacity.load_model(l300_log.records())
FACTS = facts()


class ModelTest(unittest.TestCase):
    def test_load_model_from_the_l300_log(self):
        self.assertEqual((MODEL["avg_rps"], MODEL["peak_rps"], MODEL["mean_service_ms"]), (40.0, 120.0, 45.2))
        self.assertEqual(MODEL["mix"], {"GET /books": 0.449, "GET /loans": 0.351, "POST /loans": 0.2})

    def test_littles_law(self):
        self.assertAlmostEqual(capacity.littles_law(120, 45.2), 5.424)
        sim = capacity.simulate(40, [ms for _, ms in MODEL["requests"]])
        self.assertAlmostEqual(sim["in_flight"], 40 * sim["p50_ms"] / 1000, delta=0.3)  # L = lambda x W (mean W)

    def test_benchmark_capacity_per_instance(self):
        self.assertEqual(capacity.benchmark(MODEL)["capacity_rps"], 75)
        self.assertEqual(capacity.benchmark(capacity.with_sync_email(MODEL))["capacity_rps"], 35)

    def test_cache_hit_ratio_is_measured(self):
        self.assertEqual(capacity.lru_hit_ratio(), 0.65)

    def test_symptom_average_sizing_collapses_at_peak(self):
        n = capacity.instances_needed(MODEL, 75)
        self.assertEqual(n, 1)
        self.assertGreater(capacity.simulate(MODEL["peak_rps"] / n, [ms for _, ms in MODEL["requests"]])["p99_ms"], 10000)
        self.assertFalse(fitness_capacity.gate(capacity)["ok"])


class AgentMemoTest(unittest.TestCase):
    def test_wrong_peak_is_rejected(self):
        problems = check_memo("plan for a peak of 40.0 req/s with 3 instances", FACTS)
        self.assertIn("peak_rps is 120.0, the memo says 40.0", problems)

    def test_fake_model_loop(self):
        server, url = fake_model_server.start_in_thread()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        reply, problems, log = draft(url, "fake-model", FACTS)
        self.assertEqual((problems, log[1]), ([], "attempt 2: OK"))
        self.assertIn("the plan is 3 instances, the memo says 1", log[0])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(agent_assist.main([]), 0)


if __name__ == "__main__":
    unittest.main()
