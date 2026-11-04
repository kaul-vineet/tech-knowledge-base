"""Build task (lesson 18): an approval deadline. Default target = solution/approval_policy.py.
Test YOUR approval_policy.py (shipped unfixed: waits forever, accepts late clicks):
  BUILD_TARGET=mine python -m unittest -v test_build_task
  PowerShell: $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task"""
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent), str(HERE.parent.parent / "L300" / "15-safe-tool-execution")]
import durable  # noqa: E402
import fake_server_l400  # noqa: E402
import payments_service  # noqa: E402

TARGET = HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"
spec = importlib.util.spec_from_file_location("target_policy", TARGET / "approval_policy.py")
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class BuildTask(unittest.TestCase):
    def test_deadline_escalates_and_ignores_late_approval(self):
        server, url = fake_server_l400.start_in_thread()
        pay, pay_url = payments_service.start_in_thread()
        clock = durable.Clock(0)
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            eng = durable.Engine(Path(d) / "wf.db", pay_url, url, "fake-model", clock=clock, policy=policy)
            eng.start("wf-1", "A-1001")
            seen = [eng.run("wf-1")]
            clock.hours = 47
            seen.append(eng.run("wf-1"))
            clock.hours = 49  # nobody answered within 48 h
            seen.append(eng.run("wf-1"))
            clock.hours = 50
            eng.signal("wf-1", "approve", "late-larry")
            seen.append(eng.run("wf-1"))
            outbox = [k for (k,) in eng.db.execute("SELECT kind FROM outbox")]
            eng.db.close()
        refunds = len(requests.get(f"{pay_url}/refunds", timeout=5).json())
        for s in (server, pay):
            s.shutdown()
            s.server_close()
        self.assertEqual((seen, refunds, outbox), (["waiting", "waiting", "escalated", "escalated"], 0, ["approval_timeout"]))


if __name__ == "__main__":
    unittest.main()
