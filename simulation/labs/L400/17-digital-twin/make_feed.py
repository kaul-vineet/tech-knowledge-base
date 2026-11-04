"""Writes sensor_feed.jsonl: 3 days of 5-minute readings from one office zone (the "real" building), seeded.

The plant is a first-order thermal zone with a thermostat. Faults a real feed has are planted on purpose:
a sensor glitch (85.0 C), a missing reading (null), a duplicate, an out-of-order message - and a physical
DRIFT: from step 500 a window is left ajar, so the zone loses heat faster (a: 0.020 -> 0.035 per step).
python make_feed.py      (the committed feed is this script's output; test_twin.py checks the bytes match)
"""
import json
import math
from pathlib import Path

import numpy as np

FEED = Path(__file__).with_name("sensor_feed.jsonl")
STEPS, DT_MIN, SEED = 864, 5, 17  # 3 days of 5-minute steps
A_TRUE, A_DRIFT, B_TRUE, DRIFT_AT = 0.020, 0.035, 0.30, 500
GLITCH_AT, MISSING_AT, DUPLICATE_AT, LATE_AT = 250, 300, 310, 620


def outdoor(k, rng_noise):
    hour = (k * DT_MIN / 60) % 24
    return 5.0 + 4.0 * math.sin(2 * math.pi * (hour - 9) / 24) + rng_noise


def plant(seed=SEED):
    """The real zone: returns rows (t_min, outdoor_C, heater_on, true_C, measured_C)."""
    rng = np.random.default_rng(seed)
    temp, heater, rows = 20.0, 0, []
    for k in range(STEPS):
        t_out = outdoor(k, rng.normal(0, 0.3))
        hour = (k * DT_MIN / 60) % 24
        setpoint = 21.0 if 7 <= hour < 19 else 17.0  # occupied hours
        heater = 1 if temp < setpoint - 0.5 else 0 if temp > setpoint + 0.5 else heater  # thermostat, hysteresis
        rows.append((k * DT_MIN, round(t_out, 2), heater, temp, round(temp + rng.normal(0, 0.15), 2)))
        a = A_DRIFT if k >= DRIFT_AT else A_TRUE
        temp = temp + a * (t_out - temp) + B_TRUE * heater + rng.normal(0, 0.03)
    return rows


def messages(rows):
    out = []
    for k, (t, t_out, heater, _, meas) in enumerate(rows):
        msg = {"t_min": t, "outdoor_C": t_out, "heater_on": heater, "zone_C": meas}
        if k == GLITCH_AT:
            msg["zone_C"] = 85.0  # sensor glitch
        if k == MISSING_AT:
            msg["zone_C"] = None  # dropped reading
        out.append(msg)
        if k == DUPLICATE_AT:
            out.append(dict(msg))  # the gateway re-sent a message
    late = out.pop(LATE_AT + 1)
    out.insert(LATE_AT + 3, late)  # one message arrives two places late
    return out


if __name__ == "__main__":
    lines = [json.dumps(m) for m in messages(plant())]
    FEED.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {len(lines)} lines to {FEED.name} (drift from t_min {DRIFT_AT * DT_MIN})")
