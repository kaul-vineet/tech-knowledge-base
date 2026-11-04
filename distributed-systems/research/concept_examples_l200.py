"""Computes every number used in the worked examples of content/concepts/L200/*.md by running the labs.
Run from the domain folder:  python research/concept_examples_l200.py   (takes ~40 s: lesson 8's tryIt loop)"""
import contextlib, importlib, io, math, sys
from pathlib import Path

LABS = Path(__file__).resolve().parent.parent / "labs" / "L200"


def load(lab, module):
    for name in ("helpers", module):  # every lab has its own helpers.py
        sys.modules.pop(name, None)
    sys.path.insert(0, str(LABS / lab))
    try:
        return importlib.import_module(module)
    finally:
        sys.path.pop(0)


print("== 07 leases ==")
el = load("07-leader-election-leases", "election")
out = el.simulate(events={3: ("n1", "pause"), 7: ("n1", "resume")}, quiet=True)
takeover = next(t for t, h, _ in out["holders"] if h == "n2")
print("last renewal t=2 + TTL", el.TTL, "-> takeover at t =", takeover, "| tokens:", sorted({tok for _, _, tok in out["holders"]}))
print([l for l in out["log"] if "REJECTED" in l])

print("== 08 at-least-once ==")
br = load("08-at-least-once-messaging", "broker")
out = br.run(quiet=True)
print([l for l in out["log"] if "m5=" in l])
print("charges", len(out["ledger"]), "orders", len({i for i, _ in out["ledger"]}), "| DLQ", out["dlq"])
for limit in (2, 5):
    br.MAX_RECEIVES = limit
    print(f"MAX_RECEIVES {limit}: good order dead-lettered in",
          sum(any(x != "poison" for x in br.run(seed=s, quiet=True)["dlq"]) for s in range(30)), "of 30 runs")
br.MAX_RECEIVES = 3

print("== 09 consistent hashing ==")
ring = load("09-consistent-hashing", "ring")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    ring.main()
print(buf.getvalue().strip())
print("P(h % 4 == h % 5) over 0..19 =", sum(h % 4 == h % 5 for h in range(20)) / 20, "-> ~80% move")

print("== 10 caching ==")
cache = load("10-caching-invalidation", "cache")
with contextlib.redirect_stdout(buf := io.StringIO()):
    cache.main()
print(buf.getvalue().strip())

print("== 11 rate limiting ==")
rl = load("11-rate-limiting", "ratelimit")
print("6th request wait = (1 - 0) /", rl.RATE, "=", (1 - 0) / rl.RATE, "s -> Retry-After", max(1, math.ceil((1 - 0) / rl.RATE)))
out = rl.run({"alice": (12, True), "bob": (12, False), "carol": (3, True)})
print({n: (s["ok"], s["429"], s["done"]) for n, s in out.items()})
