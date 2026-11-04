"""L100 question bank data (lessons 1-6). Correct option first; numbers computed below with numpy / qsim."""
import math

import numpy as np

from qbank_common import Q, fmt
from qsim import statevector as sv

# ---------- computed values ----------
MEM_30 = 2 ** 30 * 16 / 2 ** 30                                   # GiB for a 30-qubit complex128 statevector
MAX_Q_8GIB = max(n for n in range(1, 64) if 2 ** n * 16 <= 8 * 2 ** 30)
P1_COMPLEX = fmt(abs(0.8j) ** 2, 2)
XH = np.round(sv.run(1, [sv.x(0), sv.h(0)]).real, 4).tolist()
SHOTS_001 = round(0.5 * 0.5 / 0.01 ** 2)
SE_P02 = fmt(math.sqrt(0.2 * 0.8 / 400), 3)
HALF_95 = round(1.96 * math.sqrt(4000 * 0.25))
RANGE_4000 = (2000 - HALF_95, 2000 + HALF_95)
RANGE_1SE = (2000 - round(math.sqrt(4000 * 0.25)), 2000 + round(math.sqrt(4000 * 0.25)))
SUSPECT = [k for k in (560, 470, 515, 529) if abs(k - 500) > 1.96 * math.sqrt(1000 * 0.25)]
assert SUSPECT == [560]
AMP = np.array([0.5, 0.5, 0.5, -0.5])                              # index order 00, 01, 10, 11
DET = fmt(AMP[0] * AMP[3] - AMP[1] * AMP[2], 2)
CIRQ_TO_QISKIT = "110"[::-1]

L = []
# ---------------- Lesson 1: setup ----------------
L += [
    Q("qc-L100-001", 1, "concept", 1,
      "In lab 01, which object actually executes the 1-qubit circuit and returns counts?",
      ["qiskit.primitives.StatevectorSampler", "transpile(), which runs the circuit while rewriting it",
       "QuantumCircuit.measure_all(), which samples the qubit", "The pinned requirements.txt file"],
      "StatevectorSampler holds the 2^n amplitudes and samples shots. transpile() only rewrites the circuit into the "
      "basis gates; it never runs anything.", "Lesson 1 checkYourself"),
    Q("qc-L100-002", 1, "concept", 1,
      "Why does the setup lesson pin exact package versions (for example qiskit 2.6.1, cirq 1.7.0)?",
      ["Quantum SDK APIs change between releases, so pins keep the labs reproducible",
       "Pinned versions make the simulator run faster because old releases skip optimisation passes",
       "Pinning seeds the random number generator so counts repeat",
       "A cloud account requires exact versions before it will accept jobs"],
      "Quantum SDKs rename and remove APIs between major releases; pins in a venv keep the whole chain reproducible. "
      "Repeatable counts come from a sampler seed, not from version pins.", "Lesson 1 concepts"),
    Q("qc-L100-003", 1, "calculation", 2,
      "A statevector simulator stores 2^n complex128 amplitudes (16 bytes each). About how much memory does a "
      "30-qubit statevector need?",
      [f"{MEM_30:.0f} GiB", "480 bytes", "1 GiB", "30 GiB"],
      "2^30 amplitudes x 16 bytes = 16 GiB. 480 bytes (30 x 16) is the classic mistake of counting qubits instead of "
      "amplitudes: memory doubles with every added qubit.", "Lesson 1 checkYourself"),
    Q("qc-L100-004", 1, "calculation", 2,
      "Your machine has 8 GiB free for one complex128 statevector (16 bytes per amplitude). What is the largest number "
      "of qubits you can simulate?",
      [str(MAX_Q_8GIB), str(MAX_Q_8GIB + 1), str(MAX_Q_8GIB + 4), str(MAX_Q_8GIB - 6)],
      f"2^{MAX_Q_8GIB} x 16 B = 8 GiB fits exactly; one more qubit doubles it to 16 GiB. Memory grows as 2^n, so a few "
      "extra GiB never buys more than a qubit or so.", "Lesson 1 conceptSummary"),
    Q("qc-L100-005", 1, "debugging", 1,
      "Running check_env.py prints ModuleNotFoundError: No module named 'qiskit'. What is the right fix?",
      ["Activate the lab's venv, then pip install -r labs/L100/requirements.txt",
       "pip install the newest qiskit globally, without a pin, so every lab gets the latest API",
       "Install only qiskit-aer, which provides the qiskit package",
       "Switch to Python 3.9, which ships with qiskit built in"],
      "The packages live in the lab's virtual environment; installing the pinned requirements there fixes it. An "
      "unpinned global install may pull a release with a different API.", "Lesson 1 troubleshooting"),
    Q("qc-L100-006", 1, "scenario", 2,
      "On Python 3.10, pip reports that it cannot find cirq 1.7.0 or qiskit-aer 0.18.2. What should you do?",
      ["Use Python 3.11-3.13, which those pinned versions require",
       "Lower the pins to whatever versions pip can find for 3.10",
       "Skip the venv and install the packages with sudo",
       "Ignore it: cirq is never used anywhere in L100"],
      "cirq 1.7.0 and qiskit-aer 0.18.2 need Python 3.11 or newer. Loosening the pins hides the problem and breaks "
      "reproducibility, and cirq is needed in lesson 6.", "Lesson 1 troubleshooting"),
    Q("qc-L100-007", 1, "code-reading", 1,
      "This numpy/qsim version of lab 01 samples 100 shots of X|0>. What does it print?",
      ["{'0': 0, '1': 100}", "{'0': 100, '1': 0}", "{'0': 50, '1': 50}", "{'0': 48, '1': 52}"],
      "X|0> = |1>, so P(1) = 1 and every one of the 100 shots reads 1. A 50/50 split would need H, not X.",
      "Lesson 1 expectedResults",
      code='''
import numpy as np
from qsim import statevector as sv

state = sv.run(1, [sv.x(0)])
p = np.abs(state) ** 2
counts = np.random.default_rng(7).multinomial(100, p)
print(dict(zip(["0", "1"], counts.tolist())))
'''),
]

# ---------------- Lesson 2: qubits and gates ----------------
L += [
    Q("qc-L100-008", 2, "calculation", 2,
      "A qubit is in the state 0.6|0> + 0.8i|1>. What is the probability of measuring 1?",
      [f"{P1_COMPLEX}", "0.8", "0.64i", "0.36"],
      "Probability is |amplitude|^2 = |0.8i|^2 = 0.64; the i only changes the phase. 0.8 is the amplitude itself, "
      "not its squared magnitude.", "Lesson 2 conceptSummary"),
    Q("qc-L100-009", 2, "code-reading", 1,
      "What does this qsim snippet print?",
      ["{'0': 1.0}", "{'0': 0.5, '1': 0.5}", "{'1': 1.0}", "{'0': 0.25, '1': 0.75}"],
      "H is its own inverse, so H then H returns |0> exactly (interference). Expecting 50/50 treats the second H as "
      "a second coin toss.", "Lesson 2 concepts",
      code='''
from qsim import statevector as sv

state = sv.run(1, [sv.h(0), sv.h(0)])
print(sv.probabilities(state))
'''),
    Q("qc-L100-010", 2, "concept", 1,
      "A 2-qubit Qiskit result reads '10'. Which qubit was measured as 1?",
      ["Qubit 1, because qubit 0 is the rightmost character", "Qubit 0, because it is the leftmost character",
       "Both qubits, since '10' is the binary number two", "Neither: '10' is a register name, not bits"],
      "Qiskit prints bitstrings little-endian: qubit 0 is the rightmost bit. Reading left-to-right as qubit 0 first "
      "is the most common bit-order mistake.", "Lesson 2 checkYourself"),
    Q("qc-L100-011", 2, "code-reading", 2,
      "The simulator uses Qiskit's bit order. What does this print?",
      ["{'001': 1.0}", "{'100': 1.0}", "{'010': 1.0}", "{'000': 0.5, '001': 0.5}"],
      "Only qubit 0 is flipped, and qubit 0 is printed as the rightmost bit, giving '001'. '100' is what a "
      "big-endian (qubit 0 first) reading would show.", "Lesson 2 expectedResults (x_on_q0_of_2)",
      code='''
from qsim import statevector as sv

state = sv.run(3, [sv.x(0)])
print(sv.probabilities(state))
'''),
    Q("qc-L100-012", 2, "calculation", 2,
      "Starting from |0>, you apply X and then H. Which state results (qsim amplitudes rounded to 4 places)?",
      [f"{XH} - 50/50 odds, minus sign on |1>", "[0.7071, 0.7071] - exactly the same state that H|0> produces",
       "[0.0, 1.0] - H undoes the X", "[1.0, 0.0] - X and H cancel each other"],
      "X gives |1>, and H|1> = (|0> - |1>)/sqrt(2). The probabilities are 50/50 like H|0>, which is why that option is "
      "tempting, but the minus sign is real and matters for interference.", "Lesson 2 conceptSummary"),
    Q("qc-L100-013", 2, "debugging", 2,
      "A circuit built with qc.measure(0, 0) on a register named 'c' fails at result[0].data.meas with "
      "AttributeError: 'DataBin' object has no attribute 'meas'. What is the fix?",
      ["Read the register name from qc.cregs[0].name, or use measure_all()", "Increase the number of shots to 1000",
       "Add qc.barrier() before measuring", "Replace StatevectorSampler with Aer's SamplerV2, which always names the register 'meas'"],
      "Results are stored under the classical register's name; only measure_all() names it 'meas'. Shots and "
      "barriers do not change the register name.", "Lesson 2 troubleshooting"),
    Q("qc-L100-014", 2, "concept", 1,
      "Running H then measure for 1000 shots gave 489 zeros and 511 ones. What does this show?",
      ["Normal sampling: each shot is an independent random draw", "The H gate is miscalibrated in the simulator",
       "The qubit was not reset to |0> before the run", "Measurement changed the probabilities halfway through"],
      "With P = 0.5 each, counts scatter around 500 from shot to shot; an exact 500/500 would be the surprise. A "
      "noise-free simulator has no miscalibrated gates.", "Lesson 2 troubleshooting"),
    Q("qc-L100-015", 2, "concept", 2,
      "How does a measurement differ from a gate such as X or H?",
      ["It returns a classical bit and cannot be undone", "It is a reversible 2x2 matrix like every gate",
       "It only works on qubits that are already in |1>", "It always returns 0 when the qubit is in superposition"],
      "Gates are reversible matrices; measurement turns amplitudes into one classical outcome with probability "
      "|amplitude|^2 and the superposition is lost.", "Lesson 2 overview"),
]

# ---------------- Lesson 3: shots, counts, probability ----------------
L += [
    Q("qc-L100-016", 3, "calculation", 2,
      "You want P('1') to within +/-0.01 (one standard error) for a 50/50 qubit. Using SE = sqrt(p(1-p)/N), "
      "how many shots do you need?",
      [str(SHOTS_001), "100", "10000", "50"],
      "N = p(1-p)/SE^2 = 0.25/0.0001 = 2500. 10000 shots is the answer for +/-0.005: halving the error costs 4x the "
      "shots.", "Lesson 3 checkYourself"),
    Q("qc-L100-017", 3, "calculation", 2,
      "What is the standard error of an estimated probability when the true p = 0.2 and you take 400 shots?",
      [str(SE_P02), "0.04", "0.0004", "0.05"],
      "SE = sqrt(0.2 x 0.8 / 400) = 0.02. 0.0004 forgets the square root; 0.04 forgets to divide by N inside the root.",
      "Lesson 3 conceptSummary"),
    Q("qc-L100-018", 3, "calculation", 2,
      "A 50/50 qubit is measured 4000 times. Using +/-1.96 standard errors of the count (sqrt(N p (1-p))), which "
      "range should contain the number of ones about 95% of the time?",
      [f"{RANGE_4000[0]}-{RANGE_4000[1]}", f"{RANGE_1SE[0]}-{RANGE_1SE[1]}", "1800-2200", "1996-2004"],
      "The count's SE is sqrt(4000 x 0.25) = 31.6, so 1.96 SE is about 62. 1968-2032 uses one standard error only "
      "(about 68% coverage).", "Lesson 3 checkYourself"),
    Q("qc-L100-019", 3, "calculation", 2,
      "Four learners each ran H + measure for 1000 shots and got these numbers of ones. Which result falls outside "
      "the ~95% range (500 +/- 1.96 x sqrt(1000 x 0.25)) and deserves a closer look?",
      ["560", "470", "515", "529"],
      "The 95% range is about 469-531; 560 is roughly 3.8 standard errors away. 470 looks low but is just inside "
      "the range.", "Lesson 3 checkYourself"),
    Q("qc-L100-020", 3, "concept", 1,
      "You increase the shot count from 100 to 10,000. How does the statistical error of P('1') change?",
      ["It shrinks about 10x, since error scales as 1/sqrt(shots)", "It shrinks 100x, in proportion to the shots",
       "It stays the same, because only a fixed seed can reduce the statistical error", "It disappears completely above 1000 shots"],
      "Error scales as 1/sqrt(N): 100x more shots gives sqrt(100) = 10x less error. Expecting a 100x improvement "
      "confuses N with sqrt(N).", "Lesson 3 concepts"),
    Q("qc-L100-021", 3, "code-reading", 1,
      "What does this print?",
      ["True 100", "False 100", "True 50", "False 200"],
      "Two generators with the same seed replay the same random draws, so the counts are identical and each sums "
      "to the 100 shots. A seed makes runs repeatable, not more accurate.", "Lesson 3 concepts",
      code='''
import numpy as np

a = np.random.default_rng(2024).multinomial(100, [0.5, 0.5])
b = np.random.default_rng(2024).multinomial(100, [0.5, 0.5])
print(bool((a == b).all()), int(a.sum()))
'''),
    Q("qc-L100-022", 3, "scenario", 2,
      "A unit test asserts that 1000 unseeded H shots give exactly {'0': 500, '1': 500}; it fails on most machines. "
      "What is the best change?",
      ["Pass a fixed seed and compare P('1') with a statistical tolerance", "Retry the test until it passes once",
       "Raise the shots to 1,000,000 so an exact 50/50 split becomes reliable enough to assert", "Delete the test because sampling cannot be tested"],
      "Seeds make the run repeatable and a tolerance accepts normal shot noise. More shots shrink the noise but "
      "almost never give an exact 50/50 split.", "Lesson 3 troubleshooting"),
    Q("qc-L100-023", 3, "concept", 2,
      "You seed Qiskit's StatevectorSampler with seed=7 and Cirq's simulator with seed=7. Will the counts match?",
      ["No: each simulator has its own RNG, so equal seeds are unrelated", "Yes: seed 7 is a universal sequence",
       "Yes, but only when both use 1000 shots", "No, because Cirq ignores the seed argument and always draws fresh random numbers"],
      "A seed only fixes its own simulator's random stream; both are seeded and repeatable, but not with each "
      "other. Compare distributions across frameworks instead.", "Lesson 3 checkYourself"),
]

# ---------------- Lesson 4: Bell pair ----------------
L += [
    Q("qc-L100-024", 4, "code-reading", 1,
      "What does this Bell-pair snippet print?",
      ["{'00': 0.5, '11': 0.5}", "{'00': 0.25, '01': 0.25, '10': 0.25, '11': 0.25}", "{'00': 0.5, '01': 0.5}",
       "{'01': 0.5, '10': 0.5}"],
      "H then CNOT gives (|00> + |11>)/sqrt(2): the qubits always agree. Four equal outcomes would be two independent "
      "coin flips without the CNOT's correlation.", "Lesson 4 expectedResults",
      code='''
from qsim import statevector as sv

state = sv.run(2, [sv.h(0), sv.cx(0, 1)])
print(sv.probabilities(state))
'''),
    Q("qc-L100-025", 4, "debugging", 2,
      "A learner wrote the Bell circuit with the gates in the wrong order. What does this print?",
      ["{'00': 0.5, '01': 0.5}", "{'00': 0.5, '11': 0.5}", "{'00': 0.5, '10': 0.5}", "{'00': 1.0}"],
      "CX acts first on |00> and does nothing; H then puts only qubit 0 in superposition, so '00' and '01' appear. "
      "Getting '01' from an ideal simulator means checking gate order (H before CX).", "Lesson 4 troubleshooting",
      code='''
from qsim import statevector as sv

state = sv.run(2, [sv.cx(0, 1), sv.h(0)])
print(sv.probabilities(state))
'''),
    Q("qc-L100-026", 4, "calculation", 3,
      "A 2-qubit state has amplitudes [0.5, 0.5, 0.5, -0.5] for |00>, |01>, |10>, |11>. Compute a00*a11 - a01*a10. "
      "Is the state entangled?",
      [f"{DET}, so it is entangled", "0, so it is a product state", "0.5, so it is a product state",
       "-0.25, so it is entangled"],
      "0.5 x (-0.5) - 0.5 x 0.5 = -0.5, which is not 0, so the state cannot be written as a product. Equal-looking "
      "magnitudes tempt a 'product' answer, but the minus sign makes the difference.", "Lesson 4 checkYourself"),
    Q("qc-L100-027", 4, "code-reading", 2,
      "A Bell pair is followed by X on qubit 1. What does this print?",
      ["{'01': 0.5, '10': 0.5}", "{'00': 0.5, '11': 0.5}", "{'10': 0.5, '11': 0.5}", "{'00': 0.5, '01': 0.5}"],
      "(|00> + |11>)/sqrt(2) with qubit 1 flipped becomes (|10> + |01>)/sqrt(2): the qubits now always disagree. "
      "X keeps the correlation; it only changes its sign.", "Lesson 4 concepts",
      code='''
from qsim import statevector as sv

state = sv.run(2, [sv.h(0), sv.cx(0, 1), sv.x(1)])
print(sv.probabilities(state))
'''),
    Q("qc-L100-028", 4, "concept", 2,
      "In a Bell pair, Alice measures qubit 0 before Bob measures qubit 1. What does Bob see if he looks only at his "
      "own results?",
      ["50/50 random bits, unchanged by Alice's measurement", "Always 0, because Alice's measurement collapses it",
       "Always the opposite of Alice's bit", "A bias toward 1 that reveals Alice's choice"],
      "Bob's qubit alone stays 50/50; the correlation only appears when both lists of results are compared. That is "
      "why entanglement cannot send signals.", "Lesson 4 checkYourself"),
    Q("qc-L100-029", 4, "scenario", 2,
      "Your ideal-simulator Bell test passes, but on real hardware 3% of shots read '01' or '10'. What is the "
      "most likely explanation?",
      ["Hardware noise; impossible outcomes appear with small counts", "The CNOT's control and target are swapped",
       "Shot noise, which also produces '01' on the ideal simulator", "Entanglement only works below 100 shots"],
      "Real devices add gate and readout errors, so ideal-zero outcomes show up rarely. Swapping control and target "
      "on |+0> would give a very different result, not a 3% leak.", "Lesson 4 simulatorVsReal"),
    Q("qc-L100-030", 4, "concept", 2,
      "Why does the Bell lab check exact statevector probabilities and sampled counts separately?",
      ["Probabilities test the circuit exactly; counts test sampling with tolerance",
       "Counts are always exact, so probabilities are redundant", "The statevector includes hardware noise",
       "Sampled counts are only needed for circuits with one qubit; larger ones use the statevector"],
      "The statevector gives the exact distribution (0.5/0.5) with no shot noise, while counts must be checked with a "
      "tolerance or a subset test. Counts are samples, never exact probabilities.", "Lesson 4 concepts"),
]

# ---------------- Lesson 5: OpenQASM ----------------
L += [
    Q("qc-L100-031", 5, "concept", 1,
      "Why does the lab verify an OpenQASM round-trip by comparing unitaries or seeded counts, not the .qasm text?",
      ["Exporters can format the same circuit differently", "Text comparison is slower than simulation",
       "OpenQASM files cannot be read by Python", "The text changes every time you open the file"],
      "Two tools may write different but equivalent text (spacing, gate names, register names). Behaviour is what must "
      "match.", "Lesson 5 checkYourself"),
    Q("qc-L100-032", 5, "concept", 1,
      "Which line in an OpenQASM 3 file makes standard gates such as h and cx available?",
      ['include "stdgates.inc";', "OPENQASM 3.0;", "qubit[2] q;", 'include "qelib1.inc"; (the OpenQASM 2 library)'],
      "stdgates.inc defines the standard gate library. 'OPENQASM 3.0;' only declares the language version.",
      "Lesson 5 checkYourself"),
    Q("qc-L100-033", 5, "code-reading", 2,
      "Simulated ideally (Qiskit bit order), what probabilities does this OpenQASM 3 program produce?",
      ["{'00': 0.5, '11': 0.5}", "{'00': 0.5, '10': 0.5}", "{'00': 0.5, '01': 0.5}", "{'01': 0.5, '10': 0.5}"],
      "H on q[1] then cx q[1], q[0] (control first) entangles both qubits, giving a Bell pair. Reading the control "
      "as the second argument would leave q[0] untouched.", "Lesson 5 concepts",
      code='''
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[1];
cx q[1], q[0];
c = measure q;
'''),
    Q("qc-L100-034", 5, "code-reading", 3,
      "RZ(pi) and Z differ by a global phase. What does this print?",
      ["False True", "True True", "False False", "True False"],
      "RZ(pi) = diag(-i, i) = -i Z, so the matrices are not equal entry by entry, but they are equal up to a global "
      "phase, which no measurement can see. Operator.equiv makes the same comparison.", "Lesson 5 concepts",
      code='''
import numpy as np
from qsim import statevector as sv

u1 = sv.unitary(1, [(sv.rz(np.pi), 0, ())])
u2 = sv.unitary(1, [(sv.Z, 0, ())])
print(np.allclose(u1, u2), sv.equal_up_to_global_phase(u1, u2))
'''),
    Q("qc-L100-035", 5, "debugging", 1,
      "qasm3.loads(text) raises an error mentioning qiskit_qasm3_import. What should you do?",
      ["pip install qiskit-qasm3-import==0.6.0", "Switch the export to qasm3.dumps", "Delete the include line",
       "Upgrade numpy to the newest release"],
      "qasm3.loads depends on the separate qiskit-qasm3-import package (pinned at 0.6.0). dumps writes text and "
      "does not need it.", "Lesson 5 troubleshooting"),
    Q("qc-L100-036", 5, "scenario", 2,
      "A colleague's tool rejects your exported OpenQASM 3 file. What is the most portable next step?",
      ["Export OpenQASM 2 or keep to stdgates.inc gates", "Send them your Python source instead",
       "Rename the file extension from .qasm to .txt", "Add experimental export flags to the file"],
      "Many tools support only a subset of OpenQASM 3; OpenQASM 2 or standard gates are widely accepted. "
      "Experimental flags make the file less portable, not more.", "Lesson 5 troubleshooting"),
    Q("qc-L100-037", 5, "concept", 2,
      "Someone emails you an OpenQASM file to load into your pipeline. What does the lesson's caution recommend?",
      ["Load only from trusted sources and review it like code", "Load it directly; QASM cannot contain errors",
       "Convert it to OpenQASM 3 with experimental flags first", "Paste it into an AI model with your API token"],
      "A circuit file is input to your tools and should be reviewed like code; never put secrets in a prompt. QASM "
      "files can certainly be wrong or unexpected.", "Lesson 5 caution"),
]

# ---------------- Lesson 6: two frameworks ----------------
L += [
    Q("qc-L100-038", 6, "concept", 2,
      "Why can a Bell pair NOT catch a bit-order bug when you compare Qiskit and Cirq?",
      ["'00' and '11' read the same when reversed", "Bell pairs give random results in Cirq",
       "Cirq cannot build a CNOT gate", "Bit order only matters for circuits with three qubits"],
      "The only outcomes are symmetric strings, so reversing them changes nothing. An asymmetric probe like X on qubit "
      "0 exposes the bug.", "Lesson 6 checkYourself"),
    Q("qc-L100-039", 6, "code-reading", 2,
      "Cirq returns the histogram {2: 1000} for X on q0 (measured as q0, q1). What does this normalisation print?",
      ["{'01': 1000}", "{'10': 1000}", "{'2': 1000}", "{'00': 1000}"],
      "Cirq's integer 2 is '10' with q0 as the highest bit; reversing gives '01', Qiskit's order with q0 rightmost. "
      "Stopping at '10' is the raw Cirq order.", "Lesson 6 expectedResults",
      code='''
hist = {2: 1000}
raw = {format(k, "02b"): v for k, v in hist.items()}


def to_qiskit_order(counts):
    return {bits[::-1]: v for bits, v in counts.items()}


print(to_qiskit_order(raw))
'''),
    Q("qc-L100-040", 6, "concept", 2,
      "A 3-qubit Cirq histogram key prints as '110' with q0 first (q0 q1 q2). What is the same outcome in Qiskit's "
      "order (q2 q1 q0)?",
      [CIRQ_TO_QISKIT, "110", "001", "100"],
      "Reverse the string: q0=1, q1=1, q2=0 becomes '011' with q0 rightmost. Leaving it as '110' is the silent "
      "bit-order bug.", "Lesson 6 concepts"),
    Q("qc-L100-041", 6, "code-reading", 2,
      "Two frameworks ran a Bell pair. This compares their distributions with total variation distance. What does "
      "it print?",
      ["0.019 True", "0.038 True", "0.019 False", "19 False"],
      "TVD = 0.5 x (|0.508-0.489| + |0.492-0.511|) = 0.019, inside the 0.05 tolerance. 0.038 forgets the 0.5 factor.",
      "Lesson 6 concepts",
      code='''
qiskit = {"00": 508, "11": 492}
cirq = {"00": 489, "11": 511}
keys = set(qiskit) | set(cirq)
tvd = 0.5 * sum(abs(qiskit.get(k, 0) / 1000 - cirq.get(k, 0) / 1000) for k in keys)
print(round(tvd, 3), tvd < 0.05)
'''),
    Q("qc-L100-042", 6, "debugging", 2,
      "A cross-framework test does assert qiskit_counts == cirq_counts for X on qubit 0 and fails. What should "
      "change?",
      ["Normalise bit order, then compare distributions with a tolerance", "Use the same seed in both frameworks",
       "Increase both runs to 10,000 shots", "Replace the X probe with a Bell pair, whose result is the same in every framework"],
      "Cirq's raw keys are reversed and each simulator has its own RNG, so raw dicts never match exactly. A Bell "
      "pair would just hide the bit-order bug.", "Lesson 6 troubleshooting"),
    Q("qc-L100-043", 6, "scenario", 2,
      "You must add one regression circuit that proves your Qiskit-vs-Cirq comparison handles bit order. Which "
      "circuit should you pick?",
      ["X on qubit 0 only of 2 qubits", "A Bell pair (H, CX)", "H on both qubits", "No gates, so every result is '00'"],
      "X on q0 gives the asymmetric result '01' that flips to '10' if the order is wrong. The other three give "
      "symmetric outcomes that look identical either way.", "Lesson 6 caution"),
    Q("qc-L100-044", 6, "concept", 1,
      "Which statement about Qiskit and Cirq is accurate?",
      ["They share gates and physics but differ in result conventions", "Their H gates are different matrices",
       "Cirq cannot simulate entanglement", "Qiskit counts are always more accurate than Cirq's, because Qiskit is the reference"],
      "qc.h(0) and cirq.H(q0) are the same gate; the differences are API names, bit order and RNGs. Neither "
      "simulator is more accurate: both are ideal.", "Lesson 6 conceptSummary"),
    Q("qc-L100-045", 6, "design", 2,
      "You are writing a helper that compares any two frameworks' results. Which design is most robust?",
      ["Convert both to one bit order and compare probabilities", "Compare the raw count dicts key by key",
       "Compare only the most frequent outcome's exact count, since it is the most stable value", "Sort both dicts by value and compare the lists"],
      "One canonical bit order plus normalised distributions with tolerances catches real differences without "
      "flagging RNG noise. Exact counts differ even when both frameworks are correct.", "Lesson 6 concepts"),
]

L += [
    Q("qc-L100-046", 1, "concept", 1,
      "What happens to a statevector simulator's memory when you add one more qubit?",
      ["It doubles, because the amplitude count doubles", "It grows by 16 bytes for the new amplitude",
       "It grows by a fixed 1 GiB per qubit", "It stays the same until 30 qubits"],
      "n qubits need 2^n amplitudes, so n + 1 qubits need twice as many. Adding 16 bytes is the linear-thinking "
      "mistake.", "Lesson 1 conceptSummary"),
    Q("qc-L100-047", 1, "concept", 1,
      "Why can every L100 lab run with no account, token or network access?",
      ["A local simulator on your CPU stands in for hardware", "The SDK caches results from a cloud device",
       "Qiskit includes a free remote quantum computer", "The labs replay counts that were recorded on hardware and stored in the repository"],
      "StatevectorSampler and cirq.Simulator compute the circuit locally. Nothing is fetched or replayed; you would "
      "only need tokens for real hardware, and those must never be committed.", "Lesson 1 overview"),
    Q("qc-L100-048", 2, "scenario", 2,
      "You need a 2-qubit test circuit whose correct Qiskit result is exactly '10'. Which gate do you apply to |00>?",
      ["X on qubit 1", "X on qubit 0", "H on qubit 1", "X on both qubits"],
      "Qiskit prints qubit 1 on the left, so '10' means qubit 1 is 1 and qubit 0 is 0. X on qubit 0 would print '01'; "
      "H would give a 50/50 mix.", "Lesson 2 concepts"),
    Q("qc-L100-049", 3, "concept", 2,
      "Which statement best describes the counts a sampler returns?",
      ["Random samples drawn from the circuit's exact distribution", "The exact probabilities multiplied by shots",
       "Fixed values that never change once the circuit and the shot count are fixed", "Hardware noise added to the probabilities"],
      "Each shot is one random draw, so counts scatter around N x p. Treating counts as exact probabilities is the "
      "root of flaky exact-match tests; an ideal simulator has no hardware noise.", "Lesson 3 concepts"),
    Q("qc-L100-050", 4, "concept", 2,
      "What makes the Bell state (|00> + |11>)/sqrt(2) entangled?",
      ["It cannot be written as a product of two 1-qubit states", "The two qubits are physically wired together by the CNOT gate's coupler",
       "Both qubits are guaranteed to read 1", "Both qubits have the same amplitudes"],
      "Entanglement is a property of the joint state: no pair of 1-qubit states multiplies to it. Wiring is not "
      "required and each qubit alone is random, not fixed.", "Lesson 4 conceptSummary"),
    Q("qc-L100-051", 5, "concept", 2,
      "When would you export OpenQASM 2 (qasm2.dumps) rather than OpenQASM 3?",
      ["When the receiving tool only reads OpenQASM 2", "When you need more accurate simulation results",
       "When the circuit contains measurements", "When the circuit uses the cx gate"],
      "OpenQASM 2 is older and simpler but widely accepted; both formats describe the same circuit exactly. "
      "Measurements and cx exist in both versions.", "Lesson 5 concepts"),
]

QUESTIONS = L
