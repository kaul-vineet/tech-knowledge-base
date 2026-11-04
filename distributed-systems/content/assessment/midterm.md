# Midterm exam (week 7) - 90 minutes, 100 marks

Covers L100 (#1-#6), L200 (#7-#11) and L500 #23 plus #24 T24.1. Closed book; one A4 sheet of handwritten notes; calculator allowed. Show your working: marks are for the argument, not only the number. Numerical answers are recomputed in `research/l500_checks.py` (EXAMS section).

---

### Q1 - Derivation: clocks (15 marks)
Two processes. P1: event a sends m1 to P2, then local event b. P2: event c receives m1, then event d sends m2 to P1. P1: event e receives m2.
(a) Give the Lamport timestamp and the vector timestamp of every event. (6)
(b) Which pairs among {b, c, d} are concurrent? Justify with vectors. (4)
(c) b and c have the same Lamport time. How does the total order break the tie, and why does that not contradict the clock condition? (5)

**Model answer.** (a) Lamport: a = 1, b = 2, c = max(0, 1) + 1 = 2, d = 3, e = max(2, 3) + 1 = 4. Vectors: a = (1,0), b = (2,0), c = (1,1), d = (1,2), e = max((2,0),(1,2)) then tick = (3,2). [1 mark per two events, 6 total.] (b) b vs c: (2,0) and (1,1) are incomparable, so concurrent; b vs d: (2,0) vs (1,2) incomparable, concurrent; c -> d since (1,1) < (1,2). [2 + 2.] (c) Order by (L, pid): with P1 < P2, b precedes c. The clock condition only constrains causally related events; b and c are concurrent, so any order is consistent with -> (T23.1). [3 for the rule, 2 for the reason.]

### Q2 - Prediction: retries (12 marks)
A request passes through three layers (gateway -> orders -> payments); each layer makes up to 3 attempts on failure and none uses a retry budget. Payments is completely down.
(a) How many calls reach payments for one user request? (4)
(b) Predict what happens to payments' recovery when it comes back under full load, and name two mechanisms from lesson 4 that prevent it. (8)

**Model answer.** (a) 3 x 3 x 3 = 27 calls. [4] (b) The retry storm multiplies offered load by up to 27 at the moment the dependency is weakest, so it may never recover (the same amplification AWS's December 2021 summary describes when back-off failed). Mechanisms: retry at one layer only / a retry budget (lab 4's gRPC-style token bucket: failures spend tokens, successes earn a fraction back), exponential backoff with full jitter, deadlines propagated so lower layers stop when the caller has given up. [2 for the dynamic, 3 per mechanism, max 8.]

### Q3 - Explanation: idempotency and the two generals (10 marks)
Explain why no protocol over a lossy network lets a shop and a payment service be *certain* they agree, and why idempotency keys still make "charge exactly once" achievable in practice.

**Model answer.** T24.1: in the minimal run in which someone acts, the sender of the last delivered message cannot know it arrived, so the two sides can disagree - more acknowledgements only move the uncertainty. [5] Practice changes the requirement: charging is repeatable (the server stores the result under the idempotency key and returns it on retry) and reversible (refund), so the client may retry until it learns the outcome; the effect is exactly once although delivery is at least once (lab 5: 110 charged without keys, 50 with). [5]

### Q4 - Derivation: quorums (15 marks)
A store has N = 5 replicas.
(a) Prove that every read quorum meets every write quorum iff R + W > N. (7)
(b) With R = 2 and W = 4, how many replicas may be down for reads to succeed, and for writes? (4)
(c) Is R = 2, W = 4 linearizable? Answer with one sentence of evidence from the course. (4)

**Model answer.** (a) Pigeonhole: |Q_R ∩ Q_W| >= R + W - N > 0; converse: if R + W <= N take the first R and the last W replicas, which are disjoint (T24.4a). [4 + 3] (b) reads survive 3 down, writes survive 1 down. [2 + 2] (c) Not necessarily: overlap prevents stale reads of completed writes, but without read write-back two overlapping reads can see new-then-old (lab 17's inversions). [4]

### Q5 - Design critique: leader election (20 marks)
A team elects a leader with a 10-second lease in a key-value store. The leader checks `time.time() < lease_expiry` before every write to shared storage. Critique the design using the system models of lesson 23 and propose a fix. Include one concrete execution that breaks safety.

**Model answer.** The check assumes bounded process pauses and clock drift - a synchronous assumption. Execution: the leader passes the check, pauses (GC, VM migration) for 12 s, the lease expires, a new leader is elected and writes, then the old leader resumes and writes - two writers, safety violated (lab 7's stale write; L300 #13's two leaders). [8 for the execution and the model.] T23.4: without a delay bound no timeout is accurate, and safety must not depend on it. Fix: fencing tokens - the lease store issues a monotonically increasing token; the storage rejects writes with a token lower than the highest seen. Safety becomes an invariant on the storage; the lease only affects liveness. [8] Further: persist tokens, keep lease renewal well below expiry, monitor clock skew. [4]

### Q6 - Prediction: consistent hashing (15 marks)
Keys are placed by `hash(key) % N`. The cluster grows from 4 to 5 nodes.
(a) Derive the fraction of keys that move, assuming hashes are uniform. (8)
(b) What fraction moves with an ideal consistent-hash ring, and why? (7)

**Model answer.** (a) A key stays iff k mod 4 = k mod 5; over one period of 20 values that holds only for k mod 20 in {0, 1, 2, 3}, so 4/20 = 1/5 stay and 4/5 = 80% move (lab 9 measured 80.3%). [8] (b) About 1/5 = 20%: the new node takes an equal share from the others and no other key moves (lab 9 measured 18.9% with virtual nodes). [7]

### Q7 - Short answers: safety and liveness (13 marks)
Classify and justify in one line each: (a) "the fencing token never decreases" (3); (b) "every message is eventually delivered or dead-lettered" (3); (c) "no request waits more than 2 s in the queue" (3); (d) Why can a test suite refute (a) but never (b)? (4)

**Model answer.** (a) Safety. (b) Liveness. (c) Safety - the violation is visible at the 2 s mark. (d) A safety violation has a finite witness that a test can show; any finite trace can still be extended so that (b) holds, so no finite test refutes it (T23.3). [3 + 3 + 3 + 4]
