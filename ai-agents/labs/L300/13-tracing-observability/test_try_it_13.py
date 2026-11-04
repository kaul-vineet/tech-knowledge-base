"""Try it (lesson 13): two changes, run against the fake server. Run: python -m unittest -v test_try_it_13"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import traced_agent as ta  # noqa: E402
from fake_server_l300 import start_in_thread  # noqa: E402

TASK = 'What is the weather in Paris? Also search docs for "rate limits" and compute 17*23.'


class TryIt(unittest.TestCase):
    def trace(self, **faults):
        ta._INDEX.clear()
        server, url = start_in_thread(**faults)
        try:
            with tempfile.TemporaryDirectory(dir=HERE) as d:
                path = Path(d) / "t.jsonl"
                ta.run(TASK, ta.Tracer(path), base_url=url, model="fake-model")
                return [(r["name"], r["count"]) for r in ta.summarize(path)][:2], ta.diagnose(path)
        finally:
            server.shutdown()
            server.server_close()

    def test_1_no_cold_index(self):
        with mock.patch.object(ta, "COLD_INDEX_S", 0.0):
            top, slowest = self.trace()
        print("\nobserved:", top, "| slowest:", slowest)
        self.assertEqual(slowest, "chat fake-model")

    def test_2_slow_model_server(self):
        top, slowest = self.trace(slow_rate=1.0, slow_s=0.25)  # every model call +250 ms
        print("\nobserved:", top, "| slowest:", slowest)
        self.assertEqual(slowest, "chat fake-model")


if __name__ == "__main__":
    unittest.main(verbosity=2)
