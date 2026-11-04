"""Recomputes every number used in the L300 concept notes (content/concepts/L300/*.md).

python research/concept_examples_L300.py   (observed output: concept_examples_L300_observed.txt)
"""
import math
import sys
from pathlib import Path

import numpy as np

LABS = Path(__file__).resolve().parents[1] / "labs" / "L300"
for lab in ("12-variance-reduction", "13-calibration", "14-global-sensitivity", "15-cosimulation-fmi",
            "16-performance-scale"):
    sys.path.insert(0, str(LABS / lab))

import calibrate as cal  # noqa: E402
import cosim  # noqa: E402
import perf  # noqa: E402
import sensitivity as sa  # noqa: E402
import variance_reduction as vr  # noqa: E402

n = 20_000
base, anti, cv = vr.plain(n), vr.antithetic(n), vr.control_variate(n)
y, c = vr.overtime(np.random.default_rng(vr.SEED).random((n, vr.N_TASKS)))
r_yc = np.corrcoef(y, c)[0, 1]
print(f"12: exact {vr.exact_overtime():.4f}; antithetic rho {anti['rho']:+.2f} -> 1/(1+rho) = {1 / (1 + anti['rho']):.2f}, "
      f"measured {base['var_per_eval'] / anti['var_per_eval']:.2f}; corr(Y,C) {r_yc:.2f} -> 1/(1-r^2) = "
      f"{1 / (1 - r_yc ** 2):.2f}, measured {base['var_per_eval'] / cv['var_per_eval']:.2f}; "
      f"plain runs for the CV's precision: {n * base['var_per_eval'] / cv['var_per_eval']:,.0f}")
yo = cal.observed()
models = cal.candidates(cal.T_HOURS[cal.CAL], yo[cal.CAL])
same, hold = cal.scores(models, yo, cal.CAL), cal.scores(models, yo, ~cal.CAL)
print("13: same-data RMSE " + ", ".join(f"{k} {v:.3f}" for k, v in same.items())
      + "; holdout " + ", ".join(f"{k} {v:.3f}" for k, v in hold.items())
      + f"; poly-6 at 12 h {models['poly-6 (7 p)'][1](cal.T_HOURS[-1:])[0]:.2f} vs measured {yo[-1]:.2f}")
V = 16 ** 2 * 12 + 24 ** 2 + 40 ** 2 / 12 + 9 * 16 / 12
print(f"14: V = {V:.1f}; analytic ST window {24 ** 2 / V:.3f}, ST outdoor {(16 ** 2 * 12 + 24 ** 2) / V:.3f}, "
      f"S1 outdoor {16 ** 2 * 12 / V:.3f}, occupants {40 ** 2 / 12 / V:.3f}; runs N(d+2) = {8192 * 6:,}; "
      f"kept OAT {sa.variance_kept(['outdoor_C', 'occupants']):.3f}, ST {sa.variance_kept(['outdoor_C', 'window_open']):.3f}")
K = 0.5 * 3000 * 0.008
print(f"15: K = {K:.0f}; Jacobi bound tau ln(K/(K-1)) = {3600 * math.log(K / (K - 1)):.0f} s; Gauss-Seidel bound "
      f"tau ln((K+1)/(K-1)) = {3600 * math.log((K + 1) / (K - 1)):.0f} s; a = exp(-900/3600) = {math.exp(-0.25):.3f}; "
      f"900 s: {cosim.metrics(cosim.run(900))}")
print(f"16: SeedSequence collision bound for 10^6 streams ~ (2^20)^2 * 2^-128 = 2^{2 * 20 - 128}; "
      f"40 reps x 20,000 = {40 * 20_000:,} Lindley steps")
rng = np.random.default_rng(sa.SEED)
a, b = rng.random((4096, 4)), rng.random((4096, 4))
fa, fb = sa.energy(sa.scale(a)), sa.energy(sa.scale(b))
ab = a.copy()
ab[:, 3] = b[:, 3]
print(f"14: uncentred Saltelli S1 for lights_h at N=4,096: "
      f"{np.mean(fb * (sa.energy(sa.scale(ab)) - fa)) / np.var(np.r_[fa, fb]):.3f}")
