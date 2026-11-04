# 22 · Capstone: a digital twin of a service centre (input modelling → DES → calibration → sensitivity → staffing under the SLA → parallel replications → live twin → governance)

A service centre is open 08:00-20:00. Its SLA: at least 80% of calls answered within 1 minute and at most 5% abandoned, **in every hour**, with as few agent-hours as possible. The capstone runs end to end on seeded data and prints a JSON-lines scorecard. Deterministic code decides every step. The optional local model only explains the recommendation, and its explanation is published only if every number in it is verified.

Read first: `../../../content/concepts/L400/22-capstone.md`. Architecture: `architecture.mmd` (Mermaid). Decisions: `decisions/0001-0003`. Needs Python 3.12 + numpy.

## Run
```bash
python run_capstone.py          # about 3 minutes on this 1-CPU sandbox; writes scorecard.jsonl
python run_capstone.py --real-model   # agent assist against LOCAL_MODEL_URL / LOCAL_MODEL instead of the fake server
python make_data.py             # optional: regenerates data/ (history.csv is generated on first run, not committed)
```

## Expected output (real run, Python 3.12.15 + numpy 2.5.3, Linux)
```
{"milestone": "M1 input modelling", "pass": true, "service": "lognormal", "ks": {"lognormal": 0.0059, "normal": 0.1403, "exponential": 0.1762}, "max_rate_error": 0.07}
{"milestone": "M2 DES core verified", "pass": true, "sl_sim": 0.8376, "sl_erlang_c": 0.8365, "reproducible": true}
{"milestone": "M3 calibration + holdout validation", "pass": true, "patience_min": 4.5, "patience_plausible": [3.0, 5.5], "sl_mae_pp": 1.09, "abandon_mae_pp": 0.73}
{"milestone": "M4 sensitivity + staffing under SLA", "pass": true, "plan": [10, 19, 22, 25, 22, 19, 22, 24, 19, 15, 13, 11], "agent_hours": 221, "erlang_c_hours": 219, "flat_hours": 300, "erlang_c_day_abandon_max": 0.039, "elasticity_peak_sl": {"rate": -0.64, "mean_service": -0.68, "patience": -0.01}, "day_sl_min_low": 0.872, "day_abandon_max": 0.036}
{"milestone": "M5 parallel replications + live twin", "pass": true, "resume_identical": true, "alarm_delay_min": 75, "m_at_alarm": 1.201, "replan_from": "15:00", "extra_agent_hours": 14, "static_sl_after": 0.719, "twin_sl_after": 0.896}
{"milestone": "M6 governance pack + agent explanation", "pass": true, "card_findings": [], "review_flags": ["hour 15:00 plans for 6.16 calls/min > validated 5.6"], "agent_unverified": ["9"], "agent_publish": false, "decision": "235 agent-hours: plan [10, 19, 22, 25, 22, 19, 22, 28, 22, 18, 15, 13]"}
{"scorecard": "PASS", "passed": 6, "total": 6}
```
How to read it:
- **M3:** patience is weakly identified. Every value from 3.0 to 5.5 min fits within 20% of the best error, and the hidden truth is 3.0. M4 shows why it does not matter for this decision: the peak service level's elasticity to patience is -0.01.
- **M5:** the twin raised its alarm 75 minutes into a +30% surge (14:15). The static plan's worst service level after 15:00 is 0.719. The re-plan (+14 agent-hours) lifts it to 0.896.
- **M6:** the decision stands but carries a review flag, because the surge plan uses rates above the validated 5.6 calls/min. The fake agent's invented "9% saving" is caught, and its explanation is not published.

## Milestones and tests (`python -m unittest test_capstone -v`)
| Milestone | Deliverable | Test |
|---|---|---|
| M1 Input modelling | `pipeline.model_inputs()` (reuses L200 #7 `fit_inputs`) | `M1InputModelling`: lognormal by KS (D < 0.02), rates within 10% of the truth, seeded history |
| M2 DES core | `centre.py` (thinning, abandonment, CRN streams per purpose) | `M2DesCore`: Erlang C degenerate case within 0.01, monotone in agents (CRN), no abandonment with endless patience |
| M3 Calibration + validation | `pipeline.calibrate()`, `validate()` | `M3CalibrationValidation`: patience 4.5, the truth inside the plausible set, holdout MAE ≤ 3 / 2 pp |
| M4 Sensitivity + optimisation | `pipeline.sensitivity()`, `plan()` (Erlang C seed via L200 #8) | `M4SensitivityOptimisation`: peak-hour plan feasible and minimal; SL insensitive to patience |
| M5 Parallel + twin | `runner.py` (L400 #20 pattern), `demand_twin.py` (subclasses the L400 #17 Twin) | `M5ParallelAndTwin`: crash + resume = clean; one alarm at 375 min |
| M6 Governance + agent | `governance_pack.py` (L400 #21 `sha256`), `agent_explain.py` | `M6GovernanceAndAgent`: no card findings; invented number blocks publication |

Observed: `python -m unittest -v` gives `Ran 16 tests ... OK` (13 in `test_capstone` plus 3 in `test_fitness`; about 2 minutes here). The scorecard test reads `scorecard.jsonl` and skips if you have not run the capstone yet.

## Fitness functions (`python -m unittest test_fitness -v`)
- SLA: the recommended plan, simulated as 24 whole days, has every hour's SL lower bound ≥ 0.80 and abandonment ≤ 5%, with an identical checksum on 1 and 2 workers.
- Governance: the committed `model_card.json` still describes this code and data.
- Twin: no alarm before the surge, and an alarm within 90 minutes of it.

Observed: `Ran 3 tests ... OK`.

## Try it
```bash
python try_it.py
```
Observed:
```
point estimates : 208 agent-hours, worst-hour mean abandonment 0.064
95% bounds      : 221 agent-hours, worst-hour mean abandonment 0.036
Erlang C only   : 219 agent-hours, worst-hour mean abandonment 0.036
```
Deciding on point estimates saves 13 agent-hours and breaks the SLA in the 08:00 hour. Erlang C happens to meet the targets on average here, but two of its hours fail the 95% bound, and it cannot see abandonment at all (ADR 0001).

## Rubric
| Criterion | Measure | Pass |
|---|---|---|
| Inputs are justified | KS distance of the chosen fit; hourly rate error | lognormal, D < 0.02; rates within 10% |
| The DES is verified | SL against Erlang C in the degenerate case | within 0.01 |
| The model is validated on unseen data | holdout MAE (days 4-5) | SL ≤ 3 pp, abandonment ≤ 2 pp |
| The plan meets the SLA | full-day SL lower bound and abandonment, every hour | ≥ 0.80 and ≤ 5% |
| Results are reproducible at scale | checksum after crash + resume, 1 vs 2 workers | identical |
| The twin reacts to live data | alarm delay after the surge; false alarms | ≤ 90 min; 0 |
| The decision is governed | model-card findings; review flags shown | 0 findings; flags listed |
| The agent never decides | unverified numbers block publication | `agent_publish` false when any number is unverified |

## Files
- `run_capstone.py`: main file (milestones + scorecard). `centre.py`: DES core. `pipeline.py`: M1-M4. `runner.py`, `demand_twin.py`: M5. `governance_pack.py`, `agent_explain.py`: M6.
- `make_data.py`, `data/history_kpis.jsonl`, `data/today.jsonl` (`data/history.csv` is generated on demand).
- `model_card.json`, `architecture.mmd`, `decisions/0001-0003`, `try_it.py`, `test_capstone.py`, `test_fitness.py`.
