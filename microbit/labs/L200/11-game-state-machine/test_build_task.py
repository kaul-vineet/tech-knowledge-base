"""Build task check (lab 11): B pauses/resumes; paused time does not count toward ROUND_MS.

Runs solution.py. To check YOUR version: BUILD_FILE=main.py python -m unittest test_build_task
(Windows PowerShell: $env:BUILD_FILE="main.py"; py -m unittest test_build_task)
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402

BUILD_FILE = os.environ.get("BUILD_FILE", "solution.py")


class PauseBuildTask(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE, BUILD_FILE)
        self.game = self.lab.new_game()

    def poll(self):
        with serial() as out:
            self.lab.step(self.game)
        return out.getvalue()

    def test_table_has_pause_and_resume(self):
        self.assertEqual(self.lab.next_state("play", "b")[0], "paused")
        self.assertEqual(self.lab.next_state("paused", "b")[0], "play")
        self.assertEqual(self.lab.next_state("paused", "timeout")[0], "paused")
        self.assertEqual(self.lab.next_state("idle", "b")[0], "idle")

    def test_paused_time_is_not_counted(self):
        microbit.button_a.click()
        self.poll()                                     # play at t = 0
        microbit.sleep(2000)
        microbit.button_b.click()
        self.assertEqual(self.poll(), "play -> paused (b)\n")
        microbit.sleep(10000)                           # long pause: no timeout
        self.assertEqual(self.poll(), "")
        microbit.button_b.click()
        self.assertEqual(self.poll(), "paused -> play (b)\n")
        microbit.sleep(3999)                            # 2000 + 3999 < 6000
        self.assertEqual(self.poll(), "")
        microbit.sleep(1)
        self.assertEqual(self.poll(), "play -> over (timeout)\nscore 0\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
