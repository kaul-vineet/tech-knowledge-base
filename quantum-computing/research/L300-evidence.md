# L300 research evidence — quantum computing ("Harden it", lessons 12–16)

Method: kb/SPEC.md research method with the rubric of `L100-evidence.md` (I implementable, C current, A authoritative, O open, T transferable, D right depth; 0–2 each; keep ≥ 8/12). Retrieval with web_fetch / web_search on 2026-10-28. Every SDK API named in a lab is backed by its official API page or user guide; the numpy labs (which did run) implement the documented definitions directly. Numbers in the concept notes come from `L300_worked_examples.py` (output in `L300_worked_examples.out.txt`).

Design decision for all five lessons: the sandbox cannot install Qiskit, Aer, Cirq, Mitiq or PennyLane, and the spec requires that "fault and fix must actually run here". So every main lab, failureLab and buildTask is numpy-only (new density-matrix module `labs/_shared/qsim/density.py` with self-tests), and the SDK file in each lab is the documented equivalent, marked `pending-ci`.

## Lesson 12 — Noise models
**Questions:** 1. How does Aer 0.18 define depolarizing, amplitude-damping and readout errors (so numpy can match)? 2. How is a noise model attached and run with a seed? 3. What does `NoiseModel.from_backend` include?

| source | I C A O T D | score | decision |
|---|---|---|---|
| Qiskit Aer tutorial "Building noise models" (Aer 0.18.0 docs) | 2 2 2 2 2 2 | 12 | kept: `NoiseModel`, `depolarizing_error`, `ReadoutError([[1-p1given0, p1given0], [p0given1, 1-p0given1]])`, `add_all_qubit_quantum_error`, `error1.compose(error2)` = E2(E1(ρ)), `tensor`, GHZ example |
| `NoiseModel` API (Aer 0.18.0) | 2 2 2 2 2 2 | 12 | kept: `add_all_qubit_readout_error(error)`, ideal errors not added, `from_backend` = depolarizing + thermal relaxation + readout |
| `amplitude_damping_error` API (Aer 0.17.1 page) | 2 1 2 2 2 2 | 11 | kept: Kraus A0 = [[1,0],[0,√(1−a)]], A1 = [[0,√a],[0,0]]; page is 0.17.1, signature assumed unchanged in 0.18.2 (KNOWN-GAPS) |
| Aer `SamplerV2` API (0.18.2) | 2 2 2 2 2 2 | 12 | kept: `SamplerV2(*, default_shots, seed, options)` with `backend_options` passed to AerSimulator (noise_model) |
| `AerSimulator` API (0.18.2) | 2 2 2 2 1 2 | 11 | kept: `method="density_matrix"`, `noise_model` option; `seed_simulator` still not on the page, so not used |
| `cirq.depolarize` API | 2 2 2 2 2 2 | 12 | kept: p is the total probability of a non-identity Pauli, p/(4ⁿ−1) each → conversion p_cirq = λ(4^k−1)/4^k |

**Key facts:** Aer depolarizing_error(λ) = (1−λ)ρ + λ·I/2^k (Aer docs; checked in `test_density.py`: Bell fidelity 1 − λ + λ/4); readout rows are the true bit (Aer tutorial).

## Lesson 13 — Error mitigation
**Questions:** 1. Current Mitiq API for ZNE (folding, factories) and REM? 2. How do hardware stacks fold gates and extrapolate? 3. What do maintained tools do with negative quasi-probabilities?

| source | I C A O T D | score | decision |
|---|---|---|---|
| Mitiq 1.1.0 user guide "How do I use ZNE?" | 2 2 2 2 2 2 | 12 | kept: `zne.execute_with_zne(circuit, executor, factory=, scale_noise=)`, default `fold_gates_at_random`, `LinearFactory`, `RichardsonFactory`, `construct_circuits`/`combine_results` |
| Mitiq 1.1.0 "What additional options are available in ZNE?" | 2 2 2 2 2 2 | 12 | kept: `fold_global`, `fold_gates_at_random(..., fidelities={"single": 1.0}, random_state=)`, odd scale factor = G(G†G)^((s−1)/2), Richardson = PolyFactory(order = len − 1) |
| Mitiq 1.1.0 "How do I use REM?" | 2 2 2 2 2 2 | 12 | kept: `rem.execute_with_rem`, `generate_inverse_confusion_matrix(n, p0, p1)`, post-selection alternative |
| mitiq on PyPI | 1 2 2 2 1 1 | 9 | kept for facts: 1.1.0 (2026-09-03), GPL-3.0, Python ≥3.11,<3.13, Cirq is a core requirement |
| IBM guide "Error mitigation and suppression techniques" | 2 2 2 2 2 2 | 12 | kept: TREX, ZNE = noise amplification by digital gate folding (U → UU†U = factor 3) + extrapolation, ~3× overhead, "not guaranteed to produce an unbiased result"; PEC quasi-probabilities |
| mthree "Converting to probabilities" | 2 2 2 2 1 2 | 11 | kept: quasi-distributions contain negatives; `nearest_probability_distribution()` = closest in L2 |
| qcroadmap.com M3 page | 1 2 0 1 1 1 | 6 | **dropped**: unofficial summary; mthree docs cover it |

## Lesson 14 — QAOA on MaxCut
**Questions:** 1. Is `QAOAAnsatz` current in Qiskit 2.x and how is the MaxCut Hamiltonian written? 2. Which optimiser and initial angles does the official tutorial use? 3. How is the result graded?

| source | I C A O T D | score | decision |
|---|---|---|---|
| IBM tutorial "Quantum approximate optimization algorithm" | 2 2 2 2 2 2 | 12 | kept: the 5-node, 6-edge graph, Hamiltonian ½ZᵢZⱼ per edge with offset, `QAOAAnsatz(cost_operator, reps=2)`, COBYLA, init β = π/2, γ = π, brute-force check (optimum 5), "noisy, non-monotonic curve … too few shots" |
| `QAOAAnsatz` API (latest) | 2 2 2 2 1 2 | 11 | kept: signature (cost_operator, reps, initial_state, mixer_operator, flatten); not marked deprecated on the fetched page |
| scipy `minimize(method="COBYLA")` (1.18.0 manual) | 2 2 2 2 2 2 | 12 | kept: options rhobeg, tol, maxiter; PRIMA implementation since 1.16 |
| scipy on PyPI | 1 2 2 2 1 1 | 9 | kept for the pin: 1.18.1 (2026-08-21), Python ≥ 3.12 |
| `qiskit-addon-opt-mapper` (seen in the tutorial) | – | – | **not used**: extra package; the lab writes the cut table directly |

**Key facts:** RZZ(θ) = exp(−iθ/2·Z⊗Z), so e^{−iγ(1−ZZ)/2} = RZZ(−γ) up to a global phase (derived; checked in CI by `test_estimator_matches_numpy`).

## Lesson 15 — Hybrid variational loop (VQE)
**Questions:** 1. How does an official VQE example run SPSA with Qiskit 2.x primitives? 2. What are SPSA's properties and gain sequences? 3. Does `StatevectorEstimator` emulate shot noise?

| source | I C A O T D | score | decision |
|---|---|---|---|
| IBM tutorial "Ground-state energy estimation of the Heisenberg chain with VQE" (URL redirected from /variational-quantum-eigensolver) | 2 2 2 2 2 2 | 12 | kept: hand-written SPSA (a_i = a/(A+i+1)^α, c_i = c/(i+1)^γ, two calls per iteration), cost history logging, barren plateaus limit VQE scale |
| JHU APL SPSA page (J. C. Spall) | 1 2 2 2 2 2 | 11 | kept: two measurements per iteration regardless of dimension; designed for noisy measurements; p× fewer evaluations than finite differences |
| `StatevectorEstimator` API | 2 2 2 2 1 2 | 11 | kept: `StatevectorEstimator(*, default_precision=0.0, seed=None)`; exact for unitary circuits, so the SDK path samples with `StatevectorSampler` instead |
| `StatevectorSampler` API (reused from L100) | 2 2 2 2 1 2 | 11 | kept: seeded sampling for the shot-noise energy |

| yanatan16/golang-spsa README (MIT) | 1 1 1 2 2 2 | 9 | kept as **background**: quotes Spall's book (ISSO, 2003): a(k) = a/(k + 1 + A)^α, c(k) = c/(k + 1)^γ, "alpha = .602 and gamma = .101 work well for finite cases", A ≈ 10% of iterations, Bernoulli ±1 perturbations |
| Spall, "Implementation of the simultaneous perturbation algorithm…" (IEEE TAES 1998) | – | – | **not retrieved**: IEEE Xplore abstract only (paywalled); the gain values are taken from the background source above |

**Key facts:** the lab uses α = 0.602, γ = 0.101 (Spall's practical values, via the background source) and A = 10 for 150 iterations; IBM's tutorial uses α 0.9, γ 0.4, A 30 (too slow here: error ≈ 0.76 after 100 iterations in an exploratory run). The toy Hamiltonian coefficients are illustrative, not a chemistry calculation.

## Lesson 16 — Quantum classifier
**Questions:** 1. Current PennyLane version, import convention and template APIs for angle encoding and entangling layers? 2. What do the official demos say about barren plateaus and initialisation? 3. How does an official classifier demo split data and evaluate?

| source | I C A O T D | score | decision |
|---|---|---|---|
| pennylane on PyPI | 1 2 2 2 1 1 | 9 | kept: 0.45.1 (2026-06-26), Apache-2.0, Python ≥ 3.11 |
| `qp.AngleEmbedding` (0.45.1 docs) | 2 2 2 2 2 2 | 12 | kept: `AngleEmbedding(features, wires, rotation='X')`, rotation "Y" for RY; the `id` kwarg is deprecated (removed in 0.46) |
| `qp.BasicEntanglerLayers` (0.45.1 docs) | 2 2 2 2 2 2 | 12 | kept: weights (L, n_wires), `rotation=qp.RY`, ring of CNOTs, a single CNOT for two wires, `shape()` |
| PennyLane demo "Barren plateaus in quantum neural networks" | 2 2 2 2 2 2 | 12 | kept: gradient variance vs qubits for random circuits; Grant et al. (2019) identity-block initialisation as the countermeasure |
| PennyLane demo "Variational classifier" | 2 2 2 2 2 2 | 12 | kept: square loss + bias, train/validation split, accuracy tracking, `from pennylane import numpy as np` |
| PennyLane blog "import pennylane as qp" (2026-03-19) | 1 2 2 2 1 1 | 9 | kept (background): new alias `qp`; lab uses it |

## Agent-assist design decision (lesson 15)
- **Task:** the model reads a convergence-log summary and proposes optimizer settings. This is where a model can help (reading logs), and where it typically fails (quoting numbers that are not in the log, blaming the learning rate, "add shots").
- **Judge:** code recomputes the log minimum, applies its own diagnosis rule, checks ranges and a 2,000,000-shot budget, then runs the proposal itself (seed 0) and accepts only if the error < 0.03.
- **Fake server:** `fake_vqe_rule.py` registers `[[VQE-LOG]]` through `EXTRA_RULES`; the vendored server is unchanged. Prompts avoid the word "json" (the shared server's demo rule).
- **Observed** (`python agent_assist.py --fake`): diagnose ACCEPT (SPSA, error 0.0064), report REJECT (best_energy −1.8405 not in the log; wrong diagnosis; gd proposal error 0.7429), costly REJECT (1.8·10⁹ shots > budget, not run).
- Lesson 14 has no agent assist: there, an agent would only restate the brute-force comparison code already prints.

## Totals
23 new sources kept (scored 9–12; one blog and one repo marked background); reused or re-checked: AerSimulator, Aer SamplerV2, StatevectorSampler, StatevectorEstimator, Ollama OpenAI compatibility, Qiskit visualization / JupyterLab / marimo catalogue entries. Dropped or not used: qcroadmap M3 summary, qiskit-addon-opt-mapper. The Mitiq `requirements.txt` on GitHub could not be fetched (empty response), so Mitiq's Cirq bound is unknown.

## Update pass 2026-10-28 (UPDATE-L300-SPEC)
- **R3-13:** Spall, "Implementation of the Simultaneous Perturbation Algorithm for Stochastic Optimization", IEEE TAES 34(3), 1998, author's copy https://www.jhuapl.edu/SPSA/PDF-SPSA/Spall_Implementation_of_the_Simultaneous.PDF fetched. Step 1: "Practically effective (and theoretically valid) values for α and γ are 0.602 and 0.101"; gains a_k = a/(A + k + 1)^α, c_k = c/(k + 1)^γ; Bernoulli ±1 perturbations; A ≈ 10% of iterations. It replaces the golang-spsa README as the source for lesson 15's gains.
- **Mitiq 1.1.0 (learning tool, lesson 13):** facts (GPL-3.0, Python ≥3.11,<3.13, install lines) copied from the shared catalogue; not run here.

