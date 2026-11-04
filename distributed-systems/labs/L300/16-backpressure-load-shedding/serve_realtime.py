"""Tool target for lesson 16: the solution's admission control on a REAL clock and real threads, so an external
load tool such as k6 (load_test.js) can push it past capacity. 4 workers x 50 ms = 80 requests/s capacity,
queue bound 8 (= 100 ms of waiting). The lab demo uses a simulated clock instead.

python serve_realtime.py              # serve http://127.0.0.1:8016/work until Ctrl+C (LAB_PORT overrides)
python serve_realtime.py --unbounded  # the lesson's behaviour: no bound, no 503
python serve_realtime.py --check      # the same open-model load as load_test.js, sent from Python
"""
import argparse, os, threading, time

from http_helpers import QuietHandler, call, serve

PORT = int(os.environ.get("LAB_PORT", "8016"))
WORKERS, SERVICE_S, MAX_QUEUE = 4, 0.05, 8
RATE_PER_S, SECONDS = 120, 10  # load_test.js: constant-arrival-rate 120/s (150% of 80/s) for 10 s


class Work(QuietHandler):
    bounded, waiting, lock, workers = True, 0, threading.Lock(), threading.Semaphore(WORKERS)

    def do_GET(self):
        cls = type(self)
        with cls.lock:
            if cls.bounded and cls.waiting >= MAX_QUEUE:  # admission control: shed at the door
                return self.reply(503, {"error": "overloaded"}, {"Retry-After": "1"})
            cls.waiting += 1
        with cls.workers:  # wait for one of the 4 workers (this wait IS the queue)
            with cls.lock:
                cls.waiting -= 1
            time.sleep(SERVICE_S)
        self.reply(200, {"ok": True})


def start(port=PORT, bounded=True):
    Work.bounded, Work.waiting = bounded, 0
    return serve(Work, port)


def check(url, rate=RATE_PER_S, seconds=SECONDS):
    """Open model like k6: request i starts at t0 + i/rate on its own thread, whatever the server does."""
    results, lock, threads, t0 = [], threading.Lock(), [], time.monotonic()

    def one():
        start = time.monotonic()
        status, _, headers = call(url, timeout=30)
        with lock:
            results.append((status, (time.monotonic() - start) * 1000, headers.get("Retry-After")))
    for i in range(rate * seconds):
        time.sleep(max(0.0, t0 + i / rate - time.monotonic()))
        threads.append(threading.Thread(target=one))
        threads[-1].start()
    for th in threads:
        th.join()
    ok = sorted(ms for status, ms, _ in results if status == 200)
    return {"200": len(ok), "503": sum(s == 503 for s, _, _ in results),
            "p99_ms": round(ok[int(0.99 * (len(ok) - 1))]) if ok else None,
            "503_without_retry_after": sum(s == 503 and not ra for s, _, ra in results)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--unbounded", action="store_true")
    args = ap.parse_args()
    srv = start(0 if args.check else PORT, bounded=not args.unbounded)
    url = f"http://127.0.0.1:{srv.server_port}/work"
    if args.check:
        print(f"{RATE_PER_S * SECONDS} requests at {RATE_PER_S}/s for {SECONDS} s (capacity 80/s, "
              f"{'queue bound ' + str(MAX_QUEUE) if not args.unbounded else 'unbounded queue'}):", check(url))
    else:
        print(f"serving {url} ({WORKERS} workers x {SERVICE_S * 1000:.0f} ms, bounded={not args.unbounded}); Ctrl+C to stop")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass
    srv.shutdown()
    srv.server_close()
