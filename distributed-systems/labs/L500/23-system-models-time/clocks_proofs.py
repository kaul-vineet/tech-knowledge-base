"""Lesson 23 numerical checks (stdlib only, seeded: identical output on every run and OS).

python clocks_proofs.py            all four checks (this output is quoted in content/L500.json)
python clocks_proofs.py clock      one check: clock | vector | safety | detector

T23.1 Lamport clock condition: a -> b implies L(a) < L(b); (L, pid) is a total order extending ->.
T23.2 Vector clocks characterise causality: a -> b iff V(a) < V(b); concurrent iff incomparable.
T23.3 Safety vs liveness (Alpern & Schneider 1985) on every trace up to length 8.
T23.4 No timeout is an accurate failure detector without a delay bound (asynchrony vs synchrony).
"""
import itertools
import random
import sys


# ---------- random message-passing executions ----------
def random_execution(rng, n_proc=3, n_events=14):
    """Return events [(pid, kind, msg)] in a valid global order; receives may be out of send order."""
    events, in_flight, next_msg = [], [], 0
    for _ in range(n_events):
        pid = rng.randrange(n_proc)
        mine = [m for m in in_flight if m[1] == pid]
        roll = rng.random()
        if mine and roll < 0.4:
            m = rng.choice(mine)  # any pending message: the network may reorder
            in_flight.remove(m)
            events.append((pid, "recv", m[0]))
        elif roll < 0.75:
            dest = rng.choice([q for q in range(n_proc) if q != pid])
            in_flight.append((next_msg, dest))
            events.append((pid, "send", next_msg))
            next_msg += 1
        else:
            events.append((pid, "local", None))
    return events


def happened_before(events):
    """hb[i] = set of j with event i -> event j (smallest transitive relation of Lamport's definition)."""
    succ = {i: set() for i in range(len(events))}
    last, sender = {}, {}
    for i, (pid, kind, msg) in enumerate(events):
        if pid in last:
            succ[last[pid]].add(i)          # rule 1: same process, program order
        last[pid] = i
        if kind == "send":
            sender[msg] = i
        elif kind == "recv":
            succ[sender[msg]].add(i)        # rule 2: send -> receive
    hb = {}
    for i in range(len(events)):            # rule 3: transitive closure (DFS)
        seen, stack = set(), list(succ[i])
        while stack:
            j = stack.pop()
            if j not in seen:
                seen.add(j)
                stack.extend(succ[j])
        hb[i] = seen
    return hb


def lamport(events, n_proc, merge=True):
    """IR1: tick before every event; IR2: on receive set C = max(C, T_m) + 1. merge=False drops the max."""
    c, stamp, out = [0] * n_proc, {}, []
    for pid, kind, msg in events:
        if kind == "recv" and merge:
            c[pid] = max(c[pid], stamp[msg]) + 1
        else:
            c[pid] += 1
        if kind == "send":
            stamp[msg] = c[pid]
        out.append(c[pid])
    return out


def vector(events, n_proc, merge=True):
    v, stamp, out = [[0] * n_proc for _ in range(n_proc)], {}, []
    for pid, kind, msg in events:
        if kind == "recv" and merge:
            v[pid] = [max(a, b) for a, b in zip(v[pid], stamp[msg])]
        v[pid][pid] += 1
        if kind == "send":
            stamp[msg] = list(v[pid])
        out.append(tuple(v[pid]))
    return out


def vless(a, b):
    return all(x <= y for x, y in zip(a, b)) and a != b


def check_clock(runs=300, seed=23):
    rng = random.Random(seed)
    pairs = hb_pairs = viol = viol_broken = conc = conc_ordered = total_bad = 0
    for _ in range(runs):
        ev = random_execution(rng)
        hb, lam, bad = happened_before(ev), lamport(ev, 3), lamport(ev, 3, merge=False)
        for a, b in itertools.permutations(range(len(ev)), 2):
            pairs += 1
            if b in hb[a]:
                hb_pairs += 1
                viol += lam[a] >= lam[b]
                viol_broken += bad[a] >= bad[b]
                # total order (L, pid) must put a before b
                total_bad += (lam[a], ev[a][0]) >= (lam[b], ev[b][0])
            elif a not in hb[b]:
                conc += 1
                conc_ordered += lam[a] < lam[b]
    # strict total order on distinct events: (L, pid) keys are unique within one execution
    rng = random.Random(seed)
    dup_keys = 0
    for _ in range(runs):
        ev = random_execution(rng)
        keys = [(t, e[0]) for t, e in zip(lamport(ev, 3), ev)]
        dup_keys += len(keys) - len(set(keys))
    return [
        f"T23.1 Lamport clock condition: {runs} random executions, 3 processes, {pairs:,} ordered event pairs",
        f"  pairs with a->b: {hb_pairs:,}; violations of L(a) < L(b): {viol}",
        f"  (L, pid) total order: duplicate keys {dup_keys}; a->b ordered the other way {total_bad}",
        f"  converse fails: {conc_ordered:,} of {conc:,} concurrent pairs still have L(a) < L(b)",
        f"  broken receive rule (tick only, no max): {viol_broken:,} violations",
    ]


def check_vector(runs=300, seed=23):
    rng = random.Random(seed)
    pairs = mism = mism_broken = conc = incomparable = 0
    for _ in range(runs):
        ev = random_execution(rng)
        hb, vc, bad = happened_before(ev), vector(ev, 3), vector(ev, 3, merge=False)
        for a, b in itertools.permutations(range(len(ev)), 2):
            pairs += 1
            mism += (b in hb[a]) != vless(vc[a], vc[b])
            mism_broken += (b in hb[a]) != vless(bad[a], bad[b])
            if b not in hb[a] and a not in hb[b]:
                conc += 1
                incomparable += not vless(vc[a], vc[b]) and not vless(vc[b], vc[a])
    return [
        f"T23.2 vector clocks: same {runs} executions, {pairs:,} ordered pairs",
        f"  mismatches between a->b and V(a) < V(b): {mism}",
        f"  concurrent pairs {conc:,}; incomparable vectors {incomparable:,}",
        f"  broken receive rule (no element-wise max): {mism_broken:,} mismatches",
    ]


# ---------- safety vs liveness on finite traces ----------
ALPHABET = ("req", "resp", "idle")


def bad_prefix(trace):
    """Safety 'never answer more requests than were made': violated at the first prefix with resp > req."""
    open_ = 0
    for i, e in enumerate(trace):
        open_ += (e == "req") - (e == "resp")
        if open_ < 0:
            return i + 1
    return None


def outstanding(trace):
    return trace.count("req") - trace.count("resp")


def check_safety(max_len=8, ext_len=3):
    traces = [t for n in range(max_len + 1) for t in itertools.product(ALPHABET, repeat=n)]
    good = {t for t in traces if bad_prefix(t) is None}
    not_closed = sum(1 for t in good for k in range(len(t)) if t[:k] not in good)
    irremediable = 0
    for t in traces:
        if bad_prefix(t) is not None:
            for n in range(1, ext_len + 1):
                for ext in itertools.product(ALPHABET, repeat=n):
                    irremediable += bad_prefix(t + ext) is None
    # liveness "every request is eventually answered": every finite good prefix can be completed
    unextendable = sum(1 for t in good if bad_prefix(t + ("resp",) * outstanding(t)) is not None
                       or outstanding(t + ("resp",) * outstanding(t)) != 0)
    return [
        f"T23.3 safety vs liveness: all {len(traces):,} traces over {{req, resp, idle}} up to length {max_len}",
        f"  safety S = 'never more responses than requests': {len(good):,} good traces, {len(traces) - len(good):,} bad",
        f"  S prefix-closed: good traces with a bad prefix = {not_closed}",
        f"  bad traces repaired by any extension up to length {ext_len}: {irremediable}",
        f"  liveness L = 'every request eventually answered': good prefixes that cannot be completed = {unextendable}",
    ]


# ---------- failure detection: synchronous vs asynchronous ----------
def check_detector(samples=200_000, seed=4):
    rng = random.Random(seed)
    # asynchronous: no bound, heavy tail (Pareto, alpha = 1.5, minimum 1 ms)
    delays = [rng.paretovariate(1.5) for _ in range(samples)]
    lines = ["T23.4 failure detection: round-trip heartbeat, live peer, 200,000 heartbeats each",
             "  asynchronous model (Pareto alpha=1.5, min 1 ms, no upper bound): timeout -> false suspicions"]
    for timeout in (5, 20, 100, 1000):
        false_ = sum(d > timeout for d in delays)
        lines.append(f"    {timeout:>5} ms -> {false_:>6,} ({false_ / samples:.4%}); theory {timeout ** -1.5:.4%}")
    rng = random.Random(seed)
    delta = 50.0  # synchronous: every one-way delay <= delta and processing <= 5 ms
    rtts = [rng.uniform(0, delta) + rng.uniform(0, 5) + rng.uniform(0, delta) for _ in range(samples)]
    lines.append(f"  synchronous model (one-way <= 50 ms, processing <= 5 ms): timeout 105 ms -> "
                 f"{sum(r > 2 * delta + 5 for r in rtts)} false suspicions; max observed {max(rtts):.1f} ms")
    return lines


CHECKS = {"clock": check_clock, "vector": check_vector, "safety": check_safety, "detector": check_detector}


def main(argv):
    names = argv[1:] or list(CHECKS)
    for name in names:
        print("\n".join(CHECKS[name]()))


if __name__ == "__main__":
    main(sys.argv)
