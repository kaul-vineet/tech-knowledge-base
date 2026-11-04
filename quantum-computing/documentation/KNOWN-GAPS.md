# Known gaps — quantum computing L100

## Not run (pending CI)
- **None of the six SDK labs has been executed.** The authoring sandbox has no package network, so `qiskit`, `qiskit-aer`, `qiskit-qasm3-import` and `cirq` could not be installed. All six lessons are `pending-ci`. Their "expected output" blocks come from the numpy cross-checks and the documented behaviour, not from observed SDK runs.
- **What was run locally:**
  - every `crosscheck*.py` file;
  - every `python -m unittest` suite (cross-check tests pass; SDK tests are skipped).
  - Environment: Python 3.12.15, numpy 2.5.3.
- **To promote a lesson to `validated-local`:** run the `sdk-labs` CI job, paste `observed-output.txt` from the uploaded artifact into the lab README, then update `validation` in `tools/build_l100_json.py` and regenerate `content/L100.json`.

## Version compatibility not proven
- qiskit 2.6.1, qiskit-aer 0.18.2, qiskit-qasm3-import 0.6.0 and cirq 1.7.0 were each checked on PyPI. **No source states that they work together.** Aer 0.18.2 was released four days after qiskit 2.6.1, so they are likely compatible, but CI is the first real test.
- Transitive dependencies such as numpy are not pinned in `requirements.txt`, to avoid resolver conflicts. CI records `pip freeze`. The cross-check job pins numpy 2.5.3.
- qiskit-aer's PyPI page says the project is in **"reduced maintenance mode"** (critical fixes only). **Fixed (review F25):** every L100 lab now runs on Qiskit's reference `qiskit.primitives.StatevectorSampler(seed=…)`, like L200. Aer stays in `requirements.txt` as an optional equivalent (noise models, speed); no lab imports it and `check_env.py` reports it as "optional".

## API details used but not verified line-by-line
- `cirq.measure(q0, q1, key="m")` with several qubits. The `cirq.Result.histogram` docs describe a measurement with key 'abc' over qubits a, b, c, but the docs fetched had no literal multi-qubit `cirq.measure` call.
- The exact layout of Qiskit's OpenQASM 3 export (register declaration order, barrier lines). `crosscheck_qasm_numpy.py` ignores `barrier` and `measure`, and fails loudly on anything else outside its subset. CI checks it against real `qasm3.dumps` output.
- Whether `qasm3.loads` keeps the classical register name `meas`. The lab reads `qc.cregs[0].name` instead of assuming it.
- `seed_simulator=` (an AerSimulator run option) was seen only in a third-party tutorial, so it is **not used**. Seeding goes through the documented `StatevectorSampler(seed=…)` (signature re-checked on the API page 2026-10-28).
- Lab 01 calls `transpile(qc, basis_gates=["rz", "sx", "x", "cx"])` with no backend, so measurements must pass through untouched; this is the classic documented usage but has not been run here.

## Simulator limits
- `StatevectorSampler` and `cirq.Simulator` are ideal and noise-free (so is AerSimulator without a noise model). Real hardware produces outcomes the labs treat as impossible, such as '01' and '10' for a Bell pair. Noise models are out of scope for L100.
- Statevector simulation memory doubles with each added qubit. That doesn't matter at L100, where circuits have one or two qubits.
- Seeds make **one simulator** repeatable. Qiskit and Cirq use different RNGs, so the same seed number gives different counts in each. The lab 06 tests compare distributions, not exact counts.

## Items dropped or limited
- **Third-party Aer tutorial (freequantumcomputing.com):** not authoritative.
- **Old IBM docs v0.42 AerSimulator page:** stale.
- **Braket readthedocs "Getting started" page:** no code.
- **openqasm.com home page:** navigation only.
- **Equivalents are one line each, on purpose.**
  - Braket: the main README example needs an AWS account, so only the local `braket_sv` simulator is mentioned. The `LocalSimulator` class name wasn't fetched and isn't quoted.
  - Q#/QDK: Q# gate names weren't fetched and aren't quoted.
- **No university course with runnable code was kept.** The IBM Quantum Learning course page (J. Watrous) is supporting background only.

## Environment and CI caveats
- `.github/workflows/labs.yml` lives inside `quantum-computing/`, and **GitHub only runs workflows from `<repo root>/.github/workflows/`**. If this folder isn't the repo root, move the file and set `LAB_ROOT`. Action versions (`checkout@v4`, `setup-python@v5`, `upload-artifact@v4`) were not re-checked for this build.
- The authoring mount refused some file renames: `mv` and `sed -i` left ghost entries. That's why lab 05's cross-check is named `crosscheck_qasm_numpy.py` rather than `crosscheck_numpy.py`. The labs aren't affected.

## Concepts layer
- **The L200–L400 concept map is proposed, not agreed.** `kb/` contains no curriculum beyond L100, so the primer's map and each note's "Next (L200)" line need sign-off.
- **Worked examples are numpy computations, not SDK runs.** The SDK-side claims in the notes are still pending CI, like the labs:
  - lab 06's `'01'` vs `'10'`;
  - lab 04's 2000-shot check.
- **The Aaronson blog post has no open licence.** It is quoted and summarised, not reused.
- **The 95% ranges use the normal approximation** (±1.96 standard errors) to the binomial distribution. That is standard statistics, not taken from a retrieved source.
- **Crypto-only instruction (csrc.nist.rip link) does not apply.** This domain never used that link; the only match for `csrc.nist` in this folder is this note.

## Rebalance (hands-on leads)
- **Concept share measured at 20% (1478 concept vs 5859 hands-on words = 20.1%; was 46%: 3820 vs 4488)** with the REBALANCE-SPEC script. That is the bottom of the L100 target (20-25%): notes are capped at 250 words (they are 235-246 by `wc -w`), so the share cannot rise much further without cutting hands-on content.
- **tryIt items are validated through numpy or the lab's independent OpenQASM parser, not the SDKs.** All 12 were run locally (`try_it.py`, `test_try_it.py`). Their Qiskit/Cirq variants are pending CI, like the labs. Lab 01 tryIt 2 (statevector bytes) needs no SDK.
- **Lab 03 tryIt 1 quotes numpy's sample (1206 ones in 2500 shots), not the SDK's.** `StatevectorSampler` has its own RNG, so its exact count will differ; the test checks only the tolerance.
- **Lab 05 tryIt 2 expects `qiskit.qasm3.loads` to accept `s q[0];`** (`s` is in stdgates.inc). Not yet observed.
- Concept comments were added to the six main lab files only. That changed no printed output; READMEs were re-checked against fresh cross-check runs.

## Platforms (Mac mini + Windows) and local agents
- **Nothing ran on macOS or Windows.** The authoring sandbox is Linux, so every lesson says `platforms: {mac: expected, windows: expected}`. The CI matrix (`ubuntu-latest`, `macos-latest` arm64, `windows-latest`) runs `tools/run_labs.py`; switch to `tested-ci` only after it passes.
- **Wheel availability was not checked file by file.** PyPI lists MacOS and Windows classifiers for qiskit-aer 0.18.2, but the wheel file list could not be fetched (PyPI simple index refused). Apple-silicon and Windows x64 installs are first proven by CI. Windows 11 on Arm is out of scope.
- **Windows UTF-8:** without `PYTHONUTF8=1`, Python 3.12 is expected to fail with `UnicodeEncodeError` when Qiskit's box-drawing diagrams (labs 02, 04) are piped. This is inferred from the Python docs, not observed. CI and `tools/run_labs.py` set it.
- **Cross-platform fixes made:** lab 05 read and wrote files relative to the current directory (`try_it.py`, `crosscheck_qasm_numpy.py` defaults, `qasm_lab.py` → `bell.qasm`). They now use `pathlib` paths next to the script with UTF-8. `test_qasm.py` uses `pathlib`. The CI's bash-only loops (`declare -A`, `for d in */`) were replaced by `tools/run_labs.py` (`sys.executable`, `pathlib`). No `fork`, `SIGALRM`, `os.uname` or hard-coded `/tmp` were found.
- **Ollama on Windows:** the docs fetched did not say whether the installer starts the server automatically, so step 7 says to run `ollama serve` if `/v1/models` does not answer.
- **Agent assist was run only against the deterministic fake server.** No real model ran (no model download in the sandbox). The fake replies in `fake_qasm_rule.py` are hand-written imitations of common mistakes, not recorded model output. The vendored helper `labs/_shared/local_agent/` is an unchanged copy (checked with `diff`). The quantum route is registered from the lab through the `EXTRA_RULES` hook, not by editing the copy.
- **The agent check is only as strong as the parser.** It accepts h, x and cx only. Correct drafts that use other gates are rejected as unverifiable; the CI test `SdkAgreesWithTheJudge` shows Qiskit reading the same drafts.
- **Concept share after this change: 18% (18.4%)** (1478 concept vs 6534 hands-on words; was 20%: 1478 vs 5859). This is below the 20–25% L100 target because of the added hands-on content (setup steps for both OSes, agent assist). The spec says to report this and not pad the notes.

# Known gaps — L200 ("Build it", lessons 7–11)

## Not run (pending CI)
- **No L200 SDK code has been executed.** `bv_lab.py`, `grover_lab.py`, `qft_lab.py`, `param_lab.py`, `transpile_lab.py`, the Qiskit halves of every `try_it.py` / `solution_*.py`, and 29 SDK tests are written against the documented qiskit 2.6.1 API but skipped locally. All five lessons are `pending-ci`. "Expected output" for the SDK scripts is derived from the numpy cross-checks and the docs, not observed.
- **What ran locally (Python 3.12.15, numpy 2.5.3):** every `crosscheck_numpy.py`, `try_it.py`, `solution_*.py`, `agent_assist.py --fake`, `research/L200_worked_examples.py`, the shared simulator self-test (`labs/_shared/qsim`), and every L200 `python -m unittest` suite: 66 tests, 37 pass, 29 SDK tests skip (plus 5 simulator self-tests). `python tools/run_labs.py` (L100 + L200) ended "all labs OK".
- **Lesson 11 has no exact transpile numbers.** Depth and two-qubit counts per level depend on Qiskit's stochastic layout/routing and GenericBackendV2's sampled properties. The README shows the shape only; tests assert properties (only basis gates, every 2q gate on an edge, line level 0 > 4 CX, chain = 4 CX, GHZ behaviour kept), not numbers. Paste the CI table into the README after the first run.

## API details used but not verified line by line
- `BitArray.get_counts(i)` for a sweep index: the BitArray API page returned no document; the call is taken from the StatevectorSampler docs example (`get_counts(22)`).
- Shape `(21, 1)` for one-parameter sweeps follows the StatevectorEstimator example (`(100, 2)` for two parameters); a flat `(21,)` array was not tested.
- `MCMTGate(ZGate(), n - 1, 1)` is copied from the IBM Grover tutorial; its class API page was not fetched.
- `backend.operation_names` / `backend.coupling_map.get_edges()` on GenericBackendV2 come from the BackendV2 attributes listed on the GenericBackendV2 page; the exact printed basis list in the lab 11 README is inferred (default basis + reset/delay/measure).
- `Operator(qc).equiv` and `Statevector.evolve(QuantumCircuit)` are documented; `QuantumCircuit.inverse()` on a circuit containing `swap`/`cp` is assumed standard (QFT-class docs describe the same).
- The lone-H tryIt (lab 11) expects `rz, sx, rz` at level 0; Qiskit may pick an equivalent sequence. The CI test checks only "gates ⊆ {rz, sx, x}" and operator equivalence.

## Design limits
- **The numpy simulator (`labs/_shared/qsim`) is new code, not a reference implementation.** It is checked by its own self-tests (Bell pair, bit order, SWAP, unitarity) and by agreeing with numpy's FFT and the Grover closed form; CI then compares it with Qiskit.
- **Sampled numbers differ by RNG.** Lab 10 tryIt 2 quotes numpy's sampled fit (seed 7); Qiskit's StatevectorSampler uses its own RNG, so its values differ and are asserted only by tolerance (0.05).
- **Agent assist (lesson 8) ran only against the fake server.** The fake replies are hand-written imitations of typical mistakes, not recorded model output. The shared fake server routes any prompt containing "json" to its own demo rule, so the lab prompt avoids that word; a real model is not affected. The vendored `labs/_shared/local_agent/` copy is unchanged.
- **One agentAssist lesson only** (8). Lessons 7, 9–11 would only have the agent restate numbers code already prints.
- **L200 equivalents are Qiskit/Cirq only.** PennyLane/Braket/QDK one-liners were not re-verified for these algorithms, so they are omitted rather than guessed.

## Concept share and notes
- **Concept share 25.1%** (1978 concept vs 5913 hands-on words, REBALANCE-SPEC script on `content/L200.json`): inside the L200 target (25–30%) after shortening repeated boilerplate (`environment`, `simulatorVsReal`). Adding Mac/Windows variants to the build-task steps had pushed it to 24.9%.
- **Note sizes:** 392–399 words with `wc -w` in a UTF-8 locale (380–386 in the C locale, which does not count words containing "→", "π" etc.).
- **Primer:** the concept-map L200 row and agent line now match the built lessons; the primer is 585 words by the same `wc -w` used for L100 (621 in a UTF-8 locale).
- **L300 "next" lines are proposals** (phase estimation, amplitude estimation, VQE/QAOA, noise-aware layout); no L300 spec exists yet.

# Update pass: learning tools + review fixes (UPDATE-TOOLS-REVIEW-SPEC, 2026-10-28)

## Learning tools
- **No learning-tool exercise has been run.** None of the tools (Qiskit visualization, QDK + VS Code extension, openqasm3 parser, JupyterLab) can be installed in the authoring sandbox. Every `learningTools[].expected` says "Pending a manual run" and quotes the lab value the tool should reproduce. Each exercise is also listed in `validation.pendingCi`.
- Tool facts and install commands are copied from `kb/shared/learning-tools.json`; they were not re-fetched here. Not verified for this topic: whether the QDK extension draws and steps a Qiskit-exported OpenQASM 3 file (incl. `measure_all`'s barrier) and a decomposed Grover circuit; the `qdk[qiskit]` interop API (named only in the catalogue's exercise); the openqasm3 AST class names (the exercise says "count gate-call statements" rather than quoting them).
- marimo is catalogued but not mapped to any quantum lesson, so it is not in the table.
- QDK and Qiskit visualization are used in two lessons each with the same install line; the tool exercises add hands-on words, which lowered the concept share (below).

## Review findings (REVIEW-L100-L200.md)
- **Fixed:** F25 (L100 on `StatevectorSampler`; Aer an optional equivalent), F03 (every L100 `next` names an existing L200 lesson; every L200 `next` starts "L300 (planned):"), F05/F19 (lesson 1 uses the canonical commands of `kb/shared/WORKSTATION-SETUP.md`: winget `Python.Python.3.12`, the ollama.com installer on Windows, `brew services start ollama` on the Mac, `LOCAL_MODEL_URL`/`LOCAL_MODEL`), F07 (`validation.pendingCi` on all 11 lessons), F14 (no localhost URL in VERIFIED-RESOURCES), F17 (Aaronson post typed "background"), F16 (no duplicate URLs; the install-manager and winget-Ollama rows are marked background / not used), F27 (`__pycache__` folders and `run_labs.log` deleted; `.gitignore` added), F01 (status line at the top of README).
- **Recorded, not fixed:** F01 CI: `.github/workflows/labs.yml` still sits inside the topic folder and its comments still say "Qiskit / Qiskit Aer / Cirq"; it installs the same `requirements.txt`, so it needs no change to run, but this pass may not edit `.github/` (a separate job builds the root CI). F09: concept share is below target (see below). F02, F04, F06, F08, F10–F13, F15, F18, F20–F24, F26 do not apply to this topic (no quantum lesson is in the F08 `seeAlso` map).
- **L300 candidates** (topics the old L100 `next` lines promised but no L200 lesson covers): noise models (Aer noise model), the Estimator on noisy targets, quantum teleportation and measuring in other bases, OpenQASM 3 classical control (mid-circuit measurement, `if`), QPY lossless storage, comparing expectation values across SDKs.

## Concept share after this pass
- L100 **16.4%** (1483 concept vs 7565 hands-on words; was 18.4%). L200 **24.4%** (1978 vs 6135; was 25.1%). Measured with the REBALANCE-SPEC script. The drop comes from the new `learningTools` items and the longer lesson 1 setup steps (`validation` is not counted). The notes were not padded: concept note 01 changed only to name `StatevectorSampler` and fix its step pointers, and is 249 words.

# Known gaps — L300 ("Harden it", lessons 12–16)

## What ran and what did not
- **Ran locally (Python 3.12.15, numpy 2.5.3):** every L300 main lab (`noise_lab.py`, `mitigation_lab.py`, `qaoa_lab.py`, `vqe_lab.py`, `classifier_lab.py`), every `try_it.py` and `solution_*.py`, `agent_assist.py --fake`, `research/L300_worked_examples.py`, the new density-matrix self-tests, and all L300 unittest suites: 66 tests, 55 pass, 11 SDK/extras tests skip. `python tools/run_labs.py --level L300` ended "all labs OK". The fail-before proofs (`BUILD_TASK_MODULE=<naive lab module>`) were run and failed as documented in each README.
- **Not run (pending CI):** `noise_aer.py`, `qaoa_qiskit.py`, `vqe_qiskit.py` (job `sdk-labs`) and `mitiq_zne.py`, `classifier_pennylane.py` (new job `l300-extras`). Their "expected" lines in the READMEs come from the numpy labs and the docs, not from observed SDK runs. Status is `validated-local` because the main lab, failureLab, buildTask and tryIts ran here; every unrun file is in `validation.pendingCi`.
- **Learning-tool exercises** (Qiskit visualization, JupyterLab, marimo) are not run; each `expected` quotes the lab value the tool should reproduce.

## Design limits
- **The main labs use the topic's own numpy simulator**, not Qiskit/Aer. The density-matrix module (`labs/_shared/qsim/density.py`) is new code. It is checked by self-tests (trace 1, Hermitian, full depolarizing = I/4, Bell fidelity 1 − p + p/4, damping 0.25 → [0.25, 0.75]); agreement with Aer is first checked in CI (`AerAgrees`, tolerance 0.02).
- **Noise parameters are illustrative**, not from a device. `NoiseModel.from_backend` with a real or fake backend (qiskit-ibm-runtime) would give device-like values; not used, to avoid a vendor package.
- **Lesson 13's ZNE uses exact density-matrix values plus binomial shot noise.** Real folding does not scale coherent or idle-time errors linearly, so hardware extrapolations can overshoot; this is described, not simulated.
- **Lesson 14's optimiser is plain central-difference descent on an exact statevector.** The local minimum at seed 0 is specific to this graph, learning rate (0.05) and step count. With lr 0.1 the p = 1 descent jumped basins (0.8188 → 0.7841); lr 0.05 is what the lab uses.
- **Lesson 15's Hamiltonian is a toy "H2-like" Pauli sum** with illustrative coefficients, not a chemistry calculation. SPSA gains α = 0.602, γ = 0.101 come from Spall's IEEE TAES 1998 implementation paper (step 1, author's copy on jhuapl.edu; replaced the golang-spsa README, R3-13). IBM's tutorial values (α 0.9, γ 0.4, A 30) converged too slowly here.
- **Lesson 16's honest result is a tie, not "classical wins":** on 5 dataset seeds the 2-qubit model equals logistic regression 3 times and is one test point (0.05) ahead twice. With 20 test points this is within noise. The flat-gradient demo measures one partial derivative's median over 10-20 random inits (exponential decay is visible from 2 to 10 qubits, not proven); training of the 10 × 20 model is not run (too slow in pure numpy).

## API details used but not verified line by line
- `amplitude_damping_error` signature is from the Aer **0.17.1** page; assumed unchanged in 0.18.2.
- Aer `SamplerV2(seed=..., options={"backend_options": {"noise_model": ...}})`: the docs say backend_options are passed to AerSimulator; that `noise_model` is honoured there is assumed (AerSimulator lists it as a constructor option).
- Mitiq: `fold_gates_at_random(..., fidelities={"single": 1.0}, random_state=...)` and `generate_inverse_confusion_matrix(n, p0, p1)` come from the 1.1.0 user guide. The meaning of p0/p1 was not checked, so the test uses p0 = p1 only. Mitiq's Cirq version bound could not be fetched (GitHub requirements file returned nothing), so Mitiq is installed in its own CI job and venv.
- PennyLane 0.45.1: `import pennylane as qp` is the documented alias (blog 2026-03-19, docs); `qml` is assumed to still work but is not used. `qp.grad` with `pennylane.numpy` arrays and `GradientDescentOptimizer.step(cost, w, b)` returning both arguments follow the classifier demo pattern; not observed. Whether PennyLane 0.45.1 accepts numpy 2.5.x was not checked (numpy is unpinned in `requirements-extras.txt`).
- Qiskit: `QuantumCircuit.rzz` / `rx(theta, range(n))` and `StatevectorSampler` results indexed with `get_counts(0)` for a one-row parameter array follow the L200 usage; `SparsePauliOp.from_sparse_list` with "ZZ" terms follows the VQE tutorial.

## Concept share and sizes
- **Concept share 19.6%** (2712 concept vs 11146 hands-on words after the 2026-10-28 update pass; was 19.9% / 10941, REBALANCE-SPEC script on `content/L300.json`), below the 30–35% target. Notes are at full length (512–526 words with `wc -w` in the C locale, 530–548 in a UTF-8 locale; spec 450–550). The hands-on side is large because each lesson carries the full main-lab code (69–102 lines), 7 steps (3 with Mac/Windows variants), a failureLab, tradeOffs, 5–7 walkthrough items and learning-tool exercises. Per the spec the notes were not padded and the labs were not cut.
- Main lab files: 69–102 lines (spec ~60–120).

## Platforms
- Nothing ran on macOS or Windows. All five lessons say `platforms: expected`. Lab code uses pathlib, UTF-8 file I/O and no POSIX-only calls; logs are written under each lab's `logs/` folder (git-ignored).
- scipy 1.18.1 requires Python ≥ 3.12 and mitiq 1.1.0 requires Python < 3.13: the course's Python 3.12 satisfies both; Python 3.13 would break the Mitiq path.

# Update pass: L300 review fixes + learning tools (UPDATE-L300-SPEC, 2026-10-28)

## Learning tools
- **Mitiq 1.1.0 added to lesson 13** (with JupyterLab: 2 tools). Its exercise compares Mitiq's Linear/Richardson factories with the lab's 0.9687 / 0.9944. Mitiq cannot run here (Python <3.13 and its own Cirq; no SDKs in the sandbox), so the exercise is in `validation.pendingCi` and its expected values come from the lab README, not from an observed run. Other L300 lessons keep their tools (proposal: "already in lesson").

## Review findings (REVIEW-L300.md)
- **Fixed:** R3-04 (quantum side: #13 → simulation L300 #13, #15 → simulation L300 #12; titles checked against `simulation/content/L300.json`; the back-links belong to the simulation pass) · R3-05 (L200 #7–9 `next` now names L200 #8, L300 #12 and L200 #10 by exact title; #10 already pointed at L300 #15) · R3-11 (#14 prerequisites = lessons 10, 12, 13; the "general version" note moved into `next`) · R3-13 (golang-spsa README replaced by Spall's 1998 IEEE paper) · R3-14 (concept share for all levels in README.md) · R3-15 (`test_vqe` writes its log in a per-run `tempfile.TemporaryDirectory(dir=lab folder)`; two concurrent runs passed 3 times).
- **Already met:** R3-06: every L300 lab ships the unfixed module and `BUILD_TASK_MODULE=<naive>` fails test_build_task in all 5 lessons (re-run in this pass).
- **Recorded, not fixable here:** R3-01: nothing has run on macOS/Windows and the Qiskit/Aer/Mitiq/PennyLane paths are still pending CI.
- **L400 candidates** (promised by the old L200 "L300 (planned)" pointers, not built): Simon's algorithm, quantum phase estimation (from L200 #9's QFT), amplitude estimation; plus error correction with Stim and resource estimation (L300 #16 `next`).

# L400 "Design it" (lessons 17-21) + capstone 22 (L400-SPEC, 2026-10-28)

## What ran and what did not
- **Ran here (validated-local):** every L400 main lab, solution, try_it, fitness test and build-task test, lesson 21's ML-KEM-768 / X25519 / hybrid KEM (cryptography 50.0.2), both agent assists against the fake model server, and the capstone end to end (real HTTP on 127.0.0.1). Fail-before proofs observed on the shipped files: 17 (4 failures), 18 (4), 19 (5), 20 (3), 21 (6).
- **Pending CI:** `sampler_qiskit.py` (17), `bench_qiskit.py` (18), `count_qiskit.py` and `estimate_qdk.py` (19, QDK in its own job `l400-qdk`), `compile_qiskit.py` (20), and every learning-tool exercise. Nothing ran on macOS or Windows (`platforms: expected`).
- **Capstone SDK swap not built:** a Qiskit Aer adapter (NoiseModel) behind the same `NoisyBackend` interface and Mitiq REM in place of the constrained mitigation are described as equivalents only.

## API details used but not verified by running
- `qdk.qre`: `OpenQASMApplication` is imported from `qdk.qre.application` by analogy with the documented `QSharpApplication`; `results.as_frame()["qubits"]` assumes the documented column name `qubits`. The Learn docs install `qdk[qre]`, but PyPI 1.33.1 lists only jupyter/azure/qiskit/cirq/all extras (pip only warns about an unknown extra). The estimator is new ("v3") and its API may change.
- Qiskit: `Target.add_instruction(..., {qargs: InstructionProperties(error=...)})` with `RZGate(Parameter)` and scoring transpiled circuits by `target[name].get(qargs)` (compile_qiskit.py); `StatevectorSampler` running an ISA circuit with a (k, 2) parameter array as one PUB and `data.meas[i].get_bitstrings()` per row (sampler_qiskit.py).
- `qdk.qre` SurfaceCode defaults (0.03, 0.01) are documented; the QDK's physical-qubit-per-logical formula was not fetched - our 2d² is the rotated code's d² + (d² − 1) count.

## Design limits (stated in the lessons)
- Lesson 17's costs (2 s queue, 0.5 s transpile, 60 s TTL) are illustrative, not vendor numbers; real queues vary by hours.
- Lesson 18 uses a sample budget on a noiseless simulator and 10 seeds; success 0.3 vs 0.5 is not statistically separable.
- Lesson 19 is a data-blocks-only lower bound (no factories, routing or decoding) with T-limited cycles approximated per rotation layer; the RSA runtime uses measurement depth × d × 1 µs, not Gidney's reaction-limited schedule.
- Lesson 20's compiler is brute force (6720 placements) on a fake ladder with illustrative errors; ESP ignores crosstalk and leakage. `compile_lab.route` was generalised (final layout length = len(layout)) so the capstone can reuse it; lesson 20 outputs are unchanged.
- Lesson 21's scanner covers Python (`cryptography` API) and two TOML settings only; other languages, vendored code and binaries are out of scope. Mosca's Y = 3 and Z = 9 are planning assumptions, not forecasts. On this sandbox's network mount `TemporaryDirectory` cleanup can fail and leave `tmp*` folders in the lab (git-ignored; `ignore_cleanup_errors=True`).
- Capstone: a white-noise + readout model stands in for a full noise model (TVD 0.0213 from lesson 20's density matrix on the 5-qubit circuit; not validated at 8 qubits); its layout search samples 200 placements.

## Cross-links
- Lesson 21 links one way to cryptography L400 #17 "Crypto agility: versioned envelopes, negotiation and dual signing" and #18 "Post-quantum cryptography in practice: ML-KEM, ML-DSA and hybrids" (titles read from `cryptography/content/L400.json`, built in parallel); the back-links belong to the cryptography topic.
- L300 #16 `next` now points at L400 #17; the L200 #7-9 notes that said "L400 (planned)" now point here ("L400 candidates"), because those topics were not built at L400 either.

## Concept share and sizes
- L400 + capstone concept share **19.2%** (3845 concept vs 16216 hands-on words, REBALANCE-SPEC script on `content/L400.json`) against the 35-40% target. Notes 17-21 are 616-697 words (`wc -w`, spec 600-750) and the capstone note is 503 (spec 400-600); notes were not padded and labs were not cut. All levels: L100 16.4%, L200 24.1%, L300 19.6%, L400 19.2%.
- Main lab files: 63-103 lines (spec ≤ ~150); helpers are separate files.
- CSWP 39upd1 (the current crypto-agility white paper) could not be fetched; CSWP 39 (Dec 2025) is cited and marked superseded.

## L400 candidates (not built; for further study)
- From earlier pointers: Simon's algorithm, quantum phase estimation (from L200 #9's QFT), amplitude estimation (from L200 #8), and error correction with Stim (L300 #16's old `next`).
- From this level: a Qiskit Aer / real-provider adapter for the capstone; magic-state factory modelling in lesson 19 (compare with QDK in CI); SABRE/VF2-scale layout search beyond brute force; CBOM (CycloneDX) export of lesson 21's inventory and ML-DSA signatures; hybrid TLS (X25519MLKEM768) in the cryptography topic.

# L500 "Theory & Rigour" (lessons 23-27) + assessment pack (L500-SPEC, 2026-10-30)

## What ran and what did not
- **Ran here (validated-local), Python 3.12.15 + numpy 2.5.3:** `labs/L500/23-25/theorems.py` (12 theorem checks) and their `python -m unittest` suites; `python research/l500_checks.py` (re-runs every check against `checkOutput` and the lab README, recomputes 26 problem-set answers / 64 values and 16 exam values); `python research/check_l500_qbank.py` (44 questions + 15-item concept inventory); `python research/qbank_checks.py` (all 281 questions incl. L500 and the inventory: 61 recomputed answers, 49 snippets executed); `tools/check_qbank.py quantum-computing` (L100-L400, unchanged and byte-identical after rebuilding with the extended `tools/build_qbank.py`).
- **Not run:** nothing on macOS or Windows (`platforms: expected`); the CI matrix picks L500 up through `tools/run_labs.py` (new `L500` level) but has not run yet.

## Content limits
- **Proofs cited, not reproduced:** the Ω(√N) search lower bound (BBBV 1997; Boyer et al. 1998) is given as a proof idea (hybrid argument); the ≥ 1/2 success probability of Shor's reduction is cited to Shor (1997, factoring section; section number not checked) and checked exactly only for N = 15, 21, 33, 35, 91; Legendre's continued-fraction theorem and Holevo's bound are stated without proof.
- **BQP placement** (P ⊆ BPP ⊆ BQP ⊆ PSPACE) is given with a path-sum sketch; no complexity-theory primary source (e.g. Bernstein-Vazirani 1997) was fetched.
- **Order finding is simulated exactly but not as a gate-level circuit:** the check builds the state (1/√T)Σ|k>|a^k mod N> directly and applies the inverse QFT with numpy; a modular-exponentiation circuit is out of scope (L400 #19 covers its cost).
- **Preskill (2018)** was read from the arXiv v3 PDF via web_fetch (text sections 1-6.10); later sections may have been truncated by the fetch limit, so guiding questions only use sections 1-6.
- **Grover (1996)**: only the abstract page and licence link were fetched; the full PDF was not, so the reading's guiding questions rely on the abstract and on the "inversion about average" description there.

## Policy and legal limits (lesson 26)
- **Not legal advice.** The export-control material is a policy-level summary of the primary texts fetched.
- **EU quantum entry numbers not verified in the Official Journal annex:** the 2025 EU list's quantum entries (4A506, 3A501.b.13, 3A504, 3B504) were found only in a law-firm client note (dropped as a source), because the EUR-Lex HTML of Regulation (EU) 2025/2003 was truncated before Category 3/4. The lessons therefore cite only what was read in the regulation itself (Annex I replaced; in force the day after publication on 14.11.2025; General Technology Note exclusions).
- **US ECCN 4A906 technical thresholds** (qubit counts, error rates) are in the rule's CCL text, which the fetch did not reach; the lesson names the ECCNs and policy (worldwide licence requirement, License Exception IEC, General License for quantum deemed exports with reporting) without thresholds. BIS may have amended the rule since 2024 (not checked).
- **IBM's "2.5 days" Sycamore estimate** (IBM blog) was not fetched; the lesson uses the arXiv abstract's "a matter of days".
- **NCSC page licence** (Open Government Licence or otherwise) and EUR-Lex reuse terms were not checked; both are only linked and briefly quoted.

## Assessment pack limits
- **The 14-week plan is a proposal.** L500-SPEC says the plan comes "from the review", but no such pedagogy review is in `kb/` (REVIEW-L100-L200.md and REVIEW-L300.md have no week plan). Week boundaries, weights split inside components (PS 6/6/6/3.5/3.5; exams 8/12; capstone 10/5/5) and the late policy are our proposal within the spec's totals.
- **CS2023 quantum knowledge unit:** a Quantum Architectures (Q-AR) unit was *proposed* for CS2023's AR area (German, Pias & Xiang, ITiCSE 2023, abstract only); whether and how it appears in the final report was not verified. The syllabus maps to the 17 verified KA names only.
- **ABET:** outcome wording is quoted from the 2025-2026 criteria pages (CAC 1-5 + CS outcome 6; EAC 1-7). The CAC page lists proposed changes for 2026-27 that do not alter the outcomes but were not tracked further.
- **Concept inventory is not validated psychometrically** (no pilot data, no item analysis); treat normalised gain as indicative.
- **Exam and problem-set rubrics** have not been calibrated with real scripts.

## Concept share
- L500 is theory by design: concept notes are 1054 / 987 / 1114 / 922 / 727 words (`wc -w`, spec 900-1300, 700-1000, 500-800). The REBALANCE-SPEC concept-share measure was not re-run for L500 (no L500 band defined).

## Pointers
- The L400 candidates "quantum phase estimation" and "Simon's algorithm" are now partly covered in theory: phase estimation in L500 #25 (T25.3); Simon's problem is mentioned only as the sharper separation after Deutsch-Jozsa (T24.3).

