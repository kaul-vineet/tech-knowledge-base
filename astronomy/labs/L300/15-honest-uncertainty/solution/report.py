"""Stretch solution (lesson 15): report MCMC results honestly - percentiles, and a flag where +/- is asymmetric.

A parameter whose 84th-50th and 50th-16th percentile distances differ by more than 15% is not Gaussian:
quote 'median +plus -minus', never a single +/- sigma. python solution/report.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mcmc  # noqa: E402
import transit_fit as tf  # noqa: E402


def summarise(post, names):
    out = []
    for k, name in enumerate(names):
        lo, med, hi = np.percentile(post[:, k], [15.87, 50, 84.13])
        minus, plus = med - lo, hi - med
        asym = abs(plus - minus) / ((plus + minus) / 2)
        out.append({"param": name, "median": round(float(med), 5), "plus": round(float(plus), 5),
                    "minus": round(float(minus), 5), "gaussian": bool(asym <= 0.15)})
    return out


if __name__ == "__main__":
    post, _, _ = mcmc.run(tf.make_data())
    for row in summarise(post[:, :4], tf.NAMES):
        print(json.dumps(row))
