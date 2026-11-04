# Foundations I: linear algebra for qubits

Every lab in L100-L400 printed counts and probabilities. This note explains the mathematics that produced them, so that you can predict a result before you run it and recognise when a simulator (or a colleague) is wrong. All numbers below are printed by `labs/L500/23-linear-algebra-for-qubits/theorems.py`.

## Definitions

**States.** A qubit state is a unit vector |ψ> = α|0> + β|1> in C^2, with |α|^2 + |β|^2 = 1. The "ket" |ψ> is a column vector; the "bra" <ψ| is its conjugate transpose, a row vector. In numpy a ket is `np.array([alpha, beta])` and a bra-ket product is `np.vdot(phi, psi)`, which conjugates its *first* argument.

**Inner product and norm.** <φ|ψ> = Σ_k conj(φ_k) ψ_k. It measures overlap: 1 for identical unit vectors, 0 for orthogonal ones. The norm is ||ψ|| = sqrt(<ψ|ψ>).

**Unitaries.** A gate is a square matrix U with U†U = I. X, H, CX, RY(θ) and the controlled phases of the QFT are all unitary.

**Tensor products.** Two qubits live in C^2 ⊗ C^2 = C^4. The joint state of independent qubits |a> and |b> is the Kronecker product |a> ⊗ |b> (`np.kron(a, b)`). States that cannot be written this way are *entangled*.

**Born rule.** Measuring |ψ> in an orthonormal basis {|b_k>} gives outcome k with probability |<b_k|ψ>|^2.

## Key results (proved in the lesson)

1. **Unitaries preserve inner products (T23.1).** <Uφ|Uψ> = <φ|U†U|ψ> = <φ|ψ>. So norms are preserved, and probabilities still sum to 1 after any circuit. The converse also holds: a linear map that preserves every norm is unitary (polarisation identity). The check tests 1000 random unitaries in dimensions 2-16 and finds every deviation below 10^-12; it also shows that the invertible but non-unitary matrix [[1, 1], [0, 1]] turns |1> into a vector of norm 1.4142, whose "probabilities" would sum to 2.0.
2. **Tensor rules (T23.2).** (A ⊗ B)(C ⊗ D) = AC ⊗ BD and <a ⊗ b|c ⊗ d> = <a|c><b|d>. Consequence: if U and V are gates on separate qubits, U ⊗ V is a gate on both, and a product of normalised states is normalised.
3. **Born rule in any basis; global phase is invisible (T23.3).** Completeness, Σ_k |b_k><b_k| = I, makes the probabilities sum to 1. Multiplying a state by e^{iθ} changes no probability, ever. A *relative* phase can: |+> and |-> give identical 50/50 statistics in the Z basis, but H then measure gives {'0': 1.0} for |+> and {'1': 1.0} for |->.
4. **Bell statistics (T23.4).** |Φ+> = (|00> + |11>)/√2. If Alice measures in a basis rotated by angle a and Bob by b, the amplitude for "both 0" is cos(a - b)/√2, so P(same) = cos^2(a - b) and the correlation is E = cos 2(a - b).

## Intuition

Think of a unitary as a rigid rotation (with complex phases) of the state space. Rotations do not stretch vectors, so the total length, and therefore total probability, stays 1. Measurement is the only step that is not a rotation: it picks a basis direction with probability equal to the squared overlap.

The tensor product is "both at once, independently". Entanglement is exactly the failure of that picture: |Φ+> cannot be split into a left factor and a right factor. Arrange its amplitudes in a 2x2 matrix, [[1, 0], [0, 1]]/√2; a product state would give a rank-1 matrix, and this one has rank 2.

## Worked example: predicting a Bell experiment

Alice measures at a = 0 and Bob at b = π/8 (on hardware: apply RY(-2a) and RY(-2b), then measure Z).

- Amplitude for 00: <u_0 ⊗ u_{π/8}|Φ+> = (cos 0 cos π/8 + sin 0 sin π/8)/√2 = cos(π/8)/√2.
- P(00) = cos^2(π/8)/2, and by symmetry P(11) is the same, so P(same) = cos^2(π/8) = 0.8536.
- E = cos(π/4) = 0.7071.

The check prints `a = 0.0000, b = 0.3927: P(same) = 0.8536, cos^2(a-b) = 0.8536, E = 0.7071` and confirms that 20,000 sampled shots land within 4 standard errors. At a - b = π/4 the agreement drops to 0.5000: the qubits are maximally entangled, yet these particular measurements are uncorrelated. Entanglement shows up in *patterns* of correlations across bases, not in any single basis.

Every marginal is 1/2 whatever the angles: Bob alone always sees a fair coin. That is the seed of the no-signalling result in lesson 24.

## Qubit ordering (a practical trap)

Textbooks write |ab> = |a> ⊗ |b>, left factor first. Qiskit and this course's `qsim` number qubits from the right: qubit 0 is the least-significant bit. So the left factor of `np.kron` is the *highest-numbered* qubit. The check verifies that |+> ⊗ |1> = [0.0, 0.7071, 0.0, 0.7071] equals qsim's "H on q1, X on q0". State the convention in every derivation; most "wrong answers" when comparing frameworks (L100 #6) are ordering errors, not physics errors.

## How this connects to the labs

- L100 #2-#3: the 50/50 from H|0> is the Born rule applied to amplitudes 1/√2.
- L100 #4: "only 00 and 11" is T23.4 with a = b = 0.
- L200 #10: <Z> = cos θ for RY(θ)|0> is P(0) - P(1) = cos^2(θ/2) - sin^2(θ/2).
- L300 #12: noisy evolution is *not* a unitary on the state vector; it needs density matrices (lesson 24).

## Common misconceptions

- **"A qubit stores both 0 and 1, so n qubits hold 2^n answers."** The state has 2^n amplitudes, but a measurement returns n bits. Algorithms must use interference to make the useful answer likely.
- **"Superposition is just not knowing the value."** A 50/50 classical coin and |+> agree in the Z basis but not in the X basis (T23.3). Relative phase is physical.
- **"Global phase matters, so −|ψ> is a different state."** It is the same state; no experiment distinguishes them.
- **"Any invertible matrix is a valid gate."** Only unitaries preserve probability (T23.1).
- **"Entangled qubits send signals to each other."** Each marginal stays 1/2 whatever the other side does; correlations appear only when results are compared.
- **"np.vdot and np.dot are interchangeable."** `np.dot` does not conjugate; for complex states it gives the wrong inner product.

## Check yourself

Before the problem set, predict without code: (1) P(same) for a = π/8, b = -π/8; (2) whether (|00> + |01> + |10> + |11>)/2 is entangled; (3) what H ⊗ H does to |00>. Then confirm each with numpy.
