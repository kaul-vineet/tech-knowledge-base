# Distributed Systems (applied) — L100 "Run it" + L200 "Build it" + L300 "Harden it" + L400 "Design it" + Capstone + L500 "Theory & rigour"

**Status: not yet run on macOS or Windows; CI matrix pending.** Everything below ran on Linux (Python 3.12.15); `validation.pendingCi` in each lesson lists the files or variants that have not run at all.

Start here. This domain teaches the everyday mechanics of services that talk over a network: calling another service, putting timeouts on the call, retrying safely, making retries harmless, and ordering events when clocks disagree. Every lab is plain Python 3.12 standard library, runs on one machine — the Mac mini (Apple silicon) or the Windows 11 PC — and finishes in seconds. See `documentation/HARDWARE.md` for what runs where.

## L100 lesson map
| # | Level | Lesson | Lab folder | You will see | Tools | Validation |
|---|---|---|---|---|---|---|
| 1 | Setup | Set up your environment: a local multi-node lab | `labs/L100/01-setup-local-lab` | 3 node processes start, answer `/health`, stop | — | validated-local (compose.yaml: pending-ci) |
| 2 | L100 | Two services talking over HTTP | `labs/L100/02-two-services` | A → B request/response, a 404, latency min/median/max | Jaeger | validated-local |
| 3 | L100 | Timeouts: fail fast instead of hanging | `labs/L100/03-timeouts` | 2.0 s wait without timeout vs 0.5 s failure with one; p99.9-based timeout | Toxiproxy | validated-local |
| 4 | L100 | Retries with exponential backoff, jitter and a retry budget | `labs/L100/04-retries-backoff-jitter` | Full-jitter retries rescue a 30%-flaky B; budget stops a retry storm; optional agent assist (local model summarizes a retry log, code flags wrong p50/p99) | Toxiproxy, Jaeger | validated-local (agent assist: fake model server only) |
| 5 | L100 | Idempotency keys | `labs/L100/05-idempotency-keys` | 110 charged for 5×10 orders without keys; exactly 50 with keys | Jaeger | validated-local |
| 6 | L100 | Ordering events with Lamport clocks | `labs/L100/06-lamport-clocks` | Skewed wall clocks mis-order events; Lamport order doesn't | Maelstrom | validated-local |

## L200 lesson map ("Build it": extend working code, tests prove it)
| # | Level | Lesson | Lab folder | You will see | You build | Tools | Validation |
|---|---|---|---|---|---|---|---|
| 7 | L200 | Leader election with leases and fencing tokens | `labs/L200/07-leader-election-leases` | n1 pauses, lease expires at t=5, n2 takes over with token 4, n1's stale write REJECTED | `Node.resign()`: hand-over in the same tick | — | validated-local (etcd equivalent: pending-ci) |
| 8 | L200 | At-least-once messaging: ack, visibility timeout, redelivery, dead letters | `labs/L200/08-at-least-once-messaging` | 9 charges for 6 orders after crashes; poison message in the DLQ | Idempotent consumer: 6 charges | RabbitMQ UI, NATS CLI | validated-local |
| 9 | L200 | Sharding with consistent hashing | `labs/L200/09-consistent-hashing` | 4→5 nodes: modulo moves 80.3%, ring 18.9%; vnodes even the load; a hot key doesn't | `nodes_for(key, 3)` replica placement | — | validated-local (agent assist: fake model server only) |
| 10 | L200 | Caching and invalidation | `labs/L200/10-caching-invalidation` | Stale reads until the TTL; invalidate-on-write; 50-request herd = 50 DB reads | Request coalescing: 1 DB read | — | validated-local (Valkey equivalent: pending-ci) |
| 11 | L200 | Rate limiting: token bucket, 429 + Retry-After | `labs/L200/11-rate-limiting` | Polite client: 4 × 429; naive client: 35 × 429; quiet client: none | Sliding-window-log limiter | k6, Grafana | validated-local |

## L300 lesson map ("Harden it": works on the happy path, breaks under a seeded fault, you make it robust)
| # | Level | Lesson | Lab folder | Fault → symptom | You harden | Tools | Validation |
|---|---|---|---|---|---|---|---|
| 12 | L300 | Replicated log with Raft (simplified) | `labs/L300/12-raft-replicated-log` | Stale follower wins an election → `safety violations: 3` (committed x=1, x=2 lost) | Election restriction (up-to-date vote check): 0 violations, 0 of 20 seeds | Maelstrom | validated-local |
| 13 | L300 | Network partitions and fault injection | `labs/L300/13-partitions-fault-injection` | Proxy cuts n1 off the lease store → two leaders t=4-8, history `linearizable: False` | Fencing at storage: stale write rejected, history linearizable; optional agent assist (code checks the model's claims) | Toxiproxy, Maelstrom | validated-local (agent assist: fake model server only) |
| 14 | L300 | Sagas with compensation | `labs/L300/14-sagas-compensation` | Shipping fails for 3 of 6 orders → money kept, no refund | Reverse-order idempotent compensation + `recover()` from the saga log | Temporal CLI | validated-local (Temporal: manual) |
| 15 | L300 | Distributed tracing with W3C traceparent | `labs/L300/15-distributed-tracing` | One hop drops `traceparent` → 2 traces, payments time invisible | Propagating client middleware: 1 trace, full critical path | Jaeger, Grafana | validated-local (OpenTelemetry cross-check: pending-ci) |
| 16 | L300 | Backpressure and load shedding | `labs/L300/16-backpressure-load-shedding` | 150% burst, unbounded queue → p99 4.6 s, goodput 3,781 of 10,686 | Bounded queue + 503 + Retry-After: p99 155 ms, goodput 8,779; AIMD callers (tryIt) | k6 (+ web dashboard), Grafana | validated-local (k6: manual) |

## L400 lesson map ("Design it": compare options with evidence the lab generates, decide, record an ADR, keep it true with a fitness test)
| # | Level | Lesson | Lab folder | Options measured → decision | Fitness function | Tools | Validation |
|---|---|---|---|---|---|---|---|
| 17 | L400 | Consistency models in practice: quorums (N, R, W), staleness and PACELC | `labs/L400/17-consistency-quorums` | R=1 W=1: 16.74% stale; R=2 W=2: 0% stale but 2 inversions; + read write-back: linearizable, p99 65.9 → 124.5 ms → one setting per use case (ADR-017) | config setting linearizable on 10 seeds, p99 ≤ 150 ms, survives region loss | Maelstrom | validated-local |
| 18 | L400 | CRDTs for local-first collaboration: counters, OR-Set, LWW-Register and property tests | `labs/L400/18-crdts-local-first` | LWW number loses updates (81 of 140); counters + OR-Set 500/500; LWW tie diverges 114/500 until (ts, replica) tie-break (ADR-018) | laws + convergence on 3 × 500 histories; sync ≤ 4,096 B | Maelstrom | validated-local (Automerge 3.3.2: pending-ci) |
| 19 | L400 | Multi-region design: latency budget, leader placement, follower reads, failover RTO/RPO | `labs/L400/19-multi-region` | async loses 16 acked writes; majority-sync 0 (RTO ~1.3 s); multi-leader/leaderless 434/409 conflicts → majority-sync, leader eu by measured p99 (ADR-019) | brief holds on 10 seeds; eu still best-placed | Toxiproxy, k6 | validated-local |
| 20 | L400 | Chaos engineering: hypotheses, steady state, blast radius and seeded fault campaigns | `labs/L400/20-chaos-engineering` | unbounded experiment vs L300 saga: 60 customers hurt; 10% cohort + control + abort: 1; rolling restart finds the L300 Raft bug (1/20), random crashes don't (ADR-020) | experiments bounded; hardened L300 targets hold | Toxiproxy, k6 | validated-local |
| 21 | L400 | Verifying correctness: model checking and linearizability checking | `labs/L400/21-verifying-correctness` | 3 unit tests pass; random walks 16/1,000; BFS: 7-step counterexample; Porcupine-style checker pinpoints lab 17's inversion in 2,273 ops (ADR-021) | no reachable violation; config histories linearizable | Maelstrom | validated-local (TLA+/TLC: pending-ci) |
| 22 | Capstone | An order pipeline that survives chaos and proves it | `labs/L400/22-capstone` | saga + outbox + idempotent consumers + tracing + backpressure + Raft config; 9 experiments × 3 seeds | scorecard 10/10 (`run_capstone.py`, JSON lines; exit code) | Jaeger, Temporal CLI | validated-local (agent: fake model server only) |

## L500 lesson map ("Theory & rigour": proofs, ethics and primary papers; every theorem checked in code)
| # | Level | Lesson | Theorems / content | Check (seeded, stdlib) | Problems | Validation |
|---|---|---|---|---|---|---|
| 23 | L500 | Foundations I: system models, time and causality - with proofs | T23.1 Lamport clock condition (0 violations in 13,599 a->b pairs; converse fails for 11,063 concurrent pairs); T23.2 vector clocks = happened-before; T23.3 safety vs liveness; T23.4 failure detection vs timing model | `labs/L500/23-system-models-time/clocks_proofs.py` | 8 | validated-local |
| 24 | L500 | Foundations II: impossibility results and consensus - two generals, FLP, CAP, quorums and Paxos | T24.1 two generals (140/140 protocols fail); T24.2 FLP (sketch; duelling proposers 1,000 rounds undecided); T24.3 CAP as Gilbert & Lynch proved it; T24.4 quorum intersection + Paxos P2c (0 violations in 3,000 runs; broken variant 2,296) + Raft comparison | `labs/L500/24-impossibility-consensus/consensus_proofs.py` | 8 | validated-local |
| 25 | L500 | Foundations III: performance theory - M/M/1, Little's law, tail amplification, Amdahl and USL | T25.1 M/M/1 (W 4.992 vs 5 at rho 0.8); T25.2 Little (exact to 1e-15); T25.3 fan-out 100 -> 0.6329 vs 0.6340; T25.4 Amdahl bound, USL peak, fitted simulation | `labs/L500/25-performance-theory/perf_proofs.py` | 8 | validated-local |
| 26 | L500 | Ethics: reliability as a professional duty - outages, blameless post-mortems, data residency and energy | case study: AWS us-east-1 7 Dec 2021 + EU telehealth failover decision; ACM 2018, IEEE, GDPR Art. 32 / Chapter V, Google SRE ch. 15, IEA | - | 6 | validated-local (sources) |
| 27 | L500 | Reading seminar: Lamport (1978) and Ongaro & Ousterhout (2014) | 2 readings x 5 guiding questions + critical-response prompts | - | 6 | validated-local (sources) |

L500 lessons (`content/L500.json`, built by `python research/build_l500.py` from `research/l500_lessons_*.py`; notes in `content/concepts/L500/`) add `learningObjectives` (Bloom verbs), `theorems` (statement, proof, `check` command, real `checkOutput`), `problemSet` (worked solutions; calculation `answer`s recomputed), `caseStudy` (26), `readings` (27) and a `rubric` for the written work. Checks:
```bash
python research/l500_checks.py        # re-runs all 12 theorem checks (output must equal checkOutput), 21 problem answers, 12 exam numbers
python research/check_l500_qbank.py   # L500 question bank + concept inventory rules (tools/check_qbank.py reads L100-L400 only)
python research/qbank_checks.py       # every calculation and code-reading answer, L100-L500
cd labs/L500/24-impossibility-consensus && python consensus_proofs.py paxos && python -m unittest -v
```
**Assessment pack** (`content/assessment/`): `syllabus.md` (14 weeks; labs 35%, problem sets 25%, exams 20%, capstone + oral defence + peer-reviewed ADRs 20%; CS2023 and ABET CAC/EAC mapping), `midterm.md`, `final.md`, `concept-inventory.json` (15 pre/post items), `capstone-oral-defence.md`, `peer-review-adr.md`, `team-roles.md`. **Question bank:** `content/qbank/L500.json`, 44 questions (lessons 23-25: 10 each; 26-27: 7 each). Sources: `documentation/VERIFIED-RESOURCES.md` (L500 section); gaps: `documentation/KNOWN-GAPS.md` (L500 section); research log: `research/L500-evidence.md`.

L400 lessons (`content/L400.json`, notes in `content/concepts/L400/`, sections: why it matters, mental model, design space, how to decide (with a worked example from the lab's real output), failure modes at scale, common mistakes) add `designBrief`, `options` (with measured `evidence` and a `verdict`), `decisionRecord` (an ADR in Nygard format in the lab folder), `fitnessFunction` (`test_fitness.py`) and `scalingLimits`. The capstone (`level: "Capstone"`) has `architecture` (`architecture.mmd`), `milestones` (one test each), `rubric`, `fitnessFunctions`, `decisionRecords` (`adr/ADR-022-1..4`) and an `agentAssist` that only explains.

L300 lessons (`content/L300.json`, notes in `content/concepts/L300/`, 5 sections: why it matters, mental model, how it works → lab step, failure modes, common mistakes) add `failureLab` (`fault`, `symptom`, `fix`, `proof`) and `tradeOffs` (option, gains, costs, chooseWhen); `codeWalkthrough` has 5-7 items and `buildTask` is the hardening change. Labs 13, 14, 15 and 16 print JSON lines (client history, saga log, spans, per-second metrics) to read while diagnosing. Concept notes are 17% of the L300 words (spec script; target 30-35%; notes at full length 505-550 words — see KNOWN-GAPS).

**Tools** column: optional open-source learning tools (see, inspect or check what the lab does) — install commands, roles, licences and "not recommended" tools in `documentation/LEARNING-TOOLS.md`; the per-lesson exercise is the lesson's `learningTools` field (pending manual runs). Lessons also carry `seeAlso` (the same idea in another topic, e.g. the idempotent consumer in application-architecture #9) and `next` (a built lesson by level, number and exact title; L300 #16 points to L400 #17, L400 #21 to Capstone #22).

L200 concept notes are in `content/concepts/L200/` (5 sections: why it matters, mental model, how it works → lab step, trade-offs table, common mistakes); lessons are in `content/L200.json` with two new fields: `codeWalkthrough` (3-4 key lines explained) and `buildTask` (`task`, `hints`, `solution`, `check`). Concept notes are ~18% of the L200 words (spec script; target 25-30%; 19% before the learning-tools pass — see KNOWN-GAPS).

**Read first:** `documentation/CONCEPTS-PRIMER.md` (what the domain is for, mental model, concept map, glossary). Before each lab, read its short concept note in `content/concepts/` (linked as `conceptNote`; 4 sections: why it matters, mental model, how it works → lab step, common mistakes).

Lesson content (steps, code, expected results, tests, `tryIt` experiments, troubleshooting, equivalents, `inRealSystems`, `useWhen`, checkpoint + `checkYourself`, sources, `next`, `conceptNote`, `conceptSummary`) is in `content/L100.json`. Hands-on leads: concept notes are about 13% of the words (spec script; 14% before the learning-tools pass, 16% before the Mac/Windows + agent-assist additions; target 20-25%, not padded — see KNOWN-GAPS).

All lessons carry `"platforms": {"mac": "expected", "windows": "expected"}` (validated on Linux; the CI matrix covers macos-latest arm64 and windows-latest). Lesson 1 steps carry `mac` (zsh) and `windows` (PowerShell) commands.

## Concept share (measured)
Spec measure script (REBALANCE-SPEC: concept-note words vs the lesson objects without `conceptNote`, `conceptSummary`, `sources`, `validation`), run 2026-10-28 after the L400 build:
- L100: concept 1484 / hands-on 9582 words = **13.4%** (target 20-25%; notes 244-250 words).
- L200: concept 1934 / hands-on 8909 words = **17.8%** (target 25-30%; notes 375-398 words).
- L300: concept 2699 / hands-on 13468 words = **16.7%** (target 30-35%; notes 505-550 words, `wc -w`; re-measured after the L400 back-links).
- L400 + capstone: concept 3938 / hands-on 19639 words = **16.7%** (target 35-40%; notes 635-749 words, capstone 506).
All notes are at full length and were not padded; labs were not cut (KNOWN-GAPS). The `learningTools`, `failureLab`, `tradeOffs` and exact-copy `code` fields carry most of the hands-on words.

## How to run the labs
Full workstation setup (both machines, all topics): `../shared/WORKSTATION-SETUP.md`. Install once (lesson 1, step 1): macOS `brew install python@3.12` → `python3.12 -m venv .venv` → `source .venv/bin/activate`; Windows `winget install -e --id Python.Python.3.12` → `py -3.12 -m venv .venv` → `.venv\Scripts\Activate.ps1` → `$env:PYTHONUTF8 = "1"`. Then the same commands on both:
```bash
python --version                 # 3.12 or newer
cd labs/L100/04-retries-backoff-jitter
python retries.py                # the demo; compare with "Expected output" in the lab README
python -m unittest -v            # the lab's tests
python try_it.py                 # the lesson's two tryIt experiments (compare with the lab README "Try it")
```
- Each lab folder holds the lesson file (shown as `code` in the lesson), `helpers.py` for plumbing (labs 2–6: quiet HTTP handler, background server; lab 4 also the simulated flaky B, lab 6 the log printer), `try_it.py` and `test_*.py`.
- No `pip install` needed. Servers bind to `127.0.0.1` on OS-chosen ports (lab 1 uses 8001+; override with `LAB_BASE_PORT`).
- Labs 3–6 use seeded randomness or simulated time, so their output is identical on every run. Lab 2 prints measured latencies, which vary.
- Windows: set env vars with `$env:LAB_BASE_PORT=18001`, and call `curl.exe` (not the PowerShell `curl` alias).
- Optional (lab 1): the same nodes in containers (`compose.yaml`, Podman first) and a Mac mini ↔ Windows PC LAN run are in `documentation/OPTIONAL-SETUP.md`; both pending (see KNOWN-GAPS).
- Optional agent assist (lab 4): `python agent_assist.py --fake` uses the vendored `labs/_shared/local_agent` fake model server; without `--fake` it calls a local Ollama (`LOCAL_MODEL_URL`, default `http://localhost:11434/v1`). Code computes every number; the model only proposes a summary. Never send secrets to a model.
- **L200 build tasks:** each L200 lab has `solution_<name>.py` (the reference) and `test_build_task.py`. `python -m unittest` tests the reference; to test **your** edited lesson file run `BUILD_TARGET=mine python -m unittest test_build_task -v` (macOS) or `$env:BUILD_TARGET="mine"; python -m unittest test_build_task -v` (Windows PowerShell). It fails until you have built the feature.
- L200 labs 7, 8 and 11 run small HTTP services on `127.0.0.1` (OS-chosen ports) with a simulated clock, so their output is identical on every run; lab 9 is pure computation; lab 10's herd uses real threads (count can vary on a loaded machine).
- Optional containers (L200): etcd `gcr.io/etcd-development/etcd:v3.7.3` (lab 7) and Valkey `docker.io/valkey/valkey:9.1.3` (lab 10) via Podman/Colima (Mac mini) or Podman Desktop (Windows) — pending-ci.
- **L300 failure labs:** run the lesson file to see the fault, then `BUILD_TARGET=mine python -m unittest test_build_task -v` fails until you harden it (macOS; Windows: `$env:BUILD_TARGET="mine"; ...`). All L300 labs are seeded; labs 12-14 and the lab 16 simulation print identical output every run, lab 15 measures real time (ids repeat, durations vary). Lesson 15's `otel_equivalent.py` needs `python -m pip install -r requirements-otel.txt` (OpenTelemetry 1.45.1; CI only so far).
- **L400 design labs:** each lab prints the measured options (`python quorum.py`, `crdts.py`, `multiregion.py`, `chaos.py`, `modelcheck.py` + `lincheck.py`), has an ADR, a build task (`BUILD_TARGET=mine python -m unittest test_build_task -v`) and a fitness function (`BUILD_TARGET=mine python -m unittest test_fitness -v`); both fail on the unmodified lesson file. All are seeded simulations on simulated time (identical output every run; lesson 21 also prints timings, which vary). Labs 20, 21 and the capstone import earlier labs by path - keep the folder layout. Capstone: `python run_capstone.py` (scorecard, exit code), `python run_capstone.py --explain --fake` (agent explanation against the fake model server). Optional: `npm install && node automerge_equivalent.mjs` (lesson 18, Node 24) and TLC on `Election.tla` (lesson 21, Java) - CI only so far.
- CI: `.github/workflows/labs.yml` runs every L100, L200, L300 and L400 demo, test and `try_it.py`, the L500 theorem checks and tests (jobs `python-labs-l500`, `l500-checks`) (plus the reference solutions) on ubuntu-latest, macos-latest and windows-latest (Python 3.12), the agent assists and shared-helper tests against the fake server, the Compose lab with Docker and with Podman, the etcd and Valkey equivalents on Linux, the OpenTelemetry cross-check of lesson 15 (job `otel`, all three OSes), the capstone scorecard (job `capstone`), the Automerge cross-check of lesson 18 (job `automerge`) and TLC on lesson 21's `Election.tla` (job `tla`, Linux).

## Other files
- `documentation/LEARNING-TOOLS.md` — optional open-source learning tools per lesson (Toxiproxy, Jaeger, Maelstrom, RabbitMQ, NATS, k6, Grafana, Temporal CLI) and tools not recommended.
- `documentation/OPTIONAL-SETUP.md` — lesson 1 extras: containers and two machines.
- `documentation/HARDWARE.md` — Mac mini vs Windows PC: what runs where, RAM/disk, GPU (only for the optional agent).
- `documentation/VERIFIED-RESOURCES.md` — every source used, with licence, date checked and score.
- `documentation/KNOWN-GAPS.md` — what is not verified, simulated, or deferred.
- `research/L100-evidence.md` — research questions, sources considered, key facts per lesson.
- `research/concept_examples.py` — computes the numbers used in the concept notes (`python research/concept_examples.py`).
- `research/L200-evidence.md`, `research/concept_examples_l200.py` — the same for L200 (`python research/concept_examples_l200.py` runs the L200 labs).
- `research/L300-evidence.md`, `research/concept_examples_l300.py` — the same for L300.
- `research/L400-evidence.md` — the same for L400 (worked-example numbers come from the lab outputs in each L400 README).
