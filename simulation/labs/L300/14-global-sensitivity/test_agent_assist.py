import unittest

import agent_assist as aa
import fake_model_server  # importable because agent_assist put labs/_shared/local_agent on sys.path
import sensitivity as sa


class TestRankingValidation(unittest.TestCase):
    def test_only_a_full_permutation_is_accepted(self):
        good = '{"ranking": ["window_open", "outdoor_C", "lights_h", "occupants"]}'
        self.assertEqual(len(aa.validate_ranking(good)["ranking"]), 4)
        for bad in ('{"ranking": ["outdoor_C", "occupants"]}', '{"ranking": ["outdoor_C", "outdoor_C", "x", "y"]}',
                    "no json here", '{"order": []}'):
            with self.assertRaises(ValueError):
                aa.validate_ranking(bad)

    def test_disagreements_are_listed_by_position(self):
        rows = sa.table()
        decided, wrong = aa.check_ranking(["outdoor_C", "occupants", "window_open", "lights_h"], rows)
        self.assertEqual(decided[1], "window_open")
        self.assertEqual(len(wrong), 2)


class TestEndToEndWithFakeServer(unittest.TestCase):
    def test_agent_ranks_by_oat_and_code_overrules(self):
        server, url = fake_model_server.start_in_thread()
        try:
            r = aa.assist(base_url=url, model="fake-model")
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(r["proposal"]["ranking"][-1], "window_open")  # the fake agent trusts the OAT column
        self.assertEqual(r["decided"], ["outdoor_C", "window_open", "occupants", "lights_h"])
        self.assertEqual(len(r["wrong"]), 3)
        self.assertEqual(r["unverified"], ["30"])


if __name__ == "__main__":
    unittest.main()
