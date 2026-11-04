"""Feed the gateway telemetry to a twin and score its drift check (prints JSON lines).

Fixture: telemetry/classroom_seed20.csv from make_telemetry.py (lab 17's stub network, 1,200 s).
Truth: n5's link and n3's sensor drift from t = 600 s (window 20); every other stream is nominal.
Synthetic: 1,000 nominal windows per stream drawn from the twin's own model (false-alarm rate).
"""
import csv
import importlib.util
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import twin_model  # noqa: E402

FIXTURE = HERE / "telemetry" / "classroom_seed20.csv"
DRIFTING = {("n5", "DRIFT_LAT"), ("n3", "DRIFT_TEMP")}
DRIFT_WINDOW = 20


def load_twin(filename):
    path = Path(filename) if Path(filename).is_absolute() else HERE / filename
    spec = importlib.util.spec_from_file_location("twin_" + path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Twin


def load_rows(path=FIXTURE):
    by = {}
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            row = dict((k, v if k == "dev" else int(v)) for k, v in r.items())
            by.setdefault(row["dev"], []).append(row)
    return by


def run(filename="solution.py", by=None):
    by = by or load_rows()
    params = twin_model.calibrate(by)
    twin = load_twin(filename)(params)
    wins = dict((d, twin_model.windows(rows)) for d, rows in by.items())
    m = {"twin": filename, "false_alarms": 0, "detected": {}, "params": params}
    for i in range(twin_model.CALIB_WINDOWS, max(len(w) for w in wins.values())):
        for dev in sorted(wins):
            if i < len(wins[dev]):
                for a in twin.update(dev, twin_model.observe(wins[dev][i])):
                    key = (dev, a["alarm"])
                    if key in DRIFTING and i >= DRIFT_WINDOW:
                        m["detected"].setdefault("%s %s" % key, i - DRIFT_WINDOW)
                    else:
                        m["false_alarms"] += 1
    return m, twin


def synthetic_false_alarms(filename="solution.py", windows=1000, seed=20, loss=0.10):
    """Nominal windows drawn from the twin's own model: any alarm is false."""
    rng = random.Random(seed)
    params = {"x": {"loss": loss, "offset": 0.0, "temp_sd": twin_model.QUANT_SD}}
    p = twin_model.stats_for(loss)[0]
    Twin, count = load_twin(filename), 0
    twin = Twin(params)
    for i in range(windows):
        share = sum(rng.random() < p for _ in range(twin_model.WINDOW)) / twin_model.WINDOW
        if twin.update("x", {"t": i, "lat": share, "resid": rng.gauss(0, twin_model.QUANT_SD)}):
            count += 1
            twin = Twin(params)               # restart after each alarm, so latching cannot hide a rate
    return count


def summary(filename):
    m, _ = run(filename)
    return {"twin": filename, "false_alarms_fixture": m["false_alarms"],
            "detected_after_windows": m["detected"],
            "false_alarms_per_1000_synthetic": synthetic_false_alarms(filename)}


if __name__ == "__main__":
    for f in ("twin.py", "solution.py"):
        print(json.dumps(summary(f), sort_keys=True))
