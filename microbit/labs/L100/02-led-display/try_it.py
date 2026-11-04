"""Try it (lab 02): run two code changes against the stub and print what happens.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import load_variant, run_main, serial  # noqa: E402
import microbit  # noqa: E402


def _stats(img):
    px = [img.get_pixel(x, y) for y in range(5) for x in range(5)]
    return "lit=%d, sum=%d, centre=%d" % (sum(1 for v in px if v), sum(px), img.get_pixel(2, 2))


def try_1():
    # Change the DIAMOND centre row "95159" to "95959".
    return _stats(load_variant(HERE, "bright-centre").DIAMOND)


def try_2():
    # Change % 10 to % 5 in step(); call step() 7 times from level 0.
    mod = load_variant(HERE, "ramp-mod5")
    level = 0
    with serial() as out:
        for _ in range(7):
            level = mod.step(level)
    return " ".join(line.split()[1] for line in out.getvalue().splitlines())


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())

