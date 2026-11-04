"""Try it (lab 14): two edits, each re-run through the budget model.

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import json
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from tryit import variant_source  # noqa: E402
import budget  # noqa: E402


def short(line):
    d = json.loads(line)
    return "%s: avg %s mA, life %s h, meets brief %s" % (d["design"], d["avg_ma"], d["life_h"], d["meets_brief"])


def try_1():
    # solution.py with MAX_MS = 100: deep sleep, but a fixed 100 ms rate.
    return short(budget.report("solution.py", source=variant_source(HERE, "fixed-100ms-deep-sleep")))


def try_2():
    # main.py with the optimistic chip-only awake current (7.9 mA instead of 30 mA).
    mod = types.ModuleType("budget_variant")
    mod.__file__ = budget.__file__
    exec(compile(variant_source(HERE, "chip-only-current"), budget.__file__, "exec"), mod.__dict__)
    return short(mod.report("main.py"))


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
