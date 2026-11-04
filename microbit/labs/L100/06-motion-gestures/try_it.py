"""Try it (lab 06): run two code changes against the stub and print what happens.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import load_variant, run_main, serial  # noqa: E402
import microbit  # noqa: E402


def try_1():
    # Change TILT_MG = 300 to 100; inject x = 200 mg.
    mod = load_variant(HERE, "tilt-100")
    microbit.accelerometer.inject_axes(x=200)
    with serial() as out:
        mod.step()
    return out.getvalue().strip()


def try_2():
    # Use is_gesture("shake") instead of was_gesture; one shake, then 3 polls.
    mod = load_variant(HERE, "is-gesture")
    microbit.accelerometer.inject_gesture("shake")
    with serial() as out:
        for _ in range(3):
            mod.step()
    return "'shake!' printed %d time(s) in 3 polls" % out.getvalue().count("shake!\n")


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())

