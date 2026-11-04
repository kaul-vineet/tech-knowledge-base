import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent_assist as aa  # noqa: E402
from local_agent import fake_model_server  # noqa: E402  (path set by agent_assist)


class AgentAssist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = fake_model_server.start_in_thread()  # fake only: no real model in tests

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_code_decides_alarms(self):
        lines = aa.scenario_telemetry()
        self.assertEqual(lines[2], "temp=27,light=110,state=hot")
        facts = aa.decide(aa.parse(lines))
        self.assertEqual([(i, s) for i, s, _, _ in facts["alarms"]], [(3, "hot"), (4, "dark")])
        self.assertEqual(facts["mismatches"], [])

    def test_fake_agent_explanation_passes_check(self):
        out = aa.run(aa.scenario_telemetry(), base_url=self.url, model="fake-model")
        self.assertTrue(out[0].startswith("code decision (authoritative): 5 readings"))
        self.assertTrue(out[1].startswith("agent explanation (checked):"), out)
        self.assertEqual(out[2], "check: PASS (numbers all from telemetry; alarm states named)")

    def test_check_rejects_invented_number_and_missed_alarm(self):
        facts = aa.decide(aa.parse(aa.scenario_telemetry()))
        bad = "Average temperature was 24.8 C and everything looked fine."
        problems = aa.check_explanation(bad, facts)
        self.assertEqual(aa.check_explanation("Light uses a 0-255 scale; it hit 35, so dark; 27 C was hot.", facts), [])
        self.assertIn("numbers not in telemetry: ['24.8']", problems)
        self.assertIn("does not mention 'hot' (1 reading(s))", problems)
        self.assertIn("does not mention 'dark' (1 reading(s))", problems)

    def test_logged_state_mismatch_is_flagged(self):
        lines = ["temp=27,light=110,state=ok"]  # e.g. logged by a variant with HOT_C = 28
        out = aa.run(lines, base_url=self.url, model="fake-model")
        self.assertIn("warning: logged state differs from classify() at reading(s) [1]", out)

    def test_server_down_falls_back_to_code(self):
        out = aa.run(["temp=21,light=128,state=ok"], base_url="http://127.0.0.1:9/v1", model="m")
        self.assertEqual(out[-1], "agent: unavailable (URLError) -> code summary only")

    def test_cli_fake(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            aa.main(["--fake"])
        self.assertIn("check: PASS", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
