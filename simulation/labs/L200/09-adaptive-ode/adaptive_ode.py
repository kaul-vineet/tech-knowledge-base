"""L200 ODE solvers: an adaptive Dormand-Prince RK45 (SciPy's default) on coffee cooling (tolerances),
rabbits and foxes (adaptive steps) and a stiff 1 ms RC filter (stability limits the step).
python adaptive_ode.py
"""
import numpy as np

C = [0, 1/5, 3/10, 4/5, 8/9, 1]  # Dormand-Prince tableau, written as in scipy/integrate/_ivp/rk.py
A = [[], [1/5], [3/40, 9/40], [44/45, -56/15, 32/9], [19372/6561, -25360/2187, 64448/6561, -212/729],
     [9017/3168, -355/33, 46732/5247, 49/176, -5103/18656]]
B = [35/384, 0, 500/1113, 125/192, -2187/6784, 11/84]  # 5th-order weights: the step we keep
E = [-71/57600, 0, 71/16695, -71/1920, 17253/339200, -22/525, 1/40]  # 5th minus embedded 4th order


def dp_step(f, t, y, h):
    k = [f(t, y)]
    for c, a in zip(C[1:], A[1:]):
        k.append(f(t + c * h, y + h * sum(ai * ki for ai, ki in zip(a, k))))
    y_new = y + h * sum(b * ki for b, ki in zip(B, k))
    k.append(f(t + h, y_new))
    return y_new, h * sum(e * ki for e, ki in zip(E, k))  # error estimate comes almost for free


def solve(f, t0, y0, t_end, rtol=1e-6, atol=1e-9, h=0.01):
    t, y = t0, np.asarray(y0, dtype=float)
    ts, ys, rejected = [t], [y], 0
    while t < t_end:
        h = min(h, t_end - t)
        y_new, err = dp_step(f, t, y, h)
        scale = atol + rtol * np.maximum(np.abs(y), np.abs(y_new))  # tolerance per component
        e = float(np.sqrt(np.mean((err / scale) ** 2)))  # error relative to tolerance (RMS, like SciPy)
        if e <= 1:  # accept the step
            t, y = t + h, y_new
            ts.append(t)
            ys.append(y)
        else:
            rejected += 1  # reject: retry the same step with a smaller h
        h *= min(10.0, max(0.2, 0.9 * e ** -0.2)) if e > 0 else 10.0  # error ~ h^5 -> next h
    return np.array(ts), np.array(ys), rejected


def coffee(t, y, k=0.05, room=20.0):
    return -k * (y - room)  # Newton cooling, k per minute


def lotka_volterra(t, z, a=1.5, b=1.0, c=3.0, d=1.0):
    x, y = z
    return np.array([a * x - b * x * y, -c * y + d * x * y])  # rabbits grow, foxes eat rabbits


def rc_filter(t, v, tau=1e-3):
    return (np.cos(t) - v) / tau  # capacitor voltage chases a slow 1 rad/s input with a 1 ms time constant


def main():
    exact = 20 + 70 * np.exp(-0.05 * 30)
    print("1. coffee 90 C -> 30 min, room 20 C (exact {:.6f} C)".format(exact))
    for rtol in (1e-3, 1e-6, 1e-9):
        ts, ys, rej = solve(coffee, 0, [90.0], 30, rtol=rtol, atol=1e-12)
        print(f"   rtol={rtol:.0e}: {len(ts) - 1:3d} steps, {rej} rejected, error {abs(ys[-1, 0] - exact):.1e} C")
    ts, ys, rej = solve(lotka_volterra, 0, [10.0, 5.0], 15, rtol=1e-6)
    h = np.diff(ts)
    lo, hi = np.argmin(h[1:]) + 1, np.argmax(h)  # skip step 0: its size is our initial guess, not the solver's choice
    v = lambda z: z[0] - 3 * np.log(z[0]) + z[1] - 1.5 * np.log(z[1])  # conserved quantity: should not drift
    print(f"2. rabbits/foxes 0-15: {len(h)} steps, invariant drift {abs(v(ys[-1]) - v(ys[0])):.1e}")
    for name, i in (("smallest", lo), ("largest", hi)):
        print(f"   {name} step {h[i]:.4f} at t={ts[i]:5.2f}: rabbits {ys[i, 0]:5.2f}, foxes {ys[i, 1]:5.2f}")
    tau = 1e-3
    exact = (np.cos(10) + tau * np.sin(10)) / (1 + tau ** 2)  # closed form once the 1 ms start-up transient is gone
    print(f"3. stiff RC filter (tau = 1 ms), 0-10 s, exact v(10)={exact:.5f}:")
    for rtol in (1e-3, 1e-6):
        ts, ys, rej = solve(rc_filter, 0, [0.0], 10, rtol=rtol, atol=1e-9)
        print(f"   explicit RK45 rtol={rtol:.0e}: {len(ts) - 1:5d} steps ({rej:3d} rejected), v(10)={ys[-1, 0]:.5f}")
    v, dt = 0.0, 0.01
    for n in range(1, 1001):  # backward (implicit) Euler: v_new = v + dt * (cos(t_new) - v_new) / tau, solved for v_new
        v = (v + dt / tau * np.cos(n * dt)) / (1 + dt / tau)
    print(f"   implicit backward Euler dt=0.01: 1000 steps, v(10)={v:.5f}")


if __name__ == "__main__":
    main()
