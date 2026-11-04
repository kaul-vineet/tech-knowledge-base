"""Same parcel drop solved with SciPy 1.18.1 solve_ivp (pending-ci: SciPy is not installed in the sandbox).

The adaptive RK45 solver picks its own step sizes; a terminal event stops it at the ground.
python falling_scipy.py
"""
from scipy.integrate import solve_ivp

from falling import H0, accel, terminal_velocity


def rhs(t, state, drag):
    y, v = state
    return [v, accel(v, drag)]  # dy/dt = v, dv/dt = a(v)


def hit_ground(t, state, drag):
    return state[0]  # event fires when height crosses 0


hit_ground.terminal = True
hit_ground.direction = -1


def fall(drag):
    sol = solve_ivp(rhs, (0, 60), [H0, 0.0], args=(drag,), events=hit_ground, rtol=1e-8, atol=1e-8)
    return sol.t_events[0][0], sol.y_events[0][0][1]


if __name__ == "__main__":
    for drag in (False, True):
        t, v = fall(drag)
        print(f"solve_ivp drag={drag}: ground at {t:.2f} s, impact {abs(v):.2f} m/s")
    print(f"terminal velocity {terminal_velocity():.2f} m/s")
