"""Build content/L200.json from the lesson metadata below + the lab files on disk.

Run from the domain folder:  python tools/build_l200_json.py
`code` is always read from the lab file, so it stays an exact copy. Every buildTask solution path is checked.
"""
import json
import os
import posixpath
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABS = "labs/L200"

ENV = ("Mac mini or Windows 11; Python 3.12 venv (lesson 1); qiskit 2.6.1, cirq 1.7.0, numpy. No new packages.")
SIM = ("Exact, noise-free statevector primitives on the local CPU. On hardware, noise turns certain answers into "
       "most-frequent ones.")
PLATFORMS = {"mac": "expected", "windows": "expected"}
PLATFORM_NOTE = ("mac/windows 'expected': authored and run on Linux only; lab code uses pathlib, utf-8 file I/O, "
                 "sys.executable and 127.0.0.1; CI matrix runs the same tools/run_labs.py on macos-latest and windows-latest.")

S = {  # only URLs retrieved during research (see research/L200-evidence.md)
    "bv_learn": ("IBM Quantum Learning: The Deutsch-Jozsa algorithm (Bernstein-Vazirani section)",
                 "https://quantum.cloud.ibm.com/learning/en/courses/fundamentals-of-quantum-algorithms/quantum-query-algorithms/deutsch-jozsa-algorithm"),
    "cirq_bv": ("Cirq example: bernstein_vazirani.py", "https://github.com/quantumlib/Cirq/blob/main/examples/bernstein_vazirani.py"),
    "grover_tut": ("Grover's algorithm (IBM Quantum tutorial)", "https://quantum.cloud.ibm.com/docs/en/tutorials/grovers-algorithm"),
    "grover_op": ("grover_operator API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.grover_operator"),
    "cirq_textbook": ("Cirq: Textbook algorithms (QFT, phase estimation, Grover)", "https://quantumai.google/cirq/experiments/textbook_algorithms"),
    "qftgate": ("QFTGate API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QFTGate"),
    "qft_class": ("QFT class API (deprecated since 2.1)", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QFT"),
    "cirq_qft": ("cirq.qft API", "https://quantumai.google/reference/python/cirq/qft"),
    "statevector": ("Statevector API (evolve, probabilities_dict)", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Statevector"),
    "parameter": ("Parameter API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.Parameter"),
    "qc_api": ("QuantumCircuit API (parameters, assign_parameters, find_bit)", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.QuantumCircuit"),
    "sv_estimator": ("StatevectorEstimator API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorEstimator"),
    "sv_sampler": ("StatevectorSampler API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.primitives.StatevectorSampler"),
    "cirq_params": ("Cirq: Parameter sweeps", "https://quantumai.google/cirq/simulate/params"),
    "generic": ("GenericBackendV2 API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.providers.fake_provider.GenericBackendV2"),
    "coupling": ("CouplingMap API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.transpiler.CouplingMap"),
    "preset_pm": ("generate_preset_pass_manager API", "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.transpiler.generate_preset_pass_manager"),
    "set_opt": ("Set transpiler optimization level (guide)", "https://quantum.cloud.ibm.com/docs/en/guides/set-optimization"),
    "cirq_routing": ("Cirq: Qubit routing (RouteCQC)", "https://quantumai.google/cirq/transform/routing_transformer"),
    "bitorder": ("Bit-ordering in the Qiskit SDK", "https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering"),
    "ollama_openai": ("Ollama: OpenAI compatibility (/v1/chat/completions)", "https://docs.ollama.com/api/openai-compatibility"),
}


def src(*keys):
    return [{"title": S[k][0], "url": S[k][1]} for k in keys]


def step(title, detail, expected, if_not):
    return {"title": title, "detail": detail, "expected": expected, "ifNot": if_not}


def pending(local, ci):
    return {"status": "pending-ci",
            "how": ("qiskit/cirq cannot be pip-installed in the authoring sandbox (no package network). Ran locally "
                    f"(Python 3.12.15, numpy 2.5.3): {local} SDK part: {ci} runs in .github/workflows/labs.yml job "
                    "'sdk-labs' (REQUIRE_QUANTUM_SDKS=1, pinned versions); not yet observed.")}


LESSONS = [
    {
        "dir": "07-bernstein-vazirani", "file": "bv_lab.py",
        "id": "bernstein-vazirani-pattern", "number": 7, "title": "Bernstein–Vazirani as a pattern",
        "phase": "Algorithms", "category": "oracles",
        "description": "Find a hidden bit-string with one oracle query; build the oracle yourself and extend it.",
        "outcome": "You can build a parity oracle from a bit-string, wrap any oracle in the H–query–H pattern, and extend it with a bias bit.",
        "estimatedTime": "30-45 minutes",
        "overview": ["One query reveals all n bits of s because the oracle's answers become phases and a layer of H turns those phases into |s⟩."],
        "prerequisites": ["Lessons 2 and 4 (H, CX, bit order)"],
        "glossary": [
            {"term": "oracle (query gate)", "meaning": "Circuit that computes f(x) into an ancilla; the algorithm may call it but not look inside."},
            {"term": "phase kickback", "meaning": "With the ancilla in |−⟩, a flip of the ancilla becomes a −1 phase on the input."},
            {"term": "binary dot product s·x", "meaning": "Parity of the bits of x where s has a 1."},
        ],
        "concepts": ["Oracle construction: one CX per 1 in s.", "Phase kickback turns f(x) into (−1)^f(x).",
                     "H on every input maps the phase pattern to |s⟩: answer with certainty."],
        "steps": [
            step("Run the numpy cross-check", "python crosscheck_numpy.py", "secret 1011: {'1011': 1.0}; all 16 four-bit secrets recovered: True.",
                 "Run from the lab folder so labs/_shared/qsim is found."),
            step("Run the lab", "python bv_lab.py", "secret 1011: {'1011': 100} with 1 query; classical baseline needs 4 (6 for 110101).",
                 "ModuleNotFoundError qiskit: activate the lesson 1 venv."),
            step("Read the oracle", "Look at the drawing: CX from q0, q1, q3 to the ancilla q4 for '1011'.", "Three CX gates, none from q2.",
                 "CX on q2 means the string was not reversed (bit order)."),
            step("Try it", "python try_it.py", "no_kickback -> {'0000': 1.0}; unreversed -> {'1101': 1.0}.", "Compare with the tryIt predictions."),
            step("Build task: add a bias bit", "Write my_bias.py (see buildTask), then run the check (mac / windows).",
                 "OK: every 3-bit secret with bias 0 or 1 still returns the secret.", "If bias 1 changes the answer, you flipped an input qubit instead of the ancilla."),
            step("Run the tests", "python -m unittest -v", "OK (SDK tests skip without qiskit).", "Read the failing assertion; usually bit order."),
        ],
        "codeWalkthrough": [
            {"title": "for qubit, bit in enumerate(reversed(secret))", "detail": "Strings are written q(n−1)…q0, so the oracle walks them reversed; each '1' adds qc.cx(qubit, n)."},
            {"title": "qc.x(n); qc.h(range(n + 1))", "detail": "Puts the ancilla in |−⟩ (phase kickback) and the inputs in uniform superposition."},
            {"title": "qc.compose(oracle, inplace=True)", "detail": "The single query. bv_circuit accepts any oracle circuit, which is what makes it a reusable pattern."},
            {"title": "getattr(result[0].data, qc.cregs[0].name)", "detail": "Reads the register by its real name ('c') instead of assuming it."},
        ],
        "buildTask": {"task": "Support f(x) = s·x ⊕ b: add recovered_numpy(secret, bias) and bv_oracle_with_bias(secret, bias), and show the answer is still s.",
                      "hints": ["A constant b only needs one X on the ancilla.", "A −1 on every term is a global phase: it cannot change counts.",
                                "Reuse crosscheck_numpy.oracle_ops and bv_ops for the numpy version."],
                      "solution": "labs/L200/07-bernstein-vazirani/solution_bias.py",
                      "check": "python -m unittest test_build_task -v (numpy: all 3-bit secrets x bias 0/1; Qiskit variant in CI)"},
        "expectedResults": ["{'1011': 100} from one query", "Classical baseline: 4 queries for 1011, 6 for 110101", "numpy and Qiskit agree"],
        "testCases": [{"action": "bv_lab.run(bv_circuit(bv_oracle(s))) for 1011, 110101, 0000", "expected": "{s: 100}"},
                      {"action": "crosscheck_numpy.all_secrets_found(4)", "expected": "True"}],
        "tryIt": [
            {"task": "Delete qc.x(n) in bv_circuit (ancilla starts in |+⟩).", "predict": "Do you still read 1011?",
             "expected": "{'0000': 1.0}: no |−⟩, no kickback, the oracle has no visible effect.", "validatedBy": "local: try_it.py numpy (observed); Qiskit variant pending-ci"},
            {"task": "Loop over secret instead of reversed(secret) in bv_oracle.", "predict": "Which string comes back?",
             "expected": "{'1101': 1.0}: the reversed secret, a pure bit-order bug.", "validatedBy": "local: try_it.py numpy (observed); Qiskit variant pending-ci"},
        ],
        "troubleshooting": [{"symptom": "Counts spread over many strings", "action": "Check the ancilla prep (x then h) and that you measure only the n inputs."},
                            {"symptom": "Answer is reversed", "action": "Walk reversed(secret) when mapping string positions to qubits."}],
        "equivalents": ["Same idea in Cirq: examples/bernstein_vazirani.py builds the oracle with CNOTs into an output qubit prepared with X then H, plus an optional bias X.",
                        "Deutsch–Jozsa uses the same circuit; only the post-processing (OR of the bits) differs."],
        "inRealSystems": ["Used as a first end-to-end check of a new backend or compiler: the right answer is certain.",
                          "The query-H-measure skeleton reappears in Simon's algorithm and phase estimation."],
        "useWhen": "Use the BV pattern to test oracles, kickback and bit order; avoid presenting it as a speed-up on real data.",
        "checkYourself": [{"q": "Why must the ancilla start in |−⟩?", "a": "So the oracle's flip becomes a phase on the inputs (kickback); |+⟩ is unchanged by CX."},
                          {"q": "How many CX gates does the oracle for 110101 have?", "a": "Four, one per '1'."}],
        "checkpoint": "PASS if one query returns the secret for 1011 and 110101 and your bias-bit oracle passes test_build_task.",
        "sources": src("bv_learn", "cirq_bv", "sv_sampler", "bitorder"),
        "next": "L200 #8 Small Grover search: the same phase-oracle pattern, now amplifying a marked answer. (Simon's algorithm and phase estimation: not built - see KNOWN-GAPS 'L400 candidates'.)",
        "validation": pending("`python crosscheck_numpy.py`, `python try_it.py`, `python solution_bias.py` (outputs in README); "
                              "`python -m unittest` -> 10 tests: 5 OK, 5 SDK tests skipped.",
                              "bv_lab.py, test_bv.py and the Qiskit variants in test_try_it.py/test_build_task.py"),
        "projectFiles": [("bv_lab.py", "main lab: oracle + BV circuit + classical baseline"),
                         ("crosscheck_numpy.py", "independent numpy BV on labs/_shared/qsim"),
                         ("solution_bias.py", "buildTask reference solution"), ("test_build_task.py", "buildTask check (BUILD_TASK_MODULE)"),
                         ("test_bv.py", "unittest: numpy always, Qiskit in CI"), ("README.md", "run commands and observed output")],
        "summary": "Bernstein–Vazirani shows the oracle pattern: superpose, query once with the ancilla in |−⟩, interfere, measure. A parity oracle is one CX per 1 in s, and the answer is certain.",
    },
    {
        "dir": "08-grover-search", "file": "grover_lab.py",
        "id": "small-grover-search", "number": 8, "title": "Small Grover search",
        "phase": "Algorithms", "category": "amplitude amplification",
        "description": "Search 2-3 qubits with a phase oracle and grover_operator; choose the iteration count and see success vs iterations.",
        "outcome": "You can write a phase oracle for any marked set, pick the optimal iteration count, and reject proposals that would overshoot.",
        "estimatedTime": "30-45 minutes",
        "overview": ["Each Grover iteration rotates the state toward the marked states; the success probability rises, peaks, then falls."],
        "prerequisites": ["Lesson 7", "Lesson 5 agent assist (optional)"],
        "glossary": [
            {"term": "phase oracle", "meaning": "Multiplies marked basis states by −1 and leaves the rest."},
            {"term": "diffusion", "meaning": "Reflection about the uniform state; grover_operator adds it after the oracle."},
            {"term": "amplitude amplification", "meaning": "Repeating oracle + diffusion to grow the marked amplitudes."},
        ],
        "concepts": ["P(success) = sin²((2k+1)θ), sin θ = √(M/N).", "k_opt = ⌊π/(4·asin√(M/N))⌋.", "More marked states need fewer iterations."],
        "steps": [
            step("Run the numpy cross-check", "python crosscheck_numpy.py", "Oracle diagonal for 011,100: [1,1,1,-1,-1,1,1,1]; P by k for 101: 0.125, 0.7812, 0.9453, 0.3301, 0.0122.",
                 "Run from the lab folder (labs/_shared/qsim on the path)."),
            step("Run the lab", "python grover_lab.py", "2 qubits: k=1 gives 1.0; 3 qubits: k=2 gives 0.9453 and '101' tops the counts.",
                 "ImportError MCMTGate/grover_operator: check qiskit==2.6.1."),
            step("Change the iteration count", "python try_it.py", "k=3 drops to 0.3301; two marked states with k=2 give 0.25 (k=1 gives 1.0).", "Compare with the tryIt predictions."),
            step("Build task: search by predicate", "Write my_search.py (see buildTask), then run the check (mac / windows).",
                 "OK: x==5 -> (['101'], 2, 0.9453); x%3==0 -> (['000','011','110'], 1, 0.8437); M=0 or M>=N/2 refused.", "Use the floor formula and format(x, '03b')."),
            step("Agent assist", "python agent_assist.py --fake   (or without --fake for your local Ollama model)",
                 "single REJECT (bit order), pair ACCEPT with k overridden to 1, even REJECT (no amplification).", "'No local model reachable': start Ollama or add --fake."),
            step("Run the tests", "python -m unittest -v", "OK (SDK tests skip without qiskit).", "Read the failing assertion."),
        ],
        "codeWalkthrough": [
            {"title": "zeros = [...]; qc.x(zeros); MCMTGate(ZGate(), n - 1, 1)", "detail": "Open controls: X turns each '0' bit into a '1', the multi-controlled Z flips |1…1⟩, X undoes it."},
            {"title": "grover_operator(oracle).power(iterations)", "detail": "Oracle + diffusion as one block, repeated k times."},
            {"title": "math.floor(math.pi / (4 * math.asin(math.sqrt(M / 2**n))))", "detail": "The iteration count from the IBM tutorial; it lands on the first peak."},
            {"title": "Statevector(...).probabilities_dict()", "detail": "Exact success probability without shot noise, so the k-sweep is a clean curve."},
        ],
        "buildTask": {"task": "Add grover_search_numpy(predicate, n_qubits) (and Qiskit grover_search) that marks every x with predicate(x) True, picks k, and returns (marked, k, P).",
                      "hints": ["marked = [format(x, f'0{n}b') for x in range(2**n) if predicate(x)]", "Raise ValueError when M == 0 or 2*M >= N.",
                                "Reuse crosscheck_numpy.optimal_iterations and success."],
                      "solution": "labs/L200/08-grover-search/solution_search.py",
                      "check": "python -m unittest test_build_task -v (numpy part local; Qiskit variant in CI)"},
        "expectedResults": ["P(success) curve 0.125 → 0.7812 → 0.9453 → 0.3301 for one marked state of 8", "Top count is the marked state at k_opt"],
        "testCases": [{"action": "success_probability(marked, k) for k in 0..3", "expected": "Equals numpy to 3 decimals"},
                      {"action": "Operator(grover_oracle(['011','100'])) diagonal", "expected": "[1,1,1,-1,-1,1,1,1]"}],
        "tryIt": [
            {"task": "Run marked ['101'] with k=3 instead of 2.", "predict": "More iterations, higher success?",
             "expected": "P drops from 0.9453 to 0.3301: the rotation overshoots.", "validatedBy": "local: try_it.py numpy (observed); Qiskit variant pending-ci"},
            {"task": "Mark ['101', '110'] but keep k=2.", "predict": "Does adding a marked state help at k=2?",
             "expected": "P = 0.25; the optimum is now k=1 with P = 1.0.", "validatedBy": "local: try_it.py numpy (observed); Qiskit variant pending-ci"},
        ],
        "agentAssist": {
            "task": "A local model proposes the marked bitstrings and the iteration count for three plain-English searches; code accepts, overrides k, or rejects.",
            "prompt": "System: You design Grover searches in Qiskit. Bitstrings are written q(n-1)...q0 (qubit 0 is the RIGHTMOST character). Reply with one fenced code block holding {\"marked\": [bitstrings], \"iterations\": k}. User: [[GROVER-ORACLE]] 3 qubits: mark the one state with q0 = 1, q1 = 1, q2 = 0",
            "check": "Code decides: a Python predicate (agent_assist.TASKS) rebuilds the marked set; numpy computes P(success) for the proposed k and k_opt. Wrong set -> REJECT; worse k -> ACCEPT with code's k; best P < 0.9 -> REJECT.",
            "expected": "single REJECT  marks ['110'] but spec needs ['011']\npair   ACCEPT  oracle ok; k=2 gives P=0.25, code uses k=1: P=1.0\neven   REJECT  oracle ok, but best P(success)=0.5 at k=0: no amplification (M/N=2/4)",
            "realModelNote": "Not run with a real model here. Small local models often write q0 first or reuse a k; the verdict code is the same, so those proposals are rejected or overridden.",
            "validatedBy": "local: agent_assist.py --fake and test_agent_assist.py against the vendored fake server (observed); Qiskit agreement test pending-ci"},
        "troubleshooting": [{"symptom": "Wrong state amplified", "action": "Marked strings are q(n−1)…q0; reverse before choosing X positions."},
                            {"symptom": "Success near 0.5 whatever k", "action": "Half the states are marked: Grover cannot help; sample classically."}],
        "equivalents": ["Same idea in Cirq: the textbook-algorithms notebook builds a 2-qubit Grover oracle with X gates and a Toffoli on an ancilla.",
                        "Qiskit alternative oracle input: grover_operator(oracle=Statevector.from_label('011'))."],
        "inRealSystems": ["Amplitude amplification is a subroutine inside amplitude estimation and some optimisation heuristics.",
                          "The IBM tutorial shows two-qubit depth growing from 39 (3 qubits) to 14824 (9 qubits): a fault-tolerant-era algorithm."],
        "useWhen": "Use when good answers are rare and checkable by a reversible oracle and M is known; avoid when M ≥ N/2 or M is unknown.",
        "checkYourself": [{"q": "N=8, one marked state: how many iterations?", "a": "2 (P = 0.9453)."},
                          {"q": "Why can't Grover help when 2 of 4 states are marked?", "a": "θ = 45°, so every k gives P = 0.5."}],
        "checkpoint": "PASS if k=2 gives 0.9453 for '101', your predicate search passes test_build_task, and agent assist rejects the bit-order mistake.",
        "caution": "Agent assist: the model only proposes; code checks every proposal and nothing it writes is executed. Never put secrets or tokens in a prompt.",
        "sources": src("grover_tut", "grover_op", "cirq_textbook", "statevector", "ollama_openai"),
        "next": "L300 #12 Noise models: how Bell and GHZ results degrade: what gate and readout noise do to a success probability like Grover's. (Amplitude estimation: not built - see KNOWN-GAPS 'L400 candidates'.)",
        "validation": pending("`python crosscheck_numpy.py`, `python try_it.py`, `python solution_search.py`, `python agent_assist.py --fake` (outputs in README); "
                              "`python -m unittest` -> 20 tests: 14 OK, 6 SDK tests skipped.",
                              "grover_lab.py, test_grover.py and the Qiskit variants in test_try_it.py/test_build_task.py/test_agent_assist.py"),
        "projectFiles": [("grover_lab.py", "main lab: oracle, grover_operator, k-sweep, counts"),
                         ("crosscheck_numpy.py", "numpy Grover + gate-level oracle diagonal"),
                         ("solution_search.py", "buildTask reference solution"), ("test_build_task.py", "buildTask check"),
                         ("agent_assist.py", "agent assist: model proposes marked set + k, code decides"),
                         ("fake_grover_rule.py", "deterministic fake-model route ([[GROVER-ORACLE]])"),
                         ("test_agent_assist.py", "agent-assist tests (fake server only)"),
                         ("test_grover.py", "unittest"), ("README.md", "run commands and observed output")],
        "summary": "Grover search marks good states with a phase oracle and amplifies them with repeated reflections. Success follows sin²((2k+1)θ), so the iteration count must come from M and N.",
    },
    {
        "dir": "09-qft-building-block", "file": "qft_lab.py",
        "id": "qft-building-block", "number": 9, "title": "The QFT as a building block",
        "phase": "Algorithms", "category": "transforms",
        "description": "Build the 3-qubit QFT from gates, compare it with numpy's DFT, invert it, and use it to read a period.",
        "outcome": "You can build and verify a QFT (sign, normalisation, bit order), invert it, and use it to read a period.",
        "estimatedTime": "30-45 minutes",
        "overview": ["The QFT is the DFT on amplitudes; verify it against numpy once and you can reuse it inside larger algorithms."],
        "prerequisites": ["Lessons 7-8", "numpy FFT basics"],
        "glossary": [
            {"term": "QFT", "meaning": "|j⟩ ↦ (1/√N) Σ_k e^{+2πijk/N} |k⟩ (Qiskit QFTGate docs)."},
            {"term": "controlled phase (cp)", "meaning": "Adds phase e^{iλ} when both qubits are 1; symmetric in its two qubits."},
            {"term": "bit reversal", "meaning": "Final SWAPs that put output qubits in the expected order."},
        ],
        "concepts": ["QFT matrix = np.fft.ifft(eye, norm='ortho').", "Inverse = reversed gates with negated angles.", "Periodic input → peaks at multiples of N/r."],
        "steps": [
            step("Run the numpy cross-check", "python crosscheck_numpy.py", "max |difference| 0.0 for QFT and inverse; QFT|5> magnitudes all 0.3536.", "Run from the lab folder."),
            step("Run the lab", "python qft_lab.py", "hand-built == numpy DFT, == QFTGate, QFT then inverse == identity: all True.",
                 "DeprecationWarning for QFT: use QFTGate, as the lab does."),
            step("Read QFT|5>", "Read the phases line.", "Phases 0, 0.625, 0.25, 0.875, 0.5, 0.125, 0.75, 0.375 turns (5k/8 mod 1).", "Different order: check bit order and swaps."),
            step("Try it", "python try_it.py", "no swaps: error 0.7071, 0 after bit-reversing rows; negated angles equal np.fft.fft.", "Compare with the tryIt predictions."),
            step("Build task: read a period", "Write my_period.py (see buildTask), then run the check (mac / windows).",
                 "OK: periods 1, 2, 4 found for every offset (n = 3, 4).", "Use math.gcd of N and the peak positions."),
            step("Run the tests", "python -m unittest -v", "OK (SDK tests skip without qiskit).", "Read the failing assertion."),
        ],
        "codeWalkthrough": [
            {"title": "for j in reversed(range(n)): qc.h(j); qc.cp(np.pi / 2 ** (j - k), k, j)", "detail": "Most significant qubit first; phases halve with distance."},
            {"title": "qc.swap(i, n - 1 - i)", "detail": "Bit reversal; without it the result is the DFT with bit-reversed rows."},
            {"title": "np.fft.ifft(np.eye(2 ** n), axis=0, norm='ortho')", "detail": "numpy's transform with the same +i sign and 1/√N as the QFT."},
            {"title": "qft_circuit(n).inverse()", "detail": "Reverses the gate list and conjugates each gate."},
        ],
        "buildTask": {"task": "Add period_numpy(n, period, offset) (and period_qiskit) that prepares a periodic state, applies the QFT and returns the period from the peaks.",
                      "hints": ["v[offset::period] = 1, then normalise.", "Peaks sit at multiples of N/r, so N / gcd(N, peaks) = r.",
                                "Offsets change only phases, not peak positions."],
                      "solution": "labs/L200/09-qft-building-block/solution_period.py",
                      "check": "python -m unittest test_build_task -v (numpy part local; Qiskit variant in CI)"},
        "expectedResults": ["QFT == DFT == QFTGate", "QFT · QFT⁻¹ = identity", "Period 2 → peaks '000', '100'"],
        "testCases": [{"action": "Operator(qft_circuit(n)) for n = 2, 3, 4", "expected": "allclose to dft_matrix(n)"},
                      {"action": "qft_of_basis_state(5, 3)", "expected": "equals the numpy simulator state"}],
        "tryIt": [
            {"task": "Call qft_circuit(3, swaps=False).", "predict": "Still the DFT?",
             "expected": "Max error 0.7071; after bit-reversing the rows it is exact (0.0).", "validatedBy": "local: try_it.py numpy (observed); Qiskit variant pending-ci"},
            {"task": "Negate the angle in qc.cp.", "predict": "What transform is it now?",
             "expected": "It equals np.fft.fft (the inverse DFT of the QFT), error 0.0; vs the QFT the error is 0.7071.", "validatedBy": "local: try_it.py numpy (observed); Qiskit variant pending-ci"},
        ],
        "troubleshooting": [{"symptom": "Matrix matches only up to row order", "action": "Add the final swaps or reverse the bits classically."},
                            {"symptom": "Matches np.fft.fft instead", "action": "Your phase sign is negative: that is the inverse QFT."}],
        "equivalents": ["Same idea in Cirq: cirq.qft(*qubits, without_reverse=False, inverse=False); cirq.unitary compares it with numpy.",
                        "Qiskit synthesis without the gate object: qiskit.synthesis.qft.synth_qft_full (named in the QFT deprecation note)."],
        "inRealSystems": ["Inside phase estimation (energies, eigenvalues) and Shor's period finding.",
                          "Approximate QFT drops the smallest rotations to save depth (QFT approximation_degree)."],
        "useWhen": "Use the QFT inside phase estimation or period finding; skip the final swaps when the QFT is last and bits can be reversed classically.",
        "checkYourself": [{"q": "Which numpy call matches Qiskit's QFT?", "a": "np.fft.ifft(..., norm='ortho') (+i sign, 1/√N)."},
                          {"q": "How many controlled phases for 5 qubits?", "a": "10 (n(n−1)/2)."}],
        "checkpoint": "PASS if your QFT equals numpy's DFT, the inverse gives identity, and your period finder passes test_build_task.",
        "sources": src("qftgate", "qft_class", "cirq_qft", "cirq_textbook", "statevector"),
        "next": "L200 #10 Parameterized circuits and sweeps: phases become circuit parameters you sweep and fit. (Quantum phase estimation built from this QFT: not built - see KNOWN-GAPS 'L400 candidates'.)",
        "validation": pending("`python crosscheck_numpy.py`, `python try_it.py`, `python solution_period.py` (outputs in README); "
                              "`python -m unittest` -> 12 tests: 6 OK, 6 SDK tests skipped.",
                              "qft_lab.py, test_qft.py and the Qiskit variants in test_try_it.py/test_build_task.py"),
        "projectFiles": [("qft_lab.py", "main lab: QFT from gates, DFT/QFTGate comparison, inverse"),
                         ("crosscheck_numpy.py", "numpy QFT vs np.fft"), ("solution_period.py", "buildTask reference solution"),
                         ("test_build_task.py", "buildTask check"), ("test_qft.py", "unittest"), ("README.md", "run commands and observed output")],
        "summary": "The QFT is the DFT on amplitudes, with numpy's ifft sign and 1/√N scaling. It is built from H, halving controlled phases and a bit reversal; its inverse reverses the gates and negates the angles.",
    },
    {
        "dir": "10-parameterized-circuits", "file": "param_lab.py",
        "id": "parameterized-circuits", "number": 10, "title": "Parameterized circuits and sweeps",
        "phase": "Workflows", "category": "parameters",
        "description": "Use Parameter objects, bind values, sweep an angle in one primitive call, and fit expectation values.",
        "outcome": "You can write a parameterized template, sweep it with Estimator and Sampler, and fit the expectation-value curve.",
        "estimatedTime": "30-45 minutes",
        "overview": ["One template plus an array of values replaces many hand-built circuits; fitting the known curve beats reading single noisy points."],
        "prerequisites": ["Lesson 3 (shots)", "numpy least squares"],
        "glossary": [
            {"term": "Parameter", "meaning": "Compile-time symbol in a gate; must be bound before execution."},
            {"term": "PUB", "meaning": "Primitive unified bloc: (circuit, observables, parameter values[, precision])."},
            {"term": "expectation value ⟨Z⟩", "meaning": "P(0) − P(1) for one qubit."},
        ],
        "concepts": ["assign_parameters returns a bound copy.", "Parameter arrays broadcast against observable arrays.", "Fit a·cos θ + b·sin θ + c to sampled ⟨Z⟩."],
        "steps": [
            step("Run the numpy cross-check", "python crosscheck_numpy.py", "fit exact <Z> [1.0, 0.0, 0.0]; 400 shots [0.987, -0.004, -0.005].", "Run from the lab folder."),
            step("Bind a value", "python param_lab.py (first lines)", "free parameters: [Parameter(theta)]; after binding pi/3: 0 free; 1 free in the template.",
                 "TypeError on binding: bind with the Parameter object or its name."),
            step("Sweep with the Estimator", "Read 'exact <Z> at theta = 0, pi/2, pi'.", "[1.0, 0.0, -1.0]; fit <X> [0.0, 1.0, 0.0].",
                 "Shape error: parameter values must be shape (21, 1) for one parameter."),
            step("Sample and fit", "Read the last line.", "fit sampled <Z> about [1, 0, 0], within 0.05.", "Larger errors: check shots=400 and the (n0 − n1)/shots formula."),
            step("Try it", "python try_it.py", "rx: fit_X [0, 0, 0]; 25 shots worst error 0.069 vs 0.013 at 400.", "Compare with the tryIt predictions."),
            step("Build task: offset parameter", "Write my_offset.py (see buildTask), then run the check (mac / windows).",
                 "OK: phi recovered within 0.01 exactly and within 0.05 from 400 shots.", "Use atan2(-b, a) on unrounded fit coefficients."),
            step("Run the tests", "python -m unittest -v", "OK (SDK tests skip without qiskit).", "Read the failing assertion."),
        ],
        "codeWalkthrough": [
            {"title": "theta = Parameter('theta'); qc.ry(theta, 0)", "detail": "The template: one circuit object for every angle."},
            {"title": "pub = (qc, [[Z], [X]], thetas.reshape(-1, 1))", "detail": "Observables shape (2, 1) times 21 bindings gives evs shape (2, 21) in one call."},
            {"title": "bits.get_counts(i)", "detail": "Sampler results keep the sweep shape; index i is the i-th angle."},
            {"title": "np.linalg.lstsq(cos, sin, 1)", "detail": "Fits the known curve shape using all points, which averages shot noise."},
        ],
        "buildTask": {"task": "Use qc.ry(theta + phi, 0), bind only phi = 0.3, sweep theta, and recover phi from the fit.",
                      "hints": ["cos(θ+φ) = cos φ·cos θ − sin φ·sin θ, so a = cos φ, b = −sin φ.",
                                "assign_parameters({phi: 0.3}) leaves theta free (num_parameters 1).", "Do not round before atan2."],
                      "solution": "labs/L200/10-parameterized-circuits/solution_offset.py",
                      "check": "python -m unittest test_build_task -v (numpy part local; Qiskit variant in CI)"},
        "expectedResults": ["Exact fit [1, 0, 0] for <Z>, [0, 1, 0] for <X>", "Sampled fit within 0.05", "phi = 0.3 recovered"],
        "testCases": [{"action": "exact_expectations(ansatz())", "expected": "matches numpy cos θ / sin θ"},
                      {"action": "sampled_z(qc) twice", "expected": "identical (seeded)"}],
        "tryIt": [
            {"task": "Replace qc.ry with qc.rx.", "predict": "What happens to <Z> and <X>?",
             "expected": "<Z> fit stays [1.0, 0.0, 0.0]; <X> fit becomes [0.0, 0.0, 0.0] (RX rotates toward Y).", "validatedBy": "local: try_it.py numpy (observed); Qiskit variant pending-ci"},
            {"task": "Use shots=25 instead of 400.", "predict": "How far off is the fit?",
             "expected": "numpy seed 7: worst coefficient error 0.069 at 25 shots vs 0.013 at 400.", "validatedBy": "local: try_it.py numpy RNG (observed); Qiskit RNG values pending-ci (asserted by tolerance)"},
        ],
        "troubleshooting": [{"symptom": "ValueError about parameter shape", "action": "Reshape values to (number_of_points, number_of_parameters)."},
                            {"symptom": "Values bound to the wrong parameter", "action": "List binding follows qc.parameters (sorted by name); bind by dict."}],
        "equivalents": ["Same idea in Cirq: sympy.Symbol('theta') in cirq.ry, swept with cirq.Linspace and Simulator.run_sweep.",
                        "Qiskit Aer (optional, reduced maintenance): qiskit_aer.primitives.EstimatorV2/SamplerV2 accept the same PUBs."],
        "inRealSystems": ["Variational algorithms (VQE, QAOA) and quantum ML are parameter sweeps inside an optimiser loop.",
                          "Calibration (Rabi-style scans) sweeps an angle and fits the curve."],
        "useWhen": "Use parameters whenever only angles change between runs; build separate circuits when the structure changes.",
        "checkYourself": [{"q": "Does assign_parameters change the template?", "a": "No; it returns a bound copy unless inplace=True."},
                          {"q": "Why fit instead of reading the θ = π/2 point?", "a": "The fit uses all 21 points and averages the shot noise."}],
        "checkpoint": "PASS if the sampled fit is within 0.05 of [1, 0, 0] and you recover phi = 0.3 in test_build_task.",
        "sources": src("parameter", "qc_api", "sv_estimator", "sv_sampler", "cirq_params"),
        "next": "L300 #15 A hybrid variational loop (VQE) under shot noise: fitted expectation values feed an optimiser, and shot noise decides which optimiser works.",
        "validation": pending("`python crosscheck_numpy.py`, `python try_it.py`, `python solution_offset.py` (outputs in README); "
                              "`python -m unittest` -> 12 tests: 6 OK, 6 SDK tests skipped.",
                              "param_lab.py, test_param.py and the Qiskit variants in test_try_it.py/test_build_task.py"),
        "projectFiles": [("param_lab.py", "main lab: Parameter, binding, Estimator/Sampler sweeps, fit"),
                         ("crosscheck_numpy.py", "numpy sweep + seeded shots + fit"), ("solution_offset.py", "buildTask reference solution"),
                         ("test_build_task.py", "buildTask check"), ("test_param.py", "unittest"), ("README.md", "run commands and observed output")],
        "summary": "A parameterized circuit is a template with symbolic angles. Bind values for a concrete copy, or sweep many values in one primitive call and fit the expected curve.",
    },
    {
        "dir": "11-transpile-to-device", "file": "transpile_lab.py",
        "id": "transpile-to-device", "number": 11, "title": "Transpiling to a device layout",
        "phase": "Workflows", "category": "compilation",
        "description": "Transpile for line and heavy-hex coupling maps with GenericBackendV2; compare depth and two-qubit counts across optimization levels.",
        "outcome": "You can target a fake device, measure what transpiling cost, and rewrite a circuit to suit the coupling map.",
        "estimatedTime": "30-45 minutes",
        "overview": ["Devices accept only basis gates on linked qubit pairs; the transpiler makes your circuit fit, at a cost you should measure."],
        "prerequisites": ["Lesson 1 (transpile)", "Lesson 4 (CX)"],
        "glossary": [
            {"term": "basis gates", "meaning": "The native gate set; GenericBackendV2 defaults to id, rz, sx, x, cx."},
            {"term": "coupling map", "meaning": "Graph of qubit pairs that support two-qubit gates."},
            {"term": "routing", "meaning": "Inserting SWAPs so every two-qubit gate is on a linked pair."},
        ],
        "concepts": ["SWAP = 3 CX.", "Optimization levels 0-3 trade compile effort for fewer gates.", "Check behaviour after transpiling, not text."],
        "steps": [
            step("Run the numpy cross-check", "python crosscheck_numpy.py", "Basis rewrites True; star pairs off the line: (0,2), (0,3), (0,4); heavy-hex d=3 has 19 qubits.", "Run from the lab folder."),
            step("Run the lab", "python transpile_lab.py", "before: 2q 4; basis ['cx', 'delay', 'id', 'measure', 'reset', 'rz', 'sx', 'x'].",
                 "ImportError GenericBackendV2: it is in qiskit.providers.fake_provider (no extra package)."),
            step("Compare maps and levels", "Read the level 0-3 lines per backend.", "all-to-all keeps 4 CX; line level 0 has more than 4 (SWAPs); higher levels usually fewer.",
                 "Numbers change between runs: keep seed_transpiler=7."),
            step("Check behaviour", "Read 'GHZ outcomes only'.", "True for every backend and level.", "False means measurements were dropped or remapped by hand."),
            step("Try it", "python try_it.py", "ring 2 / line 3 pairs need routing; H = rz·sx·rz with phase −0.125 turn.", "Compare with the tryIt predictions."),
            step("Build task: fit the circuit to the map", "Write my_chain.py (see buildTask), then run the check (mac / windows).",
                 "OK: same state as the star, 0 pairs off the line; CI: 4 two-qubit gates at every level.", "Use cx(i, i+1)."),
            step("Run the tests", "python -m unittest -v", "OK (SDK tests skip without qiskit).", "Read the failing assertion."),
        ],
        "codeWalkthrough": [
            {"title": "GenericBackendV2(n, coupling_map=CouplingMap.from_line(n), seed=42)", "detail": "An offline fake device with a chosen topology and default basis gates."},
            {"title": "generate_preset_pass_manager(optimization_level=level, backend=backend, seed_transpiler=seed)", "detail": "The same pipeline transpile() uses; the seed makes layout and routing repeatable."},
            {"title": "qc.depth(lambda inst: inst.operation.num_qubits == 2)", "detail": "Two-qubit depth, the number that best predicts noise."},
            {"title": "same_outcomes(tqc)", "detail": "Runs the transpiled circuit and checks the counts are still only 00000 or 11111."},
        ],
        "buildTask": {"task": "Add ghz_chain(n) (CX(i, i+1)) and show it makes the same state as the star but needs no routing on a line.",
                      "hints": ["GHZ needs n−1 CX, and any spanning tree works.", "Compare with crosscheck_numpy.ghz_probabilities and non_adjacent.",
                                "compare_on_line() transpiles both at levels 0-3."],
                      "solution": "labs/L200/11-transpile-to-device/solution_chain.py",
                      "check": "python -m unittest test_build_task -v (numpy part local; transpile counts in CI)"},
        "expectedResults": ["Every transpiled CX is on a coupling-map edge", "Line costs extra CX at level 0", "Behaviour unchanged"],
        "testCases": [{"action": "transpile_for(ghz_star(), backend, level) for 3 backends x 4 levels", "expected": "only basis gates; every 2q gate on an edge"},
                      {"action": "same_outcomes(...) at level 3", "expected": "True"}],
        "tryIt": [
            {"task": "Add a 'ring' backend (CouplingMap.from_ring(5)) next to 'line'.", "predict": "How many star CX pairs need routing on each map?",
             "expected": "all-to-all 0, ring 2, line 3 (local edge-list check); level-0 two-qubit count ring <= line (pending-ci).", "validatedBy": "local: try_it.py edge lists (observed); transpile counts pending-ci"},
            {"task": "Transpile a lone H for the default basis.", "predict": "Which gates replace it?",
             "expected": "rz, sx, rz; equal to H up to a global phase of −0.125 turn.", "validatedBy": "local: try_it.py numpy (observed); Qiskit ops/equiv pending-ci"},
        ],
        "troubleshooting": [{"symptom": "Counts differ between runs", "action": "Pass seed_transpiler; levels 1-3 use stochastic layout/routing."},
                            {"symptom": "Transpiled circuit has 19 qubits", "action": "Expected on heavy-hex: the output is on physical qubits; measured bits keep your order."}],
        "equivalents": ["Same idea in Cirq: cirq.RouteCQC(device_graph) inserts SWAPs; cirq.optimize_for_target_gateset translates to a gate set.",
                        "Hardware-calibrated fake backends live in qiskit-ibm-runtime (fake_provider); not needed here."],
        "inRealSystems": ["Every hardware run is transpiled; teams track two-qubit count and depth per release.",
                          "Heavy-hex limits each qubit to at most 3 neighbours, so the layout choice matters."],
        "useWhen": "Use level 0 to see raw routing cost and level 2-3 for real targets; rewrite the circuit for the topology when you know it.",
        "checkYourself": [{"q": "Why does the star need routing on a line but not the chain?", "a": "The star uses pairs (0,2), (0,3), (0,4) that are not edges."},
                          {"q": "What does seed_transpiler fix?", "a": "The stochastic layout and routing choices, so counts repeat."}],
        "checkpoint": "PASS if every transpiled two-qubit gate is on an edge, the GHZ behaviour survives, and your chain passes test_build_task.",
        "sources": src("generic", "coupling", "preset_pm", "set_opt", "cirq_routing", "qc_api"),
        "next": "L300 #12 Noise models: how Bell and GHZ results degrade: what the transpiled circuit's extra CX gates cost once each gate has an error rate.",
        "validation": pending("`python crosscheck_numpy.py`, `python try_it.py`, `python solution_chain.py` (outputs in README); "
                              "`python -m unittest` -> 12 tests: 6 OK, 6 SDK tests skipped.",
                              "transpile_lab.py, test_transpile.py and the Qiskit variants in test_try_it.py/test_build_task.py"),
        "projectFiles": [("transpile_lab.py", "main lab: fake backends, levels 0-3, stats, behaviour check"),
                         ("crosscheck_numpy.py", "basis rewrites, SWAP = 3 CX, coupling-map adjacency"),
                         ("solution_chain.py", "buildTask reference solution"), ("test_build_task.py", "buildTask check"),
                         ("test_transpile.py", "unittest"), ("README.md", "run commands and observed output")],
        "summary": "Transpiling maps a circuit onto a device's basis gates and coupling map: layout, routing (SWAP = 3 CX), translation and optimization. Measure two-qubit count and depth, and check that behaviour is unchanged.",
    },
]


# Learning tools (kb/UPDATE-TOOLS-REVIEW-SPEC.md A2). Facts and install commands copied from kb/shared/learning-tools.json.
MANUAL = "Pending a manual run (tool not runnable in the authoring sandbox). "
LEARNING_TOOLS = {
    "08-grover-search": [
        {"name": "Microsoft Quantum Development Kit (qdk + VS Code extension)", "role": "SEE",
         "exercise": "Export the 3-qubit search for '101' with qasm3.dumps(grover_circuit(['101'], 2).decompose()) to grover.qasm, open it in VS Code with the QDK extension and step through the Grover iteration in the debugger.",
         "expected": MANUAL + "The marked state's amplitude grows with each iteration: P('101') should match the lab's numpy values 0.125 (k=0), 0.7812 (k=1), 0.9453 (k=2). If the extension rejects a gate, call .decompose() once more before exporting.",
         "mac": "pip install qdk ; VS Code extension 'Microsoft Quantum Development Kit (QDK)' (or vscode.dev/quantum/playground)",
         "windows": "pip install qdk ; same VS Code extension", "licence": "MIT (OSI: yes)", "url": "https://github.com/microsoft/qdk"},
    ],
    "11-transpile-to-device": [
        {"name": "Qiskit visualization (qiskit.visualization)", "role": "SEE",
         "exercise": "plot_coupling_map / plot_circuit_layout for the 'line' backend: draw the GHZ star after transpile at optimization_level=0 and at 3 (seed_transpiler=7), then the same for your ghz_chain.",
         "expected": MANUAL + "A 5-qubit chain; the star's pairs (0,2), (0,3), (0,4) are off the line (lab cross-check), so its layout needs SWAPs, while the chain maps onto neighbouring qubits with 4 two-qubit gates. Counts should match the lab's printed level lines.",
         "mac": "pip install 'qiskit[visualization]'", "windows": "pip install \"qiskit[visualization]\"",
         "licence": "Apache-2.0 (OSI: yes)", "url": "https://quantum.cloud.ibm.com/docs/en/api/qiskit/visualization"},
    ],
}

# Honest validation (review F02/F07): everything in a lesson that has not been run yet.
PENDING_CI = {
    "07-bernstein-vazirani": ["bv_lab.py", "test_bv.py (SDK tests)", "try_it.py + test_try_it.py (Qiskit variant)", "solution_bias.py + test_build_task.py (Qiskit variant)"],
    "08-grover-search": ["grover_lab.py", "test_grover.py (SDK tests)", "try_it.py + test_try_it.py (Qiskit variant)", "solution_search.py + test_build_task.py (Qiskit variant)",
                         "test_agent_assist.py (Qiskit agreement)", "agent_assist.py with a real local model"],
    "09-qft-building-block": ["qft_lab.py", "test_qft.py (SDK tests)", "try_it.py + test_try_it.py (Qiskit variant)", "solution_period.py + test_build_task.py (Qiskit variant)"],
    "10-parameterized-circuits": ["param_lab.py", "test_param.py (SDK tests)", "try_it.py + test_try_it.py (Qiskit variant)", "solution_offset.py + test_build_task.py (Qiskit variant)"],
    "11-transpile-to-device": ["transpile_lab.py", "test_transpile.py (SDK tests)", "try_it.py + test_try_it.py (Qiskit variant)", "solution_chain.py + test_build_task.py (transpile counts)"],
}


def os_variants(st):
    """The build-task check sets an env var, the only command that differs between zsh and PowerShell."""
    m = re.search(r"Write (my_\w+)\.py", st["detail"])
    if not m:
        return st
    cmd = "python -m unittest test_build_task -v"
    return {**st, "mac": f"BUILD_TASK_MODULE={m.group(1)} {cmd}",
            "windows": f'$env:BUILD_TASK_MODULE = "{m.group(1)}"; {cmd}'}


def build():
    out = []
    for lesson in LESSONS:
        d = dict(lesson)
        lab_dir, main_file = d.pop("dir"), d.pop("file")
        with open(os.path.join(ROOT, LABS, lab_dir, main_file), encoding="utf-8") as f:
            code = f.read()
        assert os.path.exists(os.path.join(ROOT, d["buildTask"]["solution"])), d["buildTask"]["solution"]
        obj = {k: d[k] for k in ("id", "number")}
        obj["level"] = "L200"
        obj.update({k: d[k] for k in ("title", "phase", "category", "description", "outcome")})
        obj["environment"] = ENV
        obj.update({k: d[k] for k in ("estimatedTime", "overview", "prerequisites", "glossary", "concepts")})
        obj["steps"] = [os_variants(st) for st in d["steps"]]
        obj["code"] = code
        obj["codeLanguage"] = "python"
        obj["codeWalkthrough"] = d["codeWalkthrough"]
        obj["projectFiles"] = [{"path": posixpath.normpath(f"{LABS}/{lab_dir}/{p}"), "purpose": why} for p, why in d["projectFiles"]]
        obj["projectFiles"] += [
            {"path": f"{LABS}/{lab_dir}/try_it.py", "purpose": "runs the two tryIt changes"},
            {"path": f"{LABS}/{lab_dir}/test_try_it.py", "purpose": "tryIt tests"},
            {"path": "labs/_shared/qsim/statevector.py", "purpose": "shared numpy statevector simulator for cross-checks"},
        ]
        obj["buildTask"] = d["buildTask"]
        obj["expectedResults"], obj["testCases"] = d["expectedResults"], d["testCases"]
        obj["tryIt"] = [{k: v for k, v in t.items() if k != "validatedBy"} for t in d["tryIt"]]
        if "agentAssist" in d:
            obj["agentAssist"] = {k: v for k, v in d["agentAssist"].items() if k != "validatedBy"}
        obj["troubleshooting"], obj["equivalents"] = d["troubleshooting"], d["equivalents"]
        obj["inRealSystems"], obj["useWhen"] = d["inRealSystems"], d["useWhen"]
        obj["simulatorVsReal"] = SIM
        if "caution" in d:
            obj["caution"] = d["caution"]
        obj["checkpoint"], obj["checkYourself"] = d["checkpoint"], d["checkYourself"]
        if lab_dir in LEARNING_TOOLS:
            obj["learningTools"] = LEARNING_TOOLS[lab_dir]
        obj["platforms"] = dict(PLATFORMS)
        obj["sources"], obj["next"] = d["sources"], d["next"]
        tried = " ".join(f"tryIt {i}: {t['validatedBy']}." for i, t in enumerate(d["tryIt"], 1))
        if "agentAssist" in d:
            tried += f" agentAssist: {d['agentAssist']['validatedBy']}."
        tried += f" buildTask: {d['buildTask']['solution'].rsplit('/', 1)[1]} numpy test passed locally; Qiskit variant pending-ci."
        pending_files = PENDING_CI[lab_dir] + [f"learningTools: {t['name']} exercise (manual run)" for t in LEARNING_TOOLS.get(lab_dir, [])]
        obj["validation"] = {"status": d["validation"]["status"], "how": f"{d['validation']['how']} {tried} Platforms: {PLATFORM_NOTE}",
                             "pendingCi": pending_files}
        note = f"content/concepts/L200/{lab_dir}.md"
        assert os.path.exists(os.path.join(ROOT, note)), note
        obj["conceptNote"], obj["conceptSummary"] = note, d["summary"]
        out.append(obj)
    path = os.path.join(ROOT, "content", "L200.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path, out


if __name__ == "__main__":
    p, lessons = build()
    print(f"wrote {p}: {len(lessons)} lessons")
