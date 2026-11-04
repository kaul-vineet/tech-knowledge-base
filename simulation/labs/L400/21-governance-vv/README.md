# 21 · Model governance and V&V: model card, verification suite, validation evidence, versions, review gate

The clinic queue model from L200 lesson 8 helps decide how many reception desks to open. This lab builds its governance pack:
- a verification suite (Sargent's degenerate, extreme-condition and internal-validity tests)
- validation against the exact Erlang C answer over a utilisation grid, with the accuracy requirement fixed before the runs; the validity envelope falls out of it
- sensitivity (elasticities)
- SHA-256 versions of the code and data
- a review checklist

`check_card()` compares the model card with that evidence. The shipped check only looks at headings, so a hurried draft that overclaims sails through. An optional local model drafts card prose, and code checks every claim.

Read the concept note first: `../../../content/concepts/L400/21-governance-vv.md`. Needs Python 3.12 + numpy.

## Run
```bash
python governance.py          # evidence.json + checks model_card.json and cards/draft_overclaiming.json
python -m unittest verification -v    # the verification suite alone (7 tests)
python agent_assist.py --fake # optional: agent drafts card text, code checks it (drop --fake for local Ollama)
```

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux) - shipped file
```
verification: 7 tests, 0 failures
validation vs Erlang C (10 reps x 20,000 patients):  rho  sim_Wq  exact  rel_err  rel_CI  ok
  0.50   0.157  0.158    0.4%   2.4%  True
  0.60   0.279  0.296    5.5%   3.5%  True
  0.70   0.528  0.547    3.5%   4.7%  True
  0.80   1.060  1.079    1.7%   9.9%  True
  0.85   1.573  1.623    3.1%   6.7%  True
  0.90   2.873  2.724    5.5%  11.9%  False
  0.95   6.127  6.047    1.3%  21.0%  False
validity envelope: utilisation <= 0.85; max error inside 5.5%; busiest hour in arrivals.csv needs 0.8
sensitivity (elasticity of Wq): {'lam': 6.01, 'mu': -7.02} -> most influential: mu
model_card.json: PUBLISHABLE; findings []
   [x] verification suite passes
   [x] validated envelope covers the busiest hour in the data
   [x] sensitivity results recorded
   [x] model and data versions pinned by hash
   [x] card claims match the evidence
draft_overclaiming.json: PUBLISHABLE; findings []
   ... (all ticked)
```
At ρ = 0.90 and 0.95 the error is small (5.5%, 1.3%), but 10 replications cannot pin the mean within the 10% requirement (CI 11.9%, 21.0%). The envelope therefore ends at 0.85.

## Failure lab: break it, see it, fix it
- **Fault (seeded, shipped in `governance.py`):** `check_card()` returns findings only for missing sections. `cards/draft_overclaiming.json` claims utilisation ≤ 0.95, a 2.0% error, λ as the key input and an old code hash, and it is reported **PUBLISHABLE**.
- **Fix (your build task):** check each claim against the evidence (`solution/governance.py`):
```
draft_overclaiming.json: BLOCKED; findings ['envelope claims utilisation <= 0.95, evidence supports 0.85', 'claims max error 2.0%, evidence shows 5.5%', "claims most influential input 'lam', evidence says 'mu'", 'code_sha256 is stale: re-run the evidence and bump model_version']
```
- **Proof:** `BUILD_TARGET=mine python -m unittest test_build_task` fails 1 of 2 on the shipped file (4 failing subtests; the honest card passes either way) and passes on the solution. `TestFailureLab` keeps the fault reproducible.

## Agent assist (optional, fake model in tests)
```
1. agent drafted:
   Validity and evidence (draft):
   - Valid for utilisation up to 0.95 with 3 desks.
   - Mean wait within 2.0% of Erlang C across the range.
   - Results are most sensitive to the service rate (elasticity -7.02).
   - 7 of 7 tests pass.
2. code checked each claim against evidence.json:
   OVERCLAIM envelope     'utilisation up to 0.95'
   OVERCLAIM accuracy     'within 2.0% of Erlang C'
   OK        key input    'most sensitive to the service rate'
   OK        verification '7 of 7 tests pass'
3. numbers not found in the evidence (UNVERIFIED): 3, 2.0
4. code verdict: draft REJECTED - fix the claims, then re-run
```
The agent sees only the evidence summary: no code, no keys. The fake server rule `[[SIM-CARD]]` is registered through the shared server's documented `EXTRA_RULES` hook, so `labs/_shared/local_agent` is unchanged. With a real model (`LOCAL_MODEL_URL`, `LOCAL_MODEL`), replies vary, and the claim checks still decide.

## Design decision and fitness function
Decision: `decisions/0001-machine-checked-model-card.md` (structured card + CI check; NASA-STD-7009B / FDA 2023 credibility factors serve as the human checklist). Fitness function `test_fitness.py`: verification green, committed card with no findings against fresh evidence, envelope ≥ busiest hour, all checklist items ticked. Observed: `Ran 4 tests ... OK`. The shipped heading check also passes the honest card; `test_build_task` is the one that catches the weak gate.

## Test
```bash
python -m unittest -v
```
Observed: `Ran 14 tests ... OK` (test_governance 5, test_build_task 2, test_fitness 4, test_agent_assist 3).

## Try it
```bash
python try_it.py
```
Observed:
```
accuracy requirement 10%: validated envelope utilisation <= 0.85
accuracy requirement 5%: validated envelope utilisation <= 0.5
committed data: no findings
one new row   : ['data_sha256 is stale: re-run the evidence and bump model_version']
```

## Build it (design task)
Extend `check_card(card, ev)` in `governance.py`. After the section check, add a finding when:
- the claimed `utilisation_max` exceeds `ev["envelope_rho_max"]`
- the claimed `max_rel_error` is smaller than `ev["max_rel_error_in_envelope"]`
- the claimed most influential input differs from the evidence
- the verification count does not match a clean run
- `code_sha256` or `data_sha256` differs from the evidence

Hints: a claim may be *more conservative* than the evidence, but never wider or better. Return the list of findings; an empty list means publishable.
Check: `BUILD_TARGET=mine python -m unittest test_build_task -v` (PowerShell: `$env:BUILD_TARGET = "mine"`).

## Files
- `governance.py`: main lab (verify, validate, sensitivity, hashes, checklist). Ships the heading-only `check_card()`.
- `verification.py`: the verification suite. `arrivals.csv`: the data the card versions.
- `model_card.json` (honest), `cards/draft_overclaiming.json` (the failure-lab fixture).
- `agent_assist.py`: optional local-model drafting, checked by code.
- `solution/governance.py`, `try_it.py`, `test_governance.py`, `test_build_task.py`, `test_fitness.py`, `test_agent_assist.py`.
- `decisions/0001-machine-checked-model-card.md`: the ADR.
