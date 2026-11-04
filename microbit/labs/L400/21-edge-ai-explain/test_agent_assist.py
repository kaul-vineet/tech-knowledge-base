"""The lesson's agentAssist output (fake model server) is what solution.py prints."""
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class AgentAssist(unittest.TestCase):
    def test_output_matches_the_recorded_file(self):
        out = subprocess.run([sys.executable, "solution.py"], cwd=HERE, capture_output=True, text=True,
                             encoding="utf-8", timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout, (HERE / "agent_assist_output.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
