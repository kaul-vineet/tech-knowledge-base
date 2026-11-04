"""A small closed-model load test (stdlib): `users` threads each send `requests_per_user` GETs back to back.

k6/overdue.js is the same test for Grafana k6 (open-source, AGPL-3.0), with thresholds as the CI gate.
Run: python load_test.py http://127.0.0.1:8016/reports/overdue
"""
import json
import sys
import threading
import time
import urllib.request


def percentile(values, p):  # nearest-rank
    ordered = sorted(values)
    return ordered[max(0, -(-len(ordered) * p // 100) - 1)]


def run_load(url, users=8, requests_per_user=10):
    timings, errors, lock = [], [0], threading.Lock()
    with urllib.request.urlopen(url, timeout=5) as resp:  # warm-up request, not measured
        resp.read()

    def user():
        for _ in range(requests_per_user):
            started = time.perf_counter()
            try:
                with urllib.request.urlopen(url, timeout=5) as resp:
                    resp.read()
                    ok = resp.status == 200
            except OSError:
                ok = False
            with lock:
                timings.append((time.perf_counter() - started) * 1000)
                errors[0] += not ok

    threads = [threading.Thread(target=user) for _ in range(users)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return {"requests": len(timings), "errors": errors[0], "p50_ms": round(percentile(timings, 50), 1),
            "p95_ms": round(percentile(timings, 95), 1), "max_ms": round(max(timings), 1)}


if __name__ == "__main__":
    print(json.dumps(run_load(sys.argv[1])))
