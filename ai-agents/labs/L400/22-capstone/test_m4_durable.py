"""Milestone 4 (fitness: exactly-once): approvals, crash-resume, idempotent effects (lessons 15 + 18)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import workflow  # noqa: E402
from capstone_fixture import Env, INCIDENTS  # noqa: E402


class M4Durable(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.close()

    def test_crash_after_page_resumes_without_a_second_page(self):
        agent = self.env.agent(crash_at={"after_effect:INC-4:page_oncall"})
        self.assertEqual(agent.handle(INCIDENTS["INC-4"])[0], "waiting")  # rollback needs a person
        agent.wf.signal("INC-4", "approve", "lead")
        with self.assertRaises(workflow.Crash):
            agent.handle(INCIDENTS["INC-4"])
        agent.close()
        agent = self.env.agent()  # restart: same SQLite file
        status, done = agent.handle(INCIDENTS["INC-4"])
        agent.close()
        self.assertEqual((status, done["effects"]), ("done", [["page_oncall", True], ["rollback_deploy", False]]))
        self.assertEqual([e["action"] for e in self.env.effects_list()], ["page_oncall", "rollback_deploy"])

    def test_rollback_expires_without_an_answer(self):
        agent = self.env.agent()
        self.assertEqual(agent.handle(INCIDENTS["INC-8"])[0], "waiting")
        self.env.clock.hours = 5  # nobody answered within 4 h
        status, done = agent.handle(INCIDENTS["INC-8"])
        agent.close()
        self.assertEqual((status, done["approval"]["state"]), ("done", "timed_out"))
        self.assertEqual([e["action"] for e in self.env.effects_list()], ["page_oncall", "open_incident_doc"])


if __name__ == "__main__":
    unittest.main()
