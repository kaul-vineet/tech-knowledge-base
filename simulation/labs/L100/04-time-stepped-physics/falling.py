"""L100 time-stepped simulation: a parcel dropped from a delivery drone hovering at 100 m.

Part 1 (no drag): compare explicit Euler, semi-implicit Euler and RK4 with the exact answer y = h - g t^2 / 2.
Part 2 (with drag): D = 0.5 * Cd * rho * A * v^2 slows the parcel towards terminal velocity.

python falling.py
"""
import math

G, H0 = 9.8, 100.0  # m/s^2, drop height in m
MASS, CD, AREA, RHO = 2.0, 1.05, 0.09, 1.225  # 2 kg box, 30 cm x 30 cm face, sea-level air


def accel(v, drag=True):
    # state is (height y, velocity v), v < 0 when falling; drag always opposes motion
    d = 0.5 * CD * RHO * AREA * v * abs(v) / MASS if drag else 0.0
    return -G - d


def step_euler(y, v, dt, drag):
    return y + v * dt, v + accel(v, drag) * dt  # explicit Euler: both updates use the OLD velocity


def step_semi_implicit(y, v, dt, drag):
    v_new = v + accel(v, drag) * dt
    return y + v_new * dt, v_new  # semi-implicit (symplectic) Euler: position uses the NEW velocity


def step_rk4(y, v, dt, drag):
    # RK4: four slope samples per step, weighted 1-2-2-1
    k1y, k1v = v, accel(v, drag)
    k2y, k2v = v + 0.5 * dt * k1v, accel(v + 0.5 * dt * k1v, drag)
    k3y, k3v = v + 0.5 * dt * k2v, accel(v + 0.5 * dt * k2v, drag)
    k4y, k4v = v + dt * k3v, accel(v + dt * k3v, drag)
    return (y + dt / 6 * (k1y + 2 * k2y + 2 * k3y + k4y),
            v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v))


def run(stepper, dt, t_end, drag):
    y, v, t = H0, 0.0, 0.0
    for _ in range(round(t_end / dt)):  # fixed time step: advance the state dt seconds at a time
        y, v = stepper(y, v, dt, drag)
        t += dt
    return y, v


def time_to_ground(stepper, dt, drag):
    y, v, t = H0, 0.0, 0.0
    while y > 0:
        y, v = stepper(y, v, dt, drag)
        t += dt
    return t, v


def terminal_velocity():
    return math.sqrt(2 * MASS * G / (CD * RHO * AREA))  # drag = weight


def main():
    t_end = 3.0
    exact = H0 - 0.5 * G * t_end ** 2
    print(f"No drag, height at t={t_end:.0f} s. Exact = {exact:.4f} m")
    print("    dt   explicit Euler err   semi-implicit err   RK4 err   (err = simulated - exact)")
    for dt in (0.1, 0.01, 0.001):  # step size vs error: 10x smaller dt -> Euler error 10x smaller
        errs = [run(s, dt, t_end, False)[0] - exact for s in (step_euler, step_semi_implicit, step_rk4)]
        print(f"{dt:6}   {errs[0]:+18.6f}   {errs[1]:+17.6f}   {errs[2]:+.1e}")
    vt = terminal_velocity()
    t_free, _ = time_to_ground(step_rk4, 0.001, False)
    t_drag, v_drag = time_to_ground(step_rk4, 0.001, True)
    print(f"With drag: terminal velocity = {vt:.2f} m/s")
    print(f"Time to fall {H0:.0f} m: no drag {t_free:.2f} s (exact {math.sqrt(2 * H0 / G):.2f} s), with drag {t_drag:.2f} s, impact {abs(v_drag):.2f} m/s")


if __name__ == "__main__":
    main()
