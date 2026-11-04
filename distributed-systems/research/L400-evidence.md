# L400 research evidence — Distributed Systems (applied)

Method: SPEC.md research method (unchanged). Sources fetched 2026-10-28 with web_fetch / web_search. Score = implementable / current / authoritative / open / transferable / depth (0-2 each); keep >= 8/12. Every number in the L400 concept notes, ADRs and lesson fields comes from running the labs (`labs/L400/*`; captured outputs in each README). Learning-tool facts come from `../../shared/LEARNING-TOOLS-CATALOG.md` only.

---

## Lesson 17 — Consistency models in practice
**Questions**
1. What exactly does PACELC say, and how does Abadi relate R + W > N to consistency?
2. How do Dynamo-style quorums execute reads and writes (who waits for whom), and what makes latency?
3. Is R + W > N linearizable? If not, what is the standard addition?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Abadi, Consistency Tradeoffs in Modern DDBS Design (IEEE Computer 2012), cs.umd.edu PDF | kept (primary) | 12 | PACELC definition; replication options; "simply using a quorum protocol is not sufficient" for Gilbert & Lynch consistency; cites Attiya/Bar-Noy/Dolev |
| DeCandia et al., Dynamo (SOSP 2007), allthingsdistributed.com PDF | kept (primary) | 11 | R, W, N; "latency ... dictated by the slowest of the R (or W) replicas"; sloppy quorum and hinted handoff; vector clocks |
| Jepsen consistency reference (jepsen.io/consistency) | kept (background) | 9 | Consistency model = set of allowed histories; fetched page gave only the overview |
| IEEE Xplore page of the Abadi article | dropped | — | Paywalled landing page; the author's PDF is the same text |

**Key facts**
- PACELC: "if there is a partition (P), how does the system trade off availability and consistency (A and C); else (E) ... latency (L) and consistency (C)?" — Abadi 2012
- "Technically, simply using a quorum protocol is not sufficient to guarantee consistency to the level defined by Gilbert and Lynch" (ref. 11 = Attiya, Bar-Noy, Dolev, JACM 1995) — Abadi 2012; the lab's write-back follows that reference's two-phase read.
- Dynamo/Cassandra/Riak default to PA/EL; raising R + W trades latency for consistency, but "they cannot achieve full consistency as defined by Gilbert and Lynch, even if R + W > N" — Abadi 2012
- "the latency of a get (or put) operation is dictated by the slowest of the R (or W) replicas" — Dynamo §4.5; sloppy quorum §4.6
- Single-writer register check (stale + new-then-old = not linearizable) cross-checked in code against the exhaustive L300 #13 checker on 300 short histories (identical verdicts, 89 rejected); Gibbons & Korach's register result is cited in Lowe 2017 (lesson 21).

## Lesson 18 — CRDTs for local-first collaboration
**Questions**
1. What are the sufficient conditions for convergence (state-based vs op-based)?
2. Exact specifications of G-Counter, PN-Counter, OR-Set, LWW-Register; what must LWW timestamps satisfy?
3. Which maintained library is the equivalent, at which version and licence?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Shapiro, Preguiça, Baquero, Zawirski, RR-7506 (author's copy, perso.lip6.fr) | kept (primary) | 12 | LUB is commutative, idempotent, associative; Spec. 6/7/8 (G/PN-Counter, LWW); timestamps "unique, totally ordered, ... per-replica counter concatenated with a unique replica identifier"; OR-Set add-wins; GC needs synchronisation |
| hal.inria.fr copy of RR-7506 | dropped | — | Fetch returned no document; the author's copy is identical |
| lri.fr course copies of RR-7506 | dropped | — | Course mirrors; author's copy preferred |
| Kleppmann et al., Local-first software (Ink & Switch / Onward! 2019) | kept | 10 | Seven ideals; CRDTs as foundation; conflicting values kept for the app |
| automerge/automerge README (MIT) + npm @automerge/automerge 3.3.2 | kept | 11 | Current JS package and API (from, clone, change, merge); Automerge 3 |
| PyPI automerge | dropped | — | Latest stable 0.1.2 (2022); 0.2.0.dev4 / 1.0.0rc1 pre-releases only - the JS package is the maintained path |
| Maelstrom workloads.md (g-counter, pn-counter) | kept (tool) | 10 | Checker: final reads equal the sum of all deltas |

**Key facts**
- "merge ... converges towards the LUB"; G-Counter merge = per-entry max; a sum-merge "is not a CvRDT, as merge is not idempotent" — RR-7506 §3.1.2 (the lab's tryIt 1 measures it: idempotent 7/500)
- LWW-Register timestamps "assumed unique, totally ordered, and consistent with causal order ... a per-replica counter concatenated with a unique replica identifier" — RR-7506 §3.2.1 (the build task)
- @automerge/automerge 3.3.2, MIT, published ≈10 days before 2026-10-28 — npm page
- `getConflicts` and `Counter` in automerge_equivalent.mjs follow the Automerge JS API as documented; not executed here (pending CI).

## Lesson 19 — Multi-region design
**Questions**
1. Which replication schemes exist and what does each cost (sync, async, quorum)?
2. Why does majority commit preserve every acknowledged write across a leader failure?
3. Where are RTO and RPO defined?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Raft paper (raft.github.io/raft.pdf; already in VERIFIED-RESOURCES) | kept (primary) | 12 | Majority commit, election restriction (§5.4), read-only requests must check leadership (§8) |
| Abadi 2012 (lesson 17) | kept | 12 | Sync vs async master replication; PNUTS PC/EL with reads from any replica |
| NIST SP 800-34 Rev. 1 (csrc.nist.gov page + nvlpubs PDF) | kept (terms) | 9 | Where RTO/RPO are defined (BIA, §3.2); the fetched PDF text was truncated before the definitions, so the lesson paraphrases and does not quote |
| Third-party RTO/RPO blogs (search results) | dropped | — | Secondary; vendor/consultancy pages |

**Key facts**
- Majority-sync RPO 0 is a property of the simulation's rules (commit needs a follower; the most up-to-date survivor leads); measured 0 at every placement; async 16-17 lost.
- One-way latencies (40/70/110 ms) are labelled assumptions in `helpers.py`, not measurements.

## Lesson 20 — Chaos engineering
**Questions**
1. What are the steps and advanced principles of a chaos experiment?
2. How is blast radius bounded and what is a control group?
3. Which tools are equivalents (catalog only for learning tools)?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| principlesofchaos.org (2019) | kept (primary) | 10 | Four steps (steady state, hypothesis in control and experimental group, real-world variables, disprove); minimise blast radius; automate |
| Basiri et al., Chaos Engineering (IEEE Software 2016; arXiv 1702.05843) | kept | 10 | The originating article |
| chaos-mesh/chaos-mesh README | kept (equivalent line only) | 9 | Apache-2.0, CNCF incubating, Kubernetes custom resources, Schedule/Workflow |
| Toxiproxy | kept (catalog) | — | Learning tool; facts from the catalog |

## Lesson 21 — Verifying correctness
**Questions**
1. Which algorithm does Porcupine implement, and what does memoisation store?
2. Current TLA+ tools version and licence; how is TLC run from the command line?
3. Which invariant names / persistent state does Raft require for voting?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| anishathalye/porcupine README (MIT) | kept (primary) | 11 | Algorithm = "Faster linearizability checking via P-compositionality", an optimisation of "Testing for Linearizability"; register example histories (used as test vectors); users incl. etcd, MIT 6.5840 |
| Lowe, Testing for Linearizability (CCPE 2017), author's PDF | kept (primary) | 11 | Wing & Gong tree search; graph search remembers configurations (state + linearized set); Gibbons & Korach: NP-complete in general, registers tractable |
| tlaplus/tlaplus releases + LICENSE | kept | 11 | v1.7.4 "Xenophanes" latest stable (2024-08-05; tla2tools.jar SHA-1 bee4a54f...); v1.8.0 "Clarke" pre-release (≈2026-10-25); MIT; Toolbox no longer maintained (use VS Code extension or CLI); TLC exits non-zero on violations (1.6.0 notes); CHECK_DEADLOCK in config (1.7.0 notes) |
| Raft paper Figure 2 / 3 | kept | 12 | votedFor is persistent state; Election Safety |

**Key facts**
- The lab's memoised checker reproduces Porcupine's README verdicts (true, false) and agrees with the L300 #13 exhaustive checker on 300 histories.
- TLC invocation `java -cp tla2tools.jar tlc2.TLC -config X.cfg Spec.tla` follows the tools' documented main class (tlc2.TLC is the jar's main class since 1.6.0); not run here (no Java).

## Capstone 22
Reuses lessons 5, 8, 12, 14, 15, 16, 20, 21; sources already listed (W3C Trace Context, Sagas paper, Raft paper, Principles of Chaos). Outbox: application-architecture L200 #9 (cross-topic). No new external facts.
