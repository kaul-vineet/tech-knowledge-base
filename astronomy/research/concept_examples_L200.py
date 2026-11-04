"""Recompute every number quoted in the L200 concept notes (run: python concept_examples_L200.py)."""
import importlib.util
import sys
from pathlib import Path

import numpy as np

LABS = Path(__file__).resolve().parents[1] / "labs" / "L200"


def load(folder, rel):
    sys.path.insert(0, str(LABS / folder))
    spec = importlib.util.spec_from_file_location(f"{folder}_{rel}".replace("/", "_").replace("-", "_")[:-3], LABS / folder / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


cm = load("07-crossmatch", "solution/crossmatch.py")
a, b, truth = cm.make_catalogues()
idx, sep, ev = cm.match(a, b)
one, _ = cm.match_one_to_one(a, b)
print(f"07 evals {ev:,} vs {len(a[0]) * len(b[0]):,} = {len(a[0]) * len(b[0]) / ev:.0f}x; correct {int(np.sum(idx[:len(truth)] == truth))}; "
      f"median {np.nanmedian(sep):.3f}; twice {int(np.sum(np.bincount(idx[idx >= 0]) > 1))}; one-to-one {int(np.sum(one >= 0))} kept {int(np.sum(one[:len(truth)] == truth))}; "
      f"wrap {float(cm.angular_sep(359.9999, 28, 0.0001, 28)) * 3600:.4f}")
fl = load("08-fits-wcs", "solution/fitslite.py")
cards = 16 + 1
print(f"08 header {cards * 80} -> {-(-cards * 80 // 2880) * 2880} bytes; data {64 * 64 * 4} -> {-(-64 * 64 * 4 // 2880) * 2880}; "
      f"pixel(1,1) {tuple(round(float(v), 6) for v in fl.pixel_to_sky(fl.WCS, 1, 1))}")
ph = load("09-aperture-photometry", "solution/photometry.py")
img = ph.make_image()
r0, r3 = ph.measure(img, 30, 30), ph.measure(img, 30, 72)
print(f"09 star0 {r0['net']:.1f} SNR {r0['snr']:.1f} sigma_m {1.0857 / r0['snr']:.3f}; star3 {r3['net']:.1f} SNR {r3['snr']:.1f}; "
      f"star3 r=3 SNR {ph.measure(img, 30, 72, r=3.0)['snr']:.1f}")
pr = load("10-light-curves", "periods.py")
t = pr.sample_times()
v, tr = pr.analyse(t, pr.variable_star(t)), pr.analyse(t, pr.transit_star(t))
print(f"10 n {t.size}; var {v['best_period_days']:.4f} p {v['power']:.3f} next {v['second_period_days']:.4f} alias {1 / (1 / pr.P_VAR - 1):.4f}; "
      f"transit {tr['best_period_days']:.4f} p {tr['power']:.3f} skew {tr['skew']:+.2f}")
nb = load("11-nbody", "nbody.py")
for name, step in (("Euler", nb.step_euler), ("leapfrog", nb.step_leapfrog)):
    pos, _, drift, com = nb.run(step)
    print(f"11 {name}: dE/E {drift:.2e} r {np.linalg.norm(pos[1] - pos[0]):.5f} com {com:.4f}")
