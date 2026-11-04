# Known gaps — Distributed Systems L100

## Not run locally (pending-ci)
- **Compose lab** (`labs/L100/01-setup-local-lab/compose.yaml`): no container runtime (Docker, Podman, Colima, nerdctl) in the validation sandbox. Written against the Compose docs and the `python:3.12.16-slim` tag listed on Docker Hub (2026-10-28); only YAML parsing (merge key resolved) was checked. Runs in the `compose-docker` and `compose-podman` CI jobs. Not observed working. Colima and Rancher Desktop compatibility rests on their docs (Colima: docker runtime + docker CLI; Rancher Desktop ships Docker Compose and nerdctl) — not run, and not in CI (no macOS/Windows container job).
- **CI workflow** itself (`.github/workflows/labs.yml`) has not been executed. Pins (`actions/checkout@v7`, `actions/setup-python@v7`, `python-version: "3.12"` since the platform pass, `ubuntu-24.04` for the Compose jobs) come from the setup-python README; the checkout version is only as shown in that README; availability of exact patch 3.12.15 on the runner and Docker Compose on `ubuntu-24.04` images were not verified.
- `curl` is used in the CI compose job and suggested in READMEs; it was not available in the sandbox, so local checks used Python `urllib` instead.

## Mac mini + Windows (PLATFORM-AGENT-SPEC, 2026-10-28)
- **Everything was run on Linux only.** `platforms` is `expected` for mac and windows in every lesson until the CI matrix (macos-latest arm64, windows-latest) runs. The workflow itself has not been executed.
- **Windows-only code paths not executed:** `node.py`'s exclusive bind (`SO_EXCLUSIVEADDRUSE`, `allow_reuse_address=False`) and `lab.py`'s `terminate()` → `TerminateProcess`. The fallback constant `~SO_REUSEADDR` (= winsock's definition) is used only if the `socket` module lacks `SO_EXCLUSIVEADDRUSE` — not checked on a Windows Python. Without the fix, Windows `SO_REUSEADDR` lets a second process bind a port in use (Microsoft Learn) and Python's `HTTPServer` sets `allow_reuse_address = 1` (read in the local 3.12.15 stdlib source).
- **Error wording** on macOS (`[Errno 48] Address already in use`) and Windows (`[WinError 10048]`, `[WinError 10061]`) is from docs/errno tables, not observed; the full Windows message text is localized.
- **Windows refused connections** may take longer than on Linux because of SYN retransmission; if it exceeds the 0.5 s health timeout, tryIt 2 can print `TimeoutError` instead of `ConnectionRefusedError` on Windows (unverified; the test only asserts `OSError`).
- **CI Python pin** relaxed from `3.12.15` to `3.12` (latest 3.12 per runner): python.org publishes no Windows/macOS installers for 3.12 security releases, and winget's `Python.Python.3.12` was at 3.12.10 when checked. Whether the runner caches hold 3.12.15 on macOS/Windows was not verified.
- **LAN step** (two real machines) not run; validated only with a node on `0.0.0.0` queried through the sandbox's own non-loopback IP. macOS firewall prompt wording and `ipconfig getifaddr en0` (en0 = Ethernet on a Mac mini) not verified on hardware; Windows `New-NetFirewallRule` parameters are from Microsoft Learn.
- **Podman on the CI runner**: assumed present on `ubuntu-24.04` images (not verified); `podman-compose==1.6.0` from PyPI (released 2026-06-03).
- **RAM/disk numbers** in HARDWARE.md are vendor guidance (Colima defaults, Podman Desktop and Rancher Desktop requirements), not measured.

- **Concept share** after this pass: `concept 1484 hands-on 8867 share 14%` (was 16%, below the 20–25% band; accepted by the user — notes were not padded).

## Agent assist (lab 4)
- Run only against the vendored deterministic fake model server (rule `[[RETRY-LOG-SUMMARY]]` added to `labs/_shared/local_agent/fake_model_server.py`). It makes two mistakes on purpose (p50 = mean, p99 = max); a real model's errors will differ. No real model (Ollama / llama.cpp) was run; `qwen2.5:1.5b` is only the helper's default name.
- The prompt avoids the words that trigger the fake server's built-in JSON and sentiment rules (they are checked before topic rules).
- Percentiles use nearest-rank; lab 3 uses `statistics.quantiles`. Both are correct definitions; values can differ slightly on small samples.

## Simulations / stand-ins
- All "nodes" run on one machine: no real network loss, latency or partitions. Faults are injected in code: sleeping handlers (lab 3), seeded 503s (lab 4), seeded "lost responses" via closing the connection without a reply (lab 5).
- Lab 3's latency percentiles come from a seeded lognormal sample, not from measuring a real service.
- Lab 6 wall clocks are simulated (shared simulated "true time" + fixed per-node skew) so output is reproducible; only the messages are real HTTP.
- Lab 5's dedupe store is an in-memory dict; it does not show persistence, atomicity with the side effect, per-client key scoping, or TTL expiry (described in README/caution only).

## Unverified or single-sourced facts
- **Lamport clock rules** (tick on local/send, `max(local, received) + 1` on receive, node-id tie-break): now cross-checked against the primary source, Lamport's 1978 paper (author's PDF, rules IR1, IR2(a)/(b) and the tie-break by "any arbitrary total ordering of the processes"); `max + 1` is one valid choice under IR2(b) ("greater than or equal to its present value and greater than T_m"). The Wikipedia source was replaced (R3-13).
- **AWS jitter formulas**: the blog post renders formulas as images, which web_fetch could not read; the formulas (`min(cap, base*2^n)`, full jitter `uniform(0, v)`, equal, decorrelated) were taken from the blog's linked simulator source code.
- **gRPC retry-throttling boundary**: the gRPC guide says retries pause when the token count "falls below half of maxTokens"; the lab allows retries at exactly half. The gRFC A6 text was not fetched to confirm the exact boundary.
- The lab's retry budget does not charge non-retryable errors (e.g. 404) against tokens; this is a design choice, not taken from a source.
- `urlopen(timeout=...)` being per-socket-operation (not total) is inferred from the docs' wording "timeout for blocking operations like the connection attempt"; not separately tested with a trickling server.
- **Licences**: for most docs pages the licence was not visible in the retrieved text (marked "not shown on page" in VERIFIED-RESOURCES). Not claimed.
- Amazon Builders' Library URL redirected to builder.aws.com; content matched the 2019 article.

## Spec deviations
- Main lab files after the 2026-10-28 trim: lab.py 59, two_services.py 55, timeouts.py 59, retries.py 69, idempotency.py 81, lamport.py 66 lines (spec: "typically 15-60"). Plumbing now lives in a per-lab `helpers.py` (41–43 lines). retries.py and idempotency.py stay above 60 because the retry loop + budget + demo, and the dedupe server + at-least-once client + demo, are each the lesson's concept; splitting them further would hide it from the `code` field.
- Lesson 2 output contains measured latencies and an OS-chosen port, so it is not byte-for-byte reproducible (no randomness is involved).

## Dropped / deferred
- Vector clocks, hybrid logical clocks, circuit breakers, hedged requests, deadline propagation across hops: mentioned at most in one line; deferred to L200.
- Stripe/Adyen/PayPal idempotency docs: not used as sources (vendor docs); appear only via the IETF draft's implementation list and one equivalents line.

## Concepts layer (added 2026-10-28)
- **Curriculum L200–L400** in `CONCEPTS-PRIMER.md` is a proposal for this knowledge base: no agreed curriculum file was provided. L300/L400 topics follow the table of contents of Kleppmann's Cambridge notes; L200 topics were chosen by the author.
- **RFC 9110 §9.2.2 (idempotent methods)** was not in the retrieved text; the method list in concept 5 is taken from the IETF idempotency draft, which quotes RFC 9110.
- **Kafka idempotent producer** (`enable.idempotence`): the config page could not be retrieved (it redirected to the Kafka 4.3 introduction), so Kafka is used only for primer application areas, not as an idempotency example.
- The Envoy docs page is the `latest` (1.41.0-dev) build; defaults quoted (25 ms base, 250 ms cap) may change in future releases.
- The probability figures in concept 4/5 (0.0081, 1.417, 0.92224) assume independent failures; real failures are often correlated.
- The health-reply length (44 bytes) in concept 1 uses an example PID (4242); real replies vary by a few bytes.
- Word counts before the rebalance (`wc -w`, includes code/diagram tokens): notes 616–645, primer 869. See "Rebalance" below for the current counts.

## Rebalance (2026-10-28, REBALANCE-SPEC.md)
- **Concept share below the L100 band.** Spec script: before `concept 3898 hands-on 5963 share 40%`; after `concept 1484 hands-on 7717 share 16%` (target 20–25%). The 200–250-word cap on six notes (max 1,500 concept words) cannot reach 20% unless hands-on content is cut to about 6,000 words; hands-on material (tryIt, checkYourself, inRealSystems/useWhen, code) was kept rather than deleted to hit the band. Hands-on leads, as the user decided.
- **Word counts depend on locale.** Notes are 232–243 words with `LC_ALL=C wc -w` and 244–250 with a UTF-8 locale (box-drawing and arrow characters count as words there) and with the spec's Python `split()`; the primer is 557 / 580. All are inside the spec ranges either way.
- The `#` title line was removed from each note so it has exactly the 4 headings; the lesson `title` names it.
- tryIt expected values are real output from `try_it.py` on Linux. Lab 1 tryIt 1 shows Linux's `[Errno 98]` text; other OSes word it differently. Lab 2 tryIt 2 prints a measured total (166 ms in the recorded run) that varies; its two boolean checks don't.
- Lab 1's `start()` wait was raised from 5 s to 15 s: the unchanged test failed once in the shared sandbox because three Python processes took more than 5 s to start.
- Lessons now list 4–6 `sources` (the old "Go deeper" links merged in), above the original "max 4 per lesson" note in VERIFIED-RESOURCES.

## L200 (lessons 7-11, built 2026-10-28)
### Not run locally (pending-ci)
- **etcd equivalent** (`labs/L200/07-leader-election-leases/etcd_equivalent.py`): no etcd or etcdctl in the sandbox; only byte-compiled. Runs in the CI job `etcd` (container `gcr.io/etcd-development/etcd:v3.7.3`, etcdctl from the v3.7.3 release tarball). Not verified: that `put ... --lease=<id>` is accepted inside an `etcdctl txn` request line, the tarball's top-level directory name (`etcd-v3.7.3-linux-amd64`), and that the granted 2 s lease expires within the script's 15 s polling window (etcd may grant a longer TTL than requested). The etcd JSON gateway paths for lease and election (`/v3/lease/grant`, `/v3/election/campaign`) were seen only in proto/swagger search results; the script deliberately uses etcdctl instead. On Windows, `terminate()` kills `etcdctl elect` without a resign, so failover waits for the lease TTL (inferred from the etcdctl README, not run).
- **Valkey equivalent** (`labs/L200/10-caching-invalidation/valkey_equivalent.py`): no Valkey in the sandbox. Its RESP2 client passed `test_valkey_client.py` against a fake socket server written for the test — that checks framing and reply parsing, not Valkey semantics. Runs in the CI job `valkey` (service container `valkey/valkey:9.1.3`).
- **CI workflow**: the new jobs (`python-labs-l200`, `etcd`, `valkey`) have not been executed; YAML parsed with PyYAML locally.

### Mac mini + Windows
- Everything ran on Linux only; every L200 lesson has `platforms: expected`. Build-task commands give both `BUILD_TARGET=mine ...` (zsh) and `$env:BUILD_TARGET="mine"; ...` (PowerShell) — the PowerShell form was not executed.
- Lesson 10's herd count (50 database reads) depends on thread scheduling; observed 50 on 3 of 3 Linux runs. On a loaded machine a few late threads may hit the freshly filled cache; the test asserts only `> 1`.
- Lesson 8's `try_it.py` takes ~30 s (92 broker runs over HTTP); timing on macOS/Windows not measured.

### Simulations / stand-ins
- Leases, broker visibility timeouts, TTLs and rate-limit refill run on a **simulated clock** (`SimClock`) so outputs are reproducible; real systems use wall/monotonic clocks and see clock drift and real pauses.
- The lease store and broker are single-process and in-memory: no persistence or replication (etcd uses Raft; RabbitMQ quorum queues replicate with Raft). Lesson 10's database is an in-process object with a 0.2 s sleep (an HTTP version overloaded ThreadingHTTPServer's listen backlog with 50 concurrent connections in the sandbox and was dropped).
- Lesson 9 uses md5 for placement; production stores use their own partitioner hash functions, not compared here.
- Agent assist (lesson 9) ran only against the vendored fake model server (rule `[[SHARD-LAYOUT]]` added to `labs/_shared/local_agent/fake_model_server.py`, which deliberately breaks shard S5). No real model run. The prompt avoids the words that trigger the fake server's built-in JSON/sentiment rules, and avoids `x@y` text other than node names (an earlier draft's "(name@zone)" was parsed as a node).

### Unverified or single-sourced facts
- **RFC 9110 §10.2.3 (Retry-After)**: the RFC page was retrieved but the fetched text stopped before section 10; the two forms (HTTP-date / delay-seconds, a non-negative decimal integer) are taken from MDN (which cites RFC 9110 `field.retry-after`) and cross-checked with http.dev and Envoy's docs. RFC 6585 §4 was read in full.
- **Kafka delivery semantics**: only the Confluent page (vendor docs describing Apache Kafka) was retrieved; used for one equivalents line.
- **NATS acknowledgment page**: text obtained through web_search results (two mirrors agree), not a direct fetch.
- The original consistent-hashing paper (Karger et al., 1997) and the Dynamo paper were not fetched; the lesson relies on Cassandra's docs and the memcache paper.
- "Retry-After rounded up to whole seconds halves a polite client's throughput at burst 1" is this lab's observation (tryIt 2), not a sourced claim.

### Spec deviations / measurements
- **Concept share** (spec script on `content/L200.json`): `concept 1934 hands-on 8241 share 19%` (target 25-30%). Notes are 368-393 words (`wc -w`; 375-398 with Python `split()`), so concept words are near the 2,000 cap; hands-on is dominated by the exact-copy `code` fields (2,134 words) and the new L200 fields (`codeWalkthrough` 441, `buildTask` 359, `agentAssist` 216, Mac/Windows step commands 163). Without those four it would be ~21%. Not padded, not cut further.
- Main lab files are 66-87 lines (spec ~40-90); solutions add 4-18 lines each.
- ~~L100 lessons' `next` fields still name the earlier L200 proposal~~ — fixed in the tools/review pass below (F03).

## Tools/review pass (2026-10-28, UPDATE-TOOLS-REVIEW-SPEC)
### Fixed
- **F03** L100 `next` now names built lessons (1→#9, 2→#11, 3→#7, 4→#11, 5→#8, 6→#7); L200 #11 `next` = "L300 (planned): …". L200 #7–10 still point to L300 topics (no L300 exists yet).
- **F05/F04/F19** Lesson 1 step 1 uses the `../shared/WORKSTATION-SETUP.md` commands (incl. `$env:PYTHONUTF8 = "1"`, canonical ExecutionPolicy line) and links to it. Model env vars were already `LOCAL_MODEL_URL` / `LOCAL_MODEL`. No Node in this topic.
- **F06/F15/F16** VERIFIED-RESOURCES: winstall.app mirror → winget-pkgs folder; Confluent → kafka.apache.org 4.3 design page (also added to lesson 8 `sources`); duplicate subprocess / RFC 9110 rows merged; AWS ×2, Kleppmann blog and http.dev typed "background" (lesson source titles too). No localhost URLs.
- **F07** `validation.pendingCi` on lessons 1, 4, 7, 9, 10, 11.
- **F08** `seeAlso` on L100 #2, #3, #5 and L200 #8, #11 (term "idempotent consumer").
- **F18** `subprocess.run/Popen(text=True)` now set `encoding="utf-8", errors="replace"` (lab 1 test_lab.py and try_it.py, lab 7 etcd_equivalent.py).
- **F21** Lesson 1 slimmed (hands-on ~1,960 → 1,685 words): container and two-machine steps, firewall rules and runtime table moved to `documentation/OPTIONAL-SETUP.md`; lab 1 README 826 → 533 words. Lesson 4 is now this topic's largest (1,996 hands-on words) because it carries two learning tools.
- **F27** `__pycache__` folders deleted; no logs in the topic.
- **F01** Status line added to README.

### Recorded, not fixed
- **F09** Concept share fell again with the new `learningTools` / `seeAlso` fields: L100 `concept 1484 hands-on 9554 share 13%` (was 14%), L200 `concept 1934 hands-on 8831 share 18%` (was 19%). Notes are not padded (user decision: hands-on leads).
- **F01** CI workflow (`.github/`, not edited here) is still unexecuted; it does not yet run `test_serve_realtime.py` explicitly, but unittest discovery in lab 11 picks it up (8 tests).
- **F06 (research logs)** `research/L100-evidence.md` and `L200-evidence.md` still mention winstall.app and Confluent as what was consulted at the time; they are history, not sources.

### Learning tools — not run here
- Every `learningTools` exercise is pending a manual run (Toxiproxy, Jaeger, Maelstrom, RabbitMQ, NATS, k6, Grafana are not installed). `expected` values quote the lab's real output; nothing was observed in the tools.
- Lesson 11 k6: `serve_realtime.py --check` (Python, same open-model load) ran twice: 200=24, 429=76, 0 missing Retry-After; k6 should match but was not run. Timing-based: on a slow machine the split can shift by one or two requests.
- Jaeger exercises need `pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-http` (package names from the OTel exporters page); the span-wrapping code is left to the learner.
- Toxiproxy: CLI `create` / `toxic add -t … -a …` syntax is from the README; the toxicity value is set through the HTTP API because the CLI flag for it was not verified (the CLI source page could not be fetched).
- Maelstrom on Windows (WSL2 assumed), NATS server on Windows, RabbitMQ's Erlang prerequisite on Windows: unverified (catalog gaps). RabbitMQ's exact delivery count before dead-lettering with delivery-limit 3 is left for the learner to observe.

### L300 candidates (old L100 `next` proposals, not built)
Health checks and failure detectors · API contracts / RPC frameworks (IDLs, versioning, streaming) · deadline propagation and load shedding · circuit breakers, hedged requests, adaptive throttling · transactional outbox (see application-architecture L200 #9) · vector clocks and version vectors.

## L300 (2026-10-28, L300-SPEC)
### Sizes and share
- **Concept share** (spec script on `content/L300.json`): `concept 2699 hands-on 12868 share 17%` (user target 30-35%). Notes are 505-550 words (`wc -w`), i.e. at full length; not padded. Hands-on is dominated by the exact-copy `code` fields and the new L300 fields (`failureLab`, `tradeOffs`, 5-7 item `codeWalkthrough`, `learningTools`, one `agentAssist`).
- **Main lab files** are 62-126 lines (spec ~60-120): `raft.py` is now 113 (was 137; the narrated demo moved to `helpers.demo()`, output byte-identical, R3-10). `partition.py` 126 stays over, because lab 13 carries the proxy, storage and node in one file; plumbing already lives in `helpers.py` / `checker.py`.

### Not run here (pending-ci or manual)
- **CI**: the L300 jobs added to `.github/workflows/labs.yml` (matrix + `otel`) have not run; macOS / Windows are `expected`.
- **Lesson 15 `otel_equivalent.py`** (OpenTelemetry api/sdk/exporter 1.45.1, pins checked on PyPI 2026-10-28): not run — no PyPI access in the sandbox. Import paths come from the OTel docs and source (`TraceContextTextMapPropagator`, `InMemorySpanExporter`, `OTLPSpanExporter`); the `--otlp` export to Jaeger is manual.
- **Learning tools** (Maelstrom 12/13, Toxiproxy 13, Jaeger + Grafana 15, k6 + Grafana 16): not installed; every `expected` quotes the lab's own output. Lesson 16: `serve_realtime.py --check` ran twice (bounded: 200=780, 503=420, p99 193 ms; unbounded: 200=1200, p99 3787 ms) as the k6 cross-check — timing-based.
- **Agent assist (lesson 13)** ran only against the vendored fake model server (new rule `[[PARTITION-HISTORY]]`, documented in its header; `labs/_shared/local_agent` tests still pass). No real model was run.
- **Maelstrom on Windows**: catalog says partial (WSL2 likely, unverified).

### Simplifications (by design; stated in the READMEs)
- **Raft (12)**: in-process, no disk/fsync (a crash keeps term, vote and log as if persisted), no snapshots, membership changes, PreVote, CheckQuorum or client redirects. The failure lab forces the stale node's timer to fire first; tryIt 2 shows the natural rate (11 of 20 seeds).
- **Partitions (13)**: the proxy is in-process on simulated ticks (not TCP); the lease store is an in-process copy of lesson 7's rules. The checker is exhaustive (fine for ~10 operations) and drops failed operations; indeterminate (timed-out) operations are not modelled.
- **Sagas (14)**: in-memory services and saga log; no isolation countermeasures beyond the PENDING state. Learning tool (update pass): Temporal CLI dev server — manual; the exercise pins temporalio 1.34.0 (PyPI, checked 2026-10-28; licence not shown on the fetched page, not installed here).
- **Tracing (15)**: real HTTP and real sleeps, so durations vary by run (this sandbox was slow: `/authorize` measured 60-95 ms for 60 ms of work). Ids come from a seeded RNG for reproducible output — the W3C spec recommends random ids; production must use a CSPRNG. Version handling follows W3C §3.2.4 (higher versions keep their first four fields; `ff` and extra fields on 00 are invalid) and the incoming trace-flags pass on unchanged (R3-12). No client spans, no sampling decision of its own, no tracestate.
- **Backpressure (16)**: discrete-event simulation; Retry-After is always 1 s with a 40-request bound. `load_test.js` has no thresholds (the `expected_response` tag syntax was not re-verified this session).

### Review notes
- L200 #11 `next` now points to L300 #12 (L300-SPEC), and so does L200 #7 (its old proposal, Raft, is now lesson 12). L200 #8-10 `next` now point at built L300 lessons (update pass, R3-05); their original proposals are listed under "L400 candidates" below.
- The storage mount returned `Input/output error` on in-place writes to existing files (documentation, L200.json, labs.yml, primer); those files were rewritten fresh (deleted and recreated with the full new content).

## L300 update pass (2026-10-28, UPDATE-L300-SPEC; review findings R3-xx)
### Fixed here
- **R3-12** `tracing.py` / `solution_tracing.py`: outgoing `traceparent` carries the incoming trace-flags (a trace the service starts gets `01`); the parser follows §3.2.4 for higher versions. New tests `test_sampled_flag_is_propagated_unchanged` and `test_versions_w3c_3_2_4` (lab 15: 11 tests); lesson troubleshooting has a sampling line. Seeded ids and README outputs unchanged.
- **R3-10** `raft.py` 137 → 113 lines (demo in `helpers.demo()`).
- **R3-04** `seeAlso` added: L300 #15 → ai-agents L300 #13; #16 → application-architecture L300 #13 and #15; #13 → application-architecture L300 #13 (same Toxiproxy toxics); #14 → ai-agents L300 #15 (idempotent refund); L100 #4 → ai-agents L300 #14. #14 → application-architecture L200 #9 (outbox) already existed with the exact title. Back-links live in those topics' files (not edited here). simulation L300 #16 was not linked: the queue overlap is already covered by simulation L200 #8.
- **R3-05** L200 #8 → L300 #14, #9 → L300 #12, #10 → L300 #13 (exact titles).
- **R3-06** already met: every L300 build-task test has `BUILD_TARGET=mine`, the lab files are unfixed; fail-before re-run in this pass (12: 3 failures, 13-16 as in the READMEs).
- **R3-13** L100 #6: Wikipedia → Lamport's own PDF. L300 sources were already primary (W3C, Raft paper, Sagas paper, RFC 9110); microservices.io and Kleppmann's blog stay typed "background".
- **R3-14** concept share per level reported in `documentation/README.md` (L100 13.4%, L200 17.8%, L300 16.8%).
- Tools (proposal): L300 #14 Temporal CLI dev server + Web UI; L300 #16 k6's built-in web dashboard added to the Grafana k6 exercise, Grafana OSS marked first to drop.

### Recorded, not fixed
- **R3-20** Maelstrom's `windows` field in L300 #12/#13 still reads "partial — No official statement; WSL2 likely (unverified)": install lines must come from the catalog, which is read-only here. Also catalog-owned: the Toxiproxy Mac line's `brew tap shopify/shopify` (toxiproxy is in homebrew-core). Fix both in `shared/` and re-copy.
- **R3-01** still nothing run on macOS/Windows; all learning-tool exercises (incl. Temporal and the k6 dashboard) are manual.
- k6 web dashboard: the 2 s period is chosen so the 10 s test draws graphs (catalog: graphs need > 3 × period); not run.

### L400 candidates (unbuilt L200 `next` proposals)
Total-order broadcast and Kafka-style partitioned logs with exactly-once pipelines (old L200 #8) · quorum replication on the ring: N, R, W and read repair (old #9) · replicated caches and read-your-writes (old #10).

## L400 (2026-10-28, L400-SPEC)
### Sizes and share
- **Concept share** (spec script on `content/L400.json`): `concept 3938 hands-on 19639 share 16.7%` (user target 35-40%). Notes are 635-749 words for lessons 17-21 and 506 for the capstone (`wc -w`), i.e. within the spec range, not padded; labs were not cut. The exact-copy `code` fields and the new L400 fields (`designBrief`, `options`, `fitnessFunction`, `scalingLimits`, capstone `milestones`/`rubric`) carry most hands-on words.
- **Main lab files** are 99-141 lines; the capstone's `pipeline.py` is 152 (spec "~150"; plumbing is already split into outbox.py, checks.py, reuse.py, chaos_campaign.py).

### Not run here (pending-ci or manual)
- **CI**: new jobs in `.github/workflows/labs.yml` (`python-labs-l400`, `capstone`, `automerge`, `tla`) have not run. `kb/.github/` was not edited: run `python tools/sync_root_ci.py` to regenerate the root workflow (`--paths` reported 0 missing paths for this topic). The major versions `actions/setup-node@v6` and `actions/setup-java@v5` were not re-verified in this pass.
- **Automerge (lesson 18)**: `automerge_equivalent.mjs` + `package.json` (`@automerge/automerge` 3.3.2, MIT, from npm) not run - npm is not reachable from the sandbox. `from`, `clone`, `change`, `merge` are from the npm README; `Counter`, `.value`, `toJS` and `getConflicts` follow the Automerge JS API but were not re-checked on a fetched page.
- **TLC (lesson 21)**: no Java in the sandbox. `Election.tla` mirrors `modelcheck.py`; whether TLC reports the same 1,853 distinct states for the fixed config is unverified. The CI job pins tla2tools.jar v1.7.4 and checks the SHA-1 published on the release page.
- **Learning tools**: every L400 exercise (Maelstrom #17/#18/#21, Toxiproxy + k6 #19/#20, Jaeger + Temporal #22) is manual and unrun; `expected` quotes the lab's own output. Maelstrom CLI flags follow its docs as in L300; the Toxiproxy `reset_peer` attribute and toxicity-by-API follow the README as in L300 #13.
- **Agent assist (capstone)**: fake model server only (new rule `[[CHAOS-SCORECARD]]`, documented in its header; `labs/_shared/local_agent` tests still pass). No real model run.
- **macOS / Windows**: all six lessons `expected`.

### Simplifications (by design; stated in the READMEs)
- **17**: one writer per key (versions = write order); replicas keep max(version); latencies are assumptions with a 5% slow tail. The fast anomaly checks are valid for single-writer registers and were cross-checked against the L300 #13 exhaustive checker (300 histories).
- **18**: sync is a function call with seeded duplicates; no tombstone GC; LWW timestamps are Lamport-style from local state.
- **19**: latency legs are summed analytically with seeded jitter; failure detection = a fixed 1-2 s election timeout; client redirects are not modelled beyond rejecting writes; false elections from WAN jitter are not modelled (tryIt 2 says so).
- **20**: faults are injected into in-process copies of the L300 labs; Raft experiments take down one node at a time.
- **21**: request and reply are one step; bounds 3 nodes, terms <= 2; `lincheck.py` checks one register (no P-compositionality, no indeterminate operations).
- **22**: simulated ticks; the gateway bound is 1 until the first config commit; Retry-After from L300 #16's `admit()` is always 1 tick (it is computed for that lab's 400 req/s capacity); no persistence.

### Review notes
- NIST SP 800-34: the fetched PDF text stopped before section 3.2, so RTO/RPO are paraphrased, not quoted. Jepsen's consistency page returned its overview only.
- Lesson 19's us p99 sits close to its budget (max 339.2 ms over seeds 19-38 vs 350 ms); stated as a scaling limit and guarded by the fitness test.
- Lesson 21 prints timings; they vary run to run (README and tryIt say so; tests assert verdicts and counts only). On this storage mount imports are slow (a test file can take 15-60 s to start); compute is milliseconds.
- `CONCEPTS-PRIMER.md`: the L400 concept-map line now matches the lessons built; "Byzantine faults" was in the old proposal and is listed below as a candidate.
- R3-20: L400 Maelstrom `windows` lines use the catalog's correction ("no native Windows support; WSL 2 unverified"); the Toxiproxy Mac line still copies the catalog's `brew tap` form.
- Full-topic test run (L100-L400 + capstone + shared helper, 23 suites, 179 tests): all pass. When all 23 suites ran in parallel, L300 #16 `test_serve_realtime` (wall-clock load test, not changed here) failed once (`0 not greater than 0` 503s); it passed 3 of 3 runs on its own, as did the other real-time suites (L100 #2, L200 #10, L300 #15). Same class as R3-02: wall-clock tests are load-sensitive.
- seeAlso: within-topic L400 links have reverse links (L300 #12, #13, #14, #16 updated; L300 #16 `next` now names L400 #17). Cross-topic links are one-way (allowed by L400-SPEC).

### L400 candidates (further study; the capstone's `next`)
Byzantine faults and BFT replication · transactions across shards (2PC over consensus groups) · version vectors and causal+ consistency · sequence/text CRDTs and CRDT garbage collection · per-shard leaders placed near their users · deterministic simulation testing of the real code · membership changes (joint consensus) in the model checker · total-order broadcast and Kafka-style partitioned logs with exactly-once pipelines (old L200 #8) · replicated caches and read-your-writes sessions (old L200 #10).

## L500 (2026-10-30, L500-SPEC)
### Scope and sizes
- 5 lessons (23-27), 12 theorems (4 per foundations lesson) each with a seeded numerical check, 36 problems (8/8/8/6/6), 1 case study, 2 readings; concept notes 999 / 1,120 / 1,011 / 788 / 641 words (`wc -w`; spec 900-1300, 700-1000, 500-800). L500 qbank 44 questions; concept inventory 15.
- The 14-week plan in `content/assessment/syllabus.md` was written from L500-SPEC's description; the professor's pedagogy review it refers to is not in this repository.

### What the numerical checks do and do not show
- They corroborate, they do not prove. T24.1 checks a bounded *family* of two-generals protocols (alternating messengers, threshold decisions, M <= 6), not all protocols. T24.2 *illustrates* FLP with one adversarial schedule on our Paxos; the theorem's proof is FLP 1985 (sketched in the lesson). T24.4's Paxos check is randomised exploration (3,000 runs of 250 steps, 3 acceptors), not exhaustive model checking.
- T23.4 uses Pareto delays as the 'no upper bound' model; real networks are bounded in practice, which is exactly why partial synchrony is the working assumption.
- T25.4's simulated closed system is a machine-repairman model with load-dependent service, not literally a USL: the fitted peak (15.3) differs from the measured one (13). The unconstrained fit gave a negative sigma, so the fit constrains sigma >= 0 (stated in the code and the lesson).
- M/M/1 at rho = 0.9 converges slowly (W 9.838 vs 10 over 400,000 customers); the lesson says so.

### Sources not fully read
- **Directive (EU) 2023/1791 Art. 12**: the fetched EUR-Lex page showed only the header and recitals; the 500 kW threshold and reporting duty were confirmed only by secondary compliance summaries, so the lesson states the duty at policy level ('above a power threshold') and cites the Directive only as context.
- **GDPR Arts. 33 and 44-49**: the EUR-Lex fetch stopped in the recitals. Art. 32 wording is from the legislation.gov.uk copy of the adopted text; the transfer rules are stated as the CJEU press release 91/20 summarises them. Lesson 26 is policy-level, not legal advice.
- **Dwork, Lynch & Stockmeyer 1988; Alpern & Schneider 1985; Little & Graves 2008; Amdahl 1967; IEA; CJEU 91/20**: read via search-result extracts (abstract, definitions, key paragraphs), not the full documents.
- **ABET**: CAC 2026-27 and EAC 2025-26 wording verified; the EAC 2026-27 criteria were not fetched.

### Not run here
- macOS / Windows (all L500 lessons `expected`); new CI jobs `python-labs-l500` and `l500-checks` have not run. `kb/.github/` was not edited: run `python tools/sync_root_ci.py` to regenerate the root workflow.
- `tools/check_qbank.py` reads L100-L400 only; L500 is validated by `research/check_l500_qbank.py` (same rules + inventory checks). The concept inventory reuses lesson 23 as its `lesson` per the spec although it spans L100-L500.

### Review notes
- Correct option is the longest in 14/44 L500 questions and 5/15 inventory items (after lengthening distractors; first draft 23/44 and 11/15).
- Type mix L500: concept 17, calculation 10, code-reading 6, debugging 3, scenario 7, design 1 (calculation 23%, slightly above QBANK-SPEC's 10-20%: the theory lessons are numeric).
- `next` of the capstone (#22) now points to L500 #23; the L400 further-study list is unchanged below.
