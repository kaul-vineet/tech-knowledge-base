# Distributed Systems (applied) — concepts primer

## What it is for
A distributed system is several programs (nodes) that cooperate only by sending messages over a network. You build one whenever a single process is not enough:

- **Service-to-service calls** — checkout calls a payment service over HTTP or gRPC.
- **Resilient traffic routing** — proxies such as Envoy retry, time out and load-balance calls.
- **Container platforms** — Docker Compose and Kubernetes start, health-check and restart many processes.
- **Replicated and collaborative data** — Automerge and Apache Cassandra order updates from many replicas.

## One mental model: unreliable letters between offices
Each node is an office with its own clock, connected only by couriers. A courier can be slow, lost, or deliver twice, and the sender never knows which. Everything here is a tactic for that one fact.

```
 Node A (own clock)      network: may delay / drop / duplicate       Node B (own clock)
 timeout, retry+jitter ── request ──────────────────────────────▶ dedupe store
 idempotency key       ◀─────────────────────────────── response ── Lamport clock
                        (no reply ≠ "didn't happen")
```
- No reply within a **timeout** → outcome unknown.
- Unknown outcome → **retry**, spaced with **backoff + jitter**, limited by a **budget**.
- Retries may duplicate → the receiver **deduplicates** with an **idempotency key**.
- Clocks disagree → order events with **logical clocks**, not wall time.

## Concept map
| Level | Core concepts | Local agent (proposal; code judges) |
|---|---|---|
| **L100 — run it** | Nodes as processes; request/response and latency; timeouts; retries with backoff, jitter and a budget; idempotency keys; Lamport clocks. | Summarizes a retry log; code recomputes p50/p99 (lab 4). |
| **L200 — build it** | Leases, fencing tokens; at-least-once messaging (ack, visibility timeout, DLQ); consistent hashing; cache invalidation; rate limiting (429, Retry-After). | Proposes a replica layout; code decides (lab 9). |
| **L300 — harden it** | Raft replicated log; partitions, fault injection, linearizability checks; sagas; tracing; load shedding. | Explains a partition history; the checker judges each claim (lab 13). |
| **L400 — design and prove it** | Consistency per use case (quorums, PACELC); CRDTs; multi-region RTO/RPO; chaos experiments; model and linearizability checking; capstone pipeline. | Explains chaos results; code checks each claim and decides (capstone). |
| **L500 — theory and rigour** | System models; Lamport/vector clocks (proofs); safety vs liveness; two generals, FLP, CAP, quorum intersection, Paxos vs Raft; M/M/1, Little's law, tail amplification, Amdahl/USL; ethics of reliability; Lamport 1978 and Raft 2014. | None in the labs; a local model may explain a proof, but every claim is checked by the seeded check scripts (proposal). |

## Glossary
| Term | Meaning |
|---|---|
| node | One independently running process; shares only the network. |
| latency | Time from sending a request to receiving the full response. |
| timeout / deadline | Maximum wait as a duration / as a point in time. |
| backoff + jitter | Waiting longer between retries, randomised so clients don't retry in lock-step. |
| retry budget | Limit on retries relative to normal traffic. |
| idempotency key | Client-generated ID for one logical operation, reused on every retry. |
| clock skew | Difference between two nodes' wall clocks at the same instant. |
| Lamport timestamp | Per-node counter: tick per event, carried on messages, max(local, received)+1 on receive. |

## Common misconceptions
1. **"No response means it failed."** It means *unknown*: the server may have done the work and lost the reply — hence idempotency keys.
2. **"Retries make things more reliable."** Only for transient faults; against an overloaded service, unbounded retries multiply load (3 attempts at each of 5 layers = 243 calls at the bottom).
3. **"Timestamps tell me what happened first."** Only on one machine. Across nodes, skewed clocks can put an effect before its cause.

## Sources
Kleppmann, *Distributed Systems* notes (Cambridge 2025/26) — https://www.cl.cam.ac.uk/teaching/2526/ConcDisSys/dist-sys-notes.pdf · Amazon Builders' Library, *Timeouts, retries, and backoff with jitter* — https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/ · per-lesson sources: `content/L100.json`, `content/L200.json`.
