"""Recomputes every number used in the L200 concept notes (content/concepts/L200/*.md).

python research/concept_examples_L200.py
"""
import math
import sys
from pathlib import Path

import numpy as np

LABS = Path(__file__).resolve().parents[1] / "labs" / "L200"
for lab in ("07-input-modelling", "08-multi-server-queue", "09-adaptive-ode", "10-warmup-replications",
            "11-supply-chain-inventory"):
    sys.path.insert(0, str(LABS / lab))

import adaptive_ode as ode  # noqa: E402
import fit_inputs as fi  # noqa: E402
import inventory as inv  # noqa: E402
import mmc_queue as mq  # noqa: E402
import warmup as wu  # noqa: E402

x = fi.load()
cv = x.std() / x.mean()
print(f"07: n={len(x)} cv={cv:.2f}; 1.36/sqrt(200)={1.36 / math.sqrt(200):.3f}; "
      + ", ".join(f"{f(x)['name']} D={fi.ks_statistic(x, f(x)['cdf']):.3f}" for f in fi.FITTERS))
print(f"07: P-K ratio exponential vs data = (1 + 1) / (1 + cv^2) = {2 / (1 + cv ** 2):.2f}")
e = mq.erlang_c()
print(f"08: a={mq.LAM / mq.MU}, c={mq.C}: P(wait)={e['P_wait']:.3f}, Wq={e['P_wait']:.3f}/({mq.C}*{mq.MU}-{mq.LAM})"
      f"={e['Wq']:.3f}, Lq=2.4*Wq={e['Lq']:.3f}; c=5 P(wait)={mq.erlang_c(5)['P_wait']:.3f}")
for err in (0.5, 4.0):
    print(f"09: error ratio e={err}: next h factor 0.9*e^-0.2 = {0.9 * err ** -0.2:.2f}")
ts, _, _ = ode.solve(ode.rc_filter, 0, [0.0], 10, rtol=1e-3, atol=1e-9)
print(f"09: RC explicit steps {len(ts) - 1}, mean h = {10 / (len(ts) - 1) * 1000:.2f} ms (tau = 1 ms)")
runs = np.array([wu.waits(5_000, seed) for seed in range(1, 21)])
sm = wu.welch(runs, 50)
print(f"10: Welch at 0/100/200: {sm[0]:.2f}/{sm[100]:.2f}/{sm[200]:.2f}; proposal {wu.warmup_point(sm)[0]}")
means = [wu.waits(5_000, s)[169:].mean() for s in range(201, 281)]
h10, h80 = wu.ci(means[:10])[1], wu.ci(means)[1]
print(f"10: half-width n=10 {h10:.2f}, n=80 {h80:.2f}, ratio {h10 / h80:.2f} vs sqrt(8)={math.sqrt(8):.2f}")
ca = np.array([inv.simulate(30, 80, *inv.streams(r))["cost_per_day"] for r in range(30)])
cb = np.array([inv.simulate(30, 90, *inv.streams(r))["cost_per_day"] for r in range(30)])
(_, hi), (_, hc) = inv.compare((30, 80), (30, 90), crn=False), inv.compare((30, 80), (30, 90))
print(f"11: corr(cost A, cost B) with CRN = {np.corrcoef(ca, cb)[0, 1]:.2f}; half-widths {hi:.2f} vs {hc:.2f}; "
      f"replications needed for the same width: (hi/hc)^2 = {(hi / hc) ** 2:.0f}x")
