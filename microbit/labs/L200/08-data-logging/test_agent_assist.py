import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent_assist as aa  # noqa: E402
import export_csv  # noqa: E402
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
        header, rows, _ = export_csv.extract(aa.scenario_csv())
        return aa.stats(header, rows), header

    def test_code_computes_stats(self):
        facts, _ = self.facts()
        self.assertEqual((facts["n"], facts["duration_s"]), (6, 5.0))
        self.assertEqual(facts["cols"]["temp"]["mean"], 22.5)
        self.assertAlmostEqual(facts["cols"]["light"]["mean"], 89.833, places=3)
        self.assertEqual(facts["cols"]["light"]["trend"], "down")

    def test_fake_agent_passes_check(self):
        out = aa.run(aa.scenario_csv(), base_url=self.url, model="fake-model")
        self.assertEqual(out[0], "code stats (authoritative): 6 rows over 5 s; "
                         "temp 21..24 mean 22.5 (up); light 41..120 mean 89.8 (down)")
        self.assertTrue(out[1].startswith("agent explanation (checked):"), out)

    def test_wrong_number_and_wrong_trend_are_rejected(self):
        facts, header = self.facts()
        bad = "Temperature rose to 25 with a mean of 22.5. Light rose from 120 to 41."
        self.assertEqual(aa.check_explanation(bad, facts, header), [
            "numbers not in the CSV or its stats: ['25']", "says light rose, but it went down"])
        self.assertEqual(aa.check_explanation("Light mean 89.8, temp mean 22.5 over 5 s.", facts, header), [])

    def test_server_down_falls_back_to_code(self):
        out = aa.run(aa.scenario_csv(), base_url="http://127.0.0.1:9/v1", model="m")
        self.assertEqual(out[-1], "agent: unavailable (URLError) -> code summary only")

    def test_cli_fake(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            aa.main(["--fake"])
        self.assertIn("check: PASS", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
