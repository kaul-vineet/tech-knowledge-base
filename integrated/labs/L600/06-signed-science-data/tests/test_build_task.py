"""buildTask check: ECMAScript/RFC 8785 number serialisation.

By default this checks solution/jcs_number.py. To check your edited build_task/jcs_number.py instead:
    BUILD_TARGET=mine python -m unittest tests.test_build_task -v      (PowerShell: $env:BUILD_TARGET = "mine")
On the shipped (unfixed) file 3 of 5 tests fail (Appendix B, integral doubles, small numbers); after your fix all pass.
"""
import importlib.util
import os
import struct
import unittest
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
TARGET = LAB / ("build_task" if os.environ.get("BUILD_TARGET") == "mine" else "solution") / "jcs_number.py"
spec = importlib.util.spec_from_file_location("jcs_number_under_test", TARGET)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)

APPENDIX_B = [("0000000000000000", "0"), ("8000000000000000", "0"), ("0000000000000001", "5e-324"),
              ("8000000000000001", "-5e-324"), ("7fefffffffffffff", "1.7976931348623157e+308"),
              ("ffefffffffffffff", "-1.7976931348623157e+308"), ("4340000000000000", "9007199254740992"),
              ("c340000000000000", "-9007199254740992"), ("4430000000000000", "295147905179352830000"),
              ("44b52d02c7e14af5", "9.999999999999997e+22"), ("44b52d02c7e14af6", "1e+23"),
              ("44b52d02c7e14af7", "1.0000000000000001e+23"), ("444b1ae4d6e2ef4e", "999999999999999700000"),
              ("444b1ae4d6e2ef4f", "999999999999999900000"), ("444b1ae4d6e2ef50", "1e+21"),
              ("3eb0c6f7a0b5ed8c", "9.999999999999997e-7"), ("3eb0c6f7a0b5ed8d", "0.000001"),
              ("41b3de4355555553", "333333333.3333332"), ("41b3de4355555554", "333333333.33333325"),
              ("41b3de4355555555", "333333333.3333333"), ("41b3de4355555556", "333333333.3333334"),
              ("41b3de4355555557", "333333333.33333343"), ("becbf647612f3696", "-0.0000033333333333333333"),
              ("43143ff3c1cb0959", "1424953923781206.2")]


def f(hex16):
    return struct.unpack(">d", bytes.fromhex(hex16))[0]


class BuildTask(unittest.TestCase):
    def test_appendix_b_samples(self):
        bad = [(h, target.number(f(h)), want) for h, want in APPENDIX_B if target.number(f(h)) != want]
        self.assertEqual(bad, [])

    def test_integral_doubles_have_no_fraction(self):
        self.assertEqual([target.number(x) for x in (5.0, 100.0, -2.0)], ["5", "100", "-2"])

    def test_small_numbers_use_plain_decimals_down_to_1e_minus_6(self):
        self.assertEqual([target.number(x) for x in (0.002, 1e-6, 1e-7)], ["0.002", "0.000001", "1e-7"])

    def test_large_exponent_has_explicit_plus(self):
        self.assertEqual([target.number(x) for x in (1e21, 1e30)], ["1e+21", "1e+30"])

    def test_rejects_non_json_numbers(self):
        for bad in (float("nan"), float("inf"), True):
            with self.assertRaises((ValueError, TypeError)):
                target.number(bad)


if __name__ == "__main__":
    unittest.main()
