"""tryIt experiments for lesson 7 (python try_it.py). Prints what actually happens."""
import election as el

PAUSE = {3: ("n1", "pause"), 7: ("n1", "resume")}

# tryIt 1: same pause/resume, but the storage does NOT check fencing tokens
out = el.simulate(events=PAUSE, fencing=False, quiet=True)
stale = [l for l in out["log"] if l.startswith("t=7 n1 writes")][0]
print("tryIt 1: fencing off ->", stale.split(": ", 1)[1], "| n1's stale write landed after n2's write at t=6")

# tryIt 2: TTL 6 s instead of 3 s, same 4-tick pause (t=3..6)
for ttl in (3.0, 6.0):
    el.TTL = ttl
    out = el.simulate(events=PAUSE, quiet=True)
    holders = "".join((h or "-")[-1] for _, h, _ in out["holders"])
    takeover = next((t for t, h, _ in out["holders"] if h and h != "n1"), None)
    print(f"tryIt 2: TTL {ttl:.0f} s -> holder per tick {holders} |",
          f"n2 takes over at t={takeover}" if takeover else "no failover: n1 renewed in time after its pause")
el.TTL = 3.0
