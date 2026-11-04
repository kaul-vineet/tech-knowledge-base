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

    def facts(self):
        metrics, readings = aa.gateway_run()
        alarms, pct, missing = aa.decide_alarms(metrics, readings)
        return metrics, alarms, pct, missing

    def test_code_decides_alarms(self):
        metrics, alarms, pct, missing = self.facts()
        self.assertEqual([a["name"] for a in alarms], ["LINK_NOISY", "SEQ_GAP"])
        self.assertEqual((pct, missing), (4.5, 9))

    def test_fake_agent_passes_check(self):
        out = aa.run(base_url=self.url, model="fake-model")
        self.assertEqual(out[1], "alarms (decided by code): LINK_NOISY=4.5, SEQ_GAP=9")
        self.assertTrue(out[2].startswith("agent explanation (checked):"), out)

    def test_invented_alarm_and_number_are_rejected(self):
        metrics, alarms, pct, missing = self.facts()
        bad = "190 frames arrived, 12 were damaged. TEMP_HIGH and LINK_NOISY are active."
        self.assertEqual(aa.check_explanation(bad, metrics, alarms, pct, missing), [
            "numbers not in the metrics: ['12']",
            "names alarms the code did not raise: ['TEMP_HIGH']",
            "does not mention raised alarms: ['SEQ_GAP']"])

    def test_server_down_alarms_still_stand(self):
        out = aa.run(base_url="http://127.0.0.1:9/v1", model="m")
        self.assertEqual(out[-1], "agent: unavailable (URLError) -> alarms above stand")

    def test_cli_fake(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            aa.main(["--fake"])
        self.assertIn("check: PASS", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
