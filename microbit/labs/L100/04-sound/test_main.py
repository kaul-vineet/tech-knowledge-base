import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402
import music  # noqa: E402


class SoundLab(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE)

    def test_start_plays_hello_and_pitch(self):
        with serial() as out:
            self.lab.start()
        self.assertEqual(microbit.audio.played, [microbit.Sound.HELLO])
        self.assertEqual(music.played, [("pitch", (440, 200))])
        self.assertEqual(out.getvalue(), "sound ready\n")

    def test_button_a_plays_tune(self):
        microbit.button_a.click()
        with serial() as out:
            self.lab.step()
        self.assertEqual(music.played, [("play", self.lab.TUNE)])
        self.assertIn("tune played", out.getvalue())

    def test_button_b_toggles_speaker(self):
        microbit.button_b.click()
        with serial() as out:
            self.lab.step()
        self.assertFalse(microbit.speaker.is_on())
        microbit.button_b.click()
        with serial() as out2:
            self.lab.step()
        self.assertTrue(microbit.speaker.is_on())
        self.assertEqual(out.getvalue() + out2.getvalue(), "speaker off\nspeaker on\n")

    def test_tune_after_speaker_off_is_logged_as_speaker_off(self):
        microbit.button_b.click()
        with serial():
            self.lab.step()
        microbit.button_a.click()
        with serial():
            self.lab.step()
        self.assertEqual(microbit.sound_log[-1][0], "music")
        self.assertFalse(microbit.sound_log[-1][2])

    def test_logo_plays_effect(self):
        microbit.pin_logo.inject_touch(True)
        with serial() as out:
            self.lab.step()
        fx = microbit.audio.played[-1]
        self.assertEqual((fx.freq_start, fx.freq_end, fx.duration), (400, 2000, 400))
        self.assertIn("effect played", out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
