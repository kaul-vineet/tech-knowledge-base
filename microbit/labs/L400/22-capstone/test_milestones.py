"""One test class per capstone milestone, on ONE seeded end-to-end run (seed 22)."""
import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_firmware  # noqa: E402
import run_capstone  # noqa: E402

TMP = tempfile.TemporaryDirectory(dir=HERE)   # inside the lab, removed at exit
LINES, R = run_capstone.scorecard(out_dir=Path(TMP.name))
CARD = [json.loads(line) for line in LINES]


class M0Firmware(unittest.TestCase):
    def test_board_program_is_built_from_the_labs(self):
        src = build_firmware.build()
        ast.parse(src)
        self.assertIn("def siphash24", src)                     # lab 19
        self.assertIn("def pump(state, now):", src)             # lab 17
        self.assertIn("LENGTH = 96", src)


class M1Network(unittest.TestCase):
    def test_delivery_and_latency(self):
        self.assertEqual((R["net"]["stored"], R["net"]["sampled"]), (3599, 3600))
        self.assertEqual(R["net"]["p95_ms"], 324)


class M2TrustedGateway(unittest.TestCase):
    def test_attacks_rejected(self):
        self.assertEqual(R["net"]["eve"], {"replayed": 10, "forged": 10})
        self.assertEqual((R["net"]["forged_stored"], R["net"]["replays_stored"]), (0, 0))
        self.assertEqual(R["net"]["rejects"], {"mac": 9, "replay": 8})


class M3Fleet(unittest.TestCase):
    def test_staged_two_phase_rollout(self):
        self.assertEqual(R["fleet"], {"unacked_ticks": 0, "max_on_bad": 1, "final": "222222"})


class M4Twin(unittest.TestCase):
    def test_drift_found(self):
        self.assertEqual(R["drift"]["n5 DRIFT_LAT"], 14)
        self.assertIn("n4 DRIFT_TEMP", R["drift"])              # the sun on n4 is a real change too


class M5AlarmsAndAgent(unittest.TestCase):
    def test_model_explains_code_decides(self):
        self.assertFalse(R["agent"]["accepted"])                # injected label -> reply rejected
        self.assertIn("TEMP_HIGH at n4", R["agent"]["note"])    # code-written fallback names it


class M6Dashboard(unittest.TestCase):
    def test_exports_and_scorecard(self):
        self.assertEqual(R["dash"], {"csv_rows": 3599, "prom_total": 3599})
        self.assertTrue((Path(TMP.name) / "metrics.txt").read_text(encoding="utf-8").startswith("# HELP"))
        self.assertEqual(CARD[-1]["scorecard"], "PASS")
        self.assertEqual(CARD[-1]["passed"], 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
