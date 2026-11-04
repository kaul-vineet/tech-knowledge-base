"""L200 question bank data (lessons 7-11). Correct option first; numbers computed below with numpy / qsim."""
import math

import numpy as np

from qbank_common import Q, fmt
from qsim import statevector as sv


def grover_success(n, marked, k):
    """Exact Grover success with qsim: phase oracle + diffusion, k iterations."""
    hs, xs = [sv.h(q) for q in range(n)], [sv.x(q) for q in range(n)]
    oracle = []
    for t in marked:
        zeros = [q for q, b in enumerate(reversed(t)) if b == "0"]
        oracle += [sv.x(q) for q in zeros] + [sv.mcz(list(range(n - 1)), n - 1)] + [sv.x(q) for q in zeros]
    diffuse = hs + xs + [sv.mcz(list(range(n - 1)), n - 1)] + xs + hs
    probs = sv.probabilities(sv.run(n, hs + (oracle + diffuse) * k))
    return fmt(sum(probs.get(m, 0.0) for m in marked))


def k_opt(m, n):
    return math.floor(math.pi / (4 * math.asin(math.sqrt(m / 2 ** n))))


BV_QUBITS_6 = 6 + 1
G8 = [grover_success(3, ["101"], k) for k in range(4)]
K16 = k_opt(1, 4)
P16 = grover_success(4, ["1011"], K16)
K32 = k_opt(2, 5)
P32 = grover_success(5, ["10110", "00011"], K32)
CPHASE_6 = 6 * 5 // 2
_p4 = np.zeros(8)
_p4[[1, 5]] = 1 / np.sqrt(2)
PERIOD4_PEAKS = [format(i, "03b") for i, v in enumerate(np.abs(np.fft.ifft(_p4, norm="ortho")) ** 2) if v > 1e-9]
_ry = sv.run(1, [(sv.ry(np.pi / 3), 0, ())])
RY_Z = fmt(abs(_ry[0]) ** 2 - abs(_ry[1]) ** 2, 4)
RY_P1 = fmt(abs(_ry[1]) ** 2, 4)
THETA_075 = fmt(2 * math.asin(math.sqrt(0.75)), 4)
EXTRA_CX_LINE = 3 * (4 - 1)                    # path 0-1-2-3-4: 3 SWAPs bring qubit 0's state next to 4
ROUTED_CX = 4 + 3 * 2
K64 = k_opt(1, 6)
P64_K2 = grover_success(6, ["101101"], 2)
P64_KOPT = grover_success(6, ["101101"], K64)

L = []
# ---------------- Lesson 7: Bernstein-Vazirani ----------------
BV = '''
from qsim import statevector as sv

secret, n = "110", 3
ops = [sv.x(n)] + [sv.h(q) for q in range(n + 1)]
ops += [sv.cx(q, n) for q, bit in enumerate(reversed(secret)) if bit == "1"]
ops += [sv.h(q) for q in range(n)]
probs = sv.probabilities(sv.run(n + 1, ops), 6)
inputs = {}
for bits, p in probs.items():
    inputs[bits[1:]] = round(inputs.get(bits[1:], 0) + p, 6)   # drop the ancilla (leftmost)
print(inputs)
'''
L += [
    Q("qc-L200-001", 7, "concept", 2,
      "In Bernstein-Vazirani, why must the ancilla start in |-> (X then H) rather than |+>?",
      ["So the oracle's bit flip becomes a phase on the inputs", "So the ancilla can be measured to read the secret",
       "Because |+> would make the oracle need more CX gates", "So that the inputs start in the state |s>"],
      "On |->, flipping the ancilla multiplies the state by -1: phase kickback writes (-1)^f(x) onto the inputs. "
      "|+> is unchanged by CX, so nothing is kicked back.", "Lesson 7 checkYourself"),
    Q("qc-L200-002", 7, "code-reading", 2,
      "This qsim Bernstein-Vazirani run uses secret '110'. What does it print?",
      ["{'110': 1.0}", "{'011': 1.0}", "{'110': 0.5, '111': 0.5}", "{'000': 1.0}"],
      "One query plus the final H layer turns the phase pattern into |s> with certainty; the ancilla's 50/50 is summed "
      "away. '011' would be the reversed (bit-order) mistake.", "Lesson 7 expectedResults", code=BV),
    Q("qc-L200-003", 7, "debugging", 2,
      "For secret '1011' this oracle loop prints {'1101': 1.0} instead of {'1011': 1.0}. What is the fix?",
      ["Iterate over reversed(secret) when mapping bits to qubits", "Start the ancilla in |+> instead of |->",
       "Add a second oracle query before the H layer", "Measure the ancilla together with the inputs to recover the correct bit order"],
      "The string is written q(n-1)...q0, so position 0 of the string is the highest qubit; enumerating it directly "
      "reverses the answer. The ancilla prep is fine, since the result is still certain.", "Lesson 7 troubleshooting",
      code='''
from qsim import statevector as sv

secret, n = "1011", 4
ops = [sv.x(n)] + [sv.h(q) for q in range(n + 1)]
ops += [sv.cx(q, n) for q, bit in enumerate(secret) if bit == "1"]
ops += [sv.h(q) for q in range(n)]
probs = sv.probabilities(sv.run(n + 1, ops), 6)
inputs = {}
for bits, p in probs.items():
    inputs[bits[1:]] = round(inputs.get(bits[1:], 0) + p, 6)
print(inputs)
'''),
    Q("qc-L200-004", 7, "code-reading", 3,
      "Here the ancilla is prepared with H only (no X), so it starts in |+>. What does the run print for secret '110'?",
      ["{'000': 1.0}", "{'110': 1.0}", "{'001': 1.0}", "{'110': 0.5, '000': 0.5}"],
      "With the ancilla in |+>, CX changes nothing, so no phase is kicked back and H.H returns the inputs to |000>. "
      "The oracle still runs, but its answer never reaches the inputs.", "Lesson 7 checkYourself",
      code='''
from qsim import statevector as sv

secret, n = "110", 3
ops = [sv.h(q) for q in range(n + 1)]
ops += [sv.cx(q, n) for q, bit in enumerate(reversed(secret)) if bit == "1"]
ops += [sv.h(q) for q in range(n)]
probs = sv.probabilities(sv.run(n + 1, ops), 6)
inputs = {}
for bits, p in probs.items():
    inputs[bits[1:]] = round(inputs.get(bits[1:], 0) + p, 6)
print(inputs)
'''),
    Q("qc-L200-005", 7, "concept", 2,
      "How is the parity oracle f(x) = s.x (mod 2) built in lab 07?",
      ["One CX from each input whose secret bit is 1 to the ancilla", "One H gate on every input qubit",
       "A multi-controlled Z across all qubits", "One CX from the ancilla back to each input qubit whose secret bit is 0"],
      "Each CX adds one selected input bit into the ancilla, computing the parity. The H layers belong to the "
      "surrounding pattern, not to the oracle.", "Lesson 7 concepts"),
    Q("qc-L200-006", 7, "concept", 1,
      "How many qubits does the lab-07 circuit need for a 6-bit secret?",
      [str(BV_QUBITS_6), "6", "12", "64"],
      "n inputs plus one ancilla: 6 + 1 = 7. Six forgets the ancilla that carries the kickback.", "Lesson 7 code"),
    Q("qc-L200-007", 7, "concept", 2,
      "The classical baseline needs 6 queries for secret 110101; BV needs 1. What does that comparison actually show?",
      ["A query-count advantage in a black-box model, not a wall-clock speedup", "Quantum computers are 6x faster",
       "The quantum circuit needs no gates at all", "BV breaks any encryption scheme that relies on parity checks of secret bits"],
      "BV counts oracle calls; the circuit still has gates and, on hardware, noise. It teaches the oracle pattern "
      "rather than a practical speedup.", "Lesson 7 expectedResults"),
    Q("qc-L200-008", 7, "scenario", 2,
      "On a noisy device, 100 shots of a 4-bit BV circuit return the secret 81 times and other strings 19 times. "
      "How should you read the answer?",
      ["Take the most frequent string and check it stands well clear", "Report 'no answer' because it is not 100%",
       "Average the bitstrings bit by bit and round", "Rerun the whole job until one run gives the secret in all 100 shots"],
      "On hardware, noise turns a certain answer into the most frequent one; a clear majority is the signal. "
      "Demanding 100% would reject almost every correct hardware run.", "Lesson 7 simulatorVsReal"),
]

# ---------------- Lesson 8: Grover ----------------
GROVER_BUG = '''
from qsim import statevector as sv

n, target = 3, "110"
zeros = [q for q, bit in enumerate(target) if bit == "0"]
oracle = [sv.x(q) for q in zeros] + [sv.mcz([0, 1], 2)] + [sv.x(q) for q in zeros]
hs, xs = [sv.h(q) for q in range(n)], [sv.x(q) for q in range(n)]
diffuse = hs + xs + [sv.mcz([0, 1], 2)] + xs + hs
probs = sv.probabilities(sv.run(n, hs + (oracle + diffuse) * 2), 4)
print(max(probs, key=probs.get))
'''
L += [
    Q("qc-L200-009", 8, "calculation", 2,
      "Grover search over N = 8 states with one marked state. What is the exact success probability after ONE "
      "iteration?",
      [str(G8[1]), str(G8[0]), str(G8[2]), "1.0"],
      f"The qsim run gives {G8[1]} after k = 1, rising to {G8[2]} at k = 2. {G8[0]} is the starting value 1/8 "
      "before any iteration.", "Lesson 8 expectedResults"),
    Q("qc-L200-010", 8, "calculation", 2,
      "With N = 16 and one marked state, what does k_opt = floor(pi / (4 asin(sqrt(M/N)))) give, and what is the "
      "success probability there?",
      [f"k = {K16}, P = {P16}", f"k = 4, P = {grover_success(4, ['1011'], 4)}", f"k = 2, P = {grover_success(4, ['1011'], 2)}",
       "k = 16, P = 1.0"],
      f"asin(1/4) = 0.2527, so k_opt = {K16} and qsim gives P = {P16}. Using sqrt(N) = 4 overshoots the peak.",
      "Lesson 8 concepts"),
    Q("qc-L200-011", 8, "calculation", 2,
      "For N = 8 with one marked state, someone runs 3 iterations instead of the optimal 2. What success "
      "probability do they get?",
      [str(G8[3]), str(G8[2]), "0.9999", str(G8[1])],
      f"Grover rotates past the target: the curve goes {G8[0]} -> {G8[1]} -> {G8[2]} -> {G8[3]}. More iterations are "
      "not always better.", "Lesson 8 expectedResults"),
    Q("qc-L200-012", 8, "concept", 3,
      f"N = 32 with M = 2 marked states. qsim gives k_opt = {K32} and P = {P32} - exactly the numbers for N = 16, "
      "M = 1. Why?",
      ["Success depends only on M/N, and 2/32 = 1/16", "Grover ignores the number of marked states",
       "Both searches use 4 qubits in the end", "The qsim run rounded both results to the same value"],
      "sin(theta) = sqrt(M/N) fixes the whole curve sin^2((2k+1)theta); doubling both N and M changes nothing. The "
      "N = 32 search really uses 5 qubits.", "Lesson 8 concepts"),
    Q("qc-L200-013", 8, "code-reading", 2,
      "What does this print?",
      ["[0.25, 1.0, 0.25, 0.25]", "[0.25, 0.5, 0.75, 1.0]", "[0.25, 1.0, 0.0, 1.0]", "[1.0, 0.25, 1.0, 0.25]"],
      "For N = 4, M = 1, theta = 30 degrees, so k = 1 puts (2k+1)theta at 90 degrees: exactly 1.0. k = 2 and 3 land at "
      "150 and 210 degrees, where sin^2 is 0.25 again. Success does not grow steadily with k.", "Lesson 8 concepts",
      code='''
import math

N, M = 4, 1
theta = math.asin(math.sqrt(M / N))
print([round(math.sin((2 * k + 1) * theta) ** 2, 4) for k in range(4)])
'''),
    Q("qc-L200-014", 8, "debugging", 3,
      "This Grover run should amplify '110' but prints '011'. What is the bug?",
      ["The X positions ignore Qiskit bit order; use reversed(target)", "The diffusion operator is missing the H layer before its multi-controlled Z",
       "Two iterations is too many for N = 8", "mcz must target qubit 0, not qubit 2"],
      "Strings are q(n-1)...q0, so enumerating target directly puts X on the wrong qubits and marks the reversed "
      "string. Two iterations is optimal for N = 8.", "Lesson 8 troubleshooting", code=GROVER_BUG),
    Q("qc-L200-015", 8, "scenario", 2,
      "A search over 4 items has 2 marked items. Every iteration count gives success 0.5. What should you do?",
      ["Sample classically: Grover cannot help when half are marked", "Run more iterations until it rises",
       "Add a third qubit and repeat the oracle", "Switch to the inverse diffusion operator so the rotation goes the other way"],
      "theta = 45 degrees, so sin^2((2k+1) x 45 degrees) = 0.5 for every k; a random guess already succeeds half the "
      "time. More iterations only cycle through the same value.", "Lesson 8 troubleshooting"),
    Q("qc-L200-016", 8, "concept", 2,
      "How does the number of Grover iterations scale for one marked item among N?",
      ["About (pi/4) sqrt(N): a quadratic speedup", "About log2(N): an exponential speedup",
       "About N/2, the same as classical search", "Always 2, independent of N"],
      "k_opt grows like sqrt(N), versus about N/2 classical guesses: quadratic, not exponential. The '2' only "
      "holds for N = 8.", "Lesson 8 concepts"),
    Q("qc-L200-017", 8, "concept", 2,
      "You add more marked states to the same search space. What happens to the optimal iteration count?",
      ["It decreases, because theta = asin(sqrt(M/N)) grows", "It increases in proportion to M",
       "It stays the same, since N is unchanged", "It becomes zero for any M greater than 1, since one query finds them all"],
      "Larger M means a larger rotation angle per iteration, so the peak comes sooner. The count depends on M as "
      "well as N.", "Lesson 8 concepts"),
]

# ---------------- Lesson 9: QFT ----------------
L += [
    Q("qc-L200-018", 9, "concept", 2,
      "Which numpy call reproduces Qiskit's QFT matrix?",
      ["np.fft.ifft(np.eye(N), axis=0, norm='ortho')", "np.fft.fft(np.eye(N))", "np.fft.fftn(np.eye(N), axes=(0,), norm='ortho')",
       "np.fft.ifft(np.eye(N))"],
      "The QFT uses the +i sign (numpy's ifft) and 1/sqrt(N) scaling (norm='ortho'). fft with 'ortho' has the minus "
      "sign: that is the inverse QFT.", "Lesson 9 checkYourself"),
    Q("qc-L200-019", 9, "calculation", 1,
      "The textbook QFT uses n(n-1)/2 controlled-phase gates. How many does a 6-qubit QFT use?",
      [str(CPHASE_6), "6", "36", "30"],
      "6 x 5 / 2 = 15: each qubit gets one controlled phase from every lower qubit. 30 counts each pair twice.",
      "Lesson 9 checkYourself"),
    Q("qc-L200-020", 9, "code-reading", 2,
      "This computes the phases (in turns) of QFT|5> for 3 qubits. What does it print?",
      ["[0.0, 0.625, 0.25, 0.875]", "[0.0, 0.375, 0.75, 0.125]", "[0.0, 0.125, 0.25, 0.375]",
       "[0.625, 0.625, 0.625, 0.625]"],
      "Amplitude k has phase 5k/8 turns: 0, 0.625, 1.25 -> 0.25, 1.875 -> 0.875. The second option is the fft "
      "(minus) sign, i.e. the inverse QFT.", "Lesson 9 code",
      code='''
import numpy as np

amps = np.fft.ifft(np.eye(8)[5], norm="ortho")
turns = np.round(np.angle(amps) / (2 * np.pi) % 1, 4)
print(turns[:4].tolist())
'''),
    Q("qc-L200-021", 9, "code-reading", 2,
      "A period-2 state (|0> + |2> + |4> + |6>)/2 goes through the QFT. What does this print?",
      ["{'000': 0.5, '100': 0.5}", "{'000': 0.5, '010': 0.5}", "{'000': 0.25, '010': 0.25, '100': 0.25, '110': 0.25}",
       "{'000': 1.0}"],
      "Period r = 2 in N = 8 gives peaks at multiples of N/r = 4: outcomes 0 and 4 ('000', '100'). Peaks at the "
      "input positions would mean the transform did nothing.", "Lesson 9 expectedResults",
      code='''
import numpy as np

state = np.zeros(8)
state[[0, 2, 4, 6]] = 0.5
p = np.abs(np.fft.ifft(state, norm="ortho")) ** 2
print({format(i, "03b"): round(float(v), 4) for i, v in enumerate(p) if v > 1e-9})
'''),
    Q("qc-L200-022", 9, "calculation", 2,
      "A 3-qubit input has period 4 and offset 1: (|1> + |5>)/sqrt(2). After the QFT, which outcomes have nonzero "
      "probability?",
      [", ".join(PERIOD4_PEAKS), "001, 101", "000, 100", "000 only"],
      "Peaks sit at multiples of N/r = 8/4 = 2, whatever the offset; the offset only changes phases. The input "
      "positions themselves are the tempting wrong answer.", "Lesson 9 concepts"),
    Q("qc-L200-023", 9, "concept", 2,
      "How do you build the inverse QFT from a QFT circuit?",
      ["Reverse the gate order and negate every phase angle", "Run the same QFT circuit a second time",
       "Remove the final swaps and keep everything else", "Replace every H gate with an X gate"],
      "A circuit's inverse undoes the gates in reverse order with inverse gates; for phases that means negated "
      "angles. Applying the QFT twice gives a permutation, not the identity.", "Lesson 9 concepts"),
    Q("qc-L200-024", 9, "debugging", 2,
      "Your hand-built QFT matrix equals numpy's DFT only after reordering its rows. What is missing?",
      ["The final swap layer (bit reversal)", "The 1/sqrt(N) normalisation", "One of the H gates",
       "The negative sign on every phase"],
      "Without the swaps the outputs come out bit-reversed; add them or reverse the bits classically. A missing "
      "normalisation would change the magnitudes, not the row order.", "Lesson 9 troubleshooting"),
    Q("qc-L200-025", 9, "debugging", 2,
      "Your QFT matrix matches np.fft.fft(..., norm='ortho') instead of ifft. What have you built?",
      ["The inverse QFT: your phase angles have the wrong sign", "A correct QFT: fft and ifft give identical matrices with norm='ortho'",
       "A QFT missing its final swaps", "A circuit with an extra H gate"],
      "fft uses e^(-2 pi i jk/N), the inverse QFT's sign; flip the sign of the controlled phases. Missing swaps would "
      "permute rows, not conjugate the phases.", "Lesson 9 troubleshooting"),
    Q("qc-L200-026", 9, "concept", 3,
      "Why is the QFT a building block rather than a faster way to compute a classical Fourier transform?",
      ["The output lives in amplitudes you cannot read out directly", "It is slower than np.fft for every N",
       "It only works on states with exactly one nonzero amplitude", "It needs one oracle call per frequency"],
      "Measuring returns one outcome per shot, so you cannot read all N coefficients; the QFT pays off inside "
      "algorithms that need only peaks, like period finding. Its gate count is small, not large.",
      "Lesson 9 overview"),
]

# ---------------- Lesson 10: parameterized circuits ----------------
L += [
    Q("qc-L200-027", 10, "concept", 2,
      "What does qc.assign_parameters({theta: pi/3}) do to the template qc?",
      ["Returns a bound copy; qc still has theta free", "Binds theta inside qc permanently",
       "Runs the circuit at theta = pi/3", "Deletes theta from every circuit that uses it"],
      "assign_parameters returns a new circuit unless inplace=True, so the template stays reusable. Nothing is "
      "executed by binding.", "Lesson 10 checkYourself"),
    Q("qc-L200-028", 10, "calculation", 2,
      "RY(pi/3) is applied to |0>. Using qsim, what are <Z> and P(1)?",
      [f"<Z> = {RY_Z}, P(1) = {RY_P1}", f"<Z> = {RY_P1}, P(1) = {RY_Z}", "<Z> = 0.866, P(1) = 0.5",
       "<Z> = 0.5, P(1) = 0.5"],
      "RY(theta)|0> = cos(theta/2)|0> + sin(theta/2)|1>, so P(1) = sin^2(pi/6) = 0.25 and <Z> = cos(pi/3) = 0.5. "
      "Swapping the two values is the common slip.", "Lesson 10 concepts"),
    Q("qc-L200-029", 10, "calculation", 2,
      "Which RY angle (in radians, 4 decimals) gives P(1) = 0.75 from |0>?",
      [str(THETA_075), "0.8481", "1.0472", "2.3562"],
      "P(1) = sin^2(theta/2) = 0.75 gives theta/2 = pi/3, so theta = 2pi/3 = 2.0944. 1.0472 forgets the factor of 2 "
      "in the half-angle.", "Lesson 10 concepts"),
    Q("qc-L200-030", 10, "code-reading", 2,
      "This least-squares fit of a*cos + b*sin + c runs on data with an offset. What does it print?",
      ["[1.0, 0.0, 0.3]", "[1.3, 0.0, 0.0]", "[1.0, 0.3, 0.0]", "[0.3, 0.0, 1.0]"],
      "The data are exactly cos(theta) + 0.3, so the fit returns a = 1, b = 0, c = 0.3. The columns are cos, sin, "
      "constant in that order.", "Lesson 10 concepts",
      code='''
import numpy as np

thetas = np.linspace(0, 2 * np.pi, 21)
values = np.cos(thetas) + 0.3
a = np.column_stack([np.cos(thetas), np.sin(thetas), np.ones_like(thetas)])
coef, *_ = np.linalg.lstsq(a, values, rcond=None)
print([round(float(c), 3) + 0.0 for c in coef])
'''),
    Q("qc-L200-031", 10, "code-reading", 1,
      "Lab 10 estimates <Z> from counts. What does this print?",
      ["0.55 0.775", "0.775 0.55", "0.45 0.225", "220 0.775"],
      "<Z> = (n0 - n1)/shots = (310 - 90)/400 = 0.55 and P(0) = (1 + <Z>)/2 = 0.775. Forgetting to divide by shots "
      "gives 220.", "Lesson 10 code",
      code='''
counts = {"0": 310, "1": 90}
shots = sum(counts.values())
z = (counts.get("0", 0) - counts.get("1", 0)) / shots
print(z, round((1 + z) / 2, 3))
'''),
    Q("qc-L200-032", 10, "debugging", 2,
      "A two-parameter circuit binds values with a plain list, and alpha ends up in beta's slot. What is the fix?",
      ["Bind by dict: list binding follows qc.parameters sorted by name", "Reverse the list before binding",
       "Use inplace=True on assign_parameters", "Wrap the values in a tuple so their order is preserved during binding"],
      "List binding follows qc.parameters, which is sorted by name, not by creation order; a dict is explicit. "
      "inplace only changes whether a copy is made.", "Lesson 10 troubleshooting"),
    Q("qc-L200-033", 10, "debugging", 2,
      "Sweeping 21 angles of a one-parameter circuit raises a ValueError about parameter shape. What should the "
      "values array look like?",
      ["Shape (21, 1): points by parameters", "Shape (1, 21): parameters by points", "A flat list of 21 dicts",
       "Shape (21,) with no reshaping"],
      "Primitives expect (number_of_points, number_of_parameters), so reshape(-1, 1). (1, 21) would mean one point "
      "with 21 parameters.", "Lesson 10 troubleshooting"),
    Q("qc-L200-034", 10, "concept", 2,
      "Why fit a*cos(theta) + b*sin(theta) + c to the whole sampled <Z> sweep instead of reading the point at "
      "theta = pi/2?",
      ["The fit uses all 21 points and averages out shot noise", "The point at pi/2 is never simulated",
       "Fitting removes shot noise completely, so one shot per point is enough", "Single points are always biased upward"],
      "Each sampled point carries its own shot noise; a model with 3 parameters fitted to 21 points averages it down. "
      "The pi/2 point exists but is as noisy as any other.", "Lesson 10 checkYourself"),
    Q("qc-L200-035", 10, "scenario", 2,
      "You need <Z> and <X> at 21 angles. What is the efficient way to submit this with Qiskit primitives?",
      ["One PUB: template, observables shaped (2, 1), values (21, 1)", "42 separate circuits, each bound by hand",
       "21 separate jobs, one per angle, each estimating both observables at once", "Rebuild the circuit from scratch for every angle"],
      "Observable and parameter arrays broadcast, so one estimator call returns a (2, 21) result. Hand-building "
      "circuits works but multiplies code and submissions.", "Lesson 10 code"),
]

# ---------------- Lesson 11: transpiling ----------------
L += [
    Q("qc-L200-036", 11, "code-reading", 1,
      "What does this print?",
      ["3 True", "1 True", "3 False", "2 True"],
      "sv.swap returns three CX gates whose product is the SWAP permutation matrix. That is why each routing SWAP "
      "costs 3 two-qubit gates.", "Lesson 11 concepts",
      code='''
import numpy as np
from qsim import statevector as sv

swap_ops = sv.swap(0, 1)
u = sv.unitary(2, swap_ops)
print(len(swap_ops), np.allclose(u, np.eye(4)[[0, 2, 1, 3]]))
'''),
    Q("qc-L200-037", 11, "code-reading", 2,
      "This counts how many CX pairs are NOT edges of a 5-qubit line, for the GHZ star and the GHZ chain. "
      "What does it print?",
      ["3 0", "4 0", "3 3", "0 3"],
      "The star uses (0,2), (0,3), (0,4), which are not line edges; the chain uses only neighbours. That is why "
      "the star needs routing on a line and the chain does not.", "Lesson 11 checkYourself",
      code='''
line = {(i, i + 1) for i in range(4)} | {(i + 1, i) for i in range(4)}
star = [(0, t) for t in range(1, 5)]
chain = [(i, i + 1) for i in range(4)]
print(sum(p not in line for p in star), sum(p not in line for p in chain))
'''),
    Q("qc-L200-038", 11, "calculation", 2,
      "On a line 0-1-2-3-4, a CX is needed between physical qubits 0 and 4. Routing moves qubit 0's state along "
      "the path with SWAPs until it is adjacent to 4. How many extra CX gates does that add?",
      [str(EXTRA_CX_LINE), "4", "12", "3"],
      "Three SWAPs (0-1, 1-2, 2-3) make it adjacent to 4, and each SWAP is 3 CX: 9. Answering 3 counts SWAPs, not "
      "CX gates.", "Lesson 11 concepts"),
    Q("qc-L200-039", 11, "calculation", 1,
      "A circuit with 4 CX gates needs 2 SWAPs after routing. How many CX gates are there in total (before any "
      "optimisation)?",
      [str(ROUTED_CX), "6", "8", "12"],
      "Each SWAP becomes 3 CX, so 4 + 2 x 3 = 10. Six counts each SWAP as a single two-qubit gate.",
      "Lesson 11 concepts"),
    Q("qc-L200-040", 11, "debugging", 2,
      "Transpiling the same circuit at optimization level 2 gives different gate counts on each run. What fixes "
      "this?",
      ["Pass seed_transpiler so layout and routing repeat", "Seed the sampler with seed=7",
       "Switch to optimization level 3, which always finds the same layout", "Use more shots per run"],
      "Levels 1-3 use stochastic layout and routing; seed_transpiler fixes those choices. A sampler seed only "
      "affects measurement draws.", "Lesson 11 troubleshooting"),
    Q("qc-L200-041", 11, "scenario", 2,
      "You transpile a 5-qubit GHZ circuit for the 19-qubit heavy-hex fake backend and the output has 19 qubits. "
      "What does that mean?",
      ["Expected: the output is on physical qubits; your bits keep their order", "A bug: 14 qubits were duplicated",
       "The circuit was replaced by a 19-qubit GHZ", "The transpiler failed and silently fell back to an all-to-all 19-qubit device"],
      "Transpiled circuits are expressed on the device's physical qubits; unused ones stay idle and measured bits "
      "keep your order. Nothing was added to the logic.", "Lesson 11 troubleshooting"),
    Q("qc-L200-042", 11, "concept", 2,
      "What do optimization levels 0-3 trade against each other?",
      ["Compile effort versus fewer gates and lower depth", "Accuracy of the result versus simulator speed",
       "Number of qubits versus number of shots", "Noise level versus readout error"],
      "Higher levels spend more compile time searching layouts and simplifying to cut gates and depth. They do not "
      "change the circuit's intended result.", "Lesson 11 concepts"),
    Q("qc-L200-043", 11, "concept", 2,
      "After transpiling, how should you confirm the circuit is still correct?",
      ["Check its behaviour, for example GHZ gives only all-0 or all-1", "Diff its text against the original",
       "Check that the gate count is unchanged", "Confirm it still uses exactly the same qubit indices as the original circuit"],
      "Transpiling legitimately changes gates, qubit indices and text; only behaviour must stay the same. Gate "
      "counts are expected to change.", "Lesson 11 concepts"),
    Q("qc-L200-044", 11, "design", 2,
      "You compare three backends for one circuit. Which metrics best capture the transpiler's cost on a noisy "
      "device?",
      ["Two-qubit gate count and depth after transpiling", "Number of lines in the OpenQASM export",
       "Total single-qubit gates before transpiling", "Number of classical bits measured"],
      "Two-qubit gates are the noisiest operations and depth sets exposure to decoherence, so those are what the lab "
      "measures. Pre-transpile counts ignore routing.", "Lesson 11 conceptSummary"),
]

L += [
    Q("qc-L200-045", 7, "concept", 2,
      "Why does Bernstein-Vazirani apply H to every input qubit AFTER the oracle query?",
      ["Interference turns the phase pattern (-1)^(s.x) into |s>", "To reset the ancilla before measurement",
       "To undo the oracle so the input qubits return to |0...0> before measuring", "To average out noise from the query"],
      "After kickback each input basis state carries the phase (-1)^(s.x); the H layer maps exactly that pattern to "
      "|s>. Undoing the oracle would erase the answer instead.", "Lesson 7 concepts"),
    Q("qc-L200-046", 8, "concept", 2,
      "What does Grover's diffusion operator do to the amplitudes?",
      ["Reflects them about their mean, boosting the marked ones", "Flips the sign of the marked states only",
       "Measures the register and restarts the search from the uniform superposition", "Sets every unmarked amplitude to zero"],
      "The oracle flips marked signs; diffusion then inverts about the mean, so the negative (marked) amplitudes "
      "grow. Sign-flipping is the oracle's job, not the diffuser's.", "Lesson 8 conceptSummary"),
    Q("qc-L200-047", 8, "scenario", 3,
      "A teammate hard-codes 2 Grover iterations for every search. For N = 64 with one marked item, what do qsim and "
      "the k_opt formula say?",
      [f"P = {P64_K2} at k = 2; k_opt = {K64} gives {P64_KOPT}", f"P = {P64_KOPT} at k = 2, already optimal",
       f"P = {G8[2]} at k = 2, as for N = 8", f"P = 1.0 at k = 2; k_opt = {K64} would overshoot the peak"],
      "theta = asin(1/8), so two iterations reach only sin^2(5 theta); the peak needs about (pi/4) sqrt(64) = 6. The "
      "iteration count must come from M and N, not from the N = 8 example.", "Lesson 8 conceptSummary"),
    Q("qc-L200-048", 9, "concept", 2,
      "In which kind of algorithm is the QFT used as a building block?",
      ["Period finding and phase estimation, as in Shor's algorithm", "The oracle of Bernstein-Vazirani",
       "Grover's diffusion operator", "Choosing where to insert routing SWAPs when transpiling to a line"],
      "The QFT turns a periodic amplitude pattern into peaks at multiples of N/r, which is what period finding "
      "needs. Grover's diffuser uses H and a multi-controlled Z, not a QFT.", "Lesson 9 concepts"),
    Q("qc-L200-049", 10, "concept", 2,
      "Why is a*cos(theta) + b*sin(theta) + c the right model to fit to <Z> of a single-qubit rotation sweep?",
      ["Expectation values of a 1-qubit rotation are sinusoidal in theta", "Any noisy data set can be fitted well by a three-term least-squares model",
       "Shot noise follows a cosine curve", "It is the only model numpy can fit"],
      "<Z> of RY(theta)|0> is cos(theta), and in general a single rotation gives a first-order sinusoid. Fitting the "
      "known shape is what lets the fit average away the noise.", "Lesson 10 concepts"),
    Q("qc-L200-050", 11, "concept", 1,
      "What does a device's coupling map describe?",
      ["Which physical qubit pairs support two-qubit gates", "Which gates the device accepts as its native basis set",
       "The error rate of every single-qubit gate", "The order in which qubits are measured"],
      "Two-qubit gates only run on linked pairs; the transpiler routes anything else with SWAPs. The basis gate "
      "list is a separate constraint.", "Lesson 11 overview"),
    Q("qc-L200-051", 11, "scenario", 2,
      "At optimization level 0 your GHZ star on a 5-qubit line gains many extra CX gates. What is the most direct "
      "way to cut them?",
      ["Transpile at a higher level so layout and routing search harder", "Measure fewer qubits at the end",
       "Increase the number of shots", "Replace the line backend with the same line backend reseeded"],
      "Levels 1-3 choose better initial layouts and routes and simplify gates. Shots and measurement do not change "
      "the transpiled gate count.", "Lesson 11 expectedResults"),
    Q("qc-L200-052", 10, "design", 2,
      "You must evaluate one ansatz at 500 parameter sets. Which design fits lab 10's approach?",
      ["One parameterized template, values bound in one primitive call", "500 hand-built circuits, one per set",
       "One circuit edited in place 500 times", "A new Parameter object for each of the 500 sets, all inside one large circuit"],
      "A template with a (500, p) value array is built once and swept in one call. Editing in place loses the "
      "template and invites binding mistakes.", "Lesson 10 overview"),
]

QUESTIONS = L
