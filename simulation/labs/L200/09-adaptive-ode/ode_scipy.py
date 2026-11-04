"""Same problems with SciPy 1.18.1 solve_ivp (pending-ci: SciPy is not installed in the sandbox).

RK45 is the same Dormand-Prince pair as adaptive_ode.py; Radau and BDF are implicit solvers for stiff problems.
python ode_scipy.py
"""
from importlib.metadata import version

import numpy as np
from scipy.integrate import solve_ivp

from adaptive_ode import coffee, rc_filter


def drinkable(t, y):
    return y[0] - 60.0  # event: coffee reaches 60 C


drinkable.terminal = True
drinkable.direction = -1


def coffee_event():
    sol = solve_ivp(coffee, (0, 60), [90.0], method="RK45", events=drinkable, rtol=1e-9, atol=1e-12)
    return sol.t_events[0][0]


def rc_work(method, rtol=1e-3):
    sol = solve_ivp(rc_filter, (0, 10), [0.0], method=method, rtol=rtol, atol=1e-9)
    return sol.nfev, len(sol.t) - 1, sol.y[0, -1]


if __name__ == "__main__":
    print(f"SciPy {version('scipy')}: coffee reaches 60 C at t={coffee_event():.4f} min "
          f"(exact {np.log(70 / 40) / 0.05:.4f})")
    for method in ("RK45", "Radau", "BDF", "LSODA"):
        nfev, steps, v = rc_work(method)
        print(f"RC filter {method:5}: {steps:5d} steps, {nfev:6d} f-evaluations, v(10)={v:.5f}")
