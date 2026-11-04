import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_lab, serial  # noqa: E402
import microbit  # noqa: E402


class PinsLab(unittest.TestCase):
    def setUp(self):
        self.lab = load_lab(HERE)
        self.state = self.lab.new_state()

    def tick(self):
        with serial() as out:
            duty = self.lab.step(self.state)
        return duty, out.getvalue()

    def touch_logo(self):
        microbit.pin_logo.inject_touch(True)
        self.tick()
        microbit.pin_logo.inject_touch(False)
        return self.tick()

    def test_duty_levels(self):
        self.assertEqual([self.lab.duty_for(l) for l in range(5)], [0, 255, 511, 767, 1023])

    def test_starts_off(self):
        self.assertEqual(self.tick(), (0, "on=0,level=2,duty=0\n"))
        self.assertEqual(microbit.pin1.digital_out, 0)
        self.assertEqual(microbit.pin2.get_mode(), "analog")
        self.assertEqual(microbit.pin2.get_analog_period_microseconds(), 20000)

    def test_logo_edge_toggles_once_while_held(self):
        microbit.pin_logo.inject_touch(True)
        self.tick()
        self.tick()                                   # still held: no second toggle
        self.assertTrue(self.state["on"])
        self.assertEqual(microbit.pin1.digital_out, 1)
        self.assertEqual(microbit.pin2.duty, 511)

    def test_buttons_change_level_with_limits(self):
        self.touch_logo()
        microbit.button_a.click(times=3)              # was_pressed() is one edge -> +1 per poll
        for _ in range(3):
            self.tick()
        self.assertEqual(self.state["level"], 3)
        microbit.button_a.click()
        self.tick()
        microbit.button_a.click()
        self.assertEqual(self.tick(), (1023, ""))     # capped at LEVELS = 4: nothing new to print

    def test_pin0_touch_boosts(self):
        self.touch_logo()
        microbit.pin0.inject_touch(True)
        self.assertEqual(self.tick(), (1023, "on=1,level=2,duty=1023\n"))
        self.assertEqual(microbit.pin0.get_mode(), "touch")

    def test_write_analog_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            microbit.pin2.write_analog(1024)


if __name__ == "__main__":
    unittest.main(verbosity=2)
