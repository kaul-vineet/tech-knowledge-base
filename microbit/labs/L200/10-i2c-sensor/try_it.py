"""Try it (lab 10): run two code changes against the stub + SIMULATED TMP102.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import load_variant, serial  # noqa: E402
from i2c_devices import TMP102  # noqa: E402
import microbit  # noqa: E402


def try_1():
    # ADDR = 0x49 (ADD0 wired to V+ in the code) but the sensor answers at 0x48.
    mod = load_variant(HERE, "addr-0x49")
    microbit.i2c._attach(0x48, TMP102(21.5))
    with serial() as out:
        mod.step()
    return out.getvalue().strip()


def try_2():
    # Delete the two's-complement lines in decode_temp(); the sensor reads -25 C.
    mod = load_variant(HERE, "no-sign")
    microbit.i2c._attach(0x48, TMP102(-25))
    with serial() as out:
        mod.step()
    return out.getvalue().strip()


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
