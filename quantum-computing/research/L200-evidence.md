# L200 research evidence — quantum computing ("Build it", lessons 7–11)

Method: kb/SPEC.md research method, same rubric as `L100-evidence.md` (I implementable, C current, A authoritative, O open, T transferable, D right depth; 0–2 each; keep ≥ 8/12). All retrieval was done with web_fetch / web_search on 2026-10-28. Every API used in a lab is backed by official API docs plus a second source (tutorial, guide, or the equivalent Cirq doc). Numbers in the notes come from `L200_worked_examples.py` (output in `L200_worked_examples.out.txt`).

## Lesson 7 — Bernstein–Vazirani as a pattern
**Questions:** 1. How is a BV query gate built for a given `s` in current Qiskit, and in which bit order? 2. Why is the ancilla prepared in |−⟩? 3. How many classical queries are needed?

| source | I C A O T D | score | decision |
|---|---|---|---|
| IBM Quantum Learning, "The Deutsch-Jozsa algorithm" (BV section) | 2 2 2 2 2 2 | 12 | kept: problem statement, `bv_query` (`for index, bit in enumerate(reversed(s))` → `qc.cx(index, len(s))`), one query vs n classical queries |
| Cirq `examples/bernstein_vazirani.py` | 2 2 2 2 2 2 | 12 | kept: same oracle in Cirq, ancilla prepared with X then H, optional bias bit (`f(a) = a·factors + bias`) → basis for the buildTask |
| StatevectorSampler API | 2 2 2 2 1 2 | 11 | kept (reused from L100): `StatevectorSampler(seed=…)`, `run(pubs, shots=…)` |
| quantum-education-modules.readthedocs.io BV page | 2 2 1 1 1 2 | 9 | **dropped**: only a search snippet was retrieved, licence not checked; IBM + Cirq already cover it |
| quantumcomputingcourses.com course listing | 0 1 0 1 0 0 | 2 | **dropped**: affiliate listing, no code |

**Key facts:** "the Deutsch-Jozsa circuit solves the Bernstein-Vazirani problem with a single query, any classical query algorithm must make at least n queries" (IBM Learning); phase kickback with the ancilla in |−⟩ (IBM Learning); bias bit = X on the output qubit (Cirq example).

## Lesson 8 — Small Grover search
**Questions:** 1. How is a multi-state phase oracle built in Qiskit 2.x? 2. What does `grover_operator` add? 3. What is the documented iteration formula?

| source | I C A O T D | score | decision |
|---|---|---|---|
| IBM tutorial "Grover's algorithm" | 2 2 2 2 2 2 | 12 | kept: `grover_oracle` with reversed target, X on zeros, `MCMTGate(ZGate(), n-1, 1)`; `optimal_num_iterations = floor(pi / (4*asin(sqrt(M/2**n))))`; `.power(k)`; `StatevectorSampler` and `data.meas.get_counts()`; 2Q depth 39 (n=3) … 14824 (n=9) |
| `grover_operator` API | 2 2 2 2 2 2 | 12 | kept: signature, Q = A·S0·A†·Sf, phase (not bit-flip) oracle, default zero reflection differs by a global phase only |
| Cirq "Textbook algorithms" (Grover section) | 2 2 2 2 1 2 | 11 | kept (equivalent): oracle as X + Toffoli + X with ancilla; n=2 needs one iteration |
| Statevector API | 2 2 2 2 1 2 | 11 | kept: `probabilities_dict`, `Statevector(circuit)` |

**Key facts:** P(k) = sin²((2k+1)θ) checked numerically against the matrix model (numpy, all k ≤ 4); for M = N/2 every k gives 0.5 (computed).

## Lesson 9 — QFT as a building block
**Questions:** 1. Which Qiskit object is current for the QFT? 2. What sign/normalisation does it use (to match numpy)? 3. How is the inverse obtained?

| source | I C A O T D | score | decision |
|---|---|---|---|
| `QFTGate` API | 2 2 2 2 2 2 | 12 | kept: \|j⟩ ↦ 2^{-n/2} Σ e^{2πijk/2ⁿ}\|k⟩ (+ sign) |
| `QFT` class API | 1 2 2 2 1 2 | 10 | kept for the deprecation fact: deprecated since 2.1, removed in 3.0, use `QFTGate` or `synth_qft_full`; do_swaps/inverse semantics |
| `cirq.qft` API | 2 2 2 2 2 2 | 12 | kept: `cirq.qft(*qubits, without_reverse=False, inverse=False)` |
| Cirq "Textbook algorithms" (QFT section) | 2 2 2 2 2 2 | 12 | kept: same matrix with ω = e^{2πi/2ⁿ}; inverse = negated exponents; output reversed without swaps |
| Statevector API | 2 2 2 2 1 2 | 11 | kept: `evolve(other)` accepts a QuantumCircuit (buildTask Qiskit part) |

**Key facts:** numpy's `ifft(…, norm="ortho")` uses e^{+2πijk/N}/√N, so it equals the QFT; verified to 1.2e−16 (cross-check). Without swaps the matrix equals the DFT with bit-reversed rows (computed).

## Lesson 10 — Parameterized circuits
**Questions:** 1. How are Parameters created and bound (dict vs list order)? 2. How does a V2 primitive sweep many values in one PUB, and what shape must the values have? 3. How do sampler results expose per-binding counts?

| source | I C A O T D | score | decision |
|---|---|---|---|
| `Parameter` API | 2 2 2 2 2 2 | 12 | kept: `Parameter(name)`, `assign_parameters({phi: 3.14})`, expressions |
| `QuantumCircuit` API | 2 2 2 2 2 1 | 11 | kept: `parameters` sorted alphabetically (list-binding order), `assign_parameters(..., inplace=False)` returns a copy, `find_bit` |
| `StatevectorEstimator` API | 2 2 2 2 2 2 | 12 | kept: PUB (circuit, observables, parameter values); example with params shape (100, 2) and observables shape (3, 1) → evs shape (3, 100); exact results |
| `StatevectorSampler` API | 2 2 2 2 2 2 | 12 | kept: PUB (circuit, parameter values); `result.data.<reg>.get_counts(22)` for sweep index 22 |
| Cirq "Parameter sweeps" | 2 2 2 2 2 2 | 12 | kept (equivalent): `sympy.Symbol`, `cirq.Linspace`, `run_sweep` |
| `BitArray` API page | – | – | **not retrieved** (fetch returned no document); `get_counts(loc)` is taken from the StatevectorSampler example instead |

## Lesson 11 — Transpiling to a device layout
**Questions:** 1. Which fake/generic backend ships with current Qiskit (no extra package)? 2. How are line and heavy-hex coupling maps built? 3. What do optimization levels 0–3 do, and how is the run made repeatable?

| source | I C A O T D | score | decision |
|---|---|---|---|
| `GenericBackendV2` API | 2 2 2 2 2 2 | 12 | kept: `GenericBackendV2(num_qubits, basis_gates=None, *, coupling_map=None, …, seed=None)`; default basis ["id", "rz", "sx", "x", "cx"]; fully connected if no map |
| `CouplingMap` API | 2 2 2 2 2 2 | 12 | kept: `from_line`, `from_ring`, `from_heavy_hex(distance)` with n = (5d² − 2d − 1)/2, `get_edges()` |
| `generate_preset_pass_manager` API | 2 2 2 2 2 2 | 12 | kept: default level 2; levels 0–3; `seed_transpiler`; loose `basis_gates` |
| "Set transpiler optimization level" guide | 2 2 2 2 1 2 | 11 | kept: what each level does (TrivialLayout at 0, Sabre, 2Q resynthesis at 3); "increasing the level of optimization does not always make a difference" |
| Cirq "Qubit routing" | 2 2 2 2 2 2 | 12 | kept (equivalent): `cirq.RouteCQC(device_graph)`, `optimize_for_target_gateset` |
| `FakeSherbrooke` (qiskit-ibm-runtime), seen in the guide | 2 2 2 2 1 2 | – | **not used**: extra package and vendor-specific; GenericBackendV2 covers the lesson |

**Key facts:** two-qubit depth via `qc.depth(lambda x: x.operation.num_qubits == 2)` (Grover tutorial); a SWAP is 3 CX and H = RZ(π/2)·SX·RZ(π/2) up to global phase (computed in numpy, not quoted).

## Agent-assist design decision (lesson 8)
- **Task:** the agent proposes the marked set and k for a plain-English search. This is where a model genuinely helps (turning words into bitstrings) and where it typically fails (q0-first bit order, reusing k).
- **Judge:** a predicate in code + numpy P(success). Code can override k or reject when amplification is impossible.
- **Fake server:** `fake_grover_rule.py` registers marker `[[GROVER-ORACLE]]` through `EXTRA_RULES`; the vendored server is unchanged. Prompts avoid the word "json" because the shared fake server routes any request containing it to its own demo rule (found while testing).
- **Observed** (`python agent_assist.py --fake`, Python 3.12.15, numpy 2.5.3): single REJECT (bit order), pair ACCEPT with k overridden 2 → 1, even REJECT (P = 0.5).

## Totals
18 new sources kept (all scored 10–12); 3 reused from L100 (StatevectorSampler API, Bit-ordering guide, Ollama OpenAI compatibility); 3 candidates dropped or not used; 1 page (BitArray API) not retrievable.
