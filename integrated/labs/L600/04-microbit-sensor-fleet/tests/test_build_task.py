"""Build task: 251-byte frames without breaking the radio seam.
Default target = solution/node_251.py. Test YOUR firmware/node.py:
  BUILD_TARGET=mine python -m unittest tests.test_build_task -v
  (PowerShell: $env:BUILD_TARGET="mine"; py -m unittest tests.test_build_task -v)
The shipped firmware/node.py keeps the 32-byte default, so it FAILS this check."""
import os
import unittest

from tests._shared import run
import _kb  # noqa: E402
import fleet_sim  # noqa: E402

TARGET = "node.py" if os.environ.get("BUILD_TARGET") == "mine" else "../solution/node_251.py"


def firmware():
    src = fleet_sim.firmware_sources(TARGET)["d01"]
    return _kb.labtest().load_boards(str(fleet_sim.FIRMWARE), ["x"], sources={"x": src})[0].lab


class BigFrames(unittest.TestCase):
    def test_length_and_records_per_frame(self):
        fw = firmware()
        self.assertEqual(fw.RADIO_LENGTH, 251)
        self.assertEqual(fw.RECORDS_PER_FRAME, (fw.RADIO_LENGTH - fw.HEADER) // fw.REC_LEN[fw.SCHEMA])

    def test_no_loss_fewer_frames_more_battery(self):
        mine, base = run(firmware=TARGET), run()
        self.assertEqual((mine["lost"], mine["dropped_flash_full"]), (0, 0))
        self.assertLessEqual(mine["max_frame_bytes"], 251)
        self.assertEqual(sum(mine["rejected"].values()), 0)
        self.assertLess(mine["frames"], base["frames"] / 2)
        self.assertGreaterEqual(mine["life_h_min"], base["life_h_min"])


if __name__ == "__main__":
    unittest.main()
