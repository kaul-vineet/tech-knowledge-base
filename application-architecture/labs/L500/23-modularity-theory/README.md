# Lab 23 – Foundations I: modularity theory – information hiding, dependency graphs and Martin's metrics

Why Parnas's information hiding works, what a dependency graph can prove, why a strict layering rule rules out cycles, and what Martin's instability and abstractness metrics say about the real Library Loans code.

L500 labs are **numerical checks of theorems**: each `check_*.py` prints one line per check, `[OK]` or `[FAIL]`, and exits 1 if any check fails. Proofs are in `content/L500.json` (`theorems`) and the concept note `content/concepts/L500/23-modularity-theory.md`.

## Theorems checked
- **T23.1 Strict layering ⇔ acyclic dependency graph** – Let G = (V, E) be a finite dependency graph. (a) If G has a strict layering ℓ (ℓ(u) > ℓ(v) for every edge u → v), then G has no cycle. (b) Conversely, every finite acyclic G has a strict layering, for example ℓ(v) = length of the longest path that starts at v.
- **T23.2 The condensation of any dependency graph is acyclic** – Partition V into strongly connected components (SCCs). The condensation G*, with one node per SCC and an edge C → D (C ≠ D) whenever some u ∈ C depends on some v ∈ D, is acyclic. Hence every cycle lies inside one SCC, and by T23.1(b) the SCCs can always be strictly layered.
- **T23.3 Martin's metrics: ranges and the distance to the main sequence** – For a component with Ca + Ce > 0, Nc classes of which Na are abstract: I = Ce / (Ca + Ce) ∈ [0, 1], A = Na / Nc ∈ [0, 1], and the Euclidean distance from the point (I, A) to the main sequence A + I = 1 is |A + I − 1| / √2 ∈ [0, 1/√2]. Martin's normalised distance is Dn = |A + I − 1| ∈ [0, 1].

## Files
| File | Purpose |
|---|---|
| `modularity.py` | graph extraction with ast, SCCs, layering, Martin metrics, KWIC model |
| `check_modularity.py` | numerical checks for T23.1-T23.3 (prints OK/FAIL) |
| `test_modularity.py` | unittest suite |

## Run (Mac mini zsh or Windows PowerShell; stdlib only)
```bash
cd labs/L500/23-modularity-theory
python check_modularity.py
python -m unittest -v
```
On Windows use `py -3.12` if `python` is not on PATH.

## Expected output (observed 2026-10-30, Python 3.12.15, Linux)
All random draws are seeded, so the numbers repeat exactly.
```
$ python check_modularity.py
T1 strict layering <=> acyclic
  [OK] 2000/2000 random strictly layered graphs are acyclic
      (same-layer edges allowed: 1659/2000 graphs have a cycle - strictness matters)
  [OK] converse: longest-path layering of 2000 random DAGs has 0 violations
  [OK] layered (L100 #2): 4 edges, acyclic, layers {0: ['repository', 'service'], 1: ['handler'], 2: ['app']}
  [OK] hexagonal (L200 #7): 10 edges, acyclic, layers {0: ['ports'], 1: ['domain'], 2: ['driven_memory', 'driven_sqlite', 'driving_cli', 'driving_http'], 3: ['app']}
T2 the condensation (SCC graph) of any directed graph is acyclic
  [OK] 2000/2000 condensations acyclic (1634 of the inputs had cycles)
  [OK] hexagonal lab read WITH its __main__ blocks: cycle component [['app', 'driving_cli']] (driving_cli's entry block imports app, app imports driving_cli)
  [OK] seeded edge domain -> driving_http creates the cycle component [['domain', 'driving_http']]
T3 Martin metrics on Library Loans (L200 #7 hexagonal): I, A in [0,1]; distance to A + I = 1 is Dn / sqrt(2)
      module         Ca Ce      I     A     Dn  numeric d
      app             0  5  1.000  0.00  0.000     0.0000
      domain          5  1  0.167  0.00  0.833     0.5893
      driven_memory   1  1  0.500  0.00  0.500     0.3536
      driven_sqlite   1  1  0.500  0.00  0.500     0.3536
      driving_cli     1  1  0.500  0.00  0.500     0.3536
      driving_http    1  1  0.500  0.00  0.500     0.3536
      ports           1  0  0.000  1.00  0.000     0.0000
  [OK] all I and A in [0, 1]
  [OK] max |numeric distance - Dn/sqrt(2)| = 4.7e-12 (< 1e-5)
      mean Dn = 0.405; furthest from the main sequence: domain (stable and concrete: the 'zone of pain' corner)
Worked example: Parnas KWIC change impact (modules that must change per design decision)
      conventional        [1, 4, 4, 3, 2] total 14, worst 4
      information hiding  [1, 1, 1, 1, 1] total 5, worst 1
  [OK] information hiding: every decision is known by exactly one module
ALL CHECKS OK
$ python -m unittest
Ran 6 tests ... OK
```

## If a check fails
| Symptom | Action |
|---|---|
| `ModuleNotFoundError` | Run from this folder; the lab imports its neighbours by file name. |
| Numbers differ from above | You edited an earlier lab (L100 #2, L200 #7, L200 #8); the checks read that code live – re-run and explain the difference, that is the point. |
