"""Capacity and cost planning from the lesson 15 request log (lesson 21 lab code).

load model    route mix + service times measured in the L300 log, scaled by the stated growth (libraries, peak)
Little's law  L = lambda x W: requests in flight = arrival rate x time in the system
benchmark     a seeded queue simulation of ONE instance (c workers, measured service times): the highest
              arrival rate whose p99 stays inside the SLO is the instance's capacity
sizing        instances_needed(); cost per million requests from a stated (hypothetical) instance price
Solution: instances_needed() sizes on the PEAK rate, the SLO-safe benchmark capacity, headroom, and N+1.
"""
import heapq
import math
import random
import statistics

SLO_P99_MS = 300  # lesson 15: 99 % of requests under 300 ms
WORKERS = 4  # concurrent requests one instance serves (threads/processes)
HEADROOM = 0.8  # plan to use at most 80 % of the benchmarked capacity at peak (spikes, GC, deploys)


def load_model(records, libraries=400, peak_factor=3.0, seconds=3 * 86400):
    """records: the L300 log (one library). Returns the demand for `libraries` libraries."""
    per_library = len(records) / seconds  # 25,920 requests in 3 days = 0.1 req/s
    avg = per_library * libraries
    requests = [(r["route"], r["ms"]) for r in records]  # at 0.1 req/s nothing queues: latency = service time
    mix = {route: round(sum(q == route for q, _ in requests) / len(requests), 3) for route in sorted(set(
        q for q, _ in requests))}
    return {"avg_rps": round(avg, 1), "peak_rps": round(avg * peak_factor, 1), "mix": mix,
            "requests": requests, "mean_service_ms": round(statistics.fmean(ms for _, ms in requests), 1)}


def littles_law(rate_per_s, time_in_system_ms):
    return rate_per_s * time_in_system_ms / 1000  # L = lambda x W


def simulate(rate, service_ms, workers=WORKERS, n=20000, seed=21):
    """FCFS queue with `workers` servers, Poisson arrivals: returns latency percentiles and utilization."""
    rng, t, free = random.Random(seed), 0.0, [0.0] * workers  # heap of the times each worker becomes free
    latencies, busy = [], 0.0
    for _ in range(n):
        t += rng.expovariate(rate)  # next arrival (seconds)
        s = rng.choice(service_ms) / 1000
        start = max(t, heapq.heappop(free))  # wait for the first free worker
        heapq.heappush(free, start + s)
        latencies.append((start + s - t) * 1000)
        busy += s
    latencies.sort()
    return {"rate": rate, "p50_ms": round(latencies[n // 2], 1), "p99_ms": round(latencies[int(n * 0.99)], 1),
            "utilization": round(busy / (t * workers), 2), "in_flight": round(sum(latencies) / 1000 / t, 2)}


def benchmark(model, workers=WORKERS, step=5, high=200):
    """Capacity of ONE instance: the highest arrival rate (multiple of `step`) whose simulated p99 meets the SLO.
    Binary search: p99 grows with the rate."""
    service, rows = [ms for _, ms in model["requests"]], {}
    low, high = 1, high // step  # in units of `step` req/s
    while low <= high:
        mid = (low + high) // 2
        rows[mid * step] = simulate(mid * step, service, workers)
        low, high = (mid + 1, high) if rows[mid * step]["p99_ms"] <= SLO_P99_MS else (low, mid - 1)
    return {"capacity_rps": high * step, "rows": [rows[k] for k in sorted(rows)]}


def instances_needed(model, capacity_rps):
    """How many instances to run: peak rate / (benchmarked capacity x headroom), plus one spare (N+1)."""
    serving = math.ceil(model["peak_rps"] / (capacity_rps * HEADROOM))  # peak, not average; SLO-safe capacity
    return serving + 1  # N+1: the SLO still holds while one instance is down or being deployed


def cost_per_million(instances, avg_rps, price_per_hour=0.10):
    """Hypothetical price (stated assumption, not a vendor quote): USD per instance-hour."""
    return round(instances * price_per_hour / (avg_rps * 3600) * 1e6, 2)


def change(model, route, new_ms):
    """Option helper: give `route` a new service time new_ms(old_ms, rng); recompute the mean."""
    rng = random.Random(211)
    requests = [(q, new_ms(ms, rng) if q == route else ms) for q, ms in model["requests"]]
    return {**model, "requests": requests, "mean_service_ms": round(statistics.fmean(ms for _, ms in requests), 1)}


def with_sync_email(model, email_ms=150.0):
    """The new LoanCreated email sent INSIDE POST /loans (stated relay time 150 ms per email)."""
    return change(model, "POST /loans", lambda ms, rng: ms + email_ms)


def with_cache(model, hit_ratio, hit_ms=2.0):
    """Cache GET /books: a hit costs hit_ms instead of the measured service time."""
    return change(model, "GET /books", lambda ms, rng: hit_ms if rng.random() < hit_ratio else ms)


def lru_hit_ratio(size=500, books=5000, requests=20000, seed=212):
    """Measured, not assumed: a seeded Zipf-like book popularity through an LRU cache of `size` entries."""
    rng, cache, hits = random.Random(seed), {}, 0
    weights = [1 / (rank + 1) for rank in range(books)]
    for book in rng.choices(range(books), weights, k=requests):
        if book in cache:
            hits += 1
            cache[book] = cache.pop(book)  # move to the most-recent end
        else:
            cache[book] = True
            if len(cache) > size:
                cache.pop(next(iter(cache)))  # evict the least recently used
    return round(hits / requests, 3)
