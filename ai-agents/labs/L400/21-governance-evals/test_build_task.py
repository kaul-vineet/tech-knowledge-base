"""Build task (lesson 21): retention deletes old prompt text but keeps the audit chain verifiable.
Default target = solution/retention.py. Test YOUR retention.py (shipped unfixed: deletes audit rows):
  BUILD_TARGET=mine python -m unittest -v test_build_task
  PowerShell: $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task"""
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import governance as g  # noqa: E402

TARGET = HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"
spec = importlib.util.spec_from_file_location("target_retention", TARGET / "retention.py")
retention = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retention)


class BuildTask(unittest.TestCase):
    def test_purge_content_keep_chain(self):
        with tempfile.TemporaryDirectory(dir=HERE) as d:
            log = g.AuditLog(Path(d) / "audit.db")
            for day in range(60):
                log.append(day, "agent", "triage", f"ticket text of customer {day} (personal data)")
            log.append(60, "agent", "triage", "ticket text of customer 0 (personal data)")  # same text, recent
            removed = retention.purge(log.db, today=61, keep_days=30)
            rows = log.db.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
            old = log.db.execute("SELECT COUNT(*) FROM content WHERE day < 31").fetchone()[0]
            verified = log.verify()
            log.db.close()
        print(f"\nremoved {removed}, audit rows {rows}, old content left {old}, verify {verified}")
        self.assertEqual((rows, verified), (61, (True, None)))
        self.assertEqual(old, 1)  # only day 0's text survives: a recent row (day 60) still points at it


if __name__ == "__main__":
    unittest.main()
