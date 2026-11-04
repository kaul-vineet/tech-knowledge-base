"""Tests for project 04's Mac mini scripts at sandbox size (python -m unittest discover -s mac_mini/tests).
The simulator itself is pendingMac; here the generated programs run on the microbit topic's CPython stub."""
import contextlib
import io
import sys
import unittest
from pathlib import Path

MAC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MAC))
import make_sim_programs as msp  # noqa: E402
import soak  # noqa: E402


class SimulatorPrograms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.progs = msp.programs()

    def test_only_main_and_constants_change(self):
        node = self.progs["node_sim.py"]
        self.assertIn("SIMULATOR DRIVER", node)
        self.assertNotIn("power.deep_sleep", node)
        self.assertIn("ACK_WAIT_MS = 500 ", self.progs["node_sim_wait500.py"])
        self.assertIn("RECORDS_PER_FRAME = 27 ", self.progs["node_sim_oversize.py"])
        compile(self.progs["gateway_sim.py"], "gateway_sim.py", "exec")

    def test_node_and_gateway_on_the_stub(self):
        r = msp.run_on_stub(self.progs, "node_sim.py")
        self.assertEqual((r["sampled"], r["acked"], r["left"]), (30, 30, 0))
        self.assertLessEqual(r["max_bytes_on_air"], 32)

    def test_oversize_frames_are_truncated_on_air(self):
        r = msp.run_on_stub(self.progs, "node_sim_oversize.py")
        self.assertGreater(r["maxframe"], 32)
        self.assertEqual(r["max_bytes_on_air"], 32)


class Soak(unittest.TestCase):
    def test_device_id_is_one_byte(self):
        self.assertEqual(soak.dev_id_limit(), 255)

    def test_a_short_site_run_passes(self):
        with contextlib.redirect_stdout(io.StringIO()):
            r = soak.site((20, 9, 4))
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["sampled"], 20 * 9 * 60)

    def test_500_boards_need_two_sites(self):
        import math
        self.assertEqual(math.ceil(500 / soak.DEV_ID_MAX), 2)


if __name__ == "__main__":
    unittest.main()
