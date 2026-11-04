"""Try it (lesson 17): two changes on the fixed task set. Run: python -m unittest -v test_try_it_17"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import fake_server_l400  # noqa: E402
import patterns  # noqa: E402


def measure(context_limit, fn):
    server, url = fake_server_l400.start_in_thread(context_limit=context_limit)
    try:
        return patterns.summary(patterns.evaluate("single", url, "fake-model", fn=fn))
    finally:
        server.shutdown()
        server.server_close()


class TryIt(unittest.TestCase):
    def test_1_bigger_context_window(self):
        s = measure(2000, patterns.single)
        print(f"\nobserved: context 2000 -> single {s['passed']}/10, tokens {s['tokens']}, failed {s['failed']}")
        self.assertEqual(s["passed"], 10)

    def test_2_twelve_extra_tools(self):
        base = measure(None, patterns.single)
        more = measure(None, lambda run, task: patterns.single(run, task, extra_tools=12))
        print(f"\nobserved: 6 tools -> {base['tokens']} tokens; 18 tools -> {more['tokens']} tokens "
              f"(+{more['tokens'] - base['tokens']}) for the same {more['model_calls']} model calls")
        self.assertGreater(more["tokens"], base["tokens"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
