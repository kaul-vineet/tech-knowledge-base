"""End to end: the scorecard passes, and the injected bypass exits non-zero with S3 and F3 failing."""
import json
import subprocess
import sys
import unittest

import _lab


def run(*args):
    p = subprocess.run([sys.executable, str(_lab.LAB / "run_project.py"), *args], capture_output=True, text=True,
                       encoding="utf-8", cwd=_lab.LAB, timeout=1800)
    return p.returncode, [json.loads(line) for line in p.stdout.splitlines() if line.strip()]


class TestRunProject(unittest.TestCase):
    def test_scorecard_all_pass(self):
        code, rows = run()
        self.assertEqual(code, 0)
        self.assertEqual(rows[-1]["scorecard"], {"milestones": "5/5", "seams": "4/4", "fitness": "4/4"})

    def test_inject_bypass_fails(self):
        code, rows = run("--inject", "bypass")
        failed = {r.get("seam") or r.get("fitness") or r.get("milestone") for r in rows if r.get("pass") is False}
        self.assertEqual(code, 1)
        self.assertTrue(any(n.startswith("S3") for n in failed) and any(n.startswith("F3") for n in failed))
        self.assertFalse(any(n.startswith("F1") or n.startswith("M3") for n in failed))   # static checks stay green


if __name__ == "__main__":
    unittest.main()
