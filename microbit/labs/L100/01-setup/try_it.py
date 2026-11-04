"""Try it (lab 01): run two code changes against the stub and print what happens.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import load_variant, run_main, serial  # noqa: E402
import microbit  # noqa: E402


def try_1():
    # Change sleep(1000) to sleep(250); run main() for 4 loop passes.
    mod = load_variant(HERE, "fast-tick")
    with serial() as out:
        run_main(mod, max_sleeps=4)
    return "%r, running_time()=%d ms" % (out.getvalue(), microbit.running_time())


def try_2():
    # Remove the __name__ guard (call main() directly); just import the file.
    with serial() as out:
        mod = load_variant(HERE, "no-guard", max_sleeps=3)
    return "import returned=%s, serial=%r" % (
        not getattr(mod, "stopped_on_import", False), out.getvalue())


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())

