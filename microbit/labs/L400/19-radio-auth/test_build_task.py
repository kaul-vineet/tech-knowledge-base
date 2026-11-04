"""Build task check (lab 19): per-device SipHash MAC + replay window at the gateway.

Runs solution.py. Check YOUR file: BUILD_TARGET=mine python -m unittest test_build_task
(= verifier.py, which FAILS as shipped; or BUILD_FILE=<file>). Windows PowerShell:
$env:BUILD_TARGET="mine"; py -m unittest test_build_task
"""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import attacks  # noqa: E402
import frame_auth as fa  # noqa: E402

TARGET = os.environ.get("BUILD_FILE") or ("verifier.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution.py")
KEY = bytes(range(16))


class Gateway(unittest.TestCase):
    def setUp(self):
        self.v = attacks.load_verifier(TARGET)({"n1": KEY}, mode="siphash")

    def test_attack_scenario(self):
        m, _ = attacks.run(TARGET, "siphash")
        self.assertEqual((m["forged_accepted"], m["replays_accepted"]), (0, 0))
        self.assertEqual(m["genuine_accepted"], m["genuine_intact"])

    def test_unknown_device_and_wrong_key_rejected(self):
        self.assertIsNone(self.v.check(fa.seal("n9", 1, "21,100,0", KEY)))
        self.assertIsNone(self.v.check(fa.seal("n1", 1, "21,100,0", bytes(16))))

    def test_reordering_inside_the_window_is_fine_replays_are_not(self):
        frames = [fa.seal("n1", c, "21,100,0", KEY) for c in (5, 3, 4, 70)]
        self.assertEqual([bool(self.v.check(f)) for f in frames], [True, True, True, True])
        self.assertIsNone(self.v.check(frames[1]))              # 3 again: replay
        self.assertIsNone(self.v.check(fa.seal("n1", 2, "21,100,0", KEY)))   # older than 70 - 64

    def test_forged_frame_does_not_move_the_window(self):
        self.assertTrue(self.v.check(fa.seal("n1", 10, "21,100,0", KEY)))
        self.assertIsNone(self.v.check("n1:500:45,100,0:" + "0" * 16))
        self.assertTrue(self.v.check(fa.seal("n1", 11, "21,100,0", KEY)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
