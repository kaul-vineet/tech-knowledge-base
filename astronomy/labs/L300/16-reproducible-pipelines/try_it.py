"""tryIt for lesson 16 (temporary folders; nothing is left behind).
1. Shipped cache, v2 input: change detrend's window from 5 to 1 night. Which steps re-run?
2. Fixed cache: change the module-level frequency grid FREQ (not a parameter!) and re-run. Hit or miss?
"""
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

import numpy as np

import pipeline

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pipeline_fixed", HERE / "solution" / "pipeline.py")
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)


def caches(prov):
    return [json.loads(line)["cache"] for line in prov.read_text(encoding="utf-8").splitlines()]


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        p, src = pipeline.Pipeline(tmp), Path(tmp) / "lightcurve.csv"
        shutil.copyfile(HERE / "data" / "lightcurve_v2.csv", src)
        a, b = p.run(src, window_nights=5), p.run(src, window_nights=1)
        print(f"1. shipped: window 5 -> {a}; window 1 -> {b}; cache {caches(p.prov)}")
    with tempfile.TemporaryDirectory() as tmp:
        p, src = fixed.Pipeline(tmp), Path(tmp) / "lightcurve.csv"
        shutil.copyfile(HERE / "data" / "lightcurve_v2.csv", src)
        a = p.run(src)
        fixed.FREQ = np.linspace(0.05, 3.0, 5_000)  # a grid that cannot even reach 3.32 c/d
        b = p.run(src)
        print(f"2. fixed, FREQ changed: before {a}; after {b}; cache {caches(p.prov)}")
