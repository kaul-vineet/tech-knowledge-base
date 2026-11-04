"""Try it (lab 05): run two code changes against the stub and print what happens.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import load_variant, run_main, serial  # noqa: E402
import microbit  # noqa: E402


def try_1():
    # Change HOT_C = 26 to 28; inject 27 C and light 128.
    mod = load_variant(HERE, "hot-28")
    microbit._inject_temperature(27)
    microbit.display.inject_light_level(128)
    with serial() as out:
        mod.step()
    return out.getvalue().strip()


def try_2():
    # Check hot before dark in classify(); inject 30 C and light 10.
    mod = load_variant(HERE, "hot-first")
    microbit._inject_temperature(30)
    microbit.display.inject_light_level(10)
    with serial() as out:
        mod.step()
    return out.getvalue().strip()


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())

