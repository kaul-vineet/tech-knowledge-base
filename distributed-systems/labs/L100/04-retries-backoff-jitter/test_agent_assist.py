import math
import unittest

import agent_assist as aa
from local_agent import fake_model_server  # importable after agent_assist added labs/_shared


class TestAgentAssist(unittest.TestCase):
    def test_truth_matches_an_independent_computation(self):
        lines = aa.make_log()
        lat = sorted(float(l.rsplit("=", 1)[1]) for l in lines)
        truth = aa.true_stats(lines)
        self.assertEqual(truth["attempts"], len(lines))
        self.assertEqual(truth["errors"], sum("status=503" in l for l in lines))
        self.assertEqual(truth["p50_ms"], lat[math.ceil(0.5 * len(lat)) - 1])
        self.assertEqual(truth["p99_ms"], lat[math.ceil(0.99 * len(lat)) - 1])
        self.assertLess(truth["p99_ms"], lat[-1])  # p99 is not the max for >100 samples

    def test_fake_agent_numbers_are_checked(self):
        srv, url = fake_model_server.start_in_thread()
        try:
            reply = aa.ask_agent(aa.make_log(), base_url=url)
        finally:
            srv.shutdown()
        verdict = aa.check(reply, aa.true_stats(aa.make_log()))
        self.assertEqual({k: v for k, (_, v) in verdict.items()},
                         {"attempts": "ok", "errors": "ok", "p50_ms": "WRONG", "p99_ms": "WRONG"})

    def test_checker_flags_missing_and_accepts_correct(self):
        truth = {"attempts": 10, "errors": 2, "p50_ms": 40.0, "p99_ms": 90.0}
        good = "attempts=10\nerrors=2\np50_ms=40.4\np99_ms=89.5\nsummary: fine"
        self.assertTrue(all(v == "ok" for _, v in aa.check(good, truth).values()))
        partial = aa.check("attempts=10\nsummary: no numbers", truth)
        self.assertEqual(partial["errors"], (None, "MISSING"))
        self.assertEqual(partial["attempts"][1], "ok")

    def test_main_runs_with_fake_server(self):
        self.assertEqual(aa.main(["--fake"]), 0)


if __name__ == "__main__":
    unittest.main()
