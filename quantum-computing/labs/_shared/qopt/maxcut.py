"""MaxCut problems and a vectorised QAOA statevector (numpy only), shared by L400 labs 17-22.

Convention = labs/_shared/qsim: qubit 0 is the least-significant bit of a basis index.
Generalises lesson 14 (one fixed 5-node graph) to any seeded graph so labs can scale n.
"""
import numpy as np


def regular_graph(n, d=3, seed=0):
    """Random d-regular simple graph (pairing model with rejection), seeded and reproducible."""
    rng = np.random.default_rng(seed)
    for _ in range(1000):
        stubs = rng.permutation(np.repeat(np.arange(n), d))
        pairs = {tuple(sorted(map(int, stubs[i:i + 2]))) for i in range(0, len(stubs), 2)}
        if len(pairs) == n * d // 2 and all(a != b for a, b in pairs):
            return sorted(pairs)
    raise ValueError(f"no simple {d}-regular graph found for n={n}")


def cut_values(n, edges):
    """Cut size of every one of the 2**n bitstrings (the diagonal of the cost operator C)."""
    z = np.arange(2 ** n)
    return sum((((z >> i) & 1) != ((z >> j) & 1)).astype(np.int32) for i, j in edges)


def cut_of(bits, edges):
    return int(sum(((bits >> i) & 1) != ((bits >> j) & 1) for i, j in edges))


def brute_force(n, edges):
    cuts = cut_values(n, edges)
    return int(cuts.max()), [int(b) for b in np.flatnonzero(cuts == cuts.max())]


def mix(psi, n, beta):
    """RX(2*beta) on every qubit, applied axis by axis (no 2**n x 2**n matrix)."""
    c, s = np.cos(beta), -1j * np.sin(beta)
    for q in range(n):
        v = psi.reshape(2 ** (n - q - 1), 2, 2 ** q)
        a, b = v[:, 0, :], v[:, 1, :]
        new_a = c * a + s * b
        b *= c
        b += s * a
        a[...] = new_a
    return psi


def qaoa_state(n, cuts, params):
    """params = [gamma_1..gamma_p, beta_1..beta_p]; |+>^n, then p x (cost phase, mixer)."""
    p = len(params) // 2
    psi = np.full(2 ** n, 2 ** (-n / 2), dtype=complex)
    for gamma, beta in zip(params[:p], params[p:]):
        psi = mix(psi * np.exp(-1j * gamma * cuts), n, beta)
    return psi


def expectation(n, cuts, params):
    return float(np.abs(qaoa_state(n, cuts, params)) ** 2 @ cuts)


def sample(n, cuts, params, shots, rng):
    probs = np.abs(qaoa_state(n, cuts, params)) ** 2
    return rng.choice(2 ** n, size=shots, p=probs / probs.sum())


def optimize(n, cuts, p=1, steps=60, lr=0.05, h=1e-3, grid=11):
    """Grid start for (gamma, beta), ramp to depth p, then finite-difference ascent on <C>.
    Returns (params, evaluations) so callers can charge the work to a budget."""
    evals = 0
    best = (-1.0, None)
    for g in np.linspace(0.1, np.pi / 2, grid):
        for b in np.linspace(0.1, np.pi / 2, grid):
            e = expectation(n, cuts, [g, b])
            evals += 1
            best = max(best, (e, (g, b)), key=lambda t: t[0])
    g, b = best[1]
    x = np.array([g * (k + 1) / p for k in range(p)] + [b * (p - k) / p for k in range(p)])
    for _ in range(steps):
        grad = np.array([(expectation(n, cuts, x + h * e) - expectation(n, cuts, x - h * e)) / (2 * h)
                         for e in np.eye(len(x))])
        evals += 2 * len(x)
        x = x + lr * grad
    return x, evals
