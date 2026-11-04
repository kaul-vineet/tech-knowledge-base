"""Try it: two small experiments on password hashing (run: python try_it.py)."""
import time

import passwords as lab


def timed_hash(pw: str):
    t = time.perf_counter()
    h = lab.hash_password(pw)
    return h, time.perf_counter() - t


# 1) Double the Argon2id memory cost; old hashes must still verify (params live in the PHC string).
old, t_old = timed_hash("hunter2")
lab.ARGON2ID = {**lab.ARGON2ID, "memory_cost": 2 * 19456}
new, t_new = timed_hash("hunter2")
print("1) new PHC prefix:", new[:31], f"| time {t_old:.3f}s -> {t_new:.3f}s (x{t_new / t_old:.1f})")
print("   old m=19456 hash still verifies:", lab.verify_password("hunter2", old))

# 2) Near-miss passwords: trailing space and different case.
for guess in ("hunter2", "hunter2 ", "Hunter2"):
    print(f"2) verify {guess!r:11} ->", lab.verify_password(guess, new))
