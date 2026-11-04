"""Build task: the 'calls < N' caveat. Default tests solution/rate_caveat.py.
Test YOUR version:  macOS   BUILD_TARGET=mine python -m unittest test_build_task      (from tests/)
                    Windows $env:BUILD_TARGET="mine"; python -m unittest test_build_task
The shipped rate_caveat.py is unfixed: it fails all 3 tests until you implement it."""
import importlib.util
import os
import unittest

import _lab
from adapters import T0
from capability import CapabilityError, attenuate, mint, verify

path = _lab.LAB / ("rate_caveat.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/rate_caveat.py")
spec = importlib.util.spec_from_file_location("rate_caveat_under_test", path)
impl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(impl)
KEY = b"\x08" * 32


def call(token, counter):
    verify(token, KEY, {"session": "s-1", "now": T0, "tool": "search_docs", "args": {}}, extra=counter.check)


class TestCallsCaveat(unittest.TestCase):
    def setUp(self):
        self.base = mint(KEY, "cap-s-1", ["session = s-1", f"expires < {T0 + 60}", "tool in search_docs"])

    def test_three_calls_then_denied(self):
        counter, tok = impl.CallCounter(), attenuate(self.base, "calls < 3")
        for _ in range(3):
            call(tok, counter)
        with self.assertRaises(CapabilityError):
            call(tok, counter)

    def test_two_attenuations_the_tighter_wins(self):
        counter, tok = impl.CallCounter(), attenuate(attenuate(self.base, "calls < 5"), "calls < 2")
        call(tok, counter)
        call(tok, counter)
        with self.assertRaises(CapabilityError):
            call(tok, counter)

    def test_unknown_caveat_still_fails_closed(self):
        with self.assertRaisesRegex(CapabilityError, "unknown caveat"):
            call(attenuate(self.base, "frobnicate = 1"), impl.CallCounter())


if __name__ == "__main__":
    unittest.main()
