"""Try it (lab 12): two edits to solution.py, run on two stub boards over the
seeded faulty radio (20% loss, 10% dup, 10% reorder, 5% corrupt, seed 12).

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import variant_source  # noqa: E402
import link_sim  # noqa: E402


def run_variant(name):
    src = variant_source(HERE, name)
    res = link_sim.run("solution.py", faults=link_sim.FAULTS, sources={"A": src, "B": src})
    st = res["a"]
    return "%s | sender retx %d gave_up %d | receiver gap %d" % (
        link_sim.summary(res), st["retx"], st["gave_up"], res["b"]["gap"])


def try_1():
    # Delete the duplicate check: every retransmitted copy is delivered again.
    return run_variant("no-dedupe")


def try_2():
    # MAX_TRIES = 2: the sender gives up sooner; the receiver reports the hole.
    return run_variant("max-tries-2")


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
