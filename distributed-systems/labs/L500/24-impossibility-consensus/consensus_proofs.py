"""Lesson 24 numerical checks (stdlib only, seeded: identical output on every run and OS).

python consensus_proofs.py          all four checks (this output is quoted in content/L500.json)
python consensus_proofs.py paxos    one check: generals | flp | cap | paxos

T24.1 Two generals: every protocol in a bounded family has a disagreeing (or never-attacking) run.
T24.2 FLP, illustrated: an adversarial schedule keeps safe Paxos undecided forever; random backoff ends it.
T24.3 CAP (Gilbert & Lynch 2002, Theorem 1): an always-answering register returns a stale read in a partition.
T24.4 Quorum intersection, then single-decree Paxos safety (P2c) under loss, duplication and reordering.
"""
import itertools
import random
import sys


# ---------- T24.1 two generals ----------
def generals_family(max_msgs=6):
    """Alternating messengers A->B->A...; at most M messages; X attacks iff it received >= t_X messages.
    Requirements: nobody attacks if nothing is delivered (t_X >= 1), both attack if all M are delivered,
    and they never disagree. Loss model: the first lost messenger ends the exchange, so a run is fixed
    by c = number of messages delivered (0..M). t_X = M + 1 means 'never attack'."""
    checked = failing = 0
    examples = {}
    for m in range(0, max_msgs + 1):
        for t_a, t_b in itertools.product(range(1, m + 2), repeat=2):
            checked += 1
            bad = None
            for c in range(m + 1):
                a_attacks = c // 2 >= t_a          # messages 2, 4, 6 ... go B -> A
                b_attacks = (c + 1) // 2 >= t_b    # messages 1, 3, 5 ... go A -> B
                if a_attacks != b_attacks:
                    bad = f"{c} delivered: A {'attacks' if a_attacks else 'waits'}, B {'attacks' if b_attacks else 'waits'}"
                    break
                if c == m and not a_attacks:
                    bad = f"all {m} delivered and nobody attacks"
                    break
            if bad is not None:
                failing += 1
                examples[(m, t_a, t_b)] = bad
    lines = [f"T24.1 two generals: {checked} protocols (M = 0..{max_msgs} messengers, every threshold pair)",
             f"  protocols with a disagreeing or never-attacking run: {failing}; correct protocols: {checked - failing}"]
    for m in (2, max_msgs):  # the strictest thresholds that still attack when all M arrive
        t_a, t_b = m // 2, (m + 1) // 2
        lines.append(f"  e.g. M={m}, tA={t_a}, tB={t_b}: {examples[(m, t_a, t_b)]}")
    return lines


# ---------- single-decree Paxos simulator ----------
class Paxos:
    """Acceptors keep (promised, accepted); proposers run phase 1 / phase 2 on ballots p, p+P, p+2P ..."""

    def __init__(self, n_acc=3, n_prop=3, broken=False):
        self.n_acc, self.n_prop, self.broken = n_acc, n_prop, broken
        self.maj = n_acc // 2 + 1
        self.promised = [-1] * n_acc
        self.accepted = [None] * n_acc            # (ballot, value)
        self.round = [0] * n_prop
        self.promises = [{} for _ in range(n_prop)]
        self.ballot = [None] * n_prop
        self.net = []                             # multiset of in-flight messages
        self.accept_log = []                      # (acceptor, ballot, value) every acceptance
        self.issued = []                          # (ballot, value) every accept request issued

    def start(self, p):
        b = self.round[p] * self.n_prop + p
        self.round[p] += 1
        self.ballot[p], self.promises[p] = b, {}
        for a in range(self.n_acc):
            self.net.append(("prepare", p, a, b, None))

    def deliver(self, msg):
        kind, p, a, b, payload = msg
        if kind == "prepare" and b > self.promised[a]:
            self.promised[a] = b
            self.net.append(("promise", p, a, b, self.accepted[a]))
        elif kind == "promise" and self.ballot[p] == b and a not in self.promises[p]:
            self.promises[p][a] = payload
            if len(self.promises[p]) == self.maj:   # phase 2 exactly once per ballot
                prior = [x for x in self.promises[p].values() if x is not None]
                if prior and not self.broken:
                    value = max(prior)[1]        # P2c: value of the highest-numbered accepted proposal
                else:
                    value = f"v{p}"              # broken variant ignores what phase 1 reported
                self.issued.append((b, value))
                for acc in range(self.n_acc):
                    self.net.append(("accept", p, acc, b, value))
        elif kind == "accept" and b >= self.promised[a]:
            self.promised[a] = b
            self.accepted[a] = (b, payload)
            self.accept_log.append((a, b, payload))

    def chosen(self):
        votes = {}
        for a, b, v in self.accept_log:
            votes.setdefault((b, v), set()).add(a)
        return {(b, v) for (b, v), s in votes.items() if len(s) >= self.maj}


def random_run(rng, broken, steps=250):
    px = Paxos(broken=broken)
    for _ in range(steps):
        r = rng.random()
        if r < 0.12 or not px.net:
            px.start(rng.randrange(px.n_prop))
        else:
            msg = px.net.pop(rng.randrange(len(px.net)))   # any order: reordering
            if rng.random() < 0.15:
                continue                                    # loss
            if rng.random() < 0.10:
                px.net.append(msg)                          # duplication
            px.deliver(msg)
    return px


def p2b_violations(px):
    """P2b: once (m, v) is chosen, every issued proposal numbered n > m has value v."""
    bad = 0
    for m, v in px.chosen():
        bad += sum(1 for n, w in px.issued if n > m and w != v)
    return bad


def check_paxos(runs=3000, seed=24):
    lines = []
    # quorum intersection, exhaustively
    q_pairs = q_disjoint_ok = q_disjoint_found = 0
    for n in range(1, 8):
        nodes = range(n)
        for r, w in itertools.product(range(1, n + 1), repeat=2):
            rs, ws = list(itertools.combinations(nodes, r)), list(itertools.combinations(nodes, w))
            disjoint = any(not set(x) & set(y) for x in rs for y in ws)
            q_pairs += len(rs) * len(ws)
            if r + w > n:
                q_disjoint_ok += disjoint           # must stay 0
            else:
                q_disjoint_found += disjoint        # must equal the number of (n, r, w) with r + w <= n
    configs_le = sum(1 for n in range(1, 8) for r in range(1, n + 1) for w in range(1, n + 1) if r + w <= n)
    lines += ["T24.4 quorum intersection, exhaustive for N = 1..7, every (R, W):",
              f"  {q_pairs:,} (read quorum, write quorum) pairs checked",
              f"  R + W > N with a disjoint pair: {q_disjoint_ok}; R + W <= N configurations with a disjoint pair: "
              f"{q_disjoint_found} of {configs_le}"]
    for broken in (False, True):
        rng = random.Random(seed)
        multi = p2b = decided = 0
        for _ in range(runs):
            px = random_run(rng, broken)
            values = {v for _, v in px.chosen()}
            decided += bool(values)
            multi += len(values) > 1
            p2b += p2b_violations(px) > 0
        label = "broken (ignores phase-1 values)" if broken else "correct single-decree Paxos     "
        lines.append(f"  {label}: {runs} random runs (loss 15%, dup 10%, reorder), "
                     f"decided {decided}, runs with 2 values chosen {multi}, runs violating P2b {p2b}")
    return lines


# ---------- T24.2 FLP illustrated: duelling proposers ----------
def duel(rounds):
    """Adversarial schedule: each proposer's phase 1 completes just before the other's phase 2 arrives."""
    px = Paxos(n_acc=3, n_prop=2)
    for _ in range(rounds):
        for p in (0, 1):
            px.start(p)
            for m in [m for m in px.net if m[0] == "prepare"]:   # this proposer's prepares
                px.net.remove(m)
                px.deliver(m)
            for m in [m for m in px.net if m[0] == "promise" and m[1] == p]:
                px.net.remove(m)
                px.deliver(m)                                    # queues accept(b) for p
            for m in [m for m in px.net if m[0] == "accept" and m[1] != p]:
                px.net.remove(m)
                px.deliver(m)                                    # rival's stale accepts: rejected
    return px


def backoff_rounds(rng, max_backoff=4):
    """Partial synchrony: a full proposal takes 2 time units; after a clash each proposer waits U[0, B)."""
    t = [0.0, rng.uniform(0, 0.5)]
    for attempt in range(1, 10_000):
        first, second = sorted((0, 1), key=lambda p: t[p])
        if t[second] - t[first] >= 2.0:          # first proposer finished both phases undisturbed
            return attempt
        t = [x + 2.0 + rng.uniform(0, max_backoff) for x in t]
    return None


def check_flp(rounds=1000, seed=2):
    px = duel(rounds)
    rng = random.Random(seed)
    attempts = [backoff_rounds(rng) for _ in range(10_000)]
    mean = sum(attempts) / len(attempts)
    return [f"T24.2 FLP illustrated: 2 proposers, 3 acceptors, adversarial schedule for {rounds} rounds",
            f"  ballots started {sum(px.round)}, accepts issued {len(px.issued)}, acceptances {len(px.accept_log)}, "
            f"values chosen {len({v for _, v in px.chosen()})} (safe, never live)",
            f"  with random backoff U[0, 4) after a clash (a timing assumption): 10,000 runs, all decided: "
            f"{all(a is not None for a in attempts)}, mean attempts {mean:.2f}, max {max(attempts)}"]


# ---------- T24.3 CAP ----------
def cap_run(algorithm):
    """Two groups G1 = {n1} and G2 = {n2} (CP-majority adds n3 on the n2 side of nothing: n1 is alone).
    Every message between the groups is lost. alpha_1: write v1 at n1. alpha_2: later, read at n2."""
    store = {"n1": "v0", "n2": "v0"}
    if algorithm == "CP-majority":            # n1 cannot collect 2 of 3 acks, n2 cannot collect 2 of 3 replies
        write, read = "no response (needs 2 of 3 acks)", "no response (needs 2 of 3 replies)"
    else:
        store["n1"] = "v1"                    # AP-local: write locally and ack
        # AP-sync-then-timeout: also sends v1 to n2; the message is lost; after the timeout it acks anyway
        write, read = "ok", store["n2"]       # n2 never received anything from n1
    available = not write.startswith("no response") and not read.startswith("no response")
    linearizable = not (write == "ok" and read == "v0")  # a read after a completed write must not see v0
    return [("write v1 @n1", write), ("read @n2", read)], available, linearizable


def check_cap():
    lines = ["T24.3 CAP: partition {n1} | {n2}, all messages between the groups lost; write v1 @n1, then read @n2"]
    for alg in ("AP-local", "AP-sync-then-timeout", "CP-majority"):
        hist, avail, lin = cap_run(alg)
        lines.append(f"  {alg:<22} {hist[0][1]:<32} read -> {hist[1][1]:<36} available={avail} linearizable={lin}")
    return lines


CHECKS = {"generals": generals_family, "flp": check_flp, "cap": check_cap, "paxos": check_paxos}


def main(argv):
    for name in argv[1:] or list(CHECKS):
        print("\n".join(CHECKS[name]()))


if __name__ == "__main__":
    main(sys.argv)
