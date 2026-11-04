# ADR 0001: The agent proposes experiments; a contract gate and a claim checker decide

## Status
Accepted (2026-10-30)

## Context
A local model plans simulation experiments for a help-desk model and summarises the results for a manager. Models invent tool arguments (lam 0.97, outside the range we verified), invent numbers ("about 32.3 min" for a run that never happened) and overstate results ("significant improvement" from 3 replications). The brief is that nobody can be fooled by the agent's text. Measured in this lab (`run_project.py`, fake model):
- The agent proposed 4 jobs: 1 was rejected by the contract (lam 0.97 > 0.95) and 1 by the budget (Sobol' 64 = 384,000 customers > 300,000).
- Its draft had 4 sentences. 1 was rejected (2 untraced numbers: 0.97 and 32.3). With `--inject few-reps`, a second sentence was also rejected: "significant improvement with 3 replications", where the 95% CI of the difference runs from -3.436 to 0.019.

## Decision
- The tool schemas (`contract.SCHEMAS`) are the only API between the agent and the pipeline. The same dict is sent to the model as `tools` and used by the validator, so they cannot drift apart. A cross-field rule the schema cannot express (lam/mu ≤ 0.9, the verified envelope) is checked in code.
- Rejections go back to the agent as tool results ("errors are data", ai-agents L100 #6). Nothing runs and nothing is charged.
- Every summary sentence that contains a number must cite an `[exp-...]` id from the registry. Its numbers must match that experiment's facts at the precision written. Its wording ("significant", direction words, "not significant") must agree with the computed verdict. A rejected sentence is replaced by a line that code writes from the facts.

## Consequences
- The agent can still choose which experiments to run. It cannot make one run outside the envelope, and it cannot publish a number the registry does not hold.
- The checker matches numbers by value, so a correct number can still be attached to the wrong label (the diff half-width 0.29 quoted as "the baseline mean"). The fact names in `traces` make this reviewable, but they do not prevent it. See scalingLimits.
- Fitness functions: `tests/test_fitness.py::test_claims_traced` and `tests/test_seam_contract.py`.
