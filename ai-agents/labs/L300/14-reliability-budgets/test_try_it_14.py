"""Try it (lesson 14): two changes on the seeded flaky run. Run: python -m unittest -v test_try_it_14"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import compare  # noqa: E402


def summary(res):
    fallbacks = sum(e["event"] == "fallback" for e in res["events"])
    return f"canned {res['canned']}, fallbacks {fallbacks}, HTTP calls {res['http_calls']}"


class TryIt(unittest.TestCase):
    def test_1_no_retries(self):
        res = compare.run("hardened", retries=0)
        print("\nobserved:", summary(res))
        self.assertEqual(res["canned"], 1)

    def test_2_no_fallback_model(self):
        res = compare.run("hardened", fallback=False)
        print("\nobserved:", summary(res))
        self.assertEqual(res["canned"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
