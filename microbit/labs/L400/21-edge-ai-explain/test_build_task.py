"""Build task check (lab 21): the model explains; it cannot change an alarm.

Runs solution.py. Check YOUR file: BUILD_TARGET=mine python -m unittest test_build_task
(= incident_assistant.py, which FAILS as shipped; or BUILD_FILE=<file>). Windows PowerShell:
$env:BUILD_TARGET="mine"; py -m unittest test_build_task
"""
import importlib.util
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import solution  # noqa: E402,F401
import fuzz  # noqa: E402
import incident  # noqa: E402
from alarms import decide  # noqa: E402
from local_agent import fake_model_server  # noqa: E402
from local_agent.client import chat  # noqa: E402

TARGET = os.environ.get("BUILD_FILE") or ("incident_assistant.py" if os.environ.get("BUILD_TARGET") == "mine"
                                          else "solution.py")
spec = importlib.util.spec_from_file_location("target_" + TARGET[:-3], HERE / TARGET)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SNAP = incident.snapshot()


class Boundary(unittest.TestCase):
    def test_injected_label_cannot_clear_an_alarm(self):
        server, url = fake_model_server.start_in_thread()
        try:
            out = mod.run(lambda m: chat(m, base_url=url, model="fake-model", timeout=60), SNAP)
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(out["alarms"], decide(SNAP))
        self.assertNotIn("cleared", out["note"])

    def test_no_adversarial_reply_changes_the_alarms(self):
        code = decide(SNAP)
        for kind, text in fuzz.replies(code):
            with self.subTest(kind=kind):
                self.assertEqual(mod.run(lambda m: text, SNAP)["alarms"], code)

    def test_model_down_still_shows_the_alarms(self):
        def down(messages):
            raise ConnectionRefusedError()
        out = mod.run(down, SNAP)
        self.assertEqual(out["alarms"], decide(SNAP))
        self.assertIn("TEMP_HIGH at n4", out["note"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
