"""Recompute every calculation answer and execute every code-reading snippet in content/qbank/*.json (L100-L500).

python research/qbank_checks.py   -> prints OK and exits 0 when every stored answer matches the code.
Each CALC entry: (level, distinctive phrase from the question, function returning the correct option text).
"""
import contextlib, io, json, math, sys
from pathlib import Path

TOPIC = Path(__file__).resolve().parent.parent
LEVELS = ["L100", "L200", "L300", "L400", "L500"]


# ---------- L100 ----------
def full_jitter_range_ms(attempt, base_ms, cap_ms):  # lesson 4: uniform(0, min(cap, base * 2^attempt)), attempt from 0
    return f"0 to {min(cap_ms, base_ms * 2 ** attempt):g} ms"


def amplification(*attempts_per_layer):  # lesson 4: retries at every layer multiply
    return f"{math.prod(attempts_per_layer)} calls"


def remaining_timeout_s(deadline_s, *spent_s):  # lesson 3: timeout = deadline - now
    return f"{round(deadline_s - sum(spent_s), 3):g} s"


def false_timeouts(requests, pct_a, pct_b):  # lesson 3: timeout at percentile p -> (1 - p) of normal requests time out
    a, b = round(requests * (1 - pct_a / 100)), round(requests * (1 - pct_b / 100))
    return f"about {a:,} (vs about {b:,} with p{pct_b:g})"


def lamport_receive(local, received):  # lesson 6
    return str(max(local, received) + 1)


def lamport_chain():  # lesson 6: A: local, send m1; B: 3 locals, recv m1, send m2; C: local, recv m2
    a = b = c = 0
    a += 1; a += 1; m1 = a
    b += 3; b = max(b, m1) + 1; b += 1; m2 = b
    c += 1; c = max(c, m2) + 1
    return str(c)


def ledger_totals(orders, amount, lost_responses):  # lesson 5: each lost response -> one more attempt reaching the server
    without_keys = (orders + lost_responses) * amount
    return f"{without_keys} without keys, {orders * amount} with keys"


def sequential_vs_parallel(*ms):  # lesson 2: sequential latencies add up
    return f"{sum(ms)} ms sequentially, {max(ms)} ms in parallel"


# ---------- L200 ----------
def lease_takeover(last_renewal, ttl):  # lesson 7: failover = last renewal + TTL
    return f"t={last_renewal + ttl}"


def dlq_time(first_receive, visibility, max_receives):  # lesson 8: crash every time, never acked
    t, receives = first_receive, 0
    while True:
        if receives >= max_receives:
            return f"t={t}"
        receives += 1
        t += visibility


def movement(n_before, n_after, keys=720_000):  # lesson 9: hash % N vs ideal ring share
    mod = sum(1 for k in range(keys) if k % n_before != k % n_after) / keys
    ring = 1 / n_after
    return f"ring about {ring:.1%}, hash % N about {mod:.1%}"


def stale_window(cached_at, ttl, changed_at):  # lesson 10: no invalidation -> stale until expiry
    expires = cached_at + ttl
    return f"until t={expires} s ({expires - changed_at} s of stale reads)"


def cache_db_reads(ttl, seconds):  # lesson 10: cache-aside, one read per second, entry expires at set + ttl
    reads, expires = 0, None
    for t in range(seconds):
        if expires is None or t >= expires:
            reads += 1
            expires = t + ttl
    return f"{reads} database reads"


class _Bucket:  # lesson 11: lazy refill token bucket
    def __init__(self, rate, burst):
        self.rate, self.burst, self.tokens, self.last = rate, burst, float(burst), 0.0

    def allow(self, now):
        self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


def burst_pass(rate, burst, n):
    b = _Bucket(rate, burst)
    return f"{sum(b.allow(0.0) for _ in range(n))} requests"


def two_batches(rate, burst, n1, t2, n2):
    b = _Bucket(rate, burst)
    first = sum(b.allow(0.0) for _ in range(n1))
    second = sum(b.allow(t2) for _ in range(n2))
    return f"{first + second} requests ({first} + {second})"


def retry_after(tokens, rate):  # lesson 11: max(1, ceil((1 - tokens) / rate))
    return f"Retry-After: {max(1, math.ceil((1 - tokens) / rate))}"


# ---------- L300 ----------
def raft_majority(n):  # lesson 12
    m = n // 2 + 1
    return f"majority {m}, tolerates {n - m} failed nodes"


def self_time():  # lesson 15: create [10,190] has children authorize [30,150] and receipt [160,185]
    create = 190 - 10
    children = (150 - 30) + (185 - 160)
    return f"{create - children} ms"


def littles_law(rate_per_s, time_ms):  # lesson 16: L = lambda * W
    return f"{rate_per_s * time_ms / 1000:g} requests"


def queue_delay(workers, service_ms, bound):  # lesson 16: capacity = workers * 1000 / service_ms
    cap = workers * 1000 / service_ms
    return f"capacity {cap:g}/s, worst queue wait about {bound / cap * 1000:g} ms"


def drain(burst_rate, burst_s, capacity, after_rate):  # lesson 16
    backlog = (burst_rate - capacity) * burst_s
    return f"backlog {backlog:g}, drained {backlog / (capacity - after_rate):g} s after the burst"


def two_leader_ticks(first_both, heal):  # lesson 13: both lead from n2's acquisition until n1 is refused at the heal
    return f"{len(range(first_both, heal))} ticks"


# ---------- L400 ----------
def smallest_r(n, w):  # lesson 17: R + W > N
    return f"R = {n - w + 1}"


def quorum_tolerance(n, r, w):  # lesson 17: a read needs R live replicas, a write W
    return f"reads survive {n - r} down, writes survive {n - w} down"


def pn_value(p, n):  # lesson 18
    return str(sum(p.values()) - sum(n.values()))


def rpo_estimate(writes_per_s, lag_ms):  # lesson 19: async -> writes inside the replication lag are lost
    return f"about {writes_per_s * lag_ms / 1000:g} writes"


ONE_WAY = {("us", "eu"): 40, ("eu", "ap"): 70, ("us", "ap"): 110}


def _ow(a, b):
    return 0 if a == b else ONE_WAY.get((a, b), ONE_WAY.get((b, a)))


def commit_ms(user, leader):  # lesson 19: client -> leader -> nearest follower -> leader -> client
    nearest = min(_ow(leader, f) for f in ("us", "eu", "ap") if f != leader)
    return 2 * _ow(user, leader) + 2 * nearest


def best_leader():
    worst = {ld: max(commit_ms(u, ld) for u in ("us", "eu", "ap")) for ld in ("us", "eu", "ap")}
    ld = min(worst, key=worst.get)
    return f"{ld} (worst region {worst[ld]} ms)"


def blast(orders, pct, abort_after):  # lesson 20: every faulted order is harmed when the hypothesis is false
    cohort = orders * pct // 100
    return f"{cohort} without abort, {min(cohort, abort_after)} with abort"


def growth_factor(a, b):  # lesson 21
    return f"about {b / a:.1f}x"


def p_hit(per_walk, walks):  # lesson 21: chance at least one random walk hits the bug
    return f"about {1 - (1 - per_walk) ** walks:.0%}"



# ---------- L500 ----------
def sync_timeout(one_way_ms, proc_ms):  # lesson 23: round trip <= 2 * Delta + processing
    return f"{2 * one_way_ms + proc_ms} ms"


def mm1_w_ms(lam, mu):  # lesson 25: W = 1 / (mu - lambda)
    return f"{1000 / (mu - lam):g} ms"


def fanout_slow(p, n):  # lesson 25: 1 - (1 - p)^n
    return f"about {1 - (1 - p) ** n:.0%}"


def amdahl_speedup(sigma, p):  # lesson 25
    return f"{p / (1 + sigma * (p - 1)):.2f}"


def downtime_minutes(avail, days):  # lesson 26
    return f"{(1 - avail) * days * 24 * 60:.1f} minutes"


def facility_mwh(it_kw, pue):  # lesson 26: energy = IT power x PUE x hours
    return f"{it_kw * pue * 8760 / 1000:.1f} MWh"


def lamport_mutex_messages(n):  # lesson 27: requests + acks + releases to the other N - 1
    return f"{3 * (n - 1)} messages"

CALC = [
    ("L100", "attempt 5 (attempts count from 0)", lambda: full_jitter_range_ms(5, 20, 500)),
    ("L100", "base 25 ms and max 250 ms", lambda: full_jitter_range_ms(3, 25, 250)),
    ("L100", "up to 4 attempts, and the gateway", lambda: amplification(4, 3)),
    ("L100", "one 0.8 s deadline", lambda: remaining_timeout_s(0.8, 0.25, 0.35)),
    ("L100", "200,000 normal requests", lambda: false_timeouts(200_000, 99, 99.9)),
    ("L100", "Node C's Lamport clock is 12", lambda: lamport_receive(12, 7)),
    ("L100", "B does three local events", lambda: lamport_chain()),
    ("L100", "6 responses are lost", lambda: ledger_totals(5, 10, 6)),
    ("L100", "50 ms, 30 ms and 20 ms", lambda: sequential_vs_parallel(50, 30, 20)),
    ("L200", "TTL is 8 s", lambda: lease_takeover(23, 8)),
    ("L200", "MAX_RECEIVES = 3", lambda: dlq_time(5, 20, 3)),
    ("L200", "8 nodes to 9", lambda: movement(8, 9)),
    ("L200", "cached at t=5 s", lambda: stale_window(5, 45, 20)),
    ("L200", "TTL of 20 s", lambda: cache_db_reads(20, 60)),
    ("L200", "rate 5/s and burst 8", lambda: burst_pass(5, 8, 30)),
    ("L200", "rate 2/s, burst 5", lambda: two_batches(2, 5, 10, 1.5, 10)),
    ("L200", "0.25 tokens per second", lambda: retry_after(0.1, 0.25)),
    ("L300", "seven-node Raft cluster", lambda: raft_majority(7)),
    ("L300", "orders GET /create runs from", lambda: self_time()),
    ("L300", "300 requests per second", lambda: littles_law(300, 40)),
    ("L300", "6 workers", lambda: queue_delay(6, 15, 60)),
    ("L300", "500 requests/s for 8 s", lambda: drain(500, 8, 400, 300)),
    ("L300", "healed at t=9", lambda: two_leader_ticks(4, 9)),
    ("L400", "N = 5 and W = 3", lambda: smallest_r(5, 3)),
    ("L400", "N = 5, R = 2, W = 4", lambda: quorum_tolerance(5, 2, 4)),
    ("L400", "P = {a: 7, b: 4}", lambda: pn_value({"a": 7, "b": 4}, {"a": 2, "b": 3})),
    ("L400", "100 order writes per second", lambda: rpo_estimate(100, 160)),
    ("L400", "nearest follower and back", lambda: best_leader()),
    ("L400", "80 orders", lambda: blast(80, 25, 1)),
    ("L400", "1,853 to 29,221", lambda: growth_factor(1853, 29221)),
    ("L400", "16 of 1,000 random walks", lambda: p_hit(16 / 1000, 100)),
    ("L500", "clock is 9 when it receives a message stamped 14", lambda: lamport_receive(9, 14)),
    ("L500", "at most 30 ms", lambda: sync_timeout(30, 4)),
    ("L500", "N = 9 replicas and W = 6", lambda: smallest_r(9, 6)),
    ("L500", "λ = 45 per second", lambda: mm1_w_ms(45, 50)),
    ("L500", "500 requests per second", lambda: littles_law(500, 80)),
    ("L500", "20 leaves", lambda: fanout_slow(0.05, 20)),
    ("L500", "10% serial", lambda: amdahl_speedup(0.1, 8)),
    ("L500", "99.9% availability over a 30-day month", lambda: downtime_minutes(0.999, 30)),
    ("L500", "30 kW of IT load", lambda: facility_mwh(30, 1.5)),
    ("L500", "N = 7 processes", lambda: lamport_mutex_messages(7)),
]


def run_snippet(code):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(code, "<snippet>", "exec"), {"__name__": "__snippet__"})
    return out.getvalue().strip()


def main():
    errors, n_calc, n_code = [], 0, 0
    banks = {lv: json.loads((TOPIC / "content" / "qbank" / f"{lv}.json").read_text(encoding="utf-8")) for lv in LEVELS}
    used = set()
    for lv, qs in banks.items():
        for q in qs:
            right = q["options"][q["answer"]]
            if q["type"] == "calculation":
                hits = [i for i, (clv, phrase, _) in enumerate(CALC) if clv == lv and phrase in q["question"]]
                if len(hits) != 1:
                    errors.append(f"{q['id']}: {len(hits)} CALC entries match (need exactly 1)")
                    continue
                used.add(hits[0]); n_calc += 1
                want = CALC[hits[0]][2]()
                if right != want:
                    errors.append(f"{q['id']}: stored answer {right!r} != computed {want!r}")
                if sum(o == want for o in q["options"]) != 1:
                    errors.append(f"{q['id']}: computed answer appears {sum(o == want for o in q['options'])} times in options")
            if q.get("code"):
                if len(q["code"].splitlines()) > 15:
                    errors.append(f"{q['id']}: snippet longer than 15 lines")
                if q["type"] == "code-reading":  # every code-reading answer is the snippet's printed output
                    n_code += 1
                    try:
                        got = run_snippet(q["code"])
                    except Exception as exc:  # a snippet that crashes is a broken question
                        errors.append(f"{q['id']}: snippet raised {exc!r}"); continue
                    if got != right:
                        errors.append(f"{q['id']}: snippet prints {got!r}, stored answer {right!r}")
                else:
                    compile(q["code"], q["id"], "exec")  # debugging snippets must at least parse
            elif q["type"] == "code-reading":
                errors.append(f"{q['id']}: code-reading question without code")
    for i, (lv, phrase, _) in enumerate(CALC):
        if i not in used:
            errors.append(f"CALC entry never used: {lv} {phrase!r}")
    for e in errors:
        print("ERROR", e)
    if errors:
        sys.exit(1)
    print(f"OK: {n_calc} calculation answers recomputed, {n_code} code-reading snippets executed")


if __name__ == "__main__":
    main()
