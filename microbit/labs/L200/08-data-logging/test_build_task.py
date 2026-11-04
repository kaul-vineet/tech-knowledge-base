"""Build task check (lab 08): a full log stops logging cleanly; serial CSV continues.

Runs solution.py. To check YOUR version: BUILD_FILE=main.py python -m unittest test_build_task
(Windows PowerShell: $env:BUILD_FILE="main.py"; py -m unittest test_build_task)
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import log  # noqa: E402  (stub)
import microbit  # noqa: E402

BUILD_FILE = os.environ.get("BUILD_FILE", "solution.py")


class LogFullBuildTask(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE, BUILD_FILE)
        log._set_capacity(40)                   # header + one row fit, the 2nd row does not

    def test_log_full_is_handled(self):
        with serial() as out:
            self.lab.setup()
            state = self.lab.new_state()
            for t in (21, 22, 23):
                microbit._inject_temperature(t)
                self.lab.step(state)
                microbit.sleep(1000)
        self.assertEqual(out.getvalue().splitlines(), [
            "time_ms,temp,light", "0,21,127", "log full after 1 rows", "1000,22,127", "2000,23,127"])
        self.assertFalse(state["logging"])
        self.assertEqual(log.rows, ["Time (seconds),temp,light", "0.00,21,127"])

    def test_other_oserrors_are_not_swallowed(self):
        def broken(*args, **kwargs):
            raise OSError(5)
        self.lab.log.add = broken
        try:
            with serial(), self.assertRaises(OSError):
                self.lab.setup()
                self.lab.step(self.lab.new_state())
        finally:
            import importlib
            importlib.reload(log)


if __name__ == "__main__":
    unittest.main(verbosity=2)
