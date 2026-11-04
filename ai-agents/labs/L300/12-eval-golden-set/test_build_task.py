"""Build task (lesson 12): per-category gate catches the 'account' collapse even without a baseline.
Default target = solution/category_gate.py. Test YOUR category_gate.py (shipped unfixed, so it fails first):
  BUILD_TARGET=mine python -m unittest -v test_build_task
  PowerShell: $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task"""
import importlib.util
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import eval_gate as eg  # noqa: E402
from fake_server_l300 import start_in_thread  # noqa: E402

TARGET = HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"
spec = importlib.util.spec_from_file_location("target_category_gate", TARGET / "category_gate.py")
cg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cg)


class BuildTask(unittest.TestCase):
    def test_category_gate(self):
        server, url = start_in_thread()
        try:
            v1 = eg.evaluate(HERE / "prompts" / "v1.txt", base_url=url, model="fake-model")
            v2 = eg.evaluate(HERE / "prompts" / "v2.txt", base_url=url, model="fake-model")
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(cg.category_gate(v1), [])
        self.assertEqual(cg.category_gate(v2), ["account: 0/2 passed (0%) < 80%"])


if __name__ == "__main__":
    unittest.main()
