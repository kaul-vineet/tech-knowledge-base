"""Try it (lab 17): two edits to solution.py, each run with 24 sensors (10% loss per link, seed 17).

Run:  python try_it.py    (asserted by test_try_it.py)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edge_sim  # noqa: E402
from tryit import variant_source  # noqa: E402  (labs/sim_stub, on sys.path via edge_sim)

N = 24
NAMES = ["n%d" % (i + 1) for i in range(N)] + ["relay"]


def run_variant(name):
    src = variant_source(str(HERE), name)
    res, _ = edge_sim.run("solution.py", n=N, loss={k: 0.10 for k in NAMES[:-1]}, readings=20,
                          sources={k: src for k in NAMES})
    return "delivered {stored}/{sampled} ({delivery_pct}%), p95 {p95_ms} ms, gave_up {gave_up}, " \
           "relay drops {relay_queue_drops}, sensor drops {sensor_queue_drops}".format(**res)


def try_1():
    # Keep the jitter, go back to the default 3-frame queue.
    return run_variant("queue-3")


def try_2():
    # Keep the 12-frame queue, remove the random phase and the timeout jitter.
    return run_variant("no-jitter")


if __name__ == "__main__":
    print("try 1:", try_1())
    print("try 2:", try_2())
