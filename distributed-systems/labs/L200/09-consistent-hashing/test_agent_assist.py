import unittest

import agent_assist as aa
from local_agent import fake_model_server  # importable after agent_assist added labs/_shared


class TestAgentAssist(unittest.TestCase):
    def test_fake_agent_layout_is_rejected_for_the_right_reasons(self):
        srv, url = fake_model_server.start_in_thread()
        try:
            layout = aa.parse(aa.ask_agent(base_url=url))
        finally:
            srv.shutdown()
        self.assertEqual(sorted(layout), list(range(8)))
        self.assertEqual(aa.check(layout), ["S5: zones ['a', 'a', 'c'] -> two replicas share a zone",
                                            "n1: 5 replicas > capacity 4"])

    def test_checker_accepts_a_valid_layout_and_flags_missing_and_unknown(self):
        good = {i: [f"n{1 + i % 2}", f"n{3 + (i + 1) % 2}", f"n{5 + i % 2}"] for i in range(8)}
        self.assertEqual(aa.check(good), [])
        bad = dict(good)
        del bad[7]
        bad[0] = ["n1", "n3", "n9"]
        self.assertEqual(aa.check(bad), ["S7: missing", "S0: unknown node(s) ['n9']"])

    def test_main_runs_with_fake_server(self):
        self.assertEqual(aa.main(["--fake"]), 0)


if __name__ == "__main__":
    unittest.main()
