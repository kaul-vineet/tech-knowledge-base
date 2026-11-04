import unittest

import agent_assist as aa
import fake_model_server  # importable because agent_assist put labs/_shared/local_agent on sys.path


class TestChecks(unittest.TestCase):
    def test_unknown_names_are_reported_not_used(self):
        known, unknown = aa.validate({"visible": ["Vega", "Planet X", 7]})
        self.assertEqual(known, ["Vega"])
        self.assertEqual(unknown, ["Planet X", 7])

    def test_reply_without_list_is_rejected(self):
        with self.assertRaises(ValueError):
            aa.validate({"visible": "Vega"})

    def test_numbers_must_come_from_the_table(self):
        rows = [("Deneb", 56.271, 310.07, True), ("Canopus", -33.229, 136.6, False)]
        ok, bad = aa.check_numbers("Deneb is at 56.27 deg, Canopus at -33.23; it rises at 22:40.", rows)
        self.assertEqual(ok, ["56.27", "-33.23"])
        self.assertEqual(bad, ["22", "40"])


class TestEndToEndWithFakeServer(unittest.TestCase):
    def test_agent_proposes_code_decides(self):
        server, url = fake_model_server.start_in_thread()
        try:
            r = aa.assist(base_url=url, model="fake-model")
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(r["wrong"], ["Canopus", "Sirius"])  # the agent's guess is overruled by computed altitudes
        self.assertIn("Deneb", r["up"])
        self.assertEqual(r["unverified"], ["22", "40"])


if __name__ == "__main__":
    unittest.main()
