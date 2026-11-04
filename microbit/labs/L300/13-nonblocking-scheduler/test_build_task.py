"""Build task check (lab 13): cooperative scheduler, no sleep() in the loop.

Runs solution.py. To check YOUR version: BUILD_FILE=main.py python -m unittest test_build_task
(Windows PowerShell: $env:BUILD_FILE="main.py"; py -m unittest test_build_task)
main.py as shipped FAILS this check: that is the failureLab "before".
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
import tap_sim  # noqa: E402
import microbit  # noqa: E402

BUILD_FILE = os.environ.get("BUILD_FILE", "solution.py")


def events(out):
    return [json.loads(l) for l in out.splitlines() if '"event"' in l]


class Scheduler(unittest.TestCase):
    def test_every_quick_tap_counts(self):
        self.assertEqual(tap_sim.run_any(tap_sim.taps(), filename=BUILD_FILE), 8)

    def test_no_overruns_on_the_happy_path(self):
        state, sched, out = tap_sim.run_scheduler(tap_sim.taps(), filename=BUILD_FILE)
        self.assertEqual(sched["stats"], {"runs": 610, "overruns": 0, "missed": 0, "errors": 0})

    def test_long_press_still_clears(self):
        state, sched, out = tap_sim.run_scheduler([(500, 150), (1500, 3200)], until_ms=6000,
                                                  filename=BUILD_FILE)
        self.assertEqual([l for l in out.splitlines() if l.startswith(("tap", "clear"))],
                         ["tap 1", "clear"])

    def test_sensor_keeps_its_period(self):
        state, sched, out = tap_sim.run_scheduler([], until_ms=3001, filename=BUILD_FILE)
        rows = [json.loads(l) for l in out.splitlines() if l.startswith('{"t"') and "temp" in l]
        self.assertEqual([r["t"] for r in rows], [0, 1000, 2000, 3000])

    def test_overrun_is_logged(self):
        def slow(lab, sched):
            sched["tasks"][1]["fn"] = lambda s, now: microbit.sleep(300)
        state, sched, out = tap_sim.run_scheduler([], until_ms=1500, filename=BUILD_FILE, setup=slow)
        first = [e for e in events(out) if e["event"] == "overrun"][0]
        self.assertEqual(first, {"t": 0, "event": "overrun", "task": "sensor", "budget": 20, "ms": 300})

    def test_failing_task_leads_to_safe_state(self):
        def broken(lab, sched):
            def boom(s, now):
                raise OSError(19)                      # e.g. a sensor that stopped answering
            sched["tasks"][1]["fn"] = boom
        state, sched, out = tap_sim.run_scheduler([], until_ms=5000, filename=BUILD_FILE, setup=broken)
        kinds = [(e["event"], e["task"]) for e in events(out)]
        self.assertEqual(kinds, [("error", "sensor")] * 3 + [("safe_state", "sensor")])
        self.assertTrue(sched["safe"])
        self.assertEqual(microbit.pin0.digital_out, 0)
        self.assertEqual(microbit.display.current_image(), microbit.Image.NO)


if __name__ == "__main__":
    unittest.main(verbosity=2)
