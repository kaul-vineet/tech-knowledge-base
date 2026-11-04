"""Agent assist (lesson 18) against the deterministic fake model only."""
import sys
import unittest
from pathlib import Path

import agent_assist

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_agent"))
import fake_model_server  # noqa: E402


class TestAgentAssist(unittest.TestCase):
    def test_gate(self):
        f = {"candid": 7, "objectId": "AKB1", "class": "transient", "flux": 120.5, "sigmaflux": 20.0, "magpsf": 19.8,
             "rb": 0.9, "fwhm": 4.1, "n_prv": 2}
        self.assertEqual(agent_assist.check("A transient at magnitude 19.8, seen 2 times before.", f), (True, []))
        self.assertEqual(agent_assist.check("A new transient - actually a variable star.", f), (False, []))
        self.assertEqual(agent_assist.check("A transient that rose by 3 magnitudes.", f), (True, ["3"]))

    def test_fake_model_explanations_are_blocked(self):
        server, url = fake_model_server.start_in_thread()
        try:
            rows = [agent_assist.explain(p, base_url=url) for p in agent_assist.demo_alerts()]
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual([(r["code_class"], r["class_ok"], r["unverified"], r["publish"]) for r in rows],
                         [("known_variable", False, ["2.5"], False), ("moving", True, ["2.5"], False),
                          ("transient", True, ["2.5"], False)])


if __name__ == "__main__":
    unittest.main()
