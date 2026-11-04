"""Try it (lab 03): run two code changes against the stub and print what happens.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import load_variant, run_main, serial  # noqa: E402
import microbit  # noqa: E402


def try_1():
    # Count with was_pressed() instead of get_presses() (slow 3 s loop);
    # click A three times between two polls.
    mod = load_variant(HERE, "count-with-was-pressed")
    microbit.button_a.click(times=3)
    with serial() as out:
        count = mod.step(0)
    return "count=%d, serial=%r" % (count, out.getvalue())


def try_2():
    # Count with is_pressed(): 3 quick clicks between polls, then hold A for 3 polls.
    mod = load_variant(HERE, "count-with-is-pressed")
    microbit.button_a.click(times=3)
    with serial() as out:
        count = mod.step(0)
    clicks = "after 3 clicks: count=%d serial=%r" % (count, out.getvalue())
    microbit.button_a.press()
    with serial() as out:
        for _ in range(3):
            count = mod.step(count)
    return clicks + "; held for 3 polls: count=%d serial=%r" % (count, out.getvalue())


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())

