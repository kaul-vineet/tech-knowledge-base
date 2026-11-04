# Quantum computing — concepts primer

Read this before the labs. Numbers come from `research/concepts_worked_examples.py`.

## What it is for in practice
Today's quantum computers are small and noisy, so most practical work is **writing, simulating and testing circuits**. Open-source examples: chemistry (OpenFermion), error-correction research (Stim), differentiable circuits for machine learning (PennyLane), algorithm prototyping (Qiskit, Cirq — the L100 labs) and resource estimation (Microsoft QDK).

## One mental model
**A quantum program is a classical program that builds a circuit, sends it to an executor, and gets back bitstring counts.** The quantum state is hidden; you only see samples.

```
 your Python ──build──▶ circuit ──export──▶ OpenQASM text ──▶ other tools
                          │ transpile
                          ▼
         executor: simulator (StatevectorSampler, cirq.Simulator) or hardware
                          │ state = 2^n amplitudes (hidden)
                          ▼
         measure × shots ──▶ counts {'00': 503, '11': 497}
```

Two facts carry most of L100: the probability of each outcome is |amplitude|² (the Born rule), and simulator memory doubles with every qubit (16 bytes per amplitude: 30 qubits = 16 GiB).

## Concept map
| level | core concepts |
|---|---|
| **L100 — run it** | toolchain and simulators · X/H gates · shots and seeds · Bell pair · OpenQASM · bit order across frameworks |
| **L200 — build it** | BV oracles · Grover iterations · QFT vs DFT · parameter sweeps · transpiling to a coupling map |
| **L300 — harden it** | noise models · readout mitigation + ZNE · QAOA vs brute force · VQE under shot noise · classifier vs baseline |
| **L400 — make it scale** | error correction with Stim · resource estimation · fault-tolerant blocks · custom transpiler passes |

**Local agents per level** (a local model proposes, code decides):
- **L100:** drafts OpenQASM from a description; the lab parser and numpy accept or reject it (lab 5).
- **L200:** proposes Grover marked states and iterations (lab 8); code checks them with numpy.
- **L300:** reads a VQE convergence log and proposes optimizer settings (lab 15); code checks the claims and runs it.
- **L400:** drafts Stim circuits or resource-estimation inputs; Stim's sampler/decoder and the estimator are authoritative.

L400 (including its agent line) is a **proposed** progression (see KNOWN-GAPS).

## Glossary
| term | meaning |
|---|---|
| qubit | Quantum bit; measuring it gives 0 or 1 |
| amplitude | Complex number per basis state; probability = \|amplitude\|² |
| statevector | All 2ⁿ amplitudes of n qubits |
| gate | Reversible operation on qubits: X, H, CNOT |
| shot / counts | One run plus measurement / bitstring → number of shots |
| seed | Fixed start for a simulator's random number generator |
| entanglement | Joint state that cannot be split into per-qubit states |
| transpile | Rewrite a circuit for a target's gates and connectivity |
| OpenQASM | Open, vendor-neutral text language for circuits |
| bit order | Which qubit is written first; Qiskit puts qubit 0 on the right |

## Common misconceptions
1. **"A quantum computer tries all answers in parallel."** Measuring gives one random outcome. Algorithms arrange **interference** so wrong answers cancel, which only works for problems with special structure.
2. **"Entanglement sends messages instantly."** Measuring one qubit of a pair does not change the other's own probabilities; the correlation appears only when both results are compared.
3. **"Simulator results are what hardware will give."** Simulators default to noise-free runs; hardware shows outcomes the simulator calls impossible.

## Sources
- OpenFermion — https://github.com/quantumlib/OpenFermion
- Stim — https://github.com/quantumlib/Stim
- PennyLane circuits — https://docs.pennylane.ai/en/stable/introduction/circuits.html
- Microsoft QDK — https://github.com/microsoft/qdk
- IBM Quantum Learning, *Multiple systems* (no faster-than-light signalling) — https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/multiple-systems/quantum-information
- AerSimulator API (16 bytes per amplitude) — https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.AerSimulator.html
- S. Aaronson, "Shor, I'll do it" (interference, not parallel trial) — https://scottaaronson.blog/?p=208
