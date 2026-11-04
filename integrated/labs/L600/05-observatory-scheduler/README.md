# L600 #05 · A robotic-observatory night scheduler (astronomy + simulation + ai-agents)

A small robotic telescope at Gurgaon (28.46 N, 77.03 E, IST = UTC+05:30) has one night, 2026-11-19, and 11 observation requests. Each request has an RA/Dec, a priority from 1 to 5 and one uninterrupted exposure of 30 to 180 minutes. Each topic contributes one part:
- **Astronomy** says what is observable: airmass ≤ 2.0 (Kasten & Young), Sun ≤ −18°, at least 30° from the Moon, with sidereal time checked against Wallace & Capitaine 2006.
- **Simulation** says what a plan is worth when clouds come in spells: a two-state Markov chain, 1000 seeded nights and common random numbers.
- **AI agents** may only propose a plan and explain it. A deterministic validator decides.

Concept note: `../../../content/concepts/L600/05-observatory-scheduler.md`. Lesson object: `../../../content/parts/05.json`.

## What is reused (imported in place by `_kb.py`; nothing copied, nothing edited)
| From | File | Used for |
|---|---|---|
| astronomy L300 #12 | `labs/L300/12-observation-planning/ephem.py` | Sun (USNO), GMST, Moon (Schlyter), alt/az, separation |
| astronomy L300 #12 | `labs/L300/12-observation-planning/solution/plan.py` | `airmass()`: Kasten & Young 1989, infinite below the horizon; SIMBAD coordinates of 8 stars |
| astronomy L100 #3 | `labs/L100/03-time-systems/timescales.py` | GAST (the validator's independent sidereal route) and the Wallace & Capitaine check |
| simulation L200 #10 | `labs/L200/10-warmup-replications/warmup.py` | `ci()`: t-interval over independent replications |
| shared | `kb/shared/local_agent/` | `chat()` client and the deterministic fake model server. The rules `[[OBS-PLAN]]` and `[[OBS-EXPLAIN]]` are appended to `EXTRA_RULES` at runtime by `agent_plan.py`. |

## Run
Python 3.12 + numpy only. The commands are the same on macOS (zsh) and Windows (PowerShell). Run them from this folder (`cd kb/integrated/labs/L600/05-observatory-scheduler`; on Windows use `cd kb\integrated\labs\L600\05-observatory-scheduler`).
```bash
python scheduler.py
python run_project.py
python run_project.py --inject local-as-utc
python -m unittest discover -s tests -t .
```

## Expected output (real runs: Python 3.12.15 + numpy 2.5.3, Linux; deterministic)
`python scheduler.py`
```
greedy: expected value 8.209  hash 904a1758f573bdfc
  {"target": "Deneb", "priority": 4, "start_utc": "2026-11-19T13:20:00Z", "end_utc": "2026-11-19T15:20:00Z", "start_local": "18:50", "max_airmass": 1.447, "p_complete": 0.5319}
  {"target": "Aldebaran", "priority": 4, "start_utc": "2026-11-19T15:20:00Z", "end_utc": "2026-11-19T16:50:00Z", "start_local": "20:50", "max_airmass": 1.939, "p_complete": 0.6012}
  {"target": "Capella", "priority": 3, "start_utc": "2026-11-19T16:50:00Z", "end_utc": "2026-11-19T18:50:00Z", "start_local": "22:20", "max_airmass": 1.372, "p_complete": 0.5319}
  {"target": "Betelgeuse", "priority": 5, "start_utc": "2026-11-19T18:50:00Z", "end_utc": "2026-11-19T21:50:00Z", "start_local": "00:20", "max_airmass": 1.229, "p_complete": 0.4163}
local: expected value 10.534  hash 4928d62de8143130
  {"target": "Vega", "priority": 3, "start_utc": "2026-11-19T13:20:00Z", "end_utc": "2026-11-19T14:20:00Z", "start_local": "18:50", "max_airmass": 1.93, "p_complete": 0.6795}
  {"target": "Deneb", "priority": 4, "start_utc": "2026-11-19T14:20:00Z", "end_utc": "2026-11-19T16:20:00Z", "start_local": "19:50", "max_airmass": 1.826, "p_complete": 0.5319}
  {"target": "Aldebaran", "priority": 4, "start_utc": "2026-11-19T16:20:00Z", "end_utc": "2026-11-19T17:50:00Z", "start_local": "21:50", "max_airmass": 1.433, "p_complete": 0.6012}
  {"target": "Betelgeuse", "priority": 5, "start_utc": "2026-11-19T17:50:00Z", "end_utc": "2026-11-19T20:50:00Z", "start_local": "23:20", "max_airmass": 1.485, "p_complete": 0.4163}
  {"target": "Sirius", "priority": 4, "start_utc": "2026-11-19T20:50:00Z", "end_utc": "2026-11-19T23:20:00Z", "start_local": "02:20", "max_airmass": 1.591, "p_complete": 0.4706}
```
`python run_project.py` (exit 0)
```
{"check": "M1 sky + typed time", "pass": true, "dark_local": "18:50-05:20", "slots": 64, "feasible": 7}
{"check": "M2 greedy baseline", "pass": true, "expected_value": 8.209, "plan": ["Deneb", "Aldebaran", "Capella", "Betelgeuse"], "violations": []}
{"check": "M3 local search", "pass": true, "expected_value": 10.534, "plan": ["Vega", "Deneb", "Aldebaran", "Betelgeuse", "Sirius"], "violations": []}
{"check": "M4 Monte Carlo weather", "pass": true, "runs": 1000, "greedy": "8.261+/-0.272", "local": "10.494+/-0.306", "greedy_better_nights": 0.178}
{"check": "M5 agent proposes, code decides", "pass": true, "agent_reasons": ["Sirius: '2026-11-20T02:20': need ISO 8601 with 'Z' or an explicit UTC offset", "Betelgeuse: altitude -16.4 deg, airmass inf at 2026-11-19T13:20:00Z (limit 2.0)", "Fomalhaut: altitude 22.3 deg, airmass 2.62 at 2026-11-19T16:20:00Z (limit 2.0)"], "valid_offset_plan": "agent", "explanation_published": true}
{"check": "SEAM time astronomy<->scheduler", "pass": true, "types_enforced": true, "max_route_diff_deg": 0.0019}
{"check": "SEAM agent<->validator", "pass": true, "rejected": ["Vega: '2026-11-19T18:50': need ISO 8601 with 'Z' or an explicit UTC offset", "Sirius: altitude -38.9 deg, airmass inf at 2026-11-19T13:20:00Z (limit 2.0)"], "invented_number_blocked": true}
{"check": "SEAM weather<->promises", "pass": true, "worst_z": 1.68, "promises": {"Vega": 0.6795, "Deneb": 0.5319, "Aldebaran": 0.6012, "Betelgeuse": 0.4163, "Sirius": 0.4706}}
{"check": "SEAM units deg/h/rad", "pass": true, "transit_identity_err": 4.263256414560601e-14}
{"check": "FF1 no observation above airmass 2.0", "pass": true, "max_airmass": 1.939}
{"check": "FF2 value >= greedy x 1.15 (1000 runs)", "pass": true, "ratio": 1.27, "paired_diff": "2.233+/-0.190"}
{"check": "FF3 deterministic for a seed", "pass": true, "plan_hash": "4928d62de8143130"}
{"scorecard": "PASS", "passed": 12, "total": 12}
```
Compute takes about 2 s per build. On a slow network drive, imports take most of the wall time (set `PYTHONDONTWRITEBYTECODE=1`).

## Seams and the tests that guard them
| Seam | Contract | Test |
|---|---|---|
| astronomy ↔ scheduler (time) | Sky maths accepts only `UtcInstant` (aware, offset 0, built by `astimezone`). The two altitude routes agree to 0.0019°. GAST matches the Wallace & Capitaine 2006 example to 0.023 s. | `tests/test_obs_seam_time.py` |
| ai-agents ↔ scheduler | `PLAN <target> <ISO 8601 with Z/offset>` lines become typed rows and go through `validator.validate()`. A plan is adopted only with 0 violations and a value ≥ the optimiser's. Explanation numbers must be facts. | `tests/test_obs_seam_agent.py` |
| simulation ↔ scheduler | The promise is p_complete = π(1−a)^(n−1). Each block must complete within 3 binomial SE of its promise over 1000 runs (worst z = 1.68). | `tests/test_obs_seam_weather.py` |
| units | The transit identity holds, and a dropped ×15 moves a star by more than 1°. | `tests/test_obs_seam_units.py` |

## Failure lab: local time passed where UTC is expected
- **Inject:** `python run_project.py --inject local-as-utc` (or set `SCHED_FAULT=local-as-utc`). The scheduler hands the sky maths `UtcInstant(slot.local.replace(tzinfo=None).replace(tzinfo=UTC))`, which relabels the IST wall clock as UTC.
- **Symptom:** the scheduler's own rows look fine (max airmass 1.982). The validator, recomputing at the published UTC times, finds Betelgeuse at −16.4°. Exit 1:
```
{"check": "M1 sky + typed time", "pass": true, "dark_local": "18:50-05:20", "slots": 64, "feasible": 5}
{"check": "M2 greedy baseline", "pass": false, "expected_value": 5.254, "plan": ["Betelgeuse", "Aldebaran", "Arcturus"], "violations": ["Betelgeuse: altitude -16.4 deg, airmass inf at 2026-11-19T13:20:00Z (limit 2.0)", "Arcturus: altitude -33.2 deg, airmass inf at 2026-11-19T19:20:00Z (limit 2.0)"]}
{"check": "M3 local search", "pass": false, "expected_value": 6.65, "plan": ["Aldebaran", "Sirius", "Capella", "Arcturus"], "violations": ["Aldebaran: altitude 4.9 deg, airmass 10.42 at 2026-11-19T13:20:00Z (limit 2.0)", "Sirius: altitude -19.1 deg, airmass inf at 2026-11-19T14:50:00Z (limit 2.0)"]}
{"check": "M4 Monte Carlo weather", "pass": true, "runs": 1000, "greedy": "5.297+/-0.213", "local": "6.678+/-0.219", "greedy_better_nights": 0.27}
{"check": "M5 agent proposes, code decides", "pass": false, "agent_reasons": ["Sirius: '2026-11-20T02:20': need ISO 8601 with 'Z' or an explicit UTC offset", "Betelgeuse: altitude -16.4 deg, airmass inf at 2026-11-19T13:20:00Z (limit 2.0)", "Fomalhaut: altitude 22.3 deg, airmass 2.62 at 2026-11-19T16:20:00Z (limit 2.0)"], "valid_offset_plan": "optimiser", "explanation_published": true}
{"check": "SEAM time astronomy<->scheduler", "pass": false, "types_enforced": true, "max_route_diff_deg": 0.0019}
{"check": "SEAM agent<->validator", "pass": true, "rejected": ["Vega: '2026-11-19T18:50': need ISO 8601 with 'Z' or an explicit UTC offset", "Sirius: altitude -38.9 deg, airmass inf at 2026-11-19T13:20:00Z (limit 2.0)"], "invented_number_blocked": true}
{"check": "SEAM weather<->promises", "pass": true, "worst_z": 0.72, "promises": {"Aldebaran": 0.6012, "Sirius": 0.4706, "Capella": 0.5319, "Arcturus": 0.768}}
{"check": "SEAM units deg/h/rad", "pass": true, "transit_identity_err": 4.263256414560601e-14}
{"check": "FF1 no observation above airmass 2.0", "pass": false, "max_airmass": 1.982}
{"check": "FF2 value >= greedy x 1.15 (1000 runs)", "pass": true, "ratio": 1.261, "paired_diff": "1.381+/-0.142"}
{"check": "FF3 deterministic for a seed", "pass": true, "plan_hash": "fb42c4a848b05466"}
{"scorecard": "FAIL", "passed": 7, "total": 12}
```
- **Diagnose:** `sky.sky_instant(slot, "local-as-utc") - slot.utc` is exactly 330 minutes, the IST offset. The type check passed because a relabelled clock has offset 0.
- **Fix:** build instants only with `UtcInstant.from_aware()` (`astimezone`). `test_no_relabelling_to_utc_outside_the_marked_fault` forbids `replace(tzinfo=UTC)` anywhere else. The seam test re-validates every block at its real UTC time.
- **Proof (before / after):** `SCHED_FAULT=local-as-utc python -m unittest tests.test_obs_seam_time` gives `Ran 7 tests ... FAILED (failures=2)` (greedy and local subtests). Without the variable it gives `OK`. In PowerShell: `$env:SCHED_FAULT = "local-as-utc"`, then remove it with `Remove-Item Env:SCHED_FAULT`.

## Fitness functions (`tests/test_obs_fitness.py`)
| What | Threshold | Observed |
|---|---|---|
| FF1 no observation above airmass 2.0 (also below the horizon, in twilight or near the Moon) | 0 violations at 5-min sampling | 0; max airmass 1.939 |
| FF2 expected value vs greedy, 1000 runs (seed 7) | ≥ 1.15 × greedy, and the paired CI is above 0 | 10.494 vs 8.261 (ratio 1.270); paired 2.233 ± 0.190 |
| FF3 deterministic for a seed | same plan hash and same weather matrix | `4928d62de8143130` |

## Build task: parse the times an agent writes
`plan_times.py` ships **unfixed**: it relabels every time as UTC, so `+05:30` is shifted by 330 minutes and a naive local time is accepted. Make zoned times convert and naive times raise `ValueError`. `solution/plan_times.py` is the reference version.
```bash
BUILD_TARGET=mine python -m unittest tests.test_obs_build_task -v     # PowerShell: $env:BUILD_TARGET = "mine"
```
Shipped file: `Ran 5 tests ... FAILED (failures=3)` (offset not converted, naive accepted, valid +05:30 plan rejected by the validator). After the fix, or without the variable (which checks the solution): `OK`. `BUILD_TARGET=mine python run_project.py` also fails M5 and SEAM agent on the shipped file, and the scorecard reads 10/12.

## Try it
```
python try_it/t1_cloudier_site.py
1. a=0.04 pi_clear=0.833 | greedy 8.261 local 10.494 ratio 1.270 | Betelgeuse 180 min p=0.416 | greedy wins 0.178
1. a=0.08 pi_clear=0.714 | greedy 4.503 local 5.965 ratio 1.325 | Betelgeuse 180 min p=0.173 | greedy wins 0.230
python try_it/t2_tighter_airmass.py
2. airmass <= 2.0: feasible 7 | greedy ['Deneb', 'Aldebaran', 'Capella', 'Betelgeuse'] 8.209 | local ['Vega', 'Deneb', 'Aldebaran', 'Betelgeuse', 'Sirius'] 10.534 | violations 0
2. airmass <= 1.5: feasible 4 | greedy ['Deneb', 'Aldebaran', 'Capella', 'Betelgeuse'] 8.209 | local ['Deneb', 'Aldebaran', 'Capella', 'Betelgeuse'] 8.209 | violations 0
```

## Tests
`python -m unittest discover -s tests -t .` gives `Ran 42 tests ... OK`. This was observed on 3 consecutive runs. No test depends on the wall clock, and the fake model server binds to 127.0.0.1 on a free port.

## Agent (fake model here; a real model is pendingCi)
The fake model's plan has priority order, blocks back to back from dusk, windows ignored and the last time written as local time without a zone. It is rejected for 4 reasons: an unzoned `2026-11-20T02:20`, Betelgeuse at −16.4°, Fomalhaut at airmass 2.62 and Deneb at airmass 6.50. The optimiser's plan stays in place. The same optimiser plan written in `+05:30` is **adopted**, so the gate is not "reject everything". The explanation is published because every number in it is a fact:
> The optimised plan promises an expected value of 10.534 against 8.209 for greedy, 28.3 percent more. It starts with Vega because it sets early. Betelgeuse is the riskiest promise: its block completes with probability 0.416.

Real model: `ollama pull qwen2.5:1.5b`, set `LOCAL_MODEL_URL=http://localhost:11434/v1` and `LOCAL_MODEL=qwen2.5:1.5b`, then run `python run_project.py --real`. Never put credentials in prompts. The model has no tools.

## Limits (honest)
- J2000 coordinates are used without precession (about 0.36° by 2026). The Sun and Moon positions are low precision (1–2 arcmin). The astropy/astroplan cross-check is pendingCi.
- The weather parameters (a = 0.04, b = 0.20 per 10 min) are assumptions, not site data.
- There are no slews, filter changes or calibrations, and no re-planning during the night.
