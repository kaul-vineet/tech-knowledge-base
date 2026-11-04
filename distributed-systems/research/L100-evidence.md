# L100 research evidence — Distributed Systems (applied)

Method: SPEC.md research method. All sources fetched 2026-10-28. Score = implementable / current / authoritative / open / transferable / depth (0-2 each). Keep ≥ 8/12.

---

## Lesson 1 — Set up your environment: local multi-node lab
**Questions**
1. How do I run several independent HTTP "nodes" with only the Python stdlib, one process each?
2. How do I start/stop N child processes reliably and know when they are ready?
3. What is the current Compose file name/CLI for the optional container version, and which Python image tag is current?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Python docs http.server | kept | 11 | ThreadingHTTPServer, BaseHTTPRequestHandler, do_* dispatch; "not recommended for production" warning |
| Python docs subprocess | kept | 10 | Popen, terminate/kill, recommends `sys.executable` to relaunch Python |
| Docker Docs "How Compose works" | kept | 9 | compose.yaml preferred name; `docker compose up/down/ps` |
| Docker Hub python image | kept (supporting) | 9 | confirms tag `3.12.16-slim` exists |
| Kleppmann Cambridge notes | kept | 10 | definition of node; message-passing only |
| Generic "microservices on localhost" blog posts | dropped | — | not retrieved/needed; vendor/blog quality unknown |

**Key facts**
- `ThreadingHTTPServer` "is identical to HTTPServer but uses threads to handle requests" (added 3.7). — https://docs.python.org/3/library/http.server.html
- "http.server is not recommended for production. It only implements basic security checks." — same URL
- "passing sys.executable is the recommended way to launch the current Python interpreter again" — https://docs.python.org/3/library/subprocess.html
- Default Compose file path is `compose.yaml` (preferred); `docker compose up` starts, `docker compose down` stops and removes. — https://docs.docker.com/compose/intro/compose-application-model/
- "Each of the computers in a distributed system is called a node"; nodes "can only communicate by sending each other messages over a network". — https://www.cl.cam.ac.uk/teaching/2526/ConcDisSys/dist-sys-notes.pdf

---

## Lesson 2 — Two services talking
**Questions**
1. How does service A make a request with stdlib only, and how are non-2xx answers surfaced?
2. Which clock should measure latency?
3. What can go wrong in a request/response exchange?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Python docs urllib.request | kept | 11 | urlopen/Request/headers/HTTPError; recommends Requests for higher level |
| Python docs time | kept | 10 | perf_counter is monotonic, highest resolution; time() can go backwards |
| Python docs http.server | kept | 11 | send_response/send_header/end_headers; HTTP/1.0 default |
| Kleppmann notes §1.4 RPC | kept | 10 | RPC failure modes: no response → unknown outcome |
| Go net/http | kept (supporting) | 10 | Go equivalent; non-2xx is not an error |

**Key facts**
- `urlopen(url, data=None, [timeout, ]*, context=None)`; "HTTPDefaultErrorHandler will raise an HTTPError" for non-2xx. — https://docs.python.org/3/library/urllib.request.html
- `ProxyHandler({})` disables autodetected proxies (used in all labs so localhost is never proxied). — same URL
- `perf_counter()`: "clock with the highest available resolution to measure a short duration"; `time()` "can return a lower value than a previous call if the system clock has been set back". — https://docs.python.org/3/library/time.html
- "If the client sends an RPC request but receives no response, it doesn't know whether or not the server received and processed the request." — Kleppmann notes
- Go: "A non-2xx status code doesn't cause an error." — https://pkg.go.dev/net/http

---

## Lesson 3 — Timeouts
**Questions**
1. What is urllib's behaviour without a timeout, and what exception signals a timeout?
2. How should a timeout value be chosen?
3. How do other stacks express timeouts/deadlines?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Amazon Builders' Library: Timeouts, retries, and backoff with jitter | kept | 9 | concrete method: pick acceptable false-timeout rate → matching percentile (0.1% → p99.9); pitfalls |
| gRPC Deadlines guide | kept | 10 | no default deadline; DEADLINE_EXCEEDED; propagation as timeout to avoid clock skew |
| Python urllib.request | kept | 11 | timeout semantics ("blocking operations like the connection attempt") |
| Go net/http | kept | 10 | Client.Timeout includes connect, redirects, body read; 0 = no timeout |
| MDN AbortSignal.timeout | kept (supporting) | 10 | Node/Web fetch timeout → TimeoutError (Node.js ≥17.3) |

**Key facts**
- "Timeouts are the maximum amount of time that a client waits for a request to complete." … "we choose an acceptable rate of false timeouts (such as 0.1%). Then, we look at the corresponding latency percentile on the downstream service (p99.9 in this example)." Pitfall: if p99.9 is close to p50, add padding. — Builders' Library
- "By default, gRPC does not set a deadline which means it is possible for a client to end up waiting for a response effectively forever." — https://grpc.io/docs/guides/deadlines/
- Go: "The timeout includes connection time, any redirects, and reading the response body… A Timeout of zero means no timeout." — https://pkg.go.dev/net/http
- urllib timeout: "specifies a timeout in seconds for blocking operations like the connection attempt (if not specified, the global default timeout setting will be used)". — urllib docs
- Observed locally: read timeout raised `TimeoutError` (lab output).

Cross-check: "set a timeout on every call / no-timeout can wait forever" — Builders' Library + gRPC docs (official). Percentile method — Builders' Library + gRPC ("educated guess … validated by load testing").

---

## Lesson 4 — Retries with exponential backoff and jitter
**Questions**
1. What exactly is capped exponential backoff with full jitter, and why full jitter?
2. How many retries, and how to stop retries from overloading a sick dependency (retry budget)?
3. Which errors should be retried?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| AWS Architecture Blog: Exponential Backoff and Jitter | kept | 9 | the requested reference; Full vs Equal vs Decorrelated comparison |
| aws-arch-backoff-simulator source | kept (supporting) | 9 | exact formulas (blog shows them as images) |
| gRPC Retry guide | kept | 11 | retryPolicy fields; ±20% jitter; retryThrottling token bucket |
| Google SRE "Handling Overload" | kept | 9 | per-request limit of 3 attempts; per-client 10% retry ratio; retry at one layer |
| Builders' Library | kept | 9 | retries are selfish; 5 layers × 3 retries = 243×; token-bucket limit; 4xx vs 5xx |
| Tenacity / Resilience4j / Polly docs | kept (supporting) | 9 / 8 / 10 | API names for equivalents |
| Third-party "retry best practices" blogs | dropped | — | not needed; primary sources cover it |

**Key facts**
- Capped exponential: `expo(n) = min(cap, 2**n * base)`; Full Jitter: `random.uniform(0, expo(n))`; Equal: `v/2 + uniform(0, v/2)`; Decorrelated: `min(cap, uniform(base, sleep*3))`. — simulator source
- Blog conclusion: no-jitter backoff is "the clear loser"; Full and Decorrelated jitter cut work substantially; "Full Jitter" uses less work, slightly more time; jittered backoff "should be considered a standard approach for remote clients". — AWS blog
- gRPC: example `maxAttempts 4, initialBackoff 0.1s, maxBackoff 1s, backoffMultiplier 2, retryableStatusCodes [UNAVAILABLE]`; "Jitter of plus or minus 20% is applied"; throttling: "Failed RPCs decrement the count by 1, successful RPCs increment it by tokenRatio. If the token_count falls below half of maxTokens, retries are paused". — https://grpc.io/docs/guides/retry/
- SRE: "per-request retry budget of up to three attempts"; per-client "A request will only be retried as long as this ratio is below 10%"; "requests should only be retried at the layer immediately above the layer that is rejecting them". — https://sre.google/sre-book/handling-overload/
- Builders' Library: 5-deep stack with 3 retries per layer → "243x"; "limiting retries locally using a token bucket"; client errors should not be retried, server errors may succeed later; "APIs with side effects aren't safe to retry unless they provide idempotency".
- Resilience4j defaults: `maxAttempts 3` (including the first call), `waitDuration 500 ms`; `IntervalFunction.ofExponentialBackoff()`. Polly defaults: `MaxRetryAttempts 3`, `BackoffType Constant`, `Delay 2 s`, `UseJitter false`; exponential+jitter uses DecorrelatedJitterBackoffV2. Tenacity: `wait_random_exponential(multiplier=1, max=60)`, `stop_after_attempt`, `retry_if_exception_type`.

Cross-check: full-jitter formula — AWS blog/simulator + Polly/tenacity (randomised exponential). Retry budget — gRPC docs (official) + SRE book + Builders' Library. Which errors — Builders' Library + gRPC retryableStatusCodes.

---

## Lesson 5 — Idempotency keys
**Questions**
1. What does the IETF Idempotency-Key draft require of clients and servers (syntax, uniqueness, fingerprint, expiry)?
2. Which status codes for missing key, key reuse with different payload, and concurrent retry?
3. Why does a lost response force a retry that can duplicate side effects?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| draft-ietf-httpapi-idempotency-key-header-08 | kept | 11 | the requested spec; latest version (-08, 2026-10-22) |
| Builders' Library | kept | 9 | idempotency needed for safe retries; token-based idempotency |
| Kleppmann notes | kept | 10 | retry may charge a card twice; server-side dedup |
| Vendor API idempotency pages (Stripe, Adyen, PayPal) | dropped | — | vendor docs; the draft lists them as implementations, enough for one equivalents line |

**Key facts** (all from the draft unless noted)
- "Idempotency-Key is an Item Structured Header Field [RFC9651]. Its value MUST be a String" → sent as `"uuid"` (quoted).
- "The idempotency key MUST be unique and MUST NOT be reused with another request with a different request payload." "It is RECOMMENDED that a UUID [RFC9562] or a similar random identifier be used."
- Fingerprint MAY be a checksum of the request payload (lab uses SHA-256 of the body).
- Expiry: resource MAY use time-based keys and SHOULD publish its expiration policy.
- Enforcement: first time → process normally; retry after completion → "respond with a response consistent with the request being completed"; concurrent retry → "resource conflict error".
- Errors: missing key → 400; key reused with different payload → 422; retried while original still processing → 409.
- Security: validate key format; low-entropy keys can leak other clients' cached responses; use a composite lookup key with client-specific attributes.
- Methods OPTIONS, HEAD, GET, PUT, DELETE are idempotent; POST and PATCH are not (per RFC 9110, quoted in the draft).
- Kleppmann: resending a request "might cause the request to be performed more than once (e.g. charging a credit card twice)"; a fair-loss link becomes reliable by retransmitting "and by filtering out duplicated messages on the recipient side".

Cross-check: dedupe-on-retry — IETF draft (spec) + Kleppmann notes + Builders' Library.

---

## Lesson 6 — Ordering events with Lamport clocks
**Questions**
1. What are the Lamport clock rules on local event, send, and receive?
2. What ordering guarantee do they give (and not give)?
3. Why can't wall-clock timestamps order events across nodes?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Lamport 1978 (author's MSR page) | kept | 8 | original source; summary of causal partial order and total order consistent with it |
| Wikipedia: Lamport timestamp | kept | 11 | explicit rules and pseudocode; clock consistency condition; tie-break |
| gRPC Deadlines | kept | 10 | official example of clock skew between servers |
| Python time docs | kept | 10 | wall clock can go backwards; monotonic clocks only valid within one machine |
| Kleppmann notes §3 | attempted, not used for this lesson | — | section 3.4 text could not be retrieved (see KNOWN-GAPS) |

**Key facts**
- Rules: increment before each local event; include the counter when sending; on receive `time = max(timestamp, time) + 1`. — https://en.wikipedia.org/wiki/Lamport_timestamp
- "if one event comes before another, then that event's logical clock comes before the other's" (one-way only); total order via "any arbitrary total ordering of the processes" to break ties, but that order "cannot be depended on to imply a causal relationship". — Wikipedia
- "There is only a partial order in which an event e1 precedes an event e2 iff e1 can causally affect e2"; timestamps provide "a total ordering of events that was consistent with the causal order". — Lamport, MSR page
- "the clocks on the two servers might not be synchronized" → gRPC sends a timeout, not an absolute deadline. — https://grpc.io/docs/guides/deadlines/
- `time.time()` "can return a lower value than a previous call if the system clock has been set back". — Python time docs

Cross-check: Lamport rules — Wikipedia + author's summary (paper text itself not retrieved). Clock skew — gRPC (official) + Python docs.

---

## CI / tooling
- actions/setup-python README shows `actions/checkout@v7` and `actions/setup-python@v7` (2026-10-28). — https://github.com/actions/setup-python
- Python seeding: "By reusing a seed value, the same sequence should be reproducible from run to run as long as multiple threads are not running." (labs keep RNG use sequential or under a lock with a sequential client.) — https://docs.python.org/3/library/random.html

---

## Concepts layer (added 2026-10-28, per CONCEPTS-SPEC.md)
**Questions**
1. Where does each L100 mechanism show up in widely used open-source software (for "In real systems")?
2. Which real application areas and which L200–L400 topics frame the domain primer?
3. Which worked-example numbers can be computed and checked?

**New candidates**
| Source | Decision | Score | Reason / facts used |
|---|---|---|---|
| RFC 9110 HTTP Semantics | kept | 10 | HTTP is a request/response protocol; each response has a status code; example GET exchange (§3.4, §3.9). §9.2.2 itself was not in the retrieved text — the idempotent-method list is taken from the IETF idempotency draft, which cites RFC 9110. |
| Envoy router filter | kept | 11 | "fully jittered exponential back-off … default base interval of 25ms"; retry N delayed in [0, (2^N−1)·B); cap 10× base (250 ms); route timeout "includes all retries"; per-try timeout; `x-envoy-expected-rq-timeout-ms`; `x-envoy-upstream-service-time`; `retry-on` policies 5xx / gateway-error / connect-failure / retriable-4xx (409). |
| Kubernetes probes task page | kept | 10 | HTTP probe success = code ≥200 and <400; liveness failure → restart; readiness failure → no traffic from Services; `periodSeconds`, `initialDelaySeconds`. |
| Apache Kafka 4.3 Introduction | kept (primer only) | 8 | event streaming use cases (payments, IoT, microservices); per-partition order guarantee; replication factor 3 common. The requested producer-config page (`enable.idempotence`) redirected here; not used for idempotence claims. |
| Automerge binary format spec | kept | 9 | "Operation IDs are lamport timestamps"; operation ID = (actor ID, counter); compare counter, then actor ID. |
| Apache Cassandra CQL DML | kept | 9 | default write timestamp = coordinator's current time in microseconds; "counter updates are not idempotent". |
| httpwg.org rendering of RFC 9110 §9.2.2 | dropped | — | fetch returned no document. |

**Cross-checks for concept-note claims**
- Envoy full-jitter defaults vs AWS full jitter and gRPC jitter: three independent implementations/specs of jittered exponential backoff.
- Kubernetes HTTP health checks vs lab 1's `/health` polling and Compose docs.
- Lamport timestamps in Automerge vs Wikipedia/Lamport (lesson 6 sources).
- Wall-clock write timestamps (Cassandra) vs gRPC's statement that server clocks may not be synchronized.

**Worked examples** — every number in `content/concepts/*.md` comes from running `python research/concept_examples.py` (output 2026-10-28):
```
ports: [8001, 8002, 8003] | health body: {"node": "node1", "port": 8001, "pid": 4242} | Content-Length: 44
response body: {"item": "pear", "price": 4} | Content-Length: 28
median ms: 4.7 | 3 sequential calls at median ms: 14.1
B hangs, no timeout: all threads busy after 2.0 s
timeout 0.5 s: max throughput while B hangs = 20.0 req/s (>= 5 arriving)
deadline budget left for downstream call: 1.5 s
B latency: p50=40 ms  p99=88 ms  p99.9=116 ms
lab p99.9 timeout: 0.116
full-jitter ceilings s: [0.02, 0.04, 0.08, 0.16, 0.32, 0.5]
P(4 attempts all fail) = 0.0081
expected attempts per request (max 4) = 1.417
5 layers x 3 attempts each = 243 calls at the bottom
Envoy upper bounds ms for retries 1..3 (base 25): [25, 75, 175]
{"amount": 10} -> sha256 7f8b279ef4be0909 ...
{"amount": 99} -> sha256 1fb625524708d0b0 ...
P(at least one of 5 responses lost, p=0.4) = 0.92224
L=1 A wall=+0.010 user clicks Buy
L=2 A wall=+0.020 send 'create order' to B
L=3 B wall=-0.050 recv 'create order' from A
L=4 B wall=-0.040 reserve stock
L=5 B wall=-0.030 send 'charge card' to C
L=6 C wall=+0.100 recv 'charge card' from B
L=7 C wall=+0.110 send 'payment ok' to A
L=8 A wall=+0.080 recv 'payment ok' from C
L=8 C wall=+0.130 write audit log
L=9 A wall=+0.100 show receipt
```
Lab-run figures quoted in notes (latencies 10.0/4.8/4.7/3.2/3.0 ms from the lab 2 re-run after the rebalance; 11 vs 5 charges) are copied from the lab READMEs' real output.

## Rebalance (2026-10-28, REBALANCE-SPEC.md)
- Concept notes cut to 4 headings (Why it matters / Mental model / How it works / Common mistakes), 3 "How it works" points each pointing at the lab step that shows it. Removed parts moved into each lesson object: `inRealSystems` and `useWhen` (one line each, condensed from the old "In real systems" and "Use it when / avoid when" sections — same facts and sources as above, nothing new), `checkYourself` (the old questions/answers), `next` (old "Next: L200 …"). "Go deeper" links were merged into each lesson's `sources` (deduplicated by URL); the Envoy, Kubernetes, RFC 9110 and Cassandra pages that back `inRealSystems` claims were added there too.
- No new external sources were used; no new factual claims were introduced beyond observed lab output.
- **tryIt** (2 per lesson, 12 total): each is scripted in the lab's `try_it.py` and was run on Python 3.12.15 (Linux); every `expected` value is copied from that real output (also pasted in the lab README "Try it" section). Seeded labs (4, 5, 6) and lab 3 gave identical output on two runs; lab 1's errno text is Linux-specific; lab 2's total ms varies (the checks it prints do not).
- Lab code: plumbing (quiet handler + `reply()`, proxy-free opener, background server; `FlakyB` in lab 4; `violations()`/`show()` in lab 6) moved to a per-lab `helpers.py`; concept-naming comments added at the lines where each concept happens. Seeded demo output of labs 3–6 was diffed before/after: identical. Lab 1's start-up wait was raised from 5 s to 15 s after the unchanged test failed once on a loaded machine (behaviour otherwise the same). `PaymentB.loss_rate` and `Node.on_receive` were factored out so tryIt can change them without editing the lab file.
- Measured with the spec script after the rebalance: see KNOWN-GAPS → Rebalance.

## Platform + agent pass (2026-10-28, PLATFORM-AGENT-SPEC.md)
Questions: (1) Do the lab helpers behave the same on macOS and Windows? (2) How is a child process stopped correctly on each OS? (3) Which open-source runtimes run compose.yaml on a Mac mini / Windows PC? (4) What is needed to call nodes across the two machines? (5) Where does a local agent honestly help in L100?

Key facts (source):
- Windows `SO_REUSEADDR` "allows a socket to forcibly bind to a port in use by another socket"; behaviour is then indeterminate; servers should set `SO_EXCLUSIVEADDRUSE` (Microsoft Learn, SO_REUSEADDR/SO_EXCLUSIVEADDRUSE). `http.server.HTTPServer.allow_reuse_address = 1` and `socketserver.TCPServer.server_bind` sets `SO_REUSEADDR` when it is true (local CPython 3.12.15 source, `inspect.getsource`). → node.py: exclusive bind on Windows. Cross-check: WSAEADDRINUSE 10048 / WSAEACCES 10013 table (Winsock error codes).
- `Popen.terminate()`: SIGTERM on POSIX, `TerminateProcess()` on Windows; `kill()`: SIGKILL on POSIX, alias of terminate() on Windows; `send_signal(SIGTERM)` on Windows is an alias for terminate() (Python subprocess docs). `wait(timeout)` raises TimeoutExpired. → lab.py stop(): terminate → wait → kill.
- `sys.executable` is the recommended way to relaunch the current interpreter (subprocess docs, Popen warning).
- venv activation: `source <venv>/bin/activate` (zsh) / `<venv>\Scripts\Activate.ps1`; may need `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` (Python venv docs).
- `brew install python@3.12` installs `$HOMEBREW_PREFIX/bin/python3.12`, Apple-silicon bottles, stable 3.12.16 (formulae.brew.sh). winget id `Python.Python.3.12`, latest 3.12.10 (winstall.app).
- `podman compose` is a thin wrapper around docker-compose or podman-compose (Podman docs); macOS/Windows use a Podman machine VM / WSL 2 (podman.io install); Podman Desktop: `winget install RedHat.Podman-Desktop`, 6 GB RAM for the machine, onboarding installs compose CLI (podman-desktop.io). Fully qualified image names avoid short-name ambiguity (registries.conf note on podman.io).
- Colima: Docker runtime by default, docker client via `brew install docker`; bind mounts outside `/Users/$USER` appear empty; default VM 2 CPU / 2 GiB / 100 GiB (Colima README + FAQ). Homebrew `docker-compose` needs `cliPluginsExtraDirs` for `docker compose` (formula page).
- Rancher Desktop: macOS 13+, Windows 11 + WSL; bundles nerdctl, Moby and Docker Compose; 8 GB RAM recommended (Rancher Desktop docs).
- Docker Desktop: free for small businesses (<250 employees AND <$10M revenue), personal, education, non-commercial OSS; otherwise paid (Docker docs) → one equivalents line only.
- Firewall: `New-NetFirewallRule -DisplayName ... -Direction Inbound -Protocol TCP -LocalPort ... -Action Allow -Profile Private -RemoteAddress LocalSubnet` (Microsoft Learn parameters: Profile values, LocalSubnet keyword); macOS: System Settings → Network → Firewall, add apps allowed to accept incoming connections (Apple Support).
- Ollama: OpenAI-compatible `/v1/chat/completions` at `http://localhost:11434/v1/`; context size not settable via the OpenAI API (Modelfile `num_ctx`) (Ollama docs); GPU: Metal on Apple, NVIDIA CC 5.0+ driver 550+, AMD ROCm/Vulkan on Windows (Ollama gpu.mdx).

Kept vs dropped: kept official docs (Microsoft Learn, Python, Podman, Colima repo, Rancher Desktop, Homebrew, Ollama repo docs; scores 8–11). Dropped: tutorial blogs about Ollama setup and errno pages (secondary; one is a commercial newsletter).

Agent assist choice: lab 4 only — the log it summarizes is exactly the lesson's output (retries + latency), and the check (recompute counts and nearest-rank percentiles) is short, deterministic and exact. Lab 3 (latency) would duplicate it; labs 1/2/5/6 have no honest summarization task at L100.
Observed numbers (`python agent_assist.py --fake`): 126 attempts, 46 errors; code p50 24.1 ms, p99 141.0 ms; fake agent p50 32.7 (mean), p99 210.6 (max) → both flagged.
