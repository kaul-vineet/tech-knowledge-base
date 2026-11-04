import sys
import tempfile
import unittest
from pathlib import Path

import check_env


class TestWorkbench(unittest.TestCase):
    def test_python_version(self):
        self.assertGreaterEqual(sys.version_info[:2], (3, 12))

    def test_numpy_available(self):
        import numpy  # noqa: F401

    def test_pins_are_exact_and_crlf_safe(self):
        self.assertEqual(check_env.parse_pins("numpy==2.5.3\r\n# c\r\nastropy==8.0.2\r\n"),
                         {"numpy": "2.5.3", "astropy": "8.0.2"})
        for pkg, pin in check_env.PINS.items():
            self.assertRegex(pin, r"^\d+(\.\d+)+$", pkg)

    def test_data_folders_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            made = check_env.make_folders(Path(tmp) / "data")
            self.assertEqual(made, ["data/raw", "data/cache", "data/derived"])
            self.assertTrue(all((Path(tmp) / m).is_dir() for m in made))

    def test_seeded_field_is_reproducible(self):
        self.assertEqual(check_env.synthetic_stars(42), check_env.synthetic_stars(42))
        self.assertEqual(check_env.synthetic_stars(42)[0], (278.6242, 8.97))


if __name__ == "__main__":
    unittest.main()
