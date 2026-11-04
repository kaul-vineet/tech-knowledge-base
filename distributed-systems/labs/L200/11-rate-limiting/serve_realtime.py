"""Tool target for lesson 11: the lesson's Api (token bucket, 429 + Retry-After) on a REAL clock, so an
external load tool such as k6 (load_test.js) can hit it. The lab demo uses a simulated clock instead.

python serve_realtime.py            # serve http://127.0.0.1:8011/data until Ctrl+C (LAB_PORT overrides)
python serve_realtime.py --check    # same open-model load as load_test.js, sent from Python: 200/429 split
"""
import argparse, os, time

import ratelimit as rl
from helpers import call, serve

PORT = int(os.environ.get("LAB_PORT", "8011"))
RATE_PER_S, SECONDS = 10, 10  # load_test.js: constant-arrival-rate 10 requests/s for 10 s, one client id


def start(port=PORT):
    rl.Api.clock, rl.Api.limiters, rl.Api.make_limiter = time.monotonic, {}, None  # real clock, fresh buckets
    return serve(rl.Api, port)


def check(url, rate=RATE_PER_S, seconds=SECONDS):
    """Send rate*seconds requests at fixed start times (open model, like k6). Returns the counts."""
    counts, no_retry_after, t0 = {}, 0, time.monotonic()
    for i in range(rate * seconds):
        time.sleep(max(0.0, t0 + i / rate - time.monotonic()))
        status, _, headers = call(url, headers={"X-Client-Id": "k6"})
        counts[status] = counts.get(status, 0) + 1
        no_retry_after += status == 429 and not headers.get("Retry-After")
    return counts, no_retry_after


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    srv = start(0 if args.check else PORT)
    url = f"http://127.0.0.1:{srv.server_port}/data"
    if args.check:
        counts, missing = check(url)
        total = sum(counts.values())
        print(f"{total} requests at {RATE_PER_S}/s for {SECONDS} s (limit {rl.RATE:g}/s, burst {rl.BURST}): "
              f"200={counts.get(200, 0)} 429={counts.get(429, 0)} -> 429 share {counts.get(429, 0) / total:.0%}; "
              f"429 without Retry-After: {missing}")
    else:
        print(f"serving {url} (limit {rl.RATE:g}/s, burst {rl.BURST} per X-Client-Id); Ctrl+C to stop")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass
    srv.shutdown()
    srv.server_close()
