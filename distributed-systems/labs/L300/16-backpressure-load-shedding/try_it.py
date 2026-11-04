"""tryIt experiments for lesson 16 (python try_it.py). Prints what actually happens (simulated, seeded)."""
import solution_backpressure as sol
from aimd import AIMDLimit
from helpers import simulate

# tryIt 1: how big should the bounded queue be? Same burst, three bounds.
for bound in (10, 40, 400):
    s = sol.summary(simulate(sol.Server(max_queue=bound), sol.BURST, sol.SERVICE_MS))
    print(f"tryIt 1: max_queue {bound:>3}: p99 {s['p99_ms']:>6} ms, shed {s['shed']:>4}, ok {s['ok']}, goodput {s['goodput']}")

# tryIt 2: the same burst, now the callers also run an AIMD concurrency limit
for name, limiter in (("no client limit", None), ("AIMD client limit", AIMDLimit())):
    recs = simulate(sol.Server(), sol.BURST, sol.SERVICE_MS, limiter=limiter)
    s = sol.summary(recs)
    local = sum(r["status"] == "local" for r in recs)
    print(f"tryIt 2: {name}: 503s the server had to send {s['shed']}, rejected locally {local}, ok {s['ok']}, p99 {s['p99_ms']} ms"
          + (f", final limit {limiter.limit:.1f}" if limiter else ""))
