import unittest

import agent_assist as aa
import fake_model_server  # importable because agent_assist put labs/_shared/local_agent on sys.path


class TestChecks(unittest.TestCase):
    def test_bad_proposals_are_rejected(self):
        for bad in ({"class": "black hole", "period_days": 1.0}, {"class": "transit", "period_days": "3"},
                    {"class": "transit", "period_days": 1e6}, {"class": "transit", "period_days": True}):
            with self.assertRaises(ValueError):
                aa.validate(bad)

    def test_alias_is_named(self):
        self.assertEqual(aa.judge_period(1.31, 0.5669), "overruled: 1-day alias of the code's period")
        self.assertEqual(aa.judge_period(0.567, 0.5669), "agrees")
        self.assertEqual(aa.judge_period(3.0, 0.5669), "overruled")

    def test_decision_rule(self):
        self.assertEqual(aa.decide({"power": 0.77, "skew": 0.0}), "pulsating variable")
        self.assertEqual(aa.decide({"power": 0.03, "skew": 0.8}), "transit")
        self.assertEqual(aa.decide({"power": 0.03, "skew": 0.0}), "unknown")


class TestEndToEndWithFakeServer(unittest.TestCase):
    def test_agent_alias_overruled_and_invented_number_flagged(self):
        server, url = fake_model_server.start_in_thread()
        try:
            r = aa.assist(base_url=url, model="fake-model")
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(r["code"], ("pulsating variable", "0.5669"))
        self.assertTrue(r["verdict"].endswith("1-day alias of the code's period"))
        self.assertEqual(r["unverified"], ["0.001"])


if __name__ == "__main__":
    unittest.main()
