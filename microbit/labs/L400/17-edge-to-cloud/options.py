"""Lab 17 design options, measured on the stub network (prints one JSON line per option).

A  direct serial: every board on its own USB cable to the PC (no radio)
B  radio relay -> one serial gateway, as shipped (node.py) and after the build task (solution.py)
C  BLE: not measurable here - micro:bit MicroPython V2 implements only BLE flashing (docs, ble.html)
Run:  python options.py      (Windows: py options.py)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edge_sim  # noqa: E402

DIRECT = ("        state[\"queue\"].append(sample(now))\n",
          "        state[\"seq\"] += 1                                         # option A: own USB cable\n"
          "        forward(state, state[\"dev\"], state[\"seq\"], sample(now))\n")


def direct_serial(n=6):
    src = (HERE / "solution.py").read_text(encoding="utf-8")
    assert src.count(DIRECT[0]) == 1
    src = src.replace(*DIRECT)
    names = ["n%d" % (i + 1) for i in range(n)] + ["relay"]
    res, _ = edge_sim.run("solution.py", n=n, sources={k: src for k in names})
    return dict(res, option="A direct serial", usb_cables=n)


def options():
    rows = [direct_serial()]
    for f in ("node.py", "solution.py"):
        res, _ = edge_sim.run(f)
        rows.append(dict(res, option="B radio relay (%s)" % f, usb_cables=1))
    rows.append({"option": "C BLE", "measured": False,
                 "why": "micro:bit MicroPython V2: only BLE flashing is implemented; no BLE API for user code"})
    return rows


if __name__ == "__main__":
    for row in options():
        print(json.dumps(row))
