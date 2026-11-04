"""One test class per capstone milestone (M1-M6). python -m unittest test_capstone -v"""
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

import agent_explain
import centre
import demand_twin
import fake_model_server  # importable because agent_explain put labs/_shared/local_agent on sys.path
import governance_pack
import make_data
import pipeline
import runner

INP = pipeline.model_inputs(pipeline.history())
PATIENCE = 4.5  # the calibrated value (M3 re-derives it)


class M1InputModelling(unittest.TestCase):
    def test_lognormal_wins_by_ks_and_rates_are_close_to_the_hidden_truth(self):
        self.assertEqual(INP["service_dist"], "lognormal")
        self.assertLess(INP["ks_d"], 0.02)
        self.assertLess(max(abs(a - b) / b for a, b in zip(INP["rates"], make_data.TRUE_RATES)), 0.10)

    def test_history_is_reproducible(self):
        calls, _ = make_data.history_day(1)
        self.assertEqual(len(calls), 2763)
        self.assertEqual(calls[0], {"day": 1, "t_min": 0.263, "service_min": 3.932})


class M2DesCore(unittest.TestCase):
    def test_degenerate_case_matches_erlang_c(self):
        runs = [centre.simulate([2.0] * 100, [3] * 100, 1.0, None, 1e9, seed=s) for s in range(4)]
        sim = np.mean([h["sl"] for run in runs for h in run[1:]])
        exact = 1 - pipeline.mmc_queue.erlang_c(3, 2.0, 1.0)["P_wait"] * math.exp(-1.0)
        self.assertAlmostEqual(sim, exact, delta=0.01)

    def test_more_agents_never_hurt_with_common_random_numbers(self):
        a = centre.period(5.0, 20, 4.0, 0.8, 3.0, seed=3)
        b = centre.period(5.0, 21, 4.0, 0.8, 3.0, seed=3)
        self.assertGreaterEqual(b["sl"], a["sl"])
        self.assertLessEqual(b["abandon"], a["abandon"])

    def test_nobody_abandons_with_endless_patience(self):
        self.assertEqual(centre.period(5.0, 18, 4.0, 0.8, 1e9, seed=1)["abandon"], 0.0)


class M3CalibrationValidation(unittest.TestCase):
    def test_calibrated_patience_and_holdout_errors(self):
        patience, sse = pipeline.calibrate(INP)
        self.assertEqual(patience, PATIENCE)
        flat = [p for p, v in sse.items() if v <= 1.2 * min(sse.values())]
        self.assertIn(make_data.TRUE_PATIENCE, flat)  # the truth (3.0) is inside the plausible set
        val = pipeline.validate(INP, patience)
        self.assertLessEqual(val["sl_mae_pp"], 3)
        self.assertLessEqual(val["abandon_mae_pp"], 2)


class M4SensitivityOptimisation(unittest.TestCase):
    def test_peak_hour_plan_is_minimal_and_feasible(self):
        rate = INP["rates"][3]
        best = pipeline.plan_hour(rate, INP, PATIENCE)
        self.assertTrue(best["ok"])
        self.assertFalse(pipeline.hour_check(rate, best["agents"] - 1, INP, PATIENCE)["ok"])

    def test_service_level_is_insensitive_to_patience(self):
        elastic = pipeline.sensitivity(INP, PATIENCE, [25] * 12)
        self.assertLess(abs(elastic["patience"]), 0.1)
        self.assertLess(elastic["rate"], -0.3)


class M5ParallelAndTwin(unittest.TestCase):
    def test_resume_and_worker_count_do_not_change_results(self):
        tasks = [((r,), INP["rates"], [22] * 12, INP["mean_service"], INP["cv"], PATIENCE) for r in range(6)]
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.db", Path(tmp) / "b.db"
            runner.run(a, tasks, workers=2)
            with self.assertRaises(runner.Crash):
                runner.run(b, tasks, workers=1, crash_after=3)
            runner.run(b, tasks, workers=1)
            self.assertEqual(runner.checksum(a), runner.checksum(b))

    def test_twin_detects_the_surge_and_not_before(self):
        tw, alarms = demand_twin.replay(INP["rates"])
        self.assertEqual([a["t_min"] for a in alarms], [375])  # surge starts at 300 min (13:00)
        self.assertGreater(tw.m, 1.15)


class M6GovernanceAndAgent(unittest.TestCase):
    def test_card_matches_evidence(self):
        ev = {"inputs": INP, "validation": {"sl_mae_pp": 1.09, "abandon_mae_pp": 0.73}}
        self.assertEqual(governance_pack.check(governance_pack.load_card(), ev), [])

    def test_agent_explanation_with_an_invented_number_is_not_published(self):
        agent_explain.use_fake_rule(fake_model_server)
        server, url = fake_model_server.start_in_thread()
        try:
            facts = {"plan_agent_hours": 221, "erlang_c_agent_hours": 219, "peak_agents": 25, "peak_hour": "11:00",
                     "alarm_clock": "14:15", "extra_agent_hours": 14, "saving_percent": -0.9}
            r = agent_explain.explain(facts, base_url=url, model="fake-model")
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(r["unverified"], ["9"])
        self.assertFalse(r["publish"])


class Scorecard(unittest.TestCase):
    def test_scorecard_lines_are_json(self):
        path = Path(__file__).with_name("scorecard.jsonl")
        if not path.exists():
            self.skipTest("run python run_capstone.py first")
        lines = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(lines[-1]["total"], 6)


if __name__ == "__main__":
    unittest.main()
