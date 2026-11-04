# 1. Govern the staffing model with a structured model card whose claims CI checks against fresh evidence

## Status
Accepted (2026-10-28)

## Context
The clinic queue model (L200 lesson 8) informs desk staffing. The decision consequence is medium: advisory, signed off by the clinic manager. We need documentation of purpose and assumptions, a validity envelope, verification and validation evidence, sensitivity results, versioning of code and data, and a review checklist. Measured by `governance.py`: verification 7/7; validation against Erlang C (10 reps, 10% requirement on error and CI) passes up to utilisation 0.85, worst error 5.5%; the busiest data hour needs 0.80; μ is the most influential input (elasticity -7.02 against 6.01 for λ). Options:
- A. Prose README: 0 of 4 overclaims in `cards/draft_overclaiming.json` caught (the shipped heading check said PUBLISHABLE).
- B. Structured card + `check_card()` against evidence: 4 of 4 caught (envelope 0.95, error 2.0%, key input λ, stale code hash). Data change detected (tryIt 2).
- C. Full risk-informed credibility assessment (NASA-STD-7009B, FDA 2023 / ASME V&V 40): mostly human-scored, so its cost per release is not measured here. Kept for safety-relevant decisions.

## Decision
Use option B: a JSON model card, evidence regenerated in CI, and `check_card()` blocking publication on any finding. Use option C's credibility factors as the human review checklist.

## Consequences
- Every code or data change stales the card until the evidence is re-run and model_version is bumped (SemVer).
- Prose quality is still human-reviewed; an agent may draft it, but code checks every claim (`agent_assist.py`).
- Fitness function: `test_fitness.py` (verification green; committed card has no findings; envelope ≥ busiest hour; checklist all ticked).
