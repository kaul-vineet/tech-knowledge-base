"""SALib equivalent (pending-ci): the same Sobol' and Morris analysis with SALib 1.6.0 (pip install SALib==1.6.0).

API checked against the SALib 'Concise API Reference' (sample.sobol.sample, analyze.sobol.analyze,
sample.morris.sample, analyze.morris.analyze). python sensitivity_salib.py
"""
import numpy as np
from SALib.analyze import morris as morris_analyze
from SALib.analyze import sobol as sobol_analyze
from SALib.sample import morris as morris_sample
from SALib.sample import sobol as sobol_sample

import sensitivity as sa

PROBLEM = {"num_vars": len(sa.NAMES), "names": sa.NAMES, "bounds": np.c_[sa.LOW, sa.HIGH].tolist()}


def sobol_indices(n=8192):
    x = sobol_sample.sample(PROBLEM, n, calc_second_order=False, seed=sa.SEED)  # N*(D+2) rows, scrambled Sobol'
    return sobol_analyze.analyze(PROBLEM, sa.energy(x), calc_second_order=False, seed=sa.SEED)


def morris_indices(r=20):
    x = morris_sample.sample(PROBLEM, r, num_levels=4, seed=sa.SEED)
    return morris_analyze.analyze(PROBLEM, x, sa.energy(x), num_levels=4, seed=sa.SEED)


if __name__ == "__main__":
    si, mo = sobol_indices(), morris_indices()
    for i, name in enumerate(sa.NAMES):
        print(f"{name:12s} SALib S1 {si['S1'][i]:6.3f}  ST {si['ST'][i]:6.3f} +/- {si['ST_conf'][i]:.3f}   "
              f"Morris mu* {mo['mu_star'][i]:7.1f}  sigma {mo['sigma'][i]:7.1f}")
