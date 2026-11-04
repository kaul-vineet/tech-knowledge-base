## Why it matters
Every lab so far quietly assumed something about time and failure. Lab 3 chose a timeout from a percentile, as if delays had a bound. Lab 6 sorted events by Lamport time, as if that order meant something. Lab 7 trusted a lease to expire before a new leader acted. Foundations I makes those assumptions explicit, proves what the mechanisms guarantee, and checks each proof in code. The payoff is practical: when a design review says "this is safe", you can ask "in which model?"

## Definitions
A **system model** has three parts (Kleppmann's notes, §2.3).
- **Network**: reliable, fair-loss (a message retried often enough eventually arrives) or arbitrary (an adversary may tamper, which TLS reduces to fair-loss).
- **Nodes**: *crash-stop* (a crashed node never returns), *crash-recovery* (it returns with only what it wrote to stable storage) or *Byzantine* (it may deviate arbitrarily, even maliciously).
- **Timing**, after Dwork, Lynch and Stockmeyer (1988). In a *synchronous* system there are known bounds Δ on message delay and Φ on relative speed. In an *asynchronous* system there are none. In a *partially synchronous* system the bounds exist but are unknown, or hold only after an unknown Global Stabilisation Time (GST).

**Happened-before** (Lamport 1978) is the smallest relation with three rules:
1. a precedes b in one process;
2. a sends a message that b receives;
3. transitivity.

Two events are **concurrent** when neither happened before the other. A **property** is a set of executions. **Safety** says nothing bad ever happens; **liveness** says something good eventually happens (Alpern & Schneider 1985).

## Key results
- **T23.1 Clock condition.** Rule IR1: tick between events. Rule IR2: on receive, jump above the message's timestamp. Together they give a → b ⇒ C(a) < C(b). The proof is one line once you see the trick: → is the *smallest* relation closed under rules 1-3, and "C(a) < C(b)" is closed under all three. Sorting by (C, process id) is then a total order that extends →. The converse is false.
- **T23.2 Vector clocks.** Component k of V(e) counts the events of process k in e's causal past. The element-wise max on receive is a union of prefixes, so a → b ⇔ V(a) < V(b), and concurrency ⇔ incomparable vectors.
- **T23.3 Safety/liveness.** Every safety violation has a finite witness that no future can repair. No finite prefix ever violates liveness. Every property is the intersection of one of each.
- **T23.4 Failure detection.** With bounds, a timeout of 2Δ + π is perfect. Without bounds, a slow peer is indistinguishable from a crashed one, so every timeout is fallible. With partial synchrony, a timeout that grows after each mistake is eventually right.

## Intuition
Logical clocks are a *coordinate system*, not a stopwatch. Lamport's tick lines can be bent any way that keeps every message crossing one; many total orders fit the same execution. Only → is determined by the execution. Vector clocks pay n integers per message to keep the extra knowledge "these two are concurrent". CRDTs and conflict detection (lab 18) need exactly that knowledge.

Safety and liveness are proved differently. Safety needs an **invariant**: show that no step can break it. Liveness needs **progress**, and in distributed systems progress needs a fairness or timing assumption. This is why Raft is "always safe, live when the network behaves": its safety is a set of invariants, and its liveness rests on randomized timeouts.

## Worked example
Three processes; the problem set's scenario (23-P1). P1 does a, sends m1 (b), then c. P2 does d, receives m1 (e), sends m2 (f). P3 does g, h, then receives m2 (i).

| event | Lamport | vector |
|---|---|---|
| c | 3 | (3,0,0) |
| e | max(1,2)+1 = 3 | (2,2,0) |
| i | max(2,4)+1 = 5 | (2,3,3) |

L(c) = 3 < L(i) = 5, yet c and i are **concurrent**. The vectors disagree in both directions (3 > 2 and 0 < 3). Sorting log lines by Lamport time would put c first, which looks causal but is an accident of the counter values.

The code check (`clocks_proofs.py clock`) generated 300 random executions with 54,600 ordered event pairs. All 13,599 pairs with a → b had L(a) < L(b), and none was ordered the wrong way by (L, pid). But 11,063 of the 27,402 concurrent pairs also had L(a) < L(b): that is the converse failing. Dropping the max on receive produced 990 violations. Vector clocks matched → on every pair, and the broken version mismatched 4,546.

For failure detection, Pareto round trips (no upper bound) gave false-suspicion rates of 8.98% at 5 ms down to 0.0025% at 1 s, close to the theoretical T^-1.5 and never zero. Bounded delays with a 105 ms timeout gave exactly 0.

## Common misconceptions
- **"Lamport timestamps tell me which event came first."** Only when the events are causally related. For concurrent events the order is arbitrary but consistent.
- **"A longer timeout makes failure detection correct."** It makes it *less wrong* in an asynchronous network, never correct. Safety must not depend on it (fencing tokens, lab 7).
- **"Synchronous means blocking."** In system models it means bounded delay. Kleppmann warns that the RPC sense of the word is different.
- **"A bounded response time is a liveness property."** "Respond within 200 ms" is *safety*: a late response is a bad thing at a known instant. "Eventually respond" is liveness.
- **"Crash-recovery is the same as crash-stop plus a restart."** Only if the node persists what it promised. A vote kept in memory and forgotten after a restart elects two leaders in one term (23-P8; Raft persists `currentTerm` and `votedFor` before replying).
- **"Byzantine faults are just bugs."** A bug in software that every node runs is a *common-mode* fault. BFT protocols that assume fewer than one third of nodes are faulty cannot tolerate it (Kleppmann §2.3).

## Further reading
Lamport 1978 (lesson 27 seminar), Kleppmann's notes §§2-3 (CC BY-SA), Alpern & Schneider 1985, Dwork, Lynch & Stockmeyer 1988.
