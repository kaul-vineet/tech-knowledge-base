"""python -m unittest -v : lesson 16 engine, queueing behaviour and the reproducible overload."""
import unittest

import backpressure as bp
from aimd import AIMDLimit
from helpers import simulate


class Queueing(unittest.TestCase):
    def test_same_seed_same_records(self):
        a = simulate(bp.Server(), [(2, 300)], bp.SERVICE_MS)
        b = simulate(bp.Server(), [(2, 300)], bp.SERVICE_MS)
        self.assertEqual(a, b)

    def test_wait_grows_faster_than_load_below_capacity(self):
        waits = [bp.summary(simulate(bp.Server(), [(20, load * bp.CAPACITY)], bp.SERVICE_MS))["mean_wait_ms"]
                 for load in (0.5, 0.8, 0.95)]
        self.assertLess(waits[0], waits[1])
        self.assertGreater(waits[2] / waits[1], 3)  # 0.8 -> 0.95 is +19% load but several times the wait

    def test_throughput_caps_at_capacity(self):
        s = bp.summary(simulate(bp.Server(), [(10, 2 * bp.CAPACITY)], bp.SERVICE_MS))
        self.assertLessEqual(s["throughput_per_s"], bp.CAPACITY * 1.05)

    def test_metrics_lines_are_json(self):
        lines = bp.per_second(simulate(bp.Server(), [(3, 100)], bp.SERVICE_MS))
        self.assertEqual(len(lines), 3)
        self.assertIn('"p99_ms"', lines[0])

    def test_aimd_backs_off_and_recovers(self):
        lim = AIMDLimit(initial=10)
        self.assertTrue(lim.allow())
        lim.on_drop()
        self.assertAlmostEqual(lim.limit, 9.0)
        lim.allow()
        lim.on_success()
        self.assertAlmostEqual(lim.limit, 9 + 1 / 9)


class FailureLabSymptom(unittest.TestCase):
    def test_unbounded_queue_p99_explodes_and_goodput_collapses(self):
        s = bp.summary(simulate(bp.Server(), bp.BURST, bp.SERVICE_MS))
        self.assertEqual(s["shed"], 0)
        self.assertGreater(s["p99_ms"], 4000)
        self.assertLess(s["goodput"] / s["ok"], 0.5)  # most answers arrive after the client gave up


if __name__ == "__main__":
    unittest.main()
