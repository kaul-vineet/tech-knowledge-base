"""tryIt experiments for lesson 11 (python try_it.py). Prints what actually happens."""
import ratelimit as rl
from helpers import SimClock

# tryIt 1: "5 per second" as a FIXED window (counter reset at each whole second) vs the token bucket,
# when a client sends 5 requests at t=0.99 s and 5 more at t=1.00 s
fixed, allowed = {}, 0
for t in [0.99] * 5 + [1.00] * 5:
    window = int(t)  # fixed window = the whole second the request falls in
    fixed[window] = fixed.get(window, 0) + 1
    allowed += fixed[window] <= 5
clock = SimClock(0.99)
bucket, by_bucket = rl.TokenBucket(5.0, 5, clock), 0
for t in [0.99] * 5 + [1.00] * 5:
    clock.t = t
    by_bucket += bucket.allow()[0]
print(f"tryIt 1: 10 requests within 10 ms across a second boundary -> fixed window allows {allowed}, token bucket allows {by_bucket}")

# tryIt 2: BURST 1 instead of 5 (same 2 requests/s): what happens to the polite client?
for burst in (5, 1):
    rl.BURST = burst
    alice = rl.run({"alice": (12, True)})["alice"]
    print(f"tryIt 2: BURST {burst} -> alice {alice['ok']} ok, {alice['429']} x 429, done at t={alice['done']:g}s")
rl.BURST = 5
