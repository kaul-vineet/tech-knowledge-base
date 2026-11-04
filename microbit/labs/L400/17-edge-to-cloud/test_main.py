"""Lab 17 basics: frames, relay dedupe, one sensor end to end (node.py, the shipped file)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edge_sim  # noqa: E402
from labtest import load_boards, serial  # noqa: E402


class Frames(unittest.TestCase):
    def setUp(self):
        self.a, self.r = load_boards(str(HERE), names=("n1", "relay"), filename="node.py")

    def test_round_trip_and_crc(self):
        lab = self.a.lab
        text = lab.encode("D", "n1", 7, "1000,21,120,0")
        self.assertEqual(lab.decode(text), ("D", "n1", 7, "1000,21,120,0"))
        self.assertIsNone(lab.decode(text.replace("21", "31")))     # flipped digit -> CRC fails
        self.assertLessEqual(len(text) + 3, 32)                       # fits the default 32-byte packet

    def test_relay_acks_dedupes_and_frames_for_the_gateway(self):
        lab, st = self.r.lab, self.r.lab.new_state("relay", "relay")
        with serial() as out:
            lab.on_frame(st, ("D", "n1", 1, "0,20,100,0"))
            lab.on_frame(st, ("D", "n1", 1, "0,20,100,0"))           # a retransmit after a lost ack
        self.assertEqual((st["stats"]["fwd"], st["stats"]["dup"]), (1, 1))
        self.assertEqual(len(self.r.radio.sent), 2)                  # but both copies were acked
        frames = list(edge_sim.l15.Framer().feed(out.getvalue().encode("ascii")))
        self.assertEqual(frames, [b"n1,1,0,20,100,0"])


class OneSensor(unittest.TestCase):
    def test_single_sensor_is_fine(self):
        res, store = edge_sim.run("node.py", n=1, loss={"n1": 0.05}, readings=20)
        self.assertEqual(res["delivery_pct"], 100.0)
        self.assertEqual(store.rows()[0]["temp"], 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
