"""L500 lesson 25 data: Foundations III - algorithms and complexity. Built into content/L500.json by build_l500_json.py."""

LAB = "labs/L500/25-algorithms-and-complexity"

LESSON = {
    "id": "foundations-algorithms-and-complexity",
    "number": 25,
    "level": "L500",
    "title": "Foundations III: algorithms and complexity",
    "phase": "Theory & Rigour",
    "category": "foundations",
    "description": "Grover's success probability and ~(π/4)√N iterations, the QFT as a unitary, phase estimation, Shor's "
                   "reduction from factoring to order finding, BQP at undergraduate level, and why exponential speed-ups are rare.",
    "outcome": "You can derive Grover's sin^2((2k+1)θ) law and the optimal iteration count, prove the QFT is unitary and "
               "count its gates, derive the phase-estimation distribution and its 4/π^2 guarantee, explain Shor's "
               "classical reduction step by step, place BQP among P, BPP, NP and PSPACE, and critique speed-up claims.",
    "estimatedTime": "6-8 hours (reading 2 h, derivations and checks 2-3 h, problem set 2-3 h)",
    "prerequisites": [
        "lessons 23-24 (unitaries, tensor products, phase kickback, Deutsch-Jozsa)",
        "linear algebra: reflections and rotations in a plane, eigenvectors of a unitary (|λ| = 1)",
        "discrete maths: modular arithmetic, gcd and Euclid's algorithm, continued fractions (introduced here)",
        "complexity: big-O, polynomial vs exponential time, the classes P and NP",
        "geometric series; the inequality 2x/π <= sin x <= x on [0, π/2]",
    ],
    "learningObjectives": [
        "Derive Grover's success probability P_k = sin^2((2k+1)θ) from two reflections and evaluate the optimal number of iterations ~(π/4)√(N/M), including what happens when you overshoot.",
        "Prove that the quantum Fourier transform is unitary and explain why its circuit uses O(n^2) gates while the classical FFT on the same vector needs ~n 2^n operations.",
        "Derive the phase-estimation outcome distribution and prove the nearest estimate occurs with probability at least 4/π^2.",
        "Explain Shor's reduction from factoring to order finding, including when it fails and how continued fractions recover the order from a measured phase.",
        "Explain the definition of BQP, justify its place relative to P, BPP, NP and PSPACE, and critique claims of exponential quantum speed-up using the BBBV lower bound and the conditions under which speed-ups are known.",
    ],
    "glossary": [
        {"term": "oracle / query complexity", "meaning": "Cost measured in calls to a black-box f; lower bounds are provable in this model."},
        {"term": "Grover iterate G", "meaning": "D·O: oracle O flips marked amplitudes; diffusion D = 2|s><s| - I reflects about the uniform state."},
        {"term": "θ (Grover angle)", "meaning": "sin θ = sqrt(M/N), the initial overlap of |s> with the marked subspace."},
        {"term": "QFT", "meaning": "|j> -> (1/√N) Σ_k e^{2πi jk/N} |k>, the unitary DFT on n qubits (N = 2^n)."},
        {"term": "phase estimation", "meaning": "Given U and an eigenvector with U|u> = e^{2πiφ}|u>, outputs a t-bit estimate of φ."},
        {"term": "order r of a mod N", "meaning": "Smallest r >= 1 with a^r ≡ 1 (mod N), for gcd(a, N) = 1."},
        {"term": "continued fractions", "meaning": "Best rational approximations; recover s/r from m/2^t when 2^t >= N^2."},
        {"term": "BQP", "meaning": "Decision problems solvable by a uniform family of polynomial-size quantum circuits with error probability <= 1/3."},
        {"term": "BPP", "meaning": "The classical randomised analogue of BQP (polynomial time, error <= 1/3)."},
        {"term": "dequantization", "meaning": "A classical algorithm matching a claimed quantum speed-up once the same input assumptions are granted."},
    ],
    "theorems": [
        {
            "name": "T25.1 Grover success probability and optimal iterations",
            "statement": "Among N items with M marked, let sin θ = sqrt(M/N). After k Grover iterations on the uniform state, "
                         "the probability of measuring a marked item is P_k = sin^2((2k+1)θ). Choosing k = floor(π/(4θ)) gives "
                         "P_k >= 1 - M/N, and k ≈ (π/4)sqrt(N/M) for M << N. Any quantum algorithm needs Ω(sqrt(N/M)) queries "
                         "(BBBV 1997; Boyer et al. 1998).",
            "proof": r"""**Derivation.** Let $|w\rangle$ be the uniform superposition of the M marked items and $|r\rangle$ that of the N - M unmarked ones; they are orthonormal and
$|s\rangle = \sin\theta\,|w\rangle + \cos\theta\,|r\rangle$. Both operators keep the real plane span{|w>, |r>} invariant:
the oracle $O = I - 2|w\rangle\langle w|$ (on this plane) reflects about $|r\rangle$, and $D = 2|s\rangle\langle s| - I$ reflects about $|s\rangle$.
A product of two reflections whose mirrors meet at angle θ is a rotation by 2θ, so $G = DO$ rotates by $2\theta$ towards $|w\rangle$ and
$G^k|s\rangle = \sin((2k+1)\theta)|w\rangle + \cos((2k+1)\theta)|r\rangle$, giving $P_k = \sin^2((2k+1)\theta)$.
**Optimal k.** P_k = 1 needs $(2k+1)\theta = \pi/2$, i.e. $k = \pi/(4\theta) - 1/2$. With $k = \lfloor \pi/(4\theta)\rfloor$ we have $\pi/(4\theta) - 1 < k \le \pi/(4\theta)$, so
$|(2k+1)\theta - \pi/2| \le \theta$ and $P_k \ge \cos^2\theta = 1 - M/N$. Since $\theta \approx \sin\theta = \sqrt{M/N}$, $k \approx (\pi/4)\sqrt{N/M}$.
**Overshoot.** The rotation does not stop: at $k \approx \pi/(2\theta)$ the state is back near $|r\rangle$ (P ≈ 0). "More iterations is better" is false (L200 #8).
**Optimality (cited).** Bennett, Bernstein, Brassard and Vazirani (1997) prove that, relative to a random oracle, no quantum algorithm decides NP in time $o(2^{n/2})$;
Boyer, Brassard, Høyer and Tapp (1998) give the closed-form P_k above and show Grover is within a small constant of optimal. Proof idea (hybrid argument):
each query can move the state's dependence on the marked item by only $O(1/\sqrt N)$ in norm, so $\Omega(\sqrt N)$ queries are needed to separate N possibilities. ∎""",
            "check": f"{LAB}/theorems.py::T25.1",
        },
        {
            "name": "T25.2 The QFT is unitary and has an O(n^2) circuit",
            "statement": "F_{jk} = ω^{jk}/sqrt(N) with ω = e^{2πi/N} is unitary. For N = 2^n, F is implemented exactly by n Hadamards, "
                         "n(n-1)/2 controlled phase gates and floor(n/2) swaps.",
            "proof": r"""**Unitarity.** $(F^\dagger F)_{jk} = \frac1N\sum_{m=0}^{N-1}\omega^{-mj}\omega^{mk} = \frac1N\sum_{m}\omega^{m(k-j)}$. For $j = k$ every term is 1 and the sum is 1.
For $j \ne k$, $q = \omega^{k-j} \ne 1$ but $q^N = 1$, so the geometric series gives $\sum_m q^m = (1 - q^N)/(1 - q) = 0$. Hence $F^\dagger F = I$.
**Circuit (product formula).** Write $j = j_{n-1}\dots j_0$ in binary. Then
$F|j\rangle = \frac{1}{\sqrt N}\bigotimes_{l=1}^{n}\big(|0\rangle + e^{2\pi i\, j/2^l}|1\rangle\big)$ (expand $e^{2\pi i jk/N}$ over the bits of k). The phase $e^{2\pi i j/2^l}$ depends only on the
last l bits of j, i.e. on the binary fraction $0.j_{l-1}\dots j_0$. A Hadamard on qubit $j_{l-1}$ produces the first bit of that fraction; controlled phases $R_m = \mathrm{diag}(1, e^{2\pi i/2^m})$
from the lower qubits add the rest. Doing this from the top qubit down costs $n$ H gates and $(n-1) + (n-2) + \dots + 0 = n(n-1)/2$ controlled phases, and leaves the
output in reversed order, fixed by $\lfloor n/2\rfloor$ swaps. ∎

**What the O(n^2) does and does not buy.** The circuit transforms $2^n$ amplitudes with $O(n^2)$ gates, while an FFT on the same vector costs ~$n2^n$ operations.
But you cannot read the amplitudes out: measurement returns one k. The QFT is useful only inside algorithms whose output is a single, likely, informative k (periods, phases).""",
            "check": f"{LAB}/theorems.py::T25.2",
        },
        {
            "name": "T25.3 Phase estimation",
            "statement": "With t counting qubits, controlled-U^{2^j} gates and an inverse QFT, an eigenvector U|u> = e^{2πiφ}|u> yields outcome m "
                         "with probability P(m) = |(1/T) Σ_{k<T} e^{2πik(φ - m/T)}|^2, T = 2^t. If φT is an integer the outcome is exact; "
                         "otherwise the nearest m (|φ - m/T| <= 1/(2T)) occurs with probability at least 4/π^2 ≈ 0.405.",
            "proof": r"""**Derivation.** After Hadamards the counting register is $T^{-1/2}\sum_k|k\rangle$. Controlled-$U^{2^j}$ from counting qubit j multiplies $|k\rangle|u\rangle$ by
$\prod_j e^{2\pi i\varphi k_j 2^j} = e^{2\pi i\varphi k}$ (phase kickback; $|u\rangle$ is unchanged). So the register holds $T^{-1/2}\sum_k e^{2\pi i\varphi k}|k\rangle$, which for $\varphi = m/T$
is exactly $F|m\rangle$ (T25.2). Applying $F^\dagger$: the amplitude of $|m\rangle$ is $\frac1T\sum_k e^{2\pi i k(\varphi - m/T)}$.
**Exact case.** If $\varphi T = m$, every term is 1: $P(m) = 1$.
**Bound.** Let $\delta = \varphi - m/T$ with $0 < |\delta| \le 1/(2T)$. Summing the geometric series, $|a_m| = \frac{|\sin(\pi T\delta)|}{T|\sin(\pi\delta)|}$.
Because $\pi T|\delta| \le \pi/2$, concavity gives $|\sin(\pi T\delta)| \ge 2T|\delta|$, and $|\sin(\pi\delta)| \le \pi|\delta|$. Therefore $|a_m| \ge \frac{2T|\delta|}{T\pi|\delta|} = 2/\pi$ and $P(m) \ge 4/\pi^2$. ∎

Using t = n + O(log(1/ε)) qubits makes the estimate accurate to n bits with probability ≥ 1 - ε (Cleve, Ekert, Macchiavello & Mosca 1998 present
Deutsch-Jozsa, Shor and phase estimation in this one framework). Phase estimation is the engine of Shor's algorithm and of quantum chemistry energy estimation
(the fault-tolerant alternative to the VQE of L300 #15).""",
            "check": f"{LAB}/theorems.py::T25.3",
        },
        {
            "name": "T25.4 Shor's reduction: factoring reduces to order finding",
            "statement": "Let N be odd, composite and not a prime power, and gcd(a, N) = 1 with order r. If r is even and a^{r/2} ≢ -1 (mod N), "
                         "then gcd(a^{r/2} - 1, N) is a nontrivial factor of N. For a chosen uniformly at random the condition holds with "
                         "probability at least 1/2 (Shor 1997). Order finding is phase estimation of U_a|y> = |ay mod N>, whose eigenphases are s/r; "
                         "with 2^t >= N^2, continued fractions recover s/r from the measured m/2^t.",
            "proof": r"""**Reduction.** $a^r \equiv 1$ means $N \mid (a^{r/2}-1)(a^{r/2}+1)$. N does not divide $a^{r/2}-1$ (otherwise the order would be at most r/2), and by assumption
N does not divide $a^{r/2}+1$. So N shares a factor with each bracket without dividing either: $1 < \gcd(a^{r/2}-1, N) < N$. Euclid's algorithm computes it in polynomial time.
**Success probability (cited).** Writing $N = \prod p_i^{e_i}$ with k ≥ 2 distinct odd primes, the Chinese remainder theorem splits a random a into independent random residues, and the
condition fails with probability at most $2^{1-k} \le 1/2$ (Shor 1997, factoring section; the check counts the fraction exactly for N = 15, 21, 33, 35, 91).
**Order finding.** $U_a$ permutes the residues, so it is unitary; its eigenvectors $|u_s\rangle = r^{-1/2}\sum_{k<r} e^{-2\pi i sk/r}|a^k \bmod N\rangle$ have eigenvalues $e^{2\pi i s/r}$, and
$|1\rangle = r^{-1/2}\sum_s |u_s\rangle$, so phase estimation on input $|1\rangle$ returns a good estimate of $s/r$ for a uniformly random s. If $|s/r - m/2^t| \le 1/(2\cdot 2^t) \le 1/(2r^2)$
then s/r is a convergent of the continued fraction of $m/2^t$ (Legendre's theorem), so the denominator gives r (or a divisor of r when gcd(s, r) > 1; repeat and take the lcm).
**Cost.** Modular exponentiation dominates: $O(n^3)$ gates for an n-bit N with schoolbook arithmetic, so factoring is in BQP, whereas no polynomial-time classical algorithm is known. ∎

**Proportion check.** The worked example N = 15, a = 7 gives r = 4 and outcomes 0, 64, 128, 192 out of 256 with probability 1/4 each; 64 and 192 give r = 4 directly, so one run
succeeds with probability 1/2. This is also why "factoring 15" demonstrations prove little: the hard part (modular exponentiation for 2048-bit N) is absent (L400 #19).""",
            "check": f"{LAB}/theorems.py::T25.4",
        },
    ],
    "problemSet": [
        {"id": "qc-L500-25-P1", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "Grover search with N = 1024 and one marked item. Give θ, the optimal k = floor(π/(4θ)), P_k, and P after 26 and 50 iterations.",
         "solution": "θ = asin(1/32) = 0.03126 rad. k = floor(π/(4θ)) = 25, P_25 = sin^2(51θ) = 0.9995. P_26 = 0.9927 (just past the peak) and P_50 = 0.0002 (the state has rotated back to the unmarked direction). Classical exhaustive search needs up to 1023 queries, 512 on average."},
        {"id": "qc-L500-25-P2", "type": "calculation", "difficulty": 2, "marks": 4,
         "problem": "Same N = 1024 but M = 4 marked items. Give the optimal k and P_k, and P if you mistakenly run the M = 1 count of 25 iterations.",
         "solution": "sin θ = sqrt(4/1024) = 1/16. k = floor(π/(4θ)) = 12 (half of the M = 1 count, since k ∝ sqrt(N/M)), P_12 = 0.9999. Running 25 iterations overshoots badly: P_25 = 0.0023. Unknown M is handled by randomised iteration counts or quantum counting (Boyer et al.)."},
        {"id": "qc-L500-25-P3", "type": "derivation", "difficulty": 2, "marks": 6,
         "problem": "Show that D = 2|s><s| - I and the oracle O restricted to span{|w>, |r>} are reflections, and derive P_k = sin^2((2k+1)θ).",
         "solution": "D|s> = |s> and D|s⊥> = -|s⊥> for |s⊥> ⊥ |s> in the plane, so D is the reflection about |s>; O|r> = |r>, O|w> = -|w>, so O is the reflection about |r>. Composing reflections about lines at angle θ gives a rotation by 2θ; starting at angle θ from |r>, after k steps the angle is (2k+1)θ and the |w> amplitude is sin((2k+1)θ) (T25.1)."},
        {"id": "qc-L500-25-P4", "type": "proof", "difficulty": 2, "marks": 5,
         "problem": "Prove that the N x N matrix F_jk = ω^{jk}/sqrt(N), ω = e^{2πi/N}, is unitary.",
         "solution": "(F†F)_jk = (1/N) Σ_m ω^{m(k-j)}. For j = k this is 1. For j ≠ k, q = ω^{k-j} ≠ 1 and q^N = 1, so Σ_{m=0}^{N-1} q^m = (1 - q^N)/(1 - q) = 0. Hence F†F = I (T25.2); the check confirms it numerically for N up to 256."},
        {"id": "qc-L500-25-P5", "type": "calculation", "difficulty": 2, "marks": 5,
         "problem": "Phase estimation with t = 3 counting qubits on an eigenphase φ = 1/3. Give the probability of the most likely outcome m and of the second most likely. Verify the 4/π^2 bound.",
         "solution": "P(m) = |(1/8) Σ_k e^{2πik(1/3 - m/8)}|^2. The most likely is m = 3 (3/8 = 0.375) with P = 0.6878; next is m = 2 (0.25) with P = 0.1749. 0.6878 >= 4/π^2 = 0.4053 as T25.3 guarantees. Estimate: φ ≈ 0.375 with t = 3; more counting qubits sharpen it."},
        {"id": "qc-L500-25-P6", "type": "calculation", "difficulty": 2, "marks": 5,
         "problem": "Run Shor's classical reduction by hand for N = 21, a = 2: find r, check the conditions, and extract the factors.",
         "solution": "Powers of 2 mod 21: 2, 4, 8, 16, 11, 1, so r = 6 (even). a^{r/2} = 2^3 = 8 ≢ -1 = 20 (mod 21). gcd(8 - 1, 21) = 7 and gcd(8 + 1, 21) = 3, so 21 = 7 × 3 (T25.4)."},
        {"id": "qc-L500-25-P7", "type": "calculation", "difficulty": 3, "marks": 5,
         "problem": "Order finding for N = 21, a = 2 with t = 9 counting qubits returns m = 427. Use continued fractions (denominator <= N) to recover r, and check it.",
         "solution": "427/512 = 0.83398...; its continued fraction convergents with denominator <= 21 end at 5/6 (Fraction(427, 512).limit_denominator(21) = 5/6). So r = 6; check 2^6 mod 21 = 1. If the measured m had given s/r with gcd(s, r) > 1 (e.g. 2/6 = 1/3) the denominator 3 would fail the check, and you repeat. In the check one run succeeds with P = 0.3084."},
        {"id": "qc-L500-25-P8", "type": "calculation", "difficulty": 1, "marks": 3,
         "problem": "A dense state-vector simulator stores 2^n complex128 amplitudes (16 bytes each). How much memory does n = 40 need? Reconcile this with the theorem BQP ⊆ PSPACE.",
         "solution": "2^40 × 16 B = 17,592,186,044,416 bytes = 16 TiB (17.6 TB). BQP ⊆ PSPACE does not say simulation is cheap in time: one amplitude <x|C|0> can be computed as a sum over all paths through the circuit (a Feynman path sum) reusing polynomial memory for each path, at exponential time cost. Memory and time trade off; neither is polynomial in general."},
        {"id": "qc-L500-25-P9", "type": "essay", "difficulty": 3, "marks": 10,
         "problem": "Essay (600-900 words): 'Why are exponential quantum speed-ups rare?' Use the BBBV lower bound, the structure exploited by Shor's algorithm, the read-in/read-out problem, dequantization, and constant-factor overheads from fault tolerance. End with a checklist for evaluating a speed-up claim.",
         "solution": "Model answer outline: (1) Unstructured problems: BBBV proves Ω(sqrt N) queries, so search gives at most a quadratic gain, which large constant overheads (L400 #19: physical qubits, T-gates, code cycles) can erase. (2) Exponential gains come from structure, notably hidden periodicity (Shor: order finding via QFT) and simulation of quantum systems; NP-complete problems are not known to have such structure and BQP is not believed to contain NP. (3) Input/output: loading N classical numbers costs ~N operations and measurement returns one sample, so linear-algebra 'speed-ups' assume oracles (e.g. QRAM) that may be the real cost. (4) Dequantization: given the same sampling access, classical algorithms have matched some claimed quantum machine-learning speed-ups (Preskill 2018 cites Tang 2018 as an example). (5) Moving targets: classical simulation improved from the 2019 '10,000 years' estimate to a 15-hour GPU computation (lesson 26). Checklist: what is the problem and input model? Best classical baseline, same budget? Asymptotic or measured? Constant factors and error correction included? Is the output a useful answer or a sample? Rubric: argument 40, use of theorems 30, evidence 20, clarity 10."},
        {"id": "qc-L500-25-P10", "type": "calculation", "difficulty": 2, "marks": 4,
         "problem": "BQP allows error 1/3. A BQP algorithm is run 15 independent times and the majority answer is taken. Compute the error probability exactly, and explain why the class is unchanged if 1/3 is replaced by 1/4 or 0.49.",
         "solution": "Error = P(at most 7 of 15 runs correct) with p = 2/3 = Σ_{k=0}^{7} C(15,k)(2/3)^k(1/3)^{15-k} = 0.0882. By the Chernoff bound the error falls exponentially in the number of repetitions for any constant gap from 1/2, so any error bound 1/2 - c (constant c > 0) gives the same class after polynomially many repetitions."},
    ],
    "rubric": [
        {"criterion": "Derivation correctness", "excellent": "Each identity justified (reflections, geometric series, inequalities); limits of validity stated.", "adequate": "Correct results, a justification missing.", "inadequate": "Formula quoted, not derived.", "weight": 35},
        {"criterion": "Complexity reasoning", "excellent": "Distinguishes query vs gate complexity, asymptotic vs measured, proven vs believed (e.g. BQP vs NP).", "adequate": "Mostly correct use of classes.", "inadequate": "Claims 'quantum solves NP-complete problems' or equivalent.", "weight": 25},
        {"criterion": "Numerical evidence", "excellent": "Uses theorems.py output for every number; notes tolerances and seeds.", "adequate": "Numbers mostly traced to code.", "inadequate": "Numbers by hand or unexplained.", "weight": 20},
        {"criterion": "Critical evaluation (essay)", "excellent": "Weighs counter-evidence and classical baselines; ends with a usable checklist.", "adequate": "Balanced but generic.", "inadequate": "One-sided or hype-driven.", "weight": 20},
    ],
    "conceptNote": "content/concepts/L500/25-algorithms-and-complexity.md",
    "conceptSummary": "Grover is a rotation by 2θ per query: P_k = sin^2((2k+1)θ), best near (π/4)√(N/M), and provably no better than quadratic. The QFT is a unitary DFT built from O(n^2) gates; phase estimation reads an eigenphase with probability >= 4/π^2 of the nearest value. Shor reduces factoring to order finding, which is phase estimation plus continued fractions. BQP is bounded-error quantum polynomial time; exponential speed-ups need special structure and are rare.",
    "sources": [
        {"title": "Grover (1996), A fast quantum mechanical algorithm for database search, arXiv:quant-ph/9605043", "url": "https://arxiv.org/abs/quant-ph/9605043"},
        {"title": "Boyer, Brassard, Høyer, Tapp (1998), Tight bounds on quantum searching, arXiv:quant-ph/9605034", "url": "https://arxiv.org/abs/quant-ph/9605034"},
        {"title": "Bennett, Bernstein, Brassard, Vazirani (1997), Strengths and weaknesses of quantum computing, arXiv:quant-ph/9701001", "url": "https://arxiv.org/abs/quant-ph/9701001"},
        {"title": "Shor (1997), Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum computer, arXiv:quant-ph/9508027", "url": "https://arxiv.org/abs/quant-ph/9508027"},
        {"title": "Cleve, Ekert, Macchiavello, Mosca (1998), Quantum algorithms revisited, arXiv:quant-ph/9708016", "url": "https://arxiv.org/abs/quant-ph/9708016"},
        {"title": "IBM Quantum Learning - Grover's algorithm (J. Watrous)", "url": "https://quantum.cloud.ibm.com/learning/en/courses/fundamentals-of-quantum-algorithms/grover-algorithm/introduction"},
        {"title": "IBM Quantum Learning - Phase estimation and factoring (J. Watrous)", "url": "https://quantum.cloud.ibm.com/learning/en/courses/fundamentals-of-quantum-algorithms/phase-estimation-and-factoring/introduction"},
        {"title": "Preskill (2018), Quantum Computing in the NISQ era and beyond, Quantum 2, 79", "url": "https://quantum-journal.org/papers/q-2018-08-06-79/"},
    ],
    "seeAlso": [
        "quantum-computing L200 #8 Small Grover search: the iterations-vs-success curve that T25.1 derives in closed form.",
        "quantum-computing L200 #9 The QFT as a building block: the same H + controlled-phase + swap circuit proved unitary in T25.2.",
        "quantum-computing L300 #15 A hybrid variational loop (VQE) under shot noise: the NISQ alternative to phase-estimation energy estimation (T25.3).",
        "quantum-computing L400 #18 Benchmarking honestly against classical solvers: the practical side of 'why speed-ups are rare'.",
        "quantum-computing L400 #19 Resource estimation: logical vs physical qubits and feasibility: what Shor's O(n^3) gates cost on error-corrected hardware.",
        "quantum-computing L400 #21 Quantum and post-quantum: crypto inventory and migration plan: why T25.4 is the reason RSA and ECC must be replaced.",
    ],
    "next": "L500 #26 Ethics, society and professional responsibility: honest speed-up claims, harvest-now-decrypt-later and the duty to migrate, export controls and access.",
}
