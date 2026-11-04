# L100 research evidence — quantum computing (applied)

Method: SPEC.md research method. All retrieval was done with web_fetch / web_search on 2026-10-28.

**Rubric:** each of the following is scored 0–2:
- I = implementable
- C = current
- A = authoritative
- O = open
- T = transferable
- D = right depth

A source is kept if it scores ≥ 8/12. Every API call used in a lab is backed by at least 2 sources, at least one of them official docs or a spec.

## Version facts (all labs)
| fact | source 1 (official) | source 2 |
|---|---|---|
| qiskit 2.6.1 is the latest release (2026-10-22); Requires Python >=3.10; Apache-2.0 | https://pypi.org/project/qiskit/ | https://quantum.cloud.ibm.com/docs/en/guides/install-qiskit ("Check the Programming Language section on the Qiskit PyPI project page") |
| qiskit-aer 0.18.2 (2026-10-26); Requires Python >=3.11; Apache-2.0; "reduced maintenance mode" | https://pypi.org/project/qiskit-aer/ | https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html (page titled "Qiskit Aer 0.18.2") |
| cirq 1.7.0 (2026-06-29); Requires Python >=3.11; Apache-2.0 | https://pypi.org/project/cirq/ | https://quantumai.google/cirq/start/install ("Cirq currently supports Python 3.11 and later") |
| qiskit-qasm3-import 0.6.0 (2025-06-10), Apache-2.0; needed by qiskit.qasm3.load/loads | https://pypi.org/project/qiskit-qasm3-import/ | https://quantum.cloud.ibm.com/docs/en/api/qiskit/qasm3 ("the package qiskit_qasm3_import must be installed") |

---

## Lesson 1 — Set up your quantum environment
**Questions**
1. Which exact versions of qiskit, qiskit-aer and cirq are current, and which Python versions do they support?
2. What is the documented minimal local workflow (venv → pip → run a circuit on a local simulator) that needs no account?
3. How do you run a circuit on AerSimulator and read counts?

**Candidates**
| source | I C A O T D | score | decision |
|---|---|---|---|
| Install Qiskit (quantum.cloud.ibm.com) | 2 2 2 2 1 2 | 11 | kept: venv steps; "working locally… using simulators… installation is done" |
| qiskit PyPI | 2 2 2 2 1 1 | 10 | kept: version pin, Python floor |
| qiskit-aer PyPI | 2 2 2 2 1 1 | 10 | kept: version pin, Python ≥3.11, Bell example with AerSimulator/SamplerV2 |
| Aer tutorial "Simulators" | 2 1 2 2 1 2 | 10 | kept: `AerSimulator()`, `transpile(circ, simulator)`, `simulator.run(circ).result().get_counts()` (notebook printed qiskit 1.0.1, so C=1) |
| Cirq install | 2 2 2 2 1 2 | 11 | kept (supporting) |
| freequantumcomputing.com Aer guide | 2 2 0 1 1 2 | 8 | **dropped**: third-party tutorial site, not authoritative, and its licence wasn't checked. Only used as a hint that `seed_simulator=` exists, and the labs don't use that option |

**Key facts**
- Use a venv: `python3 -m venv .venv`, `source .venv/bin/activate`, `pip install qiskit`. Source: https://quantum.cloud.ibm.com/docs/en/guides/install-qiskit
- `AerSimulator()` is a local backend: `sim.run(circ, shots=…)` → `result.get_counts()`. Sources: https://qiskit.github.io/qiskit-aer/tutorials/1_aersimulator.html and https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html (the `run(circuits, parameter_binds=None, **run_options)` signature).
- `measure_all()` creates a register named `meas`. Source: https://quantum.cloud.ibm.com/docs/en/guides/simulate-with-qiskit-sdk-primitives ("The name of the classical register defaults to 'meas'").

## Lesson 2 — Qubits and gates in code
**Questions**
1. How do you apply X and H and measure in Qiskit 2.x, and how do you run several circuits with the current V2 primitives?
2. How are multi-qubit result bitstrings ordered?
3. Which gate definitions are framework-neutral?

**Candidates**
| source | I C A O T D | score | decision |
|---|---|---|---|
| Bit-ordering in the Qiskit SDK | 2 2 2 2 2 2 | 12 | kept: bit n-1 is leftmost and bit 0 is rightmost; `qc.x(1)` → `{'10': 1024}` |
| Aer SamplerV2 API | 2 2 2 2 1 2 | 11 | kept: `SamplerV2(*, default_shots=1024, seed=None, options=None)`, `run(pubs, *, shots=None)` |
| OpenQASM stdgates.inc | 1 2 2 2 2 1 | 10 | kept: neutral definitions of x (|0>→|1>) and h |
| transpile API | 1 2 2 2 1 1 | 9 | kept: `transpile(circuits, backend=None, …)` accepts a list |
| docs.quantum.ibm.com AerSimulator v0.42 page | — | — | **dropped**: stale API version (page itself says to migrate to latest) |

**Key facts**
- Aer `SamplerV2(seed=…)` gives "The seed for random number generation". Source: https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.primitives.SamplerV2.html. Same pattern in `StatevectorSampler(seed=…)`: https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorSampler
- Counts are read as `result[0].data.meas.get_counts()`. Sources: https://pypi.org/project/qiskit-aer/ (Bell example) and https://quantum.cloud.ibm.com/docs/en/guides/simulate-with-qiskit-sdk-primitives

## Lesson 3 — Shots, counts and probability
**Questions**
1. How do you set the number of shots and a seed with the current primitives?
2. Why do counts vary, and how big is the variation?
3. How do other frameworks expose repetitions and seeds?

**Candidates**
| source | I C A O T D | score | decision |
|---|---|---|---|
| Aer SamplerV2 API | 2 2 2 2 1 2 | 11 | kept: `seed`, `shots` |
| StatevectorSampler API | 2 2 2 2 1 1 | 10 | kept: seed is an int or Generator; "If None, a random seeded default RNG will be used" |
| Exact simulation with SDK primitives | 2 2 2 2 1 2 | 11 | kept: shots run option; the reference sampler can "introduce the effect of the sampling overhead (also known as 'shot noise')" |
| Cirq Simulation | 2 2 2 2 1 2 | 11 | kept: "You can set this seed by passing an integer or numpy.RandomState as the seed parameter in the Simulator constructor" |
| Aer primitives guide | 2 2 2 2 1 1 | 10 | kept (supporting): `pub = (circuit, params, shots)` |

**Key facts:** The spread uses the binomial standard error sqrt(p(1−p)/N). This is standard statistics, not taken from any of the sources above. The lab checks it numerically in `crosscheck_numpy.py`.

## Lesson 4 — Entanglement with a Bell pair
**Questions**
1. What is the minimal Bell-pair circuit, and what are its ideal counts?
2. In `cx`, which argument is the control and which is the target?
3. How do you get exact probabilities as well as sampled counts?

**Candidates**
| source | I C A O T D | score | decision |
|---|---|---|---|
| Aer tutorial | 2 1 2 2 1 2 | 10 | kept: Bell circuit, memory shows only '00'/'11' |
| Exact simulation with SDK primitives | 2 2 2 2 1 2 | 11 | kept: Bell counts `{'00': 513, '11': 511}` |
| stdgates.inc | 1 2 2 2 2 1 | 10 | kept: "the first qubit is the control and the second the target" |
| Bit-ordering guide | 2 2 2 2 2 2 | 12 | kept: `cx(0, 1)` has qubit 0 as control; `Statevector(...).probabilities_dict()` |
| IBM Quantum Learning: Multiple systems | 0 2 2 2 2 1 | 9 | kept (supporting, course): entanglement as correlation between systems. No code |

## Lesson 5 — Portable circuits with OpenQASM
**Questions**
1. What are the current Qiskit functions for exporting and importing OpenQASM 3 and 2, and what do they depend on?
2. How do you show that a round-trip preserved behaviour?
3. What is OpenQASM for, and who governs it (neutrality, licence)?

**Candidates**
| source | I C A O T D | score | decision |
|---|---|---|---|
| qiskit.qasm3 API | 2 2 2 2 2 2 | 12 | kept: `dumps(circuit, **kwargs)`, `loads(program, *, num_qubits=None, …)` needs qiskit_qasm3_import; experimental native `loads_experimental` |
| qiskit.qasm2 API | 2 2 2 2 2 1 | 11 | kept: `dumps(circuit, /)`, `loads(string, …)`, exact Bell export text; "OpenQASM 2 is not a suitable serialization language … consider qiskit.qpy" |
| qiskit-qasm3-import PyPI | 1 2 2 2 1 1 | 9 | kept: version 0.6.0 |
| OpenQASM intro | 1 2 2 2 2 2 | 11 | kept: "intermediate representation for higher-level compilers to communicate with quantum hardware" |
| openqasm/openqasm repo | 1 2 2 2 2 1 | 10 | kept (supporting): Apache-2.0, current version 3.1 |
| Cirq interop | 2 2 2 2 2 1 | 11 | kept (equivalents): `circuit.to_qasm(version="3.0")`, `circuit_from_qasm` needs ply |
| openqasm.com home page | 0 2 2 2 1 0 | 7 | **dropped**: navigation and bibliography only |

**Key facts**
- `Operator(a).equiv(Operator(b))` returns "True if operators are equivalent up to global phase", and `Operator(data)` accepts a `QuantumCircuit`. This is used in `qasm_lab.same_unitary`. Sources: https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Operator (official API, score 10: I2 C2 A2 O2 T1 D1) and the `Operator(qasm2.loads(...))` usage in https://quantum.cloud.ibm.com/docs/en/api/qiskit/qasm2
- The reference OpenQASM 2 file reproduces the exporter output printed in the qiskit.qasm2 docs.

## Lesson 6 — Same circuit, two frameworks
**Questions**
1. What are the Cirq equivalents of H, CNOT, measure, and of shots and seed?
2. How does Cirq order bits in histograms compared with Qiskit?
3. How do you compare results across frameworks robustly?

**Candidates**
| source | I C A O T D | score | decision |
|---|---|---|---|
| Cirq Simulation | 2 2 2 2 1 2 | 11 | kept: `cirq.Simulator(seed=…)`, `run(circuit, repetitions=…)`, `result.histogram(key=…)` |
| cirq.Result API | 2 2 2 2 1 1 | 10 | kept: histogram is "big-endian … the first measured qubit determining the highest-value bit" |
| cirq PyPI | 2 2 2 2 1 1 | 10 | kept: version, `cirq.X`, `cirq.measure(qubit, key='m')`, `cirq.Simulator().run(circuit, repetitions=20)` |
| Bit-ordering in Qiskit | 2 2 2 2 2 2 | 12 | kept: Qiskit is little-endian |
| Cirq interop gate table | 2 2 2 2 2 1 | 11 | supporting: `cx → cirq.CX`, `h → cirq.H`, `x → cirq.X` |

## Equivalents (one line each, all lessons)
| tool | source | score | fact used |
|---|---|---|---|
| PennyLane | https://docs.pennylane.ai/en/stable/introduction/circuits.html | 11 | `qp.device('default.qubit', wires=2)`, `@qp.qnode`, `qp.set_shots`, `qp.from_qasm` (needs PennyLane-Qiskit plugin) |
| Amazon Braket SDK | https://github.com/amazon-braket/amazon-braket-sdk-python | 9 | `Circuit().h(0).cnot(0, 1)`, `measurement_counts`, local `braket_sv` simulator (examples/local_bell.py), Apache-2.0. The README's main example needs an AWS account, so the line only mentions the local simulator |
| Microsoft QDK / Q# | https://github.com/microsoft/qdk | 9 | MIT. The Python package is now `qdk`: the repo shows "Drop qsharp Python Package". Q# gate names weren't fetched, so none are quoted |
| Braket "Getting started" readthedocs page | https://amazon-braket-sdk-python.readthedocs.io/en/latest/examples-getting-started.html | 6 | **dropped**: just a list of tutorial links, with no runnable code on the page |

---

# Concepts layer (CONCEPTS-SPEC.md) — evidence

Same method and rubric as above. Every number in `documentation/CONCEPTS-PRIMER.md` and `content/concepts/*.md` was computed by `research/concepts_worked_examples.py`; its recorded output is in `research/concepts_worked_examples.out.txt` (Python 3.12.15, numpy 2.5.3).

## Questions
- **Primer:** What is quantum computing used for in practice, with open-source examples? Which misconceptions do engineers bring with them?
- **Concepts 01–06:** For each lesson, what is the mental model behind the lab? Which mechanics can a learner verify with small numbers?

## Candidates
| source | I C A O T D | score | decision |
|---|---|---|---|
| IBM Learning, *Single systems: quantum information* | 1 2 2 2 2 2 | 11 | kept. Born rule ("probability equal to the absolute value squared"); worked state ((1+2i)/3, −2/3) with 5/9 and 4/9; H\|0⟩=\|+⟩, H\|1⟩=\|−⟩, H\|+⟩=\|0⟩; sign/phase changes alter later behaviour |
| IBM Learning, *Multiple systems: quantum information* | 1 2 2 2 2 2 | 11 | kept. Product vs entangled states; Bell states; measuring one system can't change the other's outcome probabilities, "as that would allow for faster-than-light communication" |
| Introduction to transpilation | 1 2 2 2 2 1 | 10 | kept. Transpilation rewrites to the target's topology and instruction set (ISA); six stages: init, layout, routing, translation, optimization, scheduling |
| quantumlib/Stim | 1 2 2 2 1 1 | 9 | kept. Fast stabilizer-circuit simulation for QEC; no non-Clifford gates; Apache-2.0 |
| quantumlib/OpenFermion | 1 2 2 2 1 1 | 9 | kept. Compiles and analyses algorithms for fermionic systems including quantum chemistry; PySCF and Psi4 plugins; Apache-2.0 |
| Aaronson, "Shor, I'll do it" | 0 1 2 1 2 2 | 8 | kept (misconception only). "trying everything in parallel just isn't the sort of thing that a quantum computer can do"; wrong answers' amplitudes "interfere destructively". Cross-checked with IBM Learning single-systems (phases and interference) |
| antoinebuteau.com "Lessons from Scott Aaronson" | 0 2 0 1 1 1 | 5 | **dropped**: secondary compilation of quotes; the primary blog was fetched instead |
| deployquantum.com course chapter | 0 2 0 1 1 2 | 6 | **dropped**: commercial training site; not authoritative |

## Facts reused from earlier sources (both already in VERIFIED-RESOURCES)
- **16 bytes per amplitude** comes from the AerSimulator API: "a state vector of n-qubits uses 2^n complex values (16 Bytes)". The GiB figures were computed by the script.
- **Cirq histogram is big-endian** (cirq.Result API). Qiskit is little-endian (bit-ordering guide). Some IBM runtime primitives return big-endian results (bit-ordering guide).
- **Application areas:**
  - PennyLane binds circuits to NumPy, PyTorch and JAX (PennyLane circuits page).
  - QDK includes a resource estimator (microsoft/qdk README).
  - Qualtran, qsim and Stim are listed in Cirq's ecosystem (cirq PyPI).

## L200–L400 concept map
No agreed curriculum beyond L100 exists in `kb/`. The progression in the primer is proposed from the topics the sources cover:
- Estimator and observables;
- transpiler targets and noise models;
- variational algorithms, using chemistry libraries;
- Stim/QEC and resource estimation.

# Platform + local-agent layer (PLATFORM-AGENT-SPEC.md) — evidence, 2026-10-28

## Questions
1. What are the verified install commands for Python 3.12 and Ollama on macOS (Homebrew) and Windows (winget)?
2. Which simulator/GPU paths exist on Apple silicon and on Windows for the pinned SDKs?
3. What Windows-only behaviour changes lab output (encoding, venv activation)?
4. Which CI labels give Apple-silicon macOS and Windows runners?
5. Is Ollama's endpoint OpenAI-compatible at `http://localhost:11434/v1`, so the shared `client.chat()` works unchanged?

## Kept (score/12) and key facts
- **Python docs, venv (12).** The PowerShell activation is `<venv>\Scripts\Activate.ps1`. The page says "it may be required to enable the Activate.ps1 script": `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.
- **Python docs, Using Python on Windows (12).**
  - The install manager is the recommended route: `winget install 9NQ7512CXL7T -e --accept-package-agreements --disable-interactivity`.
  - Runtimes are added with `py install <tag>`.
  - "the V: may be omitted" for tags starting with 3, so `py -3.12` is valid.
- **Python docs, os UTF-8 Mode (11).** UTF-8 mode is enabled by default only from 3.15 (PEP 686). In UTF-8 mode, stdout uses UTF-8. `PYTHONUTF8` controls it, so 3.12 needs `PYTHONUTF8=1`.
- **Qiskit "Visualize circuits" (10).** The text drawer output shown uses box-drawing characters (┌───┐), which is why the Windows encoding fix matters for labs 02 and 04.
- **Homebrew python@3.12 (10).** `brew install python@3.12` has an Apple-silicon bottle and installs `python3.12`.
- **winget-pkgs Python/Python/3/12 (9).** Manifests exist (id `Python.Python.3.12`), so it is listed as the alternative.
- **Homebrew ollama (10).**
  - `brew install ollama` has an Apple-silicon bottle.
  - `brew services start ollama` runs it as a service.
- **winget-pkgs Ollama/Ollama (9).** The package id is `Ollama.Ollama`, latest manifest 0.34.2.
- **Ollama OpenAI compatibility (11).**
  - The documented base URL is `http://localhost:11434/v1/`.
  - `/v1/chat/completions` supports `temperature` and `seed`.
  - `/v1/models` is listed.
- **Ollama hardware support (10).**
  - Apple GPUs are supported through Metal.
  - NVIDIA needs compute capability 5.0+ and driver 550+.
  - Vulkan provides extra GPU support on Windows.
- **Ollama library qwen2.5 (8).** The `qwen2.5:1.5b` tag is 986 MB. Models other than 3B/72B are Apache-2.0.
- **qiskit-aer-gpu PyPI (10).** "This package is only available on x86_64 Linux." The wheels are manylinux x86_64 only, so there is no GPU simulator path on the Mac mini or on Windows.
- **actions/runner-images (10).** `macos-latest` is macOS 26 arm64; `windows-latest` is Windows Server 2025 x64; `ubuntu-latest` is 24.04.

## Dropped / not retrieved
- **PyPI simple index for qiskit-aer:** the request was refused, and the project page did not list wheel files. Per-platform wheel availability is recorded in KNOWN-GAPS.
- **Docker Desktop:** not relevant, because no container is used in this topic.

## Agent-assist design decision
- **Task:** OpenQASM drafting fits lesson 5, where the independent parser already exists. Other lessons would only have the agent restate numbers that code already prints, so they get no agentAssist.
- **Judge:** the existing `crosscheck_qasm_numpy.py`, plus a spec dict in code. Unverifiable drafts are rejected.
- **Fake server:** extended through `EXTRA_RULES` from `fake_qasm_rule.py` with the marker `[[QASM-DRAFT]]`. The vendored copy is byte-identical.
- **Observed** (`python agent_assist.py --fake`, Python 3.12.15, numpy 2.5.3):
  - bell: ACCEPT, counts `{'00': 502, '11': 498}`;
  - ghz3: REJECT, `{'000': 0.5, '011': 0.5}`;
  - phase: REJECT, `unsupported statement: 'rz(pi/2) q[0]'`.


## Update pass 2026-10-28: review F25 (reference primitives instead of Aer)
- Question: can every L100 lab run on Qiskit's built-in primitives, with Aer only as an equivalent?
- Source re-checked: StatevectorSampler API (https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorSampler): `StatevectorSampler(*, default_shots=1024, seed=None)`, `run(pubs, *, shots=None)`, results per register (`result[0].data.<creg>.get_counts()`), incompatible with mid-circuit measurements (L100 measures only at the end).
- Decision: labs 01-06 use `StatevectorSampler(seed=…)`; lab 01 keeps `transpile` with an explicit basis (`rz, sx, x, cx`). qiskit-aer 0.18.2 stays pinned as an optional equivalent ("reduced maintenance mode" per PyPI). Learning-tool facts come from kb/shared/LEARNING-TOOLS-CATALOG.md.
