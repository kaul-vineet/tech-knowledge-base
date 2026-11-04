"""Runs every check script in this folder: each must exit 0 (the scripts assert the theorem's prediction) and print
exactly the checkOutput recorded in content/L500.json.   python -m unittest -v"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
LESSON = 24


def recorded():
    lessons = json.loads((HERE.parents[2] / "content" / "L500.json").read_text(encoding="utf-8"))
    lesson = next(l for l in lessons if l["number"] == LESSON)
    items = lesson.get("theorems", []) + ([lesson["codeCheck"]] if "codeCheck" in lesson else [])
    return {Path(t["check"]).name: t["checkOutput"] for t in items}


class TestChecks(unittest.TestCase):
    def test_scripts_pass_and_match_recorded_output(self):
        expected = recorded()
        self.assertTrue(expected)
        for name, want in expected.items():
            with self.subTest(script=name):
                r = subprocess.run([sys.executable, name], cwd=HERE, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(r.returncode, 0, r.stderr)
                if sys.platform.startswith("linux"):  # recorded on Linux; other OSes must still pass the asserts
                    self.assertEqual(r.stdout.rstrip("\n"), want)
