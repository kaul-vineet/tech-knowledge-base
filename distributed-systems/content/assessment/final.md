# Final exam (exam week) - 3 hours, 100 marks

Covers L100-L500 (lessons 1-27). Open notes (course material only, no network); calculator allowed. Numerical answers are recomputed in `research/l500_checks.py` (EXAMS section).

---

### Q1 - Derivation: capacity (15 marks)
An instance serves requests as an M/M/1 queue with mu = 200 requests/s. Offered load is 160 requests/s.
(a) Compute rho, the mean time in system W and the mean number in system L; verify with Little's law. (6)
(b) You add a second instance and split the load evenly. Compute the new W. (4)
(c) Explain why the improvement is far larger than "twice the capacity" suggests. (5)

**Model answer.** (a) rho = 0.8; W = 1/(200 - 160) s = 25 ms; L = rho/(1 - rho) = 4; check lambda W = 160 x 0.025 = 4. [2 + 2 + 2] (b) Each instance gets 80/s: W = 1/(200 - 80) s = 8.33 ms. [4] (c) W = (1/mu)/(1 - rho): at rho = 0.8 queueing multiplies service time by 5, at 0.4 by 1.67; delay is convex in utilisation, so the last 40% of load costs most of the delay (T25.1; lab 16). [5]

### Q2 - Derivation: tail latency (12 marks)
A search request fans out to 40 shards; each shard exceeds 100 ms with probability 0.5%, independently.
(a) What fraction of requests exceed 100 ms? (4)
(b) What per-shard exceedance probability keeps the request-level rate at 1%? Which shard percentile does that correspond to? (5)
(c) Name one technique from Dean & Barroso and say whether it reduces p or n. (3)

**Model answer.** (a) 1 - 0.995^40 = 18.2%. [4] (b) p <= 1 - 0.99^(1/40) = 0.000251, i.e. the shard's p99.975 must be under 100 ms. [5] (c) Hedged requests (reduce the effective p by racing a second replica), tied requests (p), micro-partitioning / selective replication (p), "good enough" results (n). [3]

### Q3 - Proof: Paxos safety (15 marks)
State invariant P2c of single-decree Paxos and prove that, together with P1a, it guarantees that at most one value is chosen. State where you use quorum intersection and where you use stable storage.

**Model answer.** P2c (Lamport 2001): if (n, v) is issued, some majority S has either accepted nothing below n, or v is the value of the highest-numbered proposal below n accepted in S. Proof as T24.4(b): induction on n > m for a chosen (m, v) by majority C; S ∩ C non-empty (quorum intersection) [4]; that acceptor accepted (m, v) before promising n, else P1a forbids it [3]; so the highest reported proposal is numbered in [m, n-1] and has value v by induction [4]; hence P2b and a unique chosen value [2]. Stable storage: acceptors must remember promises and acceptances across restarts, otherwise a recovered acceptor can break P1a [2].

### Q4 - Explanation: CAP and PACELC (10 marks)
State the CAP theorem as Gilbert and Lynch proved it, and explain with numbers from lab 17 why PACELC is the more useful design question for a single-region store.

**Model answer.** No read/write object in the asynchronous model can guarantee both availability (every request to a non-failing node eventually answers) and atomic consistency in all fair executions where messages may be lost [5]. With no partition you can have both; the everyday trade is latency vs consistency: lab 17 measured p99 65.9 ms for R = 2, W = 2 versus 124.5 ms with read write-back (linearizable), and 16.74% stale reads at R = 1, W = 1 [5].

### Q5 - Design critique: multi-region and ethics (15 marks)
A healthcare booking service in an EU region replicates asynchronously to a standby region in another jurisdiction and promises "no data loss on failover".
(a) Critique the promise using lab 19's measurement. (5)
(b) Identify the data-protection question the standby raises and the ACM Code principles that apply. (6)
(c) Propose a design and the evidence you would collect before claiming it. (4)

**Model answer.** (a) Asynchronous replication loses acknowledged writes inside the replication lag: lab 19 measured 16 lost acknowledged writes on failover with async, 0 with majority-sync (RTO about 1.3 s) - the promise is false as stated (ACM 1.3 honesty). [5] (b) Copying EU personal (health) data outside the EEA is a transfer under GDPR Chapter V: it needs an adequacy decision or appropriate safeguards with enforceable rights and effective remedies (CJEU C-311/18); Art. 32 also makes availability and timely restoration part of security. ACM 1.2, 1.6, 2.5, 3.7. [6] (c) Majority-sync across two EEA regions plus a witness, or a degraded non-personal fallback; evidence: measured RPO = 0 and RTO under the seeded chaos campaign, a failover game day, and a transfer assessment signed off by the DPO. [4]

### Q6 - Prediction: Raft (10 marks)
A developer removes the up-to-date check from RequestVote "to make elections faster". Predict what lab 12's checker reports and explain with Raft's Leader Completeness argument.

**Model answer.** A stale follower can win an election and overwrite committed entries: lab 12 reported `safety violations: 3` (committed x=1 and x=2 lost) [4]. The proof of Leader Completeness needs a voter that both stored the committed entry and voted for the new leader *and* the restriction that it only votes for logs at least as up-to-date; without the restriction the second half fails [6].

### Q7 - Derivation: scalability (10 marks)
Load tests on 1-48 nodes fit the USL with sigma = 0.04, kappa = 0.001.
(a) Derive the peak p* and the relative capacity there. (6)
(b) The team plans 48 nodes for next year. Advise them. (4)

**Model answer.** (a) dC/dp = 0 where 1 - sigma - kappa p^2 = 0, so p* = sqrt(0.96/0.001) = 31.0; C(31) = 31/(1 + 0.04 x 30 + 0.001 x 31 x 30) = 9.90. [3 + 3] (b) 48 is past the peak: C(48) is lower than C(31), so more nodes give less throughput. Reduce kappa (shard to cut cross-node coherency, avoid broadcast invalidation) or sigma (remove the serial bottleneck) and re-measure before buying hardware. [4]

### Q8 - Short answers: operating responsibly (13 marks)
(a) Give the three elements of a bounded chaos experiment from lesson 20 and why each is an ethical as well as an engineering control. (6)
(b) Rewrite as blameless: "Alex pushed a bad config and took down checkout." Add two action items. (4)
(c) A 99.95% monthly SLO: how many minutes of downtime remain after a 15-minute incident? (3)

**Model answer.** (a) Hypothesis with steady-state metric; small blast radius (cohort, e.g. 10%) with a control group; automatic abort. Each limits harm to people who did not consent to the experiment (ACM 1.2). [2 x 3] (b) "A configuration change passed review and was deployed to all checkout instances at once; validation did not cover the new field." Actions: schema validation in CI (owner: platform); staged rollout with automatic rollback (owner: release). [2 + 2] (c) 21.6 - 15 = 6.6 minutes. [3]
