"""Same fits and KS statistics with SciPy 1.18.1 scipy.stats (pending-ci: SciPy is not installed in the sandbox).

python fit_scipy.py
"""
from importlib.metadata import version

from scipy import stats

import fit_inputs as fi


def fit_all(x):
    """{name: (fitted parameters, KS D)} - floc=0 pins the location so the fits match the numpy lab."""
    out = {}
    scale = stats.expon.fit(x, floc=0)[1]
    out["exponential"] = ({"rate": 1 / scale}, stats.kstest(x, "expon", args=(0, scale)).statistic)
    mu, sd = stats.norm.fit(x)  # MLE: same mean and ddof=0 sd as the numpy lab
    out["normal"] = ({"mu": mu, "sigma": sd}, stats.kstest(x, "norm", args=(mu, sd)).statistic)
    s, _, sc = stats.lognorm.fit(x, floc=0)  # lognorm: shape s = sigma, scale = exp(mu)
    out["lognormal"] = ({"sigma": s, "scale": sc}, stats.kstest(x, "lognorm", args=(s, 0, sc)).statistic)
    return out


if __name__ == "__main__":
    print(f"SciPy {version('scipy')}")
    for name, (params, d) in fit_all(fi.load()).items():
        print(f"{name:12} " + " ".join(f"{k}={v:.3f}" for k, v in params.items()) + f"  KS D={d:.3f}")
