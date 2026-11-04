# L200 research evidence — Distributed Systems (applied)

Method: SPEC.md research method (unchanged from L100). All sources fetched 2026-10-28 with web_fetch / web_search. Score = implementable / current / authoritative / open / transferable / depth (0-2 each); keep ≥ 8/12. Worked-example numbers in the concept notes come from `python research/concept_examples_l200.py` (runs the labs).

---

## Lesson 7 — Leader election with leases and fencing tokens
**Questions**
1. What must a lease store offer (atomic create-if-absent, TTL, monotonic revision) and how does etcd expose it?
2. Why is a lease not enough for correctness, and what exactly does a fencing token check?
3. How do real systems hand over leadership faster than the TTL?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Kleppmann, "How to do distributed locking" (2016) | kept | 10 | Fencing token definition, 33/34 example, GC-pause failure, ZooKeeper zxid as token |
| etcd docs v3.6: Interacting with etcd | kept | 11 | Lease grant/revoke/keep-alive; keys deleted when the lease expires; global revision |
| etcd docs v3.6: gRPC gateway | kept | 10 | `/v3/kv/txn` with `compare target CREATE` (CAS), keys base64 in JSON |
| etcdctl README (main) | kept | 10 | `lease grant`, `txn` grammar (`create("k") = "0"`), `elect` (resign on signal; 60 s default lease) |
| etcd releases page | kept (supporting) | 9 | v3.7.3 latest; images gcr.io/etcd-development/etcd (primary), quay.io/coreos/etcd |
| etcd v3election proto / swagger (via search) | kept (supporting) | 8 | Campaign/Proclaim/Leader/Resign on `/v3/election/*`; LeaderKey.rev usable in txn compares |
| Kubernetes docs: Leases | kept | 10 | Lease objects for leader election; alpha "release lock on exit" (matches the build task) |
| Redis/Valkey `SET NX EX` lock pattern (valkey.io SET page) | kept (equivalents only) | 9 | Lease without fencing token; page itself recommends a token + compare-delete |

**Key facts**
- "a fencing token is simply a number that increases ... every time a client acquires the lock"; storage "rejects the request with token 33" after seeing 34. — Kleppmann blog
- "Once a lease's TTL elapses, the lease expires and all attached keys are deleted." — etcd interacting_v3
- txn compare on `CREATE` revision via `/v3/kv/txn`; key/value base64 in JSON. — etcd gRPC gateway page
- `ELECT` "returns a zero exit code only if it is terminated by a signal and can revoke its candidacy"; abnormal termination delays progress "by up to the default lease length of 60 seconds". — etcdctl README
- Kubernetes uses Lease objects "to ensure only one instance of a component is running"; an alpha gate makes kube-controller-manager release the lock on exit "rather than waiting for the lock's TTL to expire". — kubernetes.io Leases

## Lesson 8 — At-least-once messaging
**Questions**
1. What do brokers do with a delivered but unacknowledged message, and after how long?
2. How do real brokers bound redelivery of poison messages?
3. Where do duplicates come from, and who must remove them?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| NATS docs: Ack responses and redelivery | kept | 10 | AckWait default 30 s; ack / nak / term / in-progress; redelivery loop |
| NATS docs: Pull consumers in depth | kept (supporting) | 9 | explicit-ack pull consumer, batch/expires, MaxAckPending default 1000 |
| RabbitMQ docs: Quorum Queues (4.4) | kept | 11 | x-delivery-count, delivery limit default 20 since 4.0, dead-lettering, consumer timeout |
| Confluent docs: Kafka message delivery guarantees (via search) | kept (supporting, equivalents line) | 8 | consumer saves position after processing = at-least-once; vendor page describing Apache Kafka |
| kafka.apache.org 4.3 introduction | dropped | 6 | fetched page did not contain the delivery-semantics section |
| AWS SQS visibility-timeout docs | not used | — | commercial; not needed (concept is broker-neutral) |

**Key facts**
- "If the answer never comes, the server assumes the worker stopped and delivers the message again ... Its length is AckWait, and it defaults to 30 seconds." — NATS acknowledgment
- "Starting with RabbitMQ 4.0, the delivery limit for quorum queues defaults to 20"; over the limit messages are dropped or dead-lettered. — RabbitMQ quorum queues
- Consumers "should use manual acknowledgements to ensure messages that aren't successfully processed are returned to the queue". — RabbitMQ quorum queues

## Lesson 9 — Sharding with consistent hashing
**Questions**
1. How much data moves on membership change with modulo vs a ring (measured, not assumed)?
2. What do virtual nodes fix, and what do they cost?
3. How do Dynamo-style stores choose replicas on the ring?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Apache Cassandra docs: Dynamo | kept | 11 | Naive modulo "might invalidate almost all of the mappings"; walk the ring to RF distinct nodes; vnodes pros/cons; 256 random tokens in 2.x |
| Nishtala et al., Scaling Memcache at Facebook (NSDI'13) | kept | 10 | Consistent hashing across memcached servers; "a single key can account for 20% of a server's requests" |
| Karger et al. 1997 (original consistent hashing paper) | not fetched | — | Cassandra + memcache sources suffice; listed as a gap |
| Ollama OpenAI-compatibility doc (from L100) | kept (agent assist) | 9 | Local endpoint used by `local_agent.client` |

**Key facts**
- "adding a single node might invalidate almost all of the mappings"; consistent hashing "only has to move a small fraction of the keys". — Cassandra Dynamo page
- Replicas: "walk the ring in a clockwise fashion until we encounter three distinct nodes"; SimpleStrategy skips nodes already in the replica set. — same
- Measured in the lab (10,000 keys): modulo 80.3%, ring 18.9% moved going 4 → 5 nodes; imbalance 2.20 (1 vnode) vs 1.03 (100 vnodes).

## Lesson 10 — Caching and invalidation
**Questions**
1. What is the cache-aside read/write path and why delete instead of update?
2. What causes a thundering herd and how do real systems suppress it?
3. Which Valkey commands implement TTL fill, invalidation and a loader lock, and what does RESP look like on the wire?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| Nishtala et al., Scaling Memcache at Facebook | kept | 10 | Demand-filled look-aside cache; delete on write "because deletes are idempotent"; leases vs stale sets and herds (17K/s → 1.3K/s) |
| Go golang.org/x/sync/singleflight | kept | 10 | "only one execution is in-flight for a given key at a time" (v0.24.0, BSD-3-Clause) |
| Valkey docs: SET | kept | 11 | EX/PX/NX/XX/IFEQ; NX+EX lock pattern |
| Valkey docs: RESP protocol | kept | 11 | Commands = array of bulk strings; `$-1` null; `+`, `-`, `:` replies |
| Docker Hub valkey/valkey | kept (supporting) | 9 | Tag 9.1.3 (latest); protected mode off in the image |

**Key facts**
- "For write requests, the web server issues SQL statements to the database and then sends a delete request to memcache ... We choose to delete cached data instead of updating it because deletes are idempotent." — memcache paper
- "A thundering herd happens when a specific key undergoes heavy read and write activity"; leases: "return a token only once every 10 seconds per key". — memcache paper
- "Clients send commands to a Valkey server as an array of bulk strings"; "$-1\r\n" is the null bulk string. — Valkey protocol

## Lesson 11 — Rate limiting
**Questions**
1. What exactly do RFC 6585 and RFC 9110 say about 429 and Retry-After (both forms)?
2. How do Envoy / NGINX / Go implement limits (algorithm, status, Retry-After)?
3. Why do fixed windows allow double bursts?

**Candidates**
| Source | Decision | Score | Reason |
|---|---|---|---|
| RFC 6585 §4 | kept | 11 | 429 "MAY include a Retry-After header"; MUST NOT be cached; server decides how to identify the user |
| RFC 9110 | kept (truncated retrieval) | 10 | Retrieved, but the fetched text ended before §10.2.3; grammar cross-checked via MDN + http.dev |
| MDN: Retry-After | kept | 10 | `<http-date>` or `<delay-seconds>` = non-negative decimal integer; cites RFC 9110 field.retry-after |
| http.dev: Retry-After (via search) | kept (supporting) | 8 | Same two forms; points to RFC 9110 §10.2.3 |
| Envoy docs: Local rate limit | kept | 11 | Token bucket; 429; Retry-After delay-seconds = seconds to next token, clamped to ≥ 1 |
| NGINX docs: limit_req | kept | 10 | Leaky bucket; rate + burst; `limit_req_status` default 503 |
| Go golang.org/x/time/rate | kept | 10 | Limiter = token bucket of size b refilled at r; Allow/Reserve/Wait (v0.16.0) |
| Valkey docs: INCR (rate limiter pattern) | kept (supporting) | 9 | Fixed-window counter per IP per second with EXPIRE |
| Microsoft Learn Dev Proxy Retry-After page (via search) | dropped | 7 | Vendor tool page; MDN + RFC suffice |

**Key facts**
- "The 429 status code indicates that the user has sent too many requests in a given amount of time ... MAY include a Retry-After header". — RFC 6585 §4
- Retry-After: "<delay-seconds> A non-negative decimal integer indicating the seconds to delay after the response is received", or an HTTP date. — MDN (spec: RFC 9110 field.retry-after)
- Envoy: "The delay is the number of seconds until the next token is available ..., clamped to at least one second." — Envoy local rate limit
