# Lab 25 – Foundations III: formal reasoning about design – contracts, Liskov substitution, model checking and the evidence

Pre/postconditions and invariants on the real Member aggregate, Liskov's behavioural subtyping rule, explicit-state model checking of a loan workflow, and an honest reading of the empirical evidence on modularity and defects.

L500 labs are **numerical checks of theorems**: each `check_*.py` prints one line per check, `[OK]` or `[FAIL]`, and exits 1 if any check fails. Proofs are in `content/L500.json` (`theorems`) and the concept note `content/concepts/L500/25-formal-reasoning-design.md`.

## Theorems checked
- **T25.1 Invariant induction for an aggregate** – Let Inv be a predicate on the state of an aggregate. If (i) Inv holds after construction, (ii) every public operation, started in a state satisfying Inv and its precondition, ends in a state satisfying Inv, and (iii) a rejected operation leaves the state unchanged, then Inv holds in every state reachable through the public API.
- **T25.2 Liskov substitution rule for a method** – Let T specify method m by (pre_T, post_T) and let S implement m with (pre_S, post_S). If pre_T ⇒ pre_S and (pre_T ∧ post_S) ⇒ post_T, then every client proved correct against T's specification remains correct when it receives an S. (Liskov & Wing 1994 also require invariants and history constraints to be preserved.)
- **T25.3 BFS model checking is complete for finite models and returns shortest counterexamples** – For a finite transition system, breadth-first search from the initial state visits exactly the reachable states and terminates. If an unsafe state is reachable, the first unsafe state BFS dequeues has minimal distance from the start, so following parent pointers gives a shortest counterexample trace.

## Files
| File | Purpose |
|---|---|
| `contracts.py` | invariant/postcondition/atomicity checks on the real Member; Liskov checks |
| `model_check.py` | BFS explicit-state model checker for the loan workflow |
| `check_formal.py` | numerical checks for T25.1-T25.3 |
| `test_formal.py` | unittest suite |

## Run (Mac mini zsh or Windows PowerShell; stdlib only)
```bash
cd labs/L500/25-formal-reasoning
python check_formal.py
python -m unittest -v
```
On Windows use `py -3.12` if `python` is not on PATH.

## Expected output (observed 2026-10-30, Python 3.12.15, Linux)
All random draws are seeded, so the numbers repeat exactly.
```
$ python check_formal.py
T1 invariant induction: Inv(initial) and every operation preserves Inv => Inv in every reachable state
  [OK] base case: a new Member satisfies Inv
      310,352 random calls on the real L200 #8 Member aggregate, 178,288 rejected by rules
  [OK] Inv broken after 0 calls
  [OK] borrow postcondition broken 0 times
  [OK] rejected calls that changed state: 0
  [OK] loans is exposed as a read-only tuple (no append behind the root's back)
T2 Liskov rule: weaker-or-equal precondition and stronger-or-equal postcondition => safe substitution
      StrictLimit        pre broken at  0 of 44 points, post broken at  0; supertype client (overdue 0 / 1) ends with: [2, 0]
  [OK] StrictLimit: violations (0, 0) as predicted (0, 0)
      GenerousLimit      pre broken at  0 of 44 points, post broken at  8; supertype client (overdue 0 / 1) ends with: [5, 5]
  [OK] GenerousLimit: violations (0, 8) as predicted (0, 8)
      NoOverdueAccepted  pre broken at 33 of 44 points, post broken at  0; supertype client (overdue 0 / 1) ends with: [3, 'error: members with overdue loans are not accepted']
  [OK] NoOverdueAccepted: violations (33, 0) as predicted (33, 0)
  [OK] the client written for the supertype stays within 3 loans only with the valid subtype
T3 BFS model checking: explores every reachable state; the first violation found has a shortest trace
      buggy check-then-act: violation after exploring 9 states; counterexample: ['A reads: book free', 'B reads: book free', 'A borrows', 'B borrows']
  [OK] BFS counterexample length 4 = brute-force minimum 4
  [OK] atomic conditional insert: 8 reachable states, no violation, 0 deadlocks
  [OK] AG EF book available: from all 8 reachable states the book can become free again
      state explosion, members -> (buggy, fixed) reachable states: {2: (9, 8), 3: (27, 20), 4: (81, 48), 5: (243, 112), 6: (729, 256)}
  [OK] buggy = 3^n and fixed = (n + 2) * 2^(n - 1) for n = 2..6
ALL CHECKS OK
$ python -m unittest
Ran 5 tests ... OK
```

## If a check fails
| Symptom | Action |
|---|---|
| `ModuleNotFoundError` | Run from this folder; the lab imports its neighbours by file name. |
| Numbers differ from above | You edited an earlier lab (L100 #2, L200 #7, L200 #8); the checks read that code live – re-run and explain the difference, that is the point. |
