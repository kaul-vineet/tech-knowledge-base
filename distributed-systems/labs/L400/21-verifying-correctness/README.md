# 21 · Verifying correctness: model checking and linearizability checking

Design question: a change to the election code ("votedFor need not be persisted") passed review and three example-based tests. How do we verify protocol changes and store implementations before they ship? Two automatic tools, both stdlib Python: an **explicit-state model checker** (breadth-first search over every reachable state of a toy Raft election, invariants checked in each state, shortest counterexample returned - what TLC does for a TLA+ spec; `Election.tla` is the same model) and a **Porcupine-style linearizability checker** (Wing & Gong's search with Lowe's memoisation) for histories recorded from a running store (lab 17).

Files: `modelcheck.py` (lesson: the election model, `bfs`, `random_walks`) · `lincheck.py` (part 2: the memoised checker, run on lab 17's histories) · `solution_modelcheck.py` (build task) · `Election.tla`, `Election.cfg`, `ElectionFixed.cfg` (TLA+/TLC equivalent, pending CI) · `test_modelcheck.py` · `test_lincheck.py` · `test_build_task.py` · `test_fitness.py` · `ADR-021-verify-protocols-and-histories.md` · `try_it.py`.

## Run (Mac mini: `python3` inside the venv is `python`; Windows: same commands in PowerShell)
```bash
python modelcheck.py
python lincheck.py
```

## Expected output (real run, Python 3.12.15, Linux; counts are deterministic, times vary by machine)
```
BFS: 4519 distinct states explored, invariant ElectionSafety violated
  1. n0 times out -> candidate, term 1
  2. n1 votes for n0 in term 1
  3. n0 becomes leader of term 1
  4. n2 times out -> candidate, term 1
  5. n1 restarts (votedFor forgotten)
  6. n1 votes for n2 in term 1
  7. n2 becomes leader of term 1
random simulation: bug hit in 16/1000 walks of <= 30 steps (shortest 8 steps)
```
```
1) Porcupine README histories: True, False (README says true, false)
2) lab 17 R=2 W=2 write-back=False: 2273 ops, linearizable False, 48590 steps, 156 ms
   longest partial linearization 433 ops; cannot place r6 read -> 28 [1738.9, 1799.6] ms
2) lab 17 R=2 W=2 write-back=True: 1947 ops, linearizable True, 2890 steps, 81 ms
```
BFS proves the bug in 7 steps: n1 votes for n0, restarts, **forgets** its vote and votes again in the same term - two leaders of term 1. The three example tests in `test_modelcheck.py` all pass on this protocol; random simulation finds it in 16 of 1,000 walks. `lincheck.py` agrees with Porcupine's README examples, then rejects lab 17's R=2 W=2 history (2,273 operations) and points at the exact read of the first new-then-old inversion; with write-back the history is linearizable.

## Test
```bash
python -m unittest -v     # Ran 11 tests ... OK  (4 model-check + 3 lincheck + 2 build-task + 2 fitness)
```

## Build task: persist the vote, and check the cause
1. Set `PERSIST_VOTE = True` (votedFor is persistent state, Raft Figure 2).
2. Add a `VoteOnce` invariant over the ghost log `state[1]` (every vote ever cast; a restart cannot erase it): nobody votes for two candidates in one term. Put it before `ElectionSafety`.

Before your change (real run): `Ran 2 tests in 0.569s / FAILED (failures=2)`. The reference prints:
```
BFS: 1853 distinct states explored, invariant none violated
random simulation: bug hit in 0/1000 walks of <= 30 steps (shortest - steps)
```
With the bug re-introduced, `VoteOnce` fails after 4 steps - at the cause - instead of 7 steps at the consequence.

## TLA+ / TLC equivalent (pending CI)
`java -cp tla2tools.jar tlc2.TLC -config Election.cfg Election.tla` should report `Invariant ElectionSafety is violated`; with `ElectionFixed.cfg` it should finish with no error (the Python model explores 1,853 distinct states; TLC's count should match if the models are equivalent - unverified). TLA+ tools v1.7.4 (latest stable; v1.8.0 is a pre-release), MIT licence, Java 11+. Not run here: no Java in the authoring sandbox.

## Fitness function (keeps ADR-021 true)
`test_fitness.py`: the election model has no reachable violation of any invariant (and really explores > 1,000 states), and lab 17's config setting produces linearizable histories on seeds 11-13.

## Try it (real run - `python try_it.py`; times vary)
```
tryIt 1:  11 ops: memoised False in 2.31 ms, exhaustive (L300) False in 40.1 ms
tryIt 1:  26 ops: memoised False in 0.27 ms, exhaustive (L300) False in 240.6 ms
tryIt 1:  41 ops: memoised False in 0.29 ms, exhaustive (L300) False in 265.6 ms
tryIt 2: MAX_TERM=2: 1853 distinct states, 36 ms, violation: none
tryIt 2: MAX_TERM=3: 29221 distinct states, 856 ms, violation: none
```
tryIt 1: on the same non-linearizable histories the exhaustive L300 checker slows down fast; the memoised search stays flat. tryIt 2: one more term multiplies the model's state space by 16 - why models stay small and bounds are raised in nightly runs.

## Platform notes
Pure computation on simulated time: no sockets, no sleeps, no files written. Seeded, so the output is identical on macOS, Windows and Linux (CI matrix pending).
