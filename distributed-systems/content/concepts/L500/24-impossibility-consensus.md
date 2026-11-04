## Why it matters
"CAP says we can't", "FLP proves consensus is impossible", "just use a quorum": these slogans appear in design reviews and are usually half right. Foundations II states each result exactly as its authors proved it, so you can tell when a slogan applies. It then proves the one positive result every replicated system relies on: majority quorums intersect, and Paxos's phase 1 carries any value that might already be chosen into the next proposal.

## Definitions
- **Consensus** requires three things. *Agreement*: no two correct processes decide differently. *Validity*: the decision was some process's input. *Termination*: every correct process eventually decides. Agreement and validity are safety; termination is liveness (lesson 23).
- **Valency** (FLP): a configuration is **bivalent** if both decisions are still reachable from it. It is 0-valent or 1-valent if only one is.
- **Atomic register** (Gilbert & Lynch's C): every operation appears to happen at one instant between its call and its return. In particular, a read that starts after a write completes sees that write or a later one.
- **Availability** (their A): every request to a non-failing node eventually gets a response, with no time bound.
- **Partition tolerance** (their P): the network may lose any number of messages.
- **Quorum**: a set of replicas whose replies an operation needs. A **ballot** is a unique, ordered proposal number; Raft calls it a term.

## Key results
1. **Two generals (T24.1).** Over a lossy channel no protocol guarantees coordinated action. Proof: take the shortest prefix of the loss-free run in which someone acts. The sender of its last delivered message cannot tell whether that message arrived. So it acts as in the shorter run, where nobody acts, and the two generals disagree.
2. **FLP (T24.2).** In the asynchronous model, every deterministic consensus protocol that tolerates one crash has a run that never decides. The proof has two steps. Some initial configuration is bivalent (Lemma 2). From any bivalent configuration the adversary can deliver the next pending message and stay bivalent (Lemma 3). The result is an infinite fair run with no decision.
3. **CAP (T24.3).** In the asynchronous model no read/write object guarantees both availability and atomicity in all fair executions where messages may be lost. Corollary 1.1: the same holds even if atomicity is required only when no message is lost, because asynchrony hides the loss. Proof: partition the nodes into G1 | G2, write at G1, then read at G2. G2 cannot tell this run from one with no write, so the read returns the old value.
4. **Quorum lemma + Paxos (T24.4).** If R + W > N, any read quorum meets any write quorum, by pigeonhole. Any two majorities meet. If (m, v) is chosen by a majority C, every later proposer's promise set S meets C. The shared acceptor accepted (m, v) before promising, so it reports a proposal numbered at least m. The proposer adopts the highest one reported, which by induction has value v. So no second value can ever be chosen.

## Intuition
All three impossibility proofs use the same move: **indistinguishability**. Build two executions that look identical to some node but require different answers. Then any deterministic node is wrong in one of them.

The escape routes therefore change what a node can know or what it must do:
- timing assumptions, so a timeout carries information (partial synchrony);
- randomness, so the adversary cannot predict the next choice;
- weaker requirements: eventual consistency, compensation instead of atomic action, or "good enough" answers.

Paxos and Raft keep every safety property in every execution. They give up only guaranteed termination, which returns once the network behaves.

Raft and Paxos protect the same thing in different places:
- Paxos lets anyone propose, but forces the proposer to *adopt* any possibly-chosen value it learns in phase 1.
- Raft restricts *who may lead*: a voter refuses a candidate with a less up-to-date log. So the leader already holds every committed entry and never needs to adopt anything.

Both arguments rest on one acceptor (Paxos) or one voter (Raft) that sits in both majorities.

## Worked example
**Quorum sizing (24-P1).** N = 7 and R = 3. Read-write overlap needs W ≥ 5; write-write overlap needs W ≥ 4. So W = 5, and every read meets every write in at least 3 + 5 - 7 = 1 replica.

**Phase 1 (24-P6).** A1 has accepted (2, x), A2 has accepted (3, y), and A3 nothing. A proposer with ballot 5 that hears from {A1, A3} must propose x. One that hears from {A2, A3} must propose y. Neither value is chosen yet; phase 1 protects only values that *might* have been chosen.

**The checks** (`consensus_proofs.py`):
- All 21,343 read/write quorum pairs for N ≤ 7 intersect when R + W > N. Every configuration with R + W ≤ N (56 of 56) has a disjoint pair.
- 3,000 random Paxos runs with 15% loss, 10% duplication and reordering all decided, never on two values, with 0 violations of P2b.
- The broken variant, which ignores phase-1 values, chose two values in 2,296 of 3,000 runs.
- Under an adversarial schedule, two duelling proposers ran 1,000 rounds with 2,000 ballots and 0 acceptances: safe and never live. A random backoff (a timing assumption) ended every duel, after 4.35 attempts on average.
- Gilbert & Lynch's execution: both "always answer" designs returned v0 after the write of v1 completed. The majority design stayed atomic but answered neither request.

## Common misconceptions
- **"Pick any two of C, A and P."** You cannot opt out of partitions. With no partition you can have both C and A. The real choice is what each operation does *during* message loss, and PACELC adds the latency cost when there is none (lab 17).
- **"CAP consistency is ACID consistency."** It is linearizability of a single object (Gilbert & Lynch, footnote 3).
- **"FLP means consensus never works."** It means *guaranteed termination* is impossible for *deterministic* protocols in a *fully asynchronous* model. Production systems drop one of those three assumptions.
- **"A majority of replicas holding an entry means it is committed."** Not in Raft if the entry is from an older term (Figure 8). It can still be overwritten.
- **"Even cluster sizes add tolerance."** Six nodes tolerate 2 crashes, the same as five, and need more acknowledgements.
- **"Two generals is solved by more acknowledgements."** Every extra acknowledgement just moves the uncertainty to the other side. Practice avoids the problem with idempotency and compensation (labs 5 and 14).

## Further reading
FLP 1985; Gilbert & Lynch 2002 and their 2012 *Perspectives*; Lamport, *Paxos Made Simple* (2001); Ongaro & Ousterhout 2014 §5.4 (lesson 27 seminar).
