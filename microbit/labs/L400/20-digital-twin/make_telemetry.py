"""Regenerate the twin's input: gateway rows from lab 17's stub network (CPython, slow: ~1 min).

1,200 s, six sensors, solution.py from lab 17. True room: twin_model.room_temp + a fixed offset per
board + seeded noise, rounded to whole degrees like temperature(). Seeded drift from t = 600 s:
  n5  link loss ramps 0.15 -> 0.45 (a board slowly blocked by a metal cupboard / weak battery)
  n3  sensor bias ramps 0 -> +1.5 C (sunlight reaching the board)
Writes telemetry/classroom_seed20.csv (dev, seq, t_sensor, t_store, temp, light, motion).
"""
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "17-edge-to-cloud"))
import twin_model  # noqa: E402
import edge_sim  # noqa: E402  (lab 17, reused: the same network the twin models)
from store import to_csv  # noqa: E402

SEED, DURATION_S, DRIFT_S = 20, 1200, 600
OFFSETS = [0.4, -0.3, 0.2, 0.8, -0.5, 0.1]
LOSS = {"n1": 0.05, "n2": 0.05, "n3": 0.10, "n4": 0.10, "n5": 0.15, "n6": 0.15}
FIXTURE = HERE / "telemetry" / "classroom_seed20.csv"


def ramp(t_ms, start, end, amount):
    return 0.0 if t_ms < start * 1000 else amount * min(1.0, (t_ms / 1000 - start) / (end - start))


def loss_fn(a, b, t):
    dev = a if a.startswith("n") else b
    p = LOSS.get(dev, 0.1)
    return p + ramp(t, DRIFT_S, DURATION_S, 0.30) if dev == "n5" else p


def make_inputs(seed):
    rng = random.Random(seed)

    def inputs(i, t):
        true = twin_model.room_temp(t) + OFFSETS[i] + (ramp(t, DRIFT_S, DURATION_S, 1.5) if i == 2 else 0)
        return int(round(true + rng.gauss(0, 0.3))), (100 + 10 * i) % 256, False
    return inputs


def generate(duration_s=DURATION_S, seed=SEED):
    rows = []
    edge_sim.run("solution.py", seed=seed, readings=duration_s, drain_ms=3000, loss_fn=loss_fn,
                 inputs=make_inputs(seed), on_row=rows.append)
    return sorted(rows, key=lambda r: (r["dev"], r["seq"]))


if __name__ == "__main__":
    rows = generate()
    FIXTURE.write_text(to_csv(rows), encoding="utf-8")
    print("wrote", FIXTURE.name, len(rows), "rows")
