"""Try it (lab 13): two edits to solution.py, same 8 seeded quick taps as the failureLab.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import variant_source  # noqa: E402
import tap_sim  # noqa: E402


def run_variant(name):
    state, sched, out = tap_sim.run_scheduler(tap_sim.taps(), source=variant_source(HERE, name))
    events = [json.loads(l) for l in out.splitlines() if '"event"' in l]
    kinds = sorted(set(e["event"] for e in events))
    return "counted %d of 8 | stats %s | events %s" % (state["taps"], sched["stats"], kinds or "none")


def try_1():
    # Poll the button every 200 ms instead of 20 ms (taps last 150 ms).
    return run_variant("button-200ms")


def try_2():
    # A task that blocks: sleep(300) inside read_sensor().
    return run_variant("slow-sensor")


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
