import unittest

import agent_assist as aa
import fake_model_server  # importable because agent_assist put labs/_shared/local_agent on sys.path


class TestProposalValidation(unittest.TestCase):
    def test_only_known_candidates_are_accepted(self):
        self.assertEqual(aa.validate_proposal({"distribution": " LogNormal "}), "lognormal")
        for bad in ({"distribution": "weibull"}, {"distribution": 3}, {"dist": "normal"}, ["normal"]):
            with self.assertRaises(ValueError):
                aa.validate_proposal(bad)

    def test_object_extracted_from_fenced_prose(self):
        reply = 'Sure!\n```json\n{"distribution": "normal", "reason": "x"}\n```'
        self.assertEqual(aa.extract_object(reply)["distribution"], "normal")


class TestNumberCheck(unittest.TestCase):
    def test_table_numbers_pass_and_invented_ones_are_flagged(self):
        rows = [("lognormal", 0.0312), ("exponential", 0.2171)]
        ok, bad = aa.check_numbers("D = 0.031 vs 0.22; mean 4.75; accepted at 99% since D < 0.05", rows,
                                   {"mean": 4.75})
        self.assertEqual(ok, ["0.031", "0.22", "4.75"])
        self.assertEqual(bad, ["99", "0.05"])


class TestEndToEndWithFakeServer(unittest.TestCase):
    def test_agent_proposes_code_decides_and_checks(self):
        server, url = fake_model_server.start_in_thread()
        try:
            r = aa.assist(base_url=url, model="fake-model")
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(r["picked"], "exponential")  # the fake agent's plausible but wrong pick
        self.assertEqual(r["decided"], "lognormal")  # code's decision from the KS statistics
        self.assertEqual(r["rank"], 3)
        self.assertEqual(r["unverified"], ["0.05", "99"])
        self.assertEqual(len(r["verified"]), 2)


if __name__ == "__main__":
    unittest.main()
