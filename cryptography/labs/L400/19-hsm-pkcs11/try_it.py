"""Try it: two experiments on hardware-style key storage (run: python try_it.py)."""
import statistics
import time

import solution_nonexportable as tok

# 1) PIN guessing: three wrong PINs, then the RIGHT one. What does the token say?
t = tok.SoftToken("kb-l19", so_pin="so-demo-1234", user_pin="user-demo-5678")
s = t.open_session()
answers = []
for pin in ("0000", "1111", "2222", "user-demo-5678"):
    try:
        s.login("USER", pin)
        answers.append("OK")
    except tok.PKCS11Error as e:
        answers.append(str(e))
print("1) logins:", answers)

# 2) What does "sign via a handle" cost compared with holding the key bytes? (median of 500, microseconds)
t2 = tok.SoftToken("kb-l19b", so_pin="so", user_pin="pin")
s2 = t2.open_session()
s2.login("USER", "pin")
_, priv = s2.generate_key_pair(tok.CKM_EDDSA, "bench")
raw = t2._objects[priv]["key"]  # only possible because this token is software: a real HSM has no such door


def med(fn, n=500):
    runs = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        runs.append((time.perf_counter() - t0) * 1e6)
    return statistics.median(runs)


h, r = med(lambda: s2.sign(priv, tok.CKM_EDDSA, b"m")), med(lambda: raw.sign(b"m"))
print(f"2) sign via handle {h:.1f} us vs raw key {r:.1f} us (overhead {h / r:.2f}x, plus one audit event per call:"
      f" {len(t2.audit)} events)")
