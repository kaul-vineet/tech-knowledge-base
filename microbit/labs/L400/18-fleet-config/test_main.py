"""Lab 18 basics: config parsing/validation, frames, the one-phase agent's happy path (config_agent.py)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fleet_sim  # noqa: E402
from labtest import load_boards  # noqa: E402


class Config(unittest.TestCase):
    def setUp(self):
        (self.b,) = load_boards(str(HERE), names=("n1",), filename="config_agent.py")

    def test_parse_and_validate(self):
        lab = self.b.lab
        self.assertEqual(lab.parse_cfg(2, "i=500;th=28;g=18"), {"v": 2, "i": 500, "th": 28, "g": 18})
        self.assertIsNone(lab.parse_cfg(2, "i=50;th=28;g=18"))      # interval below 100 ms
        self.assertIsNone(lab.parse_cfg(2, "i=500;th=28"))          # missing key
        self.assertIsNone(lab.parse_cfg(2, "i=500;th=28;g=18;x=1"))  # unknown key

    def test_frames(self):
        lab = self.b.lab
        text = lab.encode("C", "n1", 2, "i=500;th=28;g=18")
        self.assertEqual(lab.decode(text), ("C", "n1", 2, "i=500;th=28;g=18"))
        self.assertIsNone(lab.decode(text.replace("28", "29")))

    def test_good_config_reaches_every_device_on_a_quiet_link(self):
        m, _ = fleet_sim.run("config_agent.py", "push-all", loss=0.0, plan={0: fleet_sim.GOOD}, end_ms=3000)
        self.assertEqual(list(m["final"].values()), [2] * 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
