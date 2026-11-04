"""Milestone 5: spans for every step (lesson 13) and fallbacks (lesson 14); no model -> policy still decides."""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from capstone_fixture import Env, INCIDENTS  # noqa: E402


class M5Observability(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.close()

    def test_spans_and_fallback(self):
        agent = self.env.agent(endpoints=[("http://127.0.0.1:9/v1", "fake-model"), (self.env.model_url, "fake-small")])
        status, done = agent.handle(INCIDENTS["INC-2"])
        events = [e["event"] for e in agent.client.events]
        agent.close()
        spans = [json.loads(x)["name"] for x in (Path(self.env.tmp.name) / "trace.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertIn("fallback", events)
        self.assertEqual(done["decide"]["model_severity"], "SEV1")  # the fallback model answered
        for name in ("execute_tool get_metrics", "retrieve runbooks", "chat proposal", "effect page_oncall",
                     "invoke_agent incident-triage"):
            self.assertIn(name, spans)

    def test_no_model_at_all(self):
        agent = self.env.agent(endpoints=[("http://127.0.0.1:9/v1", "fake-model")])
        status, done = agent.handle(INCIDENTS["INC-7"])
        agent.close()
        self.assertEqual((done["propose"]["proposal"], done["decide"]["severity"], done["decide"]["actions"]),
                         (None, "SEV2", ["page_oncall"]))


if __name__ == "__main__":
    unittest.main()
