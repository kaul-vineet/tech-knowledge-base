import unittest

import agent_assist as aa
import partition as pt
from local_agent import fake_model_server  # importable after agent_assist added labs/_shared


class TestAgentAssist(unittest.TestCase):
    def test_code_computes_the_truth(self):
        events, history, _ = pt.run(pt.OPS, pt.FAULTS)
        self.assertEqual(aa.facts(events, history), {"linearizable": "no", "stale_leader": "n1", "lost_write": "c1 write 3"})

    def test_fake_agent_claims_are_checked(self):
        events, history, _ = pt.run(pt.OPS, pt.FAULTS)
        srv, url = fake_model_server.start_in_thread()
        try:
            reply = aa.ask_agent(events, history, base_url=url)
        finally:
            srv.shutdown()
            srv.server_close()
        verdicts = {k: (claim, ok) for k, claim, _, ok in aa.check(reply, aa.facts(events, history))}
        self.assertEqual(verdicts, {"linearizable": ("no", True), "stale_leader": ("n2", False),
                                    "lost_write": ("c1 write 1", False)})

    def test_missing_claims_are_wrong(self):
        self.assertFalse(aa.check("summary: all good", {"linearizable": "no"})[0][3])

    def test_main_runs_with_fake_server(self):
        self.assertEqual(aa.main(["--fake"]), 0)


if __name__ == "__main__":
    unittest.main()
