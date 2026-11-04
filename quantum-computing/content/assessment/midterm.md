# Midterm examination — Quantum computing (applied + theory)

**Covers:** weeks 1-7 — L100 #1-#6, L200 #7-#11, L500 #23 (linear algebra for qubits) and #24 (quantum information basics).
**Time:** 120 minutes. **Total:** 100 marks. Closed book; one A4 sheet of your own notes allowed; a non-programmable calculator is allowed.
**Conventions:** textbook order |ab> = |a> ⊗ |b> unless a question says "qsim/Qiskit order" (qubit 0 rightmost).
Every number in the model answers is recomputed by `research/l500_checks.py` (section "exams").

---

## Q1 — Proof (15 marks)
(a) Prove that a unitary U preserves inner products, and deduce that it preserves norms. (6)
(b) Explain why this guarantees that the counts of a noiseless circuit always add up to the number of shots. (4)
(c) Give a 2x2 invertible matrix that is *not* unitary and a state whose "probabilities" it would push above 1. (5)

**Model answer.** (a) <Uφ|Uψ> = <φ|U†U|ψ> = <φ|ψ>; set φ = ψ to get ||Uψ|| = ||ψ|| (T23.1). (b) After the circuit, the Born probabilities |<k|Uψ>|^2 sum to ||Uψ||^2 = 1 (completeness of the measurement basis), so the multinomial over outcomes has total count = shots. (c) M = [[1, 1], [0, 1]]: M|1> = (1, 1), norm 1.4142, "probabilities" summing to 2.0.
**Marking.** (a) 2 for the bra of Uψ, 2 for using U†U = I, 2 for the norm corollary. (b) 2 for completeness, 2 for linking to counts. (c) 3 for a correct matrix, 2 for the state and number.

## Q2 — Calculation and prediction (15 marks)
Alice and Bob share |Φ+>. Alice measures at angle a = 0 and Bob at b = π/8 (basis cos θ|0> + sin θ|1>, -sin θ|0> + cos θ|1>), for 2000 shots.
(a) Derive P(same). (6) (b) Predict the expected number of agreeing shots and a 95% range using the normal approximation. (6) (c) A run gives 1640 agreements. What do you conclude? (3)

**Model answer.** (a) Amplitude for 00 is (cos a cos b + sin a sin b)/√2 = cos(a - b)/√2; with 11 likewise, P(same) = cos^2(π/8) = 0.8536 (T23.4). (b) Expected 2000 × 0.8536 ≈ 1707; standard deviation sqrt(2000 p(1 - p)), so the 95% half-width is 1.96 × that ≈ 31, range about 1676-1738. (c) 1640 is outside the range: suspect a basis/angle error (e.g. RY(+2b) instead of RY(-2b) still gives cos^2, but measuring Bob at 2b gives cos^2(π/4) = 0.5) or noise; re-check the rotation convention before blaming hardware.
**Marking.** (a) 4 derivation, 2 value. (b) 2 mean, 3 interval, 1 interpretation. (c) 3 for a reasoned diagnosis.

## Q3 — Short explanation (10 marks)
The same Bell-like circuit prints '01' in one framework and '10' in another (L100 #6). Explain using the tensor-product convention, and state how you would make a test framework-independent.

**Model answer.** Qiskit/qsim index qubit 0 as the least-significant (rightmost) bit; Cirq and textbooks often print qubit 0 first. The state is identical; only the string order differs (T23.2). Make tests compare distributions after mapping bitstrings to named qubits, or compare probability vectors in one declared ordering.
**Marking.** 5 for the ordering explanation, 3 for "same state", 2 for a concrete test design.

## Q4 — Prediction (15 marks)
Grover search on N = 8 items with one marked item.
(a) Without running code, predict P(success) after k = 1, 2, 3 iterations using P_k = sin^2((2k+1)θ). (9)
(b) A teammate says "three iterations must be better than two". Respond. (6)

**Model answer.** sin θ = 1/√8. P_1 = 0.78125, P_2 = 0.9453, P_3 = 0.3301 (T25.1; L200 #8 shows the first two, rounded to 0.7812 and 0.9453). The Grover iterate is a rotation by 2θ, so it overshoots after the optimum floor(π/(4θ)) = 2; more iterations make it worse until the rotation comes round again.
**Marking.** 3 per probability (method 1, value 2); 6 for the rotation argument.

## Q5 — Derivation (15 marks)
Derive the teleportation identity |ψ>|Φ+> = ½ Σ_{x,z} |Bell_xz> ⊗ X^x Z^z|ψ> (up to signs) and use it to show (a) each of Alice's outcomes has probability 1/4 for every |ψ>, and (b) Bob learns nothing before the classical bits arrive.

**Model answer.** See T24.2: expand with |ψ> = α|0> + β|1>, rewrite Alice's pair in the Bell basis, collect Bob's states |ψ>, Z|ψ>, X|ψ>, XZ|ψ>. Each branch is ½ × unit vector ⇒ probability ¼ independent of α, β. Bob's average state is ¼ Σ X^xZ^z|ψ><ψ|Z^zX^x = I/2 (T24.4), so no information is transferred until the bits arrive.
**Marking.** 8 for the expansion (4 for correct Bell substitution, 4 for collecting terms), 3 for (a), 4 for (b).

## Q6 — Design critique (15 marks)
A pull request adds this test to a lab: `assert counts == {'00': 500, '11': 500}` for a 1000-shot Bell circuit with a fixed simulator seed. Critique the test and propose a better one. Address simulator changes and real hardware.

**Model answer.** The exact split is a property of one RNG stream, not of the circuit: a library upgrade or another simulator breaks it, and on hardware '01'/'10' appear due to noise (L300 #12). Better: (1) assert only '00' and '11' appear on an ideal simulator; (2) assert the '00' fraction is within a statistical tolerance (e.g. 4 standard errors, sqrt(0.25/1000) ≈ 0.016 each) of 0.5; (3) on noisy backends, compare against a noise-model prediction with a tolerance, not against ideal outcomes.
**Marking.** 6 for identifying the two failure modes, 6 for a statistically sound replacement, 3 for the hardware extension.

## Q7 — Proof and evaluation (15 marks)
(a) Prove that Deutsch-Jozsa outputs 0^n with probability 0 for a balanced f. (8)
(b) Evaluate the claim "Deutsch-Jozsa shows an exponential quantum speed-up". (7)

**Model answer.** (a) The amplitude of |0^n> after H^n·O_f·H^n is (1/2^n)Σ_x(-1)^{f(x)} = 0 when half the values are 1 (T24.3). (b) True only against deterministic exact algorithms (2^{n-1}+1 queries). A randomised classical algorithm with k queries errs with probability at most 2^{1-k}, so with 10 queries the error is below 2^-9: the separation largely disappears in the bounded-error model that matters in practice; DJ is a teaching example.
**Marking.** (a) 5 derivation, 3 conclusion. (b) 4 for the deterministic/randomised distinction, 3 for a judgement.
