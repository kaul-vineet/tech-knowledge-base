# Foundations III: algorithms and complexity

L200 ran Grover search and the QFT; L400 estimated what Shor's algorithm would cost. This note derives why those algorithms work, how much they can gain, and why large quantum speed-ups are the exception rather than the rule. Numbers come from `labs/L500/25-algorithms-and-complexity/theorems.py`.

## Definitions

- **Query complexity:** cost counted in calls to a black-box function. Lower bounds can be *proved* in this model, which is why so much theory uses it.
- **Grover angle:** with M marked items among N, sin θ = sqrt(M/N).
- **QFT:** the unitary |j> -> (1/√N) Σ_k e^{2πi jk/N}|k> on n qubits, N = 2^n.
- **Phase estimation:** given U and an eigenvector with U|u> = e^{2πiφ}|u>, produce a t-bit estimate of φ.
- **Order:** the smallest r with a^r ≡ 1 (mod N).
- **BQP:** decision problems solved by a uniform family of polynomial-size quantum circuits with error probability at most 1/3. Repetition and a majority vote shrink the error exponentially. With 15 runs it is already 0.0882 (problem P10).

## Key results

**Grover (T25.1).** In the plane spanned by the marked and unmarked superpositions, the oracle and the diffusion step are two reflections. Their product is a rotation by 2θ, so after k iterations P_k = sin^2((2k+1)θ). The best k is floor(π/(4θ)) ≈ (π/4)√(N/M), with P_k ≥ 1 - M/N. Simulation matches the formula to 10^-9: for N = 1024 the best k is 25 (P = 0.9995), and for N = 4096 it is 50 (P = 0.9999). Bennett, Bernstein, Brassard and Vazirani proved that no quantum algorithm does better than Ω(√N) for unstructured search, so the gain is quadratic, not exponential.

**QFT (T25.2).** The DFT matrix is unitary: off-diagonal entries of F†F are geometric series of roots of unity, which sum to zero. The circuit uses n Hadamards, n(n-1)/2 controlled phases and floor(n/2) swaps. For n = 5 that is 17 gates acting on 32 amplitudes, whereas an FFT needs about n·2^n = 160 operations. But measurement returns only one k, so the QFT helps only when one outcome carries the answer.

**Phase estimation (T25.3).** Controlled powers of U write the phase φ into the counting register as Σ_k e^{2πiφk}|k>. An inverse QFT turns this into a peak at m ≈ φ·2^t, with probability |(1/T) Σ_k e^{2πik(φ - m/T)}|^2. When φ·2^t is an integer the answer is exact. Otherwise the nearest m appears with probability at least 4/π^2 ≈ 0.405. Across every case tested, the smallest such probability is 0.4054.

**Shor's reduction (T25.4).** If the order r of a is even and a^{r/2} ≢ -1 (mod N), then gcd(a^{r/2} - 1, N) is a proper factor of N. A random a works with probability at least 1/2 (for N = 21 the check counts 6 of 11). Order finding is phase estimation of the permutation |y> -> |ay mod N>, whose eigenphases are s/r. Continued fractions then recover r from m/2^t, provided 2^t ≥ N^2.

## Intuition

- Grover is a **steady rotation**, not an accumulation. Keep turning and you pass the target: for N = 64, P is 0.9966 at k = 6 but 0.0001 at k = 12.
- The QFT is a **change of basis that makes periodicity visible**. A state with period r in the computational basis becomes peaks at multiples of N/r in the Fourier basis.
- Phase estimation is **interference used as a ruler**. Each counting qubit reads one binary digit of φ, and the inverse QFT lines the digits up.
- Shor's algorithm is **number theory plus one quantum subroutine**. Everything except order finding is classical and efficient.

## Worked example: factoring 21 with a = 2

1. Classically, gcd(2, 21) = 1, so continue.
2. Quantum order finding with t = 9 counting qubits (512 ≥ 441 = 21^2) gives a likely outcome m = 427.
3. Continued fractions: 427/512 ≈ 0.83398, and its best approximation with denominator ≤ 21 is 5/6. So r = 6, and indeed 2^6 mod 21 = 1.
4. r is even, and 2^3 = 8 ≢ 20 (mod 21). So gcd(7, 21) = 7 and gcd(9, 21) = 3, and 21 = 7 × 3.

In the check, one run recovers r = 6 with probability 0.3084. A failed run (for example a reading of 1/3) is detected by testing a^r ≡ 1 and is simply repeated.

## Where BQP sits

P ⊆ BPP ⊆ BQP ⊆ PSPACE. The last inclusion holds because a single amplitude can be computed as a sum over paths through the circuit, reusing polynomial memory, at exponential time cost. Factoring is in BQP but is not known to be in BPP. NP-complete problems are *not* believed to be in BQP; Preskill (2018) states the same expectation. A dense simulator for 40 qubits would need 2^40 × 16 bytes = 16 TiB. That cost is why classical simulation is hard, but not a proof that quantum computers are faster.

## Why exponential speed-ups are rare

1. **No structure, no exponential gain.** BBBV caps unstructured search at a quadratic speed-up, and large constant factors on error-corrected hardware can wipe that out (L400 #19).
2. **Known exponential gains rely on special structure:** hidden periodicity (Shor) and simulation of quantum systems are the main examples.
3. **Input and output bottlenecks.** Loading N classical numbers costs about N operations, and one measurement returns one sample. Preskill makes this point about quantum machine learning and QRAM.
4. **Dequantization.** After Preskill's paper was submitted, Tang found a classical algorithm matching the quantum recommendation-system runtime. He added a note saying the exponential speed-up was gone.
5. **Moving baselines.** Preskill defines speed-up against the best classical hardware *and* algorithm, which keep improving (lesson 26).

## Common misconceptions

- **"Quantum computers try all answers in parallel and pick the right one."** Measurement returns one outcome; only interference can make the right one likely.
- **"More Grover iterations are always better."** Overshooting rotates the state away from the target (P_25 = 0.0023 for N = 1024, M = 4).
- **"The QFT computes the Fourier transform of my data faster."** It transforms amplitudes you cannot read out; loading and reading data costs more than the speed-up.
- **"Shor's algorithm breaks all cryptography."** It breaks factoring and discrete-log based public-key schemes (RSA, ECC, Diffie-Hellman). Symmetric ciphers face only Grover's quadratic speed-up, and lattice-based schemes such as ML-KEM have no known efficient quantum attack.
- **"BQP contains NP."** This is not known and is widely believed false.

## Check yourself

Predict, then check with code: (1) the best k for N = 256, M = 1; (2) the gate count of a 6-qubit QFT; (3) whether a = 14 works for N = 15. For (3), first compute gcd(14, 15), then the order of 14, then test whether 14^{r/2} ≡ -1 (mod 15).
