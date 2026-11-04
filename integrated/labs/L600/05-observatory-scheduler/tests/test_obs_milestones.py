"""One test class per milestone (M1-M5); the same checks run_project.py prints."""
import unittest

from tests import _lab

import agent_plan  # noqa: E402
import sky  # noqa: E402
import validator  # noqa: E402
import weather  # noqa: E402
import _kb  # noqa: E402


class M1SkyAndTime(unittest.TestCase):
    def test_dark_window_and_first_slot_in_utc(self):
        r = _lab.night()
        self.assertEqual(len(r["slots"]), 64)
        self.assertEqual(r["slots"][0].utc.iso(), "2026-11-19T13:20:00Z")
        self.assertEqual(f"{r['slots'][0].local:%H:%M}-{r['slots'][-1].local:%H:%M}", "18:50-05:20")

    def test_infeasible_requests_are_known_for_a_reason(self):
        r = _lab.night()
        dead = {q.name for q, row in zip(r["reqs"], r["ok"]) if not row.any()}
        self.assertEqual(dead, {"Fomalhaut", "Polaris", "Canopus", "Arcturus"})
        fom = next(q for q in r["reqs"] if q.name == "Fomalhaut")  # bright enough, but the Moon is too close
        self.assertLess(max(sky.moon_sep_deg(fom, s.utc) for s in r["slots"][:10]), sky.MIN_MOON_SEP_DEG)


class M2Greedy(unittest.TestCase):
    def test_greedy_plan_validates(self):
        r = _lab.night()
        self.assertEqual([x["target"] for x in r["greedy_rows"]], ["Deneb", "Aldebaran", "Capella", "Betelgeuse"])
        self.assertEqual(validator.validate(validator.rows_from_blocks(r["greedy"], r["reqs"], r["slots"])), [])
        self.assertAlmostEqual(r["greedy_value"], 8.209, places=3)


class M3LocalSearch(unittest.TestCase):
    def test_local_search_validates_and_beats_greedy(self):
        r = _lab.night()
        self.assertEqual(validator.validate(validator.rows_from_blocks(r["local"], r["reqs"], r["slots"])), [])
        self.assertGreaterEqual(r["local_value"], r["greedy_value"])
        self.assertAlmostEqual(r["local_value"], 10.534, places=3)


class M4MonteCarlo(unittest.TestCase):
    def test_simulated_mean_matches_the_analytic_promise(self):
        r = _lab.night()
        clear = weather.clear_matrix(1000, len(r["slots"]), 7)
        for key in ("greedy", "local"):
            m, h = weather.summary(weather.realised([(s, n, r["reqs"][i].priority) for s, n, i in r[key]], clear))
            self.assertLessEqual(abs(m - r[key + "_value"]), h, key)


class M5Agent(unittest.TestCase):
    def test_fake_agent_plan_rejected_and_explanation_gated(self):
        r = _lab.night()
        server, url = _kb.fake_model_server.start_in_thread()
        try:
            text = agent_plan.ask(agent_plan.plan_prompt(r["reqs"], r["slots"]), url)
            facts = agent_plan.explain_facts(r)
            explanation = agent_plan.ask(agent_plan.explain_prompt(facts), url)
        finally:
            server.shutdown()
            server.server_close()
        verdict = agent_plan.decide(text, r["local"], r["reqs"], r["slots"])
        self.assertEqual(verdict["adopted"], "optimiser")
        self.assertEqual(len(verdict["reasons"]), 4)
        self.assertTrue(agent_plan.checked_explanation(explanation, facts, r["reqs"])[0])


if __name__ == "__main__":
    unittest.main()
