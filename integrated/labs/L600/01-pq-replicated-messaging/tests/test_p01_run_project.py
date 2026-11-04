"""End to end: run_project.py exits 0 with every line passing, and --inject leader-counter exits 1 with the
failure-lab line (reused nonces + recovered plaintext). Uses --messages 300 to keep the run short."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # the lab folder

LAB = Path(__file__).resolve().parents[1]


def run(*args):
    p = subprocess.run([sys.executable, str(LAB / "run_project.py"), "--messages", "300", *args], cwd=LAB,
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, [json.loads(line) for line in p.stdout.splitlines() if line.startswith("{")]


class TestRunProject(unittest.TestCase):
    def test_default_all_pass(self):
        code, rows = run()
        self.assertEqual(code, 0)
        self.assertEqual((rows[-1]["passed"], rows[-1]["total"]), (13, 13))

    def test_inject_leader_counter_fails(self):
        code, rows = run("--inject", "leader-counter")
        self.assertEqual(code, 1)
        lab = next(r for r in rows if "failure_lab" in r)
        self.assertGreater(lab["reused_nonces"], 0)
        self.assertEqual(lab["keystream_reuse"]["recovered"], lab["keystream_reuse"]["actual"])


if __name__ == "__main__":
    unittest.main()
