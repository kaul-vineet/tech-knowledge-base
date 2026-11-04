import hashlib
import json
import unittest

import numpy as np

import make_feed
import twin


class TestFeed(unittest.TestCase):
    def test_committed_feed_is_the_seeded_generator_output(self):
        lines = [json.dumps(m) for m in make_feed.messages(make_feed.plant())]
        fresh = hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()
        self.assertEqual(fresh, hashlib.sha256(make_feed.FEED.read_bytes().replace(b"\r\n", b"\n")).hexdigest())

    def test_replay_drops_duplicate_and_late_messages_and_keeps_the_null(self):
        msgs, skipped = twin.read_feed()
        self.assertEqual(skipped, {"late_or_duplicate": 2, "null_reading": 1})
        self.assertTrue(all(a["t_min"] < b["t_min"] for a, b in zip(msgs, msgs[1:])))


class TestKalmanAndCusum(unittest.TestCase):
    def test_filter_converges_on_a_constant_noiseless_zone(self):
        tw = twin.Twin()
        tw.x = np.array([15.0, 0.0])
        for k in range(200):  # outdoor = zone = 20 C, heater off: the model says nothing changes
            tw.predict(20.0, 0)
            tw.update(k, 20.0, None, 20.0, 0)
        self.assertAlmostEqual(tw.x[0], 20.0, places=2)

    def test_tabular_cusum_by_hand(self):
        tw = twin.Twin(recalibrate=False)
        for z in (1.5, 1.5, 1.5):  # each step adds z - k = 1.0 to S_hi
            tw.drift_check(0, z)
        self.assertAlmostEqual(tw.s_hi, 3.0)
        self.assertEqual(tw.s_lo, 0.0)

    def test_refit_recovers_a_and_b_from_clean_data(self):
        tw, rng = twin.Twin(a=0.01, b=0.1), np.random.default_rng(0)
        temp = 20.0
        for _ in range(twin.WINDOW):
            out, heat = rng.uniform(0, 10), int(rng.integers(0, 2))
            new = temp + 0.035 * (out - temp) + 0.3 * heat
            tw.history.append((temp, out, heat, new))
            temp = new
        tw.refit(0)
        self.assertAlmostEqual(tw.a, 0.035, places=6)
        self.assertAlmostEqual(tw.b, 0.3, places=6)


class TestFailureLab(unittest.TestCase):
    """Fault: the shipped update() assimilates every reading. Your fix is checked by test_build_task.py."""

    def test_fault_glitch_causes_false_alarms_and_a_bad_refit(self):
        tw, errors = twin.run()
        alarms = [e["t_min"] for e in tw.events if e["event"] == "drift_alarm"]
        self.assertEqual(alarms[0], 1250)  # the 85.0 C glitch
        self.assertGreater(sum(t < 2500 for t in alarms), 0)
        self.assertGreater(twin.rmse(errors, 0, 2500), 1.0)


if __name__ == "__main__":
    unittest.main()
