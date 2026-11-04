# L300 research evidence – Application Architecture (lessons 12–16, "harden it")

Method: unchanged from SPEC.md. For each lesson: 2–3 implementation questions → web_search / web_fetch of official docs,
specs and maintained OSS → screen out marketing, stale or unclear-licence pages → score kept sources 0–2 on implementable (I),
current (C), authoritative (A), open (O), transferable (T), right depth (D) → keep ≥ 8/12 → cross-check each claim against
≥ 2 sources (≥ 1 official) or a local run. All fetches were done on 2026-10-28. Scores are given as I/C/A/O/T/D = total.
"search-only" = seen in a search result, not fetched; such URLs are not used as lesson sources.
Worked-example numbers: `research/L300_concept_examples.py` → `research/L300-concept-examples-output.txt`.

## Lesson 12 – CQRS and read models
**Questions.** (1) What does a read model need to survive a crash: where is its position stored? (2) Is rebuilding from
the log a recognised practice, and how do frameworks do it? (3) How big is the consistency window and how do you see it?

| Source | Decision | Score | Reason |
|---|---|---|---|
| martinfowler.com/bliki/CQRS.html (2011) | kept | 1/1/2/2/2/2 = 10 | Definition + the "risky complexity" caution |
| learn.microsoft.com … /patterns/cqrs (updated 2025-02-21) | cross-check only (vendor docs; not cited in the lesson after the update pass, R3-13) | 2/2/2/1/2/2 = 11 | Eventual consistency, outbox + idempotent read-model consumer, replay to rebuild; cross-check only, not a lesson source (F15 rule: vendor pages as background) |
| docs.kurrent.io/clients/python/v1.0/subscriptions | equivalent line only (update pass, R3-13) | 2/2/2/1/1/2 = 10 | Checkpoint = stored commit position; vendor client docs, so no longer a lesson source |
| martinfowler.com/eaaDev/EventSourcing.html (2005) | kept (update pass, primary) | 1/1/2/2/2/2 = 10 | Complete Rebuild by re-running the event log; "Should it crash it replays the events" |
| cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf (Greg Young) | background (update pass) | 1/1/2/2/2/1 = 9 | Primary CQRS text; PDF reachable but its text was not extracted, so no fact is taken from it |
| martendb.io/events/projections/rebuilding.html | kept | 2/2/2/2/1/2 = 11 | RebuildProjectionAsync; progression row reset on rebuild |
| microservices.io/patterns/data/cqrs.html | dropped | 1/2/1/1/2/1 = 8 | Paid-bootcamp promotion on the page; facts covered by Azure + Fowler |
| Axon StreamingEventProcessor API docs | dropped (equivalent line only) | search-only | Token store + resetTokens(); not fetched |

**Key facts**
- "beware that for most systems CQRS adds risky complexity"; use it on specific portions (a bounded context). https://martinfowler.com/bliki/CQRS.html
- "The read model is eventually consistent with the write model"; "make the read-model consumer idempotent to tolerate duplicate delivery"; views can be regenerated "by replaying historical events". https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs
- A checkpoint is "the position of an event … that your application has processed"; store it to "recover from crashes". https://docs.kurrent.io/clients/python/v1.0/subscriptions (vendor; equivalent line only)
- Primary: "Complete Rebuild: We can discard the application state completely and rebuild it by re-running the events from the event log"; a system that holds state in memory "Should it crash it replays the events from the overnight store". https://martinfowler.com/eaaDev/EventSourcing.html
- Marten rebuilds a projection with the async daemon; a rebuild starts by resetting the stored position. https://martendb.io/events/projections/rebuilding.html
- Local run: seeded crash at seq 31 → base drift 2 rows, half fix double-counts, solution 0 rows; lag p50 9.6–12.8 ms at a 20 ms poll.

## Lesson 13 – Resilience patterns
**Questions.** (1) Exact circuit-breaker states and the half-open rule? (2) What separates a bulkhead from a timeout, and how do
resilience4j / Polly implement it? (3) Does a Python `Future.result(timeout)` stop the work?

| Source | Decision | Score | Reason |
|---|---|---|---|
| martinfowler.com/bliki/CircuitBreaker.html (2014) | kept | 2/1/2/2/2/2 = 11 | Closed/open/half-open, trial call |
| resilience4j.readme.io/docs/circuitbreaker | kept | 2/1/2/2/1/2 = 10 | States and defaults (50 %, window 100, 60 s open, 10 half-open calls) |
| resilience4j.readme.io/docs/bulkhead | kept | 2/1/2/2/1/2 = 10 | SemaphoreBulkhead vs FixedThreadPoolBulkhead; maxConcurrentCalls 25 |
| github.com/resilience4j/resilience4j/releases | kept (supporting) | 1/2/2/2/0/1 = 8 | v2.4.0 latest (year inferred) |
| github.com/App-vNext/Polly docs/strategies/circuit-breaker.md | kept | 2/2/2/2/1/2 = 11 | Polly v8 states incl. Isolated; defaults; pollydocs.org page was blocked by the fetch filter |
| pollydocs.org/strategies/index.html + rate-limiter.html | kept (supporting) | 2/2/2/2/1/1 = 10 | Timeout/fallback strategies; AddConcurrencyLimiter in Polly.RateLimiting |
| learn.microsoft.com … /patterns/bulkhead (2026-03-19), /circuit-breaker (2025-03-21) | equivalent line only (update pass, R3-13) | 1/2/2/1/2/2 = 10 | Pool isolation; half-open allows a limited number of calls |
| sre.google/sre-book/addressing-cascading-failures/ (ch. 22) | kept (update pass, primary) | 2/1/2/2/2/2 = 11 | Deadlines, fail fast, bimodal latency exhausting threads, cap one client's share of threads |
| docs.python.org/3/library/concurrent.futures.html | kept | 2/2/2/2/1/2 = 11 | result(timeout) raises TimeoutError; running calls cannot be cancelled |

**Key facts**
- Half open: "the circuit is ready to make a real call as trial"; success resets, failure restarts the timeout. https://martinfowler.com/bliki/CircuitBreaker.html
- resilience4j: CLOSED/OPEN/HALF_OPEN (+ METRICS_ONLY, DISABLED, FORCED_OPEN); "If you want to restrict the number of concurrent threads, please use a Bulkhead." https://resilience4j.readme.io/docs/circuitbreaker
- Bulkhead: "Isolate the elements of an application into pools so that if one element fails, the others continue to function." https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead (vendor; equivalent line only)
- Primary: with a 100 s deadline, 5 % hung requests leave the frontend able to handle only 19.6 % of requests; "it's usually best to immediately return an error for that backend"; consider "only allowing 25% of your threads to be occupied by any one client" (a bulkhead). https://sre.google/sre-book/addressing-cascading-failures/
- `Future.cancel()` returns False if "the call is currently being executed"; so a timed-out call keeps its worker (combined statement; observed in `test_timeout_frees_the_caller_not_the_thread`). https://docs.python.org/3/library/concurrent.futures.html
- Local run: shared pool 8 → 8/24 ok with `pools shared 8/8`; bulkheads 4+4 → 24/24.

## Lesson 14 – Consumer-driven contract testing
**Questions.** (1) What is the current pact-python version and API? (2) How does provider verification use provider states?
(3) What do contract tests NOT do?

| Source | Decision | Score | Reason |
|---|---|---|---|
| docs.pact.io (Introduction, How Pact works) | kept | 2/2/2/2/2/2 = 12 | "contract by example"; provider replays requests and compares with the minimal expected response. Commercial banner ignored |
| pypi.org/project/pact-python | kept | 2/2/2/2/1/2 = 11 | 4.2.0 (2026-10-22), MIT, Python ≥ 3.11 |
| docs.pact.io/implementation_guides/python/docs/consumer + /provider | kept | 2/2/2/2/1/2 = 11 | Pact(...).with_specification("V4"), serve(), write_file(); Verifier add_source/add_transport/state_handler |
| github.com/pact-foundation/pact-python/releases | kept (supporting) | 1/2/2/2/0/1 = 8 | 4.0.0 removed pact.v2 |
| martinfowler.com/articles/consumerDrivenContracts.html (2006) | kept | 1/1/2/2/2/2 = 10 | Definition; "do not necessarily reduce the coupling" |
| docs.pact.io/pact_broker/can_i_deploy | kept (supporting) | 2/1/2/2/1/2 = 10 | Matrix-based deploy gate |
| github.com/pact-foundation/pact-specification | kept (supporting) | 1/2/2/2/1/1 = 9 | V3 messages, V4 |
| spring-attic/spring-cloud-contract | equivalent line only | – | Archived 2026-07-07; maintenance moved to Stubborn.sh |

**Key facts**
- pact-python 4.2.0 is current; the API is top-level `pact` (`from pact import Pact, match`); `pact.v2` was removed in 4.0.0; Pact instances default to spec V4 since 3.0.0. https://pypi.org/project/pact-python/, https://github.com/pact-foundation/pact-python/releases
- "Pact is, in effect, 'contract by example'"; the contract "is generated during the execution of the automated consumer tests". https://docs.pact.io/
- Provider verification sends each request "and the actual response it generates is compared with the minimal expected response". https://docs.pact.io/getting_started/how_pact_works
- Local run: the rename passes provider, stub and status-only checks; body verification reports `$.title: missing`.

## Lesson 15 – SLOs and error budgets
**Questions.** (1) Exact multiwindow, multi-burn-rate parameters? (2) Burn-rate and budget formulas? (3) Why percentiles, not means?

| Source | Decision | Score | Reason |
|---|---|---|---|
| sre.google/workbook/alerting-on-slos/ | kept | 2/2/2/2/2/2 = 12 | Table 5-8: 1h/5m 14.4 (2 %), 6h/30m 6 (5 %), 3d/6h 1 (10 %); short = 1/12 long |
| sre.google/sre-book/service-level-objectives/ | kept | 1/2/2/2/2/2 = 11 | SLI definition; "prefer to work with percentiles rather than the mean" |
| sre.google/workbook/implementing-slos/ | kept | 2/2/2/2/2/2 = 12 | SLI = good/total; error budget = 100 % − SLO; 4-week window |
| prometheus.io/docs/practices/histograms/ | kept | 2/2/2/2/1/2 = 11 | histogram_quantile; prefer native histograms; do not average summary quantiles |
| github.com/prometheus/prometheus (releases) | kept (supporting) | 1/2/2/2/0/1 = 8 | 3.15.1 (2026-10-21), Apache-2.0 |
| grafana.com/licensing/ | kept (supporting, vendor) | 0/2/2/1/1/2 = 8 | AGPLv3 since 2021-04-20 (matches the KB catalogue) |

**Key facts**
- Burn rate = how fast the service consumes the budget relative to the SLO; budget consumed = burn rate × window ÷ period; 14.4 over 1 h = 2 % of 30 days. https://sre.google/workbook/alerting-on-slos/
- The chapter's example config also has a 24h/2h ticket at burn 3, not in table 5-8; the lab uses the table only.
- "Most metrics are better thought of as distributions rather than averages." https://sre.google/sre-book/service-level-objectives/
- Local run: mean 147.9 ms, p95 94.3 ms, p99 2846.3 ms; latency burn 19.7 → page 1h/5m; time to page 57 min vs formula 43.9 min.

## Lesson 16 – Performance and architecture fitness in CI
**Questions.** (1) How do you count SQL statements portably in Python? (2) How should micro-benchmarks be read? (3) How does k6
make a budget a CI gate?

| Source | Decision | Score | Reason |
|---|---|---|---|
| docs.python.org/3.12/library/timeit.html (served /3/) | kept | 2/2/2/2/1/2 = 11 | repeat default 5; "the min() of the result is probably the only number you should be interested in" |
| docs.python.org/3/library/sqlite3.html | kept | 2/2/2/2/1/2 = 11 | set_trace_callback "for each SQL statement that is actually executed" |
| grafana.com/docs/k6/latest/using-k6/thresholds/ | kept | 2/2/2/1/2/2 = 11 | p(95)<200; non-zero exit when a threshold fails |
| grafana.com/docs/k6/latest/set-up/install-k6/ | kept (supporting) | 2/2/2/1/1/1 = 9 | brew install k6; winget install k6 --source winget; docker pull grafana/k6 |
| github.com/grafana/k6/releases | kept (supporting) | 1/2/2/2/0/1 = 8 | v2.3.0 (2026-09-21), AGPL-3.0 |
| docs.djangoproject.com/en/6.1/topics/db/optimization/ | kept | 2/2/2/2/2/2 = 12 | Queries in a loop; select_related / prefetch_related |
| pypi.org/project/import-linter/ | kept | 2/2/2/2/1/2 = 11 | 2.15, BSD-2-Clause |
| pypi.org/project/pytest-benchmark/, pypi.org/project/pyperf/ | kept (equivalents) | 2/2/2/2/1/1 = 10 | 5.3.0 / 2.10.0 |
| evolutionaryarchitecture.com/ffkatas/ | background only | search-only | Fitness-function definition seen in a snippet, not fetched |
| Rails guide, N + 1 section | dropped | – | Section text cut off in the fetch |

**Key facts**
- `Connection.set_trace_callback` fires for each statement SQLite actually executes (also transaction statements). https://docs.python.org/3/library/sqlite3.html
- k6: if any threshold fails, k6 exits with a non-zero code. https://grafana.com/docs/k6/latest/using-k6/thresholds/
- Local run: N+1 11 / 337 statements (10 / 500 loans), JOIN 1 / 1; both pass a 200 ms p95 budget in-process.
