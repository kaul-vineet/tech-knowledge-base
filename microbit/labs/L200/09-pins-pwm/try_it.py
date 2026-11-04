"""Try it (lab 09): run two code changes against the stub and print what happens.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import load_variant, serial  # noqa: E402
import microbit  # noqa: E402


def try_1():
    # Remove the edge detection (variant no-edge); hold the logo for 3 polls.
    mod = load_variant(HERE, "no-edge")
    state = mod.new_state()
    microbit.pin_logo.inject_touch(True)
    with serial() as out:
        for _ in range(3):
            mod.step(state)
    return " | ".join(out.getvalue().splitlines())


def try_2():
    # LEVELS = 3 instead of 4 (variant levels-3); turn on at the default level 2.
    mod = load_variant(HERE, "levels-3")
    state = mod.new_state()
    state["on"] = True
    with serial() as out:
        mod.step(state)
    return "%s | duty_for(0..3) = %s" % (out.getvalue().strip(), [mod.duty_for(l) for l in range(4)])


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
