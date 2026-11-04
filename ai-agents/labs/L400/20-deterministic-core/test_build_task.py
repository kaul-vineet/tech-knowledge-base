"""Build task (lesson 20): explanations that contradict the decision are replaced by the template.
Default target = solution/explain_check.py. Test YOUR explain_check.py (shipped unfixed: shows any text):
  BUILD_TARGET=mine python -m unittest -v test_build_task
  PowerShell: $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task"""
import importlib.util
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import edge  # noqa: E402
import fake_server_l400  # noqa: E402

TARGET = HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"
spec = importlib.util.spec_from_file_location("target_explain_check", TARGET / "explain_check.py")
ec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ec)


class BuildTask(unittest.TestCase):
    def test_explanations_match_decisions(self):
        server, url = fake_server_l400.start_in_thread()
        original, edge.explain_check = edge.explain_check, ec
        try:
            rows = {r["id"]: r for r in edge.evaluate("code_decides", url, "fake-model")}
        finally:
            edge.explain_check = original
            server.shutdown()
            server.server_close()
        print("\nc04:", rows["c04"]["explanation"], "| c11:", rows["c11"]["explanation"])
        self.assertEqual(rows["c04"]["explanation"], "Decision: deny for 0.0. Reason: R3 outside the 30-day window.")
        self.assertEqual(rows["c08"]["explanation"], "Decision: escalate for 0.0. Reason: R6 over 50.00 needs a person.")
        self.assertEqual(rows["c11"]["explanation"], "Good news: your refund of 20 is approved.")  # consistent: kept
        self.assertEqual(rows["c01"]["explanation"], "Decision: approve_auto for 30.0. Reason: R5 up to 50.00 within policy.")

    def test_invented_amount(self):
        d = {"action": "approve_auto", "amount": 30.0, "rule": "R5 up to 50.00 within policy"}
        self.assertEqual(ec.checked("Approved: we refund 300 today.", d), ec.template(d))


if __name__ == "__main__":
    unittest.main()
