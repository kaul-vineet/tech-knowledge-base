"""L400 question bank data (lessons 17-22). Correct option first; numbers computed from the labs' models."""
import math

from qbank_common import Q, fmt

# ---------- lesson 17: modelled wall time (Costs in labs/L400/17-hybrid-architecture/backend.py) ----------
ITERS, STARTS, PER_CIRCUIT, TRANSPILE, CLASSICAL = 30, 4, 0.02, 0.5, 0.05
CIRCUITS = ITERS * 2 * STARTS


def wall(jobs, queue):
    return round(jobs * queue + TRANSPILE + CIRCUITS * PER_CIRCUIT + ITERS * CLASSICAL, 2)


BATCH_Q10, SYNC_Q10 = wall(ITERS, 10.0), wall(CIRCUITS, 10.0)
BILLED = round(CIRCUITS * PER_CIRCUIT, 2)
BACKOFF_3 = sum(1.0 * 2 ** (a - 1) for a in (1, 2, 3))

# ---------- lesson 18 ----------
TTS_03 = round(200 * math.log(0.01) / math.log(1 - 0.3))
SE_10 = fmt(math.sqrt(0.4 * 0.6 / 10), 2)


# ---------- lesson 19: surface-code model of estimate_lab.py ----------
def p_l(d, p=1e-3):
    return 0.03 * (p / 0.01) ** ((d + 1) / 2)


def distance(q, cycles, budget=0.01):
    return next(d for d in range(3, 102, 2) if q * cycles * p_l(d) <= budget)


RSA_Q = math.ceil(3 * 2048 + 0.002 * 2048 * math.log2(2048))
RSA_PHYS = RSA_Q * 2 * 27 ** 2
RSA_CYCLES = round(500 * 2048 ** 2 + 2048 ** 2 * math.log2(2048))
RSA_HOURS = fmt(RSA_CYCLES * 27 * 1e-6 / 3600, 1)
D_50 = distance(50, 10_000)
PHYS_50 = 50 * 2 * D_50 ** 2
PL_5 = p_l(5)
T_ROT = math.ceil(3 * math.log2(1 / 1e-6))

# ---------- lesson 20 ----------
ESP_12 = fmt(0.99 ** 12 * 0.98 ** 5, 4)
DIRECT_BAD, DETOUR = fmt(0.85, 4), fmt(0.99 ** 4, 4)
LAYOUTS = math.perm(8, 5)

# ---------- lesson 21 ----------
Y_MIG, Z_CRQC = 3, 9
SYSTEMS = {"archive (10 years)": 10, "replication (7 years)": 7, "telemetry (5 years)": 5, "chat (1 year)": 1}
P1 = [k for k, x in SYSTEMS.items() if x + Y_MIG > Z_CRQC]
MLKEM_PK, MLKEM_CT, X25519 = 1184, 1088, 32
HYB = (MLKEM_PK + X25519, MLKEM_CT + X25519)
ECC_256 = 9 * 256 + 2 * math.ceil(math.log2(256)) + 10

# ---------- lesson 22 ----------
RAW, MITIGATED, IDEAL = 6.774, 6.8549, 7.3525
GAP_CLOSED = fmt((MITIGATED - RAW) / (IDEAL - RAW), 2)

L = []
# ---------------- Lesson 17: hybrid architecture ----------------
CACHE_NAIVE = '''
import numpy as np

cache, transpiles = {}, 0
rng = np.random.default_rng(0)
for iteration in range(30):
    for circuit in range(8):                       # 4 starts x 2 SPSA evaluations
        params = tuple(np.round(rng.uniform(0, 3, 2), 12))
        key = ("qaoa-maxcut", params, "line-8", 1)
        if key not in cache:
            cache[key] = "compiled"
            transpiles += 1
print(transpiles)
'''
CACHE_FIXED = '''
import numpy as np

cache, transpiles, hits = {}, 0, 0
rng = np.random.default_rng(0)
for iteration in range(30):
    for circuit in range(8):
        params = tuple(np.round(rng.uniform(0, 3, 2), 12))   # bound at run time, not compiled in
        key = ("qaoa-maxcut", "line-8", 1)
        if key in cache:
            hits += 1
        else:
            cache[key] = "compiled"
            transpiles += 1
print(transpiles, hits)
'''
L += [
    Q("qc-L400-001", 17, "calculation", 3,
      "Lab 17's model: 240 circuits over 30 optimiser steps, 0.02 s execution per circuit, 0.5 s for the one "
      "transpile, 0.05 s classical work per step. If the queue wait rises from 2 s to 10 s per job, what is the "
      "batched mode's modelled wall time?",
      [f"{BATCH_Q10} s", f"{SYNC_Q10} s", "66.8 s", "300.0 s"],
      "30 jobs x 10 s + 0.5 + 240 x 0.02 + 30 x 0.05 = 306.8 s. 2406.8 s is the sync loop, which pays the queue for "
      "every one of the 240 circuits.", "Lesson 17 designBrief / options"),
    Q("qc-L400-002", 17, "concept", 3,
      "In the same model, what device time is billed for the sync loop and for batched jobs?",
      [f"{BILLED} s for both", f"{BILLED} s sync, 0.16 s batched", "486.8 s sync, 66.8 s batched", "480 s for both"],
      "Both modes execute the same 240 circuits at 0.02 s each; queue waiting is wall time, not device time. "
      "Treating wall time as billed time is the tempting mistake.", "Lesson 17 checkYourself"),
    Q("qc-L400-003", 17, "debugging", 3,
      "A transpile cache built like this reports 240 transpiles for 240 circuits of one template. What is wrong?",
      ["The key includes bound parameter values, so every angle misses", "The cache dict is cleared each iteration",
       "The template name should be hashed first", "The optimisation level must be left out of the key, since it never changes"],
      "Angles change every step, so a key containing them never repeats. Key on template structure, target and "
      "optimisation level; the level belongs in the key because it changes the compiled circuit.",
      "Lesson 17 failureLab", code=CACHE_NAIVE),
    Q("qc-L400-004", 17, "code-reading", 3,
      "With the cache keyed on structure, target and optimisation level only, what does this print?",
      ["1 239", "240 0", "30 210", "8 232"],
      "The key never changes, so the first circuit compiles and the other 239 hit the cache. One transpile per "
      "template and target is exactly the fitness threshold.", "Lesson 17 fitnessFunction", code=CACHE_FIXED),
    Q("qc-L400-005", 17, "code-reading", 3,
      "This mirrors the orchestrator's retry loop for a job that fails on attempts 1-3 and succeeds on attempt 4. "
      "What does it print?",
      [f"4 {BACKOFF_3}", "4 3.0", "3 15.0", "4 8.0"],
      "Sleeps of 1, 2 and 4 s follow the three failures, then attempt 4 returns: 7 s in total. 15 s would include a "
      "fourth sleep that never happens.", "Lesson 17 code",
      code='''
max_attempts, backoff_s, failing = 4, 1.0, {1, 2, 3}
slept = 0.0
for attempt in range(1, max_attempts + 1):
    if attempt not in failing:
        break
    if attempt == max_attempts:
        raise RuntimeError("gave up")
    slept += backoff_s * 2 ** (attempt - 1)
print(attempt, slept)
'''),
    Q("qc-L400-006", 17, "concept", 3,
      "What makes a retried job safe, so that best_ratio stays 0.6922 with injected failures?",
      ["Each circuit carries an orchestrator-chosen seed independent of attempts", "The backend caches the last result",
       "Retries use more shots so the failed attempt's noise averages out in the result", "Failures are silently dropped from the batch"],
      "Seeds derived from (run seed, iteration, start, sign) reproduce identical samples on any attempt. A seed that "
      "depends on the attempt number would change the answer.", "Lesson 17 checkYourself"),
    Q("qc-L400-007", 17, "scenario", 3,
      "A team proposes sessions for a workload whose classical step takes 70 s between jobs. What does the lab's "
      "evidence predict?",
      ["The TTL expires, wall time matches batched, billing soars", "Sessions stay fastest and cheapest",
       "Sessions refuse to start with long classical steps", "Billing drops because the device idles"],
      "Past the interactive TTL each job re-queues, so wall time is like batched while the whole window is billed "
      "(2165.3 s). Sessions suit fast classical steps only.", "Lesson 17 options"),
    Q("qc-L400-008", 17, "design", 3,
      "Which design keeps the 'batched by default' decision true as the code evolves?",
      ["A fitness test on jobs, transpiles, wall and billed time", "A comment above DEFAULT_MODE",
       "A wiki page describing the ADR", "Code review by the original author whenever the orchestrator file changes"],
      "A fitness function fails CI when jobs > 30, transpiles != 1 or budgets are exceeded. Comments and documents "
      "do not stop a regression like the parameter-keyed cache.", "Lesson 17 fitnessFunction"),
]

# ---------------- Lesson 18: benchmarking ----------------
L += [
    Q("qc-L400-009", 18, "calculation", 3,
      "TTS99 = budget x ln(0.01) / ln(1 - success). A solver finds the optimum in 30% of 200-sample runs. What is "
      "its TTS99 in samples?",
      [str(TTS_03), "1329", "667", "600"],
      "200 x ln(0.01)/ln(0.7) = 2582. 1329 is the value for success 0.5; 667 is just 200/0.3.", "Lesson 18 code"),
    Q("qc-L400-010", 18, "code-reading", 3,
      "What does this print?",
      ["None 200", "0 200", "inf 0", "None 0"],
      "Success 0 means the optimum was never seen, so there is no finite time-to-solution. Success 1 means every run "
      "succeeds, so one run's budget is enough.", "Lesson 18 troubleshooting",
      code='''
import math


def tts99(success_rate, samples_per_run):
    if success_rate == 0:
        return None
    if success_rate == 1:
        return samples_per_run
    return round(samples_per_run * math.log(0.01) / math.log(1 - success_rate))


print(tts99(0.0, 200), tts99(1.0, 200))
'''),
    Q("qc-L400-011", 18, "code-reading", 3,
      "Lesson 18's decide() picks the winner. With these two rows, what does it print?",
      ["greedy", "qaoa", "a tie error", "annealing"],
      "Ratio, success and first-best are equal, so the last key element (is the solver classical?) breaks the tie for "
      "greedy. A quantum solver must win outright to justify its cost.", "Lesson 18 code",
      code='''
CLASSICAL = ("greedy", "annealing")
rows = [
    {"solver": "qaoa", "median_ratio": 1.0, "success": 0.5, "median_first_best": 40},
    {"solver": "greedy", "median_ratio": 1.0, "success": 0.5, "median_first_best": 40},
]
key = lambda r: (r["median_ratio"], r["success"], -r["median_first_best"], r["solver"] in CLASSICAL)
print(max(rows, key=key)["solver"])
'''),
    Q("qc-L400-012", 18, "calculation", 3,
      "Ten seeded runs give a success rate near 0.4. What is its binomial standard error sqrt(p(1-p)/n)?",
      [str(SE_10), "0.024", "0.04", "0.49"],
      "sqrt(0.24/10) = 0.15, so 0.3 vs 0.5 differ by little more than one standard error. 0.024 forgets the square "
      "root; ten seeds cannot rank those solvers.", "Lesson 18 scalingLimits"),
    Q("qc-L400-013", 18, "debugging", 3,
      "A benchmark report says QAOA wins at n = 12 (ratio 1.0 vs 0.8), every row claiming budget 200. The code "
      "gives QAOA 4x samples and its best of 10 seeds, the baselines one run at a quarter budget. What fixes it?",
      ["Same budget and seeds for all, medians, and a check on 'used'", "Give the classical solvers best-of-10 too",
       "Report wall-clock time instead of samples", "Drop the classical baselines from the report, since they ran at a lower budget"],
      "A fair harness holds budget and seeds fixed, reports medians over all runs and raises BudgetViolation on "
      "over-spending. Giving everyone best-of-N still hides reliability.", "Lesson 18 failureLab"),
    Q("qc-L400-014", 18, "scenario", 3,
      "With the fair harness, QAOA wins on one 12-node graph. Product asks to ship QAOA. What do you answer?",
      ["No: it won 1 of 5 other graphs and exact enumeration is cheap here", "Yes: a fair win is a fair win",
       "Yes, but only for 12-node graphs", "No: QAOA can never beat a classical MaxCut solver on any graph of any size"],
      "One instance proves nothing; on other 12-node graphs QAOA won once in five, and 4096 evaluations solve n = 12 "
      "exactly. The decision is about evidence, not a claim that QAOA can never win.", "Lesson 18 checkYourself"),
    Q("qc-L400-015", 18, "concept", 3,
      "Why does the harness report medians and success rates instead of each solver's best run?",
      ["Best-of-N hides reliability and invites cherry-picking", "Medians are always higher than best runs",
       "Best runs cannot be computed for QAOA", "Success rates make the simulator faster"],
      "Users get a typical run, not the luckiest one; best-of-N is only acceptable alongside medians with the same N "
      "for every solver.", "Lesson 18 tradeOffs"),
    Q("qc-L400-016", 18, "design", 3,
      "You are comparing algorithms, not deployed services. Which budget should the benchmark equalise?",
      ["Equal sample budget: hardware-neutral and auditable", "Equal wall-clock budget on your laptop",
       "Equal lines of code per solver", "Whatever budget each solver needs to win"],
      "A sample budget is reproducible and independent of machine and queue. Wall-clock budgets suit deployed "
      "services but depend on hardware and queues.", "Lesson 18 tradeOffs"),
]

# ---------------- Lesson 19: resource estimation ----------------
DIST = '''
def p_l(d, p=1e-3):
    return 0.03 * (p / 0.01) ** ((d + 1) / 2)


def choose_distance(p, logical_qubits, cycles, budget=0.01):
    if p >= 0.01:
        raise ValueError("above threshold: no distance helps")
    for d in range(3, 102, 2):
        if logical_qubits * cycles * p_l(d, p) <= budget:
            return d


print(choose_distance(1e-3, 20, 249))
'''
L += [
    Q("qc-L400-017", 19, "calculation", 3,
      f"RSA-2048 needs {RSA_Q} logical qubits in the lab's model and the error budget picks d = 27. With about 2d^2 "
      "physical qubits per logical qubit (data blocks only), how many physical qubits is that?",
      [f"{RSA_PHYS:,}", f"{RSA_Q * 27 ** 2:,}", f"{RSA_Q * 2 * 3 ** 2:,}", "20,000,000"],
      "6190 x 2 x 729 = 9,025,020. 4,512,510 forgets the measure qubits (d^2 data + d^2 - 1 measure); 111,420 is "
      "what the fixed d = 3 fault reports.", "Lesson 19 expectedResults"),
    Q("qc-L400-018", 19, "calculation", 3,
      "A workload has 50 logical qubits and 10,000 logical cycles. With p = 1e-3, p_L(d) = 0.03 (p/0.01)^((d+1)/2) "
      "and a total budget of 0.01, what is the smallest odd distance, and the physical-qubit count (2d^2 per logical)?",
      [f"d = {D_50}, {PHYS_50:,} physical", f"d = {D_50 - 2}, {50 * 2 * (D_50 - 2) ** 2:,} physical",
       "d = 3, 900 physical", f"d = {D_50 + 2}, {50 * 2 * (D_50 + 2) ** 2:,} physical"],
      "qubits x cycles x p_L(d) must be <= 0.01; d = 11 gives 0.015, d = 13 gives 0.0015. d = 11 is the tempting "
      "'nearly enough' choice that breaks the budget.", "Lesson 19 failureLab"),
    Q("qc-L400-019", 19, "code-reading", 3,
      "What does this distance chooser print for QAOA n = 20, p = 1 (249 logical cycles)?",
      ["9", "3", "7", "11"],
      "20 x 249 x p_L(7) = 0.015 exceeds the budget; d = 9 gives 0.0015. A fixed d = 3 gives p_fail 1.0.",
      "Lesson 19 checkYourself", code=DIST),
    Q("qc-L400-020", 19, "calculation", 3,
      f"The RSA-2048 model has {RSA_CYCLES:,} logical cycles at d = 27, and each logical cycle takes d code cycles of "
      "1 us. About how long is the run?",
      [f"{RSA_HOURS} hours", "0.6 hours", "2143 seconds", "435 hours"],
      "2.14e9 x 27 x 1 us = 57,870 s = 16.1 h. 0.6 h forgets the factor d per logical cycle.",
      "Lesson 19 expectedResults"),
    Q("qc-L400-021", 19, "calculation", 3,
      "Lab 19 uses Ross & Selinger's T-count of ceil(3 log2(1/eps)) per rotation. How many T gates does one rotation "
      "need at eps = 1e-6?",
      [str(T_ROT), "18", "7", "20"],
      "3 x log2(10^6) = 59.8, rounded up to 60. 7 is the T-count of a Toffoli, not a rotation.", "Lesson 19 code"),
    Q("qc-L400-022", 19, "concept", 3,
      "Why does the estimator raise an error instead of returning a distance when p >= 1%?",
      ["Above threshold p_L grows with d: no distance meets any budget", "The formula divides by zero at 1%",
       "Distances above 101 are not supported by the estimator's search loop in Python", "Physical error rates above 1% do not exist"],
      "(p/p_th)^((d+1)/2) exceeds 1 above threshold, so bigger codes are worse. Returning any number would claim "
      "feasibility that cannot exist.", "Lesson 19 checkYourself"),
    Q("qc-L400-023", 19, "debugging", 3,
      "Your estimator says RSA-2048 is fault-tolerant-feasible with 111,420 physical qubits, yet its own p_fail is "
      "1.0. What is wrong?",
      ["choose_distance returns a fixed d = 3 instead of using the budget", "The physical-qubit formula should use d^3",
       "The Toffoli count is too high", "The feasibility threshold of 1,000,000 physical qubits is set far too high"],
      "A fixed '17 physical per logical' ignores runtime and budget; derive d from qubits x cycles x p_L(d) <= budget. "
      "The thresholds were fine; the input to them was wrong.", "Lesson 19 failureLab"),
    Q("qc-L400-024", 19, "concept", 3,
      "The lab's 9,025,020 physical qubits for RSA-2048 is described as a lower bound. What does it leave out?",
      ["Magic-state factories, routing space and decoding", "The logical qubits of the algorithm",
       "The code distance chosen from the budget", "The 1 us code-cycle time"],
      "Data blocks only: the full machine also needs factories, routing and decoders. Published whole-machine "
      "estimates include these.", "Lesson 19 checkYourself"),
    Q("qc-L400-025", 19, "design", 3,
      "Product wants the service to gate requests by feasibility before running them. Which estimation approach "
      "should the gate use?",
      ["Budget-derived distance on data blocks, validated against counts", "A fixed overhead factor of 1000",
       "Only the full QDK estimator, nothing local", "Whatever the hardware vendor's latest published marketing figure says"],
      "It is transparent, fast and testable, and its formulas match counted circuits; the QDK estimator is a CI "
      "cross-check. A fixed factor can claim feasibility with certain failure.", "Lesson 19 tradeOffs"),
]

# ---------------- Lesson 20: error-aware compilation ----------------
L += [
    Q("qc-L400-026", 20, "calculation", 3,
      "ESP is the product of (1 - error) over every gate and measurement. A compiled circuit has 12 CX at 1% error "
      "and 5 measurements at 2% error (ignore 1-qubit gates). What is its ESP?",
      [str(ESP_12), "0.78", "0.8864", "0.9813"],
      "0.99^12 x 0.98^5 = 0.8012. Adding errors (1 - 0.22) gives 0.78, which is close but wrong for a product of "
      "independent survivals.", "Lesson 20 conceptSummary"),
    Q("qc-L400-027", 20, "scenario", 3,
      "Two qubits sit on a coupler that drifted to 15% CX error. A detour SWAP (3 CX) plus the CX over 1%-error "
      "couplers is possible. Which is better for that interaction, by ESP?",
      [f"Detour: {DETOUR} vs {DIRECT_BAD}", f"Direct: {DIRECT_BAD} vs {DETOUR}", "Equal: both are 0.85",
       "Direct, because fewer gates always win"],
      "0.99^4 = 0.9606 beats 0.85: four good gates are safer than one bad one. Counting gates alone picks the direct "
      "route, which is how trivial layouts land on the worst coupler.", "Lesson 20 checkYourself"),
    Q("qc-L400-028", 20, "calculation", 3,
      "Brute-force layout search places 5 logical qubits on an 8-qubit device in every ordered way. How many "
      "placements is that?",
      [f"{LAYOUTS:,}", "56", "40,320", "32,768"],
      "8 x 7 x 6 x 5 x 4 = 6720 ordered placements. 56 is the unordered choice of 5 of 8; 40,320 is 8!.",
      "Lesson 20 scalingLimits"),
    Q("qc-L400-029", 20, "code-reading", 3,
      "This simplified CX-cancellation pass removes back-to-back identical CX pairs. What does it print?",
      ["2 ['rz', 'cx']", "4 ['cx', 'rz', 'cx', 'cx']", "0 []", "3 ['rz', 'cx', 'cx']"],
      "Both identical adjacent CX pairs cancel (CX.CX = I); the rz and the last CX have no identical neighbour, so "
      "they stay. Cancelling across a gate on the same qubit would be wrong.", "Lesson 20 code",
      code='''
ops = [("cx", (0, 1)), ("cx", (0, 1)), ("rz", (1,)), ("cx", (1, 2)), ("cx", (1, 2)), ("cx", (0, 1))]
out = []
for op in ops:
    if op[0] == "cx" and out and out[-1] == op:
        out.pop()
    else:
        out.append(op)
print(len(out), [o[0] for o in out])
'''),
    Q("qc-L400-030", 20, "concept", 3,
      "Why can a compilation with depth 21 beat one with depth 18 on the drifted device?",
      ["The deeper one avoids the 15% coupler, so its ESP is higher", "Deeper circuits decohere less",
       "Depth is irrelevant on superconducting devices as long as ESP is computed", "The shallower one uses more measurements"],
      "A few extra layers on good couplers cost less fidelity than one CX on a bad coupler (ESP 0.7835 at depth 21). "
      "Depth still matters, which is why there is a budget.", "Lesson 20 checkYourself"),
    Q("qc-L400-031", 20, "debugging", 3,
      "After your router inserts SWAPs, the noiseless equivalence check fails. What is the likely bug?",
      ["The logical-to-physical map was not updated for both qubits", "ESP is computed before routing",
       "The depth budget is too small", "CX cancellation runs after routing and removes the inserted SWAP gates"],
      "A SWAP moves two logical qubits, so route() must update the occupant of the target qubit too. ESP and depth "
      "do not affect noiseless equivalence.", "Lesson 20 troubleshooting"),
    Q("qc-L400-032", 20, "concept", 3,
      "Why must equivalence be proven before any compilation is scored by ESP?",
      ["A routing bug can yield a wrong circuit with a fine-looking ESP", "ESP cannot be computed without it",
       "Equivalence checks lower the depth", "The device rejects any circuit that arrives without an equivalence proof"],
      "ESP scores gates, not correctness; a plausible wrong circuit can score well. Check noiseless TVD < 1e-9 first.",
      "Lesson 20 checkYourself"),
    Q("qc-L400-033", 20, "scenario", 3,
      "Yesterday's compiled circuit had ESP 0.79; today, with no code change, it measures much worse. What should "
      "the service do?",
      ["Recompile against today's calibration", "Keep yesterday's layout because it was tested",
       "Raise the depth budget", "Switch to a trivial layout"],
      "Devices drift daily; ESP computed on a stale error map mis-ranks layouts. Recompile per calibration.",
      "Lesson 20 scalingLimits"),
    Q("qc-L400-034", 20, "design", 3,
      "A layout cannot meet the 22-layer depth budget on some device. How should the compiler behave?",
      ["Fail loudly so the trade-off is explicit", "Silently return the best circuit over budget",
       "Drop gates until the depth fits", "Raise the budget automatically"],
      "A strict budget makes coherence use predictable and testable; when it cannot be met the caller must decide. "
      "Silent over-budget output hides the problem.", "Lesson 20 tradeOffs"),
]

# ---------------- Lesson 21: post-quantum migration ----------------
GREP = '''
import re

lines = [
    '"""Replaces the old RSA signer."""',
    "key = x25519.X25519PrivateKey.generate()",
    "priv = rsa.generate_private_key(65537, 3072)",
    "shared = ec_key.exchange(ec.ECDH(), peer)",
]
hits = [i for i, t in enumerate(lines) if re.search(r"rsa[-_]?(\\d+)?", t, re.I)]
print(hits)
'''
L += [
    Q("qc-L400-035", 21, "scenario", 3,
      f"Mosca's inequality marks key establishment P1 when X + Y > Z, with migration time Y = {Y_MIG} and years to a "
      f"cryptographically relevant quantum computer Z = {Z_CRQC}. Which systems are P1?",
      [", ".join(P1), "archive (10 years) only", "all four systems", "telemetry (5 years), chat (1 year)"],
      "10 + 3 and 7 + 3 exceed 9; 5 + 3 and 1 + 3 do not. Archive alone forgets that 7-year data also outlives the "
      "window once migration time is added.", "Lesson 21 checkYourself"),
    Q("qc-L400-036", 21, "code-reading", 3,
      "Lab 21's naive scanner greps for 'rsa'. Which line indices does it flag?",
      ["[0, 2]", "[2]", "[1, 2, 3]", "[0, 1, 2, 3]"],
      "It flags a docstring (a false positive) and the real RSA call, but misses X25519 and ECDH. That is why the "
      "inventory parses code instead of grepping words.", "Lesson 21 failureLab", code=GREP),
    Q("qc-L400-037", 21, "calculation", 3,
      "ML-KEM-768 has a 1184-byte public key and a 1088-byte ciphertext; X25519 adds 32 bytes to each in the hybrid. "
      "What are the hybrid's sizes?",
      [f"{HYB[0]} / {HYB[1]} bytes", "1184 / 1088 bytes", "1248 / 1152 bytes", "32 / 32 bytes"],
      "1184 + 32 = 1216 and 1088 + 32 = 1120. 1184/1088 is pure ML-KEM without the classical share.",
      "Lesson 21 expectedResults"),
    Q("qc-L400-038", 21, "calculation", 3,
      "Roetteler et al.'s bound is 9n + 2 ceil(log2 n) + 10 logical qubits to break an n-bit prime-field curve. "
      "How many for P-256?",
      [str(ECC_256), "6190", "2304", "768"],
      "9 x 256 + 2 x 8 + 10 = 2330, far fewer than RSA-2048's 6190. 2304 drops the logarithmic and constant terms.",
      "Lesson 21 code (shor_context.py)"),
    Q("qc-L400-039", 21, "concept", 3,
      "Which algorithms does Shor's algorithm break?",
      ["RSA and elliptic-curve cryptography", "AES-256 and SHA-256", "ML-KEM and ML-DSA", "All encryption in use today"],
      "Shor factors and solves discrete logs, breaking RSA and ECC. AES-256 and SHA-256 are not expected to need "
      "transition (NIST IR 8547).", "Lesson 21 concepts"),
    Q("qc-L400-040", 21, "concept", 3,
      "Why is a service that signs session tokens with ECDSA not P1, while ECDH replication of 7-year data is?",
      ["Signatures are not exposed to harvest-now-decrypt-later", "ECDSA is already quantum-safe",
       "Session tokens are additionally encrypted with AES-256-GCM before signing", "ECDH uses longer keys than ECDSA"],
      "Recorded ciphertext can be decrypted later, but a signature only needs to be trusted while it is checked. "
      "ECDSA is still quantum-vulnerable and is migrated before 2030 (P2).", "Lesson 21 checkYourself"),
    Q("qc-L400-041", 21, "scenario", 3,
      "Senders were switched to the hybrid KEM before all receivers were upgraded, and handshakes fail with "
      "'unknown kem'. What rollout rule was broken?",
      ["Upgrade receivers first, then switch senders by config", "Never use a hybrid during transition",
       "Switch everyone on a single flag day", "Disable the algorithm name in the envelope"],
      "Envelopes carry the algorithm name so receivers that know it can accept; senders switch only when receivers "
      "are ready. Removing the name would turn loud failures into silent ones.", "Lesson 21 scalingLimits"),
    Q("qc-L400-042", 21, "design", 3,
      "During the transition period, which key-establishment design does the lesson choose?",
      ["Agile interface with hybrid X25519 + ML-KEM-768", "Replace each call site with ML-KEM-768 directly",
       "Wait until 2030 and migrate then", "Keep X25519 and add longer keys"],
      "The hybrid stays secure if either part holds, and a registry makes the next swap a config line. Call-site "
      "replacement repeats the work next time; waiting leaves harvestable data exposed.", "Lesson 21 options"),
]

# ---------------- Lesson 22: capstone ----------------
L += [
    Q("qc-L400-043", 22, "concept", 3,
      "In the capstone report, who decides that annealing wins?",
      ["decide() from lesson 18's harness, in code", "The local model, after reading the report",
       "The client, by choosing a solver in the request", "Whichever solver finished first"],
      "Code picks the winner (equal ratio and success, fewest samples to the best cut). The agent only explains, and "
      "its explanation is checked against the report.", "Lesson 22 checkYourself"),
    Q("qc-L400-044", 22, "calculation", 3,
      f"Readout mitigation moved <C> from {RAW} to {MITIGATED}; the ideal is {IDEAL}. What fraction of the gap to "
      "ideal did it close?",
      [str(GAP_CLOSED), "0.86", "0.93", "0.01"],
      "(6.8549 - 6.774)/(7.3525 - 6.774) = 0.14. Most of the gap is gate noise (fidelity 0.6224), which readout "
      "mitigation does not touch.", "Lesson 22 expectedResults"),
    Q("qc-L400-045", 22, "concept", 3,
      "Why is mitigated <C> still below the ideal value?",
      ["Readout mitigation removes readout bias, not gate noise", "The mitigation matrix was inverted wrongly",
       "The ideal value includes shot noise", "The classical solvers lowered it"],
      "Only measurement bias is corrected; gate errors on the device remain. A broken inverse would give invalid or "
      "far-off values, not a small improvement.", "Lesson 22 checkYourself"),
    Q("qc-L400-046", 22, "scenario", 3,
      "A client posts a 12-node MaxCut instance; the only device has 8 qubits. What should the service do?",
      ["Refuse the quantum path with a reason, answer classically", "Return HTTP 400 for the whole request",
       "Run QAOA on 8 of the 12 nodes", "Queue it until a bigger device appears"],
      "The feasibility gate keeps the request off the quantum path, and the same fair harness answers with classical "
      "solvers. HTTP 400 is for invalid input such as n = 30.", "Lesson 22 rubric"),
    Q("qc-L400-047", 22, "debugging", 3,
      "Milestone M2 fails on 'rows identical' when two job failures are injected. What is the cause?",
      ["A retry changed the samples: seeds depend on the attempt", "The transpile cache missed once",
       "The queue time grew by 2 s", "The agent rewrote the benchmark rows while it was explaining the report"],
      "Retries must reproduce identical samples, so circuit seeds may not depend on attempts. Extra queue time changes "
      "wall time, not the rows.", "Lesson 22 troubleshooting"),
    Q("qc-L400-048", 22, "code-reading", 3,
      "The capstone compares benchmark rows while ignoring local_s. What does this print?",
      ["True", "False", "None", "KeyError"],
      "Only local_s differs, and it is dropped before comparing: simulator time is not judged. Comparing raw rows "
      "would print False for every rerun.", "Lesson 22 code",
      code='''
IGNORE = ("local_s",)


def rows(report):
    return [{k: v for k, v in r.items() if k not in IGNORE} for r in report["benchmark"]]


a = {"benchmark": [{"solver": "greedy", "median_ratio": 1.0, "local_s": 0.41}]}
b = {"benchmark": [{"solver": "greedy", "median_ratio": 1.0, "local_s": 0.57}]}
print(rows(a) == rows(b))
'''),
    Q("qc-L400-049", 22, "design", 3,
      "An agent's pitch claims 'QAOA wins - quantum advantage' while the report's winner is annealing. How should "
      "the service handle it?",
      ["Reject it: code checks winner, numbers and claims", "Publish it with a disclaimer",
       "Let the agent rerun the benchmark until QAOA wins", "Average the agent's view with the report"],
      "The agent only explains; any explanation whose winner, numbers or claims disagree with the report is rejected "
      "by code. Agents never decide.", "Lesson 22 rubric"),
    Q("qc-L400-050", 22, "scenario", 3,
      "A teammate wants to bind the capstone service to 0.0.0.0 so others can try it. What does the lesson say?",
      ["Keep 127.0.0.1; never expose it or the model beyond a trusted network", "Fine, if the port is unusual",
       "Fine, as long as the agent sees only report numbers and never customer data", "Bind 0.0.0.0 but disable /health"],
      "The safety rubric requires 127.0.0.1 only, and credentials or customer data never go to a model. An unusual "
      "port is not access control.", "Lesson 22 caution"),
]

L += [
    Q("qc-L400-051", 17, "concept", 3,
      "Why does lab 17 separate the optimiser, the orchestrator and the backend adapter?",
      ["Modes and backends can change without touching the optimiser", "It makes the circuits shorter",
       "Each part needs its own quantum device so jobs never wait in one queue", "It removes the need for a transpiler"],
      "The optimiser asks for energies, the orchestrator decides jobs, caching and retries, and the adapter talks to "
      "one backend. Swapping sync/batched/session or a provider stays local to one part.", "Lesson 17 conceptSummary"),
    Q("qc-L400-052", 17, "concept", 3,
      "Why are lab 17's execution modes compared on a FakeClock instead of real time?",
      ["Modelled time is deterministic, so tests are fast and repeatable", "Real queues are always exactly 2 s",
       "A FakeClock makes the simulator compute faster than wall-clock time allows", "Billing can only be computed on real time"],
      "Queue, transpile and execution costs advance the fake clock, so tests never sleep and give the same numbers "
      "every run. The costs are illustrative; real queues vary by hours.", "Lesson 17 simulatorVsReal"),
    Q("qc-L400-053", 18, "concept", 3,
      "Why is exact enumeration the reference solver for n <= 16 in lab 18?",
      ["It proves the optimum, so every ratio is measured exactly", "It is the fastest solver at every size",
       "It is the solver the service will ship", "It needs no sample budget at all"],
      "2^n evaluations are affordable at these sizes (65,536 at n = 16) and give the true optimum to grade against. "
      "It stops being practical near n = 30.", "Lesson 18 options"),
    Q("qc-L400-054", 18, "concept", 3,
      "Why must the winner rule be fixed in code before results are seen?",
      ["So nobody can pick the metric that favours a preferred solver", "Because decide() runs before the solvers",
       "So the rule can ignore success rates", "Because Python cannot change a function's behaviour once the program is running"],
      "Choosing the metric after seeing results is how benchmarks fabricate wins. A pre-registered rule (quality, "
      "then reliability, then speed, ties classical) keeps the method defensible.", "Lesson 18 concepts"),
    Q("qc-L400-055", 19, "concept", 3,
      "Why does lab 19 validate its formulas against circuits it actually builds?",
      ["Counted gates catch formula mistakes where both can be computed", "Built circuits run faster than formulas",
       "The formulas are only valid for circuits that have actually been built and run", "The QDK estimator requires it"],
      "For n = 6-12 the CX and rotation counts of built circuits equal the formulas, which earns trust for sizes that "
      "cannot be built (RSA-2048).", "Lesson 19 concepts"),
    Q("qc-L400-056", 19, "concept", 3,
      "Why does RSA-2048 need a much larger code distance than QAOA n = 20 under the same 1% budget?",
      ["Failure probability scales with qubits x cycles, and RSA has far more", "RSA uses a different error model",
       "Larger keys need larger codes by definition, regardless of runtime or qubit count", "QAOA is error-free on a surface code"],
      "With 6190 qubits and 2.1e9 cycles, p_L per qubit-cycle must be around 1e-15, which takes d = 27; QAOA n = 20 "
      "meets the budget at d = 9.", "Lesson 19 checkYourself"),
    Q("qc-L400-057", 20, "concept", 3,
      "What does ESP (estimated success probability) leave out, and how should you use it?",
      ["Crosstalk and leakage; use it to rank, then validate on results", "Gate errors; use it as exact fidelity",
       "Readout errors; add them separately later", "Depth; it must always be combined with a depth budget and is never used alone"],
      "ESP multiplies per-gate and readout fidelities and treats every error as fatal, so it underestimates fidelity "
      "and misses correlated effects. Its job is ranking options.", "Lesson 20 scalingLimits"),
    Q("qc-L400-058", 20, "concept", 3,
      "What does a noise-aware layout do that a trivial layout does not?",
      ["Places and routes qubits using today's per-coupler error rates", "Uses fewer qubits than the circuit needs",
       "Removes every SWAP from the circuit", "Maps logical qubit i to physical qubit i"],
      "It searches placements by ESP on the current calibration and routes along reliable paths. Mapping i -> i is "
      "the trivial layout that landed on the 15% coupler.", "Lesson 20 concepts"),
    Q("qc-L400-059", 21, "concept", 3,
      "Why does lab 21 inventory crypto by parsing code (AST) instead of grepping for algorithm names?",
      ["Parsing resolves imports, aliases and each call's purpose", "Grep cannot read .py files",
       "AST scanning finds secrets in comments", "Parsing is much faster than grep on large repositories with many files"],
      "Grep finds words: it flagged a docstring and missed X25519, ECDH and ECDSA (recall 3/8). The AST scanner "
      "knows what each call does, which priorities need.", "Lesson 21 failureLab"),
    Q("qc-L400-060", 21, "concept", 3,
      "In lab 21, what makes the next algorithm swap 'a configuration change'?",
      ["Callers use one interface and the algorithm is picked by name", "Every call site imports ML-KEM directly",
       "The algorithm is hard-coded in a single constant per file", "The envelope omits the algorithm name"],
      "establish()/accept() look the KEM up in a registry from CONFIG, and envelopes carry its name so receivers "
      "pick it from data. Direct imports at each call site mean editing every site again.", "Lesson 21 concepts"),
    Q("qc-L400-061", 22, "concept", 3,
      "Milestone M3 checks the capstone's cheap white-noise model against a density-matrix simulation (TVD 0.0213, "
      "limit 0.03). Why?",
      ["To validate the fast model before the service relies on it", "To make the backend run faster",
       "To replace readout mitigation", "To prove the drifted device has no noise left after compilation"],
      "The service samples a cheap model, so it must first be shown to match a trusted simulation within a "
      "tolerance. It models noise; it does not remove it.", "Lesson 22 milestones"),
    Q("qc-L400-062", 22, "concept", 3,
      "What is the capstone's honest answer to 'should we use the quantum solver?' for simulator-sized MaxCut?",
      ["No: a classical solver wins, and the report shows the evidence", "Yes: QAOA always wins at 8 qubits",
       "It depends on what the agent recommends", "Yes, because the quantum path ran end to end without any job errors"],
      "Under equal budgets and seeds the code-made decision picks annealing; the service says so with the numbers. "
      "Running without errors says nothing about winning.", "Lesson 22 conceptSummary"),
]

QUESTIONS = L
