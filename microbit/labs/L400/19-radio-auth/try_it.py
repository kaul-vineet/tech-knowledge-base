"""Try it (lab 19): two edits to solution.py, run against the seeded attack scenario (SipHash mode).

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import attacks  # noqa: E402
from tryit import variant_source  # noqa: E402


def run_variant(name):
    with tempfile.TemporaryDirectory(dir=HERE) as d:  # private copy: parallel runs cannot collide
        tmp = Path(d) / ("tryit_%s.py" % name.replace("-", "_"))
        tmp.write_text(variant_source(str(HERE), name), encoding="utf-8")
        m, _ = attacks.run(str(tmp), "siphash")
    return "genuine accepted %(genuine_accepted)d of %(genuine_intact)d intact, forged accepted " \
           "%(forged_accepted)d, replays accepted %(replays_accepted)d" % m


def try_1():
    # WINDOW = 1: only a counter higher than every earlier one is accepted.
    return run_variant("window-1")


def try_2():
    # Check the replay window BEFORE the MAC: a forged frame can now move the window.
    return run_variant("replay-check-first")


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
