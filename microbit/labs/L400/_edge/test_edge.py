import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from minibroker import MiniBroker, matches  # noqa: E402
from simnet import LinkAir, percentile, serial_ms  # noqa: E402
from store import Store, to_csv, to_prometheus  # noqa: E402


class Helpers(unittest.TestCase):
    def test_topic_filters(self):
        self.assertTrue(matches("classroom/+/telemetry", "classroom/n1/telemetry"))
        self.assertTrue(matches("classroom/#", "classroom/n1/telemetry"))
        self.assertFalse(matches("classroom/+", "classroom/n1/telemetry"))
        self.assertFalse(matches("classroom/n2/telemetry", "classroom/n1/telemetry"))

    def test_retained_reaches_late_subscriber(self):
        b = MiniBroker()
        b.publish("fleet/n1/config", "v2", retain=True)
        got = []
        b.subscribe("fleet/+/config", lambda t, p: got.append((t, p)))
        self.assertEqual(got, [("fleet/n1/config", "v2")])

    def test_store_is_an_idempotent_consumer(self):
        s = Store()
        row = dict(dev="n1", seq=1, t_sensor=0, t_store=5, temp=21, light=100, motion=0)
        self.assertTrue(s.add(row))
        self.assertFalse(s.add(row))          # QoS 1 redelivery
        self.assertEqual((len(s.rows()), s.duplicates), (1, 1))
        self.assertIn("n1,1,0,5,21,100,0", to_csv(s.rows()))
        self.assertIn('classroom_readings_total{dev="n1"} 1', to_prometheus(s.summary()))

    def test_percentile_and_serial_time(self):
        self.assertEqual(percentile([5, 1, 3, 2, 4], 50), 3)
        self.assertEqual(percentile(list(range(1, 101)), 95), 95)
        self.assertAlmostEqual(serial_ms(24), 2.083, places=3)

    def test_link_air_loss_is_seeded(self):
        a, b = LinkAir(loss={"s1": 1.0}, seed=1), LinkAir(default_loss=0.0, seed=1)
        self.assertEqual(a.p_loss("s1", "relay"), 1.0)
        self.assertEqual(b.p_loss("s1", "relay"), 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
