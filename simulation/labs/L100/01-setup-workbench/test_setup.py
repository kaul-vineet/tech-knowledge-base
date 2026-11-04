import sys
import unittest

import check_env


class TestSetup(unittest.TestCase):
    def test_python_version(self):
        self.assertGreaterEqual(sys.version_info[:2], (3, 12))

    def test_numpy_available(self):
        self.assertIsNotNone(check_env.installed("numpy"))

    def test_pins_are_exact(self):
        self.assertEqual(set(check_env.PINS), {"numpy", "simpy", "scipy", "mesa"})
        for pin in check_env.PINS.values():
            self.assertRegex(pin, r"^\d+\.\d+\.\d+$")

    def test_pins_parse_with_windows_line_endings(self):
        self.assertEqual(check_env.parse_pins("# pins\r\nnumpy==2.5.3\r\n\r\n"), {"numpy": "2.5.3"})

    def test_seeded_rng_is_reproducible(self):
        self.assertEqual(check_env.seeded_draws(42), check_env.seeded_draws(42))
        self.assertNotEqual(check_env.seeded_draws(42), check_env.seeded_draws(43))


if __name__ == "__main__":
    unittest.main()
