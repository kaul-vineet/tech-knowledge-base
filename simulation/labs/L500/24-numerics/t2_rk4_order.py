"""Theorem 24.2 (classical RK4: local error O(h^5), global error O(h^4)).
(0) The Butcher tableau satisfies all 8 order conditions for order 4 (exact rational arithmetic).
(a) On y' = lam y one RK4 step multiplies y by R(z) = 1 + z + z^2/2 + z^3/6 + z^4/24 (z = h lam): the Taylor
    series of e^z to z^4, so the local error is z^5/120 + O(z^6).
(b) Same nonlinear test problem as 24.1: global error falls 16x per halving of h."""
import math
from fractions import Fraction as Fr


def f(t, y):
    return y - t * t + 1


def exact(t):
    return (t + 1) ** 2 - 0.5 * math.exp(t)


def rk4_step(f, t, y, h):
    k1 = f(t, y)
    k2 = f(t + h / 2, y + h / 2 * k1)
    k3 = f(t + h / 2, y + h / 2 * k2)
    k4 = f(t + h, y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


A = [[0, 0, 0, 0], [Fr(1, 2), 0, 0, 0], [0, Fr(1, 2), 0, 0], [0, 0, 1, 0]]
b = [Fr(1, 6), Fr(1, 3), Fr(1, 3), Fr(1, 6)]
c = [sum(row) for row in A]
Ac = [sum(A[i][j] * c[j] for j in range(4)) for i in range(4)]
conds = {
    "sum b = 1": (sum(b), 1), "b.c = 1/2": (sum(bi * ci for bi, ci in zip(b, c)), Fr(1, 2)),
    "b.c^2 = 1/3": (sum(bi * ci**2 for bi, ci in zip(b, c)), Fr(1, 3)), "b.Ac = 1/6": (sum(bi * x for bi, x in zip(b, Ac)), Fr(1, 6)),
    "b.c^3 = 1/4": (sum(bi * ci**3 for bi, ci in zip(b, c)), Fr(1, 4)),
    "b.(c*Ac) = 1/8": (sum(bi * ci * x for bi, ci, x in zip(b, c, Ac)), Fr(1, 8)),
    "b.Ac^2 = 1/12": (sum(b[i] * sum(A[i][j] * c[j] ** 2 for j in range(4)) for i in range(4)), Fr(1, 12)),
    "b.AAc = 1/24": (sum(b[i] * sum(A[i][j] * Ac[j] for j in range(4)) for i in range(4)), Fr(1, 24)),
}
ok = [name for name, (got, want) in conds.items() if got == want]
print(f"(0) order conditions satisfied: {len(ok)}/8 ({', '.join(ok)})")
assert len(ok) == 8
lam = -1.3
for h in (0.1, 0.05):
    z = h * lam
    one = rk4_step(lambda t, y: lam * y, 0.0, 1.0, h)
    R = 1 + z + z**2 / 2 + z**3 / 6 + z**4 / 24
    assert abs(one - R) < 1e-15
    print(f"(a) z = {z:+.3f}: RK4 step = R(z) to {abs(one - R):.0e}; e^z - R(z) = {math.exp(z) - R:+.3e}; z^5/120 = {z**5 / 120:+.3e}")

print("(b) h         global err   ratio   observed order")
prev, orders = None, []
for k in range(1, 6):
    h = 0.2 / 2 ** (k - 1)
    t, y = 0.0, 0.5
    for _ in range(round(2.0 / h)):
        y, t = rk4_step(f, t, y, h), t + h
    g = abs(y - exact(2.0))
    if prev:
        orders.append(math.log2(prev / g))
    ratio = f"{prev / g:6.2f}   {orders[-1]:.3f}" if prev else "     -   -"
    print(f"    {h:<9.5f} {g:.3e}   {ratio}")
    prev = g
assert abs(orders[-2] - 4) < 0.1
print("global error ~16x smaller per halving: O(h^4) (N = 2/h steps x O(h^5) local error)")
