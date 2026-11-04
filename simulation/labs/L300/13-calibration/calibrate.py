"""L300 calibration: fit a room cool-down model to a logged temperature curve, and validate it honestly.

An office's heating switches off at 18:00; a sensor logs the room every 10 minutes for 12 hours.
Three candidate models are calibrated by least squares on the first 8 hours and checked on the last 4.
python calibrate.py
"""
import numpy as np

SEED, NOISE = 13, 0.15
T_HOURS = np.arange(0, 12 + 1e-9, 1 / 6)  # 73 readings, every 10 minutes
CAL = T_HOURS <= 8.0  # calibration window; the rest (8-12 h) is the holdout


def observed(seed=SEED):
    """Synthetic 'measured' data: fast air mode (1.5 h) + slow wall mode (9 h) + sensor noise. Truth is known."""
    truth = 12 + 6 * np.exp(-T_HOURS / 1.5) + 4 * np.exp(-T_HOURS / 9.0)
    return truth + np.random.default_rng(seed).normal(0, NOISE, T_HOURS.size)


def one_exp(t, p):  # [T_inf, A, tau]: Newton cooling, one time constant (3 parameters)
    return p[0] + p[1] * np.exp(-t / p[2])


def two_exp(t, p):  # [T_inf, A, tau_air, B, tau_wall]: air + walls (5 parameters)
    return p[0] + p[1] * np.exp(-t / p[2]) + p[3] * np.exp(-t / p[4])


def gauss_newton(model, t, y, p0, iters=200, lam=1e-3):
    """Least squares: minimise sum (model - y)^2 with damped Gauss-Newton (Levenberg-Marquardt) steps."""
    p = np.array(p0, float)
    cost = lambda q: float(np.sum((model(t, q) - y) ** 2))
    for _ in range(iters):
        r = model(t, p) - y
        J = np.column_stack([(model(t, p + h) - model(t, p)) / h[i]  # forward-difference Jacobian
                             for i, h in enumerate(np.diag(1e-6 * np.maximum(1.0, np.abs(p))))])
        step = np.linalg.solve(J.T @ J + lam * np.diag(np.diag(J.T @ J)), -J.T @ r)
        if cost(p + step) < cost(p):
            p, lam = p + step, lam / 3  # accept, trust the quadratic model more
        else:
            lam *= 5  # reject, take smaller steps
        if np.linalg.norm(step) < 1e-10 * (1 + np.linalg.norm(p)):
            break
    return p, J


def poly(degree):
    """Black-box curve: polynomial in t/8 (7 parameters for degree 6) - flexible, but no physics."""
    def fit(t, y):
        coef = np.linalg.lstsq(np.vander(t / 8, degree + 1), y)[0]
        return lambda tt: np.vander(tt / 8, degree + 1) @ coef
    return fit


def candidates(t, y):
    """Calibrate each model on (t, y); return name -> (n_params, predict function)."""
    p1, _ = gauss_newton(one_exp, t, y, [y[-1], y[0] - y[-1], 2.0])
    p2, _ = gauss_newton(two_exp, t, y, [y[-1], 5.0, 1.0, 5.0, 6.0])
    return {"one-exp (3 p)": (3, lambda tt: one_exp(tt, p1)),
            "two-exp (5 p)": (5, lambda tt: two_exp(tt, p2)),
            "poly-6 (7 p)": (7, poly(6)(t, y))}


rmse = lambda a, b: float(np.sqrt(np.mean((a - b) ** 2)))


def scores(models, y, mask):
    """RMSE of every calibrated model on the readings selected by mask."""
    return {name: rmse(f(T_HOURS[mask]), y[mask]) for name, (_, f) in models.items()}


def select(y):
    """Calibrate every candidate on the first 8 h, score them and return the best."""
    models = candidates(T_HOURS[CAL], y[CAL])
    s = scores(models, y, CAL)  # score each model on the readings it was fitted to
    return min(s, key=s.get), s, models


def main():
    y = observed()
    print(f"{y.size} readings, {CAL.sum()} for calibration (0-8 h), {(~CAL).sum()} held out (8-12 h); "
          f"sensor noise sd {NOISE}")
    best, _, models = select(y)
    same, hold = scores(models, y, CAL), scores(models, y, ~CAL)
    print("  model           RMSE on calibration data   RMSE on holdout   prediction at 12 h (measured "
          f"{y[-1]:.2f})")
    for name, (_, f) in models.items():
        print(f"  {name:14s}  {same[name]:10.3f} C               {hold[name]:8.3f} C      {f(T_HOURS[-1:])[0]:8.2f} C")
    print(f"select() picks {best}; its holdout RMSE is {hold[best]:.3f} C")


if __name__ == "__main__":
    main()
