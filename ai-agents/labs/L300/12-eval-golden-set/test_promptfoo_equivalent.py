"""promptfoo equivalent (pending-ci). The sync check runs everywhere; the npx run only when RUN_PROMPTFOO=1."""
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import make_promptfoo_tests  # noqa: E402

PROMPTFOO = "promptfoo@0.125.1"


class PromptfooEquivalent(unittest.TestCase):
    def test_tests_file_in_sync_with_golden_set(self):
        self.assertEqual((HERE / "promptfoo_tests.jsonl").read_text(encoding="utf-8"), make_promptfoo_tests.build())

    @unittest.skipUnless(os.environ.get("RUN_PROMPTFOO") == "1" and shutil.which("npx"), "needs Node 24 + network (CI)")
    def test_promptfoo_exit_codes(self):
        from fake_server_l300 import start_in_thread
        server, _ = start_in_thread(port=8765)  # promptfooconfig.yaml points at 127.0.0.1:8765
        try:
            npx = shutil.which("npx")
            env = dict(os.environ, PROMPTFOO_DISABLE_TELEMETRY="1", PROMPTFOO_DISABLE_UPDATE="1")  # no usage telemetry
            run = lambda *a: subprocess.run([npx, "-y", PROMPTFOO, "eval", "-c", "promptfooconfig.yaml", "--no-cache", *a],
                                            cwd=HERE, env=env, capture_output=True, encoding="utf-8", timeout=600)
            ok, bad = run(), run("-p", "prompts/v2.txt")
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(ok.returncode, 0, ok.stdout[-2000:] + ok.stderr[-2000:])
        self.assertEqual(bad.returncode, 100, bad.stdout[-2000:])  # promptfoo: 100 = at least one test failed


if __name__ == "__main__":
    unittest.main()
