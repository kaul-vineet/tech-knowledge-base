"""Seeded fine requests (not lesson code): 30 % students, days late 0-60 (most loans are a little late)."""
import random


def requests(n=2000, seed=17):
    rng = random.Random(seed)
    for i in range(n):
        days = min(60, int(rng.expovariate(1 / 6)))  # mean ~6 days late, long tail
        yield {"member_id": f"m{rng.randrange(500)}", "member_type": "student" if rng.random() < 0.3 else "adult",
               "days_late": days, "seq": i}
