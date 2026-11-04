"""Build task (lesson 14): a circuit breaker stops paying for a dead primary on every chat.
Default target = solution/circuit_breaker.py. Test YOUR circuit_breaker.py (shipped unfixed, so it fails first):
  BUILD_TARGET=mine python -m unittest -v test_build_task
  PowerShell: $env:BUILD_TARGET="mine"; python -m unittest -v test_build_task"""
import importlib.util
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import resilient_agent as ra  # noqa: E402
from fake_server_l300 import start_in_thread  # noqa: E402

TARGET = HERE if os.environ.get("BUILD_TARGET") == "mine" else HERE / "solution"
spec = importlib.util.spec_from_file_location("target_circuit_breaker", TARGET / "circuit_breaker.py")
cb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cb)
QUESTIONS = ["What is 1+1?", "What is 2+2?", "What is 3+3?", "What is 4+4?"]


class BuildTask(unittest.TestCase):
    def primary_calls(self, client_cls, **kw):
        dead, dead_url = start_in_thread(fail_rate=1.0)  # primary always 503
        ok, ok_url = start_in_thread()
        try:
            client = client_cls([(dead_url, "fake-model"), (ok_url, "fake-small")], backoff=0.0, **kw)
            answers = [ra.answer(q, client) for q in QUESTIONS]
        finally:
            for s in (dead, ok):
                s.shutdown()
                s.server_close()
        return dead.stats["requests"], answers

    def test_breaker_saves_calls(self):
        plain, a1 = self.primary_calls(ra.Client)
        breaker, a2 = self.primary_calls(cb.BreakerClient, trip_after=2, cool_down=5)
        self.assertEqual(a1, a2)
        self.assertEqual((plain, breaker), (24, 9))  # 8 chats x 3 attempts vs: 2 chats fail (6), 5 skipped, 1 probe (3)


if __name__ == "__main__":
    unittest.main()
