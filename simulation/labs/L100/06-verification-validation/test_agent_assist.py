import unittest

import agent_assist as aa
import fake_model_server  # importable because agent_assist put labs/_shared/local_agent on sys.path
import vv


class TestPlanValidation(unittest.TestCase):
    def test_bad_values_are_rejected_not_run(self):
        values, customers, problems = aa.validate_plan(
            {"parameter": "lam", "values": [True, 0.5, 1.2, "0.7", 0.5, float("nan")], "seed": "any"})
        self.assertEqual(values, [0.5])
        self.assertEqual(customers, 20_000)
        self.assertEqual(len(problems), 6)  # ignored key, bool, 1.2, string, duplicate, NaN

    def test_only_lam_may_be_swept(self):
        with self.assertRaises(ValueError):
            aa.validate_plan({"parameter": "mu", "values": [0.5]})

    def test_customers_must_be_a_bounded_int(self):
        for bad in (10 ** 9, 500, True, 20000.0):
            with self.assertRaises(ValueError):
                aa.validate_plan({"parameter": "lam", "values": [0.5], "customers": bad})

    def test_too_many_values_are_capped(self):
        values, _, problems = aa.validate_plan({"parameter": "lam", "values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]})
        self.assertEqual(len(values), aa.MAX_VALUES)
        self.assertIn("kept the first 6 values", problems)

    def test_object_extracted_from_fenced_prose(self):
        reply = 'Sure!\n```json\n{"parameter": "lam", "values": [0.5]}\n```\nDone.'
        self.assertEqual(aa.extract_object(reply), {"parameter": "lam", "values": [0.5]})


class TestNumberCheck(unittest.TestCase):
    ROWS = [("0.50", "1.014", "0.033", "1.000"), ("0.90", "9.141", "1.275", "9.000")]

    def test_table_numbers_pass_and_invented_ones_are_flagged(self):
        ok, bad = aa.check_numbers("At lam=0.90 the wait is 9.14 min (about 9 min); at 0.95 it is 19.0 min.",
                                   self.ROWS, 20_000)
        self.assertEqual(ok, ["0.90", "9.14", "9"])
        self.assertEqual(bad, ["0.95", "19.0"])


class TestEndToEndWithFakeServer(unittest.TestCase):
    def test_agent_proposes_code_decides_and_checks(self):
        server, url = fake_model_server.start_in_thread()
        try:
            r = aa.assist(base_url=url, model="fake-model")
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(r["proposal"]["values"], [0.5, 0.7, 0.9, 1.2])
        self.assertEqual(r["values"], [0.5, 0.7, 0.9])  # 1.2 never reached the simulator
        mean, _ = vv.replicate(0.9, reps=10, n=20_000)
        self.assertIn(f"0.90 | {mean:.3f}", r["table"])  # the table comes from code, not from the agent
        self.assertEqual(r["unverified"], ["0.95", "19.0"])
        self.assertEqual(len(r["verified"]), 6)


if __name__ == "__main__":
    unittest.main()
