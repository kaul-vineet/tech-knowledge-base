"""Theorem 24.1 (explicit Euler: local truncation error O(h^2), global error O(h)).
Test problem (Burden & Faires' classic): y' = y - t^2 + 1, y(0) = 0.5, exact y = (t + 1)^2 - 0.5 e^t, t in [0, 2].
Local error = one step from the exact value; global error = |y_N - y(2)| after N = 2/h steps."""
import math


def f(t, y):
    return y - t * t + 1


def exact(t):
    return (t + 1) ** 2 - 0.5 * math.exp(t)


def euler(h, t_end=2.0):
    t, y = 0.0, 0.5
    for _ in range(round(t_end / h)):
        y, t = y + h * f(t, y), t + h
    return y


print("h         local err   ratio  global err   ratio  observed order")
prev_l = prev_g = None
orders = []
for k in range(1, 7):
    h = 0.2 / 2 ** (k - 1)
    local = abs(0.5 + h * f(0.0, 0.5) - exact(h))
    glob = abs(euler(h) - exact(2.0))
    rl = f"{prev_l / local:5.2f}" if prev_l else "  -  "
    rg = f"{prev_g / glob:5.2f}" if prev_g else "  -  "
    order = f"{math.log2(prev_g / glob):.3f}" if prev_g else "-"
    if prev_g:
        orders.append(math.log2(prev_g / glob))
    print(f"{h:<9.5f} {local:.3e}  {rl}  {glob:.3e}  {rg}  {order}")
    prev_l, prev_g = local, glob
assert abs(orders[-1] - 1) < 0.05  # halving h halves the global error: O(h)
print("local error falls ~4x per halving (O(h^2)); global ~2x (O(h)): N = 2/h steps each add O(h^2)")
