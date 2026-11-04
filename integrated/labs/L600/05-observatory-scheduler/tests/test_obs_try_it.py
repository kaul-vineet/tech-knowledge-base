"""Both tryIt scripts run and print the values recorded in the README and the lesson."""
import subprocess
import sys
import unittest

from tests import _lab


def run(name):
    p = subprocess.run([sys.executable, str(_lab.LAB / "try_it" / name)], capture_output=True, text=True,
                       encoding="utf-8", cwd=str(_lab.LAB))
    assert p.returncode == 0, p.stderr
    return p.stdout


class TryIt(unittest.TestCase):
    def test_cloudier_site(self):
        out = run("t1_cloudier_site.py")
        self.assertIn("a=0.08 pi_clear=0.714 | greedy 4.503 local 5.965 ratio 1.325", out)

    def test_tighter_airmass(self):
        out = run("t2_tighter_airmass.py")
        self.assertIn("airmass <= 1.5: feasible 4", out)
        self.assertIn("local ['Deneb', 'Aldebaran', 'Capella', 'Betelgeuse'] 8.209 | violations 0", out)


if __name__ == "__main__":
    unittest.main()
