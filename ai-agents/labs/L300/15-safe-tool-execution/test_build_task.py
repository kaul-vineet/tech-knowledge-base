"""Build task (lesson 15): crash between 'sent' and 'done' -> restart -> resume() refunds exactly once.
Default target = solution/resumable_gate.py. Test YOUR resumable_gate.py (shipped unfixed, so it fails first):
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
sys.path[:0] = [str(HERE), str(HERE.parent)]
import payments_service  # noqa: E402

TARGET = HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"
spec = importlib.util.spec_from_file_location("target_resumable_gate", TARGET / "resumable_gate.py")
rg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rg)


class BuildTask(unittest.TestCase):
    def test_resume_after_crash(self):
        pay, url = payments_service.start_in_thread()
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            db = Path(d) / "approvals.db"
            gate = rg.ResumableGate(db, url)
            gate.request("send_refund", {"order_id": "A-7", "amount": 12.5}, "run-9", "call_1")
            gate.decide(1, "alice", approve=True)
            real_send = gate._send

            def crash_after_send(args, key):
                real_send(args, key)  # the refund happened...
                raise SystemExit("process killed before status 'done' was written")
            gate._send = crash_after_send
            with self.assertRaises(SystemExit):
                gate.execute_approved()
            gate.db.close()
            restarted = rg.ResumableGate(db, url)  # new process, same SQLite file
            result = restarted.resume()
            status = restarted.db.execute("SELECT status FROM approvals WHERE id = 1").fetchone()[0]
            restarted.db.close()
        refunds = requests.get(f"{url}/refunds", timeout=5).json()
        pay.shutdown()
        pay.server_close()
        self.assertEqual((len(refunds), result[0]["replayed"], status), (1, True, "done"))


if __name__ == "__main__":
    unittest.main()
