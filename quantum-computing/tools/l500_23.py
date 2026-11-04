"""L500 lesson 23 data: Foundations I - linear algebra for qubits. Built into content/L500.json by build_l500_json.py."""

LAB = "labs/L500/23-linear-algebra-for-qubits"

LESSON = {
    "id": "foundations-linear-algebra-for-qubits",
    "number": 23,
    "level": "L500",
    "title": "Foundations I: linear algebra for qubits",
    "phase": "Theory & Rigour",
    "category": "foundations",
    "description": "Dirac notation, inner products, tensor products, unitaries and the Born rule, with proofs that "
                   "unitaries preserve norm and a derivation of Bell-state measurement statistics, each checked in numpy.",
    "outcome": "You can read and write the state-vector mathematics behind every circuit in L100-L400, prove the two "
               "facts the labs silently rely on (unitarity keeps probabilities summing to 1; a Bell pair gives "
               "cos^2(a-b) agreement), and confirm each result numerically.",
    "estimatedTime": "4-6 hours (reading 1.5 h, proofs and checks 1.5 h, problem set 2-3 h)",
    "prerequisites": [
        "linear algebra: complex numbers and conjugates, vectors, matrix multiplication, transpose, eigenvalues",
        "trigonometry: sin/cos identities (cos(a)cos(b) + sin(a)sin(b) = cos(a - b))",
        "probability: discrete distributions, expected value",
        "L100 #2-#4 (gates, shots, Bell pair) for the circuits being explained",
    ],
    "learningObjectives": [
        "Explain Dirac notation (kets, bras, inner and outer products) and translate between it and numpy arrays, including the qubit-ordering convention.",
        "Prove that a unitary matrix preserves inner products and norms, and explain why that is exactly what keeps measurement probabilities summing to 1.",
        "Derive the joint state of two qubits with the tensor product and decide, with proof, whether a given two-qubit state is a product state or entangled.",
        "Derive the measurement statistics of the Bell state |Φ+> in rotated bases (P(same) = cos^2(a - b)) and evaluate a simulation against that prediction.",
    ],
    "glossary": [
        {"term": "ket |ψ>", "meaning": "A column vector in C^d representing a state; for one qubit d = 2."},
        {"term": "bra <ψ|", "meaning": "The conjugate transpose of |ψ> (a row vector)."},
        {"term": "inner product <φ|ψ>", "meaning": "sum_k conj(φ_k) ψ_k; numpy: np.vdot(phi, psi). Linear in the second argument."},
        {"term": "norm ||ψ||", "meaning": "sqrt(<ψ|ψ>); a state vector has norm 1."},
        {"term": "unitary U", "meaning": "A square matrix with U†U = I; every gate in a circuit is one."},
        {"term": "tensor (Kronecker) product ⊗", "meaning": "Combines systems: (A ⊗ B)_{(i,j),(k,l)} = A_ik B_jl; numpy: np.kron."},
        {"term": "Born rule", "meaning": "Measuring |ψ> in an orthonormal basis {|b_k>} gives outcome k with probability |<b_k|ψ>|^2."},
        {"term": "global vs relative phase", "meaning": "e^{iθ}|ψ> is the same state; a phase on one component only changes interference."},
        {"term": "product state / entangled state", "meaning": "|a> ⊗ |b> for some single-qubit |a>, |b>; entangled = not of that form."},
        {"term": "Bell states", "meaning": "|Φ±> = (|00> ± |11>)/√2, |Ψ±> = (|01> ± |10>)/√2: an orthonormal basis of two qubits."},
    ],
    "theorems": [
        {
            "name": "T23.1 Unitaries preserve inner products, norms and total probability",
            "statement": "If U is unitary (U†U = I) then <Uφ|Uψ> = <φ|ψ> for all φ, ψ; in particular ||Uψ|| = ||ψ||, so the "
                         "Born probabilities of Uψ in any orthonormal basis sum to 1. Conversely, a linear map that preserves "
                         "the norm of every vector of a finite-dimensional complex space is unitary.",
            "proof": r"""**Proof.** The bra of $U|\psi\rangle$ is $(U|\psi\rangle)^\dagger = \langle\psi|U^\dagger$. Hence
$\langle U\varphi|U\psi\rangle = \langle\varphi|U^\dagger U|\psi\rangle = \langle\varphi|I|\psi\rangle = \langle\varphi|\psi\rangle$.
Taking $\varphi = \psi$ gives $\|U\psi\|^2 = \|\psi\|^2 = 1$. If $\{|b_k\rangle\}$ is any orthonormal basis then
$\sum_k |\langle b_k|U\psi\rangle|^2 = \|U\psi\|^2$ (Parseval: expand $U|\psi\rangle = \sum_k \langle b_k|U\psi\rangle |b_k\rangle$ and use orthonormality), so the probabilities sum to 1.

**Converse (polarisation).** Suppose $\|A x\| = \|x\|$ for all $x$. For complex inner products,
$\langle x|y\rangle = \tfrac14\sum_{k=0}^{3} i^{-k}\,\|x + i^k y\|^2$ (check by expanding each norm). Every term on the right is unchanged when $x, y$ are replaced by $Ax, Ay$, so $\langle Ax|Ay\rangle = \langle x|y\rangle$ for all $x, y$, i.e. $\langle x|(A^\dagger A - I)y\rangle = 0$ for all $x, y$; choosing $x = (A^\dagger A - I)y$ gives $A^\dagger A = I$. ∎

**Why it matters.** Every gate in L100-L400 is unitary, which is why counts always add up to the number of shots. The matrix
[[1, 1], [0, 1]] is invertible but not unitary: it sends |1> to a vector of norm √2, whose "probabilities" would sum to 2.""",
            "check": f"{LAB}/theorems.py::T23.1",
        },
        {
            "name": "T23.2 Tensor-product rules",
            "statement": "For matrices of compatible sizes, (A ⊗ B)(C ⊗ D) = AC ⊗ BD (mixed-product rule); for vectors, "
                         "<a ⊗ b|c ⊗ d> = <a|c><b|d>; hence if U and V are unitary then U ⊗ V is unitary, and a product "
                         "of normalised states is normalised.",
            "proof": r"""**Proof.** Index the rows of a Kronecker product by pairs: $(A\otimes B)_{(i,j),(k,l)} = A_{ik}B_{jl}$. Then
$[(A\otimes B)(C\otimes D)]_{(i,j),(m,n)} = \sum_{k,l} A_{ik}B_{jl}C_{km}D_{ln} = (\sum_k A_{ik}C_{km})(\sum_l B_{jl}D_{ln}) = (AC)_{im}(BD)_{jn}$,
which is the $(i,j),(m,n)$ entry of $AC\otimes BD$. For vectors, $(a\otimes b)^\dagger = a^\dagger\otimes b^\dagger$, so by the
same rule $\langle a\otimes b|c\otimes d\rangle = (a^\dagger c)\otimes(b^\dagger d) = \langle a|c\rangle\langle b|d\rangle$ (a 1x1 Kronecker product is an ordinary product).
Finally $(U\otimes V)^\dagger(U\otimes V) = (U^\dagger\otimes V^\dagger)(U\otimes V) = U^\dagger U\otimes V^\dagger V = I\otimes I = I$. ∎

**Ordering convention.** Textbooks write $|ab\rangle = |a\rangle\otimes|b\rangle$ with the left factor most significant. Qiskit (and this
course's qsim) label qubit 0 as the least-significant bit, so the left factor of np.kron is the *highest-numbered* qubit. The check
confirms |+> ⊗ |1> equals qsim's "H on q1, X on q0" (L100 #6 shows why this matters when comparing frameworks).""",
            "check": f"{LAB}/theorems.py::T23.2",
        },
        {
            "name": "T23.3 Born rule in any orthonormal basis; global phase is unobservable",
            "statement": "For a unit vector |ψ> and orthonormal basis {|b_k>}, p_k = |<b_k|ψ>|^2 is a probability distribution. "
                         "Replacing |ψ> by e^{iθ}|ψ> changes no p_k in any basis, whereas a relative phase (e.g. |+> vs |->) "
                         "can change the distribution in another basis.",
            "proof": r"""**Proof.** $p_k \ge 0$ trivially, and $\sum_k p_k = \sum_k \langle\psi|b_k\rangle\langle b_k|\psi\rangle = \langle\psi|\big(\sum_k |b_k\rangle\langle b_k|\big)|\psi\rangle = \langle\psi|\psi\rangle = 1$,
because $\sum_k |b_k\rangle\langle b_k| = I$ for an orthonormal basis (completeness). With a global phase,
$|\langle b_k|e^{i\theta}\psi\rangle|^2 = |e^{i\theta}|^2|\langle b_k|\psi\rangle|^2 = |\langle b_k|\psi\rangle|^2$; since any later unitary $U$ gives
$Ue^{i\theta}|\psi\rangle = e^{i\theta}U|\psi\rangle$, no experiment can ever detect $\theta$. A *relative* phase is different:
$|\pm\rangle = (|0\rangle \pm |1\rangle)/\sqrt2$ give identical Z-basis statistics (1/2, 1/2), but in the X basis $|\langle +|+\rangle|^2 = 1$ and $|\langle +|-\rangle|^2 = 0$. ∎

Measuring "in the X basis" on hardware means applying H and then measuring Z, because $|\langle \pm|\psi\rangle|^2 = |\langle 0/1|H|\psi\rangle|^2$; this is the
rotate-then-measure pattern behind every basis change in the labs.""",
            "check": f"{LAB}/theorems.py::T23.3",
        },
        {
            "name": "T23.4 Bell-state measurement statistics",
            "statement": "Let |Φ+> = (|00> + |11>)/√2 = CX(H ⊗ I)|00>. If each qubit is measured in the rotated basis "
                         "{|u_θ> = cos θ|0> + sin θ|1>, |u_θ⊥> = -sin θ|0> + cos θ|1>} with angles a and b, then "
                         "P(00) = P(11) = cos^2(a - b)/2, P(01) = P(10) = sin^2(a - b)/2, so P(same) = cos^2(a - b) and the "
                         "correlation E = P(same) - P(different) = cos 2(a - b). The four Bell states form an orthonormal basis "
                         "that CX followed by H maps onto |00>, |01>, |10>, |11>.",
            "proof": r"""**Derivation.** Start from $|00\rangle$: $H\otimes I$ gives $(|00\rangle + |10\rangle)/\sqrt2$ and CX (control = first qubit) flips the second qubit
when the first is 1, giving $|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt2$. For the rotated basis vectors (real amplitudes, so bras need no conjugation):
$\langle u_a\otimes u_b|\Phi^+\rangle = \tfrac{1}{\sqrt2}(\cos a\cos b + \sin a\sin b) = \tfrac{1}{\sqrt2}\cos(a-b)$, so $P(00) = \cos^2(a-b)/2$.
Similarly $\langle u_a^\perp\otimes u_b^\perp|\Phi^+\rangle = \tfrac1{\sqrt2}(\sin a\sin b + \cos a\cos b)$ gives $P(11) = \cos^2(a-b)/2$, and
$\langle u_a\otimes u_b^\perp|\Phi^+\rangle = \tfrac1{\sqrt2}(-\cos a\sin b + \sin a\cos b) = \tfrac1{\sqrt2}\sin(a-b)$ gives $P(01) = \sin^2(a-b)/2$ (same for 10).
Therefore $P(\text{same}) = \cos^2(a-b)$ and $E = \cos^2(a-b) - \sin^2(a-b) = \cos 2(a-b)$. With $a = b = 0$ this is L100 #4's "only 00 and 11, each 1/2".
Each marginal is 1/2 for every angle: Bob alone sees a fair coin whatever Alice does (no signalling, made precise in lesson 24).

**Bell basis.** Writing $|\Phi^\pm\rangle, |\Psi^\pm\rangle$ in the computational basis, the Gram matrix of the four vectors is $I$ by direct calculation.
$(H\otimes I)\,\mathrm{CX}$ is unitary and is the inverse of the preparation circuit $\mathrm{CX}(H\otimes I)$ applied to $|00\rangle, |01\rangle, |10\rangle, |11\rangle$,
so it maps the Bell states back to those basis states: a "Bell measurement" is CX, H, then an ordinary measurement. ∎

**Numerical check.** On hardware, measuring in basis angle θ = applying RY(-2θ) then measuring Z. The check compares the exact
probabilities with cos^2(a - b) for five angle pairs and draws 20,000 seeded shots per pair (agreement within 4 standard errors).""",
            "check": f"{LAB}/theorems.py::T23.4",
        },
    ],
    "problemSet": [
        {"id": "qc-L500-23-P1", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "Let |ψ> = (|0> + i|1>)/√2 and |φ> = (|0> + |1>)/√2 = |+>. Compute <ψ|φ> and |<ψ|φ>|^2. What is the probability of outcome '+' if |ψ> is measured in the X basis?",
         "solution": "<ψ| = (1, -i)/√2 (conjugate!). <ψ|φ> = (1·1 + (-i)·1)/2 = (1 - i)/2 = 0.5 - 0.5i. |<ψ|φ>|^2 = (0.25 + 0.25) = 0.5. By the Born rule (T23.3) the probability of '+' is |<+|ψ>|^2 = 0.5. Common error: forgetting to conjugate the bra gives (1 + i)/2, which has the same modulus here but the wrong phase; the check in research/l500_checks.py recomputes 0.5 with np.vdot."},
        {"id": "qc-L500-23-P2", "type": "proof", "difficulty": 1, "marks": 5,
         "problem": "Prove that H = (1/√2)[[1, 1], [1, -1]] is unitary and Hermitian, that H^2 = I, and deduce its eigenvalues.",
         "solution": "H has real entries and is symmetric, so H† = H^T = H (Hermitian). H†H = H^2 = (1/2)[[1+1, 1-1], [1-1, 1+1]] = I, so H is unitary. If Hv = λv with v ≠ 0 then v = H^2 v = λ^2 v, so λ^2 = 1 and λ ∈ {+1, -1}; the trace is 0 = λ1 + λ2, so one eigenvalue is +1 and the other -1."},
        {"id": "qc-L500-23-P3", "type": "calculation", "difficulty": 2, "marks": 5,
         "problem": "Write |+> ⊗ (√3/2 |0> + 1/2 |1>) in the basis |00>, |01>, |10>, |11> (textbook order: left factor first). Give P(11) and the probability that the LEFT qubit reads 1. Which qsim/Qiskit qubit is the left factor?",
         "solution": "Amplitudes = (1/√2)(√3/2, 1/2, √3/2, 1/2) = (0.6124, 0.3536, 0.6124, 0.3536). P(11) = (1/(2√2))^2 = 0.125. P(left = 1) = P(10) + P(11) = 0.375 + 0.125 = 0.5, as it must be for a product state with |+> on the left. In qsim/Qiskit order the left factor of np.kron is the highest-numbered qubit (q1 here), see T23.2."},
        {"id": "qc-L500-23-P4", "type": "proof", "difficulty": 2, "marks": 6,
         "problem": "Prove that |Φ+> = (|00> + |11>)/√2 is not a product state.",
         "solution": "Suppose |Φ+> = (α|0> + β|1>) ⊗ (γ|0> + δ|1>) = αγ|00> + αδ|01> + βγ|10> + βδ|11>. Comparing coefficients: αγ = 1/√2, βδ = 1/√2, αδ = 0, βγ = 0. From αδ = 0 either α = 0 (contradicting αγ ≠ 0) or δ = 0 (contradicting βδ ≠ 0). Hence no such factorisation exists and |Φ+> is entangled. (Equivalent test: arrange the amplitudes as the 2x2 matrix [[1, 0], [0, 1]]/√2; a product state gives a rank-1 matrix, this has rank 2.)"},
        {"id": "qc-L500-23-P5", "type": "calculation", "difficulty": 2, "marks": 5,
         "problem": "Alice and Bob share |Φ+>. Alice measures at angle a = 0, Bob at b = π/8 (basis {cos θ|0> + sin θ|1>, ...}). Give P(same), the correlation E, and P(same) for a = π/8, b = -π/8.",
         "solution": "By T23.4, P(same) = cos^2(a - b) = cos^2(π/8) = 0.8536 and E = cos(2(a - b)) = cos(π/4) = 0.7071. For a = π/8, b = -π/8: a - b = π/4, P(same) = cos^2(π/4) = 0.5 (E = 0): the outcomes are uncorrelated even though the state is maximally entangled. The theorem check prints the same three numbers from simulation."},
        {"id": "qc-L500-23-P6", "type": "calculation", "difficulty": 1, "marks": 3,
         "problem": "RY(θ) = [[cos θ/2, -sin θ/2], [sin θ/2, cos θ/2]]. For θ = π/3 compute RY(θ)|0>, P(1) and <Z>.",
         "solution": "RY(π/3)|0> = (cos π/6, sin π/6) = (0.8660, 0.5). P(1) = sin^2(π/6) = 0.25, P(0) = 0.75, <Z> = P(0) - P(1) = 0.5 = cos θ. (L200 #10 fits exactly this cos θ curve.)"},
        {"id": "qc-L500-23-P7", "type": "derivation", "difficulty": 2, "marks": 6,
         "problem": "Show that (H ⊗ I)·CX maps |Φ+>, |Φ->, |Ψ+>, |Ψ-> to |00>, |10>, |01>, |11> respectively (control = left qubit), and explain why this implements a measurement in the Bell basis.",
         "solution": "CX|Φ±> = (|00> ± |10>)/√2 = |±> ⊗ |0>; CX|Ψ±> = (|01> ± |11>)/√2 = |±> ⊗ |1>. Then H|+> = |0>, H|-> = |1>, so Φ+ -> |00>, Φ- -> |10>, Ψ+ -> |01>, Ψ- -> |11>. Because this unitary maps the orthonormal Bell basis onto the computational basis, measuring in the computational basis afterwards gives outcome k with probability |<Bell_k|ψ>|^2 (T23.1 + T23.3): exactly a Bell-basis measurement. The check prints the qsim version (qsim labels bits q1 q0)."},
        {"id": "qc-L500-23-P8", "type": "calculation", "difficulty": 2, "marks": 4,
         "problem": "For |Φ+> compute the expectation values <Z⊗Z>, <X⊗X>, <Y⊗Y> and <Z⊗I>. Which of them would a product state |a>|b> with <Z⊗I> = 0 and <I⊗Z> = 0 be unable to reproduce simultaneously?",
         "solution": "<Z⊗Z> = 1, <X⊗X> = 1, <Y⊗Y> = -1, <Z⊗I> = 0 (computed with np.kron in research/l500_checks.py). For a product state <A⊗B> = <A><B>; <Z⊗I> = 0 forces <Z> = 0 on the left qubit, so <Z⊗Z> = 0 ≠ 1. Perfect correlations with random marginals are the signature of entanglement."},
        {"id": "qc-L500-23-P9", "type": "short-answer", "difficulty": 1, "marks": 3,
         "problem": "A student models a noisy gate as M = [[1, 1], [0, 1]] applied to the state vector. Show with one vector that M is not a valid closed-system evolution and say which theorem it violates.",
         "solution": "M|1> = (1, 1) with norm √2 = 1.4142, so the outcome probabilities would sum to 2.0. M is invertible but not unitary (M†M ≠ I), violating T23.1. Noise is modelled with density matrices and channels instead (L300 #12, lesson 24)."},
    ],
    "rubric": [
        {"criterion": "Correctness of mathematics", "excellent": "Every step valid; conjugation, ordering and normalisation handled explicitly.", "adequate": "Main argument right; one slip (e.g. a missing conjugate) that does not change the conclusion.", "inadequate": "Key step wrong or assumed (e.g. treats U as preserving norm without using U†U = I).", "weight": 40},
        {"criterion": "Proof structure and rigour", "excellent": "States what is assumed and proved; each line follows; quantifiers ('for all ψ') explicit.", "adequate": "Readable but skips a justification a reader could supply.", "inadequate": "Argument by example only, or circular.", "weight": 25},
        {"criterion": "Numerical evidence", "excellent": "Runs the check, quotes the real output, and explains any tolerance used.", "adequate": "Runs the check but does not connect output to the claim.", "inadequate": "No check, or numbers typed in by hand.", "weight": 20},
        {"criterion": "Communication", "excellent": "Notation consistent, qubit order stated, units/bases named.", "adequate": "Mostly consistent notation.", "inadequate": "Mixes conventions so results cannot be checked.", "weight": 15},
    ],
    "conceptNote": "content/concepts/L500/23-linear-algebra-for-qubits.md",
    "conceptSummary": "A qubit state is a unit vector in C^2; n qubits live in the tensor product C^(2^n). Gates are unitaries, and unitaries preserve inner products, so probabilities always sum to 1 (proved, then checked on 1000 random unitaries). The Born rule turns amplitudes into probabilities in any orthonormal basis; global phase never shows, relative phase does. A Bell pair measured at angles a and b agrees with probability cos^2(a - b).",
    "sources": [
        {"title": "IBM Quantum Learning - Basics of quantum information: Single systems, Quantum information (J. Watrous)", "url": "https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/single-systems/quantum-information"},
        {"title": "IBM Quantum Learning - Basics of quantum information: Multiple systems, Quantum information (J. Watrous)", "url": "https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/multiple-systems/quantum-information"},
        {"title": "IBM Quantum Learning - Limitations on quantum information (global phase, no-cloning)", "url": "https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/quantum-circuits/limitations-on-quantum-information"},
        {"title": "Bit-ordering in the Qiskit SDK", "url": "https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering"},
    ],
    "seeAlso": [
        "quantum-computing L100 #2 Qubits and gates in code: the X and H matrices whose unitarity T23.1 proves.",
        "quantum-computing L100 #3 Shots, counts and probability: the Born rule (T23.3) is where the 50/50 comes from.",
        "quantum-computing L100 #4 Entanglement with a Bell pair: T23.4 derives its 00/11 statistics and generalises them to any angles.",
        "quantum-computing L100 #6 Same circuit, two frameworks: the tensor-product ordering convention of T23.2.",
        "quantum-computing L200 #10 Parameterized circuits and sweeps: <Z> = cos θ for RY(θ)|0> (problem P6).",
    ],
    "next": "L500 #24 Foundations II: quantum information basics - what entanglement buys you (teleportation, superdense coding) and what quantum mechanics forbids (cloning).",
}
