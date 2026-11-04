"""tryIt experiments for lesson 3 (python try_it.py). Prints what actually happens."""
import time

import timeouts as t

b = t.start_b()
base = f"http://127.0.0.1:{b.server_port}/work?delay="

# tryIt 1: same timeout (0.1 s), B answers in 0.05 s vs 0.2 s
for delay in ("0.05", "0.2"):
    result, took = t.call(base + delay, timeout=0.1)
    print(f"tryIt 1: delay={delay:<4} timeout=0.1 -> {result}")

# tryIt 2: one 0.5 s deadline shared by two sequential calls that each take 0.3 s
deadline = time.monotonic() + 0.5
for hop in (1, 2):
    remaining = deadline - time.monotonic()  # pass the remaining budget, not a fresh timeout
    result, took = t.call(base + "0.3", timeout=remaining)
    print(f"tryIt 2: call {hop} timeout={remaining:.1f} s -> {result} after {took:.1f} s")
b.shutdown()
