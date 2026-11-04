"""L500 question bank data (lessons 23-27). Correct option first; build_qbank.py balances positions.

Calculation values are computed here with math/numpy; research/qbank_checks.py recomputes each one independently and
executes every code snippet (labs/_shared on sys.path).
"""
import math

import numpy as np

from qbank_common import Q, fmt


def grover_p(n_items, m, k):
    return math.sin((2 * k + 1) * math.asin(math.sqrt(m / n_items))) ** 2


def grover_k(n_items, m):
    return math.floor(math.pi / (4 * math.asin(math.sqrt(m / n_items))))


OVERLAP = fmt(abs(np.vdot(np.array([math.sqrt(3), 1]) / 2, np.array([1, 1]) / math.sqrt(2))) ** 2)
BELL_PI6 = fmt(math.cos(math.pi / 6) ** 2, 2)
PURITY = fmt(0.9 ** 2 + 0.1 ** 2, 2)
K256 = grover_k(256, 1)
P256, P256_13 = fmt(grover_p(256, 1, K256)), fmt(grover_p(256, 1, K256 + 1))
K1M = grover_k(10 ** 6, 1)
NOISE = fmt((1 - 0.002) ** 500)

QUESTIONS = [
    # ---------------- lesson 23: linear algebra for qubits ----------------
    Q("qc-L500-001", 23, "concept", 2,
      "Why do the measurement probabilities of any circuit in this course always sum to 1?",
      ["Every gate is unitary, and unitaries preserve the norm of the state vector",
       "The simulator renormalises the state after every gate",
       "Hadamard gates spread probability evenly over all outcomes",
       "Gates are Hermitian matrices, and Hermitian matrices have real eigenvalues"],
      "T23.1: <Uψ|Uψ> = <ψ|U†U|ψ> = 1, so total probability is conserved with no renormalisation. Hermiticity is a different property (H is both, but CX·(H⊗I) is not Hermitian).",
      "Lesson 23 T23.1"),
    Q("qc-L500-002", 23, "calculation", 2,
      "|ψ> = (√3|0> + |1>)/2 is measured in the X basis. What is the probability of outcome '+'?",
      [str(OVERLAP), "0.5", "0.866", "0.683"],
      "Born rule: |<+|ψ>|^2 = ((√3 + 1)/(2√2))^2 = (4 + 2√3)/8 ≈ 0.933. 0.866 is the amplitude ratio √3/2, not a probability.",
      "Lesson 23 T23.3"),
    Q("qc-L500-003", 23, "code-reading", 2,
      "What does this qsim snippet print? (qsim prints bitstrings as q1 q0.)",
      ["{'01': 0.5, '11': 0.5}", "{'10': 0.5, '11': 0.5}", "{'00': 0.5, '01': 0.5}", "{'01': 1.0}"],
      "H on q1 makes the left character 0/1 at random; X on q0 fixes the right character to 1. '10'/'11' is the textbook-order mistake of T23.2.",
      "Lesson 23 T23.2",
      code="""from qsim import statevector as sv

state = sv.run(2, [sv.h(1), sv.x(0)])
print(sv.probabilities(state, 4))"""),
    Q("qc-L500-004", 23, "concept", 2,
      "Which pair of single-qubit states can be distinguished perfectly by some measurement?",
      ["|+> and |->", "|ψ> and -|ψ>", "|0> and i|0>", "|+> and e^{iπ/3}|+>"],
      "|+> and |-> differ by a relative phase and are orthogonal (H then measure separates them). The other pairs differ only by a global phase, which no experiment can detect (T23.3).",
      "Lesson 23 T23.3"),
    Q("qc-L500-005", 23, "calculation", 2,
      "Alice and Bob share |Φ+>. Alice measures at angle a = 0 and Bob at b = π/6 (basis cos θ|0> + sin θ|1>, ...). What is P(same outcome)?",
      [str(BELL_PI6), "0.5", "0.87", "0.25"],
      "T23.4: P(same) = cos^2(a - b) = cos^2(π/6) = 0.75. 0.87 is cos(π/6), the amplitude-like value without squaring.",
      "Lesson 23 T23.4"),
    Q("qc-L500-006", 23, "debugging", 2,
      "A student checks normalisation and this prints 0.0 for a perfectly normalised state. What is wrong?",
      ["np.dot skips the complex conjugate; use np.vdot",
       "The state is not normalised: it should be divided by 2, not √2",
       "Complex amplitudes cannot be stored in numpy arrays",
       "abs() must be applied before the dot product, not after"],
      "np.dot(psi, psi) computes 1/2 + (i)^2/2 = 0. The bra must be conjugated: np.vdot(psi, psi) = 1/2 + 1/2 = 1 (lesson 23 misconceptions).",
      "Lesson 23 concept note",
      code="""import numpy as np

psi = np.array([1, 1j]) / np.sqrt(2)
print(round(abs(np.dot(psi, psi)), 4))"""),
    Q("qc-L500-007", 23, "concept", 2,
      "Which two-qubit state is a product state (not entangled)?",
      ["(|00> + |01> + |10> + |11>)/2", "(|00> + |11>)/√2", "(|01> - |10>)/√2", "(|00> + i|11>)/√2"],
      "(|00> + |01> + |10> + |11>)/2 = |+> ⊗ |+>; its amplitude matrix [[1, 1], [1, 1]]/2 has rank 1. The other three have rank-2 amplitude matrices; a phase i on |11> does not remove entanglement.",
      "Lesson 23 problem P4"),
    Q("qc-L500-008", 23, "scenario", 2,
      "A colleague models a 'leaky' gate by multiplying state vectors by M = [[1, 1], [0, 1]]. What is the decisive objection?",
      ["M is not unitary: |1> becomes a vector of norm √2",
       "M is not Hermitian, and every quantum gate must be Hermitian",
       "M has determinant 1, so it cannot change the state at all",
       "M is invertible, but quantum gates must be non-invertible to model leakage"],
      "Closed-system evolution must be unitary (T23.1). Many valid gates are not Hermitian (e.g. the S gate), and noise is modelled with density-matrix channels, not arbitrary matrices.",
      "Lesson 23 problem P9"),
    Q("qc-L500-009", 23, "code-reading", 3,
      "What does this snippet print?",
      ["0.8536", "0.9239", "0.5", "0.1464"],
      "It measures |Φ+> at a = 0 and b = π/8 and sums P(00) + P(11) = cos^2(π/8) = 0.8536 (T23.4). 0.9239 is cos(π/8) without squaring; 0.1464 is P(different).",
      "Lesson 23 T23.4",
      code="""import numpy as np
from qsim import statevector as sv

bell = sv.run(2, [sv.h(0), sv.cx(0, 1)])
a, b = 0.0, np.pi / 8
out = sv.run(2, [(sv.ry(-2 * a), 0, ()), (sv.ry(-2 * b), 1, ())], bell)
p = np.abs(out) ** 2
print(round(float(p[0] + p[3]), 4))"""),

    # ---------------- lesson 24: quantum information basics ----------------
    Q("qc-L500-010", 24, "concept", 2,
      "A CNOT with a blank |0> target copies |0> and |1> perfectly. Why does this not contradict the no-cloning theorem?",
      ["|0> and |1> are orthogonal; only non-orthogonal states cannot be cloned",
       "No-cloning only applies to systems of three or more qubits",
       "The CNOT is not unitary, so the theorem does not apply to it",
       "No-cloning only forbids copying entangled states, not single-qubit states"],
      "From <ψ|φ> = <ψ|φ>^2, clonable pairs must have overlap 0 or 1 (T24.1). Orthogonal basis states are fine; |+> is turned into a Bell state instead of |+>|+>.",
      "Lesson 24 T24.1"),
    Q("qc-L500-011", 24, "concept", 2,
      "Immediately after Alice's Bell measurement in teleportation, before her two bits arrive, what is Bob's reduced state?",
      ["I/2, whatever |ψ> was", "|ψ> exactly", "|ψ> up to a known Pauli correction", "|0>, until the corrections are applied"],
      "Averaged over Alice's four equally likely outcomes, Bob holds (1/4)Σ X^x Z^z|ψ><ψ|Z^z X^x = I/2 (T24.2, T24.4). 'Up to a Pauli' is true only once he knows which Pauli, i.e. after the bits arrive.",
      "Lesson 24 T24.2"),
    Q("qc-L500-012", 24, "concept", 2,
      "Alice teleports |ψ> = 0.6|0> + 0.8|1>. How are her four Bell-measurement outcomes distributed?",
      ["0.25 each, for any |ψ>", "0.36 and 0.64 split over the outcomes",
       "0.5 each for two outcomes, 0 for the other two", "Weighted towards Ψ- because |β| > |α|"],
      "Each branch of the teleportation identity is (1/2) × a unit vector, so each outcome has probability 1/4 for every |ψ> (T24.2). That is why the outcomes reveal nothing about |ψ>.",
      "Lesson 24 T24.2"),
    Q("qc-L500-013", 24, "code-reading", 3,
      "This Deutsch-Jozsa snippet uses the 3-bit parity function. What does it print?",
      ["0.0 7", "1.0 0", "0.5 7", "0.0 0"],
      "Parity is balanced, so P(000) = 0 (T24.3); the phase pattern (-1)^{x·111} is exactly H^3|111>, so the output is |111> = index 7 with certainty.",
      "Lesson 24 T24.3",
      code="""import numpy as np
from qsim import statevector as sv

n = 3
f = [0, 1, 1, 0, 1, 0, 0, 1]                    # parity of x
hn = sv.unitary(n, [sv.h(q) for q in range(n)])
state = hn @ np.diag([(-1.0) ** v for v in f]) @ hn[:, 0]
print(round(float(abs(state[0]) ** 2), 4), int(np.argmax(abs(state))))"""),
    Q("qc-L500-014", 24, "calculation", 2,
      "For |ψ> = √0.9|00> + √0.1|11>, what is the purity Tr(ρ_A^2) of the first qubit's reduced state?",
      [str(PURITY), "0.9", "1.0", "0.5"],
      "ρ_A = diag(0.9, 0.1), so Tr ρ_A^2 = 0.81 + 0.01 = 0.82 (T24.4). 1.0 is the purity of the global pure state; 0.5 would need maximal entanglement.",
      "Lesson 24 T24.4"),
    Q("qc-L500-015", 24, "concept", 2,
      "|+><+| and I/2 have the same diagonal (1/2, 1/2). What distinguishes them physically?",
      ["Coherences: after H, |+> always gives 0; I/2 still gives 50/50",
       "Nothing: equal diagonals mean the two density matrices describe the same state",
       "I/2 has trace 1 but |+><+| has trace 2",
       "|+><+| is a mixed state and I/2 is a pure state"],
      "Coherences (off-diagonals) encode relative phase; X-basis measurement reveals them. I/2 is the maximally mixed state (purity 0.5), |+><+| is pure (purity 1).",
      "Lesson 24 concept note"),
    Q("qc-L500-016", 24, "scenario", 2,
      "A team wants to debug a long quantum program by 'saving a copy' of a register mid-circuit, then continuing. What should you advise?",
      ["Save the circuit, not the state: re-run to the checkpoint and measure statistics",
       "Use a CNOT fan-out to copy each qubit into a spare register",
       "Measure the register, store the bits and reload them later as the same quantum state",
       "Use teleportation to keep one copy and send another to the debugger"],
      "No-cloning (T24.1) rules out copies; measuring collapses the state; teleportation moves rather than copies. Re-preparation from the circuit is the standard debugging pattern.",
      "Lesson 24 T24.1"),
    Q("qc-L500-017", 24, "debugging", 3,
      "This teleportation simulation prints [1.0, 0.0, 0.0, 1.0] for |ψ> = 0.6|0> + 0.8|1>. What is the bug?",
      ["The X and Z corrections are attached to the wrong measured qubits",
       "The Bell pair between q1 and q2 is prepared incorrectly",
       "Z must be applied before X, otherwise the fidelity drops to 0",
       "|ψ> is not normalised, so two branches have zero probability"],
      "X must follow Alice's q1 outcome and Z her q0 outcome (T24.2). Order of X and Z only changes a global phase. The two outcomes needing exactly one correction get the wrong one and fidelity 0.",
      "Lesson 24 T24.2",
      code="""import itertools
import numpy as np
from qsim import statevector as sv

psi = np.array([0.6, 0.8])
start = np.kron([1, 0, 0, 0], psi)                 # q2 = q1 = |0>, q0 = psi
t = sv.run(3, [sv.h(1), sv.cx(1, 2), sv.cx(0, 1), sv.h(0)], start).reshape(2, 2, 2)
fids = []
for m0, m1 in itertools.product((0, 1), repeat=2):
    bob = t[:, m1, m0] / np.linalg.norm(t[:, m1, m0])
    if m0: bob = sv.X @ bob
    if m1: bob = sv.Z @ bob
    fids.append(round(float(abs(np.vdot(psi, bob)) ** 2), 4))
print(fids)"""),
    Q("qc-L500-018", 24, "concept", 2,
      "Superdense coding sends 2 classical bits by transmitting 1 qubit. Why does this not exceed what one qubit can carry?",
      ["The e-bit shared in advance pays for the second bit",
       "It does exceed the limit; quantum channels have unlimited classical capacity",
       "The two bits are only correct with probability 1/2 each",
       "Bob must also receive Alice's measurement results over a classical channel"],
      "Entanglement is consumed as a resource (T24.2b). Without the pre-shared e-bit, one qubit transmits at most one classical bit (Holevo's bound, stated in the lesson without proof).",
      "Lesson 24 T24.2"),

    # ---------------- lesson 25: algorithms and complexity ----------------
    Q("qc-L500-019", 25, "calculation", 2,
      "Grover search over N = 256 items with one marked item. What are the optimal iteration count floor(π/(4θ)) and its success probability?",
      [f"k = {K256}, P = {P256}", f"k = {K256 + 1}, P = {P256_13}", "k = 16, P = 1.0", "k = 128, P = 1.0"],
      "sin θ = 1/16, k = floor(π/(4θ)) = 12, P = sin^2(25θ) ≈ 0.9999 (T25.1). k = 16 is √N without the π/4; k = 128 is the classical average.",
      "Lesson 25 T25.1"),
    Q("qc-L500-020", 25, "concept", 2,
      "Why does running Grover's algorithm for many more iterations than (π/4)√N make success *less* likely?",
      ["Each iteration is a fixed rotation by 2θ, which turns past the target",
       "Noise accumulates, and the ideal algorithm itself would keep improving",
       "The oracle stops marking the item after the first √N queries",
       "Amplitudes keep growing until they exceed 1 and are renormalised"],
      "G = D·O is a rotation (T25.1); P_k = sin^2((2k+1)θ) is periodic in k. For N = 64, P is 0.9966 at k = 6 and 0.0001 at k = 12, even with perfect hardware.",
      "Lesson 25 T25.1"),
    Q("qc-L500-021", 25, "code-reading", 2,
      "This snippet evaluates the phase-estimation outcome distribution for t = 3 counting qubits. What does it print?",
      ["2 0.5775", "3 0.5775", "2 1.0", "0 0.3"],
      "φ·8 = 2.4, so the nearest outcome is m = 2 with P = 0.5775 ≥ 4/π^2 (T25.3). P = 1.0 would need φ·2^t to be an integer.",
      "Lesson 25 T25.3",
      code="""import numpy as np

phi, t = 0.3, 3
T = 2 ** t
p = [abs(sum(np.exp(2j * np.pi * k * (phi - m / T)) for k in range(T))) ** 2 / T ** 2
     for m in range(T)]
best = int(np.argmax(p))
print(best, round(p[best], 4))"""),
    Q("qc-L500-022", 25, "calculation", 2,
      "Shor's reduction for N = 15 with a = 7: what are the order r and the factors obtained from gcd(a^{r/2} ± 1, N)?",
      ["r = 4; factors 3 and 5", "r = 2; factors 3 and 5", "r = 4; factors 7 and 15", "r = 3; no factor (r is odd)"],
      "7^1..7^4 mod 15 = 7, 4, 13, 1, so r = 4; 7^2 = 49 ≡ 4, gcd(3, 15) = 3 and gcd(5, 15) = 5 (T25.4).",
      "Lesson 25 T25.4"),
    Q("qc-L500-023", 25, "concept", 3,
      "Which statement about BQP is accurate?",
      ["Factoring is in BQP; NP-complete problems probably are not",
       "BQP equals NP, as Shor's algorithm showed",
       "BQP is contained in P because quantum circuits can be simulated",
       "BQP requires zero error, unlike the classical class BPP"],
      "P ⊆ BPP ⊆ BQP ⊆ PSPACE; factoring ∈ BQP (T25.4) but is not known to be NP-complete, and the BBBV lower bound suggests no generic exponential speed-up for NP. BQP allows error 1/3.",
      "Lesson 25 concept note"),
    Q("qc-L500-024", 25, "debugging", 2,
      "A student's Grover loop prints '0.1374 0.1288' (total probability, marked-item probability). What is the bug?",
      ["The diffusion step is missing the factor 2: it must be 2·mean - a_i",
       "The oracle should flip the sign of every unmarked amplitude instead",
       "Three iterations is too many for N = 16; the state has overshot",
       "The initial state must be |0...0>, not the uniform superposition"],
      "a_i -> mean - a_i is not unitary, so the norm shrinks (total probability 0.1374 instead of 1). Inversion about average is 2|s><s| - I (T25.1, reading 1). Overshoot would keep the total at 1.",
      "Lesson 25 T25.1",
      code="""import numpy as np

N, marked = 16, 5
psi = np.full(N, 1 / np.sqrt(N))
for _ in range(3):
    psi[marked] *= -1
    psi = psi.mean() - psi          # diffusion step
print(round(float(np.sum(psi ** 2)), 4), round(float(psi[marked] ** 2), 4))"""),
    Q("qc-L500-025", 25, "scenario", 3,
      "A vendor claims an exponential quantum speed-up for regression on your 10^9-row table. Which question exposes the most likely hidden cost first?",
      ["What do loading the data and the best classical baseline cost?",
       "How many qubits does the device have, and how many of them are connected?",
       "Which programming language is the quantum SDK written in?",
       "Is the speed-up exponential in the number of rows or in the number of columns?"],
      "Loading N numbers costs ~N operations and output is one sample; dequantized classical algorithms can match such claims given the same access (Preskill 2018 note on Tang). Qubit counts matter less than the input model.",
      "Lesson 25 concept note"),
    Q("qc-L500-026", 25, "calculation", 2,
      "Order finding for N = 15, a = 7 with t = 8 measures m = 192. Using continued fractions with denominator <= 15, what order do you obtain?",
      ["r = 4", "r = 3", "r = 192", "r = 2"],
      "192/256 = 3/4 exactly, so the denominator gives r = 4 (check 7^4 mod 15 = 1). m = 128 would give 1/2, a divisor of r that fails the check (T25.4).",
      "Lesson 25 T25.4"),
    Q("qc-L500-027", 25, "concept", 2,
      "The n-qubit QFT uses O(n^2) gates while an FFT on 2^n numbers needs about n·2^n operations. Why is this not a faster general-purpose Fourier transform?",
      ["Amplitudes cannot be read out; one measurement gives one index, and loading costs ~2^n",
       "The QFT circuit is only approximately unitary",
       "The QFT computes a different transform from the DFT",
       "Controlled-phase gates are exponentially slower than classical floating-point multiplications"],
      "T25.2: the QFT is exactly the unitary DFT, but it acts on amplitudes. It helps only inside algorithms (phase estimation, Shor) where one measured outcome carries the answer.",
      "Lesson 25 T25.2"),

    # ---------------- lesson 26: ethics ----------------
    Q("qc-L500-028", 26, "calculation", 1,
      "Mosca's inequality: data must stay secret for X = 7 years, migration takes Y = 5 years, and a CRQC is assumed in Z = 10 years. What follows?",
      ["At risk: X + Y = 12 > 10, exposed for 2 years", "Safe: X = 7 < Z = 10",
       "At risk: Y + Z = 15 > X, exposed for 8 years", "Safe: X + Y = 12 is less than 2Z = 20"],
      "If X + Y > Z, data protected today is still secret-sensitive when it becomes decryptable; here by 12 - 10 = 2 years. Comparing X with Z alone ignores migration time.",
      "Lesson 26 problem P1"),
    Q("qc-L500-029", 26, "concept", 1,
      "What does 'harvest now, decrypt later' mean?",
      ["Recording ciphertext now to decrypt it with a future quantum computer",
       "Breaking today's encryption with today's quantum computers",
       "Storing post-quantum keys now and deploying them later",
       "Encrypting data with quantum key distribution so it can be decrypted later"],
      "HNDL is why migration is urgent for long-lived secrets even though no CRQC exists yet (NIST IR 8547; lesson 26).",
      "Lesson 26 concept note"),
    Q("qc-L500-030", 26, "scenario", 2,
      "A hospital board asks whether to spend this year's IT budget on an emergency 'quantum-proofing' contract after a start-up's press release. What is the professional recommendation?",
      ["Plan a migration: inventory first, then hybrid ML-KEM for long-lived data",
       "Do nothing until a quantum computer factors RSA-2048 publicly",
       "Sign the emergency contract, since the press release proves the risk is immediate",
       "Switch all symmetric encryption to longer keys and ignore public-key algorithms"],
      "The risk is real because of HNDL and long data lifetimes, not because of the press release; NCSC asks for discovery and a plan by 2028, NIST deprecates vulnerable public-key algorithms after 2030 (lesson 26 case model answer).",
      "Lesson 26 caseStudy"),
    Q("qc-L500-031", 26, "concept", 2,
      "Which sequence correctly summarises the 2019 'quantum supremacy' comparison?",
      ["10,000 years claimed; IBM argued days; 15 GPU-hours in 2022",
       "Claimed 10,000 years classically; confirmed by every later study",
       "Claimed 200 seconds classically; the quantum device took 10,000 years",
       "Claimed 15 hours classically; later raised to 10,000 years"],
      "Google's blog: 200 s vs 10,000 years; Pednault et al.: 'a matter of days'; Pan, Chen and Zhang: ~15 hours on 512 GPUs. Advantage claims are relative to a moving classical baseline.",
      "Lesson 26 concept note"),
    Q("qc-L500-032", 26, "concept", 2,
      "Under the EU dual-use regime's General Technology Note, which kind of information is excluded from technology controls?",
      ["Information 'in the public domain' and 'basic scientific research'",
       "All software written in open-source languages",
       "Any technology shared with universities",
       "Technology for quantum computers with fewer than 100 qubits"],
      "Delegated Regulation (EU) 2025/2003, Annex I, General Technology Note. Hardware and unpublished production technology can still require authorisation.",
      "Lesson 26 caseStudy frameworks"),
    Q("qc-L500-033", 26, "scenario", 3,
      "A lab with international students wants to release an open-source error-correction decoder and tune it on a collaborator's processor abroad. What is the right first step?",
      ["Ask compliance to classify it first; do not exclude students by nationality",
       "Bar all non-citizen students from the project to be safe",
       "Publish everything immediately, because export controls never apply to universities",
       "Move the work to a personal laptop so institutional rules do not apply"],
      "Publication and basic research are often excluded, but transfers of unpublished technology can be (deemed) exports; ACM 2.3 asks you to know the rules and ACM 1.4 forbids pre-emptive discrimination.",
      "Lesson 26 caseStudy"),
    Q("qc-L500-034", 26, "concept", 1,
      "Which ACM Code principle most directly requires disclosing a benchmark's weak classical baseline in a press release?",
      ["1.3 Be honest and trustworthy", "1.6 Respect privacy",
       "2.8 Access computing resources only when authorized", "3.6 Use care when modifying or retiring systems"],
      "1.3 asks for full disclosure of capabilities and limitations and forbids misleading claims; IEEE 7.8 item 5 adds 'honest and realistic in stating claims or estimates'.",
      "ACM Code of Ethics 1.3"),
    Q("qc-L500-035", 26, "code-reading", 1,
      "This helper computes how many years of a record's required secrecy fall after a CRQC appears. What does it print?",
      ["9", "11", "0", "20"],
      "Secrecy is needed until 2027 + 20 = 2047; a CRQC in 2038 leaves 2047 - 2038 = 9 years exposed (harvested ciphertext can be decrypted then).",
      "Lesson 26 problem P2",
      code="""def exposed_years(captured, secrecy_years, crqc_year):
    return max(0, captured + secrecy_years - crqc_year)

print(exposed_years(2027, 20, 2038))"""),
    Q("qc-L500-036", 26, "design", 3,
      "Which migration design best addresses both HNDL and future algorithm changes?",
      ["Hybrid (classical + ML-KEM) behind one interface, by data lifetime",
       "Replace RSA with longer RSA keys everywhere at once",
       "Wait for quantum key distribution hardware before changing anything",
       "Hard-code ML-KEM-768 in every service so no classical algorithm remains"],
      "Hybrids protect against both a CRQC and an unexpected PQC weakness; one interface gives crypto agility (L400 #21, NIST IR 8547). Hard-coding repeats today's agility problem.",
      "Lesson 26; L400 #21"),

    # ---------------- lesson 27: reading seminar ----------------
    Q("qc-L500-037", 27, "code-reading", 2,
      "Grover described his diffusion step as 'inversion about average'. What does this check print?",
      ["True", "False", "[2.0, 0.0, 0.0, 0.0]", "0.25"],
      "a_i -> 2·mean(a) - a_i is exactly (2|s><s| - I)a, the reflection used in T25.1.",
      "Lesson 27 reading 1",
      code="""import numpy as np

a = np.array([0.5, -0.5, 0.5, 0.5])
s = np.full(4, 0.5)
D = 2 * np.outer(s, s) - np.eye(4)
print(bool(np.allclose(D @ a, 2 * a.mean() - a)))"""),
    Q("qc-L500-038", 27, "calculation", 1,
      "For N = 10^6 items and one marked item, how many Grover iterations does floor(π/(4θ)) prescribe?",
      [str(K1M), "1000", "500000", "1571"],
      "θ = asin(10^-3), floor(π/(4θ)) = 785 ≈ (π/4)·1000. 500,000 is Grover's classical figure for a 50% chance; 1571 is about twice the optimum and would overshoot.",
      "Lesson 27 problem P1"),
    Q("qc-L500-039", 27, "concept", 1,
      "How does Preskill (2018) define the NISQ era?",
      ["50 to a few hundred qubits, noisy, without error correction",
       "Any quantum computer that has demonstrated quantum supremacy",
       "Fault-tolerant machines with fewer than 1000 logical qubits",
       "Quantum annealers with thousands of qubits"],
      "Section 4.1 of the paper: 'intermediate scale' means 50 to a few hundred qubits; 'noisy' means imperfect control without error correction.",
      "Preskill 2018, section 4.1"),
    Q("qc-L500-040", 27, "concept", 2,
      "According to Preskill (2018), a quantum speed-up should be measured against what?",
      ["The best classical hardware and algorithm for the same task",
       "A single-core laptop running brute force",
       "The same quantum device running without noise",
       "The classical algorithm used in the original proposal, fixed for all time"],
      "He defines speed-up against the best classical hardware and algorithm and calls classical computing a moving target - the lesson 26 supremacy timeline is an example.",
      "Preskill 2018, section 6"),
    Q("qc-L500-041", 27, "concept", 2,
      "What happened to the exponential speed-up claimed for quantum recommendation systems, according to the note Preskill added?",
      ["Tang's classical algorithm matched it, so the exponential gap vanished",
       "It was confirmed experimentally on a 100-qubit device",
       "It was shown to require fault tolerance, but the speed-up remains exponential",
       "It was proven impossible because recommendation is NP-hard"],
      "The paper's footnote notes that Tang's classical algorithm returns recommendations in poly(k)·polylog(mn) time - a dequantization (lesson 25).",
      "Preskill 2018, section 6.7"),
    Q("qc-L500-042", 27, "calculation", 2,
      "In the simple model where a G-gate circuit succeeds with probability (1 - ε)^G, what is the success probability for ε = 0.002 and G = 500?",
      [str(NOISE), "0.9", "0.002", "0.6065"],
      "(1 - 0.002)^500 ≈ e^{-1} ≈ 0.3675: reliable circuit size is about 1/ε, the quantitative core of Preskill's NISQ argument. 0.6065 is e^{-0.5}.",
      "Lesson 27 problem P3"),
    Q("qc-L500-043", 27, "scenario", 2,
      "You want to put both readings in your team's course notes. What may you do?",
      ["Adapt Preskill (CC BY) with credit; link to Grover and quote only briefly",
       "Copy both papers in full, since both are free to read online without any login",
       "Use neither, since academic papers can never be quoted",
       "Copy Grover in full (arXiv is open) but only link to Preskill"],
      "Free to read is not free to copy: arXiv's licence grants distribution rights to arXiv, not to you; Quantum publishes under CC BY 4.0. ACM 1.5 asks you to respect licences.",
      "Lesson 27 problem P6"),
    Q("qc-L500-044", 27, "concept", 2,
      "What does Preskill (2018) say about quantum computers and NP-hard problems such as the travelling salesman problem?",
      ["Not efficiently for hard instances; search gets only a modest speed-up",
       "They solve them in polynomial time using Grover's algorithm",
       "They solve them efficiently once 100 qubits are available",
       "NP-hard problems are exactly the problems quantum computers are designed for"],
      "Section 3.1: quantum computers can speed up exhaustive search, but only modestly (citing Grover and BBBV), so NP-hard problems are likely quantumly hard too.",
      "Preskill 2018, section 3.1"),
]
