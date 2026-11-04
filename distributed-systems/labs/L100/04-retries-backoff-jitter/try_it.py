"""tryIt experiments for lesson 4 (python try_it.py). Prints what actually happens."""
import random
from collections import Counter

import retries as r


# tryIt 1: phase 1 of the demo (B 30% 503, same seeds) with max_attempts=1 vs the default 4
def phase1(max_attempts):
    r.FlakyB.rng, r.FlakyB.fail_rate = random.Random(42), 0.3
    srv = r.serve(r.FlakyB)
    url, rng, budget = f"http://127.0.0.1:{srv.server_port}/data", random.Random(7), r.RetryBudget()
    out = [r.get_with_retry(url, rng, budget, max_attempts, sleep=lambda s: None) for _ in range(10)]
    srv.shutdown(); srv.server_close()
    return sum(o == 200 for o, _, _ in out), sum(n for _, n, _ in out)


for m in (1, 4):
    ok, attempts = phase1(m)
    print(f"tryIt 1: max_attempts={m}: {ok}/10 succeeded, {attempts} attempts")

# tryIt 2: 100 clients fail together and back off after attempt 2 (ceiling 0.08 s)
rng = random.Random(7)
no_jitter = [min(0.5, 0.02 * 2 ** 2)] * 100
full_jitter = [r.backoff_full_jitter(2, rng) for _ in range(100)]
for name, sleeps in (("no jitter", no_jitter), ("full jitter", full_jitter)):
    busiest = max(Counter(int(s * 1000) // 10 for s in sleeps).values())  # 10 ms slots
    print(f"tryIt 2: {name:<11}: busiest 10 ms slot has {busiest} of 100 retries")
