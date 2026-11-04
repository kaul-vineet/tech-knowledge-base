"""L500 lesson 24 data: Foundations II - quantum information basics. Built into content/L500.json by build_l500_json.py."""

LAB = "labs/L500/24-quantum-information-basics"

LESSON = {
    "id": "foundations-quantum-information-basics",
    "number": 24,
    "level": "L500",
    "title": "Foundations II: quantum information basics",
    "phase": "Theory & Rigour",
    "category": "foundations",
    "description": "No-cloning with proof, teleportation and superdense coding derived line by line, Deutsch-Jozsa "
                   "correctness, and density matrices with the partial trace, each checked numerically.",
    "outcome": "You can prove why quantum states cannot be copied, derive the teleportation and superdense-coding "
               "protocols from the Bell basis, prove that Deutsch-Jozsa never errs, and use density matrices and the "
               "partial trace to describe part of an entangled system (and to show that entanglement cannot signal).",
    "estimatedTime": "5-7 hours (reading 2 h, proofs and checks 2 h, problem set 2-3 h)",
    "prerequisites": [
        "lesson 23 (Dirac notation, tensor products, Bell basis, T23.1-T23.4)",
        "linear algebra: outer products, trace, Hermitian and positive semidefinite matrices, eigenvalues",
        "Boolean functions and XOR; a geometric series sum",
    ],
    "learningObjectives": [
        "Prove the no-cloning theorem in two ways (linearity and inner products) and explain why copying basis states with a CNOT does not contradict it.",
        "Derive the teleportation identity |ψ>|Φ+> = (1/2) Σ |Bell_xz> ⊗ X^x Z^z|ψ> and use it to explain why each outcome has probability 1/4 and why no information travels faster than the classical bits.",
        "Derive superdense coding and analyse it as the resource-dual of teleportation (1 e-bit + 1 qubit = 2 bits).",
        "Prove that Deutsch-Jozsa outputs 0^n with probability 1 for constant f and 0 for balanced f, and evaluate the classical query cost it is compared with.",
        "Analyze states with density matrices and partial traces, and explain with them why measurements on one half of a Bell pair cannot signal to the other half.",
    ],
    "glossary": [
        {"term": "no-cloning", "meaning": "No fixed unitary and blank state copy every unknown |ψ> to |ψ>|ψ>."},
        {"term": "e-bit", "meaning": "One shared Bell pair, used as a resource."},
        {"term": "teleportation", "meaning": "Moves an unknown qubit state using 1 e-bit + 2 classical bits; the original is destroyed."},
        {"term": "superdense coding", "meaning": "Sends 2 classical bits by transmitting 1 qubit of a pre-shared e-bit."},
        {"term": "phase kickback", "meaning": "With the target in |->, an oracle |x>|y> -> |x>|y ⊕ f(x)> acts as |x> -> (-1)^f(x) |x>."},
        {"term": "balanced / constant function", "meaning": "f: {0,1}^n -> {0,1} that outputs 1 on exactly half of the inputs / on all or none."},
        {"term": "density matrix ρ", "meaning": "Σ_i p_i |ψ_i><ψ_i|: Hermitian, positive semidefinite, trace 1. Pure iff Tr ρ^2 = 1."},
        {"term": "partial trace Tr_A", "meaning": "The unique map giving the state of B alone: (Tr_A ρ)_{jk} = Σ_i ρ_{(i,j),(i,k)}."},
        {"term": "purity", "meaning": "Tr ρ^2, between 1/d (maximally mixed) and 1 (pure)."},
        {"term": "no-signalling", "meaning": "Nothing Alice does locally changes Bob's reduced state ρ_B."},
    ],
    "theorems": [
        {
            "name": "T24.1 No-cloning theorem",
            "statement": "Let d >= 2. There is no state |e> and unitary U on C^d ⊗ C^d such that U(|ψ> ⊗ |e>) = |ψ> ⊗ |ψ> for every unit vector |ψ>.",
            "proof": r"""**Proof 1 (inner products).** Suppose such $U, |e\rangle$ exist and take any two states $|\psi\rangle, |\varphi\rangle$. By T23.1 and T23.2,
$\langle\psi|\varphi\rangle = \langle\psi|\varphi\rangle\langle e|e\rangle = \langle U(\psi\otimes e)|U(\varphi\otimes e)\rangle = \langle\psi\otimes\psi|\varphi\otimes\varphi\rangle = \langle\psi|\varphi\rangle^2$.
So $x = \langle\psi|\varphi\rangle$ satisfies $x = x^2$, i.e. $x \in \{0, 1\}$: a cloner could only work on a set of mutually orthogonal (or identical) states.
But $|0\rangle$ and $|+\rangle$ have $\langle 0|+\rangle = 1/\sqrt2$, a contradiction. ∎

**Proof 2 (linearity, as in Watrous's IBM course).** If $U(|0\rangle|e\rangle) = |00\rangle$ and $U(|1\rangle|e\rangle) = |11\rangle$, linearity forces
$U(|+\rangle|e\rangle) = (|00\rangle + |11\rangle)/\sqrt2$, which is entangled (P4 of lesson 23) and so differs from $|{+}{+}\rangle = (|00\rangle+|01\rangle+|10\rangle+|11\rangle)/2$.

**Remarks.** (i) The CNOT "copier" clones $|0\rangle$ and $|1\rangle$ perfectly; on $\cos(\theta/2)|0\rangle + \sin(\theta/2)|1\rangle$ its joint fidelity with the ideal
clone is $(c^3 + s^3)^2$ ($c = \cos\theta/2$, $s = \sin\theta/2$), falling to 1/2 for $|+\rangle$. (ii) The theorem forbids perfect cloning of *unknown* states;
approximate cloning with bounded fidelity is possible. (iii) Consequences: no "save a copy" for debugging a quantum state, no amplifying a weak quantum signal,
and the security of quantum key distribution.""",
            "check": f"{LAB}/theorems.py::T24.1",
        },
        {
            "name": "T24.2 Teleportation and superdense coding",
            "statement": "(a) If Alice holds |ψ> and shares |Φ+> with Bob, measuring her two qubits in the Bell basis gives each of the four "
                         "outcomes (x, z) with probability 1/4, and Bob's qubit is then X^x Z^z |ψ>; applying Z^z X^x restores |ψ> exactly. "
                         "(b) If Alice applies Z^a X^b to her half of |Φ+> and sends it to Bob, a Bell measurement by Bob returns (a, b) with certainty.",
            "proof": r"""**(a) Derivation.** Write $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ on qubit M, with $|\Phi^+\rangle$ on A (Alice) and B (Bob):
$|\psi\rangle|\Phi^+\rangle = \tfrac{1}{\sqrt2}(\alpha|000\rangle + \alpha|011\rangle + \beta|100\rangle + \beta|111\rangle)$ (order M, A, B).
Invert the Bell-basis definitions: $|00\rangle = (\Phi^+ + \Phi^-)/\sqrt2$, $|11\rangle = (\Phi^+ - \Phi^-)/\sqrt2$, $|01\rangle = (\Psi^+ + \Psi^-)/\sqrt2$, $|10\rangle = (\Psi^+ - \Psi^-)/\sqrt2$ on (M, A). Collecting terms,
$$|\psi\rangle|\Phi^+\rangle = \tfrac12\big[\,|\Phi^+\rangle(\alpha|0\rangle+\beta|1\rangle) + |\Phi^-\rangle(\alpha|0\rangle-\beta|1\rangle) + |\Psi^+\rangle(\alpha|1\rangle+\beta|0\rangle) + |\Psi^-\rangle(\alpha|1\rangle-\beta|0\rangle)\,\big].$$
The four Bob states are $|\psi\rangle, Z|\psi\rangle, X|\psi\rangle, XZ|\psi\rangle$ (the last up to a global phase $-1$). Each branch has amplitude $1/2$ times a unit vector,
so by the Born rule each Bell outcome has probability $1/4$ *independently of* $\alpha, \beta$: the outcomes carry no information about $|\psi\rangle$.
Bob applies $X^x$ then $Z^z$ (or the circuit form: Alice does CX(M→A), H(M), measures; Bob applies X if A = 1, then Z if M = 1). Fidelity is exactly 1.
Until Bob receives the 2 classical bits his reduced state is $\tfrac14\sum_{xz} X^xZ^z|\psi\rangle\langle\psi|Z^zX^x = I/2$, so nothing has been signalled; and
Alice's measurement destroyed her copy, consistent with T24.1.

**(b) Derivation.** On Alice's qubit, $X$ maps $\Phi^\pm \to \Psi^\pm$ and $Z$ maps $\Phi^+\to\Phi^-$, $\Psi^+\to\Psi^-$; so $Z^aX^b \otimes I$ sends $|\Phi^+\rangle$ to a distinct Bell state for each of the four messages
(up to sign). Bob's CX then H maps the Bell basis to the computational basis (T23.4), giving (a, b) with probability 1.
**Resource view:** teleportation spends 1 e-bit + 2 bits to send 1 qubit; superdense coding spends 1 e-bit + 1 qubit to send 2 bits. ∎""",
            "check": f"{LAB}/theorems.py::T24.2",
        },
        {
            "name": "T24.3 Deutsch-Jozsa correctness",
            "statement": "Given a promise that f: {0,1}^n -> {0,1} is constant or balanced, the circuit H^{⊗n}, oracle (phase form "
                         "|x> -> (-1)^{f(x)}|x>), H^{⊗n} applied to |0^n> outputs 0^n with probability 1 if f is constant and 0 if f is balanced, using one oracle call. "
                         "A deterministic classical algorithm needs 2^{n-1} + 1 queries in the worst case.",
            "proof": r"""**Proof.** Using $H^{\otimes n}|x\rangle = 2^{-n/2}\sum_y (-1)^{x\cdot y}|y\rangle$:
after the first layer the state is $2^{-n/2}\sum_x|x\rangle$; the oracle gives $2^{-n/2}\sum_x (-1)^{f(x)}|x\rangle$ (phase kickback: with an ancilla in $|-\rangle$,
$|x\rangle|-\rangle \mapsto (-1)^{f(x)}|x\rangle|-\rangle$). After the final layer the amplitude of $|0^n\rangle$ is
$$a_0 = \frac{1}{2^n}\sum_x (-1)^{f(x)}.$$
If f is constant, $a_0 = \pm 1$, so $P(0^n) = 1$. If f is balanced, half the terms are $+1$ and half $-1$, so $a_0 = 0$ and $P(0^n) = 0$.
**Classical bound.** An adversary can answer the first $2^{n-1}$ queries of any deterministic algorithm with the same value; both a constant and a balanced
function are consistent with those answers, so one more query is needed: $2^{n-1}+1$. ∎

**Honest caveat.** A *randomised* classical algorithm that queries k random inputs errs with probability at most $2^{1-k}$ (it can only fail on a balanced f by seeing
k equal values), so the exponential separation is only against exact deterministic algorithms. That is why Deutsch-Jozsa is a teaching example, not an application;
Bernstein-Vazirani (L200 #7) and Simon's problem sharpen the separation.""",
            "check": f"{LAB}/theorems.py::T24.3",
        },
        {
            "name": "T24.4 Density matrices, partial trace and no-signalling",
            "statement": "ρ = Σ p_i|ψ_i><ψ_i| is Hermitian, positive semidefinite with trace 1, and Tr ρ^2 = 1 iff ρ is pure. For |Φ+>, "
                         "Tr_A |Φ+><Φ+| = I/2 (purity 1/2) although the global state is pure. For any state ρ_AB and any unitary U_A or "
                         "measurement on A whose result is not communicated, Tr_A of the new state equals Tr_A ρ_AB.",
            "proof": r"""**Properties.** $\rho^\dagger = \sum p_i (|\psi_i\rangle\langle\psi_i|)^\dagger = \rho$; $\langle v|\rho|v\rangle = \sum p_i|\langle\psi_i|v\rangle|^2 \ge 0$; $\mathrm{Tr}\rho = \sum p_i\langle\psi_i|\psi_i\rangle = 1$.
With eigenvalues $\lambda_k \ge 0$ summing to 1, $\mathrm{Tr}\rho^2 = \sum\lambda_k^2 \le (\max_k\lambda_k)\sum_k\lambda_k \le 1$, with equality iff one $\lambda_k = 1$, i.e. $\rho$ is a projector onto one pure state.
**Bell pair.** $|\Phi^+\rangle\langle\Phi^+| = \tfrac12(|00\rangle\langle00| + |00\rangle\langle11| + |11\rangle\langle00| + |11\rangle\langle11|)$. Tracing out A keeps only terms with equal A-labels:
$\mathrm{Tr}_A = \tfrac12(|0\rangle\langle0| + |1\rangle\langle1|) = I/2$, purity $\tfrac14+\tfrac14 = 1/2$. Global knowledge is perfect; local knowledge is nil: a hallmark of entanglement.
**No-signalling.** Partial trace is invariant under conjugation by operators on the traced-out factor: $\mathrm{Tr}_A[(U\otimes I)\rho(U^\dagger\otimes I)] = \mathrm{Tr}_A[\rho\,(U^\dagger U\otimes I)] = \mathrm{Tr}_A\rho$
(cyclicity of the trace over A). An unread measurement $\rho \mapsto \sum_k (P_k\otimes I)\rho(P_k\otimes I)$ with $\sum_k P_k = I$ gives, by the same cyclicity, $\mathrm{Tr}_A[\rho\sum_k P_k] = \mathrm{Tr}_A\rho$. ∎

**Why it matters for practice.** Noise models (L300 #12) are maps on density matrices, and "the state of one qubit of a register" in any SDK is a partial trace.
The mixture ½|0><0| + ½|+><+| has eigenvalues (2 ± √2)/4: different ensembles can give the same ρ, so ρ, not the recipe, is what experiments can distinguish.""",
            "check": f"{LAB}/theorems.py::T24.4",
        },
    ],
    "problemSet": [
        {"id": "qc-L500-24-P1", "type": "proof", "difficulty": 2, "marks": 6,
         "problem": "Give the inner-product proof of no-cloning in your own words, and explain why it does not rule out a device that clones the two states |0> and |1> only.",
         "solution": "See T24.1, Proof 1: a cloning unitary must satisfy <ψ|φ> = <ψ|φ>^2 for every pair it clones, so every pair of clonable states has overlap 0 or 1. |0> and |1> are orthogonal (overlap 0), so a CNOT with blank |0> clones them; the contradiction only arises once a non-orthogonal pair such as |0>, |+> (overlap 1/√2 = 0.7071, squared 0.5) must also be cloned."},
        {"id": "qc-L500-24-P2", "type": "derivation", "difficulty": 3, "marks": 8,
         "problem": "Derive the teleportation identity |ψ>|Φ+> = (1/2) Σ_{x,z} |Bell_{xz}> ⊗ X^x Z^z |ψ> (up to signs), and state which correction Bob applies for each of Alice's four outcomes.",
         "solution": "Expand |ψ>|Φ+> with |ψ> = α|0> + β|1> into four computational terms, substitute the inverse Bell relations for Alice's pair and collect (T24.2a). Outcomes: Φ+ -> Bob has |ψ>, no correction; Φ- -> Z|ψ>, apply Z; Ψ+ -> X|ψ>, apply X; Ψ- -> XZ|ψ> (= -ZX|ψ>), apply X then Z. Each has probability 1/4 because each branch is (1/2) × a unit vector."},
        {"id": "qc-L500-24-P3", "type": "calculation", "difficulty": 2, "marks": 4,
         "problem": "Alice teleports |ψ> = cos(π/8)|0> + sin(π/8)|1>. (i) What is the probability of each of her four outcomes? (ii) If her outcome needs both corrections and Bob forgets them and measures Z, what is P(1)? (iii) What is P(1) if Bob applies the corrections first?",
         "solution": "(i) 0.25 each, independent of ψ (T24.2). (ii) Uncorrected, Bob holds XZ|ψ> ∝ -sin(π/8)|0> + cos(π/8)|1>, so P(1) = cos^2(π/8) = 0.8536. (iii) Corrected, he holds |ψ>, so P(1) = sin^2(π/8) = 0.1464. Averaged over Alice's outcomes, before the bits arrive Bob's P(1) is 1/2 (ρ_B = I/2)."},
        {"id": "qc-L500-24-P4", "type": "derivation", "difficulty": 2, "marks": 5,
         "problem": "Show that applying I, X, Z, ZX to Alice's half of |Φ+> produces the four Bell states, and write Bob's decoding circuit. Why does this not let Alice send 2 bits with one qubit and no prior entanglement?",
         "solution": "(X ⊗ I)|Φ+> = |Ψ+>, (Z ⊗ I)|Φ+> = |Φ->, (ZX ⊗ I)|Φ+> = (|01> - |10>)/√2 = |Ψ-> (X acts first, then Z). Bob applies CX (Alice's qubit as control) then H to it and measures: messages 00, 01, 10, 11 come out with probability 1 (check prints the table). Without the pre-shared e-bit a single qubit carries at most 1 classical bit (Holevo's bound, stated here without proof); the second bit is 'paid for' by the e-bit delivered earlier."},
        {"id": "qc-L500-24-P5", "type": "calculation", "difficulty": 2, "marks": 4,
         "problem": "Deutsch-Jozsa with n = 2 and f(x1, x2) = x1 XOR x2. Compute P(00). How many queries does a deterministic classical algorithm need in the worst case for n = 10?",
         "solution": "f is balanced (f = 1 on 01 and 10). a_0 = (1/4)(1 - 1 - 1 + 1) = 0, so P(00) = 0 and the algorithm answers 'balanced'. Classical worst case for n = 10: 2^9 + 1 = 513 queries (versus 1 quantum query). A randomised classical algorithm with 10 queries errs with probability at most 2^-9."},
        {"id": "qc-L500-24-P6", "type": "calculation", "difficulty": 2, "marks": 5,
         "problem": "For |ψ> = √0.8 |00> + √0.2 |11>, compute ρ_A = Tr_B |ψ><ψ|, its purity and its von Neumann entropy S = -Σ λ log2 λ.",
         "solution": "Only equal B-labels survive: ρ_A = diag(0.8, 0.2). Purity = 0.64 + 0.04 = 0.68. S = -(0.8 log2 0.8 + 0.2 log2 0.2) = 0.7219 bits (less than 1 bit: less entangled than a Bell pair, whose ρ_A = I/2 has S = 1)."},
        {"id": "qc-L500-24-P7", "type": "calculation", "difficulty": 2, "marks": 4,
         "problem": "Find the eigenvalues and purity of ρ = ½|0><0| + ½|+><+|. Give a different ensemble of two orthogonal states with the same ρ.",
         "solution": "ρ = [[3/4, 1/4], [1/4, 1/4]]. Eigenvalues (2 ± √2)/4 = 0.8536 and 0.1464; purity = 0.8536^2 + 0.1464^2 = 0.75. Its eigen-decomposition is itself an ensemble: the two orthonormal eigenvectors (cos(π/8), sin(π/8)) and (-sin(π/8), cos(π/8)) with weights 0.8536 and 0.1464 give the same ρ, so no experiment can tell the two preparations apart."},
        {"id": "qc-L500-24-P8", "type": "calculation", "difficulty": 2, "marks": 4,
         "problem": "The CNOT 'copier' is applied to cos(θ/2)|0> + sin(θ/2)|1> with blank |0>. For θ = π/3 compute the joint fidelity with |ψ>|ψ> and the fidelity of the copy qubit alone with |ψ>.",
         "solution": "Output = c|00> + s|11> with c = cos(π/6), s = sin(π/6). Joint fidelity = |<ψψ|out>|^2 = (c^3 + s^3)^2 = 0.5999. The copy qubit alone is ρ = diag(c^2, s^2), so <ψ|ρ|ψ> = c^4 + s^4 = 0.6250. Both equal 1 only at θ = 0 or π (basis states), as T24.1 requires."},
        {"id": "qc-L500-24-P9", "type": "short-answer", "difficulty": 2, "marks": 5,
         "problem": "A blog post claims: 'Teleportation proves entanglement sends information instantly, and also makes a copy of the qubit at Bob's end.' Correct both claims using T24.1, T24.2 and T24.4.",
         "solution": "(1) Before Alice's 2 classical bits arrive, Bob's reduced state is I/2 whatever |ψ> is (T24.2a, T24.4 no-signalling), so he learns nothing; the bits travel at most at light speed. (2) Alice's Bell measurement leaves her qubits in a basis state uncorrelated with |ψ>; exactly one copy exists at any time, consistent with no-cloning (T24.1). Teleportation moves a state; it neither copies it nor signals."},
    ],
    "rubric": [
        {"criterion": "Correctness of derivations", "excellent": "Identities expanded fully; signs and global phases tracked; probabilities justified by the Born rule.", "adequate": "Correct result with a skipped algebra step.", "inadequate": "Asserts the protocol works without deriving it.", "weight": 40},
        {"criterion": "Use of theorems", "excellent": "Cites the exact theorem (T23.x/T24.x) each step relies on; recognises when a promise or assumption is needed.", "adequate": "Uses the right ideas without naming them.", "inadequate": "Applies a result outside its conditions (e.g. clones orthogonal states and claims a contradiction).", "weight": 25},
        {"criterion": "Numerical evidence", "excellent": "Runs theorems.py, quotes output, and ties every number in the answer to code.", "adequate": "Runs code but numbers only partly traced.", "inadequate": "No code evidence.", "weight": 20},
        {"criterion": "Physical interpretation", "excellent": "Explains what can and cannot be done (signalling, copying, query cost) in plain words.", "adequate": "Some interpretation.", "inadequate": "None, or a misconception (FTL, copying).", "weight": 15},
    ],
    "conceptNote": "content/concepts/L500/24-quantum-information-basics.md",
    "conceptSummary": "Linearity forbids copying unknown states (no-cloning). Entanglement is a resource: 1 e-bit + 2 bits teleports a qubit, 1 e-bit + 1 qubit carries 2 bits, and neither signals faster than light because Bob's local state stays I/2 until the bits arrive. Deutsch-Jozsa turns a global property of f into one interference amplitude. Density matrices and the partial trace describe parts of systems and noisy states.",
    "sources": [
        {"title": "IBM Quantum Learning - Limitations on quantum information (no-cloning theorem, J. Watrous)", "url": "https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/quantum-circuits/limitations-on-quantum-information"},
        {"title": "IBM Quantum Learning - Entanglement in action (teleportation, superdense coding, CHSH)", "url": "https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/entanglement-in-action/introduction"},
        {"title": "IBM Quantum Learning - The Deutsch-Jozsa algorithm", "url": "https://quantum.cloud.ibm.com/learning/en/courses/fundamentals-of-quantum-algorithms/quantum-query-algorithms/deutsch-jozsa-algorithm"},
        {"title": "IBM Quantum Learning - General formulation of quantum information: Density matrices", "url": "https://quantum.cloud.ibm.com/learning/en/courses/general-formulation-of-quantum-information/density-matrices/introduction"},
        {"title": "Cleve, Ekert, Macchiavello, Mosca (1998), Quantum algorithms revisited, arXiv:quant-ph/9708016", "url": "https://arxiv.org/abs/quant-ph/9708016"},
    ],
    "seeAlso": [
        "quantum-computing L100 #4 Entanglement with a Bell pair: the e-bit every protocol here consumes.",
        "quantum-computing L200 #7 Bernstein–Vazirani as a pattern: the same H-oracle-H interference argument as T24.3, with a sharper separation.",
        "quantum-computing L300 #12 Noise models: how Bell and GHZ results degrade: noise channels act on the density matrices of T24.4.",
        "quantum-computing L300 #13 Error mitigation: readout correction and zero-noise extrapolation: mitigation estimates properties of ρ, it cannot clone or purify it (T24.1).",
        "quantum-computing L200 #8 Small Grover search: its phase oracle is the phase-kickback construction proved in T24.3.",
    ],
    "next": "L500 #25 Foundations III: algorithms and complexity - Grover's sqrt(N), the QFT and phase estimation, Shor's reduction, and why exponential speed-ups are rare.",
}
