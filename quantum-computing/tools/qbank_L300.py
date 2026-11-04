"""L300 question bank data (lessons 12-16). Correct option first; numbers computed with qsim and the lab modules."""
import math
import sys

import numpy as np

from qbank_common import Q, TOPIC, fmt
from qsim import density as dm
from qsim import statevector as sv

for _lab in ("12-noise-models", "13-error-mitigation", "14-qaoa-maxcut", "15-hybrid-vqe-loop"):
    sys.path.insert(0, str(TOPIC / "labs" / "L300" / _lab))
import mitigation_lab as ml  # noqa: E402
import noise_lab as nl  # noqa: E402
import qaoa_lab as ql  # noqa: E402
import vqe_lab as vl  # noqa: E402

BELL = nl.metrics(2, nl.NOISE)
GHZ3 = nl.metrics(3, nl.NOISE)
DEPOL_P1 = fmt(dm.probabilities(dm.run(1, [("depol", 0.1, (0,))]))[1], 4)
DAMP_P1 = fmt(dm.probabilities(dm.run(1, [sv.x(0), ("damp", 0.2, 0)]))[1], 4)
RO_11 = fmt((dm.readout_matrix(0.02, 0.04, 2) @ np.eye(4)[3])[3], 4)
TOL = fmt(4 * math.sqrt(BELL["success"] * (1 - BELL["success"]) / 2000), 4)

ZNE = [fmt(ml.exact_value(s), 4) for s in (1, 3, 5)]
_s = np.array([1.0, 3.0, 5.0])
W = [float(np.prod([sk / (sk - sj) for sk in _s if sk != sj])) for sj in _s]   # Lagrange weights at scale 0
RICH = fmt(np.dot(W, ZNE), 4)
LIN = fmt(np.polyval(np.polyfit(_s, ZNE, 1), 0), 4)
STD_GAIN = fmt(math.sqrt(sum(w * w for w in W)), 2)
FOLD5_CX = sum(1 for op in ml.folded(ml.mirror_ops(), 5) if op[2])
MIRROR_CX = sum(1 for op in ml.mirror_ops() if op[2])

MAXCUT, OPT_STRINGS = ql.brute_force()
CUT_01010 = int(ql.CUT[int("01010", 2)])
RATIO_UNIFORM = ql.ratio([0.0, 0.0])

E0 = fmt(vl.E0, 4)
_diag = np.real(np.diag(vl.H))
BEST_BASIS = format(int(np.argmin(_diag)), "02b")
BEST_BASIS_E = fmt(_diag.min(), 4)
FD_ERR = fmt(0.01 / (2 * 1e-3), 3)
SPSA_ERR = fmt(0.01 / (2 * 0.1), 3)
FD_EVALS_400, SPSA_EVALS = 2 * 400, 2

FLOOR_4000 = fmt(math.sqrt(2) / 2 / math.sqrt(4000), 4)
_weights, _train, _epochs = 2 * 2, 40, 60
TRAIN_EVALS = _epochs * _train * (1 + 2 * _weights)

L = []
# ---------------- Lesson 12: noise models ----------------
L += [
    Q("qc-L300-001", 12, "calculation", 2,
      "With the lab-12 NOISE model (p1 0.002, p2 0.02, damping 0.01, readout 0.02/0.04), what are the Bell pair's "
      "state fidelity and measurable success P('00') + P('11')?",
      [f"fidelity {BELL['fidelity']}, success {BELL['success']}", f"fidelity {BELL['success']}, success {BELL['fidelity']}",
       "fidelity 1.0, success 1.0", f"fidelity {GHZ3['fidelity']}, success {GHZ3['success']}"],
      "The density-matrix run gives fidelity 0.9719 and, after readout flips, success 0.925. Swapping them is "
      "tempting, but readout errors lower measured success without touching the state's fidelity.",
      "Lesson 12 expectedResults"),
    Q("qc-L300-002", 12, "concept", 2,
      "Why is the Bell pair's measured success lower than its state fidelity under the same noise model?",
      ["Readout flips act after the state is prepared", "Fidelity ignores the CX gate's depolarizing noise",
       "Success is computed from fewer shots than fidelity", "Amplitude damping only affects measured success"],
      "Fidelity <psi|rho|psi> describes the prepared state; readout errors then flip recorded bits, lowering only "
      "the measured success. Damping changes the state itself, so it lowers both.", "Lesson 12 checkYourself"),
    Q("qc-L300-003", 12, "code-reading", 2,
      "A depolarizing channel rho -> (1 - p) rho + p I/2 acts on |0>. What does this print?",
      [str(DEPOL_P1), "0.1", "0.9", "0.025"],
      "The I/2 part is a 50/50 mixture, so P(1) = p/2 = 0.05. Answering 0.1 treats depolarizing as a guaranteed flip "
      "with probability p.", "Lesson 12 simulatorVsReal (qsim density.py conventions)",
      code='''
from qsim import density as dm

rho = dm.run(1, [("depol", 0.1, (0,))])
print(round(float(dm.probabilities(rho)[1]), 4))
'''),
    Q("qc-L300-004", 12, "code-reading", 2,
      "|1> passes through amplitude damping (Kraus A0 = [[1,0],[0,sqrt(1-g)]], A1 = [[0,sqrt(g)],[0,0]]). What does "
      "this print?",
      [str(DAMP_P1), "0.2", "0.8944", "0.6"],
      "Damping moves population from |1> to |0> with probability gamma, leaving P(1) = 0.8. 0.8944 is sqrt(0.8), an "
      "amplitude rather than a probability.", "Lesson 12 code",
      code='''
from qsim import density as dm
from qsim import statevector as sv

rho = dm.run(1, [sv.x(0), ("damp", 0.2, 0)])
print(round(float(dm.probabilities(rho)[1]), 4))
'''),
    Q("qc-L300-005", 12, "code-reading", 2,
      "Each qubit has readout flips p01 = 0.02 (0 read as 1) and p10 = 0.04 (1 read as 0). Two qubits are truly in "
      "|11>. What does this print for P(recording '11')?",
      [str(RO_11), "0.96", "0.9604", "0.94"],
      "Each qubit is read correctly with probability 0.96, independently: 0.96^2 = 0.9216. 0.9604 uses the wrong "
      "flip rate (0.98^2, for true 0s).", "Lesson 12 code",
      code='''
import numpy as np
from qsim import density as dm

a = dm.readout_matrix(0.02, 0.04, 2)      # A[recorded, true]
recorded = a @ np.eye(4)[3]               # true state |11> = index 3
print(round(float(recorded[3]), 4))
'''),
    Q("qc-L300-006", 12, "code-reading", 3,
      "What does this density-matrix snippet print?",
      ["[0.45, 0.05, 0.05, 0.45]", "[0.4, 0.1, 0.1, 0.4]", "[0.5, 0.0, 0.0, 0.5]", "[0.45, 0.1, 0.0, 0.45]"],
      "Two-qubit depolarizing keeps the Bell state with weight 0.8 and mixes in I/4 with weight 0.2: 0.4 + 0.05 = "
      "0.45 on 00/11, 0.05 on 01/10. [0.4, 0.1, ...] forgets the identity part also lands on 00 and 11.",
      "Lesson 12 concepts",
      code='''
import numpy as np
from qsim import density as dm
from qsim import statevector as sv

rho = dm.run(2, [sv.h(0), sv.cx(0, 1), ("depol", 0.2, (0, 1))])
print(np.round(dm.probabilities(rho), 3).tolist())
'''),
    Q("qc-L300-007", 12, "calculation", 3,
      "The hardened check accepts success >= s - Z sqrt(s(1 - s)/shots). With the model's s for the Bell pair, "
      "2000 shots and Z = 4, what is the tolerance?",
      [str(TOL), "0.0059", "0.075", "0.2364"],
      f"4 x sqrt({BELL['success']} x {fmt(1 - BELL['success'], 3)} / 2000) = {TOL}. 0.0059 is one standard error "
      "without the factor Z = 4.", "Lesson 12 checkYourself"),
    Q("qc-L300-008", 12, "debugging", 2,
      "A regression test 'success >= 0.8' passes for a GHZ circuit that is missing its H gate. Why?",
      ["Without H nearly every shot is all-0, so success looks excellent", "The threshold is too strict for noise",
       "Readout mitigation hides the missing gate", "Success is always 1.0 on a density-matrix simulator, whatever the circuit does"],
      "P(all 0) + P(all 1) is near 1 when the circuit outputs only zeros. Also check the 0/1 balance against the "
      "model's prediction.", "Lesson 12 checkYourself"),
    Q("qc-L300-009", 12, "debugging", 2,
      "You set p2 = 0 in the noise model but the Bell fidelity is still below 1. What is happening?",
      ["p1 and damping are still on; zero every key for an ideal run", "The density matrix rounding adds error",
       "CX gates cannot be simulated at all when p2 is zero, so they are skipped", "Readout flips lower the state fidelity"],
      "Single-qubit depolarizing and amplitude damping still act after every gate; use the IDEAL dictionary. "
      "Readout flips do not affect fidelity.", "Lesson 12 troubleshooting"),
    Q("qc-L300-010", 12, "concept", 2,
      f"In the lab's noisy Bell run, P('00') = {BELL['p_all0']} but P('11') = {BELL['p_all1']}. What explains the "
      "asymmetry?",
      ["Damping decays toward |0> and p10 exceeds p01", "The H gate prefers |0> in every simulator",
       "Shot noise from the 2000-shot sample", "The CX target is always read first"],
      "Amplitude damping pushes |1> toward |0>, and 1 is misread as 0 (0.04) more often than the reverse (0.02). "
      "These are exact model probabilities, so shot noise plays no part.", "Lesson 12 code"),
    Q("qc-L300-011", 12, "design", 3,
      "You need a regression test for GHZ circuits that runs nightly on a noisy backend. Which approach fits?",
      ["Compare with the model's prediction minus Z sigma, and check balance", "Assert only all-0 and all-1 appear",
       "Require success >= 0.8 with no other check", "Skip the test on any night whose counts include '01'-type error outcomes"],
      "A model-based check has a known false-alarm rate and still catches structural bugs. Exact-outcome tests fail "
      "every correct noisy run; fixed thresholds pass a missing H.", "Lesson 12 tradeOffs"),
]

# ---------------- Lesson 13: error mitigation ----------------
L += [
    Q("qc-L300-012", 13, "calculation", 3,
      "Richardson extrapolation to zero noise uses scale factors 1, 3 and 5. What are the weights on the three "
      "measured values?",
      [f"+{W[0] * 8:.0f}/8, {W[1] * 8:.0f}/8, +{W[2] * 8:.0f}/8", "+1/3, +1/3, +1/3", "+3/8, -10/8, +15/8",
       "+5/4, -1/2, +1/4"],
      "Lagrange interpolation evaluated at 0 gives +15/8, -10/8, +3/8; they sum to 1. Reversing the order assigns the "
      "big weight to the noisiest point.", "Lesson 13 checkYourself"),
    Q("qc-L300-013", 13, "calculation", 3,
      f"The mirror GHZ-3 circuit gives P(000) = {ZNE[0]}, {ZNE[1]}, {ZNE[2]} at scales 1, 3, 5 (ideal 1.0). What "
      "are the Richardson and linear zero-noise estimates?",
      [f"Richardson {RICH}, linear {LIN}", f"Richardson {LIN}, linear {RICH}", f"Richardson {ZNE[0]}, linear {ZNE[0]}",
       "Richardson 1.0, linear 1.0"],
      f"Richardson uses the quadratic through all three points ({RICH}); a straight-line fit gives {LIN}. Both remove "
      f"most of the bias of the raw {ZNE[0]}, Richardson more of it (the lab's unrounded values give 0.9944 / 0.9687).",
      "Lesson 13 expectedResults"),
    Q("qc-L300-014", 13, "calculation", 3,
      "Each ZNE point has the same shot-noise std sigma. With Richardson weights for scales 1, 3, 5, by what factor "
      "is sigma multiplied in the extrapolated value?",
      [str(STD_GAIN), "1.0", "0.58", "3.5"],
      "std = sigma x sqrt(sum w^2) = sigma x sqrt(334)/8, about 2.28x; the lab saw 0.0069 grow to 0.017. 0.58 is "
      "what averaging three points would give.", "Lesson 13 tradeOffs"),
    Q("qc-L300-015", 13, "code-reading", 2,
      "What does this single-qubit readout mitigation print?",
      ["[1.0165, -0.0165]", "[0.985, 0.015]", "[1.0, 0.0]", "[0.9835, 0.0165]"],
      "The plain inverse M^-1 p returns a quasi-probability: it sums to 1 but has a negative entry. Expecting a "
      "clean [1.0, 0.0] assumes the inverse stays on the simplex.", "Lesson 13 failureLab",
      code='''
import numpy as np

m = np.array([[0.97, 0.06], [0.03, 0.94]])   # column j: observed distribution when |j> was prepared
p_noisy = np.array([0.985, 0.015])
print(np.round(np.linalg.solve(m, p_noisy), 4).tolist())
'''),
    Q("qc-L300-016", 13, "calculation", 2,
      f"The lab's mirror GHZ-3 circuit has {MIRROR_CX} CX gates. With local folding G -> G (G^-1 G)^k at scale 5, how "
      "many CX gates does the folded circuit contain?",
      [str(FOLD5_CX), str(MIRROR_CX + 4), str(MIRROR_CX * 3), str(MIRROR_CX * 25)],
      "Scale 5 replaces each CX with 5 copies (k = 2): 4 x 5 = 20. Adding 4 extra gates in total confuses per-gate "
      "folding with folding the whole circuit once.", "Lesson 13 code"),
    Q("qc-L300-017", 13, "concept", 2,
      "What does 'scale factor 3' mean for a CX gate in ZNE?",
      ["CX becomes CX.CX.CX: same logic, about 3x the noise", "The CX error rate is set to 3% in software",
       "The whole circuit runs three times and the three results are averaged", "Three CX gates are removed to reduce noise"],
      "Folding inserts G^-1 G pairs, which cancel logically but add noise. Running the same circuit three times "
      "only reduces shot noise.", "Lesson 13 checkYourself"),
    Q("qc-L300-018", 13, "debugging", 2,
      "After mitigation, rng.choice raises 'Probabilities are not non-negative'. Calibration used 100 shots per "
      "basis state. What is the fix?",
      ["Constrain the solution to the simplex and use >= 4000 shots", "Clip negative entries to 0 and report the rest without renormalising",
       "Invert the matrix twice for stability", "Reduce the run shots to 100 as well"],
      "Solve min ||M p - p_noisy||^2 with p >= 0 and sum 1, and spend enough shots on calibration and runs. Clipping "
      "alone breaks the sum and biases the result.", "Lesson 13 failureLab"),
    Q("qc-L300-019", 13, "scenario", 3,
      "Your Richardson ZNE estimate of a probability comes out at 1.04, above the ideal maximum. What should you do?",
      ["Switch to linear extrapolation or add shots per scale", "Report 1.04: mitigation is unbiased",
       "Add higher scale factors such as 9 and 11", "Apply readout mitigation to the extrapolated value to pull it below 1"],
      "Richardson over-fits shot noise; a linear fit or more shots per scale tames the variance. Higher scales make "
      "the polynomial even more sensitive to noise.", "Lesson 13 troubleshooting"),
    Q("qc-L300-020", 13, "concept", 2,
      "Which statement summarises the cost of error mitigation?",
      ["It trades bias for variance and needs extra runs", "It removes noise at no extra cost",
       "It turns a noisy device into a fault-tolerant one", "It lowers variance but adds bias"],
      "Mitigation removes systematic bias but amplifies shot noise and multiplies circuit runs. It is not error "
      "correction.", "Lesson 13 concepts"),
    Q("qc-L300-021", 13, "design", 3,
      "Mitigated results feed a sampler that draws bitstrings for a downstream report. Which readout-mitigation "
      "option should you choose?",
      ["Constrained least squares on the probability simplex", "The plain inverse M^-1, which is unbiased",
       "No mitigation, since reports accept raw counts", "Richardson extrapolation of the readout matrix over several shot counts"],
      "Anything that samples or reports probabilities needs a valid distribution; the constrained solve also had "
      "lower mean TVD at small budgets (0.0426 vs 0.055). The plain inverse can go negative.",
      "Lesson 13 tradeOffs"),
]

# ---------------- Lesson 14: QAOA MaxCut ----------------
L += [
    Q("qc-L300-022", 14, "calculation", 2,
      "Brute force over the lab's 5-node graph (edges 01, 02, 04, 12, 23, 34): what is the maximum cut and how many "
      "bitstrings achieve it?",
      [f"cut {int(MAXCUT)}, {len(OPT_STRINGS)} strings", "cut 6, 1 string", f"cut {int(MAXCUT)}, 2 strings",
       "cut 4, 8 strings"],
      "Enumerating all 32 strings gives 5 with four optimal strings (two complementary pairs). Cut 6 would need every "
      "edge cut, impossible with the triangle 0-1-2.", "Lesson 14 expectedResults"),
    Q("qc-L300-023", 14, "code-reading", 2,
      "This computes the cut size of one bitstring on the lab's 5-node graph (Qiskit order, q4...q0). What does it "
      "print?",
      [str(CUT_01010), str(CUT_01010 + 1), str(CUT_01010 - 2), "6"],
      "'01010' puts qubits 1 and 3 on one side; edges 01, 12, 23 and 34 cross: 4. It is a good cut but not one of the "
      "optimal 5s.", "Lesson 14 code",
      code='''
EDGES = [(0, 1), (0, 2), (0, 4), (1, 2), (2, 3), (3, 4)]
z = int("01010", 2)
print(sum(((z >> i) & 1) != ((z >> j) & 1) for i, j in EDGES))
'''),
    Q("qc-L300-024", 14, "calculation", 2,
      "With gamma = beta = 0 the QAOA state is the uniform superposition. What approximation ratio <C>/optimum "
      "does it give on the lab graph?",
      [str(RATIO_UNIFORM), "0.0", "0.5", "1.0"],
      "Each of the 6 edges is cut with probability 1/2, so <C> = 3 and 3/5 = 0.6. That is the random-guess baseline any "
      "trained QAOA must beat.", "Lesson 14 code"),
    Q("qc-L300-025", 14, "code-reading", 2,
      "This brute-forces MaxCut on a triangle. What does it print?",
      ["2 6", "3 1", "2 3", "3 2"],
      "A triangle can cut at most 2 of its 3 edges, and 6 of the 8 strings do so (all except 000 and 111). Cutting "
      "all 3 is impossible for an odd cycle.", "Lesson 14 code",
      code='''
import numpy as np

edges, n = [(0, 1), (1, 2), (0, 2)], 3
z = np.arange(2 ** n)
cut = sum(((z >> i) & 1) != ((z >> j) & 1) for i, j in edges)
print(int(cut.max()), int((cut == cut.max()).sum()))
'''),
    Q("qc-L300-026", 14, "concept", 3,
      "A p = 2 run ends at ratio 0.7002 while p = 1 reached 0.822. Why is that an optimiser failure rather than a "
      "limit of p = 2?",
      ["Zero second-layer angles reproduce p = 1, so better points exist", "p = 2 circuits always have more noise",
       "Deeper QAOA has a lower maximum ratio", "The brute-force optimum is different for p = 2, so 0.7002 is the new best"],
      "Every p = 1 point is reachable at p = 2, so the true p = 2 optimum is at least as good; the run stopped in a "
      "local minimum. The exact simulator has no noise to blame.", "Lesson 14 checkYourself"),
    Q("qc-L300-027", 14, "concept", 2,
      "QAOA reports <C> = 4.62 on the 5-node graph. What should the service return to the user?",
      ["The best sampled bitstring and its cut", "The value 4.62 rounded to a cut of 5", "The average bitstring",
       "The angles gamma and beta"],
      "<C> is an average over outcomes; the answer is the best bitstring you sample, here optimal with P = 0.707. "
      "Rounding an average does not produce a valid cut.", "Lesson 14 checkYourself"),
    Q("qc-L300-028", 14, "debugging", 2,
      "Gradient descent from the best p = 1 grid point makes the ratio DROP. What does the lesson suggest?",
      ["The learning rate is too large; 0.05 instead of 0.1", "Use a coarser grid", "Remove the mixer layer",
       "Switch from central to forward differences"],
      "A step size of 0.1 jumped out of the basin in testing; 0.05 stays in it. The grid point itself was fine.",
      "Lesson 14 troubleshooting"),
    Q("qc-L300-029", 14, "design", 3,
      "You must make a p = 2 QAOA result reliable and reproducible. Which strategy fits the lesson's evidence?",
      ["Warm-start from p = 1 angles plus seeded restarts, keep the best", "One random start with more steps",
       "A full grid search over all four angles at the same resolution as p = 1", "Raise p until the ratio stops changing"],
      "Interpolated warm starts land in the right basin and seeded restarts guard against local minima (0.9247). "
      "Extra steps from one random start stayed at 0.7002; a 4-D grid grows exponentially.", "Lesson 14 tradeOffs"),
    Q("qc-L300-030", 14, "concept", 2,
      "What do QAOA's two alternating layers do?",
      ["A diagonal phase by cut size, then an RX mixer", "An RX mixer, then a measurement of every edge",
       "A Grover oracle, then a diffusion operator", "A QFT, then an inverse QFT"],
      "The cost layer multiplies each basis state by exp(-i gamma C(z)); the mixer RX(2 beta) moves amplitude "
      "between bitstrings. A classical optimiser tunes both angles.", "Lesson 14 conceptSummary"),
]

# ---------------- Lesson 15: VQE ----------------
L += [
    Q("qc-L300-031", 15, "code-reading", 2,
      "This builds the lab's toy Hamiltonian. What does it print (energy of |00>, then the exact ground energy)?",
      ["-1.06 -1.8405", "-1.05 -1.8405", "-1.06 -1.06", "-0.88 -1.24"],
      "On |00> every Z term gives +1 and <XX> = 0: -1.05 + 0.39 - 0.39 - 0.01 = -1.06. eigvalsh gives E0 = -1.8405, "
      "the referee for the optimiser.", "Lesson 15 expectedResults",
      code='''
import numpy as np

TERMS = {"II": -1.05, "ZI": 0.39, "IZ": -0.39, "ZZ": -0.01, "XX": 0.18}
P = {"I": np.eye(2), "Z": np.diag([1.0, -1.0]), "X": np.array([[0.0, 1.0], [1.0, 0.0]])}
H = sum(c * np.kron(P[k[0]], P[k[1]]) for k, c in TERMS.items())
psi = np.array([1.0, 0.0, 0.0, 0.0])
print(round(float(psi @ H @ psi), 4), round(float(np.linalg.eigvalsh(H)[0]), 4))
'''),
    Q("qc-L300-032", 15, "calculation", 3,
      f"For the same Hamiltonian (E0 = {E0}), which computational basis state has the lowest energy, and what is it?",
      [f"'{BEST_BASIS}' with {BEST_BASIS_E}", "'00' with -1.06", f"'01' with {E0}", "'11' with -1.8405"],
      "The diagonal of H gives -1.82 for '10' (qubit 1 set). It is above E0 because the XX term needs a superposition "
      "of '10' and '01' - which is why the ansatz includes a CX.", "Lesson 15 code"),
    Q("qc-L300-033", 15, "calculation", 3,
      "Energy estimates carry noise eps = 0.01. What gradient error does a central finite difference with h = 1e-3 "
      "add, and what does an SPSA step with c_k = 0.1 add (eps / 2c_k)?",
      [f"{FD_ERR} vs {SPSA_ERR}", f"{SPSA_ERR} vs {FD_ERR}", "0.01 vs 0.01", "0.00001 vs 0.001"],
      "Noise divided by 2h = 0.002 gives 5, larger than the true gradient; divided by 2c_k = 0.2 it is 0.05. Small "
      "steps amplify noise, they do not reduce it.", "Lesson 15 checkYourself"),
    Q("qc-L300-034", 15, "concept", 2,
      "How many energy evaluations does ONE optimiser step need with 400 parameters: central finite differences "
      "versus SPSA?",
      [f"{FD_EVALS_400} vs {SPSA_EVALS}", "400 vs 400", "2 vs 800", "800 vs 400"],
      "Finite differences need 2 evaluations per parameter; SPSA perturbs all parameters at once and always needs 2. "
      "That is why SPSA scales to many parameters on hardware.", "Lesson 15 checkYourself"),
    Q("qc-L300-035", 15, "debugging", 2,
      "A shot-based VQE log shows the energy estimate jumping around while gradient norms stay above 5. What is "
      "the diagnosis?",
      ["Shot noise dominates the finite-difference gradient", "The ansatz is too shallow to reach E0, so the optimiser keeps searching",
       "The learning rate is too small", "The Hamiltonian has the wrong sign"],
      "Noise/h produces large fake gradients; switch to SPSA, larger perturbations, or more shots. A shallow ansatz "
      "would converge smoothly to a wrong value instead.", "Lesson 15 troubleshooting"),
    Q("qc-L300-036", 15, "concept", 2,
      "A noisy VQE run reports a best energy of -1.86, below the exact E0 = -1.8405. What happened?",
      ["A noisy minimum was reported; re-estimate with many shots", "The ansatz found a state below E0",
       "E0 was computed with the wrong Hamiltonian, so the true minimum is lower", "SPSA always undershoots E0 by 1%"],
      "The variational principle guarantees E(theta) >= E0 for the exact energy; a lower value is a lucky noisy "
      "estimate. Re-estimate the final parameters with many shots.", "Lesson 15 troubleshooting"),
    Q("qc-L300-037", 15, "concept", 2,
      "The lab measures II, ZI, IZ, ZZ in one group and XX in another. Why group them?",
      ["Commuting terms share one measurement basis, saving shots", "Each group needs its own Hamiltonian",
       "Grouping removes all shot noise from the estimate of each Pauli term", "XX cannot be measured on a quantum device"],
      "Z-type terms are all read from the same Z-basis counts; XX needs an H on each qubit first. Two settings "
      "instead of five per energy estimate.", "Lesson 15 code"),
    Q("qc-L300-038", 15, "scenario", 2,
      "An agent claims its suggested settings reached 'best_energy -1.835'. How does the lab decide whether to "
      "accept the claim?",
      ["Code runs the settings and recomputes the minimum from the log", "Accept it if the agent is confident",
       "Accept it, because any value above E0 is physically possible and plausible", "Ask the agent to repeat the claim"],
      "The model only proposes; code runs the proposal within a fixed shot budget and checks every number against "
      "the JSON-lines log. Plausibility is not evidence.", "Lesson 15 concepts"),
    Q("qc-L300-039", 15, "design", 3,
      "You will run VQE on hardware with 40 parameters and a modest shot budget. Which optimiser fits best?",
      ["SPSA: 2 evaluations per step and built for noisy estimates", "Finite-difference gradient descent with h = 1e-3 for precise gradients",
       "Exact gradient descent on the statevector", "COBYLA with one shot per evaluation"],
      "SPSA's cost is independent of the parameter count and tolerates shot noise. Finite differences need 80 "
      "evaluations per step and amplify noise.", "Lesson 15 tradeOffs"),
]

# ---------------- Lesson 16: quantum classifier ----------------
L += [
    Q("qc-L300-040", 16, "calculation", 2,
      "The lab's shot-noise floor for one parameter-shift gradient is sqrt(2)/2 / sqrt(shots) (0.0224 at 1000 "
      "shots). What is it at 4000 shots?",
      [str(FLOOR_4000), "0.0056", "0.0224", "0.0894"],
      "Four times the shots halves the noise: 0.0112. 0.0056 divides by 4 instead of sqrt(4).",
      "Lesson 16 code"),
    Q("qc-L300-041", 16, "code-reading", 3,
      "This compares the parameter-shift rule with a finite difference (h = 0.1) for d<Z>/d(theta) of RY(theta)|0> "
      "at theta = pi/3. What does it print?",
      ["-0.866 -0.8646", "-0.8646 -0.866", "-0.866 -0.866", "0.5 0.4992"],
      "The shift rule with +/-pi/2 is exact (-sin(pi/3) = -0.866); the finite difference is slightly off. 0.5 is "
      "<Z> itself, not its derivative.", "Lesson 16 concepts",
      code='''
import numpy as np
from qsim import statevector as sv


def z_exp(t):
    psi = sv.run(1, [(sv.ry(t), 0, ())])
    return abs(psi[0]) ** 2 - abs(psi[1]) ** 2


t = np.pi / 3
shift = (z_exp(t + np.pi / 2) - z_exp(t - np.pi / 2)) / 2
finite = (z_exp(t + 0.1) - z_exp(t - 0.1)) / 0.2
print(round(shift, 4), round(finite, 4))
'''),
    Q("qc-L300-042", 16, "calculation", 2,
      "Training uses 40 examples, 4 weights and 60 epochs. Each epoch needs one forward evaluation per example plus "
      "2 parameter-shift evaluations per weight per example. How many circuit evaluations in total?",
      [f"{TRAIN_EVALS:,}", "19,200", "2,400", "9,600"],
      "60 x 40 x (1 + 2 x 4) = 21,600. 19,200 forgets the forward pass.", "Lesson 16 tradeOffs"),
    Q("qc-L300-043", 16, "concept", 2,
      "The quantum model scores 0.9 test accuracy and logistic regression 0.85 on seed 3. Why is this not evidence "
      "of a quantum advantage?",
      ["It is one test point of 20; over 5 seeds they tie", "Logistic regression was trained on the test set",
       "Accuracy cannot be compared between models", "The quantum model used more test data"],
      "0.05 of 20 test points is a single example; over five seeds the models tie or differ by one point. Compare "
      "over several seeds before claiming anything.", "Lesson 16 checkYourself"),
    Q("qc-L300-044", 16, "concept", 3,
      "At 10 qubits x 20 layers with random angles, the median gradient is 0.0208 against a 1000-shot floor of "
      "0.0224. What does that mean for training?",
      ["The optimiser cannot tell the gradient's sign: a random walk", "Training is slower but still reliable",
       "The model has converged to a minimum", "Gradients are computed exactly by parameter shift, so shots do not matter"],
      "Below the noise floor the measured gradient is dominated by shot noise, so updates are random. This is the "
      "flat-gradient (barren plateau) problem, not convergence.", "Lesson 16 checkYourself"),
    Q("qc-L300-045", 16, "debugging", 2,
      "A wide, deep classifier's loss is flat from epoch 0. What does the lesson prescribe?",
      ["Run gradient_scan, then use near-identity init and a local readout", "Raise the learning rate tenfold",
       "Add more layers to increase expressivity", "Switch to a global readout over all qubits so every layer contributes signal"],
      "Measure gradients first; near-identity init (angles ~ N(0, 0.05^2)) and a local <Z0> readout keep them large "
      "(median 0.863). More layers and global readouts make gradients flatter.", "Lesson 16 troubleshooting"),
    Q("qc-L300-046", 16, "concept", 2,
      "Why does near-identity initialisation keep gradients alive?",
      ["Each layer starts close to identity, so the circuit acts shallow", "It sets every gradient to exactly 1",
       "It removes the need for a classical bias term, so there is less to train", "It makes the readout global"],
      "Starting near identity means early steps see an effectively shallow circuit with large gradients; capacity is "
      "earned by training. It does not fix gradient values.", "Lesson 16 checkYourself"),
    Q("qc-L300-047", 16, "scenario", 2,
      "Two runs of the classifier differ by 0.05 test accuracy. A teammate says the second model is better. "
      "What is your response?",
      ["That is one test point; compare across several dataset seeds", "Ship the better run immediately",
       "Increase the learning rate until both runs agree on the same test accuracy", "Report the maximum of the two accuracies"],
      "With 20 test points, 0.05 is one example and well within run-to-run variation. Repeat over seeds and compare "
      "distributions.", "Lesson 16 troubleshooting"),
    Q("qc-L300-048", 16, "design", 2,
      "A team wants a classifier for a tabular dataset in production. How should the classical baseline be used?",
      ["Always run it first; it is usually the answer for tabular data", "Skip it if the quantum model trains",
       "Use it only when the quantum model fails", "Train it on the test split as well, so both models get to see all the data"],
      "Logistic regression is milliseconds and 3 parameters, and here it ties the quantum model. Every comparison is "
      "on held-out data that neither model trained on.", "Lesson 16 tradeOffs"),
]

L += [
    Q("qc-L300-049", 12, "concept", 2,
      "What does it mean that a noise model is 'attached to gate names'?",
      ["An error channel is inserted after every instance of that gate", "The gate is replaced by a noisier gate type",
       "Noise is added once at the end of the circuit, scaled by the number of gates", "Only gates with that name are measured"],
      "Lab 12's noisy_steps() appends depolarizing and damping channels after each 1-qubit gate and each CX, plus "
      "readout flips at measurement. Adding noise only at the end would ignore circuit size.", "Lesson 12 concepts"),
    Q("qc-L300-050", 12, "concept", 3,
      "Why does the noise lab use a density matrix instead of a statevector?",
      ["Noise creates mixtures of states that one statevector cannot hold", "Density matrices use less memory",
       "Statevectors cannot represent entangled states such as the noisy Bell pair", "Only density matrices support the CX gate"],
      "A noisy channel leaves the system in a probabilistic mixture, which a density matrix represents exactly. It "
      "costs 4^n entries, so it uses more memory, not less.", "Lesson 12 conceptSummary"),
    Q("qc-L300-051", 13, "concept", 2,
      "In lab 13's readout calibration, what does column j of the assignment matrix contain?",
      ["The observed distribution when basis state |j> was prepared", "The true distribution of the Bell state",
       "The probability that qubit j is measured as 1 across all the calibration runs", "The mitigated result for shot j"],
      "calibrate() prepares each basis state and measures it, so column j is P(recorded | true j). Mitigation then "
      "inverts that matrix.", "Lesson 13 code"),
    Q("qc-L300-052", 14, "concept", 3,
      "Why does the grid warm start that works at p = 1 not scale to large p?",
      ["Grid points grow exponentially with the 2p angles", "Larger p circuits cannot be simulated",
       "The landscape becomes convex at large p", "Brute force stops working at p = 2"],
      "A grid with k values per angle needs k^(2p) evaluations; interpolating p -> p + 1 avoids that. The lab's "
      "brute force grades the cut, which does not depend on p.", "Lesson 14 tradeOffs"),
    Q("qc-L300-053", 15, "concept", 2,
      "What role does the exact ground energy E0 = -1.8405 play in lab 15?",
      ["A referee for measuring error, never given to the optimiser", "The starting point of the optimiser",
       "A constant the optimiser subtracts from each estimate to centre the energies", "The learning rate schedule for SPSA"],
      "Only the exact diagonalisation knows E0; the lab uses it after the run to grade the error. In real problems "
      "E0 is unknown, which is why logs and variance matter.", "Lesson 15 code"),
    Q("qc-L300-054", 15, "concept", 3,
      "How does SPSA estimate a gradient with only two energy evaluations?",
      ["It perturbs all parameters at once along a random +/-1 direction", "It reuses the previous step's gradient",
       "It measures only the largest Hamiltonian term and rescales the gradient to match", "It evaluates one parameter per step in turn"],
      "Evaluating E(x + c delta) and E(x - c delta) for a random sign vector delta gives a gradient estimate for every "
      "parameter at once. Cycling through parameters would need many steps per full gradient.", "Lesson 15 tradeOffs"),
    Q("qc-L300-055", 16, "concept", 2,
      "Why does lab 16 keep a test split that is never used for training?",
      ["It estimates how the model does on data it has not seen", "It speeds up each training epoch",
       "Quantum models cannot evaluate their training data", "It doubles the effective training set"],
      "Training accuracy rewards memorisation; held-out accuracy is the fair basis for comparing with the classical "
      "baseline.", "Lesson 16 concepts"),
    Q("qc-L300-056", 16, "concept", 3,
      "What is a 'local readout' in lab 16, and why does it help at scale?",
      ["Measuring one qubit's <Z0>, whose gradients flatten more slowly", "Reading every qubit and averaging them",
       "Running the circuit on a local simulator instead of a shared remote device", "Measuring only after the first layer"],
      "Global observables over many qubits make gradients vanish faster; a local <Z0> plus near-identity init kept "
      "the median gradient at 0.863 at 10 x 20.", "Lesson 16 failureLab"),
    Q("qc-L300-057", 16, "scenario", 3,
      "A manager asks you to scale the classifier to 10 qubits x 20 layers 'to beat logistic regression'. What do "
      "you do first?",
      ["Run a gradient scan; with random init most gradients sit below shot noise", "Train it for more epochs",
       "Train the full model straight away; more qubits and layers add capacity and accuracy", "Switch off the classical bias term"],
      "Measure gradients before training: random init at that size gave median 0.0208 against a 0.0224 floor. Then "
      "use near-identity init and still compare with the baseline over several seeds.", "Lesson 16 failureLab"),
]

QUESTIONS = L
