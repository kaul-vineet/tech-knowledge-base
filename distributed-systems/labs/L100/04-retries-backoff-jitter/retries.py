"""L100 (python retries.py): retry a flaky B (~30% 503s) with capped exponential backoff + full
jitter, then make B "sick" (90% 503s) and watch the retry budget stop a retry storm. Seeded."""
import random, time
from urllib.error import HTTPError, URLError

from helpers import OPENER, FlakyB, serve  # plumbing + the simulated flaky service B

RETRYABLE_STATUS = {429, 502, 503, 504}  # retry only transient errors; 400/404 won't fix themselves


def backoff_full_jitter(attempt, rng, base=0.02, cap=0.5):
    # capped exponential backoff: ceiling = min(cap, base*2^attempt); full jitter: uniform(0, it)
    return rng.uniform(0, min(cap, base * 2 ** attempt))


class RetryBudget:  # retry budget (gRPC-style token bucket): failure -1, success +ratio
    def __init__(self, max_tokens=10, ratio=0.5):
        self.max, self.ratio, self.tokens = max_tokens, ratio, float(max_tokens)

    def record(self, ok):
        self.tokens = min(self.max, self.tokens + self.ratio) if ok else max(0.0, self.tokens - 1)

    def can_retry(self):  # only retry while tokens >= max/2: a sick B gets no retry storm
        return self.tokens >= self.max / 2


def is_retryable(exc):
    if isinstance(exc, HTTPError):  # check first: HTTPError is a subclass of URLError
        return exc.code in RETRYABLE_STATUS
    return isinstance(exc, (URLError, TimeoutError, ConnectionError))


def get_with_retry(url, rng, budget, max_attempts=4, sleep=time.sleep):
    """Returns (outcome, attempts, sleeps). Bounded: never more than max_attempts tries."""
    sleeps = []
    for attempt in range(max_attempts):
        try:
            with OPENER.open(url, timeout=1.0) as r:
                budget.record(True)
                return r.status, attempt + 1, sleeps
        except Exception as exc:
            if retryable := is_retryable(exc):  # 404 = our bug, not B's health: budget untouched
                budget.record(False)
            if not retryable or attempt + 1 == max_attempts:
                return f"gave up ({getattr(exc, 'code', type(exc).__name__)})", attempt + 1, sleeps
            if not budget.can_retry():
                return "gave up (retry budget empty)", attempt + 1, sleeps
            sleeps.append(round(backoff_full_jitter(attempt, rng), 3))
            sleep(sleeps[-1])


def main():
    rng, budget, srv = random.Random(7), RetryBudget(), serve(FlakyB)
    url = f"http://127.0.0.1:{srv.server_port}"
    print("full-jitter ceilings (s):", [min(0.5, 0.02 * 2 ** a) for a in range(6)])
    print("GET /missing ->", get_with_retry(url + "/missing", rng, budget)[:2], "(404: not retried)")
    for phase, fail_rate in (("B flaky (30% 503)", 0.3), ("B sick (90% 503)", 0.9)):
        FlakyB.fail_rate, attempts, ok = fail_rate, 0, 0
        print(f"--- {phase} ---")
        for i in range(1, 11):
            outcome, n, sleeps = get_with_retry(url + "/data", rng, budget)
            attempts, ok = attempts + n, ok + (outcome == 200)
            print(f"req {i:02d}: {str(outcome):<28} attempts={n} sleeps={sleeps} tokens={budget.tokens:.1f}")
        print(f"{ok}/10 succeeded, {attempts} attempts (load x{attempts / 10:.1f}, worst case x4.0)")
    srv.shutdown()


if __name__ == "__main__":
    main()
