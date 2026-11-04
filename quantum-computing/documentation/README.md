# Quantum computing (applied) — start here

**Status: not yet run on macOS or Windows; CI matrix pending.** No Qiskit/Cirq/Aer/Mitiq/PennyLane/QDK code in this topic has run yet (`pending-ci`); the L300 and L400 main labs and the capstone are numpy (+ cryptography) only and ran here (`validated-local`). Each lesson lists what is still unrun in `validation.pendingCi`.

**What this covers:** writing, running and checking small quantum circuits as a software engineer: build circuits in code, run them on a local simulator, read and test the results, and move circuits between tools. It is about applying the technology, not research or theory. Everything runs on simulators. You don't need a cloud account or hardware.

**Stack (pinned, checked on PyPI 2026-10-28):** Python 3.12 (3.11+) · qiskit 2.6.1 (labs run on its reference `StatevectorSampler`) · qiskit-qasm3-import 0.6.0 · cirq 1.7.0 · numpy for independent cross-checks. qiskit-aer 0.18.2 is optional for L100–L200 (reduced-maintenance mode); L300 uses it for the noise-model SDK path. L300 adds scipy 1.18.1 (COBYLA) and, in a separate venv, mitiq 1.1.0 and pennylane 0.45.1. L400 adds cryptography 50.0.2 (ML-KEM-768 for lesson 21) and, in its own venv, qdk 1.33.1 + pandas 3.1.0 for the QDK resource estimator.

**Setup:** lesson 1 uses the canonical commands from `../../shared/WORKSTATION-SETUP.md` (same for every topic, incl. `LOCAL_MODEL_URL` / `LOCAL_MODEL` for agent assist).

**Learning tools:** open-source tools that let you see or check each lab's result (Qiskit visualization, Microsoft QDK, the openqasm3 parser, qiskit-qasm3-import, JupyterLab, marimo, Mitiq): `LEARNING-TOOLS.md`. Lessons that use one have a `learningTools` field; the Tools column below lists them.

## L100 lesson map ("Run it": copy, run, observe)

| # | Level | Lesson | Lab folder | Tools | Validation |
|---|---|---|---|---|---|
| 1 | Setup | Set up your quantum environment | `labs/L100/01-setup-environment` | — | pending-ci |
| 2 | L100 | Qubits and gates in code (X, H, measure) | `labs/L100/02-qubits-and-gates` | Qiskit visualization | pending-ci |
| 3 | L100 | Shots, counts and probability (seeding) | `labs/L100/03-shots-counts-probability` | Qiskit visualization, JupyterLab | pending-ci |
| 4 | L100 | Entanglement with a Bell pair | `labs/L100/04-bell-pair-entanglement` | Qiskit visualization | pending-ci |
| 5 | L100 | Portable circuits with OpenQASM 3 / 2 | `labs/L100/05-openqasm-portability` | openqasm3 parser, QDK | pending-ci |
| 6 | L100 | Same circuit, two frameworks (Qiskit vs Cirq) | `labs/L100/06-same-circuit-two-frameworks` | qiskit-qasm3-import, QDK | pending-ci |

Lesson data: `content/L100.json`. To regenerate it after editing a lab, run `python tools/build_l100_json.py` (the `code` field is copied from the lab file).

## L200 lesson map ("Build it": change and combine, simulator only)

| # | Level | Lesson | Lab folder | Build task | Tools | Validation |
|---|---|---|---|---|---|---|
| 7 | L200 | Bernstein–Vazirani as a pattern (oracle construction) | `labs/L200/07-bernstein-vazirani` | add a bias bit | — | pending-ci |
| 8 | L200 | Small Grover search (iterations vs success) + agent assist | `labs/L200/08-grover-search` | search by predicate | QDK | pending-ci |
| 9 | L200 | The QFT as a building block (vs numpy DFT, inverse) | `labs/L200/09-qft-building-block` | read a period | — | pending-ci |
| 10 | L200 | Parameterized circuits and sweeps (fit ⟨Z⟩) | `labs/L200/10-parameterized-circuits` | offset parameter | — | pending-ci |
| 11 | L200 | Transpiling to a device layout (GenericBackendV2) | `labs/L200/11-transpile-to-device` | GHZ chain for a line | Qiskit visualization | pending-ci |

L200 reuses the lesson 1 environment; no new packages. Each lab has a main file, `crosscheck_numpy.py` (on the shared numpy simulator `labs/_shared/qsim`), `try_it.py`, a reference `solution_*.py` and `test_build_task.py`. To check your own build-task file: `BUILD_TASK_MODULE=my_file python -m unittest test_build_task -v` (PowerShell: `$env:BUILD_TASK_MODULE = "my_file"; python -m unittest test_build_task -v`). Lesson data: `content/L200.json`, regenerated with `python tools/build_l200_json.py`; concept notes in `content/concepts/L200/` (numbers from `research/L200_worked_examples.py`); evidence in `research/L200-evidence.md`.

## L300 lesson map ("Harden it": failure modes, testing, observability, trade-offs; simulator only)

Each lab starts from code that works, injects a seeded fault, shows the failure, and hardens the code (`failureLab`, `tradeOffs`, `buildTask` = the hardening change). Main labs are numpy-only (density-matrix simulator `labs/_shared/qsim/density.py`) and ran locally; each has an SDK file that runs in CI.

| # | Level | Lesson | Lab folder | Fault → fix | SDK path (CI) | Tools | Validation |
|---|---|---|---|---|---|---|---|
| 12 | L300 | Noise models: how Bell and GHZ results degrade | `labs/L300/12-noise-models` | exact-outcome test fails under noise → model-based statistical check | Qiskit Aer NoiseModel | Qiskit visualization | validated-local (+ pending-ci) |
| 13 | L300 | Error mitigation: readout correction and ZNE | `labs/L300/13-error-mitigation` | too few shots → negative probabilities → constrained least squares | Mitiq 1.1.0 | JupyterLab, Mitiq | validated-local (+ pending-ci) |
| 14 | L300 | QAOA on MaxCut vs the classical optimum | `labs/L300/14-qaoa-maxcut` | stuck in a local minimum → warm start + restarts | Qiskit + scipy COBYLA | marimo, Qiskit visualization | validated-local (+ pending-ci) |
| 15 | L300 | A hybrid variational loop (VQE) under shot noise + agent assist | `labs/L300/15-hybrid-vqe-loop` | shot noise breaks finite differences → SPSA | Qiskit primitives + COBYLA | JupyterLab | validated-local (+ pending-ci) |
| 16 | L300 | A quantum classifier vs a classical baseline | `labs/L300/16-quantum-classifier` | flat gradients at scale → near-identity init | PennyLane 0.45.1 | marimo | validated-local (+ pending-ci) |

Observability: lessons 12, 13 and 14 print JSON lines; lessons 15 and 16 also write them to `logs/*.jsonl` next to the lab. Prove each fix with `BUILD_TASK_MODULE=<naive lab module> python -m unittest test_build_task` (fails) and `python -m unittest test_build_task` (passes); every README shows both runs. Lesson data: `content/L300.json`, regenerated with `python tools/build_l300_json.py`; concept notes in `content/concepts/L300/` (450–550 words; numbers from `research/L300_worked_examples.py`); evidence in `research/L300-evidence.md`. SDK installs: `labs/L300/requirements.txt` (L100 pins + scipy) and, in a separate venv, `labs/L300/requirements-extras.txt` (Mitiq brings its own Cirq).

## L400 lesson map ("Design it": decisions under constraints; simulator only) + capstone

Each lesson states a design brief, compares 2-3 options with numbers its lab measured, records the decision as an ADR (Nygard format, `docs/adr/` in the lab) and keeps it true with a fitness test (`test_fitness.py`). The shipped lab file is unfixed; the build task is the change that makes the decision true. Check your file with `BUILD_TARGET=mine python -m unittest test_build_task test_fitness -v` (PowerShell: `$env:BUILD_TARGET = "mine"; ...`); `BUILD_TASK_MODULE=<lab module>` shows the fail-before proof. Time-dependent numbers come from a FakeClock, so no test depends on wall-clock time.

| # | Level | Lesson | Lab folder | Decision (ADR) | Fitness function | SDK path (CI) | Tools | Validation |
|---|---|---|---|---|---|---|---|---|
| 17 | L400 | Hybrid quantum-classical architecture: orchestrator, job queue and backend adapter | `labs/L400/17-hybrid-architecture` | batched jobs + structural transpile cache + idempotent retries | jobs ≤ steps, 1 transpile, wall ≤ 90 s | Qiskit StatevectorSampler PUBs | marimo, JupyterLab | validated-local (+ pending-ci) |
| 18 | L400 | Benchmarking honestly against classical solvers | `labs/L400/18-benchmark-vs-classical` | same budget + seeds, medians; ties go classical | comparison method (budget, seeds, reproducible) | Qiskit sampling | marimo, JupyterLab | validated-local (+ pending-ci) |
| 19 | L400 | Resource estimation: logical vs physical qubits and feasibility | `labs/L400/19-resource-estimation` | budget-derived code distance + feasibility classes | p_fail ≤ 1 %, pinned decision table | QDK `qdk.qre`, Qiskit counts | QDK, JupyterLab | validated-local (+ pending-ci) |
| 20 | L400 | Error-aware compilation: layout, routing and a depth budget | `labs/L400/20-error-aware-compilation` | noise-aware layout + reliable routing + CX cancellation | depth ≤ 22, ESP ≥ 0.75, equivalent | Qiskit Target, levels 0-3 | Qiskit visualization | validated-local (+ pending-ci) |
| 21 | L400 | Quantum and post-quantum: crypto inventory and migration plan + agent assist | `labs/L400/21-post-quantum-migration` | AST inventory, Mosca priorities, hybrid X25519+ML-KEM-768 behind one interface | recall = precision = 1, ratchet, configured KEM | none needed (ML-KEM ran locally) | JupyterLab | validated-local |
| 22 | Capstone | Capstone: an end-to-end quantum optimisation service + agent assist | `labs/L400/22-capstone` | 4 ADRs (execution, code decides, readout-only mitigation, feasibility gate first) | 5 fitness tests + 6 milestone tests; `run_capstone.py` scorecard | optional SDK swap (not built) | JupyterLab, marimo, Mitiq | validated-local |

Shared helper: `labs/_shared/qopt/maxcut.py` (seeded graphs, vectorised QAOA; self-tested). The capstone imports labs 13 and 17-20 instead of copying them. Lesson data: `content/L400.json`, regenerated with `python tools/build_l400_json.py`; concept notes in `content/concepts/L400/` (17-21: 616-697 words; capstone 503); evidence in `research/L400-evidence.md`. Installs: `labs/L400/requirements.txt` (numpy, cryptography), `labs/L400/requirements-sdk.txt` (L300 pins + cryptography), `labs/L400/requirements-qdk.txt` (own venv).

## L500 lesson map ("Theory & Rigour": proofs, derivations, ethics, primary literature)

Each foundations lesson goes definitions → theorems with proofs → a numerical check that runs here → a problem set with full solutions. Lesson 26 is a structured ethics case analysis and lesson 27 a reading seminar on two primary papers. All numpy-only and `validated-local`; every theorem's `checkOutput` in `content/L500.json` is the real output of `labs/L500/<lab>/theorems.py`.

| # | Level | Lesson | Lab / material | Theorems (checked) | Problems | Validation |
|---|---|---|---|---|---|---|
| 23 | L500 | Foundations I: linear algebra for qubits | `labs/L500/23-linear-algebra-for-qubits` | 4: unitaries preserve norm; tensor rules; Born rule and phase; Bell statistics cos²(a−b) | 9 | validated-local |
| 24 | L500 | Foundations II: quantum information basics | `labs/L500/24-quantum-information-basics` | 4: no-cloning; teleportation and superdense coding; Deutsch-Jozsa; density matrices and no-signalling | 9 | validated-local |
| 25 | L500 | Foundations III: algorithms and complexity | `labs/L500/25-algorithms-and-complexity` | 4: Grover sin²((2k+1)θ), k ≈ (π/4)√N; QFT unitary, O(n²) gates; phase estimation ≥ 4/π²; Shor's reduction | 10 | validated-local |
| 26 | L500 | Ethics 26: honest claims, the duty to migrate, export controls and access | case study in `content/L500.json` | — (ACM, IEEE, NIST IR 8547, NCSC, BIS 89 FR 72926, EU 2025/2003, UN A/RES/78/287) | 6 | validated-local (numbers) |
| 27 | L500 | Reading seminar 27: Grover (1996) and Preskill (2018) | readings + response prompts | — | 6 | validated-local (numbers) |

**Assessment pack** (`content/assessment/`): `syllabus.md` (14-week plan, weights, policies, outcomes mapped to CS2023 and ABET CAC/EAC), `midterm.md`, `final.md`, `concept-inventory.json` (15 pre/post items), `capstone-oral-defence.md`, `peer-review-adr.md`, `team-roles.md`. Question bank: `content/qbank/L500.json` (44 questions).

**Checks (all must print OK):** `python research/l500_checks.py` · `python research/check_l500_qbank.py` · `python research/qbank_checks.py` · `python tools/run_labs.py --level L500` (runs the three plus the theorem checks and their tests). Lesson data: `content/L500.json`, regenerated with `python tools/build_l500_json.py` from `tools/l500_23.py` … `l500_27.py`; concept notes in `content/concepts/L500/`; evidence in `research/L500-evidence.md`.

## How to run the labs
Target machines: an Apple-silicon **Mac mini** (macOS) or a **Windows 11** x64 PC. Both run everything natively; see `HARDWARE.md`. Lesson 1 lists every setup step for both systems (`mac` / `windows` fields).

```bash
# macOS (zsh)
cd quantum-computing
python3.12 -m venv .venv && source .venv/bin/activate
python -m pip install -r labs/L100/requirements.txt
python tools/run_labs.py --sdk            # every lab: cross-checks, lab script, try_it, agent assist, tests, L500 checks
```
```powershell
# Windows (PowerShell)
cd quantum-computing
py -3.12 -m venv .venv; .venv\Scripts\Activate.ps1; $env:PYTHONUTF8 = "1"
python -m pip install -r labs\L100\requirements.txt
python tools\run_labs.py --sdk
```
Without the SDKs, `python tools/run_labs.py` runs the numpy-only parts, including every L300 and L400 main lab and the capstone (install `labs/L400/requirements.txt` for lesson 21's cryptography). Add `--level L400` (or `L100`, `L200`, `L300`) to run one level, `--extras` (in the Mitiq/PennyLane venv) for the L300 extras, and `--qdk` (in the QDK venv) for lesson 19's resource estimator. To work on one lab: `cd labs/L100/02-qubits-and-gates`, then `python crosscheck_numpy.py`, `python gates_lab.py`, `python -m unittest -v`. Each lab has a `README.md` with the run command and expected output.

## Agent assist (local model)
Lesson 5 has an `agentAssist` item: a local model (Ollama, `http://localhost:11434/v1`) drafts OpenQASM from a description, and the lab's own parser and numpy check accept or reject it. Lesson 8 has one too: the model proposes the marked states and iteration count for a Grover search; a predicate in code and numpy P(success) accept, override or reject it. Lesson 15: the model reads a VQE convergence log and proposes optimizer settings; code checks its numbers against the log, its diagnosis against a rule, the shot budget, and then runs the proposal itself. Lesson 21: the model drafts post-quantum migration notes from the crypto inventory; code rejects invented files, wrong replacements, missing P1 items and made-up dates. Capstone: the model explains the benchmark report; code rejects a different winner, numbers not in the report and 'quantum advantage' claims. Tests use only a deterministic fake server. The shared helper is vendored at `labs/_shared/local_agent/` (unchanged copy of `kb/shared/local_agent`). The model never decides anything and never receives secrets.

## How validation works
- **Cross-checks (`crosscheck*.py`)** use only numpy. They compute the expected probabilities independently of any quantum SDK. They were run in the authoring sandbox, and their real output is pasted in each lab README.
- **SDK labs** (L100 and L200) were written against the documented Qiskit 2.x / Cirq 1.7 APIs and use Qiskit's reference primitives (`StatevectorSampler`, `StatevectorEstimator`), not Aer. They have not been run yet: the sandbox could not install these SDKs. Their status is `pending-ci`.
- **CI** (`.github/workflows/labs.yml`) runs both jobs on a matrix of `ubuntu-latest`, `macos-latest` (Apple silicon, arm64) and `windows-latest`, through the same cross-platform runner `tools/run_labs.py`:
  - `crosscheck` runs with numpy only (plus agent assist against the fake server).
  - `sdk-labs` installs the pinned SDKs (`labs/L300/requirements.txt`), runs every lab script and test with `REQUIRE_QUANTUM_SDKS=1` (a skipped SDK test then fails), and uploads the observed outputs and L300 logs per OS.
  - `l300-extras` installs Mitiq and PennyLane in their own environment and runs `tools/run_labs.py --level L300 --extras` with `REQUIRE_L300_EXTRAS=1`.
  - `l400-qdk` installs the QDK resource estimator in its own environment and runs `tools/run_labs.py --level L400 --qdk` with `REQUIRE_QDK=1` and `QDK_PYTHON_TELEMETRY=none`.
- **Platforms:** each lesson has `platforms: {mac, windows}`. They say `expected` until the matrix has run; then set `tested-ci` in `tools/build_l100_json.py`.
- **Validation key:** `validated-local` = ran in the authoring sandbox · `pending-ci` = written against documented APIs, not yet run (the numpy/parser parts did run) · `validation.pendingCi` = the exact files, SDK variants and learning-tool exercises that have not run yet · `platforms` `expected` = not yet run on that OS.
- To promote a lesson to `validated-local`, paste the CI output into the lab README and update `validation` in `tools/build_l100_json.py`.

## Neutral names used
circuit · gate (X / NOT, H / Hadamard, CNOT / CX) · measurement · shots / repetitions · counts / histogram · seed · statevector · simulator (backend) · OpenQASM (neutral circuit format) · bit order (little- vs big-endian).

## Concepts (read before each lab)
- Domain primer: `CONCEPTS-PRIMER.md` (uses, mental model, concept map, glossary, misconceptions).
- One note per lesson: `../content/concepts/01-setup-environment.md` … `06-same-circuit-two-frameworks.md`. Each lesson in `content/L100.json` links its note through `conceptNote` and `conceptSummary`.
- Every number in the notes comes from `../research/concepts_worked_examples.py`.
- Hands-on leads (kb/REBALANCE-SPEC.md): each note is 200-250 words with 4 headings (Why it matters, Mental model, How it works → lab step, Common mistakes). The rest lives in the lesson object: `inRealSystems`, `useWhen`, `checkYourself` (shown with the checkpoint), `next` (L200 topic), and the former "Go deeper" links in `sources`.
- Each lesson has 2 `tryIt` items (change the code, predict, compare). Run them with `python try_it.py` in the lab folder; `test_try_it.py` asserts the results. Lab code comments name the concept on the line where it happens.
- Regenerate `content/L100.json` with `python tools/build_l100_json.py` (it copies `code` from the lab file).
- Concept share (REBALANCE-SPEC measure script, 2026-10-28, after the L400 build): L100 concept 1483 / hands-on 7565 words = 16.4% (target 20-25%); L200 1978 / 6215 = 24.1% (target 25-30%); L300 2712 / 11158 = 19.6% (target 30-35%); L400 + capstone 3845 / 16216 = 19.2% (target 35-40%). Notes are at full length (L300 530-548 words; L400 616-697, capstone 503); they were not padded and labs were not cut, so every level sits below its band (KNOWN-GAPS, "Concept share and sizes").

See also: `HARDWARE.md`, `VERIFIED-RESOURCES.md`, `KNOWN-GAPS.md`, `../research/L100-evidence.md`.
