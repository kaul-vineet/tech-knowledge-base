"""L300 lesson 16 (python backpressure.py): a server with 4 workers (10 ms per request on average, so capacity
is 400 requests/s) and a queue in front of them. Open-model load (Poisson, seeded): clients keep sending no
matter how slow the server gets. Part 1 measures queueing delay vs throughput as load approaches capacity.
Part 2 is the fault: a 10 s burst at 150% of capacity, with per-second metrics as JSON lines.
The lesson server's queue is unbounded - watch p99 and how long the server stays slow after the burst."""
import json
from collections import deque

from helpers import simulate

WORKERS, SERVICE_MS = 4, 10.0
CAPACITY = WORKERS * 1000 / SERVICE_MS  # 400 requests/s
TIMEOUT_MS = 1000  # clients give up after 1 s: work finished later is wasted


class Server:
    def __init__(self, workers=WORKERS):
        self.workers, self.queue = workers, deque()

    def admit(self, now):
        """Admission control: return None to queue the request, or Retry-After seconds to shed it with a 503."""
        return None  # unbounded queue: everything waits, however long the line already is


def pct(values, p):
    values = sorted(values)
    return values[min(len(values) - 1, int(p / 100 * len(values)))] if values else 0.0


def summary(records):
    ok = [r for r in records if r["status"] == 200]
    lat = [r["end"] - r["arrive"] for r in ok]
    secs = (max(r["end"] for r in records) - min(r["arrive"] for r in records)) / 1000
    return {"offered": len(records), "ok": len(ok), "shed": sum(r["status"] == 503 for r in records),
            "throughput_per_s": round(len(ok) / secs), "mean_wait_ms": round(sum(r["start"] - r["arrive"] for r in ok) / max(1, len(ok)), 1),
            "p50_ms": round(pct(lat, 50), 1), "p99_ms": round(pct(lat, 99), 1),
            "goodput": sum(l <= TIMEOUT_MS for l in lat)}  # answered before the client gave up


def per_second(records):
    """Metrics a dashboard would scrape: one JSON line per second of arrival time."""
    lines = []
    for sec in range(int(max(r["arrive"] for r in records) // 1000) + 1):
        rs = [r for r in records if sec * 1000 <= r["arrive"] < (sec + 1) * 1000]
        lat = [r["end"] - r["arrive"] for r in rs if r["status"] == 200]
        lines.append(json.dumps({"t": sec, "offered": len(rs), "ok": len(lat), "shed": sum(r["status"] == 503 for r in rs),
                                 "p99_ms": round(pct(lat, 99))}))
    return lines


BURST = [(5, 0.6 * CAPACITY), (10, 1.5 * CAPACITY), (15, 0.6 * CAPACITY)]

if __name__ == "__main__":
    print(f"capacity {CAPACITY:.0f} requests/s ({WORKERS} workers x {SERVICE_MS:.0f} ms)")
    print("1) load sweep, 20 s each:  load  throughput/s  mean wait  p99")
    for load in (0.5, 0.8, 0.9, 0.95):
        s = summary(simulate(Server(), [(20, load * CAPACITY)], SERVICE_MS))
        print(f"{load:>28.0%} {s['throughput_per_s']:>10} {s['mean_wait_ms']:>9} ms {s['p99_ms']:>6} ms")
    records = simulate(Server(), BURST, SERVICE_MS)
    print("2) burst: 5 s at 60%, 10 s at 150%, 15 s at 60% - per-second metrics (JSON lines):")
    print(*per_second(records)[3:30:3], sep="\n")
    print("summary:", json.dumps(summary(records)))
