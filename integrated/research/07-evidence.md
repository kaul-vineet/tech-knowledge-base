# L600 #07 — evidence: a reliable quantum-job service on unreliable backends

Checked 2026-10-30. Every number in the lesson and question bank is recomputed by `research/checks_07.py` (exit 0).

## Research questions
1. What must a service do when a lease expires while the holder is still working (duplicate execution)?
2. What are the published rules for idempotency keys (replay vs conflict)?
3. Which OpenQASM syntax variants describe the same circuit (qubit vs qreg, physical qubits), and is circuit equivalence
   preserved under qubit relabelling?
4. How is readout error mitigated, and what does it cost in variance?
5. Which interval should carry the uncertainty of a shot-based probability?
6. Do real providers publish calibration data with timestamps (so a cache can key on a version)?
7. Queue-based load levelling, bulkhead and circuit breaker: what do the primary pattern descriptions say?

## Sources kept (primary: specs, papers, official docs, maintained OSS)
| Source | Used for | What was verified |
|---|---|---|
| Gray & Cheriton, "Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency", SOSP 1989, https://www.cs.cmu.edu/~15712/papers//gray89.pdf (ACM: https://dlnext.acm.org/doi/pdf/10.1145/74851.74870) | leases | A lease is "a contract that gives its holder specified rights over property for a limited period of time"; non-Byzantine failures affect performance, not correctness, with short leases. |
| Kleppmann, "How to do distributed locking" (2016), https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html | fencing tokens | A fencing token is a number that increases every time a client acquires the lock; the storage server rejects a write whose token is lower than one it already processed; a paused holder can act after lease expiry. Author's essay that cites peer-reviewed work (kept as the clearest statement; the idea is also in the DS L200 #7 lab). |
| IETF draft-ietf-httpapi-idempotency-key-header-08 (22 Oct 2026), https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ | intake | Key reused with a different payload -> 422; retried while the original is still processing -> 409; optional fingerprint from the payload. Work in progress (Internet-Draft). |
| OpenQASM live specification, Types and Casting, https://openqasm.com/language/types.html | canonicalisation | `qubit[size] name;` declares a register; `qreg` kept for backwards compatibility; physical qubits `$n`; "Circuit equivalence does not hold over permutations of physical qubit labels". |
| Bravyi, Sheldon, Kandala, McKay, Gambetta, "Mitigating measurement errors in multi-qubit experiments", PRA 103, 042605 (2021), arXiv:2006.14044, https://arxiv.org/abs/2006.14044 | mitigation | Mitigation applies the inverse noise matrix to the measured probability vector; overhead grows exponentially in eps x n. |
| Brown, Cai, DasGupta, "Interval Estimation for a Binomial Proportion", Statistical Science 16(2) 2001, https://projecteuclid.org/journals/statistical-science/volume-16/issue-2/Interval-Estimation-for-a-Binomial-Proportion/10.1214/ss/1009213286.pdf | error bars | Wald interval coverage is erratic and poor; recommend Wilson / Jeffreys for small n. Our measurement agrees (see below). |
| qiskit-ibm-runtime `BackendProperties` API reference, https://eu-de.quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/models-backend-properties | calibration versioning | Backend properties carry `last_update_date` and per-qubit readout error, T1, T2 — a provider-side calibration timestamp a cache key can include. |
| IBM Quantum tutorial "Refresh backend properties with real-time benchmarking", https://quantum.cloud.ibm.com/docs/tutorials/refresh-backend-properties-with-real-time-benchmarking | drift | Reported properties can lag behind current device behaviour; transpiler and error mitigation rely on them. |
| Azure Architecture Center, Queue-Based Load Leveling, https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling | queue | Queue as a buffer; most queues deliver at least once, so consumers must be idempotent; producer rate above consumer rate grows the queue. Vendor docs used only for the vendor-neutral pattern text. |
| Azure Architecture Center, Bulkhead, https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead | bulkhead | Isolate elements into pools so a failing one does not exhaust shared resources; combine with retry and circuit breaker. |
| Nygard, "Documenting Architecture Decisions" (2011), https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions | ADR format | Title, Status, Context, Decision, Consequences (same source as the application-architecture topic). |

Dropped: vendor job-queue product pages (marketing), blog posts restating fencing without primary references, and
Qiskit Runtime pricing pages (not needed; no prices are modelled).

## What was verified locally and how
- `python run_project.py` -> 5/5 milestones, 4/4 seams, 3/3 fitness, exit 0. `--inject lease-expiry|stale-cache|text-key`
  -> exit 1 with the expected failing lines (README).
- `python -m unittest discover -s tests -v` -> 35 tests OK, run 3 times with identical results (fake clock, seeded).
- Build task: an unmodified copy of `ledger.py` as `my_ledger.py` fails 3 of 4 build-task tests; a copy of the solution
  passes 4/4 (`BUILD_TARGET=mine`).
- Wald vs Wilson (executed jobs only, every outcome including unobserved ones, 95% intervals): Wald covers 0.8216 of
  outcomes whose exact probability is below 0.01 (342 outcomes) and Wilson 0.9561; the service's contract metric over
  reported outcomes is 0.9362. Recomputed in `checks_07.py`.
- Canonicalisation keeps the unitary for every workload variant (statevector simulator).

## Not verified / pending CI
- Qiskit Aer `NoiseModel` backend behind the same `Backend` interface (not built; Qiskit not installed here).
- macOS and Windows runs (lab code uses pathlib, utf-8, no POSIX-only calls; expected to pass).
- Learning tools exercises (manual).
