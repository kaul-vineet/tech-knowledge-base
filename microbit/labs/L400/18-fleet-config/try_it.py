"""Try it (lab 18): two edits to solution.py, staged rollout of v2 (good) then v3 (bad group).

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fleet_sim  # noqa: E402
from tryit import variant_source  # noqa: E402


def run_variant(name, loss):
    src = variant_source(str(HERE), name)
    m, _ = fleet_sim.run("solution.py", "staged", loss=loss, sources=dict((d, src) for d in fleet_sim.DEVICES))
    return json.loads(fleet_sim.line("solution.py", "staged", m))


def summary(r):
    return "jobs: %s | final versions %s | unacked_ticks %d" % (r["jobs"], r["final"], r["unacked_ticks"])


def try_1():
    # The device sends A once after a commit instead of every 500 ms of probation (10 % loss).
    return summary(run_variant("no-repeat-report", 0.10))


def try_2():
    # Probation 300 ms instead of 3 s, on a worse link (30 % loss).
    return summary(run_variant("probation-300", 0.30))


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
