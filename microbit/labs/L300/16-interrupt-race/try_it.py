"""Try it (lab 16): two edits to the host model (the Rust code is pending-ci).

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import variant_source  # noqa: E402
import host_sim  # noqa: E402
import race_model  # noqa: E402


def load(name, filename):
    mod = types.ModuleType(name)
    mod.__file__ = os.path.join(HERE, filename)
    exec(compile(variant_source(HERE, name), mod.__file__, "exec"), mod.__dict__)
    return mod


def line(m):
    return "irqs %d, isr runs %d, consumed %d, pending %d, lost %d" % (
        m.irqs, m.isr_total, m.consumed, m.pending, m.lost())


def try_1():
    # Shorter work window: delay(200) instead of delay(2_000) -> p_window 0.03.
    sim = load("short-window", "host_sim.py")
    return "racy, short window: " + line(sim.soak(race_model.take))


def try_2():
    # Fixed take(), but the critical section is longer than one timer period.
    fixed = load("long-section", "solution_model.py")
    return "fixed, long section: " + line(host_sim.soak(fixed.take))


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
