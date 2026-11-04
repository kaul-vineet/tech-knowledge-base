## Why read primary papers
Lab 6 implemented Lamport's clock rules and lab 12 implemented Raft. Both labs simplified the original. Reading the papers shows what was simplified and why the authors made their choices. It also shows what each paper *proves* and what it only *claims*. This seminar summarises; it does not reproduce. Read the papers at their URLs.

## How to read a systems paper (four passes)
1. **Problem and model.** What is assumed about timing, faults and channels? Lamport assumes, for his mutual-exclusion algorithm, FIFO channels with no message loss; he notes these assumptions can be removed. Raft assumes crash-recovery with stable storage and no Byzantine faults.
2. **Claims.** List every claim and mark each one *proved*, *measured* or *asserted*.
3. **Argument.** Reconstruct the key proof yourself: Lamport's IR1/IR2 ⇒ clock condition; Raft's Leader Completeness by contradiction.
4. **Evidence and limits.** Test each claim against a lab you ran and against later work (FLP, CAP, lessons 23-24).

## Lamport 1978 in brief
- **Happened-before** is defined only from events inside the system, so it is a *partial* order.
- **Logical clocks** satisfying the Clock Condition need only two rules. Ordering by (time, process) extends them to a total order that the execution itself does not determine.
- **Mutual exclusion** without a central scheduler follows from that total order: each process keeps a request queue and grants itself access when its request is first and everyone has sent it a later message. This generalises to the **state machine approach**, in which every process executes the same commands in the same order.
- **Limits Lamport states himself.** The approach halts if one process fails. Failure "is only meaningful in the context of physical time". **Anomalous behaviour** (a phone call outside the system) requires physical clocks satisfying a *Strong* Clock Condition, with a derived skew bound ε ≈ d(2κτ + ξ).

## Ongaro & Ousterhout 2014 in brief
- **Goal.** Understandability, pursued through decomposition (leader election, log replication, safety) and state-space reduction (no holes in logs; entries flow only from leader to followers).
- **Five guaranteed properties** (Figure 3): Election Safety, Leader Append-Only, Log Matching, Leader Completeness, State Machine Safety.
- **The safety argument** (§5.4.3) rests on one voter that both stored the committed entry and voted for the new leader. The **election restriction** forces that leader's log to be at least as up-to-date. Figure 8 shows why only current-term entries are committed by counting replicas.
- **Timing.** broadcastTime ≪ electionTimeout ≪ MTBF affects only availability.
- **Evidence for understandability.** A user study of 43 students; 33 answered Raft questions better than Paxos questions. That is an empirical claim, with the strengths and limits of any user study.

## Seminar plan (90 minutes)
- 10 min: map each paper's model onto lesson 23's vocabulary.
- 25 min each: guiding questions in pairs, then whole-group reconstruction of the key proof.
- 20 min: lab evidence. Lab 6 skew vs Lamport order. Lab 12 with the election restriction removed (3 safety violations, committed x=1 and x=2 lost).
- 10 min: choose a response prompt.

## Worked example
Lamport's skew bound for diameter d = 3, drift κ = 10⁻⁶, a message every τ = 1 s and unpredictable delay ξ = 1 ms: ε ≈ 3(2·10⁻⁶·1 + 0.001) s = **3.006 ms**. The delay term dominates, not the drift (problem 27-P4).

## Common misconceptions
- **"Lamport's paper is about timestamps."** It is about the partial order. Timestamps are one way to extend it, and its most cited idea is the state machine.
- **"Raft is a different consensus problem from Paxos."** The paper says Raft produces a result equivalent to (multi-)Paxos and is as efficient. The difference is structure.
- **"Understandable means easy."** Subtle rules still carry the safety argument. Lab 12 failed when one line of RequestVote, the election restriction, was removed. Figure 8 is a second rule of the same kind.
