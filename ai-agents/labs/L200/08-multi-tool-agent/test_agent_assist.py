import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "L100", "01-setup"))
import agent_assist  # noqa: E402
from fake_model_server import start_in_thread  # noqa: E402


class AgentAssist(unittest.TestCase):
    def test_draft_is_checked_by_code(self):
        server, url = start_in_thread()
        try:
            draft = agent_assist.draft_schema(base_url=url, model="fake-model")
        finally:
            server.shutdown()
        ok, notes = agent_assist.check(draft)
        self.assertTrue(ok)
        self.assertEqual(notes, ["added additionalProperties: false"])  # the draft forgot it; code fixed policy

    def test_weak_draft_is_rejected(self):
        ok, notes = agent_assist.check({"type": "object", "properties": {"value": {"type": "number"}}})
        self.assertFalse(ok)
        self.assertIn("rejected good example {'value': 21, 'to': 'fahrenheit'}", notes)  # 'to' was never declared


if __name__ == "__main__":
    unittest.main()
