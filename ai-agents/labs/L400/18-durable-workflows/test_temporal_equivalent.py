"""pending-ci: the Temporal version gives the same outcome (1 refund after an activity retry). Skips unless
RUN_TEMPORAL=1 and temporalio is installed (CI job 'temporal' installs temporalio==1.34.0)."""
import asyncio
import os
import sys
import unittest
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent), str(HERE.parent.parent / "L300" / "15-safe-tool-execution")]


@unittest.skipUnless(os.environ.get("RUN_TEMPORAL") == "1", "set RUN_TEMPORAL=1 (needs temporalio + a downloadable dev server)")
class TemporalEquivalent(unittest.TestCase):
    def test_one_refund_after_activity_retry(self):
        import fake_server_l400
        import payments_service
        import temporal_equivalent as te
        server, url = fake_server_l400.start_in_thread()
        pay, pay_url = payments_service.start_in_thread()
        result = asyncio.run(te.run_demo(url, "fake-model", pay_url))
        refunds = requests.get(f"{pay_url}/refunds", timeout=5).json()
        self.assertEqual((result, len(refunds)), ("done", 1))


if __name__ == "__main__":
    unittest.main()
