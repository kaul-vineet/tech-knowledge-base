"""Build task: parse agent-written times at the seam. Default checks solution/plan_times.py;
BUILD_TARGET=mine checks the shipped plan_times.py (unfixed: 3 of 5 tests fail)."""
import importlib.util
import os
import unittest

from tests import _lab

TARGET = _lab.LAB / ("plan_times.py" if os.environ.get("BUILD_TARGET") == "mine" else "solution/plan_times.py")
_spec = importlib.util.spec_from_file_location("plan_times_under_test", TARGET)
pt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pt)

import validator  # noqa: E402


class ParsePlanTime(unittest.TestCase):
    def test_z_time(self):
        self.assertEqual(pt.parse_plan_time("2026-11-19T13:20:00Z").iso(), "2026-11-19T13:20:00Z")

    def test_offset_time_is_converted(self):
        self.assertEqual(pt.parse_plan_time("2026-11-19T18:50:00+05:30").iso(), "2026-11-19T13:20:00Z")

    def test_naive_time_is_refused(self):
        with self.assertRaises(ValueError):
            pt.parse_plan_time("2026-11-19T18:50")

    def test_bare_clock_time_is_refused(self):
        with self.assertRaises(ValueError):
            pt.parse_plan_time("18:50")

    def test_valid_plan_written_in_local_time_passes_the_validator(self):
        r = _lab.night()
        rows = [{"target": x["target"], "start": pt.parse_plan_time(f"2026-11-{x['start_utc'][8:10]}T"
                                                                     f"{x['start_utc'][11:16]}:00+00:00")}
                for x in r["local_rows"]]
        local = [{"target": "Vega", "start": pt.parse_plan_time("2026-11-19T18:50:00+05:30")}]
        self.assertEqual(validator.validate(rows), [])
        self.assertEqual(validator.validate(local), [])


if __name__ == "__main__":
    unittest.main()
