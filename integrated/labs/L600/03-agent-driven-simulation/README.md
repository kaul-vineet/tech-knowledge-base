# L600 #03 · An AI agent that runs simulation experiments — and can't fool you

**Combines:** ai-agents (tool-calling loop, schema-validated arguments, call budget) + simulation (help-desk model, V&V, Morris screening, replications and confidence intervals) + application-architecture (job pipeline, contract at the boundary, append-only registry, fitness functions).

An agent reads an analyst's brief, proposes screening runs and A/B experiments as tool calls, and writes a summary. Deterministic code decides everything else:
- which proposals may run (schema + verified envelope);
- what they cost (budget reserved before running);
- how many replications are needed (target CI half-width);
- which numbers exist (seeded runs in an append-only registry);
- which sentences of the summary are published (claim checker).

Concept note: `../../../content/concepts/L600/03-agent-driven-simulation.md` · Lesson object: `content/parts/03.json` · Architecture: `architecture.mmd` · Decisions: `decisions/0001-0003`.

## Design brief
A help desk (M/M/1, arrivals lam = 0.8/min, service mu = 1.0/min, 30 tickets waiting on Monday) is considering a triage script that makes service 5% faster (mu 1.05). The manager wants to know whether waits really drop, in a report they can trust.

Constraints (measurable):
- every numeric claim in the published report traces to a registered run (100%);
- every registered run reproduces bit-for-bit from its record (same environment);
- session budget 300,000 simulated customers and 8 model calls, never exceeded;
- a difference is called significant only with ≥ 10 replications and a 95% CI of the difference that excludes 0, with half-width ≤ 0.3 min;
- the agent never chooses the replication count and never sees secrets (only the brief and tool results).

## Run (fake model — validated here)
macOS / Linux:
```bash
cd integrated/labs/L600/03-agent-driven-simulation
python run_project.py                      # scorecard, exit 0; writes out/registry.jsonl, out/report.md, out/scorecard.jsonl
python run_project.py --inject few-reps    # the failure lab, exit 1
python -m unittest discover -s tests -v    # 38 tests
```
Windows (PowerShell):
```powershell
cd integrated\labs\L600\03-agent-driven-simulation
python run_project.py
python run_project.py --inject few-reps; "exit $LASTEXITCODE"
python -m unittest discover -s tests -v
```
Needs Python 3.12 and numpy only. It reuses `kb/simulation`, `kb/ai-agents` and `kb/shared/local_agent` through `_kb.py` (loaded by file path, never edited). It takes about 30-60 s here, mostly the M1 verification runs.

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux x86_64)
```
{"milestone": "M1 model verified (V&V) + reproducible", "pass": true, "checks": [{"rho": 0.5, "sim": 0.992, "half_width": 0.038, "formula": 1.0, "covered": true}, {"rho": 0.8, "sim": 3.894, "half_width": 0.229, "formula": 4.0, "covered": true}, {"rho": 0.9, "sim": 8.491, "half_width": 0.817, "formula": 9.0, "covered": true}], "same_seed_same_bits": true, "model": "helpdesk-mm1@3384b3898c59"}
{"milestone": "M2 contract gate before any run", "pass": true, "rejected_by_contract": ["job-4"], "ran_outside_envelope": [], "runs_for_rejected_jobs": 0}
{"milestone": "M3 experiment registry", "pass": true, "runs": 160, "experiments": 2, "facts_trace_to_runs": true}
{"milestone": "M4 replications from target half-width", "pass": true, "requested": 3, "replications": 55, "diff_half_width": 0.293, "target": 0.3, "verdict": "significant decrease", "diff": -0.895}
{"milestone": "M5 claim check + published report", "pass": true, "sentences": 4, "rejected": [{"sentence": "At lam 0.97 the mean wait would be about 32.3 min.", "reason": "untraced numbers ['0.97', '32.3']: no experiment cited"}]}
{"seam": "agent <-> tool schema", "pass": true, "test": "tests/test_seam_contract.py"}
{"seam": "agent claims <-> computed statistics", "pass": true, "test": "tests/test_seam_claims.py"}
{"seam": "sim stochasticity <-> conclusions", "pass": true, "verdict": "significant decrease", "overclaims_rejected": [], "test": "tests/test_seam_replications.py"}
{"seam": "cost/time budget", "pass": true, "rejected_by_budget": ["job-1"], "spent": 270000, "limit": 300000, "agent_calls": 5, "ledger": [["job-2 morris 50 runs", 50000], ["job-3 first 3 replications", 12000], ["job-3 extend to 10 replications", 28000], ["job-3 extend to 47 replications", 148000], ["job-3 extend to 55 replications", 32000]], "test": "tests/test_seam_budget.py"}
{"fitness": "100% of numeric claims traced to a registry run", "pass": true, "numbers": 7, "traced": 7, "test": "tests/test_fitness.py::test_claims_traced"}
{"fitness": "every run reproducible bit-for-bit from its seed", "pass": true, "reproduced": 160, "runs": 160, "env": "python 3.12.15 numpy 2.5.3 x86_64", "test": "tests/test_fitness.py::test_runs_reproducible"}
{"fitness": "budget never exceeded", "pass": true, "spent": 270000, "limit": 300000, "test": "tests/test_fitness.py::test_budget_never_exceeded"}
{"scorecard": "PASS", "passed": 12, "total": 12, "inject": null}
```
`out/report.md` (published text, then the agent's draft):
```
# Published summary

The sobol screening was skipped because the run budget did not allow it. Screening ranks mu first (mu_star 1.72) and backlog last (mu_star 0.54) [exp-65b9401a]. Faster service (mu 1.05) cut the mean wait from 4.04 to 3.14 min (-22%), a significant improvement with 55 replications [exp-4092571f].

# Agent draft

The sobol screening was skipped because the run budget did not allow it. Screening ranks mu first (mu_star 1.72) and backlog last (mu_star 0.54) [exp-65b9401a]. Faster service (mu 1.05) cut the mean wait from 4.04 to 3.14 min (-22%), a significant improvement with 55 replications [exp-4092571f]. At lam 0.97 the mean wait would be about 32.3 min.
```
How to read it:
- **M2 / budget seam:** job-1 (Sobol' N = 64 → 384 runs × 1,000 customers) was refused by the budget gate. Job-4 (lam 0.97) was refused by the schema. Neither left a run or spent a customer.
- **M4:** the agent asked for 3 replications. The ledger shows the pipeline's sequential rule at work: 3 → 10 → 47 → 55. At 55 the half-width of the difference is 0.293 ≤ 0.3. Waits drop from 4.04 to 3.14 min (-0.895, -22%). The M/M/1 steady-state difference is -0.952, inside the CI.
- **M5:** the draft's last sentence states 32.3 min for a run that never happened (the contract rejected it). It cites no experiment, so it is dropped. The other 7 numbers trace to registry facts. Each fact lists its run ids.

## Failure lab: "significant improvement" from 3 replications
```bash
python run_project.py --inject few-reps
```
```
{"milestone": "M4 replications from target half-width", "pass": false, "requested": 3, "replications": 3, "diff_half_width": 1.728, "target": 0.3, "verdict": "inconclusive", "diff": -1.709}
{"seam": "sim stochasticity <-> conclusions", "pass": false, "verdict": "inconclusive", "overclaims_rejected": ["Faster service (mu 1.05) cut the mean wait from 4.28 to 2.58 min (-40%), a significant improvement with 3 replications [exp-439c0335]."], "test": "tests/test_seam_replications.py"}
{"scorecard": "FAIL", "passed": 10, "total": 12, "inject": "few-reps"}
```
```
# Published summary

The sobol screening was skipped because the run budget did not allow it. Screening ranks mu first (mu_star 1.72) and backlog last (mu_star 0.54) [exp-65b9401a]. Code result [exp-439c0335]: mean wait 4.28 vs 2.58 min, difference -1.71 min with 95% CI from -3.44 to 0.02, n = 3 per arm: inconclusive.

# Agent draft

The sobol screening was skipped because the run budget did not allow it. Screening ranks mu first (mu_star 1.72) and backlog last (mu_star 0.54) [exp-65b9401a]. Faster service (mu 1.05) cut the mean wait from 4.28 to 2.58 min (-40%), a significant improvement with 3 replications [exp-439c0335]. At lam 0.97 the mean wait would be about 32.3 min.
```
- **Inject:** the pipeline trusts the agent's `replications: 3` (`pipeline.naive_policy`). The same fault ships in `replications.py`, the unfixed build-task file.
- **Symptom:** the draft says "cut the mean wait from 4.28 to 2.58 min (-40%), a significant improvement with 3 replications". Every number in it traces to the registry.
- **Diagnose:** the arm CIs are 4.28 ± 2.07 and 2.58 ± 1.05, which overlap. The 95% Welch CI of the difference runs from -3.436 to 0.019, which includes 0. The checker rejects the sentence, saying "claims significance; computed verdict is inconclusive", and publishes a code-written line instead.
- **Fix:** `solution/replications.py`. Run a pilot of 10, then n = ⌈n·(h/0.3)²⌉ until the target is met, reserving budget before each extension. Result: 55 replications, a significant decrease of -22%. The claim now passes.
- **Test:** `tests/test_failure_lab.py` (the fault reproduces and the checker rejects it; the fixed pipeline supports the claim; `--inject few-reps` exits 1). `BUILD_TARGET=mine python -m unittest tests.test_build_task` fails 3/3 on the shipped `replications.py` and passes on the solution.

Other seeded faults (one seam each):

| `--inject` | What breaks | Scorecard (observed) |
|---|---|---|
| `no-contract` | the lam 0.97 job runs outside the verified envelope; the agent then over-claims on it | M2, schema seam, stochasticity seam fail · 9/12, exit 1 |
| `no-budget-gate` | Sobol' runs anyway; 654,000 of 300,000 customers spent | budget seam, F3 fail · 10/12, exit 1 |
| `unseeded` | runs use OS entropy; 0 of 70 reproduce (numbers vary run to run) | M3, M4, stochasticity seam, F2 fail · 8/12, exit 1 |

## Milestones, seams, fitness functions → tests
| Line | Test |
|---|---|
| M1 model verified (V&V) + reproducible | `tests/test_milestones.py::M1ModelVerified` |
| M2 contract gate before any run | `tests/test_milestones.py::M2ContractGate` |
| M3 experiment registry | `tests/test_milestones.py::M3Registry` |
| M4 replications from target half-width | `tests/test_milestones.py::M4Replications` |
| M5 claim check + published report | `tests/test_milestones.py::M5ClaimCheck` |
| seam agent ↔ tool schema | `tests/test_seam_contract.py` (8 bad proposals, 0 runs, 0 cost) |
| seam agent claims ↔ statistics | `tests/test_seam_claims.py` (uncited, unknown id, overstated %, extra precision, wrong direction, false negation, direction without qualifier) |
| seam stochasticity ↔ conclusions | `tests/test_seam_replications.py` (exact t, n rule, keyed streams reuse runs, 3 reps inconclusive) |
| seam cost/time budget | `tests/test_seam_budget.py` (refused before running, extension stops at budget, agent loop capped at 4 calls) |
| F1 100% numeric claims traced | `tests/test_fitness.py::test_claims_traced` |
| F2 runs reproducible bit-for-bit | `tests/test_fitness.py::test_runs_reproducible` |
| F3 budget never exceeded | `tests/test_fitness.py::test_budget_never_exceeded` (adversarial proposals, 3 budgets) |

Observed: `python -m unittest discover -s tests -v` → `Ran 38 tests in 111.153s` → `OK`.

## Build task
Implement `required_replications(requested, a, b, half_width)` in `replications.py`. It must run at least 10 pilot replications, then n·(achieved half-width/target)², rounded up.
```bash
BUILD_TARGET=mine python -m unittest tests.test_build_task -v     # shipped file: FAILED (failures=3)
python -m unittest tests.test_build_task -v                       # solution: Ran 3 tests ... OK
```
PowerShell: `$env:BUILD_TARGET = "mine"; python -m unittest tests.test_build_task -v`. With `BUILD_TARGET=mine`, `run_project.py` also uses your file.

## Try it
1. `python try_it/crn.py`. Predict first: how many replications does a paired design (common random numbers) need for ±0.3?
```
independent streams (default run): n = 55 per arm, difference -0.895 +/- 0.293 min, cost 220,000 customers
common random numbers (paired)   : n = 10 per arm, difference -1.022 +/- 0.266 min, cost 40,000 customers, correlation between arms 0.963
```
2. `python try_it/tighter_target.py`. Predict first: with ±0.2 and the same budget, does the pipeline overspend?
```
target +/- 0.3: n = 55 (required 55), half-width 0.293, verdict significant decrease, budget_limited False, spent 220,000 of 250,000
target +/- 0.2: n = 10 (required 105), half-width 0.645, verdict significant decrease, budget_limited True, spent 40,000 of 250,000
```
With ±0.2 the pipeline needs 105 replications per arm (420,000 customers). It stops at 10 and says `budget_limited`. Check the half-width before you quote a ±0.2 answer.

## Agent with a real local model (optional, pendingCi)
```bash
export LOCAL_MODEL_URL=http://localhost:11434/v1 LOCAL_MODEL=qwen2.5:1.5b   # PowerShell: $env:LOCAL_MODEL_URL=...
python run_project.py --real-model
```
Only the brief and tool results go to the model (no keys, no data files). A real model may plan different jobs, so the scorecard lines that assume the fake's plan (for example "M2: at least one contract rejection") can differ. The contract, budget and claim checks do not change. This has not been run here, because there is no model in the sandbox.

## Files
`run_project.py` (main, scorecard) · `agent.py` (tool loop) · `fake_sim_agent.py` (deterministic stand-in, wraps the shared fake server) · `contract.py` (tool schemas + envelope) · `pipeline.py` (job states, budget, runs, Morris adapter, statistics) · `registry.py` (append-only JSONL, reproduce) · `model.py` (help-desk adapter, keyed seeds) · `stats.py` (exact t, Welch) · `claims.py` (claim checker) · `replications.py` (build task, unfixed) · `solution/replications.py` · `_kb.py` (reuse loader) · `tests/` · `try_it/` · `decisions/` · `architecture.mmd`.
