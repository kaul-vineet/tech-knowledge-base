"""Monte Carlo weather for one night: a two-state (clear/cloudy) Markov chain on the 10-minute slot grid.

Persistence matters: clouds come in spells, so a long block is riskier than its length alone suggests (Gabriel &
Neumann 1962 used the same two-state chain for daily rain occurrence). Parameters are ASSUMPTIONS for a site,
not measurements (ADR 0003). Streams: one SeedSequence child per run (simulation L300 #16: independent streams).
"""
import numpy as np

import _kb

P_CLEAR_TO_CLOUD, P_CLOUD_TO_CLEAR = 0.04, 0.20  # per 10-min step: clear spells ~250 min, cloud spells ~50 min


def pi_clear(a=P_CLEAR_TO_CLOUD, b=P_CLOUD_TO_CLEAR):
    return b / (a + b)  # stationary probability of 'clear'


def p_complete(n_slots, a=P_CLEAR_TO_CLOUD, b=P_CLOUD_TO_CLEAR):
    """A block survives only if all its n slots are clear: pi * (1 - a)^(n - 1) (start from the stationary state)."""
    return pi_clear(a, b) * (1.0 - a) ** (n_slots - 1)


def clear_matrix(n_runs, n_slots, seed, a=P_CLEAR_TO_CLOUD, b=P_CLOUD_TO_CLEAR):
    """Bool array (runs, slots): True = clear. Run r uses child stream r of SeedSequence(seed): add runs, keep old ones."""
    u = np.array([np.random.default_rng(c).random(n_slots) for c in np.random.SeedSequence(seed).spawn(n_runs)])
    clear = np.empty((n_runs, n_slots), dtype=bool)
    clear[:, 0] = u[:, 0] < pi_clear(a, b)
    for s in range(1, n_slots):
        stay = np.where(clear[:, s - 1], u[:, s] >= a, u[:, s] < b)  # clear stays clear w.p. 1-a; cloud clears w.p. b
        clear[:, s] = stay
    return clear


def realised(blocks, clear):
    """Value per run: a block counts (its priority) only if every one of its slots was clear. blocks: (start, n, w)."""
    v = np.zeros(clear.shape[0])
    for start, n, w in blocks:
        v += w * clear[:, start:start + n].all(axis=1)
    return v


def expected(blocks, a=P_CLEAR_TO_CLOUD, b=P_CLOUD_TO_CLEAR):
    """Analytic expectation (linearity of expectation): sum of w * p_complete(n). The promise the scheduler makes."""
    return sum(w * p_complete(n, a, b) for _, n, w in blocks)


def summary(values):
    """Mean and 95 % half-width from simulation L200 #10's t-interval (runs are independent replications)."""
    return _kb.warmup.ci(list(values))
