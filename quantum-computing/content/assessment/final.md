# Final examination — Quantum computing (applied + theory)

**Covers:** the whole course — L100 #1-#6, L200 #7-#11, L300 #12-#16, L400 #17-#22 and L500 #23-#27.
**Time:** 180 minutes. **Total:** 100 marks. Closed book; two A4 sheets of your own notes; non-programmable calculator.
Every number in the model answers is recomputed by `research/l500_checks.py` (section "exams").

---

## Q1 — Derivation (15 marks)
(a) Show that the Grover iterate is a product of two reflections in the plane spanned by the marked and unmarked superpositions, and derive P_k = sin^2((2k+1)θ) with sin θ = sqrt(M/N). (8)
(b) For N = 1024 give the optimal k and P_k when M = 1, and the optimal k when M = 4. (4)
(c) State what the BBBV lower bound implies for NP-complete problems. (3)

**Model answer.** (a) T25.1. (b) M = 1: k = floor(π/(4θ)) = 25, P_25 = 0.9995. M = 4: k = 12. (c) Generic (unstructured) search cannot beat Ω(√N) queries, so Grover gives at most a quadratic speed-up; it does not put NP-complete problems in polynomial time.
**Marking.** (a) 3 reflections, 3 rotation angle, 2 formula. (b) 2 + 2. (c) 3.

## Q2 — Calculation (10 marks)
Phase estimation with t = 3 counting qubits on an eigenphase φ = 1/3. (a) Give the most likely outcome and its probability. (6) (b) State and justify the general lower bound for the nearest outcome. (4)

**Model answer.** (a) m = 3 (estimate 0.375) with P = 0.6878. (b) P ≥ 4/π^2 ≈ 0.405: with δ = φ - m/T, |a_m| = |sin(πTδ)|/(T|sin(πδ)|) ≥ 2/π for |δ| ≤ 1/(2T) (T25.3).
**Marking.** (a) 3 method, 3 values. (b) 2 bound, 2 justification.

## Q3 — Short explanation (10 marks)
Walk through Shor's classical reduction for N = 21 with a = 2 and explain why a laboratory demonstration of "factoring 21" says little about breaking RSA-2048 (use L400 #19).

**Model answer.** Order r = 6 (2, 4, 8, 16, 11, 1); 2^3 = 8 ≢ -1 (mod 21); gcd(7, 21) = 7 and gcd(9, 21) = 3. Small demos typically compile the modular exponentiation using knowledge of the answer and run without error correction; RSA-2048 needs thousands of logical qubits (6190 in the L400 #19 model) and billions of Toffoli gates on error-corrected hardware; under its stated assumptions L400 #19 estimates about 9 million physical qubits and 16 hours.
**Marking.** 5 for the worked reduction, 5 for the scaling argument.

## Q4 — Prediction (15 marks)
A Bell circuit is run on a device whose only error is an independent symmetric readout flip with probability ε = 0.02 on each qubit.
(a) Predict P('01' or '10'). (5) (b) Will 100× more shots remove these outcomes? (4) (c) Which L300 technique corrects this, and what does it need? (6)

**Model answer.** (a) Exactly one flip: 2ε(1 - ε) = 0.0392. (b) No: shots reduce statistical error, not bias. (c) Readout-error mitigation (L300 #13): calibrate the assignment matrix from basis-state runs and invert it, with constrained least squares when shot noise makes the inverse produce negative probabilities.
**Marking.** (a) 3 method, 2 value. (b) 4. (c) 3 technique, 3 requirements.

## Q5 — Design critique (15 marks)
An ADR in a capstone repository reads: *"Decision: route all MaxCut requests to QAOA because quantum is faster. Consequences: faster results."* Critique it as a reviewer and rewrite the decision.

**Model answer.** Missing context, options and evidence; "quantum is faster" is unsupported and violates ACM 1.3/2.5 and IEEE 7.8 item 5; the L400 #18 harness, with equal budgets and seeds, found classical solvers winning at n = 8 and n = 16 and QAOA winning once in six 12-node graphs, and its ADR keeps QAOA as a research option; no feasibility gate (L400 #19) or fallback. Rewrite: *"Decision: run the fair benchmark per request class; route to QAOA only when it beats the best classical solver on the same budget and seeds (ties go classical). Consequences: classical by default today; the benchmark and fitness test keep the decision honest."*
**Marking.** 8 for identified flaws (context/evidence/ethics/feasibility), 7 for a defensible rewrite with a fitness function.

## Q6 — Derivation (10 marks)
Compute Tr_A |Φ+><Φ+| and use the cyclicity of the partial trace to show that no operation on A alone changes ρ_B.

**Model answer.** Only terms with equal A labels survive: ρ_B = ½(|0><0| + |1><1|) = I/2 (purity 0.5). For a unitary or unread measurement on A, Tr_A[(U ⊗ I)ρ(U† ⊗ I)] = Tr_A[ρ(U†U ⊗ I)] = ρ_B (T24.4).
**Marking.** 5 + 5.

## Q7 — Ethics (15 marks)
A records system must keep data confidential for X = 25 years; migration will take Y = 5 years. (a) Using Mosca's inequality, for which CRQC dates Z is the data already at risk? (5) (b) Which NIST IR 8547 and NCSC dates constrain the plan? (4) (c) Argue, citing the ACM Code, why this is a professional duty and not just a compliance item. (6)

**Model answer.** (a) At risk whenever Z < X + Y = 30 years, i.e. for any CRQC in the next 30 years. (b) NIST: quantum-vulnerable public-key algorithms deprecated after 2030, disallowed after 2035; NCSC: discovery and plan by 2028, priority migrations by 2031, complete by 2035. (c) HNDL harms data subjects who cannot protect themselves (ACM 1.2 avoid harm; 3.7 special care for infrastructure; 2.5 thorough risk evaluation); the professional must report and act on foreseeable risk.
**Marking.** (a) 5. (b) 4. (c) 6 for principle-based argument.

## Q8 — Short explanation (10 marks)
(a) How does Preskill (2018) define a quantum speed-up, and what happened to the quantum recommendation-system speed-up he discusses? (5)
(b) Google's 2019 claim compared 200 s with 10,000 years; Pan, Chen and Zhang (2022) needed about 15 hours on 512 GPUs. By what factor did the classical estimate fall? (5)

**Model answer.** (a) Against the best available classical hardware running the best classical algorithm for the same task; Tang's quantum-inspired classical algorithm matched the runtime, so the exponential speed-up disappeared (note added to the paper). (b) 10,000 × 365.25 × 24 / 15 = 5,844,000: about 5.8 million.
**Marking.** (a) 3 + 2. (b) 3 method, 2 value.
