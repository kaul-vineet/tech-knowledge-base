"""Failure lab: local wall clock relabelled as UTC before the sky maths. Reproducible by flag; fixed path stays clean."""
import re
import subprocess
import sys
import unittest

from tests import _lab

import scheduler  # noqa: E402
import sky  # noqa: E402
import validator  # noqa: E402


class LocalAsUtc(unittest.TestCase):
    def test_fault_shifts_sky_time_by_the_utc_offset(self):
        slot = sky.night_slots()[0]
        bad = sky.sky_instant(slot, "local-as-utc")
        self.assertEqual((bad.dt - slot.utc.dt).total_seconds() / 60, 330)

    def test_fault_schedules_a_target_below_the_horizon_that_the_validator_catches(self):
        r = scheduler.build(fault="local-as-utc")
        self.assertLessEqual(max(x["max_airmass"] for x in r["greedy_rows"]), sky.MAX_AIRMASS)  # looks fine inside
        out = validator.validate(validator.rows_from_blocks(r["greedy"], r["reqs"], r["slots"]))
        self.assertTrue(any("Betelgeuse: altitude -16.4 deg" in v for v in out), out)

    def test_run_project_exits_nonzero_with_the_fault(self):
        p = subprocess.run([sys.executable, str(_lab.LAB / "run_project.py"), "--inject", "local-as-utc"],
                           capture_output=True, text=True, encoding="utf-8", cwd=str(_lab.LAB))
        self.assertEqual(p.returncode, 1)
        self.assertIn('"check": "SEAM time astronomy<->scheduler", "pass": false', p.stdout)

    def test_no_relabelling_to_utc_outside_the_marked_fault(self):
        """replace(tzinfo=UTC) relabels a clock; only the deliberately injected line may do it."""
        for f in ("timeutil.py", "sky.py", "scheduler.py", "validator.py", "agent_plan.py", "solution/plan_times.py"):
            for line in (_lab.LAB / f).read_text(encoding="utf-8").splitlines():
                if re.search(r"replace\(tzinfo=(UTC|timezone\.utc)\)", line):
                    self.assertIn("# the bug", line, f)


if __name__ == "__main__":
    unittest.main()
