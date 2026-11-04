"""tryIt experiments for lesson 17 (python try_it.py). Prints what actually happens."""
import helpers
import quorum

# tryIt 1: remove the slow-message tail (TAIL_P 5% -> 0%). Does R=2 W=2 still show new-then-old inversions?
for tail in (0.05, 0.0):
    helpers.TAIL_P = tail
    m = quorum.measure(2, 2)
    print(f"tryIt 1: TAIL_P={tail:.2f}: R=2 W=2 inversions={m['inversions']} read p99={m['read_p99']} ms"
          f" write p99={m['write_p99']} ms")
helpers.TAIL_P = 0.05

# tryIt 2: partition: the clients can reach only replica a (b and c cut off). Which settings still answer?
for r, w, wb in quorum.SETTINGS:
    hist = quorum.run(r, w, down=("b", "c"), write_back=wb)
    avail = {f: round(100 * sum(o["ok"] for o in hist if o["f"] == f) / sum(o["f"] == f for o in hist), 1)
             for f in ("read", "write")}
    print(f"tryIt 2: R={r} W={w}{' +wb' if wb else ''}: reads {avail['read']}% writes {avail['write']}% answered")
