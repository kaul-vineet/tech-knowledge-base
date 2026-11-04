"""Lesson text for L500 #23-25 (Foundations I-III). Assembled by research/build_l500.py."""

PLATFORMS = {"mac": "expected", "windows": "expected"}

LAMPORT_1978 = {"title": "Lamport (1978), Time, Clocks, and the Ordering of Events in a Distributed System, CACM 21(7) (author's PDF)",
                "url": "https://lamport.azurewebsites.net/pubs/time-clocks.pdf"}
KLEPPMANN = {"title": "Kleppmann, Distributed Systems lecture notes, Cambridge 2025/26 (CC BY-SA): sections 2 and 3",
             "url": "https://www.cl.cam.ac.uk/teaching/2526/ConcDisSys/dist-sys-notes.pdf"}
ALPERN = {"title": "Alpern & Schneider (1985), Defining Liveness, Information Processing Letters 21",
          "url": "https://www.cs.cornell.edu/fbs/publications/DefLiveness.pdf"}
DLS = {"title": "Dwork, Lynch & Stockmeyer (1988), Consensus in the Presence of Partial Synchrony, JACM 35(2)",
       "url": "https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf"}
FLP = {"title": "Fischer, Lynch & Paterson (1985), Impossibility of Distributed Consensus with One Faulty Process, JACM 32(2)",
       "url": "https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf"}
GL2002 = {"title": "Gilbert & Lynch (2002), Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services, SIGACT News",
          "url": "https://www.comp.nus.edu.sg/~gilbert/pubs/BrewersConjecture-SigAct.pdf"}
GL2012 = {"title": "Gilbert & Lynch (2012), Perspectives on the CAP Theorem (safety vs liveness framing)",
          "url": "https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf"}
PAXOS = {"title": "Lamport (2001), Paxos Made Simple",
         "url": "https://lamport.azurewebsites.net/pubs/paxos-simple.pdf"}
RAFT = {"title": "Ongaro & Ousterhout (2014), In Search of an Understandable Consensus Algorithm (extended version)",
        "url": "https://raft.github.io/raft.pdf"}
LITTLE = {"title": "Little & Graves (2008), Little's Law, chapter 5 of Building Intuition (author copy)",
          "url": "https://www.isye.gatech.edu/~jvandeva/Classes/6337/2013/Little's%20Law-Published.pdf"}
TAIL = {"title": "Dean & Barroso (2013), The Tail at Scale, CACM 56(2)",
        "url": "https://www.barroso.org/publications/TheTailAtScale.pdf"}
GUNTHER = {"title": "Gunther (2008), A General Theory of Computational Scalability Based on Rational Functions (arXiv:0808.1431)",
           "url": "https://arxiv.org/abs/0808.1431"}
AMDAHL = {"title": "Amdahl (1967), Validity of the single processor approach to achieving large scale computing capabilities, AFIPS",
          "url": "https://www-inst.eecs.berkeley.edu/~n252/paper/Amdahl.pdf"}

WRITTEN_RUBRIC = [
    {"criterion": "Correctness of the argument", "excellent": "Every step follows from definitions or a cited lemma; no gaps; edge cases (equal clocks, empty quorums, rho -> 1) handled",
     "adequate": "Main idea right; one step asserted rather than shown", "inadequate": "Circular, hand-waving, or proves a different statement", "weight": "40%"},
    {"criterion": "Precise statements and assumptions", "excellent": "States the model (synchrony, fault type, independence, stationarity) and where it is used",
     "adequate": "Model stated but not tied to the step that needs it", "inadequate": "Model missing; result applied outside its assumptions", "weight": "20%"},
    {"criterion": "Numerical check", "excellent": "Calculation reproduced in code; output quoted; discrepancy explained (sampling error, edge effects)",
     "adequate": "Code runs but discrepancy not discussed", "inadequate": "No check, or numbers copied without running", "weight": "20%"},
    {"criterion": "Link to practice", "excellent": "Names the lab (L100-L400) where the result bites and what would break without it",
     "adequate": "Generic link to practice", "inadequate": "No link", "weight": "20%"},
]

# ------------------------------------------------------------------------------------------------
LESSON_23 = {
    "id": "foundations-system-models-time",
    "number": 23,
    "level": "L500",
    "title": "Foundations I: system models, time and causality - with proofs",
    "category": "theory",
    "description": "Define synchronous, asynchronous and partially synchronous models and crash vs Byzantine faults; prove Lamport's clock condition and the vector-clock characterisation of happened-before; separate safety from liveness; check every result in code.",
    "outcome": "You can state the system model a design assumes, prove what logical clocks do and do not guarantee, classify a requirement as safety or liveness, and explain why a timeout is only a guess without a delay bound.",
    "estimatedTime": "3-4 hours (reading, proofs, code checks, problem set)",
    "prerequisites": [
        "Discrete mathematics: relations (partial and total orders, transitive closure), proof by induction and by contradiction",
        "Basic probability: tail probability P(X > t) of a distribution",
        "Lesson 6 (Lamport clocks) and Lesson 3 (timeouts) - the practice this lesson proves",
    ],
    "learningObjectives": [
        "Explain the difference between synchronous, asynchronous and partially synchronous models and crash-stop, crash-recovery and Byzantine faults, and identify which one a given lab silently assumes.",
        "Prove that Lamport's rules IR1/IR2 imply the clock condition, and explain with a counterexample why the converse fails.",
        "Prove that vector clocks characterise happened-before exactly: a -> b iff V(a) < V(b).",
        "Classify a requirement as a safety or a liveness property using the Alpern-Schneider definitions, and analyze why availability is liveness while linearizability is safety.",
        "Evaluate a failure detector: derive the timeout that is perfect in a synchronous model and argue why no timeout is accurate in the asynchronous model.",
    ],
    "glossary": [
        {"term": "synchronous model", "meaning": "Known upper bounds on message delay and on relative process speed (Dwork, Lynch & Stockmeyer's Delta and Phi)."},
        {"term": "asynchronous model", "meaning": "No bound on message delay or process speed; a slow process is indistinguishable from a crashed one."},
        {"term": "partially synchronous model", "meaning": "Bounds exist but are unknown, or hold only after an unknown Global Stabilisation Time (GST)."},
        {"term": "crash-stop / crash-recovery / Byzantine", "meaning": "A faulty node halts forever / halts and may restart with only its stable storage / may deviate arbitrarily, even maliciously."},
        {"term": "happened-before (a -> b)", "meaning": "Smallest relation with: same-process order, send -> receive, transitivity. a and b are concurrent if neither a -> b nor b -> a."},
        {"term": "clock condition", "meaning": "a -> b implies C(a) < C(b). Lamport clocks satisfy it; the converse does not hold."},
        {"term": "vector clock", "meaning": "One counter per process; V(e)[k] = number of events of process k in e's causal past (including e)."},
        {"term": "safety / liveness", "meaning": "Nothing bad ever happens (a violation has a finite witness) / something good eventually happens (every finite prefix can still be completed)."},
    ],
    "theorems": [
        {
            "name": "T23.1 Lamport's clock condition and total order (Lamport 1978)",
            "statement": "If every process ticks its counter between successive events (IR1) and, on receiving a message stamped T_m, sets its counter above both its current value and T_m (IR2), then for all events a, b: a -> b implies C(a) < C(b). Ordering events by the pair (C(e), process id) is a strict total order that extends ->. The converse (C(a) < C(b) implies a -> b) is false.",
            "proof": (
                "**Setup.** Lamport defines -> as the *smallest* relation satisfying (1) a before b in the same process, (2) a is the send and b the receive of one message, (3) transitivity. So to show -> is contained in any relation R, it suffices to show R contains every rule-(1) pair, every rule-(2) pair, and is transitive.\n\n"
                "**Proof.** Let R = {(a, b) : C(a) < C(b)}.\n"
                "1. Rule (1): if a precedes b in process P_i, IR1 increments C_i at least once between them, so C(a) < C(b) (Lamport's condition C1).\n"
                "2. Rule (2): if a sends m with T_m = C(a) and b receives m, IR2 sets the receiver's clock strictly above T_m before b, so C(a) < C(b) (condition C2).\n"
                "3. < on integers is transitive, so R is transitive.\n"
                "Hence -> is contained in R, i.e. a -> b implies C(a) < C(b). This is the clock condition. ∎\n\n"
                "**Total order.** Keys (C(e), pid(e)) are pairwise distinct: two events of one process differ in C by IR1, events of different processes differ in pid. Lexicographic order on distinct keys is a strict total order, and a -> b gives C(a) < C(b), hence key(a) < key(b). ∎\n\n"
                "**Converse fails.** Take two processes that never communicate: P1 has events a1, a2 (C = 1, 2), P2 has one event b1 (C = 1). Then C(b1) < C(a2) but b1 and a2 are concurrent. Lamport notes the converse would force concurrent events to share a time, contradicting C1.\n\n"
                "**Where it bites.** Lab 6 sorts by (Lamport time, node): correct for causally related events, arbitrary for concurrent ones - which is why L400 #18 needs more than a Lamport timestamp to merge concurrent edits."
            ),
            "check": "labs/L500/23-system-models-time/clocks_proofs.py clock",
        },
        {
            "name": "T23.2 Vector clocks characterise happened-before",
            "statement": "With V_i[i] incremented at every event of P_i, the current vector sent with every message, and an element-wise maximum taken on receive (before the increment), for all distinct events a, b: a -> b if and only if V(a) < V(b) (every component <=, and the vectors differ). Consequently a and b are concurrent iff V(a) and V(b) are incomparable.",
            "proof": (
                "Write past(e) for the set of events f with f -> e or f = e.\n\n"
                "**Lemma.** V(e)[k] = |past(e) ∩ events of P_k|. *Induction over the execution order.* For a local or send event e of P_i that follows e' in P_i: past(e) = past(e') ∪ {e}, and only component i grows, by exactly 1. For a receive e of message m sent at s: past(e) = past(e') ∪ past(s) ∪ {e}. The events of P_k in any past(·) form a *prefix* of P_k's sequence (pasts are closed under program order), so the size of the union of two prefixes is the larger size: the element-wise maximum. Adding e itself is the increment of component i. ∎\n\n"
                "**(=>)** If a -> b then past(a) ⊆ past(b), so V(a) <= V(b) componentwise by the lemma. Let P_j be b's process. b is in past(b) but not in past(a) (else b -> a or b = a, impossible since -> is irreflexive and acyclic), so V(a)[j] < V(b)[j]. Hence V(a) < V(b).\n\n"
                "**(<=)** Let a be the c-th event of P_i, so V(a)[i] = c. If V(a) <= V(b) then V(b)[i] >= c: past(b) contains at least the first c events of P_i, in particular a. So a -> b or a = b; a != b gives a -> b. ∎\n\n"
                "**Cost.** n integers per message for n processes - the price of exactness (Lamport clocks use one integer but lose concurrency information)."
            ),
            "check": "labs/L500/23-system-models-time/clocks_proofs.py vector",
        },
        {
            "name": "T23.3 Safety and liveness (Alpern & Schneider 1985)",
            "statement": "Treat a property as a set of infinite executions. P is a safety property iff every execution not in P has a finite prefix that no extension can bring back into P; P is a liveness property iff every finite prefix can be extended to an execution in P. Every property is the intersection of a safety property and a liveness property.",
            "proof": (
                "**Definitions (Alpern & Schneider).** Safety: if sigma is not in P, some prefix sigma_i is irremediable: every extension of sigma_i is outside P. Liveness: every finite prefix alpha has some continuation beta with alpha·beta in P.\n\n"
                "**Decomposition.** Let cl(P) be the set of executions all of whose finite prefixes can be extended into P (the topological closure). Then:\n"
                "1. cl(P) is safety: if sigma is not in cl(P), some prefix has no extension into P, and therefore no extension into cl(P) either (an extension in cl(P) would have that prefix extendable into P).\n"
                "2. L = P ∪ (not cl(P)) is liveness: take a finite prefix alpha. If alpha extends into P we are done; otherwise every infinite extension of alpha has alpha as a non-extendable prefix, so it lies outside cl(P), hence in L.\n"
                "3. cl(P) ∩ L = (cl(P) ∩ P) ∪ (cl(P) ∩ not cl(P)) = P, because P ⊆ cl(P). ∎\n\n"
                "**Classification used in this course.** Agreement and validity of consensus, linearizability, 'at most one leader per term', 'a fencing token never decreases' and even 'every response within 200 ms' are safety (each violation happens at an identifiable point). Termination, 'every request eventually answered' (CAP availability) and 'a leader is eventually elected' are liveness (Gilbert & Lynch 2012 make the same split for CAP).\n\n"
                "**Why it matters.** Safety is proved with invariants (T24.4); liveness needs fairness or timing assumptions (T23.4, T24.2). Tests can refute safety with a finite trace; they can never refute liveness."
            ),
            "check": "labs/L500/23-system-models-time/clocks_proofs.py safety",
        },
        {
            "name": "T23.4 Failure detection depends on the timing model",
            "statement": "(a) Synchronous model: if one-way delay <= Delta and processing <= pi, a heartbeat probe with timeout 2*Delta + pi never suspects a live process and eventually suspects every crashed one (a perfect failure detector). (b) Asynchronous model: for every finite timeout T there is an admissible execution in which a live process is suspected; no timeout-based detector is both accurate and complete. (c) Partially synchronous model: a detector that increases its timeout after each false suspicion makes only finitely many mistakes (eventually accurate).",
            "proof": (
                "**(a)** Request <= Delta, processing <= pi, reply <= Delta, so a live peer's reply arrives within 2*Delta + pi. A crashed peer never replies, so it is suspected at the first timeout.\n\n"
                "**(b)** Fix T. Take any execution E1 in which the peer is live and replies. Because no delay bound exists, the execution E2 that is identical except that the reply is delayed until after T is also admissible. Up to time T the prober's local view in E2 is identical to its view in E3, where the peer crashed just before replying. A deterministic prober therefore makes the same decision at T in E2 and E3: if it suspects, it is wrong in E2 (inaccurate); if it does not, then by the same argument for every later timeout it never suspects in E3 (incomplete). This is the indistinguishability argument FLP (T24.2) builds on.\n\n"
                "**(c)** Under partial synchrony delays are <= Delta after an unknown GST. Doubling the timeout after each false suspicion reaches a value >= 2*Delta + pi after finitely many doublings, after which no live process is suspected. Raft's randomized election timeout is this idea in practice: safety never depends on it, liveness does (Ongaro & Ousterhout §5.6).\n\n"
                "**The check** uses Pareto delays (no upper bound): the false-suspicion rate is T^-1.5 - it falls with T but never reaches 0. With bounded delays and T = 105 ms it is exactly 0."
            ),
            "check": "labs/L500/23-system-models-time/clocks_proofs.py detector",
        },
    ],
    "problemSet": [
        {"id": "23-P1", "type": "calculation", "difficulty": 1, "marks": 6,
         "problem": "Three processes. P1: a (local), b (send m1 to P2), c (local). P2: d (local), e (receive m1), f (send m2 to P3). P3: g (local), h (local), i (receive m2). Compute the Lamport time L(i) and vector time V(i) (start all clocks at 0). Is c -> i, i -> c, or are they concurrent?",
         "answer": "L(i) = 5, V(i) = (2, 3, 3); c and i are concurrent",
         "solution": "Lamport: P1 a=1, b=2, c=3. P2 d=1, e=max(1, 2)+1=3, f=4. P3 g=1, h=2, i=max(2, 4)+1=5. Vectors: b=(2,0,0), c=(3,0,0); d=(0,1,0), e=max((0,1,0),(2,0,0)) then tick = (2,2,0), f=(2,3,0); g=(0,0,1), h=(0,0,2), i=max((0,0,2),(2,3,0)) then tick = (2,3,3). Answer: L(i) = 5, V(i) = (2, 3, 3); c and i are concurrent: V(c)=(3,0,0) has 3 > 2 in component 1 and 0 < 3 in component 2, so neither vector is <= the other. Note L(c) = 3 < L(i) = 5 although c does not happen before i - the converse of the clock condition fails (T23.1)."},
        {"id": "23-P2", "type": "proof", "difficulty": 2, "marks": 8,
         "problem": "Prove that ordering events by (Lamport time, process id) is a strict total order on the events of one execution and that it extends ->.",
         "solution": "Irreflexive and transitive: lexicographic order on pairs of integers is a strict total order on *distinct* pairs. Distinctness: two events of the same process have different Lamport times because IR1 ticks between them; events of different processes have different ids. So the key map is injective and the induced order on events is a strict total order. Extension: if a -> b then C(a) < C(b) by T23.1, so key(a) < key(b) whatever the ids. Remark: the order among concurrent events depends on the clock values and the id tie-break, so different clock implementations give different total orders (Lamport 1978: only -> is determined by the execution)."},
        {"id": "23-P3", "type": "proof", "difficulty": 3, "marks": 10,
         "problem": "Prove the harder direction of T23.2: if V(a) <= V(b) componentwise and a != b, then a -> b. State precisely which property of the update rule you use.",
         "solution": "Use the lemma V(e)[k] = number of events of P_k in past(e), proved by induction over the execution: a local/send event adds itself (component i + 1); a receive adds past(send) and itself, and because each process's events in a past form a prefix of its sequence, the union of two prefixes has the size of the longer one, which is exactly the element-wise maximum. Now let a be the c-th event of P_i, so V(a)[i] = c. V(a) <= V(b) gives V(b)[i] >= c, so past(b) contains the first c events of P_i, among them a. Hence a -> b or a = b, and a != b. The property used: the receive rule takes the element-wise maximum *before* ticking, and counts are prefixes (that is what makes max = union)."},
        {"id": "23-P4", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "Events x, y, z have vector timestamps V(x) = (2, 0, 1), V(y) = (1, 1, 1), V(z) = (2, 1, 1). For each pair, state whether one happened before the other or they are concurrent.",
         "answer": "x || y, y -> z, x -> z",
         "solution": "x vs y: 2 > 1 in component 1 but 0 < 1 in component 2, incomparable, so concurrent. y vs z: (1,1,1) <= (2,1,1) and different, so y -> z. x vs z: (2,0,1) <= (2,1,1) and different, so x -> z. Answer: x || y, y -> z, x -> z."},
        {"id": "23-P5", "type": "short-answer", "difficulty": 2, "marks": 6,
         "problem": "Classify each requirement as safety or liveness and justify in one line: (a) at most one leader per term; (b) every write is eventually replicated to all live replicas; (c) every response is sent within 200 ms of its request; (d) a fencing token never decreases; (e) the system eventually elects a leader once the network is stable.",
         "solution": "(a) Safety: a violation is two leaders in one term, visible at a finite point. (b) Liveness: any finite prefix can still be completed by replicating later. (c) Safety, a common surprise: if a response is late the violation is detectable at request time + 200 ms and no extension repairs it. (d) Safety: a decrease is a finite bad prefix. (e) Liveness, and conditional on a timing assumption (partial synchrony): by FLP it cannot be guaranteed in the pure asynchronous model."},
        {"id": "23-P6", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "In a synchronous model every one-way message delay is at most 50 ms and a node answers a ping within 5 ms of receiving it. What is the smallest timeout that never suspects a live node? What changes if the network is only partially synchronous?",
         "answer": "105 ms",
         "solution": "Round trip <= 50 + 5 + 50, so the smallest perfect timeout is 105 ms (T23.4a). Under partial synchrony the bound is unknown or holds only after GST, so any fixed timeout may produce false suspicions; adapt it (e.g. double after each false suspicion) so mistakes are finite, and make sure safety never depends on the detector being right (lease + fencing in L200 #7)."},
        {"id": "23-P7", "type": "calculation", "difficulty": 2, "marks": 6,
         "problem": "Two physical clocks each drift at most 50 ppm from true time. They are resynchronised every 60 s with an error of at most 1 ms. What is the largest possible difference between them just before a resynchronisation? Why is this bound useless for ordering events 2 ms apart on different machines?",
         "answer": "7 ms",
         "solution": "Relative drift <= 2 x 50 ppm = 100 ppm = 1e-4. Over 60 s that is 60,000 ms x 1e-4 = 6 ms, plus the 1 ms resync error: 7 ms. Events 2 ms apart on different machines can therefore carry timestamps in the wrong order; that is the skew lab 6 demonstrates. Use logical clocks for causality, or wait out the uncertainty (commit-wait in TrueTime-style systems)."},
        {"id": "23-P8", "type": "short-answer", "difficulty": 2, "marks": 6,
         "problem": "A Paxos acceptor or Raft voter keeps its promise / vote in memory only. Which system model makes this a bug, and give an execution that breaks safety.",
         "solution": "Crash-recovery. A node votes for candidate A in term 5, crashes, restarts with empty memory, and votes for B in term 5; A and B each count it towards a majority, so two leaders are elected in term 5 (Election Safety violated). In the crash-stop model the node never returns, so the bug is invisible - which is why the L400 #21 model checker had to model restarts to find it. Fix: persist the vote/promise before replying (Raft Figure 2: 'updated on stable storage before responding to RPCs')."},
    ],
    "rubric": WRITTEN_RUBRIC,
    "conceptNote": "content/concepts/L500/23-system-models-time.md",
    "conceptSummary": "A system model fixes timing (synchronous, asynchronous, partially synchronous) and faults (crash-stop, crash-recovery, Byzantine). Lamport clocks satisfy a -> b => C(a) < C(b) but not the converse; vector clocks make it an equivalence. Safety failures have finite witnesses, liveness failures never do. Without a delay bound a timeout is a guess: perfect at 105 ms when delays are bounded, always fallible when they are not.",
    "sources": [LAMPORT_1978, KLEPPMANN, ALPERN, DLS],
    "seeAlso": [
        "distributed-systems L100 #6 Ordering events with Lamport clocks: the lab whose ordering T23.1 proves correct for causally related events only",
        "distributed-systems L100 #3 Timeouts: fail fast instead of hanging: T23.4 explains why its p99.9-based timeout is a probability, not a guarantee",
        "distributed-systems L200 #7 Leader election with leases and fencing tokens: safety by fencing (an invariant), liveness by lease timeouts (a timing assumption)",
        "distributed-systems L400 #18 CRDTs for local-first collaboration: counters, OR-Set, LWW-Register and property tests: concurrency detection (T23.2) decides when a merge is needed",
    ],
    "next": "L500 #24 Foundations II: impossibility results and consensus - two generals, FLP, CAP, quorums and Paxos - what can and cannot be agreed in these models",
    "platforms": PLATFORMS,
}

# ------------------------------------------------------------------------------------------------
LESSON_24 = {
    "id": "foundations-impossibility-consensus",
    "number": 24,
    "level": "L500",
    "title": "Foundations II: impossibility results and consensus - two generals, FLP, CAP, quorums and Paxos",
    "category": "theory",
    "description": "Prove the two generals impossibility, sketch FLP from the original paper, state and prove CAP as Gilbert and Lynch did (not the slogan), prove quorum intersection and the safety of single-decree Paxos from its invariant, and compare with Raft; check each claim by exhaustive or randomised exploration.",
    "outcome": "You can say precisely what each impossibility result forbids and what it leaves open, prove why majority quorums and Paxos's phase 1 keep a decision unique, and judge a 'CAP says...' or 'consensus is impossible' argument in a design review.",
    "estimatedTime": "4 hours (reading, proofs, code checks, problem set)",
    "prerequisites": [
        "Proof by induction (strong induction on ballot numbers) and by contradiction",
        "Combinatorics: subsets, pigeonhole principle",
        "Lesson 23 (system models, safety vs liveness); Lessons 12 (Raft) and 17 (quorums) for the practice",
    ],
    "learningObjectives": [
        "Prove that no protocol over a lossy channel guarantees coordinated action (two generals) and explain why idempotency and compensation sidestep it in practice.",
        "Explain the FLP theorem's exact assumptions and its proof structure (bivalence), and evaluate what Paxos and Raft give up to work anyway.",
        "State CAP precisely as Gilbert and Lynch proved it, derive the proof, and critique the 'pick two of three' slogan.",
        "Prove the quorum intersection lemma (R + W > N) and use it in an invariant-based proof that single-decree Paxos chooses at most one value.",
        "Compare Paxos's phase-1 value adoption with Raft's election restriction and analyze which property each one protects.",
    ],
    "glossary": [
        {"term": "consensus", "meaning": "Agreement (no two correct processes decide differently), validity (a decision was someone's input), termination (every correct process decides)."},
        {"term": "valency", "meaning": "FLP: a configuration is bivalent if both decisions are still reachable, 0- or 1-valent if only one is."},
        {"term": "atomic (linearizable) register", "meaning": "Gilbert & Lynch's C: a total order of operations, each appearing at one instant between invocation and response."},
        {"term": "availability (CAP)", "meaning": "Every request received by a non-failing node eventually gets a response - a liveness property with no time bound."},
        {"term": "quorum", "meaning": "A set of replicas whose agreement is required; R + W > N makes every read quorum meet every write quorum."},
        {"term": "ballot / proposal number", "meaning": "Totally ordered, unique number that tags a Paxos proposal; Raft's term plays the same role."},
        {"term": "P2c", "meaning": "Paxos invariant: a proposal (n, v) is issued only if some majority S has accepted nothing below n, or v is the value of the highest-numbered proposal below n accepted in S."},
    ],
    "theorems": [
        {
            "name": "T24.1 The two generals cannot coordinate over a lossy channel",
            "statement": "Over a channel that may lose any message, no deterministic protocol guarantees all three of: (i) agreement - both generals attack or neither does; (ii) nobody attacks if no message is delivered; (iii) both attack if no message is lost.",
            "proof": (
                "**By contradiction, minimal-run argument** (the problem is from Gray 1978; Kleppmann's notes §2.1 give the intuition).\n\n"
                "Suppose protocol P satisfies (i)-(iii). In the loss-free run both decide in finite time, so it delivers finitely many messages m_1, ..., m_k, and both attack by (iii). Let r_j be the run in which m_1..m_j are delivered and every later message is lost (r_k is the loss-free run).\n"
                "1. In r_0 nothing is delivered, so nobody attacks by (ii); in r_k both attack. Let j >= 1 be the smallest index such that some general attacks in r_j.\n"
                "2. r_{j-1} and r_j differ only in whether m_j arrives. Its sender (say A) receives nothing after m_j in either run (all later messages are lost), so A's local history - and, P being deterministic, A's decision - is identical in both runs.\n"
                "3. Nobody attacks in r_{j-1} (minimality), so A does not attack in r_j. Someone attacks in r_j, so it is B: disagreement, contradicting (i). ∎\n\n"
                "**What engineers do instead.** Make the action reversible or repeatable: the shop refunds, the payment is idempotent (L100 #5), the saga compensates (L300 #14). Kleppmann's payment example works because a charge can be undone; an attack cannot.\n\n"
                "**The check** enumerates a bounded family (alternating messengers, threshold decisions) and finds a disagreeing run for every member - an instance of the proof, not a substitute for it."
            ),
            "check": "labs/L500/24-impossibility-consensus/consensus_proofs.py generals",
        },
        {
            "name": "T24.2 FLP: no deterministic asynchronous consensus tolerates one crash (Fischer, Lynch & Paterson 1985, Theorem 1)",
            "statement": "In the asynchronous model - no bound on message delay or relative speed, no synchronized clocks, no way to detect a crash, but reliable delivery of every message - every partially correct consensus protocol for N >= 2 processes has an admissible run (at most one process faulty, every message to a non-faulty process eventually received) in which no process ever decides.",
            "proof": (
                "**Proof sketch; the full proof is FLP 1985 §3 (JACM 32(2):374-382).**\n\n"
                "*Valency.* A configuration is bivalent if configurations deciding 0 and deciding 1 are both reachable from it, univalent otherwise. Partial correctness requires both decisions to be possible from some initial configuration.\n\n"
                "*Lemma 1 (commutativity).* Schedules applied by disjoint sets of processes commute.\n\n"
                "*Lemma 2 (a bivalent start exists).* Assume not. Chain the initial configurations so neighbours differ in one process's input; somewhere a 0-valent C0 sits next to a 1-valent C1, differing in process p. Run C0 with p silent (allowed: one process may be faulty) to a decision; the same schedule from C1 is indistinguishable to everyone else and reaches the same decision, so one of C0, C1 is bivalent - contradiction.\n\n"
                "*Lemma 3 (bivalence can be preserved).* From a bivalent C and any applicable event e = (p, m), some configuration reached by applying e *last* is bivalent. If not, there are neighbours C0, C1 (one step e' apart) with e(C0) 0-valent and e(C1) 1-valent. If e' is by another process, e and e' commute (Lemma 1) - contradiction. If e' is by p, run from C0 a deciding schedule in which p takes no steps; appending e or e'e leads to both decisions, so that deciding configuration would be bivalent - contradiction.\n\n"
                "*Construction.* Keep a queue of processes; at each stage apply Lemma 3 to the head process's oldest message, ending in a bivalent configuration. Every process takes infinitely many steps and receives every message (admissible), yet no configuration is ever univalent, so nobody decides. ∎\n\n"
                "**What FLP does not say.** It does not make consensus impossible in practice: termination can be achieved with randomisation, with unreliable failure detectors (Chandra & Toueg 1996; Chandra, Hadzilacos & Toueg showed the weakest one for consensus is a leader oracle, Omega - as summarised by Gilbert & Lynch 2012 §3.3.1), or under partial synchrony (Dwork, Lynch & Stockmeyer). Paxos and Raft keep *safety* unconditionally and get *liveness* only when timing behaves - Lamport (2001 §2.4) cites FLP for exactly this: electing the distinguished proposer needs randomness or real time.\n\n"
                "**The check** illustrates (does not prove) the theorem: an adversarial schedule makes two Paxos proposers pre-empt each other for 1,000 rounds - always safe, never decided - and a random backoff, i.e. a timing assumption, ends the duel."
            ),
            "check": "labs/L500/24-impossibility-consensus/consensus_proofs.py flp",
        },
        {
            "name": "T24.3 CAP, precisely (Gilbert & Lynch 2002, Theorem 1 and Corollary 1.1)",
            "statement": "In the asynchronous network model it is impossible to implement a read/write data object that guarantees both availability (every request received by a non-failing node eventually receives a response) and atomic consistency (linearizability) in all fair executions, including those in which messages are lost. Corollary: it is impossible even if atomicity is required only in executions in which no messages are lost.",
            "proof": (
                "**Model (Gilbert & Lynch §2).** C = an atomic (linearizable) single register: any read that begins after a write completes returns that value or a later one. A = every request to a non-failing node terminates, with no time bound. P = the network may lose arbitrarily many messages; a partition loses every message between its components.\n\n"
                "**Proof (by contradiction).** Suppose algorithm A is available and atomic. Split the nodes into non-empty groups G1, G2 and lose every message between them. Let v0 be the initial value.\n"
                "1. alpha_1: a client writes v1 != v0 at a node in G1; by availability the write completes. No message reaches G2.\n"
                "2. alpha_2: (a separate execution) a client reads at a node in G2; by availability it returns, and since nothing was ever written it returns v0.\n"
                "3. alpha = alpha_1 followed by alpha_2. Nodes in G2 receive nothing from G1 in either, so alpha is indistinguishable from alpha_2 to G2: the read returns v0, although it began after the write of v1 completed. Not atomic - contradiction. ∎\n\n"
                "**Corollary 1.1.** An asynchronous node cannot tell a lost message from a slow one; truncate a violating execution at the bad response and extend it so every message is delivered later: a fair, loss-free execution with a non-atomic response.\n\n"
                "**Reading it correctly.** (1) It is about one register's linearizability and unbounded-time availability, not 'consistency' in the ACID sense. (2) 'Pick two of three' misleads: with no partition both C and A are achievable (§3.2.2), and a real system chooses per operation and per data item (Gilbert & Lynch 2012 §4.4). (3) In the partially synchronous model the theorem still holds when messages are lost (Theorem 2), but an algorithm can be atomic whenever no messages are lost and return stale data only during a partition - which is why PACELC (L400 #17) asks about latency when there is *no* partition.\n\n"
                "**The check** runs Gilbert & Lynch's execution against two always-answering designs (both return v0 after the write completed) and a majority-quorum design (atomic, but n1 and n2 cannot answer)."
            ),
            "check": "labs/L500/24-impossibility-consensus/consensus_proofs.py cap",
        },
        {
            "name": "T24.4 Quorum intersection and the safety of single-decree Paxos",
            "statement": "(a) Lemma: with N replicas, every read quorum of size R intersects every write quorum of size W if and only if R + W > N; in particular any two majorities intersect. (b) Theorem (Lamport 2001): if every acceptor accepts proposal n only when it has not answered a prepare numbered above n (P1a), persists its promise and acceptance, and every proposer issues (n, v) only after collecting promises from a majority S with v = the value of the highest-numbered proposal accepted in S (or its own value if none), then invariant P2c holds, hence P2b - if (m, v) is chosen, every proposal issued with number n > m has value v - hence at most one value is ever chosen.",
            "proof": (
                "**(a)** If R + W > N then |Q_R ∩ Q_W| >= R + W - N >= 1 (pigeonhole: the two sets cannot fit disjointly into N nodes). If R + W <= N, take Q_R = the first R nodes and Q_W = the last W nodes: disjoint. Two majorities: 2 * (floor(N/2) + 1) > N. ∎\n\n"
                "**(b) Invariant proof.** Suppose (m, v) is chosen: a majority C accepted it. Show by strong induction on n > m that every issued proposal (n, w) has w = v, assuming it for all issued proposals numbered m..n-1.\n"
                "1. The proposer of n received promises from a majority S. By (a), some acceptor c is in both S and C.\n"
                "2. c accepted (m, v) *before* promising n: had it promised n first, P1a would forbid accepting m < n. So c's promise reported an accepted proposal numbered k with m <= k < n.\n"
                "3. The proposer adopts the highest-numbered proposal reported in S; its number k' satisfies m <= k <= k' < n, so by the induction hypothesis its value is v. Hence w = v.\n"
                "So P2b holds. If two values were chosen, at (m, v) and (m', v') with m < m', then (m', v') was issued, so v' = v. ∎\n\n"
                "**What the proof needs.** Unique ballot numbers (disjoint number sets per proposer), quorum intersection, and stable storage for promises and acceptances (crash-recovery model; see 23-P8). It needs *no* timing assumption: liveness does (T24.2).\n\n"
                "**Raft comparison** (Ongaro & Ousterhout 2014 §5.4). Raft's term is Paxos's ballot; its majority vote and majority commit are the two intersecting quorums. Instead of adopting a value in phase 1, Raft restricts *who can be elected*: a voter refuses a candidate whose log is less up-to-date (last term, then length). The Leader Completeness proof uses the same step 1-2 argument: some voter both accepted the committed entry and voted for the new leader. Raft also forbids committing old-term entries by counting replicas (§5.4.2, Figure 8) - the log analogue of adopting only the highest-numbered accepted value. L300 #12 removes the election restriction and the check there loses committed entries; the broken variant here (ignore phase-1 values) chooses two values in most runs."
            ),
            "check": "labs/L500/24-impossibility-consensus/consensus_proofs.py paxos",
        },
    ],
    "problemSet": [
        {"id": "24-P1", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "A leaderless store has N = 7 replicas and reads use R = 3. What is the smallest W such that every read sees the latest completed write AND any two writes overlap (so a version conflict is always detected)?",
         "answer": "W = 5",
         "solution": "Read-write overlap needs R + W > N, so W >= 5. Write-write overlap needs W + W > N, so W >= 4. Both: W = 5. Check with the lemma: |Q_R ∩ Q_W| >= 3 + 5 - 7 = 1."},
        {"id": "24-P2", "type": "proof", "difficulty": 1, "marks": 5,
         "problem": "Prove that if R + W <= N there exist a read quorum and a write quorum with no replica in common, and describe the stale read this allows.",
         "solution": "Number the replicas 1..N. Let Q_W = {1..W} and Q_R = {N-R+1..N}. Since R + W <= N, N - R + 1 > W, so the sets are disjoint. A write acknowledged by Q_W followed by a read answered by Q_R returns the old value although the write completed - the stale read lab 17 measures at R = 1, W = 1."},
        {"id": "24-P3", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "How many crashed acceptors can single-decree Paxos tolerate with N = 5 and with N = 6 while still choosing a value? How many nodes does Byzantine agreement need to tolerate f = 2 traitors (Dwork, Lynch & Stockmeyer, as quoted in Kleppmann's notes)?",
         "answer": "N = 5 and N = 6 both tolerate 2 crashes; 7 nodes for f = 2 Byzantine",
         "solution": "Progress needs a majority floor(N/2) + 1 alive: N = 5 needs 3, tolerates 2; N = 6 needs 4, tolerates 2. An even N adds cost without adding tolerance. Byzantine agreement with unpredictable delays needs N >= 3f + 1 = 7 for f = 2. Answer: N = 5 and N = 6 both tolerate 2 crashes; 7 nodes for f = 2 Byzantine."},
        {"id": "24-P4", "type": "proof", "difficulty": 2, "marks": 8,
         "problem": "Write the two generals impossibility proof in your own words, naming exactly where determinism and the lossy channel are used.",
         "solution": "Model answer follows T24.1: take the loss-free run with k messages; define r_j (first j delivered); r_0 nobody attacks, r_k both attack; minimal j with an attacker. Lossy channel: needed so that each r_j is a legal run (messages after j may be lost). Determinism: needed so that the sender of m_j, whose local history is the same in r_{j-1} and r_j, decides the same in both. Then the sender does not attack in r_j and the receiver does: disagreement. Full marks need both uses named and the minimality argument."},
        {"id": "24-P5", "type": "short-answer", "difficulty": 2, "marks": 6,
         "problem": "A colleague says 'FLP proves Raft cannot work.' Give a precise rebuttal (which FLP assumption Raft drops, what it gives up, and what still holds unconditionally).",
         "solution": "FLP assumes a deterministic protocol in a fully asynchronous model and asks for guaranteed termination. Raft keeps safety (Election Safety, Log Matching, Leader Completeness, State Machine Safety) in every execution and only promises liveness when timing behaves: randomized election timeouts and the requirement broadcastTime << electionTimeout << MTBF (Ongaro & Ousterhout §5.6) are a partial-synchrony assumption plus randomisation. So FLP's adversarial schedule can delay Raft forever (repeated split votes), but cannot make it decide two values."},
        {"id": "24-P6", "type": "calculation", "difficulty": 2, "marks": 6,
         "problem": "Single-decree Paxos, acceptors A1, A2, A3. A1 has accepted (2, 'x'), A2 has accepted (3, 'y'), A3 has accepted nothing. A proposer runs phase 1 with ballot 5. Which value must it propose if the promises come from {A1, A3}? From {A2, A3}? Is either value necessarily chosen already?",
         "answer": "x with promises from A1 and A3; y with promises from A2 and A3",
         "solution": "Phase 2 must use the value of the highest-numbered accepted proposal among the promises. {A1, A3}: only (2, 'x') reported, so propose x. {A2, A3}: (3, 'y'), so propose y. Answer: x with promises from A1 and A3; y with promises from A2 and A3. Neither is necessarily chosen: x was accepted by one acceptor and y by one, never a majority. That the proposer may end up with either shows phase 1 protects only a value that *might* be chosen; P2c guarantees that if one were chosen, every majority would contain an acceptor reporting it."},
        {"id": "24-P7", "type": "essay", "difficulty": 3, "marks": 12,
         "problem": "Critique the statement 'Our database is CP, so it is always consistent and partitions are the only reason it is ever unavailable.' Use the precise CAP statement, PACELC (lab 17) and at least one measurement from the labs. (400-600 words)",
         "solution": "Strong answers make four points. (1) CAP's C is linearizability of a single object and its A is unbounded-time response; 'CP' says only that during a partition the system refuses some requests rather than answer non-atomically. (2) It says nothing about the common case: PACELC's else-branch (latency vs consistency) is paid on every request - lab 17 measured p99 65.9 ms vs 124.5 ms for plain quorums vs read write-back. (3) Unavailability has many causes besides partitions: leader election after a crash (lab 19's RTO ~1.3 s), overload (lab 16), GC pauses - and in an asynchronous network a slow node is indistinguishable from a partition (Corollary 1.1), so a CP system may refuse requests with no partition at all. (4) 'Always consistent' depends on configuration: a quorum system with R + W > N but no read write-back is not linearizable (lab 17's inversions). A balanced conclusion: state the model (single-key linearizable writes, majority quorums), the guarantee per operation, the measured latency cost, and the availability under each failure."},
        {"id": "24-P8", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "A Raft cluster has 5 servers. How many votes does a candidate need? Can a leader be elected with 2 servers down? With 3 down?",
         "answer": "3 votes; yes with 2 down; no with 3 down",
         "solution": "A candidate needs a majority of the full cluster, floor(5/2) + 1 = 3 votes (including its own). With 2 down, 3 remain: enough. With 3 down, 2 remain: no election, and no commits either - Raft is CP. Answer: 3 votes; yes with 2 down; no with 3 down."},
    ],
    "rubric": WRITTEN_RUBRIC,
    "conceptNote": "content/concepts/L500/24-impossibility-consensus.md",
    "conceptSummary": "Over a lossy channel no protocol makes two parties act together (two generals). In an asynchronous system no deterministic consensus survives one crash (FLP), so practical protocols keep safety always and liveness only under partial synchrony. CAP, as Gilbert and Lynch proved it, is about a linearizable register and unbounded-time responses during message loss. Majority quorums intersect, and Paxos's phase 1 carries any possibly-chosen value forward: that invariant, not timing, makes the decision unique; Raft gets the same effect through its election restriction.",
    "sources": [FLP, GL2002, PAXOS, RAFT, KLEPPMANN, GL2012],
    "seeAlso": [
        "distributed-systems L300 #12 Replicated log with Raft (simplified): terms, commit index, re-election, election restriction: removing the election restriction breaks the T24.4 argument and loses committed entries",
        "distributed-systems L400 #17 Consistency models in practice: quorums (N, R, W), staleness and PACELC: the R + W > N lemma measured, and why overlap alone is not linearizable",
        "distributed-systems L300 #13 Network partitions and fault injection: proxy toxics, split brain, fencing and linearizability checking: the CAP execution reproduced with a proxy",
        "distributed-systems L300 #14 Sagas with compensation: orchestration vs choreography, idempotent steps, saga log: how practice sidesteps the two generals by making actions reversible",
        "distributed-systems L400 #21 Verifying correctness: model checking and linearizability checking: exhaustive checking of an election protocol's safety invariant",
    ],
    "next": "L500 #25 Foundations III: performance theory - M/M/1, Little's law, tail amplification, Amdahl and USL - from 'is it correct?' to 'how fast, and how far does it scale?'",
    "platforms": PLATFORMS,
}

# ------------------------------------------------------------------------------------------------
LESSON_25 = {
    "id": "foundations-performance-theory",
    "number": 25,
    "level": "L500",
    "title": "Foundations III: performance theory - M/M/1, Little's law, tail amplification, Amdahl and USL",
    "category": "theory",
    "description": "Derive the M/M/1 queue's distribution and mean delay, prove Little's law with the area argument, derive the probability that a fan-out request meets a slow leaf, derive Amdahl's bound and the USL peak - and check each against a seeded simulation.",
    "outcome": "You can predict queueing delay from utilisation, size concurrency with Little's law, compute the tail a fan-out inherits from its leaves, and estimate where adding nodes stops helping - and you know which assumptions each formula needs.",
    "estimatedTime": "3-4 hours (derivations, simulations, problem set)",
    "prerequisites": [
        "Probability: exponential distribution, independence, geometric series, P(at least one) = 1 - P(none)",
        "Calculus: derivative of a quotient, finding a maximum",
        "Lesson 16 (backpressure and load shedding) and Lesson 3 (timeouts) for the practice",
    ],
    "learningObjectives": [
        "Derive the stationary distribution of the M/M/1 queue from the balance equations and explain why delay grows as 1/(1 - rho).",
        "Prove Little's law L = lambda W on a window that starts and ends empty and explain what is needed for arbitrary windows.",
        "Derive P(a fan-out of n waits for a slow leaf) = 1 - (1 - p)^n and evaluate how strict each leaf's percentile target must be.",
        "Derive Amdahl's bound and the USL peak p* = sqrt((1 - sigma)/kappa), and analyze measured scaling data by fitting the USL.",
        "Critique a capacity plan that uses averages where the formulas' assumptions (stationarity, independence, rho < 1) fail.",
    ],
    "glossary": [
        {"term": "M/M/1", "meaning": "Poisson arrivals (rate lambda), exponential service (rate mu), one server, FIFO, infinite buffer."},
        {"term": "utilisation rho", "meaning": "lambda / mu, the fraction of time the server is busy; the queue is stable only if rho < 1."},
        {"term": "L, W, Wq", "meaning": "Mean number in system, mean time in system (sojourn), mean time waiting in the queue."},
        {"term": "Little's law", "meaning": "L = lambda W for any stable system, whatever the arrival or service distributions."},
        {"term": "tail amplification", "meaning": "A request that waits for n parallel leaves is slow if any leaf is slow: 1 - (1 - p)^n."},
        {"term": "Amdahl's law", "meaning": "Speedup S(p) = p / (1 + sigma (p - 1)) <= 1/sigma with serial fraction sigma."},
        {"term": "USL", "meaning": "Universal Scalability Law C(p) = p / (1 + sigma (p - 1) + kappa p (p - 1)): contention sigma plus coherency kappa; peak at sqrt((1 - sigma)/kappa)."},
    ],
    "theorems": [
        {
            "name": "T25.1 The M/M/1 queue",
            "statement": "For Poisson arrivals at rate lambda, exponential service at rate mu and rho = lambda/mu < 1, the stationary number in system is geometric: P(N = n) = (1 - rho) rho^n. Hence L = rho/(1 - rho), W = 1/(mu - lambda) and Wq = rho/(mu - lambda).",
            "proof": (
                "**Birth-death chain.** With memoryless arrivals and service, the number in system N(t) is a continuous-time Markov chain that moves n -> n+1 at rate lambda and n -> n-1 at rate mu (n >= 1).\n\n"
                "**Cut equations.** In steady state the probability flow across the cut between states n and n+1 balances: lambda p_n = mu p_{n+1}. So p_{n+1} = rho p_n and p_n = rho^n p_0.\n\n"
                "**Normalise.** sum p_n = p_0 / (1 - rho) = 1 needs rho < 1 and gives p_0 = 1 - rho (the idle fraction; the server is busy rho of the time, as it must be).\n\n"
                "**Means.** L = sum n (1 - rho) rho^n = (1 - rho) rho / (1 - rho)^2 = rho/(1 - rho). By Little's law (T25.2), W = L/lambda = 1/(mu - lambda); subtracting the mean service time 1/mu gives Wq = rho/(mu - lambda). ∎\n\n"
                "**Intuition.** W = (1/mu) * 1/(1 - rho): at rho = 0.5 a request spends 2 service times in the system, at 0.8 five, at 0.9 ten. The last 10% of utilisation doubles the delay - why lab 16 sheds load before the queue grows rather than after.\n\n"
                "**The check** simulates 400,000 customers per load with the Lindley recursion and integrates n(t) over time."
            ),
            "check": "labs/L500/25-performance-theory/perf_proofs.py mm1",
        },
        {
            "name": "T25.2 Little's law (Little 1961; Little & Graves 2008)",
            "statement": "For any queueing system and any window [0, T] that starts and ends empty, the time-average number in system equals the arrival rate times the mean time in system: L_T = lambda_T W_T exactly. Under stationarity (the limits exist and are finite) L = lambda W, with no assumption about arrival or service distributions, the number of servers, or the order of service.",
            "proof": (
                "**Area argument** (as in Little & Graves's picture proof). Let n(t) be the number in the system and customer i be present from a_i to d_i.\n"
                "1. The area under n(t) on [0, T] counts, for every instant, the customers present. Swap the order of counting: each customer contributes the length of its stay. If the system is empty at 0 and T, every customer who arrives in [0, T] also leaves in it, so integral_0^T n(t) dt = sum_i (d_i - a_i).\n"
                "2. Divide by T and multiply and divide by A(T), the number of arrivals: L_T = integral/T = (A(T)/T) * (sum_i W_i / A(T)) = lambda_T W_T. ∎\n"
                "3. For a window that does not end empty, the customers still present at T contribute only part of their stay; the difference between the two sides is bounded by those edge terms, which are o(T) when L and W are finite, so the identity holds in the limit.\n\n"
                "**Use it as a sizing tool.** Two of the three are easy to measure, the third follows: 300 req/s at 40 ms means 12 requests in flight, so 12 workers is the floor, not the target (lab 16 limits concurrency with exactly this relation).\n\n"
                "**The check** uses non-Markov arrivals and log-normal service: on a window that ends empty the two sides agree to floating-point precision (about 1e-15); on an arbitrary window they agree to 4 decimals."
            ),
            "check": "labs/L500/25-performance-theory/perf_proofs.py little",
        },
        {
            "name": "T25.3 Tail amplification under fan-out",
            "statement": "If a root request waits for n leaves that are independently slow with probability p, then P(root slow) = 1 - (1 - p)^n, which is about n p when n p is small. To keep P(root slow) <= q, each leaf must satisfy p <= 1 - (1 - q)^(1/n), about q/n. For any dependence between leaves, max p_i <= P(root slow) <= min(1, sum p_i).",
            "proof": (
                "**Derivation.** The root is fast only if every leaf is fast. With independence, P(all fast) = (1 - p)^n, so P(some leaf slow) = 1 - (1 - p)^n. For small x, (1 - x)^n = e^(n ln(1 - x)) ≈ 1 - n x, giving ≈ n p. Inverting: (1 - p)^n >= 1 - q iff p <= 1 - (1 - q)^(1/n) ≈ q/n.\n\n"
                "**Without independence.** The event 'root slow' is the union of the leaf events: it contains each one (lower bound max p_i) and its probability is at most their sum (union bound). Positive correlation (a shared GC pause, a hot switch) pushes the value towards the lower bound; independence is the pessimistic case for a fixed per-leaf p.\n\n"
                "**Numbers.** Dean & Barroso's example: leaves usually answer in 10 ms but 1% take a second; with 100 leaves per request, 63% of requests take more than a second (1 - 0.99^100 = 63.4%); with 2,000 leaves each slow only once in 10,000, almost one in five (1 - 0.9999^2000 = 18.1%). To keep the root at 1% slow, each leaf needs its 0.9999 quantile under the threshold - p99.99, not p99. Remedies from the paper: hedged and tied requests, micro-partitioning, and selective replication - each attacks p or n.\n\n"
                "**The check** draws log-normal leaf latencies and counts roots that wait for a leaf above the leaf p99."
            ),
            "check": "labs/L500/25-performance-theory/perf_proofs.py tail",
        },
        {
            "name": "T25.4 Amdahl's bound and the USL peak",
            "statement": "(a) Amdahl: if a fraction sigma of a fixed job is serial, S(p) = 1 / (sigma + (1 - sigma)/p) = p / (1 + sigma (p - 1)), which increases with p and is bounded by 1/sigma. (b) USL (Gunther): C(p) = p / (1 + sigma (p - 1) + kappa p (p - 1)) with kappa > 0 has a unique maximum at p* = sqrt((1 - sigma)/kappa) and decreases (retrograde scaling) beyond it.",
            "proof": (
                "**(a)** Time on p processors = sigma T_1 + (1 - sigma) T_1 / p. Divide T_1 by it: S(p) = 1/(sigma + (1 - sigma)/p); multiply top and bottom by p for the second form. As p -> infinity the denominator tends to sigma, so S(p) < 1/sigma, and dS/dp = (1 - sigma)/(1 + sigma (p - 1))^2 > 0. Amdahl's 1967 paper states the argument in words; the formula is the standard reading (Gunther 2008 eq. 1-2).\n\n"
                "**(b)** Write C = p/D with D(p) = 1 + sigma (p - 1) + kappa p (p - 1). Then C'(p) = (D - p D')/D^2, and D - p D' = 1 + sigma p - sigma + kappa p^2 - kappa p - sigma p - 2 kappa p^2 + kappa p = 1 - sigma - kappa p^2. This is positive for p < p* and negative for p > p*, where p* = sqrt((1 - sigma)/kappa): a unique maximum, and retrograde throughput after it. Amdahl is the case kappa = 0. ∎\n\n"
                "**Interpretation.** sigma is contention (queueing for a shared resource: a lock, a leader, a single partition); kappa is coherency (pairwise exchange to keep copies consistent - p(p - 1) pairs). Gunther (2008) shows the USL equals the synchronous throughput bound of a machine-repairman queue with load-dependent service; it is a model to fit to measurements, not a law of nature.\n\n"
                "**The check** verifies the closed-form peak against a numerical argmax, then simulates a closed system (p workers sharing one lock whose hold time grows with p - 1), fits sigma and kappa by least squares (sigma constrained >= 0), and compares the predicted peak with the measured one (15.3 vs 13: a useful but approximate forecast)."
            ),
            "check": "labs/L500/25-performance-theory/perf_proofs.py usl",
        },
    ],
    "problemSet": [
        {"id": "25-P1", "type": "calculation", "difficulty": 1, "marks": 5,
         "problem": "An API instance behaves like an M/M/1 queue with lambda = 80 requests/s and mu = 100 requests/s. Compute rho, L, W and Wq.",
         "answer": "rho = 0.8, L = 4, W = 50 ms, Wq = 40 ms",
         "solution": "rho = 80/100 = 0.8. L = 0.8/0.2 = 4. W = 1/(100 - 80) s = 50 ms. Wq = W - 1/mu = 50 - 10 = 40 ms. Answer: rho = 0.8, L = 4, W = 50 ms, Wq = 40 ms. Check with Little: lambda W = 80 x 0.05 = 4 = L."},
        {"id": "25-P2", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "A service receives 2,000 requests/s with mean latency 150 ms. How many requests are in flight on average? Each instance has 64 worker threads; what is the minimum number of instances?",
         "answer": "L = 300 in flight; 5 instances",
         "solution": "Little: L = lambda W = 2,000 x 0.150 = 300. Instances >= 300/64 = 4.69, so 5. Answer: L = 300 in flight; 5 instances. This is a floor: at 5 instances the threads are 94% busy, and T25.1 says queueing delay explodes near full utilisation, so plan for headroom."},
        {"id": "25-P3", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "Each leaf exceeds its latency threshold 1% of the time, independently. What fraction of root requests is slow with fan-out 100? With fan-out 50 if each leaf is slow only 0.1% of the time?",
         "answer": "63.4% and 4.9%",
         "solution": "1 - 0.99^100 = 0.634 and 1 - 0.999^50 = 0.0488. Answer: 63.4% and 4.9%. Halving the fan-out matters less than tightening the leaf tail by 10x."},
        {"id": "25-P4", "type": "calculation", "difficulty": 2, "marks": 5,
         "problem": "With fan-out 100, which per-leaf quantile must stay under the threshold so that only 1% of root requests exceed it (independent leaves)?",
         "answer": "0.999900 (p99.99)",
         "solution": "Need (1 - p)^100 >= 0.99, so 1 - p >= 0.99^(1/100) = 0.999900. Answer: 0.999900 (p99.99). Approximation q/n = 0.01/100 = 0.0001 agrees."},
        {"id": "25-P5", "type": "calculation", "difficulty": 1, "marks": 4,
         "problem": "A batch job is 5% serial. What speedup does Amdahl's law predict on 16 cores, and what is the limit?",
         "answer": "S(16) = 9.14; limit 20",
         "solution": "S(16) = 16/(1 + 0.05 x 15) = 16/1.75 = 9.14; limit 1/0.05 = 20. Answer: S(16) = 9.14; limit 20. Even 1,024 cores give only 19.64."},
        {"id": "25-P6", "type": "calculation", "difficulty": 2, "marks": 6,
         "problem": "A fitted USL has sigma = 0.02 and kappa = 0.0005. Where is the throughput peak, and what relative capacity does it reach? What happens if you add more nodes?",
         "answer": "p* = 44.3 (best integer 44, C = 15.68)",
         "solution": "p* = sqrt(0.98/0.0005) = sqrt(1960) = 44.3. C(44) = 44/(1 + 0.02 x 43 + 0.0005 x 44 x 43) = 44/2.806 = 15.68. Answer: p* = 44.3 (best integer 44, C = 15.68). Beyond it the coherency term dominates and total throughput falls: adding nodes makes the system slower, so reduce kappa (less cross-node coordination: shard, avoid broadcast invalidation) instead."},
        {"id": "25-P7", "type": "derivation", "difficulty": 2, "marks": 6,
         "problem": "Derive W = 1/(mu - lambda) for M/M/1 from the geometric distribution and Little's law, stating every assumption you use.",
         "solution": "Assumptions: Poisson arrivals, exponential service, FIFO single server, rho = lambda/mu < 1, steady state. Balance across the cut n|n+1: lambda p_n = mu p_{n+1}, so p_n = rho^n p_0; normalising gives p_0 = 1 - rho. L = sum n p_n = (1 - rho) sum n rho^n = (1 - rho) rho/(1 - rho)^2 = rho/(1 - rho). Little (valid for any stable system): W = L/lambda = rho/(lambda (1 - rho)) = (1/mu)/(1 - rho) = 1/(mu - lambda)."},
        {"id": "25-P8", "type": "calculation", "difficulty": 1, "marks": 3,
         "problem": "In an M/M/1 queue, at what utilisation does the mean time in system reach 10 mean service times?",
         "answer": "rho = 0.9",
         "solution": "W = (1/mu)/(1 - rho) = 10/mu gives 1 - rho = 0.1. Answer: rho = 0.9 (the simulation in T25.1 measured W = 9.84 at rho = 0.9 over 400,000 customers - close, with the slow convergence typical near saturation)."},
    ],
    "rubric": WRITTEN_RUBRIC,
    "conceptNote": "content/concepts/L500/25-performance-theory.md",
    "conceptSummary": "Queueing delay scales with 1/(1 - rho): an M/M/1 server at 90% busy holds a request for 10 service times. Little's law (L = lambda W) needs no distributional assumptions and sizes concurrency. Fan-out multiplies tail risk: 1 - (1 - p)^n, 63% slow at n = 100, p = 1%. Amdahl caps speedup at 1/sigma; the USL adds coherency cost and a peak at sqrt((1 - sigma)/kappa) beyond which more nodes mean less throughput. Every formula here is checked against a seeded simulation.",
    "sources": [LITTLE, TAIL, GUNTHER, AMDAHL],
    "seeAlso": [
        "distributed-systems L300 #16 Backpressure and load shedding: bounded queues, 503 + Retry-After, AIMD concurrency limits: T25.1's 1/(1 - rho) is why the unbounded queue's p99 reached 4.6 s",
        "distributed-systems L100 #3 Timeouts: fail fast instead of hanging: a timeout set at a leaf percentile becomes a root failure rate via T25.3",
        "distributed-systems L300 #15 Distributed tracing with W3C traceparent: propagation, spans as JSON lines, critical path: the critical path is where fan-out tails show up",
        "distributed-systems L400 #19 Multi-region design: latency budget, leader placement, follower reads, failover RTO/RPO: latency budgets are sums of these terms",
    ],
    "next": "L500 #26 Ethics: reliability as a professional duty - outages, blameless post-mortems, data residency and energy - who is harmed when these numbers are wrong",
    "platforms": PLATFORMS,
}

for _l in (LESSON_23, LESSON_24, LESSON_25):
    _l["validation"] = {
        "status": "validated-local",
        "how": f"Ran every theorem check command, `python -m unittest -v` in labs/L500/{_l['number']}-*, and `python research/l500_checks.py` on Python 3.12 (Linux); all checks are seeded and printed identical output on repeated runs; every calculation answer in the problem set is recomputed by research/l500_checks.py.",
        "pendingCi": ["macOS and Windows runs (CI matrix job python-labs-l500)"],
    }
