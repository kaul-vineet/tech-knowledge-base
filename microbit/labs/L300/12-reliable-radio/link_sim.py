"""Run a lab version on two stub boards over a seeded faulty radio (CPython only).

Board A sends N readings ("r1".."rN", one every SEND_EVERY_MS through the lab's
send()); both boards run step() every 10 ms. Returns what board B delivered plus
the counters, so tests and try_it.py can compare BEFORE (main.py) and AFTER.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "sim_stub"))
from labtest import load_boards, serial  # noqa: E402
import radio  # noqa: E402

FAULTS = dict(loss=0.2, dup=0.1, reorder=0.1, corrupt=0.05, seed=12)   # the failureLab
SEND_EVERY_MS = 50


def run(filename="main.py", n=20, faults=None, run_ms=6000, sources=None):
    air = radio.Air(**(faults or {}))
    a, b = load_boards(HERE, filename=filename, sources=sources, air=air)
    sa, sb = a.lab.new_state(), b.lab.new_state()
    with serial() as out:
        for t in range(0, run_ms, 10):
            if t % SEND_EVERY_MS == 0 and t // SEND_EVERY_MS < n:
                a.lab.send(sa, "r%d" % (t // SEND_EVERY_MS + 1))
            a.lab.step(sa)
            b.lab.step(sb)
            a.mb.sleep(10)
            b.mb.sleep(10)
        last = (a.lab.jline(a.mb.running_time(), sa["stats"]),
                b.lab.jline(b.mb.running_time(), sb["stats"]))
    return {"delivered": sb["delivered"], "a": sa["stats"], "b": sb["stats"],
            "faults": dict(air.faults), "json": last, "serial": out.getvalue()}


def summary(res, n=20):
    want = ["r%d" % i for i in range(1, n + 1)]
    got = res["delivered"]
    missing = [x for x in want if x not in got]
    dups = len(got) - len(set(got))
    return "delivered %d/%d, missing %s, duplicates %d, in order %s" % (
        len(set(got)), n, missing or "none", dups, got == sorted(set(got), key=want.index))


if __name__ == "__main__":
    for name in ("main.py", "solution.py"):
        for label, f in (("quiet", None), ("faulty", FAULTS)):
            r = run(name, faults=f)
            print("%-11s %-6s %s" % (name, label, summary(r)))
            print("  air", r["faults"])
            print("  A", r["json"][0])
            print("  B", r["json"][1])
