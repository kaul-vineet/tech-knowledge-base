# Learning tools — quantum computing

Open-source tools that help you **see** a concept or **check** your lab result. Facts and install commands come from the shared catalogue (`../../shared/LEARNING-TOOLS-CATALOG.md`, checked 2026-10-28). Each lesson's `learningTools` field holds the exercise; none has been run yet (manual run pending).

| Tool | Role | Licence (OSI) | Mac mini install | Windows install | Lessons it supports |
|---|---|---|---|---|---|
| Qiskit visualization (`qiskit.visualization`) | SEE | Apache-2.0 (yes) | `pip install 'qiskit[visualization]'` | `pip install "qiskit[visualization]"` | L100 #2 Bloch sphere, #3 histogram, #4 state city; L200 #11 coupling map; L300 #12 ideal vs noisy histogram + noisy state city, #14 QAOA samples; L400 #20 circuit layout / error map |
| Microsoft Quantum Development Kit (`qdk` + VS Code extension) | SEE / CHECK | MIT (yes) | `pip install qdk` + VS Code extension "Microsoft Quantum Development Kit (QDK)" (or vscode.dev/quantum/playground) | `pip install qdk` + same extension | L100 #5 circuit diagram and debugger for `bell.qasm`; #6 a third framework; L200 #8 step through Grover; L400 #19 resource estimator (`qdk.qre`) |
| OpenQASM 3 spec + `openqasm3` reference parser | CHECK | Apache-2.0 (yes) | `pip install "openqasm3[parser]"` | `pip install "openqasm3[parser]"` | L100 #5 parse the exported Bell file |
| qiskit-qasm3-import | CHECK | Apache-2.0 (yes) | `pip install qiskit-qasm3-import` (in `labs/L100/requirements.txt`) | same | L100 #5 (used by the lab's `qasm3.loads`), #6 Cirq → OpenQASM 3 → Qiskit |
| JupyterLab (+ JupyterLab Desktop) | CHECK / SEE | BSD-3-Clause (yes) | `pip install jupyterlab`, or Desktop arm64 installer | `pip install jupyterlab`, or Desktop x64 installer / `winget install jupyterlab` | L100 #3 counts vs shots; L300 #13 ZNE fits, #15 VQE logs; L400 #17 wall vs billed, #18 success vs budget, #19 qubits vs error rate, #21 Mosca timeline, #22 report |
| marimo | SEE / CHECK | Apache-2.0 (yes) | `pip install marimo` (`marimo tutorial intro`) | same | L300 #14 QAOA landscape, #16 gradient scan; L400 #17 queue/TTL sliders, #18 budget/seeds sliders, #22 budget/drift sliders |
| Mitiq 1.1.0 (library, no GUI) | CHECK | GPL-3.0 (yes) | `pip install mitiq` (Python ≥3.11,<3.13; brings its own Cirq; separate venv: `labs/L300/requirements-extras.txt`) | `pip install mitiq` (same Python range) | L300 #13 Linear/Richardson factories vs the lab's extrapolation (0.9687 / 0.9944); L400 #22 REM vs the capstone's constrained mitigation (6.8549) |

## How to use these tools
The tools complement the code labs; they don't replace them. Run the lab code first, then use a tool to see the concept or check your result. Each exercise names the lab value the tool must reproduce (e.g. ZNE intercepts 0.9687 / 0.9944, RSA-2048 d = 27). Mitiq and the QDK estimator are pending CI; their expected values are the READMEs', not observed. If values disagree, check bit order first (lesson 6). marimo notebooks are plain `.py` files (`marimo edit <file>.py`). L400 #19: the QDK resource estimator is the `qdk.qre` Python module (Learn docs install `qdk[qre]`); the VS Code extension's estimator is being deprecated.

Catalogue notes: the visualisers may call system programs on their input, so use them on trusted circuits only; QDK Python telemetry is on by default (`QDK_PYTHON_TELEMETRY=none`); the `openqasm3` parser API is not yet stable; Cirq's QASM import is experimental.

## Not recommended / changed
- **Quirk**: unmaintained (last release v2.3, 2019-09-11); `cirq.quirk_url_to_circuit` still imports Quirk URLs.
- **IBM Quantum Composer**: proprietary IBM web service that supports OpenQASM 2.0 only, so it can't read this course's OpenQASM 3 files.
- **`qsharp` PyPI package**: archived on 2026-08-24 as a compatibility shim. Use `qdk` instead.
- **Qiskit noise visualisation**: part of the Qiskit visualization entry, not a separate tool.
- **Mitiq factory plot helper**: not verified to exist; plot the scale/value pairs in JupyterLab instead.
