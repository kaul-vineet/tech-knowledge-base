"""Theorem 23.4 (stationary distribution; M/M/1 from birth-death balance).
(a) A finite irreducible aperiodic chain has a unique pi with pi P = pi, and every row of P^n -> pi.
(b) Birth-death chain: flow balance across the cut {0..n} | {n+1..} gives lam pi_n = mu pi_(n+1), so
    pi_n = (1 - rho) rho^n for rho = lam/mu < 1, and L = rho / (1 - rho).
Checks: linear solve vs P^n vs simulation; M/M/1 formula vs the truncated generator vs a CTMC simulation."""
import numpy as np

rng = np.random.default_rng(2304)

# (a) a 3-state weather-like chain
P = np.array([[0.5, 0.4, 0.1], [0.2, 0.6, 0.2], [0.1, 0.3, 0.6]])
A = np.vstack([P.T - np.eye(3), np.ones(3)])
pi = np.linalg.lstsq(A, np.array([0, 0, 0, 1.0]), rcond=None)[0]
rows = np.linalg.matrix_power(P, 50)
state, visits = 0, np.zeros(3)
u = rng.random(200_000)
cum = P.cumsum(axis=1)
for x in u:
    state = int(np.searchsorted(cum[state], x))
    visits[state] += 1
print("(a) pi from pi P = pi :", np.round(pi, 4))
print("    every row of P^50 :", np.round(rows[0], 4), "max row spread < 1e-12" if np.ptp(rows, axis=0).max() < 1e-12 else "NOT CONVERGED")
print("    simulated 200,000 :", np.round(visits / visits.sum(), 4))
assert np.allclose(rows, pi, atol=1e-12) and np.allclose(visits / visits.sum(), pi, atol=0.01)

# (b) M/M/1 with lam = 0.8, mu = 1.0
lam, mu = 0.8, 1.0
rho = lam / mu
formula = (1 - rho) * rho ** np.arange(5)
N = 200  # truncated generator: solve pi Q = 0 numerically
Q = np.zeros((N + 1, N + 1))
for n in range(N + 1):
    if n < N:
        Q[n, n + 1] = lam
    if n > 0:
        Q[n, n - 1] = mu
    Q[n, n] = -Q[n].sum()
B = np.vstack([Q.T, np.ones(N + 1)])
pq = np.linalg.lstsq(B, np.r_[np.zeros(N + 1), 1.0], rcond=None)[0]
# CTMC simulation: time-weighted occupancy (Gillespie)
n, t_in = 0, np.zeros(N + 1)
for e, w in zip(rng.random(1_000_000), rng.exponential(1.0, 1_000_000)):
    rate = lam + (mu if n > 0 else 0.0)
    t_in[min(n, N)] += w / rate
    n = n + 1 if e < lam / rate else n - 1
sim = t_in / t_in.sum()
print("(b) n:                  0       1       2       3       4      L")
print("    (1-rho) rho^n   ", " ".join(f"{x:.4f}" for x in formula), f" {rho / (1 - rho):.3f}")
print("    generator solve ", " ".join(f"{x:.4f}" for x in pq[:5]), f" {np.arange(N + 1) @ pq:.3f}")
print("    CTMC simulation ", " ".join(f"{x:.4f}" for x in sim[:5]), f" {np.arange(N + 1) @ sim:.3f}")
print(f"    Little's law: W = L / lam = {rho / (1 - rho) / lam:.3f} = 1/(mu - lam) = {1 / (mu - lam):.3f}")
assert np.allclose(pq[:5], formula, atol=1e-12) and np.allclose(sim[:5], formula, atol=0.01)
