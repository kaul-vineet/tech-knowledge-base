# 25 – Foundations III: decision theory and planning

Expected utility, the expected cost of retries under a budget, a ticket MDP solved by value iteration, BFS and A* (admissible vs overestimating heuristics), and a budgeted behaviour checker versus an allow-list - standard library only. `check T1..T4` prints the numerical check of each theorem in lesson 25.

Concept note: `../../../content/concepts/L500/25-decision-planning.md` · lesson object: `content/L500.json` #25 (theorems, proofs, problem set)
Dependencies: Python 3.12, standard library only. No model server is needed: L500 labs check mathematics, not model output.

## Run
macOS / Linux (zsh, bash):
```bash
python3 decision_planning.py            # demo
python3 decision_planning.py check T1   # numerical check of theorem T1 (T1, T2, T3, T4)
python3 -m unittest -v
```
Windows (PowerShell):
```powershell
py -3.12 decision_planning.py
py -3.12 decision_planning.py check T1
py -3.12 -m unittest -v
```

### Expected output – demo (observed 2026-10-30, Python 3.12.15, Linux sandbox)
```
refund under 50: auto-approve EU 0.74 vs human review EU 0.50 -> auto
tool succeeds 70 %: budget 3 -> 1.390 calls, gives up 2.7%
ticket MDP: V(open) 4.938, best first action auto
cheapest plan: start -> search_kb -> check_policy -> draft_reply (cost 4)
allow-list on a program that might delete: rejected ['delete_records']
```

### Expected output – `check T1` (observed 2026-10-30)
```
p=0.70 k=3: E[attempts] formula 1.3900 sim 1.3926; P(all fail) formula 0.0270 sim 0.0267
p=0.70 k=8: E[attempts] formula 1.4285 sim 1.4220; P(all fail) formula 0.0001 sim 0.0001
p=0.30 k=8: E[attempts] formula 3.1412 sim 3.1198; P(all fail) formula 0.0576 sim 0.0565
p=0.05 k=8: E[attempts] formula 6.7316 sim 6.7185; P(all fail) formula 0.6634 sim 0.6610
no budget, p=0.7: E[attempts] = 1/p = 1.4286; stuck loop p=0: cost grows as k -> k=8: 8, k=100: 100, k=10000: 10000
independent failures (p=0.7 each), call 1, give-up 20: p*C_fail = 14 > 1 so every retry pays: k*=20 of 20, cost 1.4286
correlated failures (p_i = 0.7 * 0.5^i): retry while p_i*20 >= 1 -> k*=4; cost k=1 7.0000, k*=4 4.5918, k=20 6.5160
saving from allowing attempt i = P(reach i) * (p_i*C_fail - c): 1:+13.0000, 2:+1.8000, 3:+0.4875, 4:+0.1207, 5:-0.0183, 6:-0.0790
```
All four checks' outputs are recorded in `content/L500.json` (`theorems[].checkOutput`); `python research/l500_checks.py` re-runs them and fails on any difference. Numbers are printed to 4 decimals with seeded generators so macOS and Windows should print the same text (status `expected` until the CI matrix runs).

### Tests
`python -m unittest` -> `Ran 5 tests ... OK`.

## How to use this lab with the lesson
1. Read the theorem statement in the lesson and try the proof yourself.
2. Predict the check's output before running it (which way should each number move?).
3. Run the check; change one parameter in the `check_T*` function (seed, dimension, probability) and explain the new output.
4. Use the module's functions to verify your numerical answers in the problem set.
