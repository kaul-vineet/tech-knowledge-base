"""Plumbing for lab 16 (not the lesson's concept): a discrete-event engine. Requests arrive as a Poisson process
(open model, seeded), the server's admit() decides queue or 503, free workers take the oldest queued request,
service times are exponential (seeded). Simulated milliseconds: nothing sleeps, output is identical every run."""
import heapq, random


def simulate(server, profile, service_ms, seed=16, limiter=None):
    """profile: [(seconds, requests_per_second), ...]. limiter (optional): client-side concurrency limit with
    allow(), on_success(), on_drop(). Returns one record per request:
    {arrive, start, end, status (200 / 503 / 'local'), retry_after} - times in ms."""
    rng, events, records, t, seq = random.Random(seed), [], [], 0.0, 0
    for seconds, rate in profile:  # pre-generate arrivals segment by segment
        end = t + seconds * 1000
        while True:
            t += rng.expovariate(rate / 1000)
            if t >= end:
                t = end
                break
            seq += 1
            heapq.heappush(events, (t, seq, "arrive", {"arrive": t}))
    busy = 0

    def start_next(now):
        nonlocal busy, seq
        while busy < server.workers and server.queue:
            req = server.queue.popleft()
            req["start"], busy, seq = now, busy + 1, seq + 1
            heapq.heappush(events, (now + rng.expovariate(1 / service_ms), seq, "done", req))

    while events:
        now, _, kind, req = heapq.heappop(events)
        if kind == "arrive":
            records.append(req)
            if limiter and not limiter.allow():
                req.update(status="local", end=now)  # rejected by the caller itself: no network, no server work
                continue
            retry_after = server.admit(now)
            if retry_after is None:
                server.queue.append(req)
            else:
                req.update(status=503, end=now, retry_after=retry_after)
                limiter and limiter.on_drop()
        else:
            req.update(status=200, end=now)
            busy -= 1
            limiter and limiter.on_success()
        start_next(now)
    return records
