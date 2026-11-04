"""buildTask solution (lesson 9): stop the adaptive solver at an EVENT (coffee reaches 60 C), like solve_ivp(events=...).

After every accepted step, check whether event(t, y) changed sign; if so, bisect the step size from the start of
that step until the crossing is pinned to 1e-10 min.
python solution/ode_events.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adaptive_ode import coffee, dp_step  # noqa: E402


def solve_until(f, t0, y0, t_end, event, rtol=1e-9, atol=1e-12, h=0.01):
    t, y = t0, np.asarray(y0, dtype=float)
    while t < t_end:
        h = min(h, t_end - t)
        y_new, err = dp_step(f, t, y, h)
        e = float(np.sqrt(np.mean((err / (atol + rtol * np.maximum(np.abs(y), np.abs(y_new)))) ** 2)))
        if e <= 1:
            if np.sign(event(t + h, y_new)) != np.sign(event(t, y)):  # NEW: crossing inside this step
                lo, hi = 0.0, h
                while hi - lo > 1e-10:  # bisection on the step size, re-stepping from (t, y)
                    mid = (lo + hi) / 2
                    same_side = np.sign(event(t + mid, dp_step(f, t, y, mid)[0])) == np.sign(event(t, y))
                    lo, hi = (mid, hi) if same_side else (lo, mid)
                return t + hi, dp_step(f, t, y, hi)[0]
            t, y = t + h, y_new
        h *= min(10.0, max(0.2, 0.9 * e ** -0.2)) if e > 0 else 10.0
    return None, y  # no event before t_end


if __name__ == "__main__":
    t_event, y_event = solve_until(coffee, 0, [90.0], 60, lambda t, y: y[0] - 60.0)
    print(f"coffee reaches 60 C at t={t_event:.6f} min (exact ln(70/40)/0.05 = {np.log(70 / 40) / 0.05:.6f}), "
          f"T={y_event[0]:.6f} C")
