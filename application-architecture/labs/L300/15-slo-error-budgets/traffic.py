"""Seeded request log for Library Loans: 3 days, one JSON object per request. Not lesson code.

Normal traffic: ~45 ms, rare 5xx. Seeded fault (incident=True): from 10:30 UTC on the last day, 20% of
POST /loans hit a slow path (2.4-3.0 s, lock contention). Everything else stays healthy.
"""
import functools
import json
import random
from datetime import datetime, timedelta, timezone

END = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
INCIDENT_START = datetime(2026, 10, 28, 10, 30, tzinfo=timezone.utc)
ROUTES = [("GET /books", 0.45), ("GET /loans", 0.35), ("POST /loans", 0.20)]


def requests(seed=15, days=3, every_s=10, incident=True, slow_share=0.20):
    rng = random.Random(seed)
    t = END - timedelta(days=days)
    while t < END:
        route = rng.choices([r for r, _ in ROUTES], [w for _, w in ROUTES])[0]
        ms = round(rng.lognormvariate(3.75, 0.35), 1)  # median e^3.75 = 42.5 ms
        status = 500 if rng.random() < 0.0002 else 200
        if incident and t >= INCIDENT_START and route == "POST /loans" and rng.random() < slow_share:
            ms = round(rng.uniform(2400, 3000), 1)  # the slow path
        yield {"ts": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "route": route, "status": status, "ms": ms}
        t += timedelta(seconds=every_s)


@functools.lru_cache(maxsize=8)  # the same seed gives the same log: build it once per process
def lines(**options):
    return tuple(json.dumps(record) for record in requests(**options))


def write_log(path, **options):
    path.write_text("\n".join(lines(**options)) + "\n", encoding="utf-8")  # one write: fast on network drives
