# ADR-021: Model-check protocol changes; check store histories for linearizability in CI

## Status
Accepted (lab 21, 2026-10-28). Fitness function: `test_fitness.py`.

## Context
A change to the election code ("votedFor need not be persisted, the term is enough") passed review and three
example-based tests. How should such changes be verified before they ship? Options measured with `modelcheck.py`,
`lincheck.py` and `try_it.py`:

| Option | Evidence | Verdict |
|---|---|---|
| Example-based unit tests | 3 hand-written scenarios pass on the buggy protocol (`test_modelcheck.py`) | necessary, not sufficient |
| Random simulation of the model | bug hit in 16 of 1,000 random walks (shortest 8 steps) | cheap smoke test |
| Exhaustive explicit-state BFS (TLC equivalent: `Election.tla`, pending CI) | shortest counterexample, 7 steps, after 4,519 states; with VoteOnce the cause shows in 4 steps; fixed model: 1,853 states, no violation | adopt for protocol logic |
| History checking (Porcupine-style, Wing & Gong + memoisation) | lab 17's 2,273-op R=2 W=2 history rejected in 48,590 steps, pinpointing r6's read of 28 at 1738.9 ms; the L300 exhaustive checker needed 265.6 ms vs 0.29 ms already at 41 ops (one run; times vary) | adopt for the implementation |

## Decision
Every protocol change updates the Python model (and `Election.tla`) and must pass BFS with all invariants, including
ghost-variable invariants such as VoteOnce. Store builds run seeded workloads and check the histories with the
memoised linearizability checker. The model checks the design; the history checker checks the code.

## Consequences
- The model is bounded (3 nodes, terms <= 2): one more term multiplies the space by 16 (1,853 -> 29,221 states).
  Bugs that need more nodes or terms can hide; raise the bounds in nightly runs.
- The model and the code can drift apart; history checks on the real implementation cover the gap.
- `test_fitness.py` fails the build if any invariant has a reachable violation or the config store's histories
  (seeds 11-13) stop being linearizable.
