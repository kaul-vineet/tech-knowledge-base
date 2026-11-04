"""Lab 21 basics: firmware alarm hysteresis, gateway rules, the frozen record."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import solution  # noqa: E402,F401  (load our solution.py first)
import alarms  # noqa: E402
from labtest import load_lab  # noqa: E402


def snap(temps, twin=(), auth=None):
    return {"devices": [{"dev": "n4", "label": "Bench 4", "temps": temps, "readings": 3}],
            "twin_alarms": list(twin), "auth": auth or {}}


class Rules(unittest.TestCase):
    def test_firmware_alarm_hysteresis(self):
        fw = load_lab(str(HERE), "firmware_alarm.py")
        seq, hot = [], False
        for c in (29, 30, 29, 28, 27, 30):
            hot = fw.check(hot, c)
            seq.append(hot)
        self.assertEqual(seq, [False, True, True, True, False, True])

    def test_gateway_rules_match_the_firmware(self):
        self.assertEqual(alarms.decide(snap([25, 31]))[0]["name"], "TEMP_HIGH")
        prev = alarms.decide(snap([31]))
        self.assertTrue(alarms.decide(snap([29]), prev))         # still raised: above 28
        self.assertFalse(alarms.decide(snap([27]), prev))        # cleared by CODE below 28
        a = alarms.decide(snap([22], twin=[{"dev": "n5", "alarm": "DRIFT_LAT", "z": 3.5}], auth={"mac": 2}))
        self.assertEqual([x["name"] for x in a], ["AUTH_REJECTS", "DRIFT_LAT"])

    def test_frozen_record_has_a_stable_digest(self):
        a = alarms.decide(snap([31]))
        self.assertEqual(alarms.freeze(a), alarms.freeze([dict(x) for x in a]))
        self.assertNotEqual(alarms.freeze(a)[1], alarms.freeze([])[1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
