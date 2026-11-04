"""L300 reproducible pipeline: load -> detrend -> periodogram, with a step cache and a provenance log.

Every step run appends one JSON line to prov.jsonl (W3C PROV idea: activity, used entity + hash, generated
entity + hash, parameters, code version, cache hit/miss). A cache makes re-runs fast - and can make them WRONG.
python pipeline.py   (demo: v1 input, re-run, then the corrected v2 release replaces the file)
"""
import hashlib
import inspect
import json
import shutil
from pathlib import Path

import numpy as np

from periodogram import lomb_scargle

HERE = Path(__file__).resolve().parent
FREQ = np.linspace(0.05, 12.0, 60_000)  # cycles per day


def sha256(data):
    return hashlib.sha256(data if isinstance(data, bytes) else json.dumps(data, sort_keys=True).encode()).hexdigest()


def load(path):
    rows = Path(path).read_text(encoding="utf-8").splitlines()[1:]
    t, mag = zip(*[(float(r.split(",")[0]), float(r.split(",")[2])) for r in rows])
    return {"t": list(t), "mag": list(mag)}


def detrend(lc, window_nights=5):
    """Subtract a running median over +/- window_nights (removes slow drifts, keeps the 0.3 d pulsation)."""
    t, m = np.array(lc["t"]), np.array(lc["mag"])
    med = np.array([np.median(m[np.abs(t - x) <= window_nights]) for x in t])
    return {"t": lc["t"], "mag": (m - med).round(6).tolist()}


def best_period(lc):
    power = lomb_scargle(np.array(lc["t"]), np.array(lc["mag"]), FREQ)
    k = int(np.argmax(power))
    return {"period_d": round(float(1 / FREQ[k]), 5), "power": round(float(power[k]), 4)}


class Pipeline:
    def __init__(self, workdir):
        self.dir = Path(workdir)
        (self.dir / "cache").mkdir(parents=True, exist_ok=True)
        self.prov = self.dir / "prov.jsonl"

    def cache_key(self, step, input_path, upstream, params):
        """What identifies a result: step name, input file and parameters."""
        return sha256({"step": step.__name__, "input": Path(input_path).name, "params": params})

    def step(self, func, input_path, upstream, params):
        key = self.cache_key(func, input_path, upstream, params)
        cached = self.dir / "cache" / f"{key}.json"
        hit = cached.exists()
        out = json.loads(cached.read_text(encoding="utf-8")) if hit else func(upstream, **params)
        if not hit:
            cached.write_text(json.dumps(out), encoding="utf-8")
        record = {"activity": func.__name__, "used": {"entity": Path(input_path).name,
                                                       "sha256": sha256(Path(input_path).read_bytes())[:12]},
                  "upstream_sha256": sha256(upstream)[:12], "params": params, "code_sha256": sha256(inspect.getsource(func).encode())[:12],
                  "generated_sha256": sha256(out)[:12], "cache": "hit" if hit else "miss"}
        with self.prov.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return out

    def run(self, input_path, window_nights=5):
        lc = load(input_path)
        flat = self.step(detrend, input_path, lc, {"window_nights": window_nights})
        return self.step(best_period, input_path, flat, {})


def demo(workdir):
    shutil.rmtree(workdir, ignore_errors=True)
    p, current = Pipeline(workdir), Path(workdir) / "lightcurve.csv"
    shutil.copyfile(HERE / "data" / "lightcurve_v1.csv", current)
    first, again = p.run(current), p.run(current)
    shutil.copyfile(HERE / "data" / "lightcurve_v2.csv", current)  # the corrected release arrives
    return first, again, p.run(current)


if __name__ == "__main__":
    first, again, corrected = demo(HERE / "work")
    print("v1 input        :", first)
    print("v1 re-run       :", again)
    print("v2 (corrected)  :", corrected, "  <- true period 0.3011 d")
    print((HERE / "work" / "prov.jsonl").read_text(encoding="utf-8").rstrip())
