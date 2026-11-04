"""SciPy equivalent (pending-ci): the same fits with scipy.optimize.least_squares (needs scipy==1.18.1).

python calibrate_scipy.py
"""
import numpy as np
from scipy.optimize import least_squares

import calibrate as cal


def fit(model, p0):
    y = cal.observed()
    t, yc = cal.T_HOURS[cal.CAL], y[cal.CAL]
    res = least_squares(lambda p: model(t, p) - yc, p0, method="lm")  # residual vector, as in the SciPy docs
    return res.x


if __name__ == "__main__":
    y = cal.observed()
    yc = y[cal.CAL]
    for name, model, p0 in [("one-exp", cal.one_exp, [yc[-1], yc[0] - yc[-1], 2.0]),
                            ("two-exp", cal.two_exp, [yc[-1], 5.0, 1.0, 5.0, 6.0])]:
        ours, _ = cal.gauss_newton(model, cal.T_HOURS[cal.CAL], yc, p0)
        print(f"{name}: scipy {np.round(fit(model, p0), 3)}  numpy {np.round(ours, 3)}")
