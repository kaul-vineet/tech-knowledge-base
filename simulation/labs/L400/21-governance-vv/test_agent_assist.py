import unittest

import agent_assist as aa
import fake_model_server  # importable because agent_assist put labs/_shared/local_agent on sys.path

EV = {"verification": {"tests_run": 7, "failures": 0}, "envelope_rho_max": 0.85, "max_rel_error_in_envelope": 0.055,
      "most_influential": "mu", "sensitivity": {"lam": 6.01, "mu": -7.02},
      "validation": [{"rho": 0.85, "rel_error": 0.031, "ok": True}, {"rho": 0.95, "rel_error": 0.013, "ok": False}]}


class TestClaimChecks(unittest.TestCase):
    def test_honest_text_passes(self):
        text = "Valid for utilisation up to 0.85. Mean wait within 6% of Erlang C. Most sensitive to the service rate. 7 of 7 tests pass."
        self.assertTrue(all(ok for _, _, ok in aa.check_claims(text.lower(), EV)))

    def test_overclaims_are_caught(self):
        text = "utilisation up to 0.95, within 1% of Erlang C, most sensitive to the arrival rate, 6 of 7 tests pass."
        self.assertEqual([ok for _, _, ok in aa.check_claims(text, EV)], [False, False, False, False])


class TestEndToEndWithFakeServer(unittest.TestCase):
    def test_fake_draft_is_rejected_by_code(self):
        aa.use_fake_rule(fake_model_server)
        server, url = fake_model_server.start_in_thread()
        try:
            r = aa.assist(EV, base_url=url, model="fake-model")
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual([(kind, ok) for kind, _, ok in r["claims"]],
                         [("envelope", False), ("accuracy", False), ("key input", True), ("verification", True)])
        self.assertEqual(r["unverified"], ["3", "2.0"])


if __name__ == "__main__":
    unittest.main()
