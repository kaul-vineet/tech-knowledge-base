# Known gaps — Simulation L100

## Not run locally (pending-ci)
- **SimPy, SciPy and Mesa are not installed** in the validation sandbox (pip has no network). These files were written against the current docs but have **never been executed**: `labs/L100/03-discrete-event-queue/simpy_queue.py` (SimPy 4.1.2 `Resource` + generator processes), `labs/L100/04-time-stepped-physics/falling_scipy.py` (SciPy 1.18 `solve_ivp` with a terminal event), `labs/L100/05-agent-based-schelling/schelling_mesa.py` (Mesa 3.5.1 `CellAgent`, `OrthogonalMooreGrid`, `shuffle_do`). Their unittests, and lesson 6's SciPy check of the t-quantile 2.262, are **skipped** locally and run in CI.
- **Mesa API drift:** the stable docs show `Model.__init__(seed=...)`; the 4.0.0a0 "latest" docs use `rng=`. The lab pins 3.5.1 and uses `seed=`. `OrthogonalMooreGrid(..., torus=True, ...)` is taken from the API as used in the docs' Schelling example, which does not pass `torus`; the keyword itself is not confirmed in retrieved text.
- **CI workflow** (`.github/workflows/labs.yml`, now a 3-OS matrix) has not run. Action tags `actions/checkout@v7` / `actions/setup-python@v7` and Python 3.12.15 copy the distributed-systems domain's workflow; not re-verified here. Mesa's and SciPy's dependency resolution with `numpy==2.5.3` was not tested.
- GitHub runs workflows only from the repository root `.github/workflows/`; move/rename `labs.yml` if this domain shares a repo with others.

## Mac mini / Windows (platform addendum)
- **Nothing ran on macOS or Windows.** All lessons are `platforms: expected`; the CI matrix (`macos-latest` arm64, `windows-latest` x64, `ubuntu-latest`) is written but has not run. The Homebrew, winget and venv commands are checked against official pages, not executed.
- **Wheel file names not retrieved.** PyPI's file lists and JSON API returned no text. Evidence instead: SciPy's toolchain page lists official macOS arm64 and Windows builds; numpy's classifiers list macOS and Windows; SimPy 4.1.2 and Mesa 3.5.1 are `py3-none-any`. CI uses `pip --only-binary=:all:` so a missing wheel fails the job. Mesa 3.5.1's dependency list was not retrieved (GitHub/raw fetch empty), so wheels for its dependencies are also proven only by CI.
- **Windows on ARM64** and **Intel Macs** not covered. Ollama's Windows docs page returned no text, so Windows GPU support for Ollama is not stated. Winget id `Python.Python.3.12` was confirmed by its folder in microsoft/winget-pkgs. Ollama on Windows now uses the `OllamaSetup.exe` installer (shared WORKSTATION-SETUP), because the `Ollama.Ollama` winget manifest lags (0.34.2 vs 0.40.12).
- **Cross-platform identical outputs** rely on `labs/L100/cross_platform/golden.json` (written on Linux). If macOS or Windows differ in CI, the cause is most likely libm (`math.log` in `expovariate`) or NumPy reductions; see HARDWARE.md. Lesson 6's hash now covers values rounded to 9 decimals (changed from raw `repr`; README updated).
- RAM figures are tracemalloc peaks on Linux (Python/numpy allocations only). Mesa per-agent memory was not measured (Mesa not installed).

## Local agent (lesson 6 agent assist)
- Tested only against the deterministic fake server (vendored helper + one topic rule `[[SIM-SWEEP]]`, documented in its header). No real model was run; real replies, latency and quality on the Mac mini or Windows PC are untested.
- The number check matches numbers, not meaning: a sentence that quotes correct numbers but draws a wrong conclusion passes. The agent is used only to propose and explain; acceptance is decided by code.

## Simulations and simplifications
- Lesson 3/6 queues are M/M/1 (exponential, independent times). Real coffee-shop or API traffic is not checked against data.
- **No real measured data** is used anywhere. Lesson 6 validates only against the analytic M/M/1 formula; comparison with field data is described but not demonstrated (no openly licensed queue dataset was selected).
- Lesson 4: constant g = 9.8 m/s², sea-level air density 1.225 kg/m³, Cd = 1.05 and A = 0.09 m² for a 2 kg box are illustrative values chosen for the lab, not taken from a measured source. `time_to_ground` stops at the first step below 0, so fall time is quantised to dt.
- Lesson 5 Schelling uses a 30×30 wrapping grid, 10% empty cells, and moves unhappy agents to random empty cells (Mesa's example does the same; NetLogo's model moves agents locally).
- Lesson 3's -3.2% gap to the formula is a single long run with autocorrelated waits and no warm-up deletion; lesson 6 shows the replication approach.

## Unverified or single-sourced facts
- **t quantile 2.262 (95%, 9 d.o.f.)** is a standard table value, not found in retrieved text; CI checks it against `scipy.stats.t.ppf`.
- **Closed form |v(t)| = Vt·tanh(g t / Vt)** for falling from rest with quadratic drag is used only as an independent test oracle. NASA's page derives the ascent counterpart (tan) and the terminal velocity; the descent tanh form was not found in retrieved text. The lab's RK4 agrees with it to 6 decimals.
- **RK4 formulas** come from the Berkeley chapter 22.5 text shown in a web_search result; direct web_fetch of that page returned no text. The NUS M/M/1 note was also read only via web_search.
- **NetLogo** "30% wanted → ~70% similar" comes from the model's info page; our numpy model gives 75.4% with different grid and move rules — consistent in direction, not identical.
- **Licences**: for most docs pages the licence is not visible in the retrieved text (marked in VERIFIED-RESOURCES). Owen's book and Sargent's paper are copyrighted and are linked, not copied.

## Spec deviations
- Main lab files are 41-77 lines (spec: typically 15-60): `des_queue.py` (68), `falling.py` (75) and `schelling.py` (77) exceed 60 because they hold the event loop, three integrators, or the grid model plus the demo in one copy-and-run file.
- `validation.status` is `validated-local` for lessons 3-6 even though each has a pending-ci part (library equivalent or SciPy check). Since 2026-10-28 every such lesson (1, 3-11) lists the unrun files/tests in `validation.pendingCi` (review F07).
- Lesson 2 now has 3 troubleshooting rows (L100 spec: 1-2), added on purpose: review F21 flagged it as the thinnest lesson.
- Concept-note heading count is 4 as required; each note starts with a bold title line instead of an H1.

## Dropped / deferred
- SIR epidemic ABM (Schelling chosen because Mesa and NetLogo both ship it as a reference model).
- Pi estimation kept only as a bonus line in lesson 2's `try_it.py`.
- Input-distribution fitting, SimPy priority/preemptive resources, warm-up detection, variance reduction, FMI co-simulation, calibration, digital twins: deferred to L200-L400 (see primer concept map).
- Commercial simulation tools: not used.

## L200 (lessons 7-11)

### Not run locally (pending-ci)
- **Never executed (SciPy/SimPy not installed offline):** `07-input-modelling/fit_scipy.py`, `08-multi-server-queue/simpy_mmc.py`, `09-adaptive-ode/ode_scipy.py`, `11-supply-chain-inventory/simpy_inventory.py`, and lesson 10's `scipy.stats.t.ppf` check. Their tests are **skipped** locally (6 skips in total) and run in the CI job `python-labs-l200`. `simpy_inventory.py` was logic-checked against a minimal hand-written stand-in scheduler, which is not SimPy: orders, lost sales and cost matched numpy for 5 replications × 3 policies. SimPy's own `Container` semantics are proven only by CI.
- **macOS / Windows:** all L200 lessons are `platforms: expected`. `labs/L200/cross_platform/golden.json` was written on Linux. The adaptive solver's step and rejection counts (lesson 9) are the values most likely to change if libm `exp`/`log` differ in the last bit.
- **Agent assist (lesson 7)** was tested against the fake server only (new rule `[[SIM-FIT]]`, documented in the vendored server's header). No real model was run.

### Data and simplifications
- **No real measured data.** `service_times.csv` is synthetic (lognormal, seed 2026, `make_data.py`), so the "right" family is known. Real data may fit no standard family; the lab's answer then would be resampling or a mixture, which is not covered.
- KS with estimated parameters: the lab uses D only to rank candidates and prints 1.36/√n as a reference. A valid p-value would need a parametric bootstrap (not implemented). Anderson-Darling is not covered.
- Lesson 8 is steady-state M/M/c with no abandonment, breaks or time-varying arrivals.
- Lesson 9: Dormand-Prince is implemented without FSAL reuse (7 evaluations per step instead of 6) and without dense output. Events in the buildTask use bisection by re-stepping, not SciPy's dense-output root finding. The stiffness demo uses backward Euler (closed form, linear ODE) rather than a general implicit solver.
- Lesson 10: the warm-up rule (first entry into a ±5% band around the second-half level) is a simple heuristic of ours, not Welch's published procedure, which is graphical. tryIt 2 shows it proposing 961 for one seed set. The t quantile uses a 2-term Cornish-Fisher expansion, checked against table values 2.262/2.093/2.023/1.990 (±0.005) and against SciPy in CI. No retrieved source states the expansion.
- Lesson 11: costs (0.10/25/4.00), demand (Poisson 8 × weekly Gamma(4, 0.25) factor) and lead times (uniform 1-4 days) are illustrative, not from a real shop. Lost sales only (no backorders). Review is daily (periodic), whereas Sigman's notes model continuous review.

### Unverified or single-sourced facts
- Lotka–Volterra conserved quantity (used as an accuracy check in lesson 9) and the shifted-exponential MLE (loc = min, rate = 1/(mean − min), lesson 7 buildTask) are standard results not found in retrieved text. Both are checked numerically by tests.
- Erlang B (buildTask, lesson 8) was seen only in a web_search result of the Technion lecture. The simulation agrees: 0.269 vs 0.268.
- Law WSC 2015 was read via the web_search result (abstract and replication section), not fetched in full.

### Spec deviations
- **Concept share 22.1%** (target 25-30%). Notes are at the 400-word cap (395-399 words). The hands-on side is dominated by the `code` field (~2,470 words) plus the new L200 fields (`codeWalkthrough`, `buildTask`) and lesson 7's agent assist.
- Main lab files are 67-91 lines. `fit_inputs.py` (91) is one line over the ~90 guideline.

## Update pass 2026-10-28: learning tools + review fixes

### Learning tools (pending manual runs)
- None of the GUI tools ran here: NetLogo, JaamSim, Mesa SolaraViz, Scilab/Xcos, OpenModelica, Orange, KNIME, JupyterLab, marimo. SimPy also never ran (pending-ci). Every `learningTools[].expected` gives the lab's real value and says "pending a manual run". Tool facts come from the shared catalogue only.
- Not verified, so do not state as fact: Xcos solver and tolerance settings; KNIME percentile node names; which fitted curves Orange's Distributions widget offers; whether SolaraViz needs extra packages beyond `mesa`; the JaamSim 3D view on an Apple-silicon JDK; OpenModelica GBODE's default method.
- NetLogo's Segregation model uses its own licence (CC BY-NC-SA 3.0). It is fine for learning, but do not copy it into this repo.
- The new helpers `export_csv.py` (labs 2 and 10) and their tests ran here. The CSVs they write are not committed (see `.gitignore`).

### Review findings
- **Fixed:** F01 (README status line), F03 (every L100 `next` names an existing L200 lesson; L200 `next` = "L300 (planned): ..."), F05/F19 (lesson 1 uses the shared WORKSTATION-SETUP commands: `brew install ollama` + `brew services start ollama`, Windows `OllamaSetup.exe`, `LOCAL_MODEL_URL`/`LOCAL_MODEL`, `PYTHONUTF8`), F07 (`validation.pendingCi`), F08 (`seeAlso` in lessons 3 and 7), F10 (official NPTEL page), F14/F16 (VERIFIED-RESOURCES clean-up), F21 (third troubleshooting row in lesson 2), F27 (`__pycache__` removed, `.gitignore` added).
- **Recorded, not fixed:** F01 CI run itself. The workflow lives in `.github/`, which is owned by the root-CI job and is not edited here; `export_csv` tests run only if CI discovers all `test_*.py`. F09 concept share (measured after this pass: L100 17.4% (was 19.7%), L200 20.2% (was 22.1%); targets 20-25% and 25-30%). The added `learningTools`/`seeAlso` fields are hands-on content, and notes are not padded.
- **F10 detail:** the official course page lists "Lec 15: M/M/c Queues, Erlang Delay Formula". The worked value C = 0.702 was read in the lecture transcript from the earlier mirror. The lab's Erlang C is also checked by an independent recomputation (Wq 1.079).
- **L300 candidates (F03):** agent-based follow-up (Mesa data collection, BehaviorSpace-style sweeps, SIR), calibration against measured data, variance reduction and batch means, priorities and abandonment, FMI co-simulation, (s, S) optimisation with ranking and selection.

## L300 (lessons 12-16), 2026-10-28

### Not run here (pending CI or manual)
- **Library equivalents:** SciPy (`test_exact_overtime_by_numerical_integration`, `calibrate_scipy.py`), SALib 1.6.0 (`sensitivity_salib.py`, 2 tests) and FMPy 0.3.32 (`fmpy_cosim.py` API check) are not installed offline. Their tests are skipped locally and listed in each lesson's `validation.pendingCi`.
- **OpenModelica FMU:** `RoomThermal.mo` was not compiled and `export_fmu.mos` was not run anywhere. Running it with `omc` from a terminal is our assumption; the user guide shows the same commands in OMShell/OMEdit. The FMU-vs-Python comparison test only runs if `RoomThermal.fmu` exists. OpenModelica's default co-simulation solver is forward Euler with one step per communication step, so FMU numbers will differ slightly.
- **Xcos exercise (lesson 15):** block names (sample-and-hold, saturation) and solver settings were not checked.
- **macOS/Windows:** every lesson stays `platforms: expected`. Lesson 16 used the `spawn` start method on Linux, which is the default on Windows and macOS, but it did not run on those systems.
- **Multi-core timing:** the sandbox has 1 CPU, so the lesson 16 pool is slower than numpy and the README timings are this machine's only. Runs gave numpy speed-ups between 7.0× and 25.6×, so timing noise is large here.

### Unverified or single-sourced facts
- The Saltelli 2010 (S1) and Jansen (ST) estimator formulas are now confirmed in the primary paper (Saltelli et al. 2010, Table 2, read 2026-10-28; R3-13). Our tests also match the analytic indices within 0.02. Centring the outputs before estimating is our choice (it cut S1 noise about threefold at N = 4,096). We could not check whether SALib does the same, because the `sobol.py` source fetch returned nothing.
- SALib uses a scrambled Sobol' sequence while we use pseudo-random numbers. The CI tolerance of 0.03 on ST is our assumption.
- The SALib and FMPy dependency lists, and FMPy's licence, were not shown on the retrieved PyPI pages.
- The Erlang closed form for expected overtime (lesson 12) is a standard result. A 400,000-run test checks it here, and SciPy integration checks it in CI.
- The lesson 15 stability bound h < τ·ln(K/(K−1)), and the Gauss–Seidel bound τ·ln((K+1)/(K−1)), are our own derivations for a P-loop with zero-order hold. The PI controller moves the observed threshold slightly (240 s stable, 300 s not, against 313 s). Tests check the bound numerically, not symbolically.
- The 50% relative-standard-error rule in `param_report()` (lesson 13) is our heuristic. The Gauss–Newton covariance s²(JᵀJ)⁻¹ is approximate, and NIST says nonlinear intervals are "only approximately correct".

### Simplifications
- The lesson 15 units are Python classes with an FMI-like interface. They have no status codes, no event mode, no get/set FMU state, and FMI 3.0 (`FMU3Slave`) is not used. The master is fixed-step Jacobi; the adaptive master re-runs the whole simulation instead of rolling back.
- The lesson 13 data is synthetic (two-exponential truth plus Gaussian noise) with no sensor drift or outliers. Only one holdout split is used, with no rolling-origin validation.
- Lesson 14 assumes independent, uniform inputs. Interactions with correlated inputs are not covered.
- Lesson 16 parallelises replications only, not a single model run.

### Spec deviations
- **Concept share 20.3%** (target 30-35%). The notes run 498-527 words by `wc -w`, inside 450-550. The hands-on side holds 5 lessons with `failureLab`, `tradeOffs`, `observability`, 6-7 steps and 6-7 walkthrough items each, plus lesson 14's agent assist. The notes are not padded.
- `learningTools`: lessons 12, 13 and 16 have one tool each; lessons 14 (marimo, SALib) and 15 (OpenModelica, Xcos) have two. FMPy's GUI stays out (non-OSI licence variant).

## L300 update pass (review R3, 2026-10-28)

### Fixed here
- **R3-06:** every L300 lab now ships the UNFIXED code (`antithetic_loop()`, `select()`, `screen()`, `COMM_STEP_S = 900`, `tasks_for()`); the fix is the build task and lives only in `solution/<lab file>.py`. `test_build_task.py` checks the solution by default and the learner's file with `BUILD_TARGET=mine`: on the shipped files 2/3, 2/2 (11 failures with subtests), 2/2, 2/2 and 2/3 tests fail. The former build tasks are stretch tasks (`test_stretch.py`, same switch). `TestFailureLab` keeps each fault reproducible without depending on the learner's file. Golden fingerprints are unchanged.
- **R3-08:** `learningTools.name` now equals the catalog name (marimo, JupyterLab (+ JupyterLab Desktop), OpenModelica (OMEdit), Scilab + Xcos, SALib); versions moved to the install fields.
- **R3-17 / R3-05:** L300 #12-15 and L200 #7-10 `next` now read "L300 #NN <exact title> (why)".
- **R3-04 (simulation side):** seeAlso added to all five L300 lessons: #12 ↔ #16 and #13 ↔ #14 within the topic, #12 → quantum-computing #15, #13 → quantum-computing #13, #15 → microbit #13 and #16 → distributed-systems #16.
- **R3-13:** Wikipedia (Sobol' indices) replaced by Saltelli et al. 2010 (primary).
- **R3-14:** concept share reported in `documentation/README.md`.
- **Tools:** SALib added to lesson 14 (CHECK).

### Recorded, not fixed
- **R3-04, other side:** quantum-computing #13 and #15 already link back to simulation #13 and #12. Two back-links belong to their topics and are not edited here: microbit #13 → simulation L300 #15 (sampling period vs dynamics) and distributed-systems #16 → simulation L300 #16 (it links simulation L200 #8 today). Not linked on purpose: distributed-systems L200 #9 (consistent hashing). It shares no concept with #12 or #16, which are about estimator variance and random streams, not key placement.
- **R3-01:** still nothing run on macOS/Windows; CI also checks that `BUILD_TARGET=mine` fails on the shipped files.
- **R3-14:** concept share after this pass: L100 17.4%, L200 20.1%, L300 17.6%, topic 18.3% (targets 20-25 / 25-30 / 30-35%). The notes are at their caps and are not padded.
- **L400 candidates (from stale L200 `next` pointers, R3-05):** priorities and abandonment, staffing optimisation, batch means, (s, S) optimisation with ranking and selection, agent-based follow-up (data collection, sweeps, SIR).


## L400 (lessons 17-21) + capstone 22, 2026-10-28

### Not run here (pending CI or manual)
- **macOS and Windows.** Every L400 lesson stays `platforms: expected`. Lessons 20 and 22 use the `spawn` start method (the default on both systems), but only on Linux with 1 CPU. `labs/L400/cross_platform/golden.json` was written on Linux x86_64.
- **Parquet.** `to_parquet.py` and `TestParquetExport` need pyarrow 26.0.0, which is not installed offline, so the test is skipped locally.
- **Multi-core scaling.** The sandbox has 1 CPU, so `scaling.py` gave f = 1.00 and speed-ups below 1. All README timings come from this slow, shared, network-mounted machine. One example: committing each SQLite row took 22.8 s per 5,000 rows here, and it will be far faster on a local SSD.
- **Real local model.** Lesson 21 `agent_assist.py` and capstone `agent_explain.py` were tested only against the deterministic fake server. Their rules (`[[SIM-CARD]]`, `[[SIM-STAFF]]`) are registered through the shared server's `EXTRA_RULES` hook, so `labs/_shared/local_agent` is unchanged. The prompts avoid the word "json" on purpose, because the fake server's JSON rule runs before `EXTRA_RULES`.
- **GUI tools.** None of the L400 tool exercises ran here: OpenModelica, marimo, SimPy, JupyterLab, Orange, KNIME, SALib, JaamSim. Orange and KNIME widget/node names and JaamSim's abandonment support were not verified.

### Unverified or single-sourced facts
- **OCBA rule.** It is quoted from Fu, Chen & Shi (WSC 2008, Figure 3). The original Chen et al. (2000) text could only be fetched up to its introduction. `test_ocba_by_hand` checks our implementation of the quoted formula.
- **Python docs.** The `sqlite3` connection context manager (it commits or rolls back and does not close) and the `Pool.imap_unordered` ordering were not in the fetched docs, because the page was truncated. The lab's tests prove the behaviour we rely on: the rollback is shown by `test_crash_evidence`, and order independence by the checksums.
- **Partly-read sources.** NASA-STD-7009B: only the catalogue page was read. Model Cards (Mitchell et al.): only the abstract was read. Gans, Koole & Mandelbaum: the text stopped before §4, so the Erlang A and square-root-staffing sections were not read. Rahimi & Recht: the spectral density N(0, I/ℓ²) is our derivation from the quoted σ_p² = 2dγ.
- **Thresholds of our own.** The 10% accuracy requirement (lesson 21), the 5σ innovation gate and h = 8 (lesson 17), δ = 0.10/day (lesson 18) and SD_MAX = 0.10 (lesson 19) are our design choices, each justified by the lab's measurements. None is a standard value.
- **The lesson 18 referee.** `truth.json` has its own standard error of 0.085 per design, shared across designs because it uses common random numbers. The fixed selection stage's 12-macro bias of -0.143 is within about 2 referee SEs of zero, and that is all the lab claims.

### Simplifications
- **Lesson 17.** One zone, a linear 2-state Kalman filter with fixed Q and R, a scalar heater input and a replayed (not live) feed. The micro:bit hand-off to microbit L400 #20 is described, not wired.
- **Lesson 19.** Two inputs and a box envelope. There is no convex-hull or nearest-run check.
- **Capstone.** Staffing is hourly, using the stationary approximation with a full-day repair. There is one skill and no retrials, callbacks or shift rostering. The KPI report is simulated from the same hidden parameters as the call log, not call by call from it. Patience is weakly identified (any value from 3.0 to 5.5 fits; the truth is 3.0), and M4 shows the decision is insensitive to it.

### Spec deviations
- **Concept share.** Measured with the REBALANCE-SPEC script: L400 concept 4,119 against hands-on 19,323 = 17.6% (target 35-40%). The notes are at full length: 654-735 words for 17-21 and 559 for the capstone. The L400 lesson objects carry the extra design fields (designBrief, options, ADR, fitnessFunction, scalingLimits), and the notes are not padded.
- **Run time.** Main lab files are 113-144 lines. Some suites are slow on this sandbox: lesson 20 takes about 7 minutes and the capstone about 2 minutes, because process pools start fresh interpreters on 1 CPU.

### L400 candidates (further study after the capstone)
- Priorities and multi-skill routing in the service centre (skills-based routing), plus callbacks and retrials.
- Shift rostering on top of hourly staffing (an integer programme against simulated requirements).
- Batch means and steady-state output analysis for long single runs.
- Agent-based follow-ups (Mesa data collection, BehaviorSpace sweeps, SIR), carried over from earlier candidate lists.
- Multi-zone twins (multi-state or unscented Kalman filters) on real micro:bit telemetry (microbit L400 #20).
- Indifference-zone procedures with guarantees (KN) next to OCBA, and noise-aware Bayesian optimisation.

## L500 (lessons 23-27: theory, ethics, readings) + assessment pack, 2026-10-30

### Not run here (pending CI or manual)
- **macOS and Windows.** All five L500 lessons stay `platforms: expected`. The new CI job `python-theory-l500` runs every check on all three OSes. The exact-output comparison runs on Linux only, because a different libm may change last digits (notably the float32 Euler table in `t4_floating_point.py`). The scripts' own assertions run everywhere.
- **Root CI.** `kb/.github/workflows/simulation.yml` is generated by `tools/sync_root_ci.py`. This build must not edit `kb/.github/` or `kb/tools/`, so the new L500 job reaches the root workflow only after someone runs `python tools/sync_root_ci.py`. `tools/check_qbank.py` still reads L100-L400 only, so `research/check_l500_qbank.py` applies the same rules to L500. `tools/build_site.py` already reads L500, the assessment files and the concept inventory: a test build to a scratch path succeeded (6.24 MB) and kb/site was left untouched. Two template limits remain. The template does not render the `codeCheck` field of lessons 26-27, so their outputs appear only in the lab READMEs. And because the template treats `rubric` as an L400 design field, L500 lessons may also show an empty "Measure/Pass" rubric table.

### Sources and facts not fully verified
- **NASA-STD-7009B.** Only the front matter and table of contents of the public PDF were read. The credibility factors come from the table of contents, and §4.3.8 ("M&S results reporting to decision makers") was seen as a heading only.
- **Robodebt.** The official report PDFs did not load. Facts come from the report landing page plus a CC BY 4.0 copy of the report, and the 2019 Amato consent orders are cited as described in the report's Letters Patent.
- **Search-only sources.** Gallager ch. 2 (MIT 6.262) is further reading only. Imperial College Report 9's PDF was not fetched, so CovidSim is cited through its repository and the Nature (2020) article. The CODECHECK certificate was not fetched.
- **Metropolis & Ulam (1949).** Read on JSTOR, which has no open licence. Students need JSTOR access; open copies seen in search results are JSTOR printouts and are deliberately not linked.
- **ABET.** The EAC 2026-27 criteria page was search only (the 2025-26 wording was used). The CAC 2026-27 page was read. Wording is paraphrased because the criteria are "all rights reserved".
- **UK data-protection law** (UK GDPR Art. 22, automated decision-making) is relevant to lesson 26 but was not retrieved, so it is not cited. Add it with a primary source in the next pass.

### Spec deviations and design choices
- **14-week plan.** L500-SPEC refers to a 14-week plan "from the review", but neither review file in kb/ contains one. `content/assessment/syllabus.md` therefore designs the plan so that each theory lesson lands next to the lab that uses it.
- **Problem sets for 26 and 27.** L500-SPEC defines problem sets mainly for lessons 23-25. Lessons 26 and 27 also have problem sets of 6 problems each (short-answer, essay and calculation), so the "problem sets 25%" weight covers them.
- **`codeCheck` field.** Lessons 26 and 27 add a `codeCheck` field (`check`, `checkOutput`, `purpose`). Its scripts are a synthetic illustration for the case (not Ofqual's model or data) and a branching-process companion to the 1949 reading.
- **Proof depth.** Theorems 23.2 (CLT), 23.4(a) (finite-chain ergodic theorem), 24.2 (the general order conditions) and 25.1 (Hull-Dobell sufficiency) are proof sketches with a cited full proof. Each is checked numerically, and for Hull-Dobell exhaustively for m = 64, 60 and 81.
- **Corrections during the build.** These are recorded in `research/L500-evidence.md`:
  - 23-P8 moved from t = 110 to t = 130, because the CLT is almost exact at 1 SD.
  - Python 3.12+ `sum()` compensates float sums, so the round-off demo uses `+=`.
  - The RANDU 3-D test was enlarged to 20³ cells, because 10³ cells were not decisive.
  - The float32 Euler table keeps a lucky cancellation at 10⁵ steps and says so.
- **Concept share.** The REBALANCE-SPEC measure does not apply to L500. These lessons are theory by design, and the notes meet L500-SPEC's own word ranges (23: 1,062; 24: 1,142; 25: 1,105; 26: 938; 27: 575 words).

