"""L600 #07 - a reliable quantum-job service on unreliable backends (discrete-event simulation on a fake clock).

submit -> idempotency check -> canonicalise -> cache -> scheduler picks a backend -> chunks queue per backend
dispatch: bulkhead (slots) + circuit breaker; each chunk attempt gets a lease and a fencing token
finish:  ledger.commit (fenced, versioned) -> job complete -> result with error bars, cached by version
Faults: ledger 'lease-expiry' (shipped unfixed ledger), cache key 'stale-cache' / 'text-key' (see cachekeys.py).
"""
import hashlib
import heapq
from collections import deque

import results
from _kb import q17, resilience
from backends import TransientBackendError
from cachekeys import cache_key
from canon import canonicalise, circuit_hash

LEASE_S, CHUNK, BACKOFF_S, MAX_ATTEMPTS = 10.0, 1000, 0.5, 12
SCHED_WAIT_S = 15.0                    # scheduler's wait target: half the 30 s p95 budget (headroom)


class Conflict(ValueError):
    """Same job id, different request body (HTTP 422 in an API)."""


class JobService:
    def __init__(self, backends, ledger, key=cache_key, policy="floor+budget"):
        self.clock, self.ledger, self.key, self.policy = q17.FakeClock(), ledger, key, policy
        self.backends = {b.name: b for b in backends}
        self.queues, self.busy = {n: deque() for n in self.backends}, dict.fromkeys(self.backends, 0)
        self.retrying, self.max_busy = dict.fromkeys(self.backends, 0), dict.fromkeys(self.backends, 0)
        self.breakers = {n: resilience.CircuitBreaker(n, window=10, min_calls=5, failure_rate=0.5, open_s=20.0,
                                                      clock=lambda: self.clock.now, log=lambda r: self.log.append({"t": self.clock.now, **r}))
                         for n in self.backends}
        self.jobs, self.cache, self.events, self.seq, self.log = {}, {}, [], 0, []

    def at(self, t, fn, *args):
        self.seq += 1
        heapq.heappush(self.events, (t, self.seq, fn, args))

    def run(self):
        while self.events:
            t, _, fn, args = heapq.heappop(self.events)
            self.clock.now = max(self.clock.now, t)
            fn(*args)

    def healthy(self, name):
        br = self.breakers[name]                              # open breakers leave the pool until open_s has passed
        return br.state != "open" or self.clock.now - br.opened_at >= br.open_s

    def wait_estimate(self, name):
        b = self.backends[name]
        return (len(self.queues[name]) + self.busy[name] + self.retrying[name]) / b.slots * b.expected_latency()

    def pick(self, n, ops, floor):
        """Fidelity floor first, then the queue-time target; best estimated fidelity among what is left."""
        names = [m for m in self.backends if self.healthy(m)] or list(self.backends)
        fid = {m: self.backends[m].estimated_fidelity(n, ops) for m in names}
        if self.policy in ("best-fidelity", "fastest"):        # the two rejected options (ADR 0002)
            return max(names, key=fid.get) if self.policy == "best-fidelity" else min(names, key=self.wait_estimate)
        ok = [m for m in names if fid[m] >= floor]
        fast = [m for m in ok if self.wait_estimate(m) <= SCHED_WAIT_S]
        if fast:
            return max(fast, key=fid.get)
        return min(ok, key=self.wait_estimate) if ok else max(names, key=fid.get)

    def submit(self, req):
        body = repr(sorted(req.items())).encode("utf-8")
        fp, jid = hashlib.sha256(body).hexdigest(), req["job_id"]
        if jid in self.jobs:                                   # client retry: replay, never a second job
            if self.jobs[jid]["fp"] != fp:
                raise Conflict(f"job id {jid} already used with a different request")
            return self.jobs[jid]
        n, ops, _ = canonicalise(req["qasm"])
        chash, shots, seed = circuit_hash(req["qasm"]), req["shots"], req["seed"]
        job = {"fp": fp, "req": req, "n": n, "ops": ops, "submitted": self.clock.now, "started": None, "done": None,
               "attempts": 0, "cache_hit": None}
        self.jobs[jid] = job
        for name in sorted(self.backends, key=lambda m: -self.backends[m].estimated_fidelity(n, ops)):
            b = self.backends[name]
            hit = self.cache.get(self.key(req["qasm"], chash, b, shots, seed))
            if hit and b.estimated_fidelity(n, ops) >= req["min_fidelity"]:
                job.update(backend=name, started=self.clock.now, done=self.clock.now, source=hit["job_id"],
                           cache_hit={"cached_version": hit["version"], "current_version": b.version})
                return job
        job["backend"] = name = self.pick(n, ops, req["min_fidelity"])
        job["cache_key"] = self.key(req["qasm"], chash, self.backends[name], shots, seed)
        chunks = -(-shots // CHUNK)
        self.ledger.open(jid, chunks)
        self.queues[name].extend((jid, c, 0) for c in range(chunks))
        self.dispatch(name)
        return job

    def dispatch(self, name):
        b, q = self.backends[name], self.queues[name]
        while q and self.busy[name] < b.slots:                 # bulkhead: never more than `slots` in flight
            jid, c, tries = q.popleft()
            if self.ledger.chunk_done(jid, c) or (jid, c) in self.ledger.leases:
                continue
            try:
                run_s = self.breakers[name].call(b.start, self.clock.now)
            except (TransientBackendError, resilience.CircuitOpen) as e:
                self.jobs[jid]["attempts"] += 1
                delay = self.breakers[name].open_s if isinstance(e, resilience.CircuitOpen) else BACKOFF_S * 2 ** min(tries, 5)
                if tries + 1 >= MAX_ATTEMPTS:
                    raise RuntimeError(f"{jid} chunk {c}: {MAX_ATTEMPTS} attempts failed") from e
                self.retrying[name] += 1
                self.at(self.clock.now + delay, self.requeue, name, (jid, c, tries + 1), False, True)
                continue
            token, job = self.ledger.grant(jid, c), self.jobs[jid]
            job["attempts"] += 1
            job["started"] = job["started"] if job["started"] is not None else self.clock.now
            self.busy[name] += 1
            self.max_busy[name] = max(self.max_busy[name], self.busy[name])
            self.at(self.clock.now + run_s, self.finish, name, jid, c, token, b.version)
            self.at(self.clock.now + LEASE_S, self.expire, name, jid, c, token)

    def requeue(self, name, item, front=False, backoff=False):
        self.retrying[name] -= backoff                         # a chunk waiting out a backoff counted as load
        self.queues[name].appendleft(item) if front else self.queues[name].append(item)
        self.dispatch(name)

    def expire(self, name, jid, c, token):
        """Lease ran out before the attempt reported: assume it is lost and redeliver (at-least-once)."""
        if self.ledger.holds(jid, c, token) and not self.ledger.chunk_done(jid, c):
            self.ledger.release(jid, c)
            self.log.append({"t": self.clock.now, "evt": "lease-expired", "job": jid, "chunk": c, "token": token})
            self.requeue(name, (jid, c, 0), front=True)

    def finish(self, name, jid, c, token, version):
        self.busy[name] -= 1
        job, b = self.jobs[jid], self.backends[name]
        counts = b.execute(job["n"], job["ops"], version, min(CHUNK, job["req"]["shots"] - c * CHUNK),
                           job["req"]["seed"], c)
        status, restarted = self.ledger.commit(jid, c, token, version, counts)
        self.log.append({"t": self.clock.now, "evt": "commit", "job": jid, "chunk": c, "token": token, "status": status,
                         "restarted": restarted})
        if self.ledger.holds(jid, c, token):
            self.ledger.release(jid, c)
        for k in range(self.ledger.jobs[jid]["chunks"]):        # rejected or restarted chunks go back to the queue
            if not self.ledger.chunk_done(jid, k) and (jid, k) not in self.ledger.leases and (restarted or k == c):
                self.queues[name].append((jid, k, 0))
        if job["done"] is None and self.ledger.complete(jid):
            job["done"] = self.clock.now
            self.cache[job["cache_key"]] = {"job_id": jid, "version": self.ledger.jobs[jid]["version"]}
        self.dispatch(name)

    def result(self, jid):
        job = self.jobs[jid]
        src = job.get("source", jid)                            # a cache hit reads the job that produced the result
        v = self.ledger.jobs[src]["version"]
        return results.build(jid, self.ledger.counts(src), job["n"], self.backends[job["backend"]].readout(job["n"], v),
                             job["backend"], v, cache_hit=job["cache_hit"] is not None)
