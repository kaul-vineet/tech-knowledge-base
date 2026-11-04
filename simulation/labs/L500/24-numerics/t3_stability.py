"""Theorem 24.3 (absolute stability and stiffness).
Explicit Euler on y' = lam y gives y_n = (1 + z)^n y_0, z = h lam, so it decays iff |1 + z| <= 1 (a disc of radius 1
centred at -1): for real lam < 0 that needs h <= 2/|lam|. Implicit Euler gives 1/(1 - z): stable for every Re z <= 0.
RK4's interval on the negative real axis ends where |R(z)| = 1."""
import math

lam = -50.0
print("(a) explicit Euler, lam = -50 (limit h = 2/50 = 0.04), |y| after 200 steps from y0 = 1:")
for h in (0.039, 0.040, 0.041):
    y = 1.0
    for _ in range(200):
        y += h * lam * y
    print(f"    h = {h:.3f}  |1 + h lam| = {abs(1 + h * lam):.3f}  |y_200| = {abs(y):.3e}")
R = lambda z: 1 + z + z**2 / 2 + z**3 / 6 + z**4 / 24
lo, hi = -3.0, -2.0
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (lo, mid) if abs(R(mid)) <= 1 else (mid, hi)
print(f"(b) RK4 real-axis stability limit: z = {hi:.4f} (explicit Euler: -2)")

# (c) stiff problem: y' = -1000 (y - cos t) - sin t, y(0) = 1, exact y = cos t (smooth!)
f = lambda t, y: -1000.0 * (y - math.cos(t)) - math.sin(t)


def explicit(h, T=2.0):
    t, y = 0.0, 1.0
    for _ in range(round(T / h)):
        y, t = y + h * f(t, y), t + h
    return abs(y - math.cos(T))


def implicit(h, T=2.0):
    t, y = 0.0, 1.0
    for _ in range(round(T / h)):
        t += h
        y = (y + h * (1000.0 * math.cos(t) - math.sin(t))) / (1 + 1000.0 * h)  # solve the linear implicit step
    return abs(y - math.cos(T))


print("(c) stiff y' = -1000(y - cos t) - sin t on [0, 2]; the solution cos t is smooth but lam = -1000:")
for h in (0.0021, 0.0019):
    print(f"    explicit Euler h = {h}  steps {round(2 / h):5d}  error {explicit(h):.3e}")
for h in (0.1, 0.01):
    print(f"    implicit Euler h = {h:<6} steps {round(2 / h):5d}  error {implicit(h):.3e}")
assert explicit(0.0021) > 1e3 and explicit(0.0019) < 1e-3 and implicit(0.1) < 1e-3
assert abs(hi + 2.7853) < 1e-3
