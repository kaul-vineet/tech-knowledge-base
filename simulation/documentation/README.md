# Simulation (applied) — L100 "Run it", L200 "Build it", L300 "Harden it", L400 "Design it" + capstone, L500 "Theory & rigour"

**Status: not yet run on macOS or Windows; CI matrix pending.**

Start here. This domain teaches software engineers to answer engineering questions by running models: sampling uncertain inputs (Monte Carlo), jumping between events (discrete-event queues), stepping continuous physics (Euler, RK4), letting simple agents interact (agent-based), and checking whether a model can be trusted (verification and validation). All examples are civilian: coffee-shop and API queues, project schedules, a parcel dropped by a delivery drone, neighbourhood choice.

## L100 lesson map
| # | Level | Lesson | Lab folder | You will see | Validation |
|---|---|---|---|---|---|
| 1 | Setup | Set up your simulation workbench | `labs/L100/01-setup-workbench` | Python + numpy detected, pinned SimPy/SciPy/Mesa listed, seeded draws repeat | validated-local |
| 2 | L100 | Monte Carlo: estimate a project's completion time | `labs/L100/02-monte-carlo` | Mean 17.334 ± 0.015 days, P(≤ 20 days) 0.857, CI shrinking ~1/√N | validated-local |
| 3 | L100 | Discrete-event simulation: a single-server queue | `labs/L100/03-discrete-event-queue` | Event trace with clock jumps; simulated wait 3.871 vs M/M/1 4.000 min | validated-local (SimPy variant pending-ci) |
| 4 | L100 | Time-stepped physics: a parcel dropped from a drone | `labs/L100/04-time-stepped-physics` | Euler error 1.47 → 0.0147 m as dt shrinks; RK4 ~exact; terminal velocity 18.40 m/s | validated-local (SciPy variant pending-ci) |
| 5 | L100 | Agent-based modelling: Schelling's neighbourhood model | `labs/L100/05-agent-based-schelling` | 30% preference → 75.4% similar neighbours | validated-local (Mesa variant pending-ci) |
| 6 | L100 | Is the model right? Verification vs validation | `labs/L100/06-verification-validation` | Rule unit tests, seed hashes, 4.046 ± 0.195 vs 4.000, sensitivity sweep; **agent assist**: local model proposes a sweep, code validates/runs/checks | validated-local (SciPy t-quantile test pending-ci; agent assist vs fake server only) |

## L200 lesson map ("Build it": extend working code, tests prove it)
| # | Level | Lesson | Lab folder | You will see / build | Validation |
|---|---|---|---|---|---|
| 7 | L200 | Input modelling: fit service times and check the fit | `labs/L200/07-input-modelling` | KS D 0.217 / 0.132 / 0.031 → lognormal; exponential input overstates waits ~25%. **Build:** shifted-exponential candidate. **Agent assist:** model proposes a distribution, code decides by KS and checks numbers | validated-local (SciPy variant pending-ci; agent vs fake server only) |
| 8 | L200 | Resources and queues: c desks, one line, Erlang C | `labs/L200/08-multi-server-queue` | Wq 1.110 vs Erlang C 1.079; Little's law; 5 desks for P(wait) < 20%. **Build:** waiting-room limit (Erlang B 0.268) | validated-local (SimPy variant pending-ci) |
| 9 | L200 | ODE solvers in practice: adaptive steps, tolerances, stiffness | `labs/L200/09-adaptive-ode` | Dormand-Prince RK45: error 1.3e-2 → 7.9e-9 with rtol; stiff RC 3,027 explicit vs 1,000 implicit steps. **Build:** event detection | validated-local (SciPy variant pending-ci) |
| 10 | L200 | Warm-up, replications and confidence | `labs/L200/10-warmup-replications` | Welch proposes warm-up 169; bias 5.59 → 3.71 (true 4.0); CI ±0.50 → ±0.16. **Build:** sequential replications to 5% precision | validated-local (SciPy t check pending-ci) |
| 11 | L200 | A supply-chain model: (s, S) inventory with CRN | `labs/L200/11-supply-chain-inventory` | Independent +0.03 ± 0.44 (can't tell) vs CRN −0.25 ± 0.12 (S=90 cheaper). **Build:** fill-rate metric | validated-local (SimPy Container variant pending-ci) |

## L300 lesson map ("Harden it": see it fail under a seeded fault, make it robust, prove it with a test)
| # | Level | Lesson | Lab folder | Failure lab (fault → fix) / build | Validation |
|---|---|---|---|---|---|
| 12 | L300 | Variance reduction: same precision, fewer runs | `labs/L300/12-variance-reduction` | Antithetic 1.46×, control variate 5.40× (exact 0.9196 h). **Fault (shipped):** `antithetic_loop()` reseeds per evaluation (ρ −0.00, 1.01×). **Build:** one stream per pair (1.50×). **Stretch:** pilot-based estimator choice, JSON log | validated-local (SciPy check pending-ci) |
| 13 | L300 | Calibration: fit to data, validate on data you did not fit | `labs/L300/13-calibration` | **Fault (shipped):** `select()` validates on the calibration data and picks poly-6 (holdout RMSE 12.517 °C). **Build:** time-ordered holdout picks two-exp (0.161 °C). **Stretch:** identifiability report (corr −0.994) | validated-local (SciPy `least_squares` pending-ci) |
| 14 | L300 | Global sensitivity: OAT vs Morris vs Sobol' | `labs/L300/14-global-sensitivity` | **Fault (shipped):** `screen()` by OAT drops window_open (swing 0.0; keeps 84.1% of variance). **Build:** screen by Sobol' ST = 0.155 (96.1%). **Stretch:** bootstrap CIs, honest ranking. **Agent assist:** model ranks inputs, code checks against ST | validated-local (SALib pending-ci; agent vs fake server only) |
| 15 | L300 | Co-simulation with FMI: master algorithm and communication step | `labs/L300/15-cosimulation-fmi` | **Fault (shipped):** `COMM_STEP_S = 900` → heater chatter, 6.78 °C swing (JSON log). **Build:** a step below the 313 s bound (60 s settles). **Stretch:** master that halves h from its log metrics | validated-local (FMPy pending-ci; OpenModelica FMU export manual) |
| 16 | L300 | Performance and scale: vectorise, parallelise, keep streams independent | `labs/L300/16-performance-scale` | numpy = loop to 9.1e-14, 7-26× faster. **Fault (shipped):** `tasks_for()` gives every worker one seed → 1 distinct result of 40, "± 0.000". **Build:** `SeedSequence.spawn` per replication (worker-count independent). **Stretch:** chunked tasks | validated-local (multi-core and macOS/Windows spawn pending-ci) |

## L400 lesson map ("Design it": compare options with evidence, decide in an ADR, keep the decision true with a fitness test)
| # | Level | Lesson | Lab folder | Options measured → decision (fault → fix) | Validation |
|---|---|---|---|---|---|
| 17 | L400 | Digital twins with live data: state estimation, drift detection and recalibration | `labs/L400/17-digital-twin` | open-loop 6.316 / filter-only 0.194 / **KF + CUSUM + refit 0.127 °C** (last-day RMSE). **Fault:** no innovation gate → an 85 °C glitch gives 5 false alarms. **Fix:** 5σ gate. Cross-link microbit L400 #20 | validated-local |
| 18 | L400 | Simulation-based optimisation: search, ranking & selection and fair budgets | `labs/L400/18-sim-optimisation` | **grid** 0.042 / GP-lite + EI 0.090 / (μ+λ)-ES 0.088 mean gap (324 runs each, CRN). **Fault:** winner's curse (reported cost −0.47/day). **Fix:** OCBA stage on fresh streams. Fitness: budget fairness | validated-local |
| 19 | L400 | Surrogate models and emulation: fast what-ifs that know where they stop | `labs/L400/19-surrogates` | polynomial 0.037 / **GP-lite 0.042** / random features 0.049 holdout RMSE (noise floor 0.033). **Fault:** extrapolation (1.930 / 0.877 / 0.552 vs exact 6.015). **Fix:** envelope guard + simulation fallback | validated-local |
| 20 | L400 | Large-scale and parallel simulation: reproducible streams, checkpoints and result storage | `labs/L400/20-parallel-scale` | CSV / **SQLite batched** / Parquet; scaling + Amdahl. **Fault:** position-keyed streams change results after a resume. **Fix:** `SeedSequence(root, spawn_key=(s, r))` | validated-local (Parquet + multi-core pending-ci) |
| 21 | L400 | Model governance and V&V: model cards checked against evidence | `labs/L400/21-governance-vv` | prose / **checked model card** / full credibility assessment. Envelope utilisation ≤ 0.85 computed from evidence. **Fault:** heading-only gate publishes 4 overclaims. **Fix:** claim checks + hashes. **Agent assist:** drafts card text, code checks claims | validated-local (agent vs fake server only) |
| 22 | Capstone | Capstone: a digital twin of a service centre | `labs/L400/22-capstone` | M1-M6 scorecard PASS 6/6: lognormal inputs, Erlang C-verified DES, holdout validation, 221 agent-hours under the SLA, checkpointed parallel replications, a live twin re-planning +14 agent-hours, governance pack; agent only explains | validated-local (real model, macOS/Windows pending) |

L400 lesson data (adds `designBrief`, `options`, `decisionRecord`, `fitnessFunction`, `scalingLimits`; the capstone adds `architecture`, `milestones`, `rubric`, `fitnessFunctions`, `decisionRecords`) is in `content/L400.json`. Concept notes are in `content/concepts/L400/`. Each lab ships the UNFIXED design. `test_build_task.py` and `test_fitness.py` check the solution by default and your file with `BUILD_TARGET=mine`. ADRs (Nygard format) are in each lab's `decisions/`. Run the capstone with `python run_capstone.py` in `labs/L400/22-capstone`.

L300 lesson data (adds `failureLab`, `tradeOffs`, `observability`) is in `content/L300.json`; concept notes in `content/concepts/L300/`. Each L300 lab ships the UNFIXED code; the fix is the build task and lives only in `solution/<lab file>.py`. `test_build_task.py` checks the solution by default and your file with `BUILD_TARGET=mine` (PowerShell: `$env:BUILD_TARGET = "mine"`): it fails on the shipped file and passes after the fix. The earlier build tasks are now stretch tasks (`test_stretch.py`, same switch). `TestFailureLab` keeps each fault reproducible; `research/failure_proofs_L300.py` re-checks all five (shipped FAIL / solution PASS). New pins: `labs/L300/requirements.txt` (SALib 1.6.0, FMPy 0.3.32 on top of the L100 pins). Structured logs (JSON lines): lessons 12 (stretch), 15 and 16.

**Tools:** open-source learning tools (NetLogo, JaamSim, Mesa, SimPy, Xcos, OpenModelica, Orange, KNIME, JupyterLab, marimo, SALib) per lesson: lessons 2-5, 7-22. See `documentation/LEARNING-TOOLS.md` and each lesson's `learningTools` field. Cross-topic links are in `seeAlso` (lesson 3 ↔ distributed-systems #3, lesson 7 ↔ microbit #8, lesson 12 ↔ quantum-computing #15, lesson 13 ↔ quantum-computing #13, lesson 15 → microbit #13, lesson 16 → distributed-systems #16; every L300 lesson has 1-2 links; L400: 17 → microbit L400 #20, 18 → quantum-computing L400 #18, 19 → application-architecture L400 #21, 20 → ai-agents L400 #18, 21 → ai-agents L400 #21 and application-architecture #6, 22 → ai-agents L400 #20; within the topic 17-21 ↔ capstone 22, 18 ↔ 19, 20 ↔ L300 #16).

**Validation key:** `validated-local` = the main lab, tryIt and tests ran here (Linux). `validation.pendingCi` lists the files or tests that have not run yet (SimPy/SciPy/Mesa variants, real local model). `platforms` stays `expected` until CI runs on macOS and Windows.

L200 lesson data (adds `codeWalkthrough` and `buildTask`) is in `content/L200.json`; concept notes in `content/concepts/L200/`. Each L200 lab has `solution/` (reference solution) and `test_build_task.py` (the check). No new packages.

**Read first:** `documentation/CONCEPTS-PRIMER.md`. Before each lab read its concept note in `content/concepts/` (`conceptNote` in each lesson). Lesson data — steps, tryIt, checkYourself, equivalents, sources, validation — is in `content/L100.json`.

## L500 lesson map ("Theory & rigour": proofs and derivations each checked in code, ethics, primary literature)
| # | Level | Lesson | Lab folder | Theorems / content (checked numbers) | Validation |
|---|---|---|---|---|---|
| 23 | L500 | Foundations I: probability and stochastic processes | `labs/L500/23-probability` | WLLN via Chebyshev (0.0427 <= 0.25); CLT (KS 0.159 -> 0.012); Poisson -> exponential gaps from the axioms (mean 0.5025 vs 0.5); stationary distributions and M/M/1 from cut balance (L 3.919 vs 4.000). 9 problems | validated-local |
| 24 | L500 | Foundations II: numerical methods | `labs/L500/24-numerics` | Euler local O(h^2) / global O(h) with Lipschitz bound (order 0.990); RK4 8/8 order conditions, order 3.996; explicit Euler stability disc, stiffness (952 steps blow up, implicit 20 steps 1.9e-5); IEEE 754 rounding, cancellation, h* ~ sqrt(eps). 8 problems | validated-local |
| 25 | L500 | Foundations III: random number generation and Monte Carlo theory | `labs/L500/25-rng-monte-carlo` | Hull-Dobell (exhaustive m = 64/60/81) + RANDU's 15 planes; chi-square/KS (RANDU fails 3-D: X^2 151,465); MC 1/sqrt(N) (slope -0.500) + importance sampling (7,000x); antithetic covariance proof (30.9x predicted, 30.1x observed). 8 problems | validated-local |
| 26 | L500 | Ethics: models that make decisions about people | `labs/L500/26-ethics` | Case analysis of the 2020 England grading model (Ofqual, OSR) with Robodebt and CovidSim contrasts; ACM 2018, IEEE 7.8, AQuA Book 2025, NASA-STD-7009B; synthetic check: distribution error 0.0000 but 40.0% individual agreement. 6 problems | validated-local (essays human-graded) |
| 27 | L500 | Reading seminar: Metropolis & Ulam (1949) and Sargent (2010) | `labs/L500/27-readings` | Summaries, 5 guiding questions each, critical responses; branching-process companion (0.6842 +/- 0.0064 vs 0.6863). 6 problems | validated-local |

L500 lesson data adds `learningObjectives`, `theorems` (statement, proof, check script, real `checkOutput`), `problemSet` (full solutions), `rubric`, `caseStudy` (26), `readings` (27) and `codeCheck` (26, 27) in `content/L500.json`; concept notes in `content/concepts/L500/`. Run `python research/l500_checks.py` (re-runs every check, compares output, recomputes every problem-set and exam number), `python research/check_l500_qbank.py` and `python research/qbank_checks.py`.

**Course assessment pack** (`content/assessment/`): `syllabus.md` (14-week plan, weekly reading, weights labs 35% / problem sets 25% / exams 20% / capstone + oral defence + peer-reviewed ADRs 20%, policies, outcomes mapped to CS2023 KAs and ABET EAC 1-7 / CAC 1-6), `midterm.md` and `final.md` (7 and 8 questions with model answers and marks), `concept-inventory.json` (15 pre/post items), `capstone-oral-defence.md`, `peer-review-adr.md`, `team-roles.md`. Question bank: `content/qbank/L500.json` (48 MCQs).

## How to run the labs
```bash
python --version                         # 3.12 or newer
python -c "import numpy; print(numpy.__version__)"   # 2.5.3 used for validation
cd labs/L100/02-monte-carlo
python monte_carlo.py                    # compare with "Expected output" in the lab README
python try_it.py                         # the two tryIt experiments
python -m unittest -v                    # the lab's tests
```
- Main labs need only Python 3.12 and numpy; every random generator is seeded, so outputs match the READMEs exactly.
- Library equivalents — `simpy_queue.py` (SimPy 4.1.2), `falling_scipy.py` (SciPy 1.18.1), `schelling_mesa.py` (Mesa 3.5.1) — need `python -m pip install -r labs/L100/01-setup-workbench/requirements.txt`. Locally their tests are **skipped**, not passed.
- L200 labs run the same way from `labs/L200/<lab>`; `python -m unittest test_build_task -v` checks the build task.
- **Concept share** (REBALANCE-SPEC measure script, measured 2026-10-28 after L400): L100 concept 1376 / hands-on 6539 = 17.4% · L200 2039 / 8100 = 20.1% · L300 2652 / 12386 = 17.6% · L400 4119 / 19323 = 17.6% · whole topic 10186 / 46348 = 18.0%. Targets 20-25% / 25-30% / 30-35% / 35-40%. The notes are at full length (L400: 654-735 words, capstone 559) and are not padded; the gap is recorded in KNOWN-GAPS.
- L400 labs run the same way from `labs/L400/<lab>`. They need only numpy; Parquet (pyarrow 26.0.0) is CI-only. `labs/L400/cross_platform/` fingerprints every fixed L400 lab and the capstone.
- L300 labs run the same way from `labs/L300/<lab>`; library equivalents (`calibrate_scipy.py`, `sensitivity_salib.py`, `fmpy_cosim.py`) need `python -m pip install -r labs/L300/requirements.txt`.
- CI: `.github/workflows/labs.yml` installs the pins (wheels only) on Python 3.12.15 and runs every demo, tryIt script, equivalent and test suite on `ubuntu-latest`, `macos-latest` (Apple silicon) and `windows-latest`.

## Mac mini and Windows PC
- Full workstation setup (canonical commands for all topics): `../../shared/WORKSTATION-SETUP.md`.
- Install steps for both (Homebrew / winget, venv activation, optional Ollama) are in lesson 1 (`mac` / `windows` fields) and its lab README. Every lesson has `"platforms": {"mac": "expected", "windows": "expected"}` until CI has run on both.
- Lab code is cross-platform: `pathlib`, UTF-8 file reads, CRLF-safe parsing, ASCII-only output, no POSIX-only calls; the fake model server binds 127.0.0.1.
- `labs/L100/cross_platform/`, `labs/L200/cross_platform/` and `labs/L300/cross_platform/` check that every seeded result matches `golden.json` on each OS. `documentation/HARDWARE.md` covers RAM, cores and floating-point differences.

## Local agent (optional)
Lesson 21 `agent_assist.py` (L400): the local model drafts the model card's validity lines; code checks every claim against `evidence.json` and rejects overclaims. Capstone `agent_explain.py`: the model explains the staffing plan code already chose; any unverified number blocks publication.
Lesson 14 `agent_assist.py` (L300): the local model ranks the inputs from the sensitivity table; code ranks by the Sobol' total-order index, reports every position where the agent disagrees and flags unverified numbers.
Lesson 7 `agent_assist.py` (L200): the local model proposes which distribution fits from summary statistics; code fits every candidate, decides by the smallest KS distance (overruling the agent if needed) and flags unverified numbers in its explanation.
Lesson 6 `agent_assist.py`: a local model (Ollama; set `LOCAL_MODEL_URL` and `LOCAL_MODEL` as in WORKSTATION-SETUP) proposes a parameter sweep and explains the results; deterministic code validates the plan, runs the simulation and flags any quoted number not in the results table. Tests use only the deterministic fake server in `labs/_shared/local_agent/` (vendored from `kb/shared/local_agent`). The agent never runs code, decides, or receives secrets.

## Other files
- `documentation/LEARNING-TOOLS.md` — open-source GUI/no-code tools per lesson, licences, Mac/Windows installs.
- `documentation/VERIFIED-RESOURCES.md` — every source used, licence, date checked, score.
- `documentation/HARDWARE.md` — Mac mini vs Windows PC: wheels, RAM, cores, floating point.
- `documentation/KNOWN-GAPS.md` — what is unverified, pending CI, or simplified.
- `research/L100-evidence.md`, `research/L200-evidence.md`, `research/L300-evidence.md` — research questions, sources considered, key facts per lesson.
- `research/concept_examples_L200.py` — recomputes every number in the L200 concept notes (observed output in `concept_examples_L200_observed.txt`).
- `research/L400-evidence.md`, `research/concept_examples_L400.py` and `research/failure_proofs_L400.py` — L400 sources, concept-note numbers and fault FAIL / fix PASS for lessons 17-21.
- `research/concept_examples_L300.py` — recomputes every number in the L300 concept notes; `research/failure_proofs_L300.py` — fault FAIL / fix PASS for every failure lab; `research/verify_readmes_L300.py` — re-runs L300 labs against their READMEs.
- `research/concept_examples.py` — recomputes every number in the concept notes and primer.
- `research/hardware_measure.py` — measures the RAM numbers in HARDWARE.md; `research/agent_assist_observed.txt` — fake-server run of lesson 6 agent assist.
