"""tryIt experiments for lesson 13 (run: python try_it.py)."""
import numpy as np

import calibrate as cal

y = cal.observed()

# 1. Shorter log: calibrate two-exp on the first 5 hours only. Predict: worse fit, or absurd parameters?
m = cal.T_HOURS <= 5
p, _ = cal.gauss_newton(cal.two_exp, cal.T_HOURS[m], y[m], [y[m][-1], 5.0, 1.0, 5.0, 6.0])
print(f"two-exp on 0-5 h: RMSE {cal.rmse(cal.two_exp(cal.T_HOURS[m], p), y[m]):.3f} C, "
      f"T_inf={p[0]:.0f} C, B={p[3]:.0f} C, tau_wall={p[4]:.0f} h")

# 2. Random holdout (every 3rd reading) instead of 'the last 4 hours'. Predict: does poly-6 still get caught?
hold = np.arange(y.size) % 3 == 0
models = cal.candidates(cal.T_HOURS[~hold], y[~hold])
scores = {name: cal.rmse(f(cal.T_HOURS[hold]), y[hold]) for name, (_, f) in models.items()}
print("random holdout RMSE: " + ", ".join(f"{k} {v:.3f}" for k, v in scores.items())
      + f" -> picks {min(scores, key=scores.get)}")
