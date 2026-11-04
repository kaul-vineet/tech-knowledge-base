# Verified resources — Distributed Systems L100

All URLs were retrieved on 2026-10-28 with web_fetch. Score = implementable + current + authoritative + open + transferable + right depth (0-2 each). Kept if ≥ 8/12. "Role" = *primary* (listed in the lesson's `sources`, max 4 per lesson) or *supporting* (used to check an API, an equivalents line, or a CI/image pin). Licence "not shown on page" means the licence was not visible in the retrieved text and is not claimed here (see KNOWN-GAPS).

| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| Python docs: http.server | https://docs.python.org/3/library/http.server.html | docs | not shown on page (python.org docs) | Python 3.15.2 docs; checked 2026-10-28 | 11 | 1, 2 (primary) |
| Python docs: urllib.request | https://docs.python.org/3/library/urllib.request.html | docs | not shown on page | Python 3.15.2 docs; 2026-10-28 | 11 | 2, 3 (primary) |
| Python docs: time | https://docs.python.org/3/library/time.html | docs | not shown on page | Python 3.15.2 docs; 2026-10-28 | 10 | 2, 6 (primary) |
| Python docs: random | https://docs.python.org/3/library/random.html | docs | not shown on page | Python 3.15.2 docs; 2026-10-28 | 10 | 3, 4, 5 (supporting: seeding/reproducibility) |
| Docker Docs: How Compose works | https://docs.docker.com/compose/intro/compose-application-model/ | docs | not shown on page | 2026-10-28 | 9 | OPTIONAL-SETUP.md (supporting; vendor docs for the Compose file model) |
| Docker Hub: python official image | https://hub.docker.com/_/python | docs | per-image licences (page says user must check) | tag 3.12.16-slim listed; 2026-10-28 | 9 | 1 (supporting: image pin) |
| Kleppmann, Distributed Systems lecture notes (Cambridge, 2025/26) | https://www.cl.cam.ac.uk/teaching/2526/ConcDisSys/dist-sys-notes.pdf | course | CC BY-SA (stated in notes) | 2025/26 edition (2026/27 also seen); 2026-10-28 | 10 | 1, 2, 5 (primary) |
| Amazon Builders' Library: Timeouts, retries, and backoff with jitter | https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/ (served from builder.aws.com) | background (vendor engineering article) | not shown on page | published 2019-12-05; 2026-10-28 | 9 | 3, 4, 5 (primary) |
| gRPC docs: Deadlines | https://grpc.io/docs/guides/deadlines/ | docs | not shown on page | last modified 2025-07-07; 2026-10-28 | 10 | 3, 6 (primary) |
| Go net/http package | https://pkg.go.dev/net/http | docs | BSD-3-Clause (shown) | go1.27.3; 2026-10-28 | 10 | 3 (primary), 1, 2 (supporting: equivalents) |
| MDN: AbortSignal.timeout() | https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static | docs | not shown on page | last modified 2026-09-01; 2026-10-28 | 10 | 3 (supporting: Node equivalent) |
| AWS Architecture Blog: Exponential Backoff and Jitter | https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/ | background (vendor blog) | not shown on page | 2015-03-04, updated May 2023; 2026-10-28 | 9 | 4 (primary) |
| aws-arch-backoff-simulator (backoff_simulator.py) | https://github.com/aws-samples/aws-arch-backoff-simulator/blob/master/src/backoff_simulator.py | repo | LICENSE file present, not read | master; 2026-10-28 | 9 | 4 (supporting: exact jitter formulas) |
| gRPC docs: Retry | https://grpc.io/docs/guides/retry/ | docs | not shown on page | last modified 2025-11-26; 2026-10-28 | 11 | 4 (primary) |
| Google SRE book: Handling Overload | https://sre.google/sre-book/handling-overload/ | docs (book chapter) | not shown on page | 2026-10-28 | 9 | 4 (primary) |
| Tenacity documentation | https://tenacity.readthedocs.io/en/latest/ | docs | Apache 2.0 (stated) | latest; 2026-10-28 | 9 | 4 (supporting: equivalents) |
| Resilience4j: Retry | https://resilience4j.readme.io/docs/retry | docs | not shown on page | page "updated over 3 years ago"; 2026-10-28 | 8 | 4 (supporting: equivalents) |
| Polly: Retry resilience strategy | https://www.pollydocs.org/strategies/retry.html | docs | not shown on page | 2026-10-28 | 10 | 4 (supporting: equivalents) |
| IETF draft-ietf-httpapi-idempotency-key-header-08 | https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ | spec (Internet-Draft) | IETF Trust; code components Revised BSD (stated) | -08, 2026-10-22, expires 2027-04-25; 2026-10-28 | 11 | 5 (primary) |
| Lamport (1978), Time, Clocks, and the Ordering of Events (author's page) | https://www.microsoft.com/en-us/research/publication/time-clocks-ordering-events-distributed-system/ | spec (paper page) | © ACM 1978 (stated) | CACM 21(7); 2026-10-28 | 8 | 6 (primary) |
| Lamport (1978), Time, Clocks, and the Ordering of Events (author's PDF) | https://lamport.azurewebsites.net/pubs/time-clocks.pdf | paper | © ACM 1978; fair use for teaching stated | CACM 21(7); fetched 2026-10-28 (IR1, IR2, total-order tie-break) | 12 | 6 (primary; replaces Wikipedia: Lamport timestamp, R3-13) |
| actions/setup-python | https://github.com/actions/setup-python | repo | MIT (stated) | README shows @v7 (and actions/checkout@v7); 2026-10-28 | 10 | CI workflow (supporting) |
| RFC 9110 HTTP Semantics | https://www.rfc-editor.org/rfc/rfc9110.html | spec | IETF Trust; code components Revised BSD (stated) | June 2022 (STD 97); 2026-10-28 (fetched text stopped before §10, see KNOWN-GAPS) | 10 | 2 (sources; inRealSystems), 11 (primary: Retry-After §10.2.3) |
| Envoy: Router filter | https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/router_filter | docs | not shown on page | envoy 1.41.0-dev docs; 2026-10-28 | 11 | 2, 3, 4 (sources; inRealSystems) |
| Kubernetes: Configure Liveness, Readiness and Startup Probes | https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ | docs | not shown on page | last modified 2026-06-30; 2026-10-28 | 10 | 1 (sources; inRealSystems) |
| Apache Kafka: Introduction | https://kafka.apache.org/43/getting-started/introduction/ | docs | not shown on page | Kafka 4.3 docs; 2026-10-28 | 8 | none since the 2026-10-28 rebalance (was: primer application areas; Kafka was cut from the trimmed primer) |
| Automerge binary format spec | https://automerge.org/automerge-binary-format-spec/ | spec | not shown on page | draft; 2026-10-28 | 9 | 6 (sources; inRealSystems); primer |
| Apache Cassandra: CQL Data Manipulation | https://cassandra.apache.org/doc/latest/cassandra/developing/cql/dml.html | docs | not shown on page | 5.0 docs (page says prerelease); 2026-10-28 | 9 | 5, 6 (sources; inRealSystems); primer |

**Count kept: 29** (28 rows in this table since the duplicate subprocess row was merged into the platform table on 2026-10-28) (23 from the lab build: 15 primary in at least one lesson, 8 supporting-only; plus 6 added for the concepts layer on 2026-10-28). Concept notes also re-use earlier sources; see `research/L100-evidence.md` → Concepts layer. Dropped sources are listed in `research/L100-evidence.md`. Since the 2026-10-28 rebalance, lessons list more than 4 `sources` because the concept notes' "Go deeper" links were merged into them (lesson `sources` now hold 4–6 entries).

## Added for Mac mini + Windows and agent assist (2026-10-28, PLATFORM-AGENT-SPEC)

| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| Microsoft Learn: Using SO_REUSEADDR and SO_EXCLUSIVEADDRUSE | https://learn.microsoft.com/en-us/windows/win32/winsock/using-so-reuseaddr-and-so-exclusiveaddruse | docs | not shown on page | last updated 2022-06-13; 2026-10-28 | 10 | 1 (primary: Windows exclusive bind) |
| Microsoft Learn: Windows Sockets Error Codes | https://learn.microsoft.com/en-us/windows/win32/winsock/windows-sockets-error-codes-2 | docs | not shown on page | last updated 2021-08-19; 2026-10-28 | 9 | 1, 2 (supporting: WSAEADDRINUSE 10048, WSAECONNREFUSED 10061) |
| Microsoft Learn: New-NetFirewallRule | https://learn.microsoft.com/en-us/powershell/module/netsecurity/new-netfirewallrule | docs | not shown on page | 2026-10-28 | 10 | 1 (supporting: LAN step firewall rule) |
| Apple Support: Change Firewall settings on Mac | https://support.apple.com/guide/mac-help/change-firewall-settings-on-mac-mh11783/mac | docs | not shown on page | macOS 27 guide; 2026-10-28 | 8 | 1 (supporting: LAN step) |
| Python docs: venv (activation per platform, ExecutionPolicy note) | https://docs.python.org/3/library/venv.html | docs | not shown on page | Python 3.15.2 docs; 2026-10-28 | 11 | 1 (supporting: mac/windows setup) |
| Python docs: subprocess (Popen, terminate/kill) | https://docs.python.org/3/library/subprocess.html | docs | not shown on page | Python 3.15.2 docs; 2026-10-28 | 11 | 1 (primary: process per node; terminate = SIGTERM / TerminateProcess) |
| Homebrew: python@3.12 | https://formulae.brew.sh/formula/python@3.12 | docs | formula Python-2.0 | stable 3.12.16, Apple-silicon bottles; 2026-10-28 | 9 | 1 (supporting: macOS install) |
| Homebrew: docker-compose | https://formulae.brew.sh/formula/docker-compose | docs | Apache-2.0 | 5.6.1; 2026-10-28 | 9 | 1 (supporting: Colima path, cliPluginsExtraDirs) |
| winget-pkgs manifests: Python.Python.3.12 | https://github.com/microsoft/winget-pkgs/tree/master/manifests/p/Python/Python/3/12 | repo (official winget manifests) | MIT (repo) | version folders 3.12.0–3.12.10; 2026-10-28 | 10 | 1 (supporting: winget id; replaces the winstall.app mirror, F06) |
| Podman: Installation | https://podman.io/docs/installation | docs | not shown on page | 2026-10-28 | 10 | 1 (supporting: podman machine on macOS/Windows) |
| Podman docs: podman-compose (podman compose) | https://docs.podman.io/en/latest/markdown/podman-compose.1.html | docs | not shown on page | latest; 2026-10-28 | 10 | OPTIONAL-SETUP.md (supporting: compose provider) |
| Podman Desktop: Windows / macOS install | https://podman-desktop.io/docs/installation/windows-install | docs | not shown on page | 2026-10-28 (macOS page also read) | 9 | 1 (supporting: winget RedHat.Podman-Desktop, WSL 2, 6 GB RAM) |
| PyPI: podman-compose | https://pypi.org/project/podman-compose/ | repo | GPL-2.0-only | 1.6.0 (2026-06-03); 2026-10-28 | 9 | 1 (supporting: CI pin, brew/pip install) |
| Colima README + FAQ | https://github.com/abiosoft/colima/blob/main/docs/FAQ.md | repo | MIT | main; 2026-10-28 | 9 | 1 (supporting: docker runtime, /Users/$USER bind mounts, VM defaults) |
| Rancher Desktop: Installation | https://docs.rancherdesktop.io/getting-started/installation/ | docs | not shown on page | latest; 2026-10-28 | 9 | 1 (supporting: dmg/msi, WSL, bundled compose + nerdctl) |
| Docker Docs: Docker Desktop license agreement | https://docs.docker.com/subscription-billing/desktop-license/ | docs | n/a (licence terms page) | 2026-10-28 | 8 | 1 (supporting: one equivalents line) |
| Ollama docs: Hardware support (gpu.mdx) | https://github.com/ollama/ollama/blob/main/docs/gpu.mdx | repo | LICENSE file present, not read | main; 2026-10-28 | 9 | 4 (supporting: Metal / NVIDIA / AMD / CPU) |
| Ollama docs: OpenAI compatibility | https://github.com/ollama/ollama/blob/main/docs/api/openai-compatibility.mdx | repo | LICENSE file present, not read | main; 2026-10-28 | 10 | 4 (primary: /v1/chat/completions, num_ctx via Modelfile) |

Dropped: third-party Ollama setup blogs (secondary, partly commercial) — official Ollama docs used instead; Stack Overflow answer on `os.kill` on Windows used only as a pointer, the claim is backed by the subprocess docs (`send_signal`: SIGTERM is an alias for terminate()).

## L200 additions (lessons 7-11, retrieved 2026-10-28)
Same columns and rubric. "via search" = the page text came back through web_search rather than web_fetch.

| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| Kleppmann: How to do distributed locking | https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html | background (blog) | not shown on page | 2016-02-08; 2026-10-28 | 10 | 7 (primary: fencing tokens) |
| etcd docs v3.6: Interacting with etcd | https://etcd.io/docs/v3.6/dev-guide/interacting_v3/ | docs | not shown on page | last modified 2026-04-13; 2026-10-28 | 11 | 7 (primary: leases, revisions) |
| etcd docs v3.6: Why gRPC gateway | https://etcd.io/docs/v3.6/dev-guide/api_grpc_gateway/ | docs | not shown on page | last modified 2026-01-23; 2026-10-28 | 10 | 7 (primary: txn compare / CAS) |
| etcdctl README | https://github.com/etcd-io/etcd/blob/main/etcdctl/README.md | repo | Apache-2.0 (repo LICENSE listed, not read) | main; 2026-10-28 | 10 | 7 (primary: lease, txn grammar, elect) |
| etcd releases | https://github.com/etcd-io/etcd/releases | repo | Apache-2.0 (repo) | v3.7.3 latest, v3.6.16; 2026-10-28 | 9 | 7 (supporting: image + etcdctl pin) |
| etcd v3election.swagger.json (via search) | https://github.com/etcd-io/etcd/blob/main/Documentation/dev-guide/apispec/swagger/v3election.swagger.json | repo | Apache-2.0 (repo) | main; 2026-10-28 | 8 | 7 (supporting: /v3/election/* paths) |
| Kubernetes docs: Leases | https://kubernetes.io/docs/concepts/architecture/leases/ | docs | not shown on page | last modified 2026-03-31; 2026-10-28 | 10 | 7 (primary) |
| NATS docs: Ack responses and redelivery (via search) | https://docs.nats.io/learn/jetstream/acknowledgment | docs | not shown on page | 2026-10-28 | 10 | 8 (primary: AckWait 30 s, ack/nak/term) |
| NATS docs: Pull consumers in depth | https://docs.nats.io/learn/jetstream/pull-consumers | docs | not shown on page | 2026-10-28 | 9 | 8 (primary) |
| RabbitMQ docs: Quorum Queues | https://www.rabbitmq.com/docs/quorum-queues | docs | not shown on page | version 4.4; 2026-10-28 | 11 | 8 (primary: delivery limit 20, DLX) |
| Apache Kafka 4.3 docs: Design — Message Delivery Semantics | https://kafka.apache.org/43/design/design/ | docs | not shown on page | 4.3 docs; 2026-10-28 | 10 | 8 (sources; Kafka equivalents line: commit after processing = at-least-once, before = at-most-once). Replaces the Confluent vendor page (F15). |
| Apache Cassandra docs: Dynamo | https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html | docs | not shown on page | 5.0 docs (prerelease banner); 2026-10-28 | 11 | 9 (primary) |
| Nishtala et al., Scaling Memcache at Facebook (NSDI'13) | https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf | paper | © USENIX (open access) | NSDI 2013; 2026-10-28 | 10 | 9, 10 (primary) |
| Go package golang.org/x/sync/singleflight | https://pkg.go.dev/golang.org/x/sync/singleflight | docs | BSD-3-Clause (shown) | v0.24.0; 2026-10-28 | 10 | 10 (primary) |
| Valkey docs: SET | https://valkey.io/commands/set/ | docs | not shown on page | 2026-10-28 | 11 | 10 (primary), 7 (equivalents) |
| Valkey docs: Serialization protocol specification | https://valkey.io/topics/protocol/ | spec | not shown on page | 2026-10-28 | 11 | 10 (primary: RESP2 client) |
| Docker Hub: valkey/valkey | https://hub.docker.com/r/valkey/valkey | docs | per-image licences (page says user must check) | tag 9.1.3 = latest; 2026-10-28 | 9 | 10 (supporting: CI image pin) |
| Valkey docs: INCR (rate limiter pattern) | https://valkey.io/commands/incr/ | docs | not shown on page | 2026-10-28 | 9 | 11 (supporting: equivalents) |
| RFC 6585 Additional HTTP Status Codes | https://www.rfc-editor.org/rfc/rfc6585.html | spec | IETF Trust; code components Simplified BSD (stated) | April 2012; 2026-10-28 | 11 | 11 (primary: 429) |
| MDN: Retry-After header | https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Retry-After | docs | not shown on page | last modified 2025-11-21; 2026-10-28 | 10 | 11 (primary: both forms) |
| http.dev: Retry-After (via search) | https://http.dev/retry-after | background (third-party reference) | not shown on page | updated 2026-08-17; 2026-10-28 | 8 | 11 (supporting cross-check) |
| Envoy docs: Local rate limit filter | https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/local_rate_limit_filter | docs | not shown on page | 1.41.0-dev; 2026-10-28 | 11 | 11 (primary) |
| NGINX docs: ngx_http_limit_req_module | https://nginx.org/en/docs/http/ngx_http_limit_req_module.html | docs | not shown on page | 2026-10-28 | 10 | 11 (primary) |
| Go package golang.org/x/time/rate | https://pkg.go.dev/golang.org/x/time/rate | docs | BSD-3-Clause (shown) | v0.16.0; 2026-10-28 | 10 | 11 (supporting: equivalents) |

Dropped (L200): kafka.apache.org 4.3 introduction (fetched page lacked the delivery-semantics section), Microsoft Learn Dev Proxy Retry-After page (vendor tool), etcd `rpc.swagger.json` (fetch returned nothing — the lease/election JSON paths were therefore not used; the etcd script drives etcdctl).

## Tools/review pass (2026-10-28, UPDATE-TOOLS-REVIEW-SPEC)
Changes above: winstall.app mirror → official winget-pkgs folder (F06); Confluent page → kafka.apache.org (F15); duplicate subprocess and RFC 9110 rows merged (F16); blogs and vendor engineering articles typed "background" (AWS ×2, Kleppmann blog, http.dev); Docker/Podman compose pages now back `OPTIONAL-SETUP.md` instead of lesson 1. No localhost URLs are listed.

Learning-tool facts (licence, version, installs) come from `../../shared/LEARNING-TOOLS-CATALOG.md`. Pages fetched for the exercise wording:

| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| Jaeger docs: Getting Started | https://www.jaegertracing.io/docs/latest/getting-started/ | docs | not shown on page | 2.22 (last modified 2026-10-08); 2026-10-28 | 10 | 2, 4, 5 (learningTools: image, UI :16686, OTLP :4318) |
| OpenTelemetry Python: Exporters | https://opentelemetry.io/docs/languages/python/exporters/ | docs | not shown on page | last modified 2026-01-14; 2026-10-28 | 10 | 2, 4, 5 (learningTools: opentelemetry-exporter-otlp-proto-http, SDK set-up) |
| Toxiproxy README | https://github.com/Shopify/toxiproxy | repo | MIT | 2.13.0; 2026-10-28 | 11 | 3, 4 (learningTools: CLI create / toxic add, timeout and reset_peer toxics, toxicity field, API :8474) |
| Maelstrom docs: Getting Ready | https://github.com/jepsen-io/maelstrom/blob/main/doc/01-getting-ready/index.md | repo | EPL-1.0 (repo) | main; 2026-10-28 | 10 | 6 (learningTools: prerequisites, `./maelstrom test`, `serve`, store/latest) |
| Maelstrom docs: Gossip-Based Broadcast | https://github.com/jepsen-io/maelstrom/blob/main/doc/03-broadcast/01-broadcast.md | repo | EPL-1.0 (repo) | main; 2026-10-28 | 10 | 6 (learningTools: broadcast workload flags, messages.svg) |
| Grafana k6 docs: Constant arrival rate | https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/ | docs | not shown on page | latest; 2026-10-28 | 10 | 11 (learningTools + load_test.js options) |

## L300 (2026-10-28, L300-SPEC)
New sources for lessons 12-16 (research questions, candidates and quotes: `research/L300-evidence.md`).

| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| Ongaro & Ousterhout, In Search of an Understandable Consensus Algorithm (Extended Version) | https://raft.github.io/raft.pdf | paper | not shown on page | published 2014-05-20; 2026-10-28 | 12 | 12 (primary: Figure 2, 5.4.1, 5.4.2) |
| etcd-io/raft README | https://github.com/etcd-io/raft | repo | Apache-2.0 | main; 2026-10-28 | 11 | 12 (primary; equivalents), 13 (stale-read note) |
| Maelstrom docs: Chapter 6, Raft | https://github.com/jepsen-io/maelstrom/blob/main/doc/06-raft/index.md | repo | EPL-1.0 (repo) | main; 2026-10-28 | 9 | 12 (sources; learningTools) |
| Maelstrom docs: Workloads (lin-kv) | https://github.com/jepsen-io/maelstrom/blob/main/doc/workloads.md | repo | EPL-1.0 (repo) | main; 2026-10-28 | 10 | 13 (primary; learningTools) |
| Porcupine README | https://github.com/anishathalye/porcupine | repo | MIT | master; 2026-10-28 | 10 | 13 (primary; register histories used as test cases) |
| Garcia-Molina & Salem, Sagas (SIGMOD 1987; Cornell course copy) | https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf | paper | © ACM (course reading copy) | 1987; 2026-10-28 | 10 | 14 (primary) |
| microservices.io: Pattern: Saga | https://microservices.io/patterns/data/saga.html | background (pattern site with a course advert) | © Chris Richardson | 2026-10-28 | 8 | 14 (background: orchestration vs choreography, isolation) |
| W3C Trace Context (Recommendation) | https://www.w3.org/TR/trace-context/ | spec | W3C permissive document licence | REC 2021-11-23; 2026-10-28 | 12 | 15 (primary) |
| OpenTelemetry Python: Propagation | https://opentelemetry.io/docs/languages/python/propagation/ | docs | not shown on page | last modified 2026-01-14; 2026-10-28 | 10 | 15 (primary; otel_equivalent.py) |
| PyPI: opentelemetry-sdk | https://pypi.org/project/opentelemetry-sdk/ | docs (package index) | Apache-2.0 | 1.45.1 (2026-10-06); 2026-10-28 | 10 | 15 (pin) |
| PyPI: opentelemetry-api | https://pypi.org/project/opentelemetry-api/ | docs (package index) | Apache-2.0 | 1.45.1 (2026-10-06); 2026-10-28 | 9 | 15 (supporting: pin) |
| PyPI: opentelemetry-exporter-otlp-proto-http | https://pypi.org/project/opentelemetry-exporter-otlp-proto-http/ | docs (package index) | Apache-2.0 | 1.45.1 (2026-10-06); 2026-10-28 | 9 | 15 (supporting: pin, OTLPSpanExporter import path) |
| opentelemetry-python source: in_memory_span_exporter.py (via search) | https://github.com/open-telemetry/opentelemetry-python/blob/main/opentelemetry-sdk/src/opentelemetry/sdk/trace/export/in_memory_span_exporter.py | repo | Apache-2.0 | main; 2026-10-28 | 9 | 15 (supporting: InMemorySpanExporter import path) |
| Netflix concurrency-limits README | https://github.com/Netflix/concurrency-limits | repo | Apache-2.0 | main; 2026-10-28 | 10 | 16 (primary: Little's law, AIMD/Vegas/Gradient2) |

Already listed above and now also used in L300: Google SRE book, Handling Overload (16 primary: client-side throttling, overload); RFC 9110 (16: 503, Retry-After); Kleppmann, How to do distributed locking (13 background: fencing); Toxiproxy README (13: toxics, `enabled=false`, toxicity, API token); Jaeger Getting Started (15 learningTools); Grafana k6 Constant arrival rate (16 sources and learningTools). No duplicate rows were added.

Dropped (L300): Temporal docs "Detecting Workflow failures" (fetched page did not cover sagas or compensation); Knossos repository (not fetched — Porcupine's README and Maelstrom cover the checker).

## L300 update pass (2026-10-28, UPDATE-L300-SPEC)
| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| Grafana k6 docs: Web dashboard | https://grafana.com/docs/k6/latest/results-output/web-dashboard/ | docs | not shown on page | 2026-10-28 (`K6_WEB_DASHBOARD`, default 127.0.0.1:5665, `K6_WEB_DASHBOARD_EXPORT`, period 10s default, graphs only if duration > 3 × period) | 11 | 16 (learningTools, sources) |
| temporalio/cli README | https://github.com/temporalio/cli | repo | MIT (stated) | main; 2026-10-28 (`brew install temporal`, Windows amd64 archive, dev server UI :8233) | 10 | 14 (learningTools) |
| PyPI: temporalio | https://pypi.org/project/temporalio/ | docs (package index) | not shown in fetched text | 1.34.0; 2026-10-28 | 9 | 14 (learningTools pin) |
| W3C Trace Context §3.2.2.5.1 (sampled flag), §3.2.4 (versioning) | https://www.w3.org/TR/trace-context/ | spec | (row above) | REC 2021-11-23 | 12 | 15 (R3-12 fix; already listed) |

## L400 (2026-10-28, L400-SPEC)
| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| Abadi, Consistency Tradeoffs in Modern Distributed Database System Design (IEEE Computer 2012) | https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf | paper | not shown (author's copy) | 2012; 2026-10-28 | 12 | 17, 19 (primary: PACELC; quorum is not enough for linearizability) |
| DeCandia et al., Dynamo (SOSP 2007) | https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf | paper | ACM copy notice | 2007; 2026-10-28 | 11 | 17, 19 (primary: N, R, W; sloppy quorum) |
| Jepsen: Consistency models | https://jepsen.io/consistency | docs (reference guide) | not shown on page | 2026-10-28 | 9 | 17 (background) |
| Shapiro, Preguiça, Baquero, Zawirski, A comprehensive study of CRDTs (INRIA RR-7506) | https://perso.lip6.fr/Marc.Shapiro/papers/2011/Comprehensive-CRDTs-RR7506-2011-01.pdf | paper | not shown (author's copy) | 2011; 2026-10-28 | 12 | 18 (primary: G/PN-Counter, OR-Set, LWW, merge laws) |
| Kleppmann, Wiggins, van Hardenberg, McGranaghan, Local-first software (Onward! 2019) | https://www.inkandswitch.com/essay/local-first/ | paper / essay | not shown on page | 2019; 2026-10-28 | 10 | 18 |
| automerge/automerge repository | https://github.com/automerge/automerge | repo | MIT | Automerge 3 (main); 2026-10-28 | 11 | 18 (equivalent) |
| npm: @automerge/automerge | https://www.npmjs.com/package/@automerge/automerge | docs (package index) | MIT | 3.3.2 (≈2026-10-18); 2026-10-28 | 10 | 18 (pin for automerge_equivalent.mjs) |
| PyPI: automerge | https://pypi.org/project/automerge/ | docs (package index) | MIT | 0.1.2 stable (2022), 0.2.0.dev4 pre-release; 2026-10-28 | 6 | dropped (pre-release Python binding; JS package used) |
| Maelstrom workloads (g-counter, pn-counter, lin-kv) | https://github.com/jepsen-io/maelstrom/blob/main/doc/workloads.md | docs | EPL-1.0 (repo) | main; 2026-10-28 | 10 | 17, 18, 21 (learningTools; already used in L300) |
| NIST SP 800-34 Rev. 1, Contingency Planning Guide | https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final | standard (guideline) | US government work (not subject to copyright) | Rev. 1, updated 2010-11-11; 2026-10-28 | 9 | 19 (RTO/RPO terms; definition text not retrieved, see KNOWN-GAPS) |
| Principles of Chaos Engineering | https://principlesofchaos.org/ | spec (community principles) | not shown on page | last update 2019-03; 2026-10-28 | 10 | 20, 22 (primary) |
| Basiri et al., Chaos Engineering (IEEE Software 33(3), 2016) | https://arxiv.org/abs/1702.05843 | paper | arXiv licence | v1 2017; 2026-10-28 | 10 | 20 |
| chaos-mesh/chaos-mesh repository | https://github.com/chaos-mesh/chaos-mesh | repo | Apache-2.0 | master; CNCF incubating; 2026-10-28 | 9 | 20 (equivalent line only; not a learning tool) |
| anishathalye/porcupine README | https://github.com/anishathalye/porcupine | repo | MIT | master; 2026-10-28 | 11 | 21 (primary: algorithm, register example histories) |
| Lowe, Testing for Linearizability (CCPE 2017) | https://www.cs.ox.ac.uk/people/gavin.lowe/LinearizabiltyTesting/paper.pdf | paper | not shown (author's copy) | 2017; 2026-10-28 | 11 | 21 (primary: Wing & Gong graph search, complexity) |
| tlaplus/tlaplus releases | https://github.com/tlaplus/tlaplus/releases | repo (releases) | MIT (LICENSE) | v1.7.4 stable (2024-08-05), v1.8.0 pre-release (≈2026-10-25); 2026-10-28 | 11 | 21 (TLC equivalent; CI pin + SHA-1) |
| tlaplus/tlaplus LICENSE | https://github.com/tlaplus/tlaplus/blob/master/LICENSE | repo | MIT | master; 2026-10-28 | 10 | 21 (supporting) |
| NIST SP 800-34 Rev. 1 PDF | https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-34r1.pdf | standard | US government work | May 2010; 2026-10-28 (fetch truncated before §3.2) | 8 | 19 (supporting) |

Already listed and reused in L400: Raft paper (19, 21, 22), W3C Trace Context (22), Garcia-Molina & Salem, Sagas (22), Toxiproxy README and Grafana k6 web dashboard docs (19, 20 learningTools), Jaeger Getting Started and temporalio/cli (22 learningTools).

Dropped (L400): hal.inria.fr copy of RR-7506 (fetch returned no document); IEEE Xplore landing page of the Abadi article (paywalled; author's PDF used); third-party RTO/RPO blog posts found by search (secondary/vendor).

## L500 (2026-10-30, L500-SPEC: theory, ethics, readings)
All retrieved on 2026-10-30 with web_fetch / web_search. Primary papers are summarised, never reproduced; quotations are short and attributed.

| Title | URL | Type | Licence | Version / date checked | Score /12 | Used in lesson(s) |
|---|---|---|---|---|---|---|
| Lamport (1978), Time, Clocks, and the Ordering of Events (author's PDF) | https://lamport.azurewebsites.net/pubs/time-clocks.pdf | paper | (c) ACM 1978; fair use in teaching/research granted on the paper | CACM 21(7):558-565; re-fetched 2026-10-30 (full text incl. appendix) | 12 | 23 (T23.1), 27 (reading 1) |
| Ongaro & Ousterhout (2014), USENIX ATC 14 page | https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro | paper | USENIX open access (stated) | pp. 305-319, Best Paper; 2026-10-30 | 12 | 27 (reading 2) |
| Ongaro & Ousterhout (2014), extended version | https://raft.github.io/raft.pdf | paper | not shown on page | 20 May 2014; re-fetched 2026-10-30 (§§1-5.6) | 12 | 24 (T24.4), 27 |
| Fischer, Lynch & Paterson (1985), Impossibility of Distributed Consensus with One Faulty Process | https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf | paper | (c) ACM 1985 (copy permission notice on paper) | JACM 32(2):374-382; 2026-10-30 (full text) | 12 | 24 (T24.2) |
| Gilbert & Lynch (2002), Brewer's Conjecture ... (SIGACT News) | https://www.comp.nus.edu.sg/~gilbert/pubs/BrewersConjecture-SigAct.pdf | paper | not shown on page (author's copy) | 2002; 2026-10-30 (Theorems 1, 2, Corollary 1.1, §4) | 12 | 24 (T24.3) |
| Gilbert & Lynch (2012), Perspectives on the CAP Theorem | https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf | paper | not shown on page | 2012; 2026-10-30 | 11 | 23 (safety/liveness), 24 |
| Lamport (2001), Paxos Made Simple | https://lamport.azurewebsites.net/pubs/paxos-simple.pdf | paper | not shown on page | 01 Nov 2001; 2026-10-30 (P1-P2c, phases, §2.4 progress) | 12 | 24 (T24.4) |
| Dwork, Lynch & Stockmeyer (1988), Consensus in the Presence of Partial Synchrony | https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf | paper | (c) ACM 1988 notice | JACM 35(2):288-323; abstract + intro via search result 2026-10-30 | 10 | 23 (models) |
| Alpern & Schneider (1985), Defining Liveness | https://www.cs.cornell.edu/fbs/publications/DefLiveness.pdf | paper | not shown | IPL 21:181-185; abstract and §2-3 via search result 2026-10-30 | 10 | 23 (T23.3) |
| Kleppmann, Distributed Systems lecture notes 2025/26 | https://www.cl.cam.ac.uk/teaching/2526/ConcDisSys/dist-sys-notes.pdf | course | CC BY-SA (stated) | re-fetched 2026-10-30 (§§1-2.3: two generals, Byzantine, system models) | 11 | 23, 24 |
| Little & Graves (2008), Little's Law (chapter 5) | https://www.isye.gatech.edu/~jvandeva/Classes/6337/2013/Little's%20Law-Published.pdf | book chapter (course copy) | not shown | search-result text 2026-10-30 (L = lambda W, assumptions, picture proof) | 9 | 25 (T25.2) |
| Dean & Barroso (2013), The Tail at Scale | https://www.barroso.org/publications/TheTailAtScale.pdf | paper | (c) 2013 ACM | CACM 56(2):74-80; full text 2026-10-30 (63% example, hedged/tied requests) | 12 | 25 (T25.3) |
| Gunther (2008), A General Theory of Computational Scalability Based on Rational Functions | https://arxiv.org/abs/0808.1431 | paper (preprint) | licence link on the arXiv abstract page, not read | v2, 25 Aug 2008; PDF fetched 2026-10-30 (eq. 1-6) | 10 | 25 (T25.4) |
| Amdahl (1967), Validity of the single processor approach ... | https://www-inst.eecs.berkeley.edu/~n252/paper/Amdahl.pdf | paper (course copy) | not shown | AFIPS SJCC 1967; search-result text 2026-10-30 | 8 | 25 (T25.4 history) |
| ACM Code of Ethics and Professional Conduct | https://www.acm.org/code-of-ethics | standard | may be published unchanged with copyright notice (stated) | adopted 22 June 2018; 2026-10-30 | 12 | 26 |
| IEEE Code of Ethics (Policies 7.8) | https://www.ieee.org/about/corporate/governance/p7-8.html | standard | not shown | revisions through June 2020; 2026-10-30 | 11 | 26 |
| AWS, Summary of the US-EAST-1 event (7 Dec 2021) | https://aws.amazon.com/message/12721/ | incident report (vendor primary source) | not shown | published 10 Dec 2021; 2026-10-30 | 10 | 26 (case study) |
| Google SRE book ch. 15, Postmortem Culture | https://sre.google/sre-book/postmortem-culture/ | book chapter | not shown | 2026-10-30 | 10 | 26 |
| GDPR (Regulation (EU) 2016/679), EUR-Lex | https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng | statute | (c) EU; reuse authorised (Decision 2011/833/EU) | OJ L 119; fetched 2026-10-30 (recitals only displayed) | 11 | 26 |
| GDPR Art. 32 text (UK National Archives copy of the adopted EU text) | https://www.legislation.gov.uk/eur/2016/679/article/32/adopted | statute (copy) | not shown in the retrieved text | search-result text 2026-10-30 | 10 | 26 |
| CJEU press release 91/20, C-311/18 (Schrems II) | https://curia.europa.eu/jcms/upload/docs/application/pdf/2020-07/cp200091en.pdf | court (press release) | not shown | 16 July 2020; search-result text 2026-10-30 | 10 | 26 |
| IEA (2025), Energy and AI - Energy demand from AI | https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai | report | CC BY 4.0 (shown on charts) | 2025; search-result text 2026-10-30 (945 TWh by 2030, just under 3%) | 10 | 26 |
| Directive (EU) 2023/1791 (energy efficiency, recast), EUR-Lex | https://eur-lex.europa.eu/eli/dir/2023/1791/oj/eng | statute | (c) EU; reuse authorised | consolidated 05/08/2026 listed; Art. 12 not displayed (see KNOWN-GAPS) | 8 | 26 (policy context only) |
| ABET Criteria for Accrediting Computing Programs 2026-27 (PDF) | https://www.abet.org/wp-content/uploads/2025/12/2026-2027_CAC_Criteria.pdf | standard | (c) ABET; no reproduction (outcomes quoted briefly in syllabus) | 2026-10-30 (Criterion 3, CS outcome 6) | 11 | assessment/syllabus.md |
| ABET Criteria for Accrediting Engineering Programs 2025-26 | https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2025-2026/ | standard | (c) ABET | 2026-10-30 (outcomes 1-7) | 10 | assessment/syllabus.md |
| ACM/IEEE-CS/AAAI CS2023 knowledge areas | https://csed.acm.org/knowledge-areas/ | curriculum | not shown | 2026-10-30 (17 KA names) | 11 | assessment/syllabus.md |

Dropped (L500): gdpr-info.eu / gdpr-law.eu / lawplayer.com article pages (secondary; the legislation.gov.uk copy of the adopted text was used); third-party EED Article 12 compliance briefs (ets-corp.com, scienceshot.com, episensor.com, gage.academy - used only to locate the provision, not cited); ResearchGate copy of Little & Graves (OCR-garbled; Georgia Tech course copy used).
