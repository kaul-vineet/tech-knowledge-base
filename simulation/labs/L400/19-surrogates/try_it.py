"""tryIt experiments for lesson 19 (run: python try_it.py)."""
import numpy as np

import surrogate as sg

mmc_queue = sg.mmc_queue  # the L200 lesson 8 model, put on sys.path by surrogate.py

X, y, Xh, yh = sg.design()

# 1. Fewer expensive runs: 10 instead of 30 LHS points. Predict: how much worse is each surrogate on the holdout?
for n in (30, 10):
    Xs, ys = X[:n], y[:n]  # note: the first 10 rows of a 30-point LHS are not a 10-point LHS (try it with one)
    rmse = {k: np.sqrt(np.mean((m(Xh)[0] - yh) ** 2)) for k, m in sg.fit_all(Xs, ys).items()}
    print(f"n={n}: " + "  ".join(f"{k} {v:.3f}" for k, v in rmse.items()))

# 2. Fit log(Wq) instead of Wq, then extrapolate to rho 0.95. Predict: does a better-shaped output fix extrapolation?
exact = mmc_queue.erlang_c(3, 2.7, 0.95)["Wq"]
for name, fit in (("polynomial", sg.fit_poly), ("gp-lite", sg.fit_gp)):
    raw = fit(X, y)(np.array([[2.7, 0.95]]))[0][0]
    logged = np.exp(fit(X, np.log(y))(np.array([[2.7, 0.95]]))[0][0])
    print(f"{name}: raw {raw:.3f}, log-fit {logged:.3f}, exact {exact:.3f}")
