"""Reading companion (Metropolis & Ulam 1949 discuss neutron multiplication as chains of events): sample single
chains instead of integrating. Galton-Watson process with Poisson(m) offspring: extinction probability q is the
smallest root of q = exp(m (q - 1)); Monte Carlo estimates it by following chains. Sargent-style operational check:
does the 95% CI of the simulated value contain the analytic one?"""
import math

import numpy as np

rng = np.random.default_rng(2701)
M, CHAINS, CAP, GENS = 1.2, 20_000, 500, 200
q = 0.0
for _ in range(2000):
    q = math.exp(M * (q - 1))  # fixed-point iteration from 0 converges to the smallest root
extinct = 0
for _ in range(CHAINS):
    pop = 1
    for _ in range(GENS):
        if pop == 0 or pop > CAP:  # above CAP survival is near certain: P(extinct | pop) = q^pop < 1e-80
            break
        pop = int(rng.poisson(M, pop).sum())
    extinct += pop == 0
p = extinct / CHAINS
half = 1.96 * math.sqrt(p * (1 - p) / CHAINS)
print(f"analytic extinction probability q = {q:.4f} (smallest root of q = exp({M}(q - 1)))")
print(f"Monte Carlo, {CHAINS:,} chains: {p:.4f} +/- {half:.4f} (95% CI); contains q: {abs(p - q) <= half}")
print(f"capped chains contribute bias < q^{CAP} = {q**CAP:.1e}")
assert abs(p - q) <= half
