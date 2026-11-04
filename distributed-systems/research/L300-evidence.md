# L300 research evidence — Distributed Systems (applied)

Method: SPEC.md research method (unchanged). All sources fetched 2026-10-28 with web_fetch / web_search. Score = implementable / current / authoritative / open / transferable / depth (0-2 each); keep ≥ 8/12. Worked-example numbers in the concept notes come from `python research/concept_examples_l300.py` (runs the labs; lesson 15's times vary by run). Learning-tool facts (versions, licences, installs) come from `../../shared/LEARNING-TOOLS-CATALOG.md`.

---

## Lesson 12 — Replicated log with Raft (simplified)
**Questions**
1. Exactly which rule stops a stale follower from becoming leader, and how is "more up-to-date" defined?
2. What is the commit rule, and why may a leader not commit older-term entries by counting replicas?
3. What does a production library leave to the user (storage, transport), so a lab can model those as plumbing?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Ongaro & Ousterhout, Raft extended paper (raft.github.io/raft.pdf) | kept (primary) | 12 | Figure 2 receiver rules, 5.4.1 election restriction, 5.4.2 commit rule, Figure 8 |
| etcd-io/raft README | kept | 11 | Only the algorithm; network and disk left to the user; deterministic state machine; users etcd, Kubernetes, CockroachDB, TiDB; PreVote/CheckQuorum tests |
| Maelstrom doc 06-raft | kept (supporting) | 9 | Raft chapter → linearizable KV; learning-tool exercise |
| RaftScope / Secret Lives of Data | dropped | — | Unmaintained (already listed as "not recommended" in LEARNING-TOOLS.md) |

**Key facts**
- RequestVote receiver: "If votedFor is null or candidateId, and candidate's log is at least as up-to-date as receiver's log, grant vote." — Raft paper, Figure 2
- "the voter denies its vote if its own log is more up-to-date than that of the candidate … If the logs have last entries with different terms, then the log with the later term is more up-to-date. If the logs end with the same term, then whichever log is longer is more up-to-date." — Raft paper 5.4.1
- Without it: "a follower might be unavailable while the leader commits several log entries, then it could be elected leader and overwrite these entries" — Raft paper 5.4 (the lab's failure lab)
- Leader commit: N > commitIndex, a majority of matchIndex ≥ N, and log[N].term == currentTerm; "Raft never commits log entries from previous terms by counting replicas." — Raft paper Figure 2, 5.4.2
- AppendEntries: reject if no entry at prevLogIndex with prevLogTerm; delete a conflicting entry and all that follow; commitIndex = min(leaderCommit, index of last new entry). — Raft paper Figure 2
- Randomized election timeouts (e.g. 150–300 ms) make split votes rare and resolve them. — Raft paper 5.2
- etcd raft "only implements the Raft algorithm; both network and disk IO are left to the user"; "the library models Raft as a state machine". — etcd-io/raft README

## Lesson 13 — Network partitions and fault injection
**Questions**
1. Which fault types does Toxiproxy offer and how is "down" expressed (so the lab's proxy uses the same vocabulary)?
2. What does a linearizability checker take as input, and what is a minimal correct register history example?
3. How do Jepsen-style tools apply partitions to toy systems?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Toxiproxy README (2.13.0) | kept (primary) | 11 | Toxics latency/down/bandwidth/slow_close/timeout/reset_peer/slicer/limit_data/packet_loss; down = enabled false; toxicity; API :8474 unauthenticated unless TOXIPROXY_AUTH_TOKEN; CLI syntax |
| Porcupine README | kept | 10 | Model + history → linearizable?; register examples (used as test cases); faster than Knossos; used by etcd robustness tests |
| Maelstrom workloads.md (lin-kv) | kept | 10 | lin-kv = linearizable KV workload (read/write/cas) |
| Kleppmann, How to do distributed locking (2016) | kept (background, already in L200) | 10 | Fencing tokens at the storage |
| Knossos repo | not fetched | — | Porcupine README describes the relationship; Maelstrom wraps the checker |

**Key facts**
- "down — Bringing a service down is not technically a toxic … done by POSTing to /proxies/{proxy} and setting the enabled field to false." — Toxiproxy README
- Toxic field "toxicity: probability of the toxic being applied to a link (defaults to 1.0, 100%)"; toxics are directional (upstream/downstream). — Toxiproxy README
- "Toxiproxy listens for HTTP on port 8474. The API is unauthenticated by default … To require a token, start the server with TOXIPROXY_AUTH_TOKEN set". — Toxiproxy README
- Porcupine "takes a sequential specification as executable Go code, along with a concurrent history, and it determines whether the history is linearizable"; register example histories (put 100 / get 100 / get 0 = linearizable; put 200 / get 200 then get 0 = not). — Porcupine README
- "Lin-kv: A workload for a linearizable key-value store" with read, write, cas. — Maelstrom workloads.md
- etcd's raft library offers linearizable read-only queries where the "leader checks with quorum", and lease-based reads that rely on "the clock of all the machines" — etcd-io/raft README (used for the stale-read discussion)

## Lesson 14 — Sagas with compensation
**Questions**
1. What exactly does a saga guarantee, and in which order are compensations run?
2. Orchestration vs choreography: definitions and drawbacks (isolation)?
3. How does recovery work after a crash (saga log, backward vs forward recovery)?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Garcia-Molina & Salem, Sagas (1987, Cornell course copy) | kept (primary) | 10 | T1..Tn / C1..Cn guarantee, semantic compensation, saga execution component with a log, backward/forward recovery, compensations hard to write for irreversible actions |
| microservices.io Pattern: Saga | kept (background) | 8 | Choreography vs orchestration definitions; lack of isolation, countermeasures; outbox needed. Page contains a course advert → background only |
| Temporal docs page (detecting workflow failures) | dropped | 5 | Fetched page did not cover sagas/compensation |

**Key facts**
- "Either the sequence T1, T2, … Tn … or the sequence T1, T2, … Tj, Cj, … C2, C1 … will be executed"; a compensating transaction "undoes, from a semantic point of view, any of the actions performed by Ti, but does not necessarily return the database to the state that existed". — Sagas paper, section 1
- Backward recovery: the saga execution component logs each command and, on abort, "consults the log and orders the execution of compensating transactions C2 and C1". — Sagas paper, section 4
- "Choreography - each local transaction publishes domain events that trigger local transactions in other services. Orchestration - an orchestrator (object) tells the participants what local transactions to execute." Drawbacks: "Lack of automatic rollback … Lack of isolation". — microservices.io

## Lesson 15 — Distributed tracing
**Questions**
1. Exact traceparent format and validation rules; what must a service do with an invalid header?
2. How does OpenTelemetry Python inject/extract the same header (for the pending-ci cross-check), and which versions are current?
3. Where does Jaeger receive OTLP and show traces?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| W3C Trace Context Recommendation (2021-11-23) | kept (primary) | 12 | Header ABNF, all-zero ids invalid, processing model (restart on invalid), privacy section |
| OpenTelemetry Python: Propagation | kept | 10 | TraceContextTextMapPropagator inject/extract; instrumentation libraries propagate for you |
| PyPI opentelemetry-sdk / -api / -exporter-otlp-proto-http | kept (version pins) | 10 | 1.45.1 released 2026-10-06, Python ≥ 3.10, Apache-2.0 |
| OpenTelemetry Python source: in_memory_span_exporter.py (via search) | kept (supporting) | 9 | InMemorySpanExporter module path and get_finished_spans() |
| Jaeger Getting Started | kept (from L100 tools pass) | 10 | UI :16686, OTLP :4318 |

**Key facts**
- `traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01`; trace-id = 32 lowercase hex, parent-id = 16 lowercase hex, "All zeroes forbidden"; "Vendors MUST ignore the traceparent when the parent-id is invalid (for example, if it contains non-lowercase hex characters)." — W3C Trace Context 3.2
- "If either trace-id, parent-id or trace-flags are invalid, the vendor creates a new traceparent header and deletes tracestate." — W3C 4.3
- "Update parent-id: The value of property parent-id MUST be set to a value representing the ID of the current operation." — W3C 4.3
- "Tracing vendors MUST NOT use traceparent and tracestate fields for any personally identifiable or otherwise sensitive information." — W3C 6
- `TraceContextTextMapPropagator().inject(headers, ctx)` / `.extract(carrier=...)`. — OpenTelemetry Python Propagation page
- opentelemetry-sdk 1.45.1, released Oct 6, 2026, Requires Python >= 3.10. — PyPI

## Lesson 16 — Backpressure and load shedding
**Questions**
1. What do production systems do under overload (reject early, client-side throttling, criticality)?
2. How do adaptive concurrency limits work (Little's law, AIMD)?
3. Which load model shows overload honestly (open vs closed), and how does k6 express it?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Google SRE book, Handling Overload | kept (primary) | 11 | Client-side adaptive throttling (requests vs K × accepts), criticality, keep serving provisioned rate under 2x-10x overload, retry budgets |
| Netflix concurrency-limits README | kept | 10 | Little's law (Limit = RPS × latency), TCP congestion-control analogy, Vegas/Gradient2, AIMD on clients, 429 / UNAVAILABLE |
| RFC 9110 (503, Retry-After) | kept (already in L200) | 11 | Retry-After semantics |
| Grafana k6: constant-arrival-rate | kept (already in L200 tools pass) | 10 | Open-model executor, options rate/timeUnit/duration/preAllocatedVUs/maxVUs |

**Key facts**
- "a backend task provisioned to serve a certain traffic rate should continue to serve traffic at that rate without any significant impact on latency, regardless of how much excess traffic is thrown at the task … up to a certain rate of traffic—somewhere above 2x or even 10x". — Google SRE book
- Clients "can continue to issue requests to the backend until requests is K times as large as accepts. Once that cutoff is reached, the client begins to self-regulate". — Google SRE book
- "This relationship is covered very nicely with Little's Law where Limit = Average RPS * Average Latency"; "we borrow from common TCP congestion control algorithms by equating a system's concurrency limit to a TCP congestion window". — Netflix concurrency-limits README
- constant-arrival-rate "is an open-model executor, meaning iterations start independently of system response". — k6 docs

## Validation notes
- Every lab ran locally (Python 3.12.15, Linux). Fail-before / pass-after proven for every build task with `BUILD_TARGET=mine` (lesson file) vs default (solution).
- Not run: OpenTelemetry cross-check (no PyPI access), k6, Toxiproxy, Maelstrom, Jaeger, Grafana, a real local model. See KNOWN-GAPS.

## Update pass (2026-10-28, UPDATE-L300-SPEC)
- R3-12: W3C Trace Context says a component SHOULD respect the received sampled flag and propagate it unchanged if it did not make its own decision (§3.2.2.5.1), and that a parser seeing a higher version parses the first four fields (§3.2.4; version `ff` invalid; version 00 has no extra fields). `tracing.py` now does both; `test_sampled_flag_is_propagated_unchanged` (flags 00 and 01 reach payments unchanged) and `test_versions_w3c_3_2_4` prove it. The old code always sent `01` — the same test with flags 00 fails against it.
- Lamport rules re-checked in the primary source (author's PDF): IR1 "Each process P_i increments C_i between any two successive events"; IR2(b) "Upon receiving a message m, process P_j sets C_j greater than or equal to its present value and greater than T_m"; ties broken by "any arbitrary total ordering of the processes". Replaces Wikipedia (R3-13).
- k6 web dashboard (docs page): `K6_WEB_DASHBOARD=true`, default 127.0.0.1:5665, `K6_WEB_DASHBOARD_EXPORT=<file>`; "The report only includes graphs if the test duration is greater than three times the aggregation period value", default period 10s — hence `K6_WEB_DASHBOARD_PERIOD=2s` for the 10 s `load_test.js`.
- Temporal: CLI README (MIT) — `brew install temporal`, Windows amd64 archive, dev server UI on :8233; PyPI temporalio 1.34.0 (licence not in the fetched text).

