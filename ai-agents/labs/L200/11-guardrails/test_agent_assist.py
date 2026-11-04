import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import agent_assist  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402


class AgentAssist(unittest.TestCase):
    def test_policy_wins_over_model(self):
        server, url = start_in_thread()
        try:
            proposed = agent_assist.propose_labels(base_url=url, model="fake-model")
        finally:
            server.shutdown()
        final, disagreements = agent_assist.review(proposed)
        self.assertEqual(final["archive_notes"], "high")
        self.assertEqual(disagreements, ["archive_notes: model said 'low', policy says 'high'"])

    def test_unknown_tool_fails_safe(self):
        agent_assist.TOOLS["wipe_disk"] = "Remove everything."
        try:
            final, _ = agent_assist.review({})
        finally:
            del agent_assist.TOOLS["wipe_disk"]
        self.assertEqual(final["wipe_disk"], "high")


if __name__ == "__main__":
    unittest.main()
