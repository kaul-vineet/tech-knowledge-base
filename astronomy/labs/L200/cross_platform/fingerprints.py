"""Seeded results of every L200 lab and build-task solution, at the precision the lab READMEs print.

CI runs test_fingerprints.py on Linux, macOS (Apple silicon) and Windows: all three must reproduce golden.json.
python fingerprints.py [--write]
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LABS = {"07": "07-crossmatch", "08": "08-fits-wcs", "09": "09-aperture-photometry", "10": "10-light-curves", "11": "11-nbody"}
GOLDEN = HERE / "golden.json"


def load(lab, rel):
    folder = HERE.parent / LABS[lab]
    sys.path.insert(0, str(folder))
    spec = importlib.util.spec_from_file_location(f"m{lab}_{Path(rel).stem}_{len(rel)}", folder / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def compute():
    cm = load("07", "solution/crossmatch.py")
    a, b, truth = cm.make_catalogues()
    idx, sep, ev = cm.match(a, b)
    one, _ = cm.match_one_to_one(a, b)
    fl = load("08", "solution/fitslite.py")
    ra, dec = fl.pixel_to_sky(fl.WCS, 1, 1)
    ph = load("09", "solution/photometry.py")
    res = [ph.measure(ph.make_image(), x, y) for x, y, _ in ph.STARS]
    pr = load("10", "periods.py")
    t = pr.sample_times()
    var = pr.analyse(t, pr.variable_star(t))
    nb = load("11", "solution/nbody.py")
    _, _, drift, _ = nb.run(nb.step_leapfrog, years=2.0, dt=0.001)
    return {
        "07 matched / correct / evaluations / one-to-one": [int(np.sum(idx >= 0)), int(np.sum(idx[:len(truth)] == truth)), int(ev), int(np.sum(one >= 0))],
        "08 pixel (1,1) RA / Dec": [f"{float(ra):.6f}", f"{float(dec):+.6f}"],
        "09 net / SNR": [[f"{r['net']:.1f}", f"{r['snr']:.1f}"] for r in res],
        "10 variable best period / power": [f"{var['best_period_days']:.4f}", f"{var['power']:.3f}"],
        "11 leapfrog |dE/E| 2 yr below 1e-9": bool(drift < 1e-9),
    }


if __name__ == "__main__":
    result = compute()
    if "--write" in sys.argv:
        GOLDEN.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))
